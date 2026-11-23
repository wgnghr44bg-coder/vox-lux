"""Echte geluidseffecten voor de Short 'Pause Time' (eigenaar 23 nov 2026: geluiden die je in de scène hoort; eerste
zelfgemaakte versie klonk nep -> nu echte opnames, CC0 van freesound.org, bronnen in ../geluiden/gekozen.json).
Alleen wat er in beeld gebeurt; in de bevroren wereld is het stil, behalve wat jij doet. Geen muziek.
Gebruik: python geluid.py  -> sfx.wav + short-pauze-sfx.mp4 (beeld short-pauze-v2.mp4 + stem + effecten)"""
import runpy, subprocess
from pathlib import Path
import numpy as np, soundfile as sf

HIER = Path(__file__).resolve().parent; G = HIER.parent / "geluiden"
g = runpy.run_path(str(HIER / "maak2.py"), run_name="geen_main")
kw, PAUZE, EIND, TSTART = g["kw"], g["PAUZE"], g["EIND"], g["TSTART"]
SR = 48000
N = int((EIND + 0.5) * SR); uit = np.zeros(N, np.float32)

def laad(naam):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(G / f"{naam}.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
S = {n: laad(n) for n in ("stappen", "klik", "stop", "papier", "borstel", "hap", "boek", "klok", "gang", "klas")}

def stuk(x, van, duur, fade=0.03):
    a = x[int(van * SR): int((van + duur) * SR)].copy(); f = int(fade * SR)
    if len(a) > 2 * f: a[:f] *= np.linspace(0, 1, f); a[-f:] *= np.linspace(1, 0, f)
    return a
def zet(t, x, gain):
    i = int(t * SR); j = min(N, i + len(x))
    if 0 <= i < N and j > i: uit[i:j] += x[: j - i] * gain
def lus(x, duur):
    n = int(duur * SR); return np.tile(x, n // len(x) + 1)[:n]
def toonlager(x, factor=0.7):                              # doffer: langzamer afspelen
    idx = np.arange(0, len(x) - 1, factor); return np.interp(idx, np.arange(len(x)), x).astype(np.float32)

# gang: sfeer + lopen
zet(0, stuk(lus(S["gang"], 60), 5, TSTART, 0.4), 0.10)
a, b = kw(0, "hallway", -1.0), kw(0, "hallway", 0.6); zet(a, stuk(S["stappen"], 1.0, b - a), 0.35)
# klas leeft, tot de knop: dan hard stil
zet(TSTART, stuk(lus(S["klas"], 30), 0.5, PAUZE - TSTART, 0.02), 0.16)
zet(kw(1, "press", 0.0), stuk(S["klik"], 0, 0.5), 0.6)
zet(PAUZE, stuk(S["stop"], 0, 3.0, 0.2), 0.45)
# rondlopen in de bevroren klas
for a, b in ((kw(6, "copy", -0.9), kw(6, "copy", 0.2)), (kw(6, "cookie", -1.0), kw(6, "cookie", 0.0))):
    zet(a, stuk(S["stappen"], 3.0, b - a), 0.35)
zet(kw(6, "copy", 0.2), stuk(S["papier"], 0, 1.2), 0.45)
zet(kw(6, "hair", -0.1), stuk(S["borstel"], 0.5, 1.4, 0.1), 0.35)
zet(kw(6, "cookie", 0.6), stuk(S["hap"], 0, 1.1), 0.5)
# thuis leren: bladzijde, klik per pauze
zet(kw(7, "study", -0.4), stuk(S["boek"], 0, 1.0), 0.45)
for w in ("10", "hour"): zet(kw(7, w, -0.4), stuk(S["klik"], 0, 0.5), 0.5)
# einde: klik, doffe klik die niets doet, klok tikt
zet(kw(13, "button", 0.0), stuk(S["klik"], 0, 0.5), 0.55)
zet(kw(13, "button", 0.8), toonlager(stuk(S["klik"], 0, 0.5), 0.55), 0.5)
t0 = kw(14, "clock", 0.0); zet(t0, stuk(lus(S["klok"], EIND - t0 + 1), 0, EIND - t0 + 0.4, 0.05), 0.35)

sf.write(HIER / "sfx.wav", np.clip(uit, -0.95, 0.95), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-pauze-v2.mp4"), "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"),
                "-filter_complex", "[1:a]aresample=48000,apad[s];[2:a]volume=1.0[e];[s][e]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(HIER / "short-pauze-sfx.mp4")], check=True)
print("KLAAR short-pauze-sfx.mp4")
