"""Layer D: occasional soft piano-like notes. Sparse single notes from the current chord (no melody),
felt-soft attack, slightly stretched overtones, two strings that beat gently, long natural decay."""
from .note_calculator import midi_to_hz
from .oscillator import additive, pan_gains
import torch

DUR = 9.0


def events(chords, chord_len, duration, rng, mean_gap=9.0):
    out, t = [], float(rng.uniform(2, mean_gap))
    while t < duration - 3:
        c = chords[min(int(t // chord_len), len(chords) - 1)]
        pc = c["pcs"][rng.integers(len(c["pcs"]))]
        cands = [m for m in range(57, 77) if m % 12 == pc]
        out.append({"start": t, "dur": DUR, "note": int(cands[rng.integers(len(cands))]),
                    "vel": float(rng.uniform(0.5, 0.9)), "pan": float(rng.uniform(-0.4, 0.4)),
                    "phase": float(rng.uniform(0, 6.28))})
        t += float(rng.exponential(mean_gap)) + 1.5
    return out


def render(ev, t, sr):
    f = midi_to_hz(ev["note"])
    vel = ev["vel"]
    amps = [vel * (1.0 / k ** 1.6) * (0.7 + 0.3 * vel) ** (k - 1) for k in range(1, 9)]
    decays = [0.45 + 0.35 * (k - 1) for k in range(1, 9)]
    s = additive(t, f, amps, ev["phase"], sr, inharm=0.0003, decays=decays)
    s = s + additive(t, f * 2 ** (0.4 / 1200), amps, ev["phase"] + 1.3, sr, inharm=0.0003, decays=decays)
    att = torch.clamp(t / 0.008, 0, 1)                               # felt hammer: no hard click
    rel = torch.clamp((ev["dur"] - t) / 1.5, 0, 1)
    s = s * att * rel * 0.5
    gl, gr = pan_gains(ev["pan"])
    return s * gl, s * gr
