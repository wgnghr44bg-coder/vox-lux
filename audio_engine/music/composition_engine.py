"""Builds the whole piece (chords, note events, intensity curves per layer) and renders it block by block.

Structure (times scale down for short pieces, so a 60 s Short still has every stage):
  opening      0-20 s   drone and faint shimmer only, curiosity
  development 20-60 s   strings come in, then the choir, then the first piano notes
  middle     60-120 s   deeper harmonies (heavier progressions, low cello root), restrained swells
  later       120 s +   slow, non-repeating balance changes between the layers, narration stays on top
  ending      last ±25 s  everything thins out towards a soft resolution (plus the FFmpeg fade-out)

Rendering happens in blocks of 20 s on the GPU, so a 3-hour piece needs little memory. Every random
choice is made up front from the seed, so the same config always gives the same audio.
"""
import math
from dataclasses import asdict, dataclass

import numpy as np
import soundfile as sf
import torch

from . import atmosphere_generator, choir_generator, drone_generator, piano_generator, string_generator
from .chord_engine import progression_stream
from .note_calculator import A4_HZ, name_to_pc
from .oscillator import device

LAYERS = {"drone": drone_generator, "strings": string_generator, "choir": choir_generator,
          "piano": piano_generator, "atmosphere": atmosphere_generator}
BALANCE = {"drone": 0.22, "strings": 1.0, "choir": 0.75, "piano": 0.45, "atmosphere": 0.7}


@dataclass
class MusicConfig:
    duration: float = 120.0      # seconds
    seed: int = 7
    key: str = "A"               # tonic of the minor key
    chord_len: float = 7.0       # seconds per chord
    fade: float = 2.5            # crossfade between chords
    drone: float = 1.0           # layer intensities (0 = off, 1 = default, up to 2)
    strings: float = 1.0
    choir: float = 1.0
    piano: float = 1.0
    atmosphere: float = 1.0
    piano_gap: float = 9.0       # average seconds between piano notes
    sample_rate: int = 48000
    tuning_a4: float = A4_HZ     # fixed: 432 Hz (shown in the config for clarity)
    # effects (FFmpeg)
    reverb_mix: float = 0.3      # 0 = dry, 1 = as loud as the dry signal
    reverb_size: float = 3.5     # RT60 in seconds
    highpass_hz: float = 35.0
    lowpass_hz: float = 4500.0
    width: float = 1.3           # 1 = as rendered, 2 = very wide
    compression: bool = True
    fade_in: float = 4.0
    fade_out: float = 8.0
    target_lufs: float = -24.0   # loudness of the music-only export
    preset: str = "cinematic"
    build_up: bool = True        # False: every layer at its level from the first seconds (no 0-60 s build-up)


# "referentie": measured from the owner's example (6 nov 2026): one soft sustained pad between ±250 and
# 800 Hz, no bass, nothing above ±1 kHz, hardly any movement. "cinematic": all layers, as in the brief.
PRESETS = {
    "referentie": dict(drone=0.0, strings=1.0, choir=0.5, piano=0.0, atmosphere=0.25, fade=3.5, reverb_mix=0.35,
                       reverb_size=3.0, highpass_hz=180.0, lowpass_hz=1000.0, width=1.2, build_up=False, fade_in=3.0),
    "cinematic": dict(drone=1.0, strings=1.0, choir=1.0, piano=1.0, atmosphere=1.0, fade=2.5, reverb_mix=0.3,
                      reverb_size=3.5, highpass_hz=35.0, lowpass_hz=4500.0, width=1.3),
}


def preset(name, **overrides):
    return MusicConfig(**{**PRESETS[name], "preset": name, **overrides})


def sections(duration):
    s = min(1.0, duration / 150.0)
    return {"intro": 20 * s, "dev": 60 * s, "mid": 120 * s, "ending": min(25.0, 0.12 * duration)}


def curve(keys, t):
    xs, ys = zip(*keys)
    return np.interp(t, xs, ys)


