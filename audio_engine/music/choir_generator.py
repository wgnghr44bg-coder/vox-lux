"""Layer C: soft synthetic choir. No samples and no words: a harmonic series shaped by vowel formants
(dark vowels 'ah', 'oh', 'oo'), slowly morphing from one vowel to another, three detuned voices per note,
slow attack and release, wide in the stereo field and kept quiet so it only adds depth."""
import torch

from .note_calculator import midi_to_hz
from .oscillator import TWO_PI, pan_gains, raised_cosine_env

# formant frequencies (Hz), bandwidths (Hz) and levels for a soft male/female mix
VOWELS = {
    "a": ([700, 1150, 2600], [110, 120, 180], [1.0, 0.55, 0.12]),
    "o": ([460, 820, 2500], [90, 100, 170], [1.0, 0.45, 0.08]),
    "u": ([330, 720, 2400], [80, 100, 160], [1.0, 0.3, 0.05]),
}


def events(chords, chord_len, fade, rng):
    out, att = [], max(fade, 3.0)
    for i, c in enumerate(chords):
        top = sorted(c["notes"])[-2:]
        top = [m + 12 if m < 60 else m for m in top]
        top = [m - 12 if m > 79 else m for m in top]
        for j, m in enumerate(top):
            v1, v2 = rng.choice(list(VOWELS), 2, replace=False)
            for v in range(3):
                out.append({"start": i * chord_len, "dur": chord_len + att, "fade": att, "note": int(m),
                            "v1": str(v1), "v2": str(v2), "cents": float((v - 1) * rng.uniform(6, 10)),
                            "pan": float((-0.7 if j == 0 else 0.7) * rng.uniform(0.5, 1.0)),
                            "phase": float(rng.uniform(0, 6.28)), "vib_rate": float(rng.uniform(4.8, 5.6)),
                            "vib_phase": float(rng.uniform(0, 6.28)), "gain": 1.0 / (3 * len(top))})
    return out


def render(ev, t, sr):
    f = midi_to_hz(ev["note"]) * 2 ** (ev["cents"] / 1200)
    nh = int(min(4500, sr * 0.45) // f)
    ks = torch.arange(1, nh + 1, device=t.device, dtype=t.dtype)
    fk = f * ks
    x = torch.clamp(t / ev["dur"], 0, 1)[None, :]                  # 0..1 over the note: vowel morph
    (F1, B1, A1), (F2, B2, A2) = VOWELS[ev["v1"]], VOWELS[ev["v2"]]
    gain = torch.zeros(nh, t.shape[0], device=t.device, dtype=t.dtype)
    for i in range(3):
        Fi = F1[i] + (F2[i] - F1[i]) * x
        Bi = B1[i] + (B2[i] - B1[i]) * x
        Ai = A1[i] + (A2[i] - A1[i]) * x
        gain = gain + Ai / (1.0 + ((fk[:, None] - Fi) / (Bi / 2)) ** 2)
    gain = gain * (1.0 / ks ** 0.6)[:, None]
    vib = (0.003 * f / ev["vib_rate"]) * torch.sin(TWO_PI * ev["vib_rate"] * t + ev["vib_phase"]) * torch.clamp(t / 2.0, 0, 1)
    ph = TWO_PI * fk[:, None] * t[None, :] + ks[:, None] * (ev["phase"] + TWO_PI * vib[None, :])
    s = (torch.sin(ph) * gain).sum(0) * raised_cosine_env(t, ev["dur"], ev["fade"], ev["fade"]) * ev["gain"]
    gl, gr = pan_gains(ev["pan"])
    return s * gl, s * gr
