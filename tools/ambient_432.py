"""Rustige achtergrondmuziek in 432 Hz-stemming (A4 = 432 Hz), zelf gesynthetiseerd.

Zachte akkoordenpads die langzaam wisselen, een lage grondtoon en losse
zwevende tonen die heel langzaam aanzwellen en weer wegebben. Geen aanslagen
of scherpe geluiden: bedoeld om slaperig bij weg te dromen. Elke run met hetzelfde
zaadje (--seed) geeft precies hetzelfde resultaat.

Gebruik: python3 tools/ambient_432.py uit.wav --duur 120 [--seed 7]
"""
import argparse, subprocess, wave

import imageio_ffmpeg
import numpy as np

SR = 32000
A4 = 432.0
CHORD_LEN = 24.0   # seconden per akkoord
FADE = 9.0         # overlap tussen akkoorden

# midi-noten (A-mineur / C-majeur), wisselende volgorde voor variatie
CHORDS = {
    "Am": [57, 60, 64, 69], "F": [53, 57, 60, 65], "C": [55, 60, 64, 67],
    "G": [55, 59, 62, 67], "Em": [52, 55, 59, 64], "Dm": [50, 57, 62, 65],
    "Fmaj7": [53, 57, 60, 64], "Am9": [57, 60, 64, 71],
}
PROGRESSIONS = [["Am", "F", "C", "G"], ["Am", "Em", "F", "C"], ["Dm", "Am", "Fmaj7", "G"],
                ["Am9", "F", "C", "Em"], ["F", "G", "Am", "Am"]]
PENTA = [57, 60, 62, 64, 67, 69, 72, 74, 76, 79, 81]  # A-mineur pentatonisch


def hz(m):
    return A4 * 2 ** ((m - 69) / 12)


def pad_note(f, n, t, rng):
    """Warme pad: drie licht ontstemde sinussen plus een zachte boventoon, langzaam ademend."""
    out = np.zeros(n)
    for det in (-0.25, 0.0, 0.25):
        ph = rng.uniform(0, 2 * np.pi)
        out += np.sin(2 * np.pi * (f + det) * t + ph)
    out += 0.25 * np.sin(2 * np.pi * 2 * f * t)
    out *= 0.8 + 0.2 * np.sin(2 * np.pi * t / rng.uniform(6, 11) + rng.uniform(0, 6))
    return out / 3.25


def swell(f, dur):
    """Zwevende toon die langzaam aanzwelt en wegebt (geen aanslag)."""
    t = np.arange(int(dur * SR)) / SR
    env = np.sin(np.pi * t / dur) ** 2
    tone = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * (f + 0.15) * t) \
        + 0.12 * np.sin(2 * np.pi * 2 * f * t)
    return tone * env / 1.6


def flute(f, dur):
    """Zachte fluitachtige toon: trage inzet (0,6 s), lichte vibrato, zacht uitlopend."""
    t = np.arange(int(dur * SR)) / SR
    env = np.minimum(1, t / 0.6) * np.minimum(1, (dur - t) / 1.2).clip(0)
    vib = 1 + 0.003 * np.sin(2 * np.pi * 4.5 * t) * np.minimum(1, t / 1.5)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    return (np.sin(ph) + 0.25 * np.sin(2 * ph) + 0.08 * np.sin(3 * ph)) * env / 1.33


def render(duration, seed):
    rng = np.random.default_rng(seed)
    n = int(duration * SR)
    left, right = np.zeros(n), np.zeros(n)
    t_all = np.arange(n) / SR

    # 1. akkoorden
    chords, prog = [], []
    while len(chords) * CHORD_LEN < duration + CHORD_LEN:
        if not prog:
            prog = list(PROGRESSIONS[rng.integers(len(PROGRESSIONS))])
        chords.append(prog.pop(0))
    seg = int((CHORD_LEN + FADE) * SR)
    ramp = int(FADE * SR)
    env = np.ones(seg)
    env[:ramp] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, ramp))
    env[-ramp:] = env[:ramp][::-1]
    for i, name in enumerate(chords):
        start = int(i * CHORD_LEN * SR)
        if start >= n:
            break
        end = min(start + seg, n)
        t = t_all[start:end]
        sig = sum(pad_note(hz(m), end - start, t, rng) for m in CHORDS[name]) / 4
        sig += 0.35 * np.sin(2 * np.pi * hz(CHORDS[name][0] - 12) * t)  # grondtoon
        sig *= env[: end - start]
        left[start:end] += sig
        right[start:end] += sig

    # 2. zwevende tonen: af en toe één of twee, die traag op- en wegkomen
    pos = rng.uniform(6, 12)
    while pos < duration - 1:
        chord = CHORDS[chords[int(pos // CHORD_LEN)]]
        pitch_class = {m % 12 for m in chord}
        choices = [m for m in PENTA if m % 12 in pitch_class] or PENTA
        for k in range(rng.integers(1, 3)):
            p = choices[rng.integers(len(choices))]
            b = swell(hz(p), rng.uniform(7, 12)) * rng.uniform(0.18, 0.28)
            s = int((pos + k * rng.uniform(2.5, 4.5)) * SR)
            e = min(s + len(b), n)
            if s >= n:
                break
            pan = rng.uniform(0.25, 0.75)
            left[s:e] += b[: e - s] * (1 - pan) * 2
            right[s:e] += b[: e - s] * pan * 2
        pos += rng.uniform(7, 14)

    # 3. zachte melodie: korte frasen van glijdende noten (fluitachtig, zachte inzet)
    pos = rng.uniform(4, 8)
    idx = 5
    while pos < duration - 4:
        for _ in range(rng.integers(4, 8)):
            idx = int(np.clip(idx + rng.choice([-2, -1, -1, 1, 1, 2]), 3, len(PENTA) - 1))
            dur = rng.uniform(1.8, 3.5)
            b = flute(hz(PENTA[idx]), dur + 1.2) * 0.2
            s = int(pos * SR)
            e = min(s + len(b), n)
            if s >= n:
                break
            left[s:e] += b[: e - s] * 1.1
            right[s:e] += b[: e - s] * 0.9
            pos += dur
        pos += rng.uniform(4, 10)

    stereo = np.stack([left, right], axis=1)
    return stereo / np.abs(stereo).max() * 0.7


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--duur", type=float, default=120)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    raw = a.out + ".raw.wav"
    data = (render(a.duur, a.seed) * 32767).astype("<i2")
    with wave.open(raw, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(data.tobytes())
    # galm en een zachte fade-in/uit
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error", "-y",
                    "-i", raw, "-af",
                    f"aecho=0.8:0.6:90|170|290|430:0.3|0.22|0.15|0.1,lowpass=f=2200,"
                    f"afade=t=in:d=6,afade=t=out:st={max(a.duur - 8, 0)}:d=8",
                    "-ar", "44100", a.out], check=True)
    import os; os.remove(raw)


if __name__ == "__main__":
    main()