def intensity(layer, t, cfg, sec):
    """Level of a layer at absolute times t (numpy, seconds)."""
    i, d, m, e, D = sec["intro"], sec["dev"], sec["mid"], sec["ending"], cfg.duration
    keys = {
        "drone": [(0, 0.75), (d, 1.0), (D, 1.0)],
        "strings": [(0, 0.0), (i, 0.0), (i + (d - i) * 0.6, 0.7), (m, 1.0), (D, 1.0)],
        "choir": [(0, 0.0), (i + (d - i) * 0.35, 0.0), (d, 0.5), (m, 0.85), (D, 0.85)],
        "piano": [(0, 0.0), (i + (d - i) * 0.5, 0.0), (d, 0.7), (m, 0.85), (D, 0.85)],
        "atmosphere": [(0, 1.0), (d, 0.7), (D, 0.7)],
    }[layer]
    if not cfg.build_up:                                    # steady bed: the final level from the start
        keys = [(0, keys[-1][1]), (D, keys[-1][1])]
    lv = curve(keys, t)
    if layer in ("strings", "choir"):                       # restrained swells from the middle section on
        lv = lv * np.where(t > d, 1 + 0.15 * np.sin(2 * math.pi * t / (53 if layer == "strings" else 71) + 1.1), 1.0)
    if layer in ("choir", "piano", "atmosphere"):           # later: slow balance changes, never a loop
        per = {"choir": 137.0, "piano": 101.0, "atmosphere": 89.0}[layer]
        lv = lv * np.where(t > m, 1 + 0.25 * np.sin(2 * math.pi * (t - m) / per), 1.0)
    end = np.clip((D - t) / e, 0, 1)                         # ending: thin out towards silence
    lv = lv * (0.15 + 0.85 * (0.5 - 0.5 * np.cos(math.pi * end)))
    return lv


def build(cfg):
    rng = np.random.default_rng(cfg.seed)
    sec = sections(cfg.duration)
    tonic = name_to_pc(cfg.key)
    n = int(math.ceil(cfg.duration / cfg.chord_len)) + 1
    chords = progression_stream(tonic, n, rng, deep_from=sec["dev"], chord_len=cfg.chord_len)
    ev = {
        "drone": drone_generator.events(chords, cfg.chord_len, cfg.fade, tonic, rng),
        "strings": string_generator.events(chords, cfg.chord_len, cfg.fade, rng, deep_from=sec["dev"]),
        "choir": choir_generator.events(chords, cfg.chord_len, cfg.fade, rng),
        "piano": piano_generator.events(chords, cfg.chord_len, cfg.duration, rng, mean_gap=cfg.piano_gap),
        "atmosphere": atmosphere_generator.events(chords, cfg.chord_len, cfg.duration, rng),
    }
    return {"chords": chords, "events": ev, "sections": sec}


def render(cfg, out_dir, stems=True, progress=None, block=20.0):
    """Writes music-dry.wav (float) and, if stems, stem-<layer>.wav (float) into out_dir.
    Returns the plan (chords, sections) for logging."""
    plan = build(cfg)
    sr, dev = cfg.sample_rate, device()
    total = int(cfg.duration * sr)
    files = {"mix": sf.SoundFile(out_dir / "music-dry.wav", "w", sr, 2, subtype="FLOAT")}
    if stems:
        for k in LAYERS:
            files[k] = sf.SoundFile(out_dir / f"stem-{k}.wav", "w", sr, 2, subtype="FLOAT")
    idx = {k: (np.array([e["start"] for e in v]), np.array([e["start"] + e["dur"] for e in v]))
           for k, v in plan["events"].items()}
    nb = int(math.ceil(total / (block * sr)))
    peak = 0.0
    with torch.no_grad():
        for b in range(nb):
            s0 = int(b * block * sr)
            s1 = min(total, s0 + int(block * sr))
            t0, t1 = s0 / sr, s1 / sr
            tt = np.arange(s0, s1) / sr
            mix = torch.zeros(2, s1 - s0, device=dev)
            for k, mod in LAYERS.items():
                gain = getattr(cfg, k) * BALANCE[k]
                buf = torch.zeros(2, s1 - s0, device=dev)
                if gain > 0:
                    st, en = idx[k]
                    for j in np.nonzero((st < t1) & (en > t0))[0]:
                        e = plan["events"][k][j]
                        i0 = max(s0, int(math.ceil(e["start"] * sr))) - s0
                        i1 = min(s1, int(math.floor((e["start"] + e["dur"]) * sr))) - s0
                        if i1 <= i0:
                            continue
                        t = (torch.arange(i0, i1, device=dev, dtype=torch.float64) / sr + (t0 - e["start"])).float()
                        left, right = mod.render(e, t, sr)
                        buf[0, i0:i1] += left
                        buf[1, i0:i1] += right
                    buf *= torch.from_numpy(intensity(k, tt, cfg, plan["sections"]) * gain).float().to(dev)
                mix += buf
                if stems:
                    files[k].write(buf.T.cpu().numpy())
            peak = max(peak, float(mix.abs().max()))
            files["mix"].write(mix.T.cpu().numpy())
            if progress:
                progress((b + 1) / nb)
    for f in files.values():
        f.close()
    return {"peak": peak, "chords": len(plan["chords"]), "sections": plan["sections"], "config": asdict(cfg)}
