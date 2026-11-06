"""Convolution reverb: a synthetic stereo impulse response (no recorded rooms), applied with FFmpeg 'afir'.

The impulse response is decaying noise in four frequency bands; high bands die away faster than low
bands (like a real hall, so the tail is soft and not hissy), plus a few early reflections and a short
pre-delay. Left and right use different noise, which gives width without phase problems.
"""
import numpy as np
import soundfile as sf

BANDS = [(0, 400, 1.0), (400, 1500, 0.85), (1500, 5000, 0.6), (5000, 24000, 0.35)]   # (lo, hi, rt60 factor)


def make_ir(path, rt60=3.5, sr=48000, predelay=0.025, seed=1):
    rng = np.random.default_rng(seed)
    n = int((predelay + rt60 * 1.1) * sr)
    t = np.arange(n) / sr
    ir = np.zeros((n, 2))
    freqs = np.fft.rfftfreq(n, 1 / sr)
    for ch in range(2):
        out = np.zeros(n)
        for lo, hi, fac in BANDS:
            spec = np.fft.rfft(rng.standard_normal(n))
            spec[(freqs < lo) | (freqs >= hi)] = 0
            band = np.fft.irfft(spec, n)
            out += band * np.exp(-6.91 * np.maximum(t - predelay, 0) / (rt60 * fac))
        out[: int(predelay * sr)] = 0
        att = int(0.02 * sr)                                   # soft onset of the diffuse tail
        out[int(predelay * sr): int(predelay * sr) + att] *= np.linspace(0, 1, att)
        for d, g in ((0.011, 0.5), (0.019, 0.35), (0.031, 0.25), (0.047, 0.18)):   # early reflections
            out[int((predelay + d + ch * 0.003) * sr)] += g * np.abs(out).max()
        ir[:, ch] = out
    ir /= np.sqrt((ir ** 2).sum(axis=0)).max()                 # unit energy: wet level stays predictable
    sf.write(path, ir.astype(np.float32), sr, subtype="FLOAT")
    return path
