#!/usr/bin/env python3
"""Zet src/NN-*.txt om in script-cues.txt (stem) en src/beelden.tsv in prompts.txt (comfy, Z-Image Turbo).

In src: alinea's gescheiden door een lege regel (= [pause]), een regel "--" = [long-pause], "{img:naam}" = nieuw beeld.
Beelden heten 001, 002, ... in volgorde van het script; de koppeling naam -> nummer staat in afbeeldingen-onderwerpen.tsv.
"""
import re
from pathlib import Path

d = Path(__file__).parent
STYLE = ("A scene from the year 1937, the age of the great passenger airships: no modern technology, no cars from after 1940, "
         "no modern buildings, no modern clothes. "
         "Cinematic realistic photograph, wide 16:9, soft natural light, gentle atmospheric haze, "
         "calm and peaceful mood, historically accurate 1930s, highly detailed, "
         "no fire, no flames, no smoke, no blood, nothing frightening, no text, no words, no letters, no logos, no flags, no symbols")


def omzetten(tekst):
    uit = []
    for blok in re.split(r"\n\s*\n", tekst.strip()):
        blok = blok.strip()
        if blok == "--":
            uit[-1] = "[long-pause]"
            continue
        uit += [blok, "[pause]"]
    if uit and uit[-1] == "[pause]":
        uit.pop()
    return "\n\n".join(uit)


parts = sorted((d / "src").glob("*.txt"))
script = "\n\n[long-pause]\n\n".join(omzetten(p.read_text(encoding="utf-8")) for p in parts) + "\n"
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
(d / "prompts.txt").write_text("# Life Aboard the Hindenburg, May 1937 - Z-Image Turbo, 1280x720\n" + "\n".join(prompts) + "\n", encoding="utf-8")
(d / "afbeeldingen-onderwerpen.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
spoken = re.sub(r"\{img:[^}]*\}|\[[^\]]*\]", "", script)
print(f"{len(parts)} hoofdstukken, {len(volgorde)} beelden, {len(spoken.split())} woorden, {len(spoken):,} tekens gesproken")
