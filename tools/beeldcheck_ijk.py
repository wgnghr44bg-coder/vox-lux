"""Stelt de CLIP-drempels van tools/beeldcheck.py af op echte voorbeelden: de afgekeurde beelden (afgekeurd/) en de
goedgekeurde beelden (afbeeldingen/) van Tombstone en Egypte. Kiest per soort de drempel zodat hooguit ± 4% van de goede
beelden onterecht wordt afgekeurd, en meet hoeveel foute beelden CLIP, de VLM en beide samen vangen.

  python tools/beeldcheck_ijk.py [--vlm 40]      # --vlm N: ook de VLM testen op N foute en N goede beelden
"""
import json, random, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import beeldcheck as bc

S = HIER.parent / "stories"
sets = {"tombstone-1881": 1881, "egypte-toetanchamon": -1323}
fout, goed = [], []
for m, j in sets.items():
    fout += [(p, j, m) for p in sorted((S / m / "afgekeurd").glob("*.png"))]
    goed += [(p, j, m) for p in sorted((S / m / "afbeeldingen").glob("*.png"))]
print(len(fout), "afgekeurd,", len(goed), "goedgekeurd")

sc = {}
for groep in (fout, goed):
    for m, j in sets.items():
        ps = [p for p, jj, mm in groep if mm == m]
        for p, s in zip(ps, bc.clip_scores(ps, j)):
            sc[p] = s
drempels = {}
for k in ("modern", "tekst", "vervormd"):
    g = sorted(sc[p][k] for p, _, _ in goed)
    drempels[k] = round(g[int(len(g) * 0.96)], 4)
(HIER / "beeldcheck_drempels.json").write_text(json.dumps(drempels, indent=1), encoding="utf-8")
bc.DREMPELS = drempels
clip_vangt = {p for p, _, _ in fout if bc.clip_fout(sc[p])}
clip_vals = {p for p, _, _ in goed if bc.clip_fout(sc[p])}
print("drempels", drempels)
print(f"CLIP vangt {len(clip_vangt)}/{len(fout)} foute, keurt {len(clip_vals)}/{len(goed)} goede onterecht af")

if "--vlm" in sys.argv:
    n = int(sys.argv[sys.argv.index("--vlm") + 1])
    random.seed(1)
    vf, vg = random.sample(fout, min(n, len(fout))), random.sample(goed, min(n, len(goed)))
    vangt = beide = 0
    for p, j, m in vf:
        f = bc.vlm(p, "a calm historical scene", f"the year {j}" if j > 0 else f"{-j} BC")
        vangt += bool(f)
        beide += bool(f) or p in clip_vangt
        print("  fout ", p.name, f, flush=True)
    vals = 0
    for p, j, m in vg:
        f = bc.vlm(p, "a calm historical scene", f"the year {j}" if j > 0 else f"{-j} BC")
        vals += bool(f)
        print("  goed ", p.name, f, flush=True)
    print(f"VLM vangt {vangt}/{len(vf)} foute, keurt {vals}/{len(vg)} goede onterecht af; "
          f"VLM of CLIP samen vangt {beide}/{len(vf)} foute")
    bc.vlm_vrij()
