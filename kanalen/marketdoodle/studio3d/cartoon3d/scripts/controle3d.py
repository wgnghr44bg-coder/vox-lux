"""Alle vaste Market Doodle-controles voor de 3D-video (eigenaar 27 nov: "vergeet de controles niet ook niet in deze nieuwe style").
Leest out/wachter3d.json (scripts/wachter3d.ts: per frame wat waar op het beeld staat, met dezelfde camera als de video) en draait:
  TEKSTWACHTER  gezien / spreker / gevoel / RIJDEN / DOEN  (tools/tekstwachter.py, ongewijzigd)
  LAYOUT        ondertitel mag geen gezicht bedekken (mensen én de kop van de haai)
  GELUIDCHECK   elk geluid in sfx.wav hoort bij iets dat op dat moment in beeld is
  SHORTREGELS   haak / lengte / loop (tools/shortregels.py)
  TEMPO         zelfde stem als de 2D-short -> uitslag van short-haai/TEMPOWACHTER.md
  LUIDHEID      -14 LUFS, true peak <= -1 dB
  TEKSTCONTROLE.jpg per zin begin/midden/eind (om zelf na te lopen)
Gebruik: python scripts/controle3d.py <video.mp4>"""
import json, re, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
REPO = HIER.parents[3]
sys.path.insert(0, str(REPO / "tools"))
from tekstwachter import Tekstwachter, blad
from shortregels import controleer

KORT = REPO / "kanalen" / "marketdoodle" / "short-haai"
Z = json.load(open(KORT / "zinnen.json", encoding="utf-8"))
WO = json.load(open(KORT / "woorden.json", encoding="utf-8"))
F = json.load(open(HIER / "out" / "wachter3d.json", encoding="utf-8"))
EIND = Z[-1][1] + 0.7
LIJF = {"YOU": "you", "DAD": "dad", "SIS": "sis"}
ZIE = {"shark": ["haai"], "big legs": ["haai"], "garage door": ["garagedeur"], "your sister": ["sis"], "walks to the fridge": ["koelkast", "haai"],
       "eats the whole fridge": ["koelkast"], "brand new fridge": ["dad"], "the sea": ["zee"], "beach": ["zee"], "scared of water": ["haai"],
       "bathtub": ["bad"], "night light": ["nachtlampje"], "nightlight": ["nachtlampje"], "nobody bullies": ["friend", "rich"]}
ACTIEF = 6        # controle-tempo: 6 beelden per seconde, zoals de 2D-renderer

def zin_op(t):
    for i, z in enumerate(Z):
        if z[0] - 0.05 <= t <= z[1] + 0.05: return i
    return None

def op_beeld(fr):
    """namen die echt in beeld zijn (kader binnen het beeld; koppen binnen het beeld)"""
    n = {v[0] for v in fr["voorwerpen"]}
    return n

