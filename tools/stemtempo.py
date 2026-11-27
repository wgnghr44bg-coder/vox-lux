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
F = DOEL / huidig; print(f"verteller nu {huidig:.0f} wpm -> factor {F:.3f}")
tmp = M / "_seg"; tmp.mkdir(exist_ok=True)
MAX_ZIN, MIN_KORT = 210, 0.30                           # woorden/min binnen één zin (zonder pauzes); seconden per woord bij korte uitroepen
import re as _re
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
uit = []; t = 0.0; nZ = []; nW = []; vorig_eind = 0.0
for i, z in enumerate(Z):
    gat = z[0] - vorig_eind
    ng = gat if gat >= 1.5 else gat / F
    if ng > 0: uit.append(np.zeros((int(round(ng * sr)),) + A.shape[1:], np.float32)); t += ng
    n = len(z[2].split()); d = z[1] - z[0]; wpm = n / d * 60
    f = max(1.0, min(F * 1.15, DOEL / wpm)) if wpm <= 205 else 200 / wpm  # elke zin apart naar het doel (26 nov); alleen veel te snelle zinnen (>205) iets trager, naar 200
    # 27 nov (eigenaar: "dat de stem niet te snel gaat, af en toe hoor ik dat"): het regel-gemiddelde telt de pauzes mee, dus
    # binnen een zin kon het tempo veel hoger zijn. Nu per ZIN (zonder pauzes) begrenzen op MAX_ZIN, voor ELKE stem.
    mz = max(zin_wpm(i, z), default=0)
    if mz * f > MAX_ZIN + 10: f = MAX_ZIN / mz               # uitschieters (> 220 binnen een zin, normaal ± 200) naar 210
    if n <= 3 and d / f < MIN_KORT * n: f = d / (MIN_KORT * n)   # korte uitroep ("Oh no.") niet afraffelen
    seg = rek(A[int(z[0] * sr):int(z[1] * sr)], f); nd = len(seg) / sr
    s = nd / d  # tijdschaal binnen de regel
    nZ.append([round(t, 3), round(t + nd, 3)] + z[2:])
    for w in W:
        if w[0] == i: nW.append([w[0], w[1], round(t + (w[2] - z[0]) * s, 3), round(t + (w[3] - z[0]) * s, 3)])
    uit.append(seg); t += nd; vorig_eind = z[1]
staart = A[int(Z[-1][1] * sr):]; uit.append(staart)
sf.write(M / "stem.wav", np.concatenate(uit), sr)
(M / "zinnen.json").write_text(json.dumps(nZ, ensure_ascii=False), encoding="utf-8")
(M / "woorden.json").write_text(json.dumps(nW, ensure_ascii=False), encoding="utf-8")
shutil.rmtree(tmp); MERK.write_text(json.dumps({"grootte": (M / "stem.wav").stat().st_size, "doel": DOEL}))
NN = [z for z in nZ if z[4] == "N"]; print(f"klaar: verteller {sum(len(z[2].split()) for z in NN) / sum(z[1]-z[0] for z in NN) * 60:.0f} wpm, lengte {nZ[-1][1]:.0f} s")
