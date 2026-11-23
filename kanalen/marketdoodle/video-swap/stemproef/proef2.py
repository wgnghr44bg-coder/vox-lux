"""Stemproef 2: mama en zusje moeten duidelijk anders klinken (eigenaar 23 nov)."""
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
NIEUW = {"whatif-moeder2": ("female", "middle-aged", "very low pitch"), "whatif-meisje": ("female", "child", "moderate pitch"),
         "whatif-meisje2": ("female", "child", "high pitch")}
for naam, (g, a, p) in NIEUW.items():
    if (VOICES / naam / "ref.wav").exists(): continue
    for sd in (3, 4, 9, 17, 30, 42, 55):
        ref = ov.design_voice(naam, g, a, p, "american accent", sd, ref_text="Okay, everybody, sit down please. We have a lot to do today.", speed=1.0)
        w, sr = sf.read(ref, dtype="float32")
        if "sit down" in asr({"raw": w, "sampling_rate": sr}, generate_kwargs={"language": "en"})["text"].lower(): print("stem", naam, sd, flush=True); break
    else: print("MISLUKT", naam, flush=True)
ZIN = [("whatif-moeder2", "Where is the milk? I asked for milk."), ("whatif-meisje", "Why are you two acting so weird?"),
       ("whatif-moeder2", "Where is the milk? I asked for milk."), ("whatif-meisje2", "Why are you two acting so weird?")]
for k, (v, z) in enumerate(ZIN):
    if not (VOICES / v / "ref.wav").exists(): continue
    cfg = VoiceConfig(voice=v, speed=1.0, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    c = edge_fade(trim(ov.speak([z], cfg, seed=11 + k)[0], SR), SR)
    print(v, asr({"raw": c, "sampling_rate": SR}, generate_kwargs={"language": "en"})["text"], flush=True)
    sf.write(H / f"p2-{k}.wav", c, SR)
