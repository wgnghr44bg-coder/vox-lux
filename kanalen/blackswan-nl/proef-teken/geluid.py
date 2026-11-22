"""Tekengeluid (22 nov): zacht stift-kras-geluid zolang er getekend/geschreven wordt, en een zachte 'plop' bij logo, grafiek, foto.
  python geluid.py scene.json uit.wav   -> mono 48 kHz, ver onder de stem te mengen"""
import json, sys
import numpy as np, wave
SR = 48000; rng = np.random.default_rng(7)
KRAS = "--met-kras" in sys.argv                                     # eigenaar 22 nov: stiftgeluid weg (standaard uit)
sc = json.load(open(sys.argv[1], encoding="utf-8")); n = int((sc["duur"] + 1) * SR); uit = np.zeros(n, np.float32)
def kras(t0, dur):
    m = int(dur * SR); x = rng.standard_normal(m).astype(np.float32)
    X = np.fft.rfft(x); f = np.fft.rfftfreq(m, 1 / SR); X[(f < 1800) | (f > 7000)] = 0; x = np.fft.irfft(X, m)   # alleen 'kras'-tonen
    tt = np.arange(m) / SR; mod = 0.55 + 0.45 * np.sign(np.sin(2 * np.pi * (6 + 4 * rng.random()) * tt + rng.random() * 6))   # streepjes
    env = np.minimum(1, np.minimum(tt / 0.05, (dur - tt) / 0.08)).clip(0)
    x = x / (np.abs(x).max() + 1e-9) * mod * env * 0.10
    i = int(t0 * SR); uit[i:i + m] += x[:max(0, min(m, n - i))]
def plop(t0):
    m = int(0.09 * SR); tt = np.arange(m) / SR
    x = np.sin(2 * np.pi * (520 - 2200 * tt) * tt) * np.exp(-tt * 45) * 0.22
    i = int(t0 * SR); uit[i:i + m] += x[:max(0, min(m, n - i))].astype(np.float32)
for it in sc["items"]:
    if "beeld" in it or "foto" in it:
        if KRAS and it.get("teken", 1) > 0.3: kras(it["start"], it["teken"])
    elif "tekst" in it or "streep" in it:
        if KRAS: kras(it["start"], max(0.3, it.get("teken", 0.8)))
    elif any(k in it for k in ("logo", "data", "dagen", "balken", "bordje")): plop(it["start"])
w = wave.open(sys.argv[2], "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(uit, -1, 1) * 32767).astype("<i2").tobytes()); w.close(); print("geluid", sys.argv[2])
