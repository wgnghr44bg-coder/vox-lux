#!/usr/bin/env python3
"""Zet src-feiten/deel1-3.txt (92 feitjes, één per bestaand beeld 001-092; blokken IMG/HEAD/BODY gescheiden door ===)
om in het stem-script script-cues.txt met [pause]/[long-pause] en {img:..}.
Feitjes-opbouw (eigenaar 6-7 nov 2026): geen intro (meteen het eerste feitje), kort slot, per video anders verwoord.
De oude verhaal-opbouw (src/NN-*.txt + beelden.tsv -> prompts.txt) staat nog in git-geschiedenis."""
import re
from pathlib import Path

d = Path(__file__).parent
OPEN = []   # eigenaar 7 nov 2026: geen "Tonight..."-intro meer, meteen beginnen met het eerste feitje
CLOSE = ["And so our quiet visit to the land of the young king draws to a close.",
         "[pause]",
         "The last light fades from the western cliffs, the little boats are tied up along the bank, and the old river carries on, slowly, into the dark.",
         "[long-pause]",
         "If you're still awake, another gentle story is waiting for you on the screen. And if you enjoyed this one, you're always welcome to subscribe, so you can find us again tomorrow night.",
         "[pause]",
         "Sleep well, and good night."]
facts = []
for n in range(1, 4):
    for blk in (d / "src-feiten" / f"deel{n}.txt").read_text(encoding="utf-8").split("\n===\n"):
        blk = blk.strip()
        if not blk:
            continue
        img = re.search(r"^IMG:\s*(.+?)\s*\|\s*(.+)$", blk, re.M)
        head = re.search(r"^HEAD:\s*(.+)$", blk, re.M).group(1).strip()
        body = re.search(r"^BODY:\s*(.+)$", blk, re.M | re.S).group(1).strip()
        facts.append((img.group(1), head, body))
out = []
for i, (slug, head, body) in enumerate(facts):
    out.append(f"{{img:{i + 1:02d}-{slug}}}")
    if i == 0:
        out += OPEN
    out += [head, "[pause]", " ".join(body.split()), "[long-pause]"]
out += CLOSE
(d / "script-cues.txt").write_text("\n\n".join(out) + "\n", encoding="utf-8")
txt = (d / "script-cues.txt").read_text(encoding="utf-8")
sp = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", txt)
print(len(facts), "feitjes;", len(sp.split()), "woorden;", txt.count("{img:"), "beelden")
