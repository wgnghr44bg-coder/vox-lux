#!/usr/bin/env python3
"""Soft nature sounds per scene (rain, fire, waves, wind) under a sleep documentary.

Every sound is synthesised here (no recordings, no copyright). Each scene gets at most
one sound; scenes without one are silent, so only the voice and the 432 Hz music play.
Sounds fade in and out over 3 seconds. The output is a mono WAV that is already at the
right level under the voice (mix it at 0 dB, e.g. make_video.py --geluid).

Usage:
    python3 tools/ambient_sfx.py stories/<map>/geluiden.tsv out.wav --duur 7900
    python3 tools/ambient_sfx.py --uit-effecten stories/<map>/effecten-pauzes.tsv out.wav --duur 7900
    ... --muziek video/muziek432.wav --muziek-uit video/muziek432-wissel.wav

--muziek: maakt ook een kopie van de 432 Hz-muziek die stil is zolang er een natuurgeluid
klinkt (muziek en geluid vloeien in 3 s in elkaar over; eigenaar, okt 2026). Gebruik die
kopie als --muziek bij make_video.py.

geluiden.tsv: columns van, tot (seconds, same times as effecten.tsv) and geluid
(regen, vuur, golven or wind). --uit-effecten derives it from the visual effects
instead: regen -> regen, vuur -> vuur, sneeuw -> wind (no waves; add those by hand).
"""

from __future__ import annotations

import argparse
import csv
import wave
from pathlib import Path

import numpy as np

SR = 44100
LOOP = 240           # seconds per synthesised loop (long, so the crackle never sounds repeated)
FADE = 3.0           # seconds fade in/out per scene
GAIN_DB = {"regen": -28, "golven": -25, "vuur": -21, "wind": -27}   # vuur + regen samen (eigenaar, okt 2026)
FROM_EFFECT = {"regen": "regen", "vuur": "vuur", "sneeuw": "wind"}


def _band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


def _tilt(x, power):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    f[0] = 1
    return np.fft.irfft(X / f ** power, len(x))


def _norm(x, peak=0.9):
    return x / (np.max(np.abs(x)) or 1) * peak


def _smooth(x, n):
    return np.convolve(x, np.ones(n) / n, "same")


def _bursts(rng, n, count, lmin, lmax, amp, decay):
    out = np.zeros(n)
    for p in rng.integers(0, n - lmax, size=count):
        length = rng.integers(lmin, lmax)
        out[p:p + length] += amp(rng) * rng.standard_normal(length) * np.exp(-np.arange(length) / (length / decay))
    return out


def synth(kind: str, seconds: float, seed: int = 3) -> np.ndarray:
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    if kind == "regen":
        x = _norm(_band(_tilt(rng.standard_normal(n), 0.5), 400, 7000), 0.5)
        x += _band(_bursts(rng, n, int(seconds * 40), 200, 900, lambda r: r.uniform(0.05, 0.25), 5), 1500, 9000)
        x *= 1 + 0.15 * np.sin(2 * np.pi * t / 13)
    elif kind == "vuur":
        x = _norm(_band(_tilt(rng.standard_normal(n), 1.0), 40, 600), 0.35)
        crackle = _bursts(rng, n, int(seconds * 14), 60, 500, lambda r: r.uniform(0.2, 0.9) ** 2, 4)
        crackle += _bursts(rng, n, int(seconds * 2), 2400, 2500, lambda r: 0.9, 8)
        x += _band(crackle, 800, 8000) * 0.8
    elif kind == "golven":
        x = _norm(_band(_tilt(rng.standard_normal(n), 0.7), 60, 2500), 0.8)
        phase = (t % 9.0) / 9.0
        env = _smooth(np.where(phase < 0.45, (phase / 0.45) ** 2, np.exp(-(phase - 0.45) * 4.5)), SR // 3)
        x = x * (0.15 + 0.85 * env) + _band(rng.standard_normal(n), 2500, 7000) * 0.05 * env ** 3
    elif kind == "wind":
        src = rng.standard_normal(n)
        x = np.zeros(n)
        seg = SR // 4
        for i in range(0, n, seg):
            c = 500 + 350 * np.sin(2 * np.pi * i / SR / 11) + 150 * np.sin(2 * np.pi * i / SR / 4.3)
            lo = max(0, i - seg)
            block = _band(src[lo:min(n, i + 2 * seg)], c * 0.6, c * 1.6)
            x[i:i + seg] = block[i - lo:i - lo + seg][:len(x[i:i + seg])]
        x = _smooth(x, 40) * (0.35 + 0.65 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.5 + np.sin(2 * np.pi * t / 17))))
    else:
        raise SystemExit(f"onbekend geluid: {kind}")
    return _norm(x, 0.9)


