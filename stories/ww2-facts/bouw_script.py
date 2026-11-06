#!/usr/bin/env python3
"""Zet src/deel*.txt (IMG/HEAD/BODY per feitje) om in het stem-script met [pause]/[long-pause] en {img:..}."""
import re
from pathlib import Path
d = Path(__file__).parent
# Opbouw zoals Sleepy History (eigenaar 6 nov 2026): overzicht, abonneren, kort ontspannen, "Let's begin";
# einde: samenvatting, beeld laten wegzakken, "niets hoeven onthouden", volgende video + abonneren, adem, slaap.
OPEN = ["Tonight we are going nearly ninety years back, to the years of the Second World War, from the late summer of 1939 to the quiet spring of 1945.",
        "[pause]",
        "It was a time of blackout curtains and ration books, of evacuated children and wireless sets glowing in the dark. Ordinary people found small ways to carry on. They queued, they mended, they grew vegetables in their gardens, and they wrote long letters to the people they missed.",
        "[pause]",
        "Over the next few hours, we will move gently from one small fact to the next. There is nothing you need to follow, and nothing you need to remember.",
        "[long-pause]",
        "If you enjoy these quiet journeys, you are welcome to subscribe. It helps other sleepy listeners find their way here.",
        "[pause]",
        "But for now, all you need to do is settle in. Let your shoulders drop. Let your breathing slow down, and let your eyes grow heavy.",
        "[long-pause]",
        "Let's begin.",
        "[long-pause]"]
CLOSE = ["And so, our long walk through the war years comes to its quiet end.",
         "[pause]",
         "We have listened to the wireless in small front rooms, waited out the long blackout nights, queued with ration books and watched the children come home again. We have seen how ordinary people kept going, one quiet day after another.",
         "[long-pause]",
         "Now those streets can slowly fade from view. The ration books can close, the curtains can open, and the church bells can ring softly on a Sunday morning, further and further away.",
         "[pause]",
         "There is no need to remember any of the names or the dates tonight.",
         "[long-pause]",
         "If you are still awake, there should be another quiet story waiting for you on the screen now. And if these journeys help you rest, subscribing helps other sleepy listeners find their way here.",
         "[long-pause]",
         "But for now, let your breathing settle into its own slow rhythm.",
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
