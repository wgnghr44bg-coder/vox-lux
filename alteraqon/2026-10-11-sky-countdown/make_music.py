"""Achtergrondmuziek voor de sky-countdown-video, zelf gesynthetiseerd (geen opnames, geen auteursrecht).

Filmische score in A-mineur die de tijdlijn van de video volgt (tijden = seconden in de video):
  0–15     de cijfers verschijnen: koude hoge pad, lage drone, losse pianotonen
  15–57    de wereld kijkt omhoog: pads + zachte pulse (verwondering, onrust)
  57–88    crisis (telescopen, beurzen, regeringen): lage strijkers-ostinato, schurende wrijving
  88–116   gewenning: kaal, langzame cello-melodie
  116–147.8 laatste dertig dagen: piano-arpeggio's, opbouw
  147.8–157.5 laatste tien seconden: alleen een stijgende drone, harde stilte op "Zero."
  158–eind  er gebeurt niets / de twist: licht, hoopvol, eindigt in C-groot
Elke run geeft precies hetzelfde resultaat (vast zaadje).

Gebruik (vanuit deze map): python3 make_music.py   -> music.mp3 (wordt in make.py onder de stem gemixt)
"""
import os, subprocess, wave
import numpy as np

SR = 44100
END = 187.4
rng = np.random.default_rng(365)
N = int(END * SR)
L = np.zeros(N); R = np.zeros(N)
hz = lambda m: 440.0 * 2 ** ((m - 69) / 12)

def env(n, a, r):
    """Langzaam aanzwellen (a s) en wegebben (r s)."""
    e = np.ones(n); ai, ri = int(a * SR), int(r * SR)
    if ai: e[:ai] = np.sin(np.linspace(0, np.pi / 2, ai)) ** 2
    if ri: e[-ri:] *= np.cos(np.linspace(0, np.pi / 2, ri)) ** 2
    return e

def add(t0, sig_l, sig_r=None):
    i = int(t0 * SR); n = min(len(sig_l), N - i)
    if n <= 0: return
    L[i:i + n] += sig_l[:n]; R[i:i + n] += (sig_l if sig_r is None else sig_r)[:n]

def pad(t0, dur, notes, vol, bright=6, a=3.0, r=3.0):
    """Strijkerspad: per noot een paar licht ontstemde, zachte zaagtanden (additief), links/rechts anders."""
    n = int(dur * SR); t = np.arange(n) / SR
    sl, sr = np.zeros(n), np.zeros(n)
    for m in notes:
        f = hz(m)
        for det, side in ((-0.10, 0), (0.0, 2), (0.11, 1)):
            ph = rng.uniform(0, 2 * np.pi)
            s = sum(np.sin(2 * np.pi * f * (1 + det / 100) * k * t + ph * k) / k ** 1.4 for k in range(1, bright + 1))
            s *= 1 + 0.08 * np.sin(2 * np.pi * 0.17 * t + ph)          # langzame ademing
            if side != 1: sl += s
            if side != 0: sr += s
    e = env(n, a, r) * vol / len(notes)
    add(t0, sl * e, sr * e)

def pluck(t0, m, vol, pan=0.0, decay=1.6):
    """Zachte pianoachtige toon: harmonischen die snel uitsterven, de hogere sneller."""
    n = int(4.5 * SR); t = np.arange(n) / SR; f = hz(m)
    s = sum(np.sin(2 * np.pi * f * k * t) * np.exp(-t * decay * k ** 0.8) / k ** 1.6 for k in range(1, 7))
    s *= np.minimum(1, t / 0.006) * vol
    add(t0, s * (1 - pan) , s * (1 + pan))

def cello(t0, dur, m, vol):
    """Langzame cello-achtige melodietoon met vibrato."""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    vib = 1 + 0.004 * np.sin(2 * np.pi * 5.2 * t) * np.minimum(1, t / 0.8)
    ph = 2 * np.pi * np.cumsum(f * vib) / SR
    s = sum(np.sin(k * ph) / k ** 1.2 for k in range(1, 9)) * env(n, 0.6, 0.9) * vol
    add(t0, s * 0.9, s * 1.1)

def pulse(t0, dur, m, bpm, vol0, vol1):
    """Lage strijkers-ostinato (achtsten) met crescendo."""
    step = 60 / bpm / 2; k = 0
    while k * step < dur:
        t = t0 + k * step; g = vol0 + (vol1 - vol0) * (k * step / dur)
        n = int(step * 0.95 * SR); tt = np.arange(n) / SR; f = hz(m)
        s = sum(np.sin(2 * np.pi * f * j * tt) / j ** 1.3 for j in range(1, 8))
        s *= np.minimum(1, tt / 0.02) * np.exp(-tt * 5) * g
        add(t, s, s); k += 1

