#!/usr/bin/env python3
"""Zet src/NN-*.txt om in script-cues.txt (stem) en src/beelden.tsv in prompts.txt (comfy, Z-Image Turbo).

Beelden heten 001, 002, ... in volgorde van het script (afbeeldingen/001.png); de koppeling naam -> nummer
staat in afbeeldingen-onderwerpen.tsv.
"""
import re
from pathlib import Path

d = Path(__file__).parent
STYLE = ("Strictly historical scene from the year 1620 with nothing modern at all: no cars or motor vehicles, no signs, "
         "no notice boards, no street lamps, no power lines, no drainpipes, no modern windows, no mown lawns, no modern clothes. "
         "Cinematic realistic photograph, wide 16:9 landscape, soft natural light, gentle atmospheric haze, "
         "calm and peaceful mood, historically accurate early 17th century, highly detailed, "
         "no blood, nothing frightening, no text, no words, no letters, no logos")

parts = sorted(p for p in (d / "src").glob("*.txt"))
script = "\n\n[long-pause]\n\n".join(p.read_text(encoding="utf-8").strip() for p in parts) + "\n"
(d / "script-cues.txt").write_text(script, encoding="utf-8")

beschrijving = dict(l.split("\t", 1) for l in (d / "src" / "beelden.tsv").read_text(encoding="utf-8").splitlines() if l.strip())
volgorde = re.findall(r"\{img:([^}]+)\}", script)
missing = [s for s in volgorde if s not in beschrijving]
if missing:
    raise SystemExit(f"Geen beschrijving voor: {missing}")
prompts, tsv = [], ["file\tslug\tonderwerp"]
for i, slug in enumerate(volgorde, 1):
    prompts.append(f"{i:03d}|{beschrijving[slug].strip()}, {STYLE}")
    tsv.append(f"{i:03d}.png\t{slug}\t{beschrijving[slug].strip()}")
(d / "prompts.txt").write_text("# Life Aboard the Mayflower, 1620 - Z-Image Turbo, 1280x720\n" + "\n".join(prompts) + "\n", encoding="utf-8")
(d / "afbeeldingen-onderwerpen.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
spoken = re.sub(r"\{img:[^}]*\}|\[[^\]]*\]", "", script)
print(f"{len(parts)} hoofdstukken, {len(volgorde)} beelden, {len(spoken.split())} woorden, {len(spoken):,} tekens gesproken")
