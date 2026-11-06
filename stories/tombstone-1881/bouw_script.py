#!/usr/bin/env python3
"""Zet src-feiten/deel*.txt (90 feitjes, één per bestaand beeld 001-090) (IMG/HEAD/BODY per feitje) om in het stem-script met [pause]/[long-pause] en {img:..}."""
import re
from pathlib import Path
d = Path(__file__).parent
# Opbouw zoals Sleepy History (eigenaar 6 nov 2026): overzicht, abonneren, kort ontspannen, "Let's begin";
# einde: samenvatting, beeld laten wegzakken, "niets hoeven onthouden", volgende video + abonneren, adem, slaap.
# Feitjes-opbouw (eigenaar 6-7 nov 2026), korte intro en outro, per video anders verwoord.
OPEN = ["Tonight we are going nearly a hundred and fifty years back, to a silver town on a high desert mesa in Arizona.",
        "[pause]",
        "In just a few years, Tombstone grew from a lonely prospector's camp into one of the liveliest towns in the West, with mines and theatres, newspapers and saloons, and one famous afternoon in October 1881.",
        "[pause]",
        "If you'd like more quiet history like this, you're welcome to subscribe. Now get comfortable, let the day go, and simply drift along.",
        "[long-pause]"]
CLOSE = ["And there our quiet visit to Tombstone comes to an end.",
         "[pause]",
         "The lamps along Allen Street are dimming, the wind moves softly over the mesa, and the old town settles into the night.",
         "[long-pause]",
         "If you're still awake, another calm story should be waiting for you on the screen. And if you enjoyed this one, subscribing helps others find their way here.",
         "[pause]",
         "Sleep well, and good night."]
facts = []
tsv = ["slug\tonderwerp"]
for n in range(1, 4):
    for blk in (d / "src-feiten" / f"deel{n}.txt").read_text(encoding="utf-8").split("\n===\n"):
        blk = blk.strip()
        if not blk: continue
        img = re.search(r"^IMG:\s*(.+?)\s*\|\s*(.+)$", blk, re.M)
        head = re.search(r"^HEAD:\s*(.+)$", blk, re.M).group(1).strip()
        body = re.search(r"^BODY:\s*(.+)$", blk, re.M | re.S).group(1).strip()
        facts.append((img.group(1), img.group(2), head, body))
out = []
for i, (slug, desc, head, body) in enumerate(facts):
    slug = f"{i+1:02d}-" + re.sub(r"[^a-z0-9-]", "", slug.lower().replace(" ", "-"))
    tsv.append(f"{slug}\t{desc}")
    if i == 0:
        out += [f"{{img:{slug}}}"] + OPEN
    else:
        out.append(f"{{img:{slug}}}")
    out += [head, "[pause]"]
    sents = re.split(r"(?<=[.!?])\s+", re.sub(r"\s+", " ", body))
    out.append(" ".join(sents))
    out.append("[long-pause]")
out += CLOSE
(d / "script-cues.txt").write_text("\n\n".join(out) + "\n", encoding="utf-8")
txt = (d / "script-cues.txt").read_text(encoding="utf-8")
sp = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", txt)
print(len(facts), "feitjes;", len(re.sub(r"\s+", " ", sp)), "gesproken tekens;", txt.count("{img:"), "beelden")
