"""Vrolijk 'comedy pizzicato'-muziekje, zelf gemaakt (rechtenvrij): getokkelde snaren (Karplus-Strong), bas, zachte tik.
python muziek.py <seconden> -> muziek.wav (48 kHz mono, loopt naadloos door)."""
import sys, wave, numpy as np
SR = 48000; BPM = 112; B = 60 / BPM
dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60
rng = np.random.default_rng(3)
def pluk(f, d, helder=0.5):
    n = int(SR * d); p = max(2, int(SR / f)); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * (0.994 + 0.004 * helder)
    return out * np.exp(-np.arange(n) / SR * 3)
def hz(m): return 440 * 2 ** ((m - 69) / 12)
# akkoorden C - Am - F - G, 2 maten van 4 tellen per akkoord-ronde
akk = [(60, 64, 67), (57, 60, 64), (53, 57, 60), (55, 59, 62)]
melodie = [72, None, 74, 76, None, 74, 72, None, 69, None, 72, 74, None, 72, 71, None,
           77, None, 76, 74, None, 72, 74, None, 74, None, 76, 77, None, 76, 74, None]
maat = 4 * B; ronde = int(SR * maat * 4)
loop = np.zeros(ronde + SR)
cache = {}
def noot(m, d, v):
    k = (m, d)
    if k not in cache: cache[k] = pluk(hz(m), d)
    return cache[k] * v
def leg(x, t):
    i = int(t * SR); n = min(len(x), len(loop) - i); loop[i:i + n] += x[:n]
for a, (r, t3, q) in enumerate(akk):
    t0 = a * maat
    for tel in range(4):
        leg(noot(r - 24, 0.6, 0.55), t0 + tel * B)                       # bas op elke tel
        for k, m in enumerate((r, t3, q)):                               # akkoord op de 'en'
            leg(noot(m, 0.3, 0.18), t0 + tel * B + B / 2 + k * 0.012)
        tik = rng.normal(0, 1, int(0.03 * SR)) * np.exp(-np.arange(int(0.03 * SR)) / SR * 150) * 0.05
        leg(tik, t0 + tel * B + B / 2)
for i, m in enumerate(melodie):
    if m: leg(noot(m, 0.5, 0.3), i * B / 2)
loop = loop[:ronde]
n = int(dur * SR); uit = np.tile(loop, n // ronde + 1)[:n]
uit /= np.abs(uit).max() / 0.8
with wave.open("muziek.wav", "wb") as f:
    f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR); f.writeframes((uit * 32767).astype(np.int16).tobytes())
print("muziek.wav", dur, "s")
