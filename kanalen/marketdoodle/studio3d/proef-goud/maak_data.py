"""zinnen.json + woorden.json -> data.json voor scene.html ({Z, WO, EIND, FPS}).
Zonder stem (--nep): schatting uit script.txt, om het beeld alvast te testen."""
import json, sys
from pathlib import Path
H = Path(__file__).parent
if "--nep" in sys.argv:
    zinnen, sc, t = [], None, 0.5
    for r in (H / "script.txt").read_text(encoding="utf-8").splitlines():
        r = r.strip()
        if not r or r.startswith("#"): continue
        if r.startswith("@scene"): sc = r.split()[1]; continue
        d = len(r.split()) * 0.33; zinnen.append([round(t, 2), round(t + d, 2), r, sc]); t += d + 0.8
    woorden = []
    for i, (s, e, z, _) in enumerate(zinnen):
        w = z.split(); st = (e - s) / len(w)
        woorden += [[i, x, round(s + k * st, 2), round(s + (k + 1) * st, 2)] for k, x in enumerate(w)]
else:
    zinnen = json.load(open(H / "zinnen.json", encoding="utf-8"))
    woorden = json.load(open(H / "woorden.json", encoding="utf-8"))
eind = round(zinnen[-1][1] + 1.4, 2)
json.dump({"Z": zinnen, "WO": woorden, "EIND": eind, "FPS": 30}, open(H / "data.json", "w", encoding="utf-8"), ensure_ascii=False)
print("data.json", eind, "s")
