"""Meet hoe goed het beeldmodel (Qwen2.5-VL) foute beelden vangt: N afgekeurde en N goedgekeurde beelden
(willekeurig uit stories/*/afgekeurd en afbeeldingen). Gebruik: python tools/beeldcheck_vlmtest.py [N]"""
import random, re, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import beeldcheck as bc

S = HIER.parent / "stories"
n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
slecht = [(p, m) for m in S.iterdir() if (m / "afgekeurd").is_dir() for p in (m / "afgekeurd").glob("*.png")]
goed = [(p, m) for m in S.iterdir() if (m / "afgekeurd").is_dir() for p in (m / "afbeeldingen").glob("*.png")]
random.seed(7)
uit = {}
for naam, groep in (("afgekeurd", random.sample(slecht, min(n, len(slecht)))), ("goed", random.sample(goed, min(n, len(goed))))):
    hits = 0
    for p, m in groep:
        j = bc.jaar(m)
        f = bc.vlm(p, "a calm, realistic historical scene", f"the year {j}" if j > 0 else f"{-j} BC")
        hits += bool(f)
        print(f"  {naam:9} {m.name[:12]:12} {p.name}: {f}", flush=True)
    uit[naam] = (hits, len(groep))
bc.vlm_vrij()
print(f"VLM keurt af: {uit['afgekeurd'][0]}/{uit['afgekeurd'][1]} van de foute beelden, "
      f"{uit['goed'][0]}/{uit['goed'][1]} van de goede beelden (onterecht)")
