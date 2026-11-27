"""Stemtempo (eigenaar 25 nov 2026: 161 woorden/min "stuk langzamer", 200 "wat te snel" -> "dit is goed": 180 voor Short en lange video).
Zet de stem (stem.wav + zinnen.json + woorden.json) per regel op het doeltempo van de VERTELLER, zonder opnieuw in te spreken
(ffmpeg atempo), ELKE REGEL APART naar het doel (26 nov: één vaste factor maakte het begin 154 en de rest 195-220 wpm); alleen zinnen boven 205 wpm worden iets trager (naar 200); lange stiltes (>= 1,5 s, zoals
STILTE|x) blijven gelijk. Origineel blijft bewaard als *.voor-sneller (opnieuw draaien gaat altijd vanaf het origineel).
  <omnivoice-venv>/python tools/stemtempo.py <map> [doel=180]     -> daarna tools/tempowachter.py <map>
"""
import json, subprocess, sys, shutil
from pathlib import Path
import numpy as np, soundfile as sf
M = Path(sys.argv[1]); DOEL = float(sys.argv[2]) if len(sys.argv) > 2 else 180
MERK = M / ".stemtempo.json"                            # zo weten we of stem.wav nog onze eigen uitvoer is
eigen = MERK.exists() and json.loads(MERK.read_text()).get("grootte") == (M / "stem.wav").stat().st_size
for f in ("stem.wav", "zinnen.json", "woorden.json"):
    b = M / (f + ".voor-sneller")
    if not b.exists() or not eigen: shutil.copy(M / f, b)  # nieuwe stem (stem.py opnieuw gedraaid) -> nieuwe reservekopie
A, sr = sf.read(M / "stem.wav.voor-sneller", dtype="float32")
Z = json.loads((M / "zinnen.json.voor-sneller").read_text(encoding="utf-8")); W = json.loads((M / "woorden.json.voor-sneller").read_text(encoding="utf-8"))
N = [z for z in Z if z[4] == "N"]; huidig = sum(len(z[2].split()) for z in N) / sum(z[1] - z[0] for z in N) * 60
print(f"verteller nu {huidig:.0f} wpm (regel-gemiddelde); doel per zin {195} binnen de zin")
tmp = M / "_seg"; tmp.mkdir(exist_ok=True)
MAX_ZIN, MIN_KORT = 210, 0.30                           # woorden/min binnen één zin (zonder pauzes); seconden per woord bij korte uitroepen
import re as _re
def gewicht(w):                                         # Whisper schrijft getallen als cijfers ("$312" = "three hundred and twelve dollars")
    c = _re.sub(r"[^0-9]", "", w)
    return 1 if not c else min(6, len(c) + (1 if "$" in w else 0) + (1 if "%" in w else 0))
def zin_wpm(i, z):                                      # tempo per zin binnen regel i (alleen zinnen van 3+ woorden), uit de Whisper-woordtijden
    ww = [w for w in W if w[0] == i]; uit_, cur = [], []
    for w in ww:
        cur.append(w)
        if _re.search(r"[.!?]$", w[1]) or w is ww[-1]:
            if len(cur) >= 3 and cur[-1][3] > cur[0][2]: uit_.append(len(cur) / (cur[-1][3] - cur[0][2]) * 60)
            cur = []
    return uit_
def rek(x, f):
    if abs(f - 1) < 0.005: return x
    sf.write(tmp / "a.wav", x, sr)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "a.wav"), "-af", f"atempo={f:.4f}", "-ar", str(sr), str(tmp / "b.wav")], check=True)
    y, _ = sf.read(tmp / "b.wav", dtype="float32"); return y
# 27 nov (eigenaar: "soms praat hij ineens te snel ... zorg dat dat niet meer voorkomt"): per regel rekken gaf binnen de verteller
# zinnen van 120 tot 218 woorden/min naast elkaar (sprongen). Nu PER ZIN: elke vertellerzin naar hetzelfde tempo (DOEL_ZIN binnen
# de zin, zonder pauzes); personages houden hun eigen tempo, alleen te snelle zinnen (> MAX_ZIN) worden trager.
DOEL_ZIN = 195
def zinstukken(i, z):                                   # [(t0, t1, wpm_of_None, woorden)] per zin; grenzen midden in de pauze
    ww = [w for w in W if w[0] == i]; groepen, cur = [], []
    for w in ww:
        cur.append(w)
        if _re.search(r"[.!?]$", w[1]) or w is ww[-1]: groepen.append(cur); cur = []
    if not groepen: return [(z[0], z[1], None, [])]
    grens = [z[0]] + [(a[-1][3] + b[0][2]) / 2 for a, b in zip(groepen, groepen[1:])] + [z[1]]
    uit_ = []
    for k, g in enumerate(groepen):
        r = sum(gewicht(w[1]) for w in g) / (g[-1][3] - g[0][2]) * 60 if len(g) >= 3 and g[-1][3] > g[0][2] else None
        uit_.append((max(z[0], grens[k]), min(z[1], grens[k + 1]), r, g))
    return uit_
uit = []; t = 0.0; nZ = []; nW = []; vorig_eind = 0.0
for i, z in enumerate(Z):
    gat = z[0] - vorig_eind
    if gat > 0: uit.append(np.zeros((int(round(gat * sr)),) + A.shape[1:], np.float32)); t += gat
    n = len(z[2].split()); stukken = zinstukken(i, z); lijn_t0 = t
    rs = [r for _, _, r, _ in stukken if r]; mid = sorted(rs)[len(rs) // 2] if rs else None
    for t0, t1, r, g in stukken:
        r = r or mid
        if z[4] == "N": f = min(1.45, max(0.75, DOEL_ZIN / r)) if r else 1.0
        else: f = (MAX_ZIN - 5) / r if r and r > MAX_ZIN else 1.0
        if n <= 3 and (z[1] - z[0]) / f < MIN_KORT * n: f = (z[1] - z[0]) / (MIN_KORT * n)   # korte uitroep niet afraffelen
        seg = rek(A[int(t0 * sr):int(t1 * sr)], f); nd = len(seg) / sr; sc = nd / max(1e-6, t1 - t0)
        for w in g: nW.append([w[0], w[1], round(t + (w[2] - t0) * sc, 3), round(t + (w[3] - t0) * sc, 3)])
        uit.append(seg); t += nd
    nZ.append([round(lijn_t0, 3), round(t, 3)] + z[2:]); vorig_eind = z[1]
staart = A[int(Z[-1][1] * sr):]; uit.append(staart)
sf.write(M / "stem.wav", np.concatenate(uit), sr)
(M / "zinnen.json").write_text(json.dumps(nZ, ensure_ascii=False), encoding="utf-8")
(M / "woorden.json").write_text(json.dumps(nW, ensure_ascii=False), encoding="utf-8")
shutil.rmtree(tmp); MERK.write_text(json.dumps({"grootte": (M / "stem.wav").stat().st_size, "doel": DOEL}))
NN = [z for z in nZ if z[4] == "N"]; print(f"klaar: verteller {sum(len(z[2].split()) for z in NN) / sum(z[1]-z[0] for z in NN) * 60:.0f} wpm, lengte {nZ[-1][1]:.0f} s")
