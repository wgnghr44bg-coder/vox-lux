#!/usr/bin/env python3
"""Generate a voice-over with xAI TTS and insert exact silences at pause markers.

The script is split at [pause] and [long-pause] / [long pause] (any case).
Each piece is sent to POST https://api.x.ai/v1/tts as its own request, and
ffmpeg joins the returned MP3s with real silence in between.

Usage:
    export XAI_API_KEY=...            # never hardcode or commit the key
    python3 tools/xai_voiceover.py colosseum-script.txt --lines 15 -o test.mp3
    python3 tools/xai_voiceover.py colosseum-script.txt -o narration.mp3
    python3 tools/xai_voiceover.py colosseum-script.txt --dry-run   # no API calls
    python3 tools/xai_voiceover.py colosseum-script.txt --lines 15 -o test.mp3 \
        --speed 1.05 --pause-ms 600 --long-pause-ms 1100            # tune pacing

Requires: Python 3.9+, `requests`, and ffmpeg (on PATH, via $FFMPEG, or the
`imageio-ffmpeg` pip package).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

# --- Settings ---------------------------------------------------------------

PAUSE_MS = 900  # silence inserted for [pause]
LONG_PAUSE_MS = 1600  # silence inserted for [long-pause] / [long pause]

VOICE_ID = "lux"  # same voice as the VOX project
SPEED = 1.0  # Tempo (xAI accepts 0.7-1.5)
LANGUAGE = "en"  # "en", "nl" or "auto"

# Wrap every piece in <slow><soft>...</soft></slow>. Also toggled with
# --slow-soft / --no-slow-soft on the command line.
WRAP_SLOW_SOFT = False

# xAI allows up to 15,000 characters per request; the VOX app keeps chunks
# around 2,200. Longer pieces are split at sentence ends (no silence added).
MAX_CHARS_PER_REQUEST = 2000

# Normalize the finished file to this loudness (YouTube-style ~-16 LUFS).
# Set to None to keep xAI's original levels.
LOUDNESS_LUFS: float | None = -16.0

API_URL = "https://api.x.ai/v1/tts"
SAMPLE_RATE = 44100  # output sample rate after joining

# ----------------------------------------------------------------------------

TAG_RE = re.compile(r"<[^>]+>|\[[^\]]+\]")
MARKER_RE = re.compile(r"\[\s*(long[\s-]*pause|pause)\s*\]", re.IGNORECASE)


@dataclass
class Piece:
    text: str
    silence_after_ms: int  # 0 for the last piece or sub-chunks of a long piece


def split_script(script: str) -> list[Piece]:
    """Split at pause markers; consecutive markers add their silences up."""
    pieces: list[Piece] = []
    pending_silence = 0
    pos = 0
    for m in list(MARKER_RE.finditer(script)) + [None]:
        end = m.start() if m else len(script)
        text = " ".join(script[pos:end].split())
        if text:
            if pieces:
                pieces[-1].silence_after_ms += pending_silence
            pieces.append(Piece(text, 0))
            pending_silence = 0
        if m:
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


def to_requests(pieces: list[Piece], limit: int, wrap: bool) -> list[Piece]:
    """Expand pieces into API-sized requests, optionally wrapping in tags."""
    overhead = len("<slow><soft></soft></slow>") if wrap else 0
    out: list[Piece] = []
    for piece in pieces:
        chunks = chunk_text(piece.text, limit - overhead)
        for i, chunk in enumerate(chunks):
            text = f"<slow><soft>{chunk}</soft></slow>" if wrap else chunk
            last = i == len(chunks) - 1
            out.append(Piece(text, piece.silence_after_ms if last else 0))
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


def synthesize(text: str, api_key: str, out_path: Path, retries: int = 3) -> None:
    import requests

    body = {"text": text, "voice_id": VOICE_ID, "language": LANGUAGE, "speed": SPEED}
    headers = {"Content-Type": "application/json"}
    if api_key:  # empty with --proxy-auth: a credential proxy adds the header
        headers["Authorization"] = f"Bearer {api_key}"
    for attempt in range(retries + 1):
        res = requests.post(API_URL, json=body, headers=headers, timeout=120)
        if res.ok and res.content:
            out_path.write_bytes(res.content)
            return
        retryable = res.status_code == 429 or res.status_code >= 500
        if not retryable or attempt == retries:
            raise RuntimeError(f"xAI TTS HTTP {res.status_code}: {res.text[:300]}")
        time.sleep(2 ** (attempt + 1))


def join_with_silence(ffmpeg: str, parts: list[tuple[Path, int]], output: Path) -> None:
    """Concatenate audio files, inserting `ms` of silence after each one."""
    args = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y"]
    for path, _ in parts:
        args += ["-i", str(path)]

    fmt = f"aresample={SAMPLE_RATE},aformat=sample_fmts=fltp:channel_layouts=mono"
    filters: list[str] = []
    labels: list[str] = []
    for i, (_, silence_ms) in enumerate(parts):
        filters.append(f"[{i}:a]{fmt}[a{i}]")
        labels.append(f"[a{i}]")
        if silence_ms > 0:
            filters.append(
                f"anullsrc=r={SAMPLE_RATE}:cl=mono,atrim=duration={silence_ms / 1000},{fmt}[s{i}]"
            )
            labels.append(f"[s{i}]")
    concat = f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1"
    if LOUDNESS_LUFS is not None:
        concat += f",loudnorm=I={LOUDNESS_LUFS}:TP=-1.5:LRA=11"
    filters.append(f"{concat}[out]")

    args += [
        "-filter_complex", ";".join(filters),
        "-map", "[out]",
        "-ar", str(SAMPLE_RATE),
        "-c:a", "libmp3lame", "-b:a", "192k",
        str(output),
    ]
    subprocess.run(args, check=True)


def audio_seconds(ffmpeg: str, path: Path) -> float:
    info = subprocess.run([ffmpeg, "-hide_banner", "-i", str(path)],
                          capture_output=True, text=True).stderr
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info)
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3]) if m else 0.0


def main() -> None:
    global PAUSE_MS, LONG_PAUSE_MS, SPEED, VOICE_ID

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("script", type=Path, help="voice script text file")
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
    parser.add_argument("--voice", default=VOICE_ID, help=f"xAI voice_id (default {VOICE_ID})")
    parser.add_argument("--proxy-auth", action="store_true",
                        help="send no Authorization header; a credential proxy "
                             "(e.g. Claude Code cloud credentials) adds it")
    parser.add_argument("--dry-run", action="store_true",
                        help="show the pieces and character count; no API calls")
    args = parser.parse_args()

    if not 0.7 <= args.speed <= 1.5:
        parser.error("--speed must be between 0.7 and 1.5")
    PAUSE_MS, LONG_PAUSE_MS = args.pause_ms, args.long_pause_ms
    SPEED, VOICE_ID = args.speed, args.voice

    use_wrap = WRAP_SLOW_SOFT if args.wrap is None else args.wrap
    lines = args.script.read_text(encoding="utf-8").splitlines()
    if args.lines:
        lines = lines[: args.lines]
    pieces = to_requests(split_script("\n".join(lines)), MAX_CHARS_PER_REQUEST, use_wrap)
    if not pieces:
        sys.exit("No text to speak.")

    total_chars = sum(len(p.text) for p in pieces)
    print(f"{len(pieces)} requests, {total_chars} characters billed "
          f"(voice={VOICE_ID}, speed={SPEED}, slow/soft={'on' if use_wrap else 'off'})")
    for i, p in enumerate(pieces, 1):
        pause = f"  + {p.silence_after_ms} ms silence" if p.silence_after_ms else ""
        print(f"  {i:>3}. {p.text[:70]!r}{'…' if len(p.text) > 70 else ''}{pause}")
    if args.dry_run:
        return

    api_key = os.environ.get("XAI_API_KEY", "").strip()
    if not api_key and not args.proxy_auth:
        sys.exit("Set the XAI_API_KEY environment variable first (or use --proxy-auth).")
    ffmpeg = find_ffmpeg()

    with tempfile.TemporaryDirectory() as tmp:
        parts: list[tuple[Path, int]] = []
        for i, p in enumerate(pieces, 1):
            path = Path(tmp) / f"piece_{i:03d}.mp3"
            print(f"Generating {i}/{len(pieces)}…", flush=True)
            synthesize(p.text, api_key, path)
            parts.append((path, p.silence_after_ms))
        speech_sec = sum(audio_seconds(ffmpeg, path) for path, _ in parts)
        join_with_silence(ffmpeg, parts, args.output)

    words = sum(len(TAG_RE.sub(" ", p.text).split()) for p in pieces)
    total_sec = speech_sec + sum(p.silence_after_ms for p in pieces) / 1000
    if speech_sec:
        print(f"Pace: {words / speech_sec * 60:.0f} words/min while speaking, "
              f"{words / total_sec * 60:.0f} words/min including pauses")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
