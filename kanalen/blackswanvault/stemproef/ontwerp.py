"""20 nov: nieuwe ontworpen stemmen (OmniVoice voice design), levendiger en hoger dan zakelijk-23.
Eigenaar zocht een stem 'die veel hierop lijkt' (vertelstijl van een groot uitlegkanaal); we klonen niemand, alleen eigen ontwerp."""
import sys, json
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, librosa
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
import b1
inst = b1.standaard()
H = Path(__file__).parent
REF = "OpenAI made a promise to its investors that would make anyone do a double take. And nobody saw what happened next coming."
TEST = ("In July, something strange happened inside one of the most powerful AI labs in the world. "
        "Its own AI agents broke out of their test, and hacked into a real company. So how did this happen? "
        "And why is California now taking OpenAI to court?")
KAND = [("swan-g", "young adult", "high pitch", 19), ("swan-h", "young adult", "high pitch", 88), ("swan-i", "young adult", "high pitch", 123), ("swan-j", "young adult", "high pitch", 256)]
uit = []
if __name__ != "__main__": KAND = []
for naam, age, pitch, seed in KAND:
    ov.design_voice(naam, "male", age, pitch, "american accent", seed, ref_text=REF, speed=1.0)
    cfg = VoiceConfig(voice=naam, speed=1.0, seed=seed, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    a = ov.speak([TEST], cfg, seed=seed)[0]
    sf.write(H / f"{naam}.wav", a, ov.SR)
    f0, v, _ = librosa.pyin(a, fmin=60, fmax=400, sr=ov.SR); f = f0[~np.isnan(f0)]
    wpm = len(TEST.split()) / (len(a) / ov.SR / 60)
    r = dict(naam=naam, age=age, pitch=pitch, seed=seed, hz=round(float(np.median(f))), spreiding=round(float(np.std(f))), wpm=round(wpm))
    print(r, flush=True); uit.append(r)
if uit: json.dump(uit, open(H / "meting2.json", "w"), indent=1)
