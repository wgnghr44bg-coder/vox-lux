#!/usr/bin/env python3
"""Zet src/01..07.txt (alinea's, '---' = lange pauze, {img:slug}) om in het stem-script met [pause]/[long-pause]."""
import re
from pathlib import Path
d = Path(__file__).parent
out, prev_text = [], False
for n in range(1, 8):
    for line in (d / "src" / f"{n:02d}.txt").read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("{img:"):
            out.append(line); prev_text = False
        elif line == "---":
            out.append("[long-pause]"); prev_text = False
        else:
            if prev_text:
                out.append("[pause]")
            out.append(line); prev_text = True
    prev_text = prev_text  # tussen delen: [pause]
txt = "\n\n".join(out) + "\n"
(d / "the-dyatlov-pass-mystery.txt").write_text(txt)
slugs = re.findall(r"\{img:([^}]*)\}", txt)
sp = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", txt)
print(len(slugs), "beelden;", len(re.sub(r"\s+", " ", sp)), "gesproken tekens")
(d / "slugs.txt").write_text("\n".join(slugs) + "\n")
