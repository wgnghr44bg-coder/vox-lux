"""Is een script makkelijk te volgen? Telt woorden per zin en komma's per zin.
Gebruik: python tools/script_leesbaar.py stories/<map> [stories/<map> ...]
GOED = gemiddeld hooguit 19 woorden en 2,5 komma's per zin (zoals stories/tombstone-1881).
"""
import re, sys
from pathlib import Path

for d in sys.argv[1:]:
    d = Path(d)
    f = d / "script-cues.txt"
    t = f.read_text(encoding="utf-8") if f.exists() else "\n".join(x.read_text(encoding="utf-8") for x in sorted((d / "src").glob("[0-9]*.txt")))
    t = re.sub(r"\{[^}]*\}|\[[^\]]*\]", "", t)
    zinnen = [z for z in re.split(r"(?<=[.!?])\s+", t) if z.strip()]
    w, k = len(t.split()) / len(zinnen), t.count(",") / len(zinnen)
    print(f"{d.name}: {w:.1f} woorden/zin, {k:.1f} komma's/zin -> {'GOED' if w <= 19 and k <= 2.5 else 'TE DRUK, zinnen korter en minder opsommingen'}")
