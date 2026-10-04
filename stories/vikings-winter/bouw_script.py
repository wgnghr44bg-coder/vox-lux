#!/usr/bin/env python3
"""Zet src/deel*.txt (IMG/HEAD/BODY per feitje) om in het stem-script met [pause]/[long-pause] en {img:..}."""
import re
from pathlib import Path
d = Path(__file__).parent
OPEN = ["Tonight we are going about eleven hundred years back, to the cold north of Scandinavia, where the Viking farms lie quiet under the first snow.",
        "[long-pause]",
        "On a small farm beside a grey fjord, a family is carrying the last armfuls of firewood in from the yard.",
        "[long-pause]"]
CLOSE = ["And so our long winter comes to its end. The snow has gone from the fields, the fjord is open, and a family steps out into the thin spring sun.",
         "[long-pause]",
         "If you enjoyed this quiet journey, you are welcome to subscribe. It helps other sleepy listeners find their way here.",
         "[long-pause]",
         "There should be another quiet story waiting on the screen now, if you are still awake.",
         "[long-pause]",
         "Sleep well, and good night."]
facts = []
tsv = ["slug\tonderwerp"]
for n in range(1, 7):
    for blk in (d / "src" / f"deel{n}.txt").read_text().split("\n===\n"):
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
(d / "how-vikings-survived-the-long-dark-winter.txt").write_text("\n\n".join(out) + "\n")
(d / "afbeeldingen-onderwerpen.tsv").write_text("\n".join(tsv) + "\n")
txt = (d / "how-vikings-survived-the-long-dark-winter.txt").read_text()
sp = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", txt)
print(len(facts), "feitjes;", len(re.sub(r"\s+", " ", sp)), "gesproken tekens;", txt.count("{img:"), "beelden")
