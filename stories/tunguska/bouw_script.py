#!/usr/bin/env python3
"""Zet src/*.txt (zin per regel, lege regel = lange pauze) om in het stem-script
met [pause] / [long-pause] en {img:...}-regels."""
import re, sys
from pathlib import Path
d = Path(__file__).parent
out = []
for f in sorted((d / "src").glob("*.txt")):
    chunks = []
    for line in f.read_text().split("\n"):
        line = line.strip()
        if not line:
            chunks.append("[long-pause]")
        elif line.startswith("{img:"):
            chunks.append(line)
        else:
            chunks.append(line)
            chunks.append("[pause]")
    # [pause] voor een lege regel/ beeld/ eind wordt weggelaten
    res = []
    for c in chunks:
        if c == "[long-pause]" and res and res[-1] == "[pause]":
            res.pop()
        if c.startswith("{img:") and res and res[-1] == "[pause]":
            res.pop()
            if not (len(res) >= 1 and res[-1] == "[long-pause]"):
                res.append("[long-pause]")
        if c == "[long-pause]" and res and res[-1] == "[long-pause]":
            continue
        res.append(c)
    while res and res[-1] in ("[pause]", "[long-pause]"):
        res.pop()
    out += res + ["[long-pause]"]
while out and out[-1] == "[long-pause]":
    out.pop()
text = "\n\n".join(out) + "\n"
(d / "the-tunguska-event.txt").write_text(text)
spoken = re.sub(r"\{img:[^}]*\}|\[[a-z-]*pause\]", "", text)
print(len(text), "tekens in script;", len(re.sub(r"\s+", " ", spoken)), "gesproken tekens;", text.count("{img:"), "beelden")
