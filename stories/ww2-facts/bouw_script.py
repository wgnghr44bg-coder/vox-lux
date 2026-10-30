#!/usr/bin/env python3
"""Zet src/deel*.txt (IMG/HEAD/BODY per feitje) om in het stem-script met [pause]/[long-pause] en {img:..}."""
import re
from pathlib import Path
d = Path(__file__).parent
OPEN = ["Tonight we are going nearly ninety years back, to a quiet street in an English town, in the late summer of 1939.",
        "[long-pause]",
        "The hedges are heavy with blackberries, the milkman is on his round, and in the front rooms, the wireless sets are warming up.",
        "[pause]",
        "Over the next few hours, we will wander gently through the years of the Second World War, not through its battles, but through the everyday lives of ordinary people, at home and far away.",
        "[long-pause]",
        "If quiet history helps you drift off, you're welcome to subscribe.",
        "[pause]",
        "Now, let's begin.",
        "[long-pause]"]
CLOSE = ["And so our long walk through the war years comes to its quiet end. The lights are back on in the streets, the bells ring again on Sunday mornings, and somewhere a kettle is just coming to the boil.",
         "[long-pause]",
         "If these quiet facts kept you company tonight, subscribing helps other sleepy listeners find their way here.",
         "[long-pause]",
         "There should be another quiet story waiting on the screen now, if you are still awake.",
         "[long-pause]",
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
