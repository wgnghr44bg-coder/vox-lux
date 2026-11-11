"""Voice settings and the voice library (voices/<name>/ref.wav + voice.json)."""
import json
from dataclasses import dataclass
from pathlib import Path

VOICES = Path(__file__).resolve().parent.parent / "voices"

# What OmniVoice voice design actually supports (omnivoice/cli/demo.py, v0.2.1): gender, age, pitch,
# whisper style and accent. Timbre words such as 'warm', 'raspy' or 'chest voice' are not understood,
# so a narrator is designed from these attributes plus a seed, and then kept fixed by cloning its
# reference clip for every sentence.
DESIGN_OPTIONS = {
    "gender": ["male", "female"],
    "age": ["young adult", "middle-aged", "elderly"],
    "pitch": ["very low pitch", "low pitch", "moderate pitch", "high pitch"],
    "accent": ["british accent", "american accent", "australian accent", "canadian accent"],
}


@dataclass
class VoiceConfig:
    voice: str = "narrator-b"
    speed: float = 0.64            # ±125-130 words/min incl. pauses (measured 6 nov: 0.62 -> 124, 0.76 -> 140), like the owner's example
    seed: int = 7
    num_step: int = 32             # OmniVoice diffusion steps (more = slower, slightly cleaner)
    guidance_scale: float = 2.0
    denoise: bool = True
    batch_size: int = 4            # sentences generated together on the GPU
    pause_sentence: float = 0.7    # seconds of silence after a sentence
    pause_paragraph: float = 1.1   # after a blank line
    pause_split: float = 0.3       # where a very long sentence was split at a comma
    pause_marker: float = 1.5      # [pause]
    pause_long_marker: float = 2.8  # [long-pause]
    max_chars: int = 260           # longer sentences are split at ; or ,
    lead_in: float = 0.5           # silence at the start


def ref_wav(d, meta):
    """voices/<name>/ref.wav, or (eigen stem van de eigenaar, 11 nov 2026) alleen op de pc: voice.json "ref_pc".
    De repo is openbaar, dus een echte stem staat niet op GitHub."""
    if (d / "ref.wav").exists() or not meta.get("ref_pc"):
        return d / "ref.wav"
    p = Path(meta["ref_pc"]).expanduser()
    if not p.exists():
        raise FileNotFoundError(f"stem {d.name}: {p} ontbreekt (staat alleen op de pc van de eigenaar, niet op GitHub)")
    return p


def list_voices():
    out = []
    for p in VOICES.iterdir():
        if (p / "voice.json").exists():
            meta = json.loads((p / "voice.json").read_text(encoding="utf-8"))
            if (p / "ref.wav").exists() or Path(meta.get("ref_pc", "-")).expanduser().exists():
                out.append(p.name)
    return sorted(out)


def load_voice(name):
    d = VOICES / name
    meta = json.loads((d / "voice.json").read_text(encoding="utf-8"))
    return ref_wav(d, meta), meta
