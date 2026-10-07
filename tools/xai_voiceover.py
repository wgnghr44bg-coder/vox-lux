#!/usr/bin/env python3
"""Generate a voice-over with xAI or ElevenLabs TTS and exact pause silences.

The script is split at [pause] and [long-pause] / [long pause] (any case).
Each piece is sent to the TTS API as its own request (xAI: POST
https://api.x.ai/v1/tts, ElevenLabs: POST /v1/text-to-speech/{voice}), and
ffmpeg joins the returned MP3s with real silence in between.

Usage:
    export XAI_API_KEY=...            # never hardcode or commit the key
    python3 tools/xai_voiceover.py colosseum-script.txt --lines 15 -o test.mp3
    python3 tools/xai_voiceover.py colosseum-script.txt -o narration.mp3
    python3 tools/xai_voiceover.py colosseum-script.txt --dry-run   # no API calls
    python3 tools/xai_voiceover.py colosseum-script.txt --lines 15 -o test.mp3 \
        --speed 1.05 --pause-ms 600 --long-pause-ms 1100            # tune pacing

Defaults (voice lux, speed 0.9, pauses 500/1000 ms, 300 ms after sentences,
natural pause after commas, edge silence trimmed) match the pacing of the
reference narration this was tuned against.

    export ELEVENLABS_API_KEY=...
    python3 tools/xai_voiceover.py --engine elevenlabs --list-voices   # British voices
    python3 tools/xai_voiceover.py script.txt --engine elevenlabs --voice Daniel -o out.mp3

Long productions: put {img:ID} on its own line where an image should start,
then use --timeline times.tsv (image start times), --cache-dir DIR (resume
without paying twice) and --bitrate 128k.

Requires: Python 3.9+, `requests`, and ffmpeg (on PATH, via $FFMPEG, or the
`imageio-ffmpeg` pip package).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path

# --- Settings ---------------------------------------------------------------

PAUSE_MS = 500  # silence inserted for [pause]
LONG_PAUSE_MS = 1000  # silence inserted for [long-pause] / [long pause]
# Short silence after every sentence (. ! ?) that has no marker. 0 = off.
SENTENCE_PAUSE_MS = 300
# xAI only: add its own [pause] tag after every comma, so the voice breathes
# there without breaking the sentence melody. Also --comma-pause / --no-comma-pause.
COMMA_PAUSE = True

VOICE_ID = "lux"  # eigenaar, okt 2026: na proefjes met Leo e.a. toch Lux
SPEED = 0.9  # Tempo (xAI accepts 0.7-1.5); 0.9 = rustiger (eigenaar, okt 2026)
LANGUAGE = "en"  # "en", "en-GB", "nl" or "auto"

# Wrap every piece in <slow><soft>...</soft></slow>. Also toggled with
# --slow-soft / --no-slow-soft on the command line.
WRAP_SLOW_SOFT = False

# xAI allows up to 15,000 characters per request; the VOX app keeps chunks
# around 2,200. Longer pieces are split at sentence ends (no silence added).
MAX_CHARS_PER_REQUEST = 2000

# Normalize the finished file to this loudness (YouTube-style ~-16 LUFS).
# Set to None to keep xAI's original levels.
LOUDNESS_LUFS: float | None = -16.0

# Cut the silence the TTS service leaves at the start/end of each piece, so
# PAUSE_MS / LONG_PAUSE_MS are the real gap lengths. Also --no-trim.
TRIM_EDGE_SILENCE = True
# Fade the edges of every piece (--soft-edges): no hard cut into the silence after a sentence.
SOFT_EDGES = False

API_URL = "https://api.x.ai/v1/tts"

# ElevenLabs (--engine elevenlabs). --voice takes a voice name or voice_id.
ELEVEN_VOICE = "Daniel"  # premade deep British male voice
ELEVEN_MODEL = "eleven_multilingual_v2"
ELEVEN_STABILITY = 0.5  # higher = calmer, more even delivery
ELEVEN_URL = "https://api.elevenlabs.io/v1"
SAMPLE_RATE = 44100  # output sample rate after joining
OUTPUT_BITRATE = "192k"  # MP3 bitrate (--bitrate); 128k is plenty for speech
WORKERS = 4  # parallel TTS requests (--workers)

# ----------------------------------------------------------------------------

TAG_RE = re.compile(r"<[^>]+>|\[[^\]]+\]")
# Sentence end: . ! or ? (not "..."), optional closing quote, then whitespace.
SENTENCE_END_RE = re.compile(r"(?<!\.)[.!?][\"'’”)]*(?=\s)")
ABBREVIATIONS = {"mr", "mrs", "ms", "dr", "st", "prof", "sr", "jr", "vs", "etc", "no"}
MARKER_RE = re.compile(r"\[\s*(long[\s-]*pause|pause)\s*\]", re.IGNORECASE)
# {img:ID} lines mark where an image starts; never spoken, recorded in --timeline.
CUE_RE = re.compile(r"\{img:\s*([^}]+)\}", re.IGNORECASE)
TOKEN_RE = re.compile(f"{MARKER_RE.pattern}|{CUE_RE.pattern}", re.IGNORECASE)


@dataclass
class Piece:
    text: str
    silence_after_ms: int  # 0 for the last piece or sub-chunks of a long piece
    cue: str = ""  # image cue ({img:ID} in the script) starting at this piece


def split_sentences(text: str) -> list[str]:
    """Split at sentence ends, skipping abbreviations and open <tags>."""
    out: list[str] = []
    start = 0
    for m in SENTENCE_END_RE.finditer(text):
        word = re.findall(r"(\w+)\W*$", text[start:m.end()])
        if text[m.start()] == "." and word and word[0].lower() in ABBREVIATIONS:
            continue
        if re.match(r"\s+[a-z]", text[m.end():]):
            continue  # '"Stop!" he said.' continues the same sentence
        head = text[:m.end()]
        if len(re.findall(r"<[^/>]+>", head)) != len(re.findall(r"</[^>]+>", head)):
            continue  # inside a <slow>...</slow> span: keep it in one request
        out.append(text[start:m.end()].strip())
        start = m.end()
    if text[start:].strip():
        out.append(text[start:].strip())
    return out


def split_script(script: str) -> list[Piece]:
    """Split at pause markers; consecutive markers add their silences up."""
    pieces: list[Piece] = []
    pending_silence = 0
    pending_cue = ""
    pos = 0
    for m in list(TOKEN_RE.finditer(script)) + [None]:
        end = m.start() if m else len(script)
        text = " ".join(script[pos:end].split())
        if text:
            if pieces:
                pieces[-1].silence_after_ms += pending_silence
            sentences = split_sentences(text) if SENTENCE_PAUSE_MS > 0 else [text]
            for i, sentence in enumerate(sentences):
                last = i == len(sentences) - 1
                pieces.append(Piece(sentence, 0 if last else SENTENCE_PAUSE_MS,
                                    pending_cue if i == 0 else ""))
            pending_silence = 0
            pending_cue = ""
        if m and m.group(2):
            pending_cue = m.group(2).strip()
            pos = m.end()
        elif m:
            is_long = m.group(1).lower().startswith("long")
            pending_silence += LONG_PAUSE_MS if is_long else PAUSE_MS
            pos = m.end()
    return pieces


def chunk_text(text: str, limit: int) -> list[str]:
    """Split text into chunks of at most `limit` chars, preferring sentence ends."""
    chunks: list[str] = []
    rest = text
    while len(rest) > limit:
        window = rest[:limit]
        cut = max(window.rfind(s) for s in (". ", "! ", "? ", "… "))
        if cut < limit * 0.4:
            cut = window.rfind(" ")
        cut = limit if cut < limit * 0.4 else cut + 1
        chunks.append(rest[:cut].strip())
        rest = rest[cut:].strip()
    if rest:
        chunks.append(rest)
    return chunks


def to_requests(pieces: list[Piece], limit: int, wrap: bool,
                comma_pause: bool = False) -> list[Piece]:
    """Expand pieces into API-sized requests, optionally wrapping in tags."""
    overhead = len("<slow><soft></soft></slow>") if wrap else 0
    out: list[Piece] = []
    for piece in pieces:
        text = re.sub(r",\s+", ", [pause] ", piece.text) if comma_pause else piece.text
        chunks = chunk_text(text, limit - overhead)
        for i, chunk in enumerate(chunks):
            text = f"<slow><soft>{chunk}</soft></slow>" if wrap else chunk
            last = i == len(chunks) - 1
            out.append(Piece(text, piece.silence_after_ms if last else 0,
                             piece.cue if i == 0 else ""))
    return out


def find_ffmpeg() -> str:
    exe = os.environ.get("FFMPEG") or shutil.which("ffmpeg")
    if exe:
        return exe
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg not found: install it, set $FFMPEG, or pip install imageio-ffmpeg")


ENGINE = "xai"  # "xai" or "elevenlabs" (--engine)


def eleven_headers(api_key: str) -> dict[str, str]:
    # Empty with --proxy-auth: a credential proxy adds the xi-api-key header.
    return {"xi-api-key": api_key} if api_key else {}


def eleven_voices(api_key: str) -> list[dict]:
    import requests

    res = requests.get(f"{ELEVEN_URL}/voices", headers=eleven_headers(api_key), timeout=60)
    if not res.ok:
        raise RuntimeError(f"ElevenLabs HTTP {res.status_code}: {res.text[:300]}")
    return res.json()["voices"]


# Known voices, so names work even when the key lacks "voices_read".
ELEVEN_PREMADE = {
    "daniel": "onwK4e9ZLuTAKqWW03F9",  # British, deep, news presenter
    "george": "JBFqnCBsd6RMkjVDRZzb",  # British, warm, storyteller
    # Voice Library (needs a paid ElevenLabs plan for API use):
    "nathaniel": "pFQStpMdprGFILRDrWR2",  # British, deep, meditative
}


def resolve_eleven_voice(name_or_id: str, api_key: str) -> str:
    """Accept a voice name ("Daniel") or a raw voice_id."""
    if name_or_id.lower() in ELEVEN_PREMADE:
        return ELEVEN_PREMADE[name_or_id.lower()]
    try:
        voices = eleven_voices(api_key)
    except RuntimeError:
        return name_or_id  # e.g. key without "voices_read": treat as voice_id
    for v in voices:
        if name_or_id in (v["voice_id"], v["name"]) or v["name"].lower().startswith(
            name_or_id.lower() + " "
        ):
            return v["voice_id"]
    return name_or_id


def synthesize(text: str, api_key: str, out_path: Path, retries: int = 3) -> None:
    import requests

    headers = {"Content-Type": "application/json"}
    if ENGINE == "elevenlabs":
        url = f"{ELEVEN_URL}/text-to-speech/{VOICE_ID}?output_format=mp3_44100_128"
        body = {
            "text": text,
            "model_id": ELEVEN_MODEL,
            "voice_settings": {"stability": ELEVEN_STABILITY, "similarity_boost": 0.75,
                               "speed": SPEED},
        }
        headers.update(eleven_headers(api_key))
    else:
        url = API_URL
        body = {"text": text, "voice_id": VOICE_ID, "language": LANGUAGE, "speed": SPEED}
        if api_key:  # empty with --proxy-auth: a credential proxy adds the header
            headers["Authorization"] = f"Bearer {api_key}"
    for attempt in range(retries + 1):
        res = requests.post(url, json=body, headers=headers, timeout=120)
        if res.ok and res.content:
            out_path.write_bytes(res.content)
            return
        retryable = res.status_code == 429 or res.status_code >= 500
        if not retryable or attempt == retries:
            raise RuntimeError(f"{ENGINE} TTS HTTP {res.status_code}: {res.text[:300]}")
        time.sleep(2 ** (attempt + 1))


def prepare_piece(ffmpeg: str, src: Path, dst: Path, trim: bool) -> float:
    """Decode to mono 16-bit WAV (edge silence trimmed); return its duration."""
    af = f"aresample={SAMPLE_RATE}"
    if trim:
        edge = "silenceremove=start_periods=1:start_threshold=-50dB"
        af = f"{edge},areverse,{edge},areverse,{af}"
    if SOFT_EDGES:   # soft start/end so a cut into silence never sounds clipped (same length)
        af = f"{af},afade=t=in:d=0.015,areverse,afade=t=in:d=0.12:curve=qsin,areverse"
    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(src),
                    "-af", af, "-ac", "1", "-c:a", "pcm_s16le", str(dst)], check=True)
    return (dst.stat().st_size - 44) / 2 / SAMPLE_RATE


def join_with_silence(ffmpeg: str, parts: list[tuple[Path, int]], output: Path,
                      trim: bool = False, workdir: Path | None = None) -> list[float]:
    """Concatenate audio files, inserting `ms` of silence after each one.

    Returns each part's duration in seconds after trimming, so callers can
    build a timeline. Uses the concat demuxer, so hours of audio work too.
    """
    with tempfile.TemporaryDirectory(dir=workdir) as tmp:
        tmp_dir = Path(tmp)
        lines: list[str] = []
        durations: list[float] = []
        silences: dict[int, Path] = {}
        for i, (path, silence_ms) in enumerate(parts):
            wav = tmp_dir / f"p{i:05d}.wav"
            durations.append(prepare_piece(ffmpeg, path, wav, trim))
            lines.append(f"file '{wav}'")
            if silence_ms > 0:
                if silence_ms not in silences:
                    silences[silence_ms] = tmp_dir / f"silence_{silence_ms}.wav"
                    subprocess.run([ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                                    "-f", "lavfi", "-i", f"anullsrc=r={SAMPLE_RATE}:cl=mono",
                                    "-t", str(silence_ms / 1000), "-c:a", "pcm_s16le",
                                    str(silences[silence_ms])], check=True)
                lines.append(f"file '{silences[silence_ms]}'")
        playlist = tmp_dir / "list.txt"
        playlist.write_text("\n".join(lines) + "\n")

        args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y",
                "-f", "concat", "-safe", "0", "-i", str(playlist)]
        if LOUDNESS_LUFS is not None:
            args += ["-af", f"loudnorm=I={LOUDNESS_LUFS}:TP=-1.5:LRA=11"]
        args += ["-ar", str(SAMPLE_RATE), "-ac", "1",
                 "-c:a", "libmp3lame", "-b:a", OUTPUT_BITRATE, str(output)]
        subprocess.run(args, check=True)
    return durations


def fmt_time(sec: float) -> str:
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}"


def audio_seconds(ffmpeg: str, path: Path) -> float:
    info = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)],
                          capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def main() -> None:
    global PAUSE_MS, LONG_PAUSE_MS, SENTENCE_PAUSE_MS, SPEED, VOICE_ID, ENGINE, OUTPUT_BITRATE

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("script", type=Path, nargs="?", help="voice script text file")
    parser.add_argument("--engine", choices=["xai", "elevenlabs"], default="xai")
    parser.add_argument("--list-voices", action="store_true",
                        help="ElevenLabs: list available voices (British first)")
    parser.add_argument("-o", "--output", type=Path, default=Path("narration.mp3"))
    parser.add_argument("--lines", type=int, help="only use the first N lines (for testing)")
    wrap = parser.add_mutually_exclusive_group()
    wrap.add_argument("--slow-soft", dest="wrap", action="store_true", default=None,
                      help="wrap each piece in <slow><soft>...</soft></slow>")
    wrap.add_argument("--no-slow-soft", dest="wrap", action="store_false")
    parser.add_argument("--speed", type=float, default=SPEED,
                        help=f"Tempo 0.7-1.5 (default {SPEED})")
    parser.add_argument("--pause-ms", type=int, default=PAUSE_MS,
                        help=f"silence for [pause] (default {PAUSE_MS})")
    parser.add_argument("--long-pause-ms", type=int, default=LONG_PAUSE_MS,
                        help=f"silence for [long-pause] (default {LONG_PAUSE_MS})")
    comma = parser.add_mutually_exclusive_group()
    comma.add_argument("--comma-pause", dest="comma", action="store_true", default=None,
                       help="xAI: add a natural [pause] after every comma")
    comma.add_argument("--no-comma-pause", dest="comma", action="store_false")
    parser.add_argument("--sentence-pause-ms", type=int, default=SENTENCE_PAUSE_MS,
                        help=f"silence after each sentence without a marker "
                             f"(default {SENTENCE_PAUSE_MS}, 0 = off)")
    parser.add_argument("--voice", help=f"voice (default {VOICE_ID} for xAI, "
                                        f"{ELEVEN_VOICE} for ElevenLabs)")
    parser.add_argument("--soft-edges", action="store_true",
                        help="fade in/out every piece so pauses do not start with a hard cut")
    parser.add_argument("--no-trim", action="store_true",
                        help="keep the service's own silence around each piece")
    parser.add_argument("--timeline", type=Path,
                        help="write a TSV with start/end time, image cue and text per piece")
    parser.add_argument("--cache-dir", type=Path,
                        help="keep generated pieces here; reruns reuse them (no double billing)")
    parser.add_argument("--workers", type=int, default=WORKERS,
                        help=f"parallel TTS requests (default {WORKERS})")
    parser.add_argument("--bitrate", default=OUTPUT_BITRATE,
                        help=f"MP3 bitrate (default {OUTPUT_BITRATE})")
    parser.add_argument("--proxy-auth", action="store_true",
                        help="send no API key header; a credential proxy "
                             "(e.g. Claude Code cloud credentials) adds it")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the pieces and character count; no API calls")
    args = parser.parse_args()

    ENGINE = args.engine
    eleven = ENGINE == "elevenlabs"
    key_var = "ELEVENLABS_API_KEY" if eleven else "XAI_API_KEY"
    api_key = os.environ.get(key_var, "").strip()

    if args.list_voices:
        if not eleven:
            parser.error("--list-voices needs --engine elevenlabs")
        voices = eleven_voices(api_key)
        voices.sort(key=lambda v: (v.get("labels", {}).get("accent", "") != "british",
                                   v["name"]))
        for v in voices:
            labels = v.get("labels", {})
            desc = ", ".join(str(labels[k]) for k in ("accent", "gender", "age",
                                                      "description", "use_case")
                             if labels.get(k))
            print(f"{v['name']:<28} {v['voice_id']}  {desc}")
        return
    if not args.script:
        parser.error("the script file is required")

    max_speed = 1.2 if eleven else 1.5
    if not 0.7 <= args.speed <= max_speed:
        parser.error(f"--speed must be between 0.7 and {max_speed} for {ENGINE}")
    PAUSE_MS, LONG_PAUSE_MS = args.pause_ms, args.long_pause_ms
    SENTENCE_PAUSE_MS = args.sentence_pause_ms
    OUTPUT_BITRATE = args.bitrate
    SPEED = args.speed
    VOICE_ID = args.voice or (ELEVEN_VOICE if eleven else VOICE_ID)

    use_wrap = WRAP_SLOW_SOFT if args.wrap is None else args.wrap
    if eleven and use_wrap:
        parser.error("<slow><soft> tags are xAI-only; leave --slow-soft off for ElevenLabs")
    lines = args.script.read_text(encoding="utf-8").splitlines()
    if args.lines:
        lines = lines[: args.lines]
    text = "\n".join(lines)
    if eleven:  # ElevenLabs would read xAI tags like [breath] or <slow> aloud
        text = TAG_RE.sub(lambda m: m[0] if MARKER_RE.fullmatch(m[0]) else " ", text)
    use_comma = COMMA_PAUSE if args.comma is None else args.comma
    if eleven and use_comma:
        parser.error("--comma-pause uses an xAI tag; it is not available for ElevenLabs")
    pieces = to_requests(split_script(text), MAX_CHARS_PER_REQUEST, use_wrap, use_comma)
    if not pieces:
        sys.exit("No text to speak.")

    total_chars = sum(len(p.text) for p in pieces)
    print(f"{len(pieces)} requests, {total_chars} characters billed "
          f"(engine={ENGINE}, voice={VOICE_ID}, speed={SPEED}, slow/soft={'on' if use_wrap else 'off'})")
    for i, p in enumerate(pieces, 1):
        pause = f"  + {p.silence_after_ms} ms silence" if p.silence_after_ms else ""
        print(f"  {i:>3}. {p.text[:70]!r}{'…' if len(p.text) > 70 else ''}{pause}")
    global SOFT_EDGES
    SOFT_EDGES = SOFT_EDGES or args.soft_edges
    if args.dry_run:
        return

    if not api_key and not args.proxy_auth:
        sys.exit(f"Set the {key_var} environment variable first (or use --proxy-auth).")
    ffmpeg = find_ffmpeg()
    if eleven:
        VOICE_ID = resolve_eleven_voice(VOICE_ID, api_key)

    with tempfile.TemporaryDirectory() as tmp:
        cache = args.cache_dir or Path(tmp)
        cache.mkdir(parents=True, exist_ok=True)
        settings = f"{ENGINE}|{VOICE_ID}|{SPEED}|{LANGUAGE}|{ELEVEN_MODEL if eleven else ''}"

        def piece_path(p: Piece) -> Path:
            digest = hashlib.sha1(f"{settings}|{p.text}".encode()).hexdigest()[:16]
            return cache / f"{digest}.mp3"

        todo = [p for p in pieces if not piece_path(p).exists()]
        if len(todo) < len(pieces):
            print(f"Reusing {len(pieces) - len(todo)} cached pieces")
        done = 0

        def generate(p: Piece) -> None:
            nonlocal done
            part = piece_path(p).with_suffix(".part")
            synthesize(p.text, api_key, part)
            part.rename(piece_path(p))
            done += 1
            if done % 25 == 0 or done == len(todo):
                print(f"Generated {done}/{len(todo)}", flush=True)

        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            list(pool.map(generate, todo))

        parts = [(piece_path(p), p.silence_after_ms) for p in pieces]
        print("Joining…", flush=True)
        durations = join_with_silence(ffmpeg, parts, args.output,
                                      trim=TRIM_EDGE_SILENCE and not args.no_trim,
                                      workdir=cache)
        speech_sec = sum(durations)

    if args.timeline:
        t = 0.0
        rows = ["#\tstart\tend\timage\ttext"]
        for i, (p, d) in enumerate(zip(pieces, durations), 1):
            rows.append(f"{i}\t{fmt_time(t)}\t{fmt_time(t + d)}\t{p.cue}\t{' '.join(TAG_RE.sub('', p.text).split())}")
            t += d + p.silence_after_ms / 1000
        args.timeline.write_text("\n".join(rows) + "\n", encoding="utf-8")
        print(f"Timeline: {args.timeline}")

    words = sum(len(TAG_RE.sub(" ", p.text).split()) for p in pieces)
    total_sec = speech_sec + sum(p.silence_after_ms for p in pieces) / 1000
    if speech_sec:
        print(f"Pace: {words / speech_sec * 60:.0f} words/min while speaking, "
              f"{words / total_sec * 60:.0f} words/min including pauses")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
