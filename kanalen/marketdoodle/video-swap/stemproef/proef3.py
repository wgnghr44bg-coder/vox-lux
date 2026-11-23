"""Stemproef 3: mama en zusje nog verder uit elkaar (eigenaar: 'teveel op elkaar')."""
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/tools"); sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/audio_engine")
import numpy as np, soundfile as sf, b1, torch, librosa
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig, VOICES
from transformers import pipeline
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
naam = "whatif-moeder-uk"
if not (VOICES / naam / "ref.wav").exists():
    for sd in (3, 4, 9, 17, 30):
        ref = ov.design_voice(naam, "female", "middle-aged", "very low pitch", "british accent", sd, ref_text="Okay, everybody, sit down please. We have a lot to do today.", speed=1.0)
        w, sr = sf.read(ref, dtype="float32")
        if "sit down" in asr({"raw": w, "sampling_rate": sr}, generate_kwargs={"language": "en"})["text"].lower(): print("stem", naam, sd); break
def zeg(v, z, spd=1.0, seed=11):
    cfg = VoiceConfig(voice=v, speed=spd, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    return edge_fade(trim(ov.speak([z], cfg, seed=seed)[0], SR), SR)
MAMA, ZUS = "Where is the milk? I asked for milk.", "Why are you two acting so weird?"
stil = np.zeros(int(0.7 * SR), np.float32)
zus = zeg("whatif-meisje2", ZUS, 1.05, 14)
zus_hoog = librosa.effects.pitch_shift(zus, sr=SR, n_steps=3)            # meisje 3 halve tonen hoger
for letter, mama in (("C", zeg("whatif-moeder-uk", MAMA, 0.95, 12)), ("D", zeg("whatif-moeder2", MAMA, 0.9, 12))):
    for v, c in (("mama", mama), ("zus", zus_hoog)): print(letter, v, asr({"raw": c, "sampling_rate": SR}, generate_kwargs={"language": "en"})["text"], flush=True)
    sf.write(H / f"optie-{letter}.wav", np.concatenate([mama, stil, zus_hoog]), SR)
