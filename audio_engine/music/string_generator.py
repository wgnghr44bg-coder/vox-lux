"""Layer B: cinematic string pads. Every chord note is an ensemble of three slightly detuned voices with
soft saw-like overtones, gentle vibrato, slow attack/release (= the crossfade to the next chord), spread
across the stereo field. From the middle section on a low cello-like root sometimes doubles the harmony."""
from .note_calculator import midi_to_hz
from .oscillator import additive, pan_gains, raised_cosine_env

PARTIALS = [1.0 / k ** 1.5 * (0.88 ** k) for k in range(1, 11)]
CELLO = [1.0 / k ** 1.3 * (0.8 ** k) for k in range(1, 9)]


def events(chords, chord_len, fade, rng, deep_from=None):
    out = []
    for i, c in enumerate(chords):
        start, notes = i * chord_len, c["notes"]
        for j, m in enumerate(notes):
            pan = -0.6 + 1.2 * j / max(len(notes) - 1, 1)
            for v in range(3):
                out.append({"start": start, "dur": chord_len + fade, "fade": fade, "note": m, "amps": PARTIALS,
                            "cents": float((v - 1) * rng.uniform(4, 7)), "pan": pan + float(rng.uniform(-0.15, 0.15)),
                            "phase": float(rng.uniform(0, 6.28)), "vib_rate": float(rng.uniform(4.6, 5.6)),
                            "vib_phase": float(rng.uniform(0, 6.28)), "gain": 1.0 / (3 * len(notes))})
        if deep_from is not None and start >= deep_from and rng.random() < 0.55:
            root = next(m for m in range(38, 50) if m % 12 == c["root_pc"])
            for v in range(2):
                out.append({"start": start, "dur": chord_len + fade, "fade": fade, "note": root, "amps": CELLO,
                            "cents": float((v - 0.5) * 6), "pan": float((v - 0.5) * 0.4),
                            "phase": float(rng.uniform(0, 6.28)), "vib_rate": float(rng.uniform(4.4, 5.2)),
                            "vib_phase": float(rng.uniform(0, 6.28)), "gain": 0.32})
    return out


def render(ev, t, sr):
    f = midi_to_hz(ev["note"]) * 2 ** (ev["cents"] / 1200)
    s = additive(t, f, ev["amps"], ev["phase"], sr, vib_depth=0.0018, vib_rate=ev["vib_rate"], vib_phase=ev["vib_phase"])
    s = s * raised_cosine_env(t, ev["dur"], ev["fade"], ev["fade"]) * ev["gain"]
    gl, gr = pan_gains(max(-1.0, min(1.0, ev["pan"])))
    return s * gl, s * gr
