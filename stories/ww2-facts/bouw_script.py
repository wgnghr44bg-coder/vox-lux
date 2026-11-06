#!/usr/bin/env python3
"""Zet src/deel*.txt (IMG/HEAD/BODY per feitje) om in het stem-script met [pause]/[long-pause] en {img:..}."""
import re
from pathlib import Path
d = Path(__file__).parent
# Opbouw zoals Sleepy History (eigenaar 6 nov 2026): overzicht, abonneren, kort ontspannen, "Let's begin";
# einde: samenvatting, beeld laten wegzakken, "niets hoeven onthouden", volgende video + abonneren, adem, slaap.
OPEN = []   # eigenaar 7 nov 2026: geen "Tonight..."-intro meer, meteen beginnen met het eerste feitje
CLOSE = ["And that brings our quiet journey through the war years to a close.",
         "[pause]",
         "The wireless sets fall silent, the blackout curtains are drawn back, and the long years settle gently into memory.",
         "[long-pause]",
         "If you are still awake, another quiet story is waiting for you on the screen. And if you enjoyed this one, you are always welcome to subscribe.",
         "[pause]",
         "Sleep well, and good night."]
facts = []
tsv = ["slug\tonderwerp"]
for n in range(1, 7):
    for blk in (d / "src" / f"deel{n}.txt").read_text(encoding="utf-8").split("\n===\n"):
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
(d / "afbeeldingen-onderwerpen.tsv").write_text("\n".join(tsv) + "\n", encoding="utf-8")
txt = (d / "script-cues.txt").read_text(encoding="utf-8")
sp = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", txt)
print(len(facts), "feitjes;", len(re.sub(r"\s+", " ", sp)), "gesproken tekens;", txt.count("{img:"), "beelden")
