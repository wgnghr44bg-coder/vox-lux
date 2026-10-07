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
        run([sys.executable, REPO / "tools" / "xai_voiceover.py", d / "script.txt", "-o", d / "voice.mp3", "--proxy-auth",
             "--speed", str(sc["topic"].get("voiceSpeed", SPEED)), "--voice", VOICE, "--timeline", d / "voice-times.tsv", "--cache-dir", d / ".voice-cache"])
        stamp.write_text(digest)
    if (d / "voice-times.tsv").exists():
        tm = timing_from_tsv(lines, parse_tsv(d / "voice-times.tsv"))
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
