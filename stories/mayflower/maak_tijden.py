#!/usr/bin/env python3
"""Zet voice-times.tsv (Chatterbox, tijden in s) om naar de bestanden van de vaste montage (zoals Titanic):
tijdlijn.tsv (H:MM:SS.s), afbeeldingen-tijden.tsv (001.png ...) en audio/mayflower-deel1.mp3
(kopie van voice-192k.mp3, de beste kwaliteit; niet in git). Daarna: tools/add_pauses.py, make_video.py, motion.py.
"""
import csv, shutil, subprocess
from pathlib import Path

import imageio_ffmpeg

d = Path(__file__).parent


def hms(x):
    h, rest = divmod(x, 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}"


rows = [l.split("\t") for l in (d / "voice-times.tsv").read_text(encoding="utf-8").splitlines()[1:] if l.strip()]
files = {r["slug"]: r["file"] for r in csv.DictReader(open(d / "afbeeldingen-onderwerpen.tsv", encoding="utf-8"), delimiter="\t")}

with open(d / "tijdlijn.tsv", "w", encoding="utf-8") as f:
    f.write("#\tstart\tend\timage\ttext\n")
    for r in rows:
        f.write("\t".join([r[0], hms(float(r[1])), hms(float(r[2]))] + r[3:]) + "\n")

src = d / "voice-192k.mp3"
if not src.exists():
    src = d / "voice.mp3"
(d / "audio").mkdir(exist_ok=True)
shutil.copyfile(src, d / "audio" / "mayflower-deel1.mp3")
out = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(src)], capture_output=True, text=True).stderr
h, m, s = out.split("Duration: ")[1].split(",")[0].split(":")
end = int(h) * 3600 + int(m) * 60 + float(s)

cues = [(float(r[1]), r[3]) for r in rows if r[3]]
cues[0] = (0.0, cues[0][1])
volgorde = [files[slug] for _, slug in cues]
assert volgorde == sorted(files.values()), "cues niet in de volgorde 001..084"
with open(d / "afbeeldingen-tijden.tsv", "w", encoding="utf-8") as f:
    f.write("file\tstart\tend\tslug\n")
    for i, (start, slug) in enumerate(cues):
        stop = cues[i + 1][0] if i + 1 < len(cues) else end
        f.write(f"{files[slug]}\t{start:.2f}\t{stop:.2f}\t{slug}\n")
print(f"{len(rows)} zinnen, {len(cues)} beelden, stem {hms(end)} ({src.name})")
