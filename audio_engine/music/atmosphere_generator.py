"""Layer E: atmosphere. (1) Rare high 'shimmer' tones from the chord that swell in and out very slowly,
(2) a faint 'air' bed of many slowly breathing sines at random (inharmonic) pitches, overlapping so it
never stops or loops."""
import math

import torch

from .note_calculator import midi_to_hz
from .oscillator import TWO_PI, pan_gains, raised_cosine_env


def events(chords, chord_len, duration, rng):
    out, t = [], float(rng.uniform(3, 8))
    while t < duration - 4:
        c = chords[min(int(t // chord_len), len(chords) - 1)]
        pc = c["pcs"][rng.integers(len(c["pcs"]))]
        cands = [m for m in range(74, 87) if m % 12 == pc]
        out.append({"kind": "shimmer", "start": t, "dur": float(rng.uniform(12, 16)),
                    "note": int(cands[rng.integers(len(cands))]), "pan": float(rng.uniform(-0.6, 0.6)),
                    "phase": float(rng.uniform(0, 6.28))})
        t += float(rng.uniform(14, 26))
    t = 0.0
    while t < duration:
        out.append({"kind": "air", "start": t, "dur": 24.0, "pan": 0.35 if int(t / 12) % 2 else -0.35,
                    "freqs": [float(math.exp(rng.uniform(math.log(180), math.log(900)))) for _ in range(16)],
                    "rates": [float(rng.uniform(0.05, 0.2)) for _ in range(16)],
                    "phases": [float(rng.uniform(0, 6.28)) for _ in range(16)]})
        t += 12.0
    return out


def render(ev, t, sr):
    if ev["kind"] == "shimmer":
        f = midi_to_hz(ev["note"])
        s = torch.sin(TWO_PI * f * t + ev["phase"]) + 0.7 * torch.sin(TWO_PI * (f + 0.3) * t + ev["phase"] * 2)
        s = s * raised_cosine_env(t, ev["dur"], 5.0, 6.0) * 0.12
    else:
        fr = torch.tensor(ev["freqs"], device=t.device, dtype=t.dtype)[:, None]
        ra = torch.tensor(ev["rates"], device=t.device, dtype=t.dtype)[:, None]
        ph = torch.tensor(ev["phases"], device=t.device, dtype=t.dtype)[:, None]
        am = 0.5 + 0.5 * torch.sin(TWO_PI * ra * t[None, :] + ph)
        s = (torch.sin(TWO_PI * fr * t[None, :] + ph * 3) * am).sum(0) / 16
        s = s * raised_cosine_env(t, ev["dur"], 12.0, 12.0) * 0.08
    gl, gr = pan_gains(ev["pan"])
    return s * gl, s * gr
