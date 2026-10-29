#!/usr/bin/env python3
"""Zet src/NN-*.txt om in script-cues.txt (stem) en src/beelden.tsv in prompts.txt (comfy, Z-Image Turbo).

In src: alinea's gescheiden door een lege regel (= [pause]), een regel "--" = [long-pause], "{img:naam}" = nieuw beeld.
Beelden heten 001, 002, ... in volgorde van het script; de koppeling naam -> nummer staat in afbeeldingen-onderwerpen.tsv.
"""
import re
from pathlib import Path

d = Path(__file__).parent
STYLE = ("Film still from a historical drama set in 1846 on the untouched American frontier, deep wilderness where no town and no farm exists for hundreds of miles, "
         "the horizon is only empty natural land and sky. Realistic cinematic photography, wide 16:9, soft natural light, gentle haze, calm and peaceful, "
         "historically accurate 1840s clothing and wooden wagons, highly detailed")
# Scenes in a town, fort, cabin or the present day: no "wilderness" (Z-Image has no negative prompt, so "no cars" puts cars in).
STYLE_PLEK = ("Film still from a historical drama, everything around is only what is described in the scene and untouched natural land. "
              "Realistic cinematic photography, wide 16:9, soft natural light, gentle haze, calm and peaceful, historically accurate, highly detailed")
PLEK = set("""independence-square-spring outfitters-store-counter blacksmith-wagon-wheel farm-family-reading-letter young-parkman-st-louis-levee
reed-family-wagon-illinois fort-laramie-adobe-walls fort-bridger-log-post fort-hall-white-walls fort-boise-river-evening whitman-mission-house-orchard
the-dalles-mission-camp oregon-city-falls-cabins salem-cabin-christmas-rain picayune-coin-in-glove building-log-cabin-autumn winter-rain-cabin-fireside
spring-ploughing-new-farm summer-wheat-harvest-valley choosing-land-claim-meadow railroad-across-plains deep-wagon-ruts-sandstone independence-rock-today
oregon-farm-valley-today snowy-sierra-mountains-distance sam-barlow-forest-road""".split())


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
    prompts.append(f"{i:03d}|{beschrijving[slug].strip()}, {STYLE_PLEK if slug in PLEK else STYLE}")
    tsv.append(f"{i:03d}.png\t{slug}\t{beschrijving[slug].strip()}")
(d / "prompts.txt").write_text("# Life on the Oregon Trail, 1846 - Z-Image Turbo, 1280x720\n" + "\n".join(prompts) + "\n", encoding="utf-8")
(d / "afbeeldingen-onderwerpen.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
spoken = re.sub(r"\{img:[^}]*\}|\[[^\]]*\]", "", script)
print(f"{len(parts)} hoofdstukken, {len(volgorde)} beelden, {len(spoken.split())} woorden, {len(spoken):,} tekens gesproken")
