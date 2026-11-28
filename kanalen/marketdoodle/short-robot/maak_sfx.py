"""Geluid voor de 3D-robotshort (28 nov 2026): echte CC0-opnames uit ../geluiden plus zelfgemaakte robotgeluiden (numpy).
Alleen geluid bij wat je ziet (GELUIDCHECK): elke regel in sfx.json = [tijd, naam, wat-in-beeld-moet-zijn].
Geen muziek (What If-stijl Market Doodle).   python maak_sfx.py  -> sfx.wav + sfx.json"""
import json, subprocess
from pathlib import Path
import numpy as np, soundfile as sf

H = Path(__file__).parent; G = H.parent / "geluiden"; SR = 48000
TJ = json.load(open(H / "tijden.json", encoding="utf-8")); T = TJ["T"]; EIND = TJ["EIND"]
rng = np.random.default_rng(5)

def laad(n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(G / f"{n}.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
def fade(x, f=0.02):
    k = max(1, min(len(x) // 3, int(f * SR))); x = x.copy(); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
def knip(x, a, b): return fade(x[int(a * SR):int(b * SR)])
def toon(freqs, dur, vorm="sin", env=8.0):
    t = np.arange(int(dur * SR)) / SR; f = np.interp(t, np.linspace(0, dur, len(freqs)), freqs)
    ph = 2 * np.pi * np.cumsum(f) / SR; x = np.sin(ph) if vorm == "sin" else np.sign(np.sin(ph)) * 0.5
    return fade(x * np.exp(-t * env), 0.005)
def zoem(dur, f0, f1, ruis=0.15):                       # servo / rolwiel: zaagtand + ruis, iets gefilterd
    t = np.arange(int(dur * SR)) / SR; f = np.linspace(f0, f1, len(t)); ph = np.cumsum(f) / SR
    x = 2 * (ph % 1) - 1 + rng.normal(0, ruis, len(t)); x = np.convolve(x, np.ones(12) / 12, "same")
    return fade(x * 0.5, 0.05)

uit = np.zeros(int((EIND + 1) * SR), np.float32); LIJST = []
def zet(t, naam, x, g, zie):
    i = int(t * SR); j = min(len(uit), i + len(x))
    if j > i >= 0: uit[i:j] += x[:j - i] * g; LIJST.append([round(t, 3), naam, zie])

ting, klik, plof, papier, ritsel, stappen = laad("ting"), laad("klik"), laad("plof"), laad("papier"), laad("papier-ritsel"), laad("stappen")
piep = lambda: np.concatenate([toon([1400, 1400], 0.07, "sq", 20), np.zeros(int(0.04 * SR)), toon([1900, 1900], 0.09, "sq", 20)])
# kamer: de robot rolt binnen, glimt, buigt, draait zijn armen rond
zet(0.05, "rollen", zoem(2.1, 70, 110, 0.3), 0.35, "robot")
zet(T["shiny"] + 0.05, "ting", fade(ting[: int(1.2 * SR)]), 0.6, "robot")
zet(T["polite"] + 0.05, "servo", zoem(0.6, 300, 520), 0.35, "robot")
zet(T["little"] + 0.1, "servo", zoem(0.9, 600, 900), 0.3, "robot")
zet(T["little"] - 0.35, "piep", piep(), 0.25, "robot")
zet(T["dag1"] - 1.2, "piep", piep(), 0.2, "robot")             # vlak voor "Hello, family" (shot 5, robot in beeld)
# versieren: lampjes springen aan (boom, bank, vader)
for k in ("boom", "bank", "papa"):
    zet(T[k] + (0.25 if k == "boom" else 0.2 if k == "bank" else 0.15), "lampjes", fade(klik[: int(0.25 * SR)]), 0.7, {"boom": "boom", "bank": "bank", "papa": "dad"}[k])
    zet(T[k] + (0.3 if k == "boom" else 0.25 if k == "bank" else 0.2), "pling", toon([2200, 2600], 0.3, env=10), 0.25, {"boom": "boom", "bank": "bank", "papa": "dad"}[k])
# keuken: één koekje (ting van de oven), dan de lawine
zet(T["een"] + 0.1, "ovenbel", fade(ting[: int(0.9 * SR)]), 0.5, "koekje")
law = np.zeros(int(1.8 * SR), np.float32)
for i in range(70):
    q = int(rng.uniform(0, 1.6) * SR); s = fade(plof[: int(0.12 * SR)]) * rng.uniform(0.15, 0.4); law[q:q + len(s)] += s[: len(law) - q]
zet(T["tien"] + 0.1, "lawine", law, 0.9, "koekjes")
# tuin: scheppen + plof op het buurhuis
for q in np.arange(T["schep"] + 0.05, T["oops"] + 0.2, 0.31):
    zet(float(q), "schep", fade(stappen[int(0.2 * SR): int(0.45 * SR)]), 0.35, "robot")
for q in np.arange(T["onto"] + 0.3, T["oops"] + 0.3, 0.45):
    zet(float(q), "plof", fade(plof[: int(0.3 * SR)]), 0.45, "buurhuis")
# kerstavond: inpakken (papier), doos dicht (plof), strik (pling)
zet(T["eve"] + 0.6, "papier", fade(ritsel[: int(1.8 * SR)]), 0.55, "cadeaus")
zet(T["zelf"] + 0.85, "plof", fade(plof[: int(0.4 * SR)]), 0.7, "doos")
zet(T["zelf"] + 0.95, "pling", toon([1800, 2400], 0.35, env=8), 0.3, "doos")
zet(T["slot"] + 1.4, "piep", piep(), 0.18, "doos")               # gedempt piepje uit de doos (loop)
uit /= max(1, np.abs(uit).max() / 0.9)
sf.write(H / "sfx.wav", uit, SR)
(H / "sfx.json").write_text(json.dumps(LIJST, ensure_ascii=False, indent=0), encoding="utf-8")
print("geluiden:", len(LIJST))
