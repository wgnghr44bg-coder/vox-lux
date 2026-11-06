"""Layer A: deep ambient drone. A pedal on the key tonic (or the chord root when the tonic does not fit),
sine foundation with a few soft overtones, a quiet sub-octave and a very slow breathing volume."""
import torch

from .note_calculator import midi_to_hz
from .oscillator import additive, lfo, raised_cosine_env

LOW, HIGH = 40, 51          # E2..D#3 (± 80-150 Hz in 432 tuning): deep but not boomy


def events(chords, chord_len, fade, tonic_pc, rng):
    out = []
    for i, c in enumerate(chords):
        pc = tonic_pc if tonic_pc in c["pcs"] else c["root_pc"]
        note = next(m for m in range(LOW, HIGH + 1) if m % 12 == pc)
        if out and out[-1]["note"] == note:            # same pedal note: keep sounding, no crossfade
            out[-1]["dur"] += chord_len
            continue
        out.append({"start": i * chord_len, "dur": chord_len + fade, "note": note, "fade": fade,
                    "phase": float(rng.uniform(0, 6.28)), "am_rate": float(rng.uniform(0.03, 0.07)),
                    "am_phase": float(rng.uniform(0, 6.28))})
    return out


def render(ev, t, sr):
    f = midi_to_hz(ev["note"])
    env = raised_cosine_env(t, ev["dur"], ev["fade"], ev["fade"]) * lfo(t, ev["am_rate"], ev["am_phase"], 0.18, 0.82)
    left = additive(t, f - 0.07, [1.0, 0.22, 0.10, 0.04], ev["phase"], sr)
    right = additive(t, f + 0.07, [1.0, 0.22, 0.10, 0.04], ev["phase"] + 0.9, sr)
    sub = 0.28 * torch.sin(2 * torch.pi * (f / 2) * t + ev["phase"]) if f / 2 >= 50 else 0.0
    return (left + sub) * env * 0.5, (right + sub) * env * 0.5
