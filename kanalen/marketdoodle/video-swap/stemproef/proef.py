"""Stemproef familie (eigenaar 23 nov: duidelijk verschil vader/zoon en moeder/dochter; iedereen eigen stem)."""
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/tools"); sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/audio_engine")
import numpy as np, soundfile as sf, b1, torch
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig, VOICES
from transformers import pipeline
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
NIEUW = {"whatif-papa": ("male", "middle-aged", "low pitch"), "whatif-zoon": ("male", "teenager", "high pitch"),
         "whatif-moeder": ("female", "middle-aged", "low pitch")}
for naam, (g, a, p) in NIEUW.items():
    if (VOICES / naam / "ref.wav").exists(): continue
    for sd in (3, 4, 9, 17, 30):
        ref = ov.design_voice(naam, g, a, p, "american accent", sd, ref_text="Okay, everybody, sit down please. We have a lot to do today.", speed=1.0)
        w, sr = sf.read(ref, dtype="float32")
        if "sit down" in asr({"raw": w, "sampling_rate": sr}, generate_kwargs={"language": "en"})["text"].lower(): print("stem", naam, sd, flush=True); break
ZIN = [("zoon", "Oh no. Oh no, no, no."), ("papa", "Why am I so short?"), ("zoon", "How hard can a job be?"),
       ("papa", "This is harder than my job!"), ("mama", "Where is the milk? I asked for milk."), ("dochter", "Why are you two acting so weird?")]
STEM = {"papa": "whatif-papa", "zoon": "whatif-zoon", "mama": "whatif-moeder", "dochter": "whatif-zus"}
delen = []
for k, (rol, z) in enumerate(ZIN):
    cfg = VoiceConfig(voice=STEM[rol], speed=1.0, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    c = edge_fade(trim(ov.speak([z], cfg, seed=11 + k)[0], SR), SR)
    print(rol, asr({"raw": c, "sampling_rate": SR}, generate_kwargs={"language": "en"})["text"], flush=True)
    delen += [c, np.zeros(int(0.7 * SR), np.float32)]
sf.write(H / "familie.wav", np.concatenate(delen), SR)
