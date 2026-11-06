"""Oscillators and envelopes on the GPU (torch), CPU as fallback.

All signals are computed from time *relative to the start of a note event*, so a note that spans
several render blocks continues with exactly the same phase (no clicks at block edges), and float32
stays precise (events last seconds, not hours).
"""
import math

import torch

TWO_PI = 2.0 * math.pi


def device():
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def additive(t, f, amps, phase, sr, vib_depth=0.0, vib_rate=5.0, vib_phase=0.0, inharm=0.0, decays=None):
    """Sum of harmonics k = 1..len(amps) of fundamental f.

    t: 1-D tensor, seconds since note start. amps: list of harmonic amplitudes.
    vib_depth: vibrato as a fraction of f (0.002 = 0.2 %), done as phase modulation (integrated), so the
    pitch wobbles around f instead of drifting away. inharm: piano-like stretch of the overtones.
    decays: optional per-harmonic exponential decay rates (1/s).
    """
    ks = torch.arange(1, len(amps) + 1, device=t.device, dtype=t.dtype)
    fk = f * ks * torch.sqrt(1.0 + inharm * ks * ks)
    keep = fk < sr * 0.45                                   # no aliasing above the Nyquist limit
    ks, fk = ks[keep], fk[keep]
    a = torch.tensor(amps, device=t.device, dtype=t.dtype)[keep]
    if len(ks) == 0:
        return torch.zeros_like(t)
    ph = TWO_PI * fk[:, None] * t[None, :] + phase * ks[:, None]
    if vib_depth:
        pm = (vib_depth * f / vib_rate) * torch.sin(TWO_PI * vib_rate * t + vib_phase)
        ph = ph + ks[:, None] * TWO_PI * pm[None, :]
    s = torch.sin(ph) * a[:, None]
    if decays is not None:
        d = torch.tensor(decays, device=t.device, dtype=t.dtype)[keep]
        s = s * torch.exp(-d[:, None] * t[None, :])
    return s.sum(0)


def raised_cosine_env(t, dur, attack, release):
    """0 -> 1 -> 0 with smooth (raised-cosine) attack and release; flat in between."""
    a = torch.clamp(t / max(attack, 1e-3), 0, 1)
    r = torch.clamp((dur - t) / max(release, 1e-3), 0, 1)
    return (0.5 - 0.5 * torch.cos(math.pi * a)) * (0.5 - 0.5 * torch.cos(math.pi * r))


def lfo(t, rate, phase=0.0, depth=1.0, centre=1.0):
    return centre + depth * torch.sin(TWO_PI * rate * t + phase)


def pan_gains(pan):
    """Constant-power pan, pan in -1 (left) .. 1 (right)."""
    ang = (pan + 1.0) * math.pi / 4.0
    return math.cos(ang), math.sin(ang)
