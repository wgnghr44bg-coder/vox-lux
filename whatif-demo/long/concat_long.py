#!/usr/bin/env python3
"""Glue rendered chapters (topics/<slug>/<slug>.mp4, made with make_whatif.py) into one long video
with a short cross-fade (picture and sound) between chapters.

    python3 whatif-demo/long/concat_long.py long/wind-never-stopped/wind-never-stopped.mp4 wind-1-street wind-2-boulevard wind-3-river
"""
import json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
XF = 1.0   # seconds of cross-fade


def dur(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(p)], capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def main():
    out, slugs = HERE / sys.argv[1], sys.argv[2:]
    files = [HERE / "topics" / s / f"{s}.mp4" for s in slugs]
    ins = sum([["-i", str(f)] for f in files], [])
    v, a, fc, t = "[0:v]", "[0:a]", [], 0.0
    for i in range(1, len(files)):
        t += dur(files[i - 1]) - XF
        fc.append(f"{v}[{i}:v]xfade=transition=fade:duration={XF}:offset={t:.3f}[v{i}]")
        fc.append(f"{a}[{i}:a]acrossfade=d={XF}[a{i}]")
        v, a = f"[v{i}]", f"[a{i}]"
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", ";".join(fc), "-map", v, "-map", a,
                    "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", str(out)], check=True)
    print("ready:", out, f"{dur(out):.1f}s")


if __name__ == "__main__":
    main()
