"""Effectgeluiden (zelf gemaakt, rechtenvrij) op de tijden uit data.json: klap + rinkelend goud bij "fell",
plopjes bij labels, zoef bij de obligatie. Schrijft sfx.wav (48 kHz mono)."""
import json, wave
import numpy as np
D = json.load(open("data.json", encoding="utf-8")); SR = 48000
uit = np.zeros(int((D["EIND"] + 1) * SR), np.float32); rng = np.random.default_rng(7)
def kw(w, n=1):
    k = 0
    for i, x, a, b in D["WO"]:
        if any(x.lower().strip(".,?!").startswith(v) for v in ([w] if isinstance(w, str) else w)):
            k += 1
            if k == n: return a
def zet(t, g, v=1.0):
    i = int(t * SR); uit[i:i + len(g)] += v * g[:len(uit) - i]
def tt(d): return np.arange(int(d * SR)) / SR
klap = np.sin(2 * np.pi * 55 * tt(0.6) * (1 - 0.4 * tt(0.6))) * np.exp(-tt(0.6) * 7) + rng.normal(0, 1, len(tt(0.6))) * np.exp(-tt(0.6) * 30) * 0.5
def tink(f): x = tt(0.5); return (np.sin(2 * np.pi * f * x) + 0.4 * np.sin(2 * np.pi * f * 2.76 * x)) * np.exp(-x * 9)
def plop(): x = tt(0.12); return np.sin(2 * np.pi * (500 + 900 * x / 0.12) * x) * np.exp(-x * 30)
def zoef(): x = tt(0.7); r = rng.normal(0, 1, len(x)); r = np.convolve(r, np.ones(30) / 30, "same"); return r * np.sin(np.pi * x / 0.7) ** 2 * 1.5
tv = kw("fell"); zet(tv, klap, 0.9)
for k in range(14): zet(tv + 0.05 + rng.uniform(0, 0.9), tink(rng.uniform(1800, 3200)), 0.18)
for w, n in [("safest", 1), (["five", "5"], 1), ("nothing", 1), (["five", "5"], 2), ("safe", 3)]:
    t = kw(w, n)
    if t: zet(t - 0.08, plop(), 0.35)
zet(kw("bond") - 0.2, zoef(), 0.5)
uit /= max(1, np.abs(uit).max() / 0.9)
with wave.open("sfx.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((uit * 32767).astype(np.int16).tobytes())
print("sfx.wav klaar")
