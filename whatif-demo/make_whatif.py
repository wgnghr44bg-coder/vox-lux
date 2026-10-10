#!/usr/bin/env python3
"""One command: topic number -> finished 'What if' video.

    python3 whatif-demo/make_whatif.py 1            # everything (voice, render, sound, mp4, upload.json)
    python3 whatif-demo/make_whatif.py 1 --stills   # only 6 test frames -> topics/<slug>/stills/overzicht.jpg
    python3 whatif-demo/make_whatif.py 1 --from audio   # skip voice + render, redo sound and the final mp4

The topic row comes from onderwerpen.md; the video itself is described by
topics/<slug>/scenario.js (topic, place, force, counter, lines, timing, end text, upload text).
Writing that file is the creative step (see AUTOMATISCH.md); everything after it is automatic:

  script.txt  <- lines            (English, "Imagine…", 170-210 words)
  voice.mp3   <- tools/xai_voiceover.py --proxy-auth --speed 1.05 --voice atlas --timeline voice-times.tsv
  timing.json <- measured sentence times
  silent.mp4  <- engine/render.mjs (720x1280, 30 fps, 3 workers)
  mix.wav     <- make_audio.py (voice first, bed ducked 8 dB, -14 LUFS, peak -1 dB)
  <slug>.mp4  <- scaled to 1080x1920 + mix;  upload.json  (Shorts need no thumbnail)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import time
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
TOPICS = HERE / "topics"
STAGES = ["voice", "render", "audio", "final"]
VOICE = "atlas"  # IfScape3D-stem (eigenaar, 7 okt 2026): xAI Atlas, documentairestijl, tempo 1.05, mét pauzes
SPEED = 1.05  # standaardtempo IfScape3D (Sleep Archives: Lux op 0.9); per video te overschrijven met topic.voiceSpeed


def run(cmd, **kw):
    print("$", " ".join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def topic_row(num: int) -> dict:
    for line in (HERE / "onderwerpen.md").read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and cells[0] == str(num):
            return {"number": num, "question": "What if " + cells[1], "place": cells[2], "force": cells[3], "status": cells[4]}
    sys.exit(f"Topic {num} not found in onderwerpen.md")


def find_topic(num: int) -> Path:
    for d in sorted(TOPICS.iterdir()):
        f = d / "scenario.js"
        if f.exists() and re.search(rf"number:\s*{num}\b", f.read_text(encoding="utf-8")):
            return d
    row = topic_row(num)
    sys.exit(f"No topics/<slug>/scenario.js for #{num} ({row['question']}). Write it first (see AUTOMATISCH.md).")


def load_scenario(d: Path) -> dict:
    js = ("import(process.argv[1]).then(m => console.log(JSON.stringify("
          "{ topic: m.topic, lines: m.lines, upload: m.upload || {} })))")
    out = subprocess.run(["node", "-e", js, (d / "scenario.js").as_uri()], capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def script_text(lines) -> str:
    out = []
    for _id, text, pause in lines:
        if isinstance(pause, (int, float)):
            marker = " ".join(["[long pause]"] * max(1, round(pause)))
        else:
            marker = {"pause": "[pause]", "long": "[long pause]", "none": "", "": ""}.get(pause or "", "")
        out.append(f"{text} {marker}".strip())
    return "\n".join(out) + "\n"


def check_script(lines):
    words = sum(len(re.sub(r"\[[^\]]+\]", " ", t).split()) for _, t, _ in lines)
    print(f"script: {words} words")
    if not lines[0][1].startswith("Imagine"):
        print("WARNING: the first line should start with 'Imagine'")
    if not 170 <= words <= 210:
        print("WARNING: aim for 170-210 words")


def parse_tsv(path: Path):
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        c = line.split("\t")
        if len(c) < 5: continue
        to_s = lambda s: sum(float(x) * 60 ** i for i, x in enumerate(reversed(s.split(":"))))
        rows.append((to_s(c[1]), to_s(c[2]), c[4]))
    return rows


def timing_from_tsv(lines, rows, offset=0.8) -> dict:
    """Each line is one or more TSV rows (the voice tool splits at sentence ends); match by words."""
    out, i = {}, 0
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).split()
    for lid, text, _ in lines:
        want = norm(text); got = []; start = rows[i][0]
        while i < len(rows) and len(got) < len(want):
            got += norm(rows[i][2]); end = rows[i][1]; i += 1
        if got != want:
            print(f"WARNING: timing mismatch for {lid}: {' '.join(got)!r} vs {' '.join(want)!r}")
        out[lid] = [round(start, 2), round(end, 2)]
    return {"VO_OFFSET": offset, "lines": out}


def one_take(d: Path, lines, speed):
    """Speak the whole script in ONE xAI request (its own [pause] tags), so sentences flow into each other.
    Line times come from the silences in the take: every line boundary goes to the nearest gap, in order."""
    import requests
    text = re.sub(r"\s+", " ", script_text(lines)).strip()
    raw = d / "voice-take.mp3"
    for k in range(4):
        r = requests.post("https://api.x.ai/v1/tts", json={"text": text, "voice_id": VOICE, "language": "en", "speed": speed}, timeout=300)
        if r.ok and r.content: raw.write_bytes(r.content); break
        if k == 3: raise SystemExit(f"xAI TTS HTTP {r.status_code}: {r.text[:200]}")
        time.sleep(2 ** (k + 1))
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", raw, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "44100", "-b:a", "192k", d / "voice.mp3"])
    dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", d / "voice.mp3"],
                               capture_output=True, text=True).stdout)
    log = subprocess.run(["ffmpeg", "-i", d / "voice.mp3", "-af", "silencedetect=n=-38dB:d=0.18", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]; en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    sil = list(zip(st, en + [dur] * (len(st) - len(en))))
    t_first = sil[0][1] if sil and sil[0][0] <= .05 else 0.0
    t_last = sil[-1][0] if sil and sil[-1][1] >= dur - .05 else dur
    gaps = [(a, b) for a, b in sil if a > .05 and b < dur - .05]          # inner gaps only
    words = [len(re.sub(r"[^A-Za-z0-9]", "", t)) + 2 * len(re.findall(r"[,.;:!?]", t)) for _, t, _ in lines]   # letters (+ a little per punctuation pause)
    speech = lambda t: t - sum(min(b, t) - a for a, b in gaps if a < t)   # speech-only clock
    total = speech(t_last) - speech(t_first)
    # best monotone choice of one gap per line boundary (dynamic programming): close to the word-count estimate,
    # and a marked pause ([pause]/[long pause]) should land on a long gap
    want, cum = [], 0
    for w in words[:-1]:
        cum += w; want.append(speech(t_first) + total * cum / sum(words))
    wgt = [1.5 if isinstance(pz, (int, float)) or pz == "long" else 1 if pz == "pause" else .2 for _, _, pz in lines[:-1]]
    cost = lambda i, j: abs(speech(gaps[j][0]) - want[i]) - wgt[i] * min(gaps[j][1] - gaps[j][0], 2)
    N, G = len(want), len(gaps)
    if G < N: raise SystemExit("one-take: not enough pauses to place every line")
    INF = float("inf"); best = [[INF] * G for _ in range(N)]; prev = [[-1] * G for _ in range(N)]
    for j in range(G): best[0][j] = cost(0, j)
    for i in range(1, N):
        run_min, arg = INF, -1
        for j in range(G):
            if j - 1 >= 0 and best[i - 1][j - 1] < run_min: run_min, arg = best[i - 1][j - 1], j - 1
            if arg >= 0: best[i][j] = run_min + cost(i, j); prev[i][j] = arg
    j = min(range(G), key=lambda k: best[N - 1][k]); pick = []
    for i in range(N - 1, -1, -1): pick.append(j); j = prev[i][j]
    pick.reverse()
    starts, ends = [t_first] + [gaps[j][1] for j in pick], [gaps[j][0] for j in pick]
    ends.append(t_last)
    stt = stt_line_times(d / "voice.mp3", lines)          # exact word times (ElevenLabs speech-to-text) when available
    if stt: starts, ends = stt
    hms = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:04.1f}"
    rows = ["nr\tstart\tend\tpause\ttext"] + [f"{i + 1}\t{hms(a)}\t{hms(b)}\t\t{t}" for i, (a, b, (_, t, _)) in enumerate(zip(starts, ends, lines))]
    (d / "voice-times.tsv").write_text("\n".join(rows) + "\n", encoding="utf-8")
    print(f"one take: {dur:.1f} s, {len(gaps)} pauses, {len(lines)} lines placed")


def pad_silence(d: Path, lines):
    """topic.padSilence (opt-in): a one take rarely holds a long silence, so after a line whose pause is a number
    (the silent climax, e.g. 3) the gap in voice.mp3 is stretched to that many seconds; 'pause' gaps to at least
    0.75 s and 'long' gaps to at least 1.15 s (documentary pace); later line times shift."""
    rows = parse_tsv(d / "voice-times.tsv")
    if len(rows) != len(lines): return
    times = [[a, b] for a, b, _ in rows]; cuts = []
    for i, (_, _, pz) in enumerate(lines[:-1]):
        if not isinstance(pz, (int, float)):
            pz = {"pause": .75, "long": 1.15}.get(pz)    # documentary pace (eigenaar 10 okt): never a rushed pause
            if pz is None: continue
        gap = times[i + 1][0] - times[i][1]
        if gap >= pz - .05: continue
        at, add = times[i][1] + gap / 2, pz - gap
        cuts.append((at, add))
        for j in range(i + 1, len(times)): times[j] = [times[j][0] + add, times[j][1] + add]
    if not cuts: return
    src = d / "voice-unpadded.mp3"
    if not src.exists(): (d / "voice.mp3").rename(src)
    parts, last, fc = [], 0.0, []
    for k, (at, add) in enumerate(cuts):
        orig = at - sum(a for _, a in cuts[:k])
        fc.append(f"[0:a]atrim={last:.3f}:{orig:.3f},asetpts=PTS-STARTPTS[p{k}];aevalsrc=0:d={add:.3f}:s=44100:c=stereo[s{k}]")
        parts += [f"[p{k}]", f"[s{k}]"]; last = orig
    fc.append(f"[0:a]atrim=start={last:.3f},asetpts=PTS-STARTPTS[pe]"); parts.append("[pe]")
    fc = ";".join(fc) + ";" + "".join(f"{p}aformat=sample_rates=44100:channel_layouts=stereo[f{i}];" for i, p in enumerate(parts)) \
        + "".join(f"[f{i}]" for i in range(len(parts))) + f"concat=n={len(parts)}:v=0:a=1[o]"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-filter_complex", fc, "-map", "[o]", "-b:a", "192k", d / "voice.mp3"])
    hms = lambda t: f"{int(t // 3600)}:{int(t % 3600 // 60):02d}:{t % 60:04.1f}"
    out = ["nr\tstart\tend\tpause\ttext"] + [f"{i + 1}\t{hms(a)}\t{hms(b)}\t\t{t}" for i, ((a, b), (_, t, _)) in enumerate(zip(times, lines))]
    (d / "voice-times.tsv").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("silence padded:", ", ".join(f"+{a:.1f}s at {t:.1f}s" for t, a in cuts))


def stt_line_times(mp3: Path, lines):
    """Word timestamps from ElevenLabs speech-to-text, matched to the script words -> (starts, ends) per line, or None."""
    import difflib, requests
    try:
        with open(mp3, "rb") as f:
            r = requests.post("https://api.elevenlabs.io/v1/speech-to-text", files={"file": (mp3.name, f, "audio/mpeg")},
                              data={"model_id": "scribe_v1", "timestamps_granularity": "word", "tag_audio_events": "false"}, timeout=240)
        if not r.ok: print("stt: HTTP", r.status_code); return None
        words = [w for w in r.json().get("words", []) if w.get("type") == "word"]
    except Exception as e:
        print("stt failed:", e); return None
    norm = lambda t: re.sub(r"[^a-z0-9]", "", t.lower())
    script, owner = [], []
    for i, (_, t, _) in enumerate(lines):
        for w in t.split(): script.append(norm(w)); owner.append(i)
    heard = [norm(w["text"]) for w in words]
    sm = difflib.SequenceMatcher(None, script, heard, autojunk=False)
    first, last = {}, {}
    for a, b, n in sm.get_matching_blocks():
        for k in range(n):
            i = owner[a + k]; w = words[b + k]
            first.setdefault(i, w["start"]); last[i] = w["end"]
    if len(first) < len(lines): print(f"stt: only {len(first)}/{len(lines)} lines matched"); return None
    starts = [first[i] for i in range(len(lines))]; ends = [last[i] for i in range(len(lines))]
    if all(starts[i + 1] >= ends[i] - .05 for i in range(len(lines) - 1)):
        print("stt: line times from speech recognition"); return starts, ends
    print("stt: times out of order"); return None


def contact_sheet(d: Path, times):
    st = d / "stills"
    ins = sum([["-i", str(st / f"still-{t}.jpg")] for t in times], [])
    n = len(times)
    layout = "|".join(f"{'+'.join(['w0'] * (k % 3)) or '0'}_{'+'.join(['h0'] * (k // 3)) or '0'}" for k in range(n))
    run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex",
         f"{''.join(f'[{k}]' for k in range(n))}xstack=inputs={n}:layout={layout},scale=1080:-1", str(st / "overzicht.jpg")])
    print("overview:", st / "overzicht.jpg")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("number", type=int)
    ap.add_argument("--stills", action="store_true", help="only render 6 test frames and an overview")
    ap.add_argument("--times", help="comma-separated seconds for --stills")
    ap.add_argument("--from", dest="start", choices=STAGES, default="voice")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()

    d = find_topic(a.number); slug = d.name
    sc = load_scenario(d)
    lines = sc["lines"]
    if not sc["topic"].get("wide"): check_script(lines)
    else: print("script:", sum(len(re.sub(r"\[[^\]]+\]", " ", t).split()) for _, t, _ in lines), "words (chapter of a long video)")
    script = script_text(lines)
    (d / "script.txt").write_text(script, encoding="utf-8")
    render = ["node", HERE / "engine" / "render.mjs", slug]
    stage = STAGES.index(a.start)

    # 1. voice (skipped when the script did not change)
    digest = hashlib.sha1((script + str(sc["topic"].get("voiceSpeed", SPEED)) + VOICE).encode()).hexdigest()[:12]
    stamp = d / ".voice-hash"
    if stage <= 0 and not (stamp.exists() and stamp.read_text() == digest and (d / "voice.mp3").exists()):
        if sc["topic"].get("oneTake", True):    # eigenaar 7 okt 2026: whole script in one take, the voice makes its own pauses
            one_take(d, lines, sc["topic"].get("voiceSpeed", SPEED))
            if sc["topic"].get("padSilence"): pad_silence(d, lines)
        else:
            run([sys.executable, REPO / "tools" / "xai_voiceover.py", d / "script.txt", "-o", d / "voice.mp3", "--proxy-auth",
                 "--speed", str(sc["topic"].get("voiceSpeed", SPEED)), "--voice", VOICE, "--soft-edges", "--timeline", d / "voice-times.tsv", "--cache-dir", d / ".voice-cache"])
        stamp.write_text(digest)
    if (d / "voice-times.tsv").exists():
        tm = timing_from_tsv(lines, parse_tsv(d / "voice-times.tsv"), sc["topic"].get("voOffset", 0.8))
        (d / "timing.json").write_text(json.dumps(tm, indent=1))

    if a.stills:
        times = a.times.split(",") if a.times else None
        if not times:
            run([*render, "timeline"])
            tl = json.loads((d / "timeline.json").read_text())["TL"]
            B = tl["beats"]
            times = [f"{x:.1f}" for x in (tl["titleIn"] + 1.5, (tl["titleOut"] + B["climax"]) / 2 - 8, (tl["titleOut"] + B["climax"]) / 2 + 4,
                                          B["climax"] + 1.5, B["climax"] + 4.5, B.get("fade", B["climax"] + 8) + 1)]
        run([*render, "stills", *times])
        contact_sheet(d, times)
        return

    # 2. render
    if stage <= 1:
        run([*render, "timeline"])
        run([*render, "video", d / "silent.mp4", a.workers])
    # 3. sound
    if stage <= 2:
        run([*render, "timeline"])
        run([sys.executable, HERE / "make_audio.py", d])
    # 4. final mp4, thumbnail, upload.json
    tl = json.loads((d / "timeline.json").read_text())["TL"]
    out = d / f"{slug}.mp4"
    video, audio = d / "silent.mp4", d / "mix.wav"
    hook = tl.get("hook")
    if hook:   # opening flash-forward: render it, put it in front, give it the sound of that moment
        if stage <= 2 or not (d / "hook.mp4").exists():
            run(["node", HERE / "engine" / "render.mjs", f"{slug}+hook", "video", d / "hook.mp4", a.workers])
        (d / "concat.txt").write_text(f"file '{d / 'hook.mp4'}'\nfile '{d / 'silent.mp4'}'\n")
        run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", d / "concat.txt", "-c", "copy", d / "with-hook.mp4"])
        dur = hook["dur"]
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", d / "sfx-bed.wav", "-i", d / "mix.wav", "-filter_complex",
             f"[0:a]atrim={hook['at']:.2f}:{hook['at'] + dur:.2f},asetpts=PTS-STARTPTS,aformat=sample_rates=44100:channel_layouts=stereo,volume=2.2,"
             f"afade=t=in:d=0.15,afade=t=out:st={dur - .25:.2f}:d=0.25[h];[1:a]aformat=sample_rates=44100:channel_layouts=stereo[m];"
             f"[h][m]concat=n=2:v=0:a=1,alimiter=limit=0.89:level=false[o]", "-map", "[o]", d / "final-mix.wav"])
        video, audio = d / "with-hook.mp4", d / "final-mix.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", audio,
         *([] if sc["topic"].get("wide") else ["-vf", "scale=1080:1920:flags=lanczos"]), "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", out])
    (d / "check-bron.txt").write_text(audio.name)
    up = dict(sc["upload"]); up["question"] = sc["topic"]["question"]; up["number"] = a.number; up["slug"] = slug
    (d / "upload.json").write_text(json.dumps(up, indent=1, ensure_ascii=False), encoding="utf-8")
    mb = out.stat().st_size / 1e6
    print(f"ready: {out} ({mb:.1f} MB), {d / 'upload.json'}  (Shorts: no thumbnail needed)")


if __name__ == "__main__":
    main()
