"""Geluidseffecten voor de Short 'Pause Time' v2 (eigenaar 23 nov 2026: "je mag ook geluidseffecten gebruiken wat je kan
horen in de scène"). Alles zelf gemaakt met numpy (geen rechten van anderen), geen muziek.
Gebruik: python geluid.py  -> sfx.wav (zelfde lengte als stem.wav) en short-pauze-v3.mp4 (beeld v2 + stem + effecten)."""
import runpy, subprocess
from pathlib import Path
import numpy as np, soundfile as sf

HIER = Path(__file__).resolve().parent
g = runpy.run_path(str(HIER / "maak2.py"), run_name="geen_main")
kw, PAUZE, EIND = g["kw"], g["PAUZE"], g["EIND"]
stem, SR = sf.read(HIER / "stem.wav", dtype="float32")
if stem.ndim > 1: stem = stem.mean(axis=1)
N = int((EIND + 0.5) * SR); uit = np.zeros(N, np.float32)
rng = np.random.default_rng(7)

def env(n, a=0.002, r=0.05):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / r); return e.astype(np.float32)
def zet(t, x, gain):
    i = int(t * SR); j = min(N, i + len(x))
    if 0 <= i < N: uit[i:j] += x[: j - i] * gain
def ruis(n): return rng.standard_normal(n).astype(np.float32)
def lowpass(x, k):                                    # simpel gemiddelde = zacht/dof
    return np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)
def highpass(x, k): return (x - lowpass(x, k)).astype(np.float32)

def stap():                                            # voetstap: korte doffe tik
    n = int(0.09 * SR); t = np.arange(n) / SR
    return (lowpass(ruis(n), 30) * 3 + 0.6 * np.sin(2 * np.pi * 90 * t)) * env(n, 0.002, 0.025)
def klik():                                            # knop: heldere klik
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 2200 * t) * 0.6 + highpass(ruis(n), 8) * 0.8) * env(n, 0.0005, 0.008)
def klonk():                                           # kapotte knop: dof 'klonk'
    n = int(0.25 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 140 * t) + 0.5 * np.sin(2 * np.pi * 95 * t) + lowpass(ruis(n), 40)) * env(n, 0.002, 0.07)
def bevries():                                         # alles stopt: dalende 'tape stop' + zachte dreun
    n = int(0.9 * SR); t = np.arange(n) / SR
    f = 600 * np.exp(-t * 3.2) + 40; fase = 2 * np.pi * np.cumsum(f) / SR
    toon = np.sin(fase) * np.exp(-t * 2.2) * 0.7
    dreun = np.sin(2 * np.pi * 55 * t) * np.exp(-t * 4) * 0.9
    return (toon + dreun).astype(np.float32)
def ritsel(d=0.35):                                    # papier
    n = int(d * SR); x = highpass(ruis(n), 6) * (0.5 + 0.5 * np.abs(np.sin(np.arange(n) / SR * 60)))
    return x * env(n, 0.02, d / 2.5)
def borstel():                                         # kam door het haar
    n = int(0.5 * SR); x = highpass(ruis(n), 3) * (0.4 + 0.6 * np.abs(np.sin(np.arange(n) / SR * 18)))
    return x * env(n, 0.03, 0.25) * 0.6
def hap():                                             # knapperig koekje
    n = int(0.28 * SR); x = np.zeros(n, np.float32)
    for k in range(9):
        i = int(rng.uniform(0, 0.22) * SR); m = int(0.018 * SR); x[i:i + m] += highpass(ruis(m), 4) * env(m, 0.0005, 0.004)
    return x * 1.6
def tik():                                             # klok
    n = int(0.03 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 3100 * t) * 0.5 + highpass(ruis(n), 5) * 0.5) * env(n, 0.0003, 0.006)
def opzak():                                           # knop uit de zak
    n = int(0.3 * SR); return lowpass(ruis(n), 4) * env(n, 0.04, 0.1) * 0.8

def stappen(a, b, tempo=0.42, gain=0.35):
    t = a
    while t < b: zet(t, stap(), gain); t += tempo

# 1 gang: lopen
stappen(kw(0, "hallway", -1.0), kw(0, "hallway", 0.6))
# 2 klas: knop uit de zak, klik, bevriezen
zet(kw(1, "button", -0.3), opzak(), 0.45)
zet(kw(1, "press", 0.0), klik(), 0.55)
zet(PAUZE, bevries(), 0.5)
# 3 regels/verhaal in de klas: lopen naar de juf, papier, kam, lopen naar vriend, koekje
stappen(kw(6, "copy", -0.9), kw(6, "copy", 0.2))
zet(kw(6, "copy", 0.2), ritsel(), 0.35)
zet(kw(6, "hair", -0.1), borstel(), 0.35)
stappen(kw(6, "cookie", -1.0), kw(6, "cookie", 0.0))
zet(kw(6, "cookie", 0.75), hap(), 0.5)
# 4 keuken: toets pakken, klikjes per pauze
zet(kw(7, "test", -0.3), ritsel(0.3), 0.3)
for w in ("10", "hour"): zet(kw(7, w, -0.4), klik(), 0.5)
# 8 einde: knop weer, doet niets, klok tikt
zet(kw(13, "button", 0.0), klik(), 0.5)
zet(kw(13, "button", 0.8), klonk(), 0.5)
t = kw(14, "clock", 0.0)
while t < EIND: zet(t, tik(), 0.4); t += 0.5

uit = np.clip(uit, -0.9, 0.9)
sf.write(HIER / "sfx.wav", uit, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-pauze-v2.mp4"), "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"),
                "-filter_complex", "[1:a]apad[s];[2:a]volume=0.6[e];[s][e]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "short-pauze-v3.mp4")], check=True)
print("KLAAR short-pauze-v3.mp4 (beeld v2 + stem + geluidseffecten)")