# akkoorden (midi): grondtoon laag + drieklank in het midden
C = {"Am": [33, 45, 52, 57, 60], "F": [29, 45, 53, 57, 60], "C": [36, 48, 55, 60, 64], "G": [31, 47, 55, 59, 62],
     "Dm": [38, 50, 57, 62, 65], "E": [28, 44, 52, 56, 59], "Chi": [36, 52, 60, 64, 67]}

# 1. de cijfers verschijnen (0–15)
pad(0, 15.5, [33, 45], 0.14, bright=5, a=1.2, r=2.0)
pad(0.5, 15, [76, 81], 0.035, bright=2, a=4.0, r=2.0)
for t, m in [(1.5, 69), (4.5, 72), (8, 76), (11.5, 74)]:
    pluck(t, m, 0.06, pan=rng.uniform(-0.4, 0.4))

# 2. de wereld kijkt omhoog (15–57): Am F C G, zachte pulse
for i, ch in enumerate(["Am", "F", "C", "G", "Am"]):
    pad(14 + i * 8.5, 11.5, C[ch], 0.14, bright=5, a=3.0, r=3.0)
pulse(29, 24, 33, 96, 0.03, 0.10)
for t, m in [(17, 76), (21, 72), (25.5, 79), (31, 76), (35, 74), (40, 72), (45, 71), (49.5, 69)]:
    pluck(t, m, 0.05, pan=rng.uniform(-0.4, 0.4))

# 3. crisis (57–88): Dm-pedaal, ostinato met crescendo, schurende wrijving
pad(56.5, 16, C["Dm"], 0.15, bright=7, a=1.5, r=2.0)
pad(72, 16.5, C["E"], 0.15, bright=7, a=2.0, r=3.0)
pad(64, 22, [70, 69 + 12], 0.03, bright=4, a=5.0, r=3.0)
pulse(57, 30, 38, 110, 0.06, 0.18)

# 4. gewenning (88–116): kaal, cello-melodie
for i, ch in enumerate(["Am", "F", "Dm", "E"]):
    pad(88 + i * 7, 9.5, C[ch], 0.10, bright=4, a=3.5, r=3.0)
for t, d, m in [(90, 4, 64), (94, 3, 62), (97, 5, 60), (103, 4, 59), (107, 3.5, 57), (110.5, 5, 56)]:
    cello(t, d, m, 0.06)

# 5. laatste dertig dagen (116–147.8): Am F C G, piano-arpeggio's, opbouw
prog = ["Am", "F", "C", "G"]
for i in range(4):
    ch = prog[i]; t0 = 115.8 + i * 8
    pad(t0, 10.5 if i < 3 else 8.2, C[ch], 0.12 + 0.015 * i, bright=6, a=2.5, r=2.5 if i < 3 else 0.3)
    top = sorted(C[ch][2:])
    for j, m in enumerate([top[0] + 12, top[1] + 12, top[2] + 12, top[1] + 12] * 2):
        pluck(t0 + j * 1.0 + 0.25, m, 0.04 + 0.006 * i, pan=(-0.35 if j % 2 else 0.35), decay=1.3)
pad(124, 23.7, [81, 84], 0.025, bright=2, a=6.0, r=0.3)

# 6. laatste tien seconden (147.8–157.5): stijgende drone, harde stilte op "Zero."
pad(147.8, 9.7, [33, 45, 52], 0.10, bright=8, a=1.0, r=0.05)
pad(150, 7.5, [69, 70], 0.04, bright=5, a=6.0, r=0.05)

# 7. er gebeurt niets / twist (158–eind): F C G Am -> F G C, licht en hoopvol
for i, ch in enumerate(["F", "C", "G", "Am", "F", "G"]):
    pad(158.5 + i * 4.5, 7, C[ch], 0.13 + 0.006 * i, bright=6, a=2.0, r=2.5)
pad(184, END - 184, C["Chi"], 0.15, bright=6, a=1.2, r=END - 184 - 0.2)
for t, m in [(160, 72), (164.5, 76), (169, 74), (173.5, 76), (178, 79), (182.5, 77), (184.2, 76)]:
    pluck(t, m, 0.055)

# galm: convolutie met wegstervende ruis (2,8 s), per kanaal anders
def reverb(x, seed):
    n = int(2.8 * SR); ir = np.random.default_rng(seed).standard_normal(n) * np.exp(-np.arange(n) / SR * 2.6)
    ir[0] = 0; k = 1 << int(np.ceil(np.log2(len(x) + n)))
    return np.fft.irfft(np.fft.rfft(x, k) * np.fft.rfft(ir, k), k)[:len(x)]
wl, wr = reverb(L, 1), reverb(R, 2)
L = L + 0.035 * wl; R = R + 0.035 * wr
peak = max(np.abs(L).max(), np.abs(R).max())
L, R = L / peak * 0.8, R / peak * 0.8
st = (np.stack([L, R], 1) * 32767).astype("<i2")
with wave.open("music.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(st.tobytes())
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", "music.wav", "-b:a", "192k", "music.mp3"], check=True)
os.remove("music.wav")
print("music.mp3", END, "s")
