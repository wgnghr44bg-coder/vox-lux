"""Achtergrondmuziek voor de asteroid-video, zelf gesynthetiseerd (geen opnames, geen auteursrecht).

Filmische score in D-mineur die de tijdlijn van de video volgt (tijden = seconden in de video):
  0–34     oude wereld: warme strijkerspads, losse pianotonen (verwondering)
  34–50.3  licht in de lucht: pulserende lage strijkers, stijgende spanning, crescendo -> stilte vóór de inslag
  54–94    nasleep: somber, lage pads, langzame cello-melodie
  94–158   alternatieve tijdlijn: lichter, piano-arpeggio's, glinsterende hoge pad
  158–eind twist: vol en hoopvol, eindigt in F-groot
Elke run geeft precies hetzelfde resultaat (vast zaadje).

Gebruik (vanuit deze map): python3 make_music.py   -> music.mp3 (wordt in make.py onder de stem gemixt)
"""
import os, subprocess, wave
import numpy as np

SR = 44100
END = 185.5
rng = np.random.default_rng(66)
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
C = {"Dm": [38, 50, 57, 62, 65], "Bb": [34, 50, 58, 62, 65], "F": [41, 53, 57, 60, 65], "C": [36, 52, 55, 60, 64],
     "Gm": [43, 50, 55, 58, 62], "A": [33, 49, 57, 61, 64], "Am": [45, 52, 57, 60, 64], "Fhi": [41, 57, 60, 65, 69]}

# 1. oude wereld (0–34): Dm Bb F C, losse pianotonen
for i, ch in enumerate(["Dm", "Bb", "F", "C"]):
    pad(i * 8.5, 11.5, C[ch], 0.16, a=3.5 if i else 5.0, r=3.0)
for t, m in [(4, 74), (7, 69), (12.5, 77), (16, 74), (21, 72), (24.5, 69), (29.5, 72), (32, 76)]:
    pluck(t, m, 0.07, pan=rng.uniform(-0.4, 0.4))

# 2. licht in de lucht (34–50.3): Dm-pedaal, stijgende pad, pulse met crescendo, dan stilte
pad(34, 16.3, [38, 50, 57, 62], 0.18, bright=8, a=2.5, r=0.25)
pad(40, 10.3, [63, 69, 74], 0.08, bright=5, a=6.0, r=0.25)            # schurende Eb-D-wrijving
pulse(36, 14.3, 38, 104, 0.05, 0.22)

# 3. nasleep (54–94): Dm Gm Bb A, somber, cello-melodie
for i, ch in enumerate(["Dm", "Gm", "Bb", "A", "Dm"]):
    pad(54 + i * 8, 11, C[ch], 0.13, bright=4, a=4.0, r=3.5)
for t, d, m in [(58, 4, 62), (62, 3, 60), (65, 5, 58), (71, 4, 57), (75, 3.5, 55), (78.5, 5, 57),
                (85, 4, 53), (89, 5, 50)]:
    cello(t, d, m, 0.07)

# 4. alternatieve tijdlijn (94–158): F C Dm Bb, piano-arpeggio's, glinsterende hoge pad
prog = ["F", "C", "Dm", "Bb"] * 2
for i, ch in enumerate(prog):
    t0 = 94 + i * 8
    pad(t0, 10.5, C[ch], 0.12, bright=5, a=3.0, r=3.0)
    top = sorted(C[ch][2:])
    for j, m in enumerate([top[0] + 12, top[1] + 12, top[2] + 12, top[1] + 12] * 2):
        pluck(t0 + j * 1.0 + 0.25, m, 0.045, pan=(-0.35 if j % 2 else 0.35), decay=1.3)
pad(98, 58, [81, 86], 0.025, bright=2, a=8.0, r=6.0)                   # hoge glans

# 5. twist (158–eind): Bb F C Dm -> Bb C F, vol en hoopvol
for i, ch in enumerate(["Bb", "F", "C", "Dm", "Bb", "C"]):
    pad(158 + i * 4.0, 6.5, C[ch], 0.17, bright=7, a=1.8, r=2.5)
pad(182, END - 182, C["Fhi"], 0.17, bright=6, a=1.5, r=END - 182 - 0.2)
for t, m in [(158.5, 70), (162.5, 72), (166.5, 76), (170.5, 74), (174.5, 77), (178.5, 76), (182.2, 77)]:
    pluck(t, m, 0.06)

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
