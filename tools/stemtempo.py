"""Stemtempo (eigenaar 25 nov 2026: 161 woorden/min "stuk langzamer", 200 "wat te snel" -> "dit is goed": 180 voor Short en lange video).
Zet de stem (stem.wav + zinnen.json + woorden.json) per regel op het doeltempo van de VERTELLER, zonder opnieuw in te spreken
(ffmpeg atempo). Regels van 8+ woorden niet boven 211 wpm (tempowachter); niets wordt trager; lange stiltes (>= 1,5 s, zoals
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
    f = F if n < 8 else max(1.0, min(F, 211 / wpm))
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