def seamless_loop(kind: str) -> np.ndarray:
    """A LOOP-second loop whose end crossfades into its start."""
    x = synth(kind, LOOP + FADE)
    k = int(FADE * SR)
    ramp = np.linspace(0, 1, k)
    head = x[:k] * np.sqrt(ramp) + x[-k:] * np.sqrt(1 - ramp)
    return np.concatenate([head, x[k:-k]])


def read_scenes(path: Path, from_effects: bool) -> list[tuple[float, float, str]]:
    rows = list(csv.DictReader(path.open(encoding="utf-8"), delimiter="\t"))
    scenes = []
    for r in rows:
        kind = FROM_EFFECT.get((r.get("effect") or "").strip()) if from_effects else (r.get("geluid") or "").strip()
        if kind:
            scenes.append((float(r["van"]), float(r["tot"]), kind))
    return sorted(scenes)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("scenes", type=Path, help="geluiden.tsv (or effecten.tsv with --uit-effecten)")
    ap.add_argument("out", type=Path)
    ap.add_argument("--duur", type=float, required=True, help="length of the video in seconds")
    ap.add_argument("--uit-effecten", action="store_true", help="derive sounds from effecten.tsv")
    ap.add_argument("--muziek", type=Path, help="432 Hz-muziek (wav) om te laten wisselen met de geluiden")
    ap.add_argument("--muziek-uit", type=Path, help="waar de wisselende muziek komt")
    a = ap.parse_args()
    if bool(a.muziek) != bool(a.muziek_uit):
        ap.error("--muziek en --muziek-uit horen bij elkaar")

    scenes = read_scenes(a.scenes, a.uit_effecten)
    loops = {k: seamless_loop(k) * 10 ** (GAIN_DB[k] / 20) for k in {s[2] for s in scenes}}
    total = int(a.duur * SR)
    block = 10 * SR
    with wave.open(str(a.out), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        for start in range(0, total, block):
            n = min(block, total - start)
            idx = np.arange(start, start + n)
            tt = idx / SR
            mix = np.zeros(n)
            for van, tot, kind in scenes:
                if tot + FADE < tt[0] or van - FADE > tt[-1]:
                    continue
                env = np.clip((tt - (van - FADE / 2)) / FADE, 0, 1) * np.clip(((tot + FADE / 2) - tt) / FADE, 0, 1)
                loop = loops[kind]
                mix += loop[idx % len(loop)] * np.sqrt(env)
            w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
    print(f"geluiden: {len(scenes)} scènes ({', '.join(sorted(loops))}) -> {a.out}")
    if a.muziek:
        duck_music(a.muziek, a.muziek_uit, scenes)
        print(f"muziek stil tijdens de geluiden -> {a.muziek_uit}")


def scene_level(tt: np.ndarray, scenes) -> np.ndarray:
    """0..1: hoe hard de natuurgeluiden op tijd tt klinken (zelfde fades als hierboven)."""
    level = np.zeros(len(tt))
    for van, tot, _ in scenes:
        level = np.maximum(level, np.clip((tt - (van - FADE / 2)) / FADE, 0, 1)
                           * np.clip(((tot + FADE / 2) - tt) / FADE, 0, 1))
    return level


def duck_music(src: Path, dst: Path, scenes) -> None:
    """Kopie van de muziek die wegfadet zolang er een natuurgeluid klinkt."""
    with wave.open(str(src), "rb") as r, wave.open(str(dst), "wb") as w:
        ch, sr = r.getnchannels(), r.getframerate()
        w.setnchannels(ch)
        w.setsampwidth(2)
        w.setframerate(sr)
        pos, block = 0, 10 * sr
        while True:
            raw = r.readframes(block)
            if not raw:
                break
            x = np.frombuffer(raw, "<i2").reshape(-1, ch).astype(np.float32)
            gain = 1 - scene_level((pos + np.arange(len(x))) / sr, scenes)
            w.writeframes((x * gain[:, None]).astype("<i2").tobytes())
            pos += len(x)


if __name__ == "__main__":
    main()
