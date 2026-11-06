"""OmniVoice on the GPU: one model in memory, one clone prompt per voice (so every sentence has the same
speaker), and voice design for new narrators."""
import json

import numpy as np
import soundfile as sf
import torch

from .voice_config import VOICES, load_voice

SR = 24000
_model = None
_prompts = {}


def model():
    global _model
    if _model is None:
        from omnivoice import OmniVoice
        dev = "cuda:0" if torch.cuda.is_available() else "cpu"
        _model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map=dev,
                                           dtype=torch.float16 if dev != "cpu" else torch.float32)
    return _model


def gen_config(cfg):
    from omnivoice.models.omnivoice import OmniVoiceGenerationConfig
    return OmniVoiceGenerationConfig(num_step=cfg.num_step, guidance_scale=cfg.guidance_scale, denoise=cfg.denoise)


def prompt(voice):
    if voice not in _prompts:
        ref, meta = load_voice(voice)
        _prompts[voice] = model().create_voice_clone_prompt(ref_audio=str(ref), ref_text=meta["ref_text"])
    return _prompts[voice]


def speak(texts, cfg, seed):
    """List of texts -> list of float32 numpy arrays (24 kHz mono), all in cfg.voice."""
    torch.manual_seed(seed)
    p = prompt(cfg.voice)
    with torch.no_grad():
        out = model().generate(text=list(texts), voice_clone_prompt=[p] * len(texts), speed=cfg.speed,
                               generation_config=gen_config(cfg))
    return [np.asarray(a, dtype=np.float32).reshape(-1) for a in out]


def design_voice(name, gender, age, pitch, accent, seed, ref_text=None, speed=0.8):
    """Make a new narrator from supported attributes; saves voices/<name>/ref.wav + voice.json."""
    ref_text = ref_text or "The evening is quiet now, and the kettle is warming slowly on the stove."
    instruct = f"{gender}, {age}, {pitch}, {accent}"
    torch.manual_seed(int(seed))
    with torch.no_grad():
        audio = model().generate(text=ref_text, instruct=instruct, speed=speed)[0]
    d = VOICES / name
    d.mkdir(parents=True, exist_ok=True)
    sf.write(d / "ref.wav", np.asarray(audio, dtype=np.float32), SR)
    (d / "voice.json").write_text(json.dumps({"name": name, "description": "designed with OmniVoice voice design",
                                              "ref_text": ref_text, "instruct": instruct, "seed": int(seed),
                                              "design_speed": speed, "default_speed": 0.64}, indent=2), encoding="utf-8")
    _prompts.pop(name, None)
    return d / "ref.wav"