uit = ["# Controles 3D-haai", ""]
fouten = 0
# ---------- tekstwachter ----------
TW = Tekstwachter(Z, ZIE, lijf=LIJF)
for fr in F[::30 // ACTIEF]:
    t = fr["t"]; nu = zin_op(t)
    kop = {k: (v[0], v[1]) for k, v in fr["koppen"].items() if 0 <= v[0] <= 1080 and 0 <= v[1] <= 1920}
    geb = {k: g for k, g in fr["gebaren"].items() if k in kop}
    TW.zie(t, nu, voorwerpen=[(n, tuple(b)) for n, b in fr["voorwerpen"]], koppen=kop, gebaren=geb, crop=(0, 0, 1080, 1920))
tw = TW.fouten(); fouten += len(tw)
uit += [f"## TEKSTWACHTER: {len(tw)} fouten"] + [f"- {t:.1f} s **{s}**: {x}" for t, s, x in tw] + [""]
# ---------- LAYOUT: ondertitel over een gezicht ----------
lay = {}
for fr in F:
    cb = fr["ondertitel"]
    if not cb: continue
    for naam, (cx, cy, r) in fr["koppen"].items():
        if not (0 <= cx <= 1080 and 0 <= cy <= 1920): continue
        m = r * 0.55                                      # het gezicht (ogen + mond), niet de hele kop
        if cb[0] < cx + m and cb[2] > cx - m and cb[1] < cy + m and cb[3] > cy - m:
            lay.setdefault(naam, []).append(fr["t"])
layf = []
for naam, ts in lay.items():
    reeks = [[ts[0], ts[0]]]
    for t in ts[1:]:
        if t - reeks[-1][1] < 0.1: reeks[-1][1] = t
        else: reeks.append([t, t])
    for a, b in reeks:
        if b - a >= 0.1: layf.append(f"{a:.1f}-{b:.1f} s: ondertitel bedekt het gezicht van {naam}")
fouten += len(layf)
uit += [f"## LAYOUT (gezichten): {len(layf)} fouten"] + [f"- {x}" for x in layf] + [""]
# ---------- geluid ----------
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    return Z[zin][0]
T_STAPJE, T_DEUR = kw(2, "step", -0.1), kw(2, "through", -0.1)
T_NAAR, T_EET = kw(5, "walks", -0.1), kw(5, "eats", -0.1)
T_ZEE, T_TERUG, T_LAMP = kw(7, "walks", -0.1), kw(7, "back", -0.4), kw(9, "night", -0.1)
G = [(T_STAPJE + 0.45, "bonk", "garagedeur"), (T_DEUR, "krak", "garagedeur")]
G += [(T_DEUR + 0.2 + 0.45 * k, "stap", "haai") for k in range(4)] + [(Z[3][0] + 0.2 + 0.45 * k, "stap", "haai") for k in range(7)]
G += [(T_NAAR + 0.1 + 0.45 * k, "stap", "haai") for k in range(4)] + [(T_EET + 0.4 * k, "hap", "haai") for k in range(3)]
G += [(T_EET + 1.3, "slok", "haai"), (T_ZEE + 1.2, "plons", "haai"), (T_TERUG + 0.1, "plons", "haai"), (T_LAMP, "klik", "nachtlampje")]
gf = []
for t, n, zie in G:
    fr = F[min(len(F) - 1, round((t + 0.15) * 30))]
    if zie not in op_beeld(fr): gf.append(f"{t:.1f} s: geluid '{n}' maar '{zie}' is niet in beeld")
fouten += len(gf)
uit += [f"## GELUIDCHECK: {len(gf)} fouten"] + [f"- {x}" for x in gf] + [""]
# ---------- shortregels ----------
start = [n for n in op_beeld(F[9]) if n not in ("garage",)]
sr = controleer(Z, EIND, voorwerpen_bij_start=start, woorden=WO); fouten += len(sr)
uit += [f"## SHORTREGELS: {len(sr)} fouten (in het eerste beeld: {', '.join(start)})"] + [f"- {x}" for x in sr] + [""]
# ---------- tempo (zelfde stem) ----------
tm = (KORT / "TEMPOWACHTER.md").read_text(encoding="utf-8") if (KORT / "TEMPOWACHTER.md").exists() else "(geen TEMPOWACHTER.md)"
regel = next((l for l in tm.splitlines() if "fout" in l.lower()), tm.splitlines()[0] if tm else "")
uit += ["## TEMPO (zelfde stem als de 2D-short)", f"- {regel.strip()}", ""]
# ---------- luidheid + blad ----------
if len(sys.argv) > 1:
    mp4 = Path(sys.argv[1])
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(mp4), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True, errors="replace").stderr
    I = re.findall(r"I:\s+(-?[\d.]+) LUFS", r); P = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", r)
    li, pk = float(I[-1]), float(P[-1]) if P else 0.0
    ok = -15.5 <= li <= -12.5 and pk <= -0.9
    if not ok: fouten += 1
    uit += [f"## LUIDHEID: {li:.1f} LUFS, true peak {pk:.1f} dB -> {'goed' if ok else 'FOUT'}", ""]
    blad(mp4, Z, HIER / "out" / "TEKSTCONTROLE.jpg")
    uit += ["TEKSTCONTROLE.jpg gemaakt (per zin begin/midden/eind).", ""]
uit.insert(1, f"**{fouten} fouten in totaal**")
(HIER / "out" / "CONTROLES3D.md").write_text("\n".join(uit) + "\n", encoding="utf-8")
print("\n".join(uit))
