#!/usr/bin/env python3
"""Bouwt het stem-script volgens stories/OPBOUW.md (eigenaar 7 nov 2026):
begin.txt  ->  onderwerpen (TOPIC + BRIDGE) met feitjes (IMG/HEAD/BODY)  ->  slot.txt.

Gebruik: python tools/bouw_feiten.py stories/<map> [--src src-feiten]
Schrijft <map>/script-cues.txt ({img:NN-slug}, [pause], [long-pause]) en <map>/hoofdstukken.tsv
(hoofdstuktitel <TAB> NN-slug van het eerste beeld), dat maak_motion.py gebruikt voor de hoofdstukken.
Het begin klinkt over beeld 1, de BRIDGE over het eerste beeld van het nieuwe onderwerp.
"""
import argparse, re
from pathlib import Path

ap = argparse.ArgumentParser()
ap.add_argument("map", type=Path)
ap.add_argument("--src", default=None, help="map met begin.txt, deel*.txt, slot.txt (standaard src-feiten, anders src)")
a = ap.parse_args()
d = a.map
src = d / (a.src or ("src-feiten" if (d / "src-feiten").exists() else "src"))


def alineas(p):
    if not p.exists():
        return []
    blokken = [" ".join(b.split()) for b in re.split(r"\n\s*\n", p.read_text(encoding="utf-8").strip()) if b.strip()]
    uit = []
    for b in blokken:
        uit += [b, "[pause]"]
    return uit[:-1]


delen = sorted(src.glob("deel*.txt"), key=lambda p: int(re.sub(r"\D", "", p.stem) or 0))
out, hoofdstukken, nr, wacht_topic, wacht_bridge = [], [], 0, None, None
begin = alineas(src / "begin.txt")
for p in delen:
    for blk in p.read_text(encoding="utf-8").split("\n===\n"):
        blk = blk.strip()
        if not blk:
            continue
        t = re.search(r"^TOPIC:\s*(.+)$", blk, re.M)
        if t:
            wacht_topic = t.group(1).strip()
            b = re.search(r"^BRIDGE:\s*(.+)$", blk, re.M | re.S)
            wacht_bridge = " ".join(b.group(1).split()) if b else None
            continue
        img = re.search(r"^IMG:\s*(.+?)\s*\|", blk, re.M).group(1)
        head = re.search(r"^HEAD:\s*(.+)$", blk, re.M).group(1).strip()
        body = " ".join(re.search(r"^BODY:\s*(.+)$", blk, re.M | re.S).group(1).split())
        nr += 1
        slug = f"{nr:02d}-" + re.sub(r"[^a-z0-9-]", "", img.lower().replace(" ", "-"))
        out.append(f"{{img:{slug}}}")
        if nr == 1 and begin:
            out += begin + ["[long-pause]"]
        if wacht_topic or nr == 1:
            hoofdstukken.append((wacht_topic or "Introduction", slug))
        if wacht_bridge and nr > 1:
            out += [wacht_bridge, "[pause]"]
        wacht_topic = wacht_bridge = None
        out += [head, "[pause]", body, "[long-pause]"]
out += alineas(src / "slot.txt")

# Beeldprompts voor comfy (tools/comfy/comfy_batch.py leest prompts.txt): alleen als er src/stijl.txt is (de vaste
# stijlzin voor dit onderwerp, bv. "A scene from Gettysburg in 1863 ... no text, no letters"). Bestaande video's
# (ww2-facts, tombstone, egypte) hebben hun beelden al en geen stijl.txt: daar verandert niets.
if (src / "stijl.txt").exists():
    stijl = " ".join((src / "stijl.txt").read_text(encoding="utf-8").split())
    beelden = []
    for p in delen:
        for blk in p.read_text(encoding="utf-8").split("\n===\n"):
            im = re.search(r"^IMG:\s*(.+?)\s*\|\s*(.+)$", blk.strip(), re.M)
            if im:
                beelden.append((re.sub(r"[^a-z0-9-]", "", im.group(1).lower().replace(" ", "-")), im.group(2).strip()))
    (d / "prompts.txt").write_text(f"# {d.name} - Z-Image Turbo, 1280x720\n" + "".join(
        f"{i:03d}|{b}, {stijl}\n" for i, (s, b) in enumerate(beelden, 1)), encoding="utf-8")
    (d / "afbeeldingen-onderwerpen.tsv").write_text("file\tslug\tprompt\n" + "".join(
        f"{i:03d}.png\t{s}\t{b}\n" for i, (s, b) in enumerate(beelden, 1)), encoding="utf-8")
    print(f"prompts.txt + afbeeldingen-onderwerpen.tsv: {len(beelden)} beelden")
(d / "script-cues.txt").write_text("\n\n".join(out) + "\n", encoding="utf-8")
(d / "hoofdstukken.tsv").write_text("".join(f"{t}\t{s}\n" for t, s in hoofdstukken), encoding="utf-8")
txt = (d / "script-cues.txt").read_text(encoding="utf-8")
woorden = len(re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", " ", txt).split())
print(f"{nr} feitjes, {len(hoofdstukken)} onderwerpen, {woorden} woorden, begin {'ja' if begin else 'NEE'}, "
      f"slot {'ja' if (src / 'slot.txt').exists() else 'NEE'}")
