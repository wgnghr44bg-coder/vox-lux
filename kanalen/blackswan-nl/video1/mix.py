"""Muziek (zelf gesynthetiseerd, rechtenvrij) + stem -> mix.wav (-14 LUFS).
Per hoofdstuk een ander akkoordenschema en tempo; klap + 'whoosh' bij hoofdstukkaarten en grote onthullingen;
muziek zakt weg onder citaten (Huangs brief, Kress)."""
import json, subprocess
from pathlib import Path
import numpy as np, soundfile as sf
H = Path(__file__).parent; SR = 44100
stem, ssr = sf.read(H / "stem.wav", dtype="float32")
Z = json.load(open(H / "zinnen.json", encoding="utf-8"))
dur = Z[-1][1] + 3.5; n = int(dur * SR); t = np.arange(n) / SR
rng = np.random.default_rng(7)
scenes = []
for s, e, z, sc in Z:
    if not scenes or scenes[-1][0] != sc: scenes.append([sc, s])
start = {sc: s for sc, s in scenes}
hoofd = [start[h] for h in ["h1-week", "h2-asml", "h3-keten", "h4-bubbel", "h5-jij"] if h in start]   # Geldverhaal video 1: per hoofdstuk ander akkoord
grenzen = [0.0] + hoofd + [dur]
# akkoorden (grondtonen in Hz) en bpm per deel: open, h1..h7
DELEN = [((55.0, 65.4, 82.4), 0, 0.10), ((49.0, 61.7, 73.4), 84, 0.07), ((55.0, 69.3, 82.4), 92, 0.08), ((61.7, 73.4, 92.5), 100, 0.10),
         ((46.2, 55.0, 69.3), 88, 0.09), ((43.7, 55.0, 65.4), 96, 0.11), ((49.0, 58.3, 73.4), 104, 0.10), ((41.2, 49.0, 61.7), 80, 0.08)]
m = np.zeros(n, np.float32)
def env(a, b, f=2.0):
    return np.clip(np.minimum((t - a) / f, (b - t) / f), 0, 1)
DELEN = DELEN[:len(grenzen) - 1]
for k, ((g1, g2, g3), bpm, amp) in enumerate(DELEN):
    a, b = grenzen[k], grenzen[k + 1]; e = env(a, b)
    if e.max() == 0: continue
    for i, f in enumerate((g1, g2, g3, g1 * 2)):
        lfo = 0.6 + 0.4 * np.sin(2 * np.pi * (0.05 + 0.02 * i) * t + i)
        m += (e * lfo * amp * (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 2.004 * t))).astype(np.float32)
    if bpm:                                           # zachte puls (lage kick) + hi-hat-tik
        for x in np.arange(a + 0.5, b - 0.5, 60 / bpm):
            i0 = int(x * SR); L = int(0.32 * SR); tt = np.arange(L) / SR
            kick = np.sin(2 * np.pi * (55 * np.exp(-tt * 10) + 38) * tt) * np.exp(-tt * 9) * 0.45
            m[i0:i0 + L] += kick[:max(0, n - i0)]
            j0 = int((x + 30 / bpm) * SR); Lh = int(0.05 * SR)
            hat = rng.standard_normal(Lh) * np.exp(-np.arange(Lh) / SR * 80) * 0.035
            m[j0:j0 + Lh] += hat[:max(0, n - j0)]
def klap(at, amp=1.0):
    i0 = int(at * SR); L = int(3 * SR); tt = np.arange(L) / SR
    s = (np.sin(2 * np.pi * (48 * np.exp(-tt * 1.8) + 26) * tt) * np.exp(-tt * 1.6) + rng.standard_normal(L) * 0.12 * np.exp(-tt * 10)) * amp
    m[i0:i0 + L] += s[:max(0, n - i0)].astype(np.float32)
def whoosh(at, d=1.2, amp=0.25):                      # opbouwende ruis vlak voor een klap
    i1 = int(at * SR); L = int(d * SR); i0 = max(0, i1 - L)
    r = rng.standard_normal(i1 - i0) * np.linspace(0, 1, i1 - i0) ** 2 * amp
    from numpy.fft import rfft, irfft
    m[i0:i1] += r.astype(np.float32)
# 19 nov: geen klappen/whooshes meer (eigenaar: 'het geluid elke keer bij voor die fragment hoeft ook niet')
# stil onder citaten en de vraag
duck = np.ones(n, np.float32)
for sc in []:
    i = [k for k, (x, _) in enumerate(scenes) if x == sc][0]
    a, b = scenes[i][1], scenes[i + 1][1]
    duck *= (1 - 0.8 * env(a - 0.3, b + 0.3, 0.6)).astype(np.float32)
m *= duck
m[-int(3 * SR):] *= np.linspace(1, 0, int(3 * SR))
m = m / np.abs(m).max() * 0.8
sf.write(H / "muziek.wav", m, SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(H / "stem.wav"), "-i", str(H / "muziek.wav"), "-filter_complex",
                "[0:a]aresample=44100,highpass=f=70,equalizer=f=3000:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=80,loudnorm=I=-16[s];"
                "[1:a]loudnorm=I=-31[mu];[s][mu]amix=inputs=2:normalize=0:duration=longest,loudnorm=I=-14:TP=-1:LRA=11[o]",
                "-map", "[o]", "-ar", "44100", "-ac", "2", str(H / "mix.wav")], check=True)
print("mix.wav klaar", round(dur / 60, 1), "min")
