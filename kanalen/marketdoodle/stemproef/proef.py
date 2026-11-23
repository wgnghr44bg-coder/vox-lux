"""Stemproef verteller What If (eigenaar 23 nov: "hij mag wel iets enthousiaster zijn")."""
import sys
from pathlib import Path
sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/tools"); sys.path.insert(0, r"C:/Users/rane/Documents/vox-lux-routine/audio_engine")
import numpy as np, soundfile as sf, b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
ZIN = ["It's 7:15 in the morning. You walk into the kitchen.", "And above your dad's head, there's a glowing number.",
       "Sixty-four thousand dollars.", "So, what if you could see how much everyone earns?"]
for letter, v, spd in (("A", "eigen-stem-swan", 1.05), ("B", "swan-a", 1.0), ("C", "swan-f", 1.0), ("D", "swan-b", 1.0), ("E", "eigen-stem-trrr", 1.05)):
    cfg = VoiceConfig(voice=v, speed=spd, seed=7, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    out = [edge_fade(trim(c, SR), SR) for c in ov.speak(ZIN, cfg, seed=7)]
    stil = np.zeros(int(0.45 * SR), np.float32)
    sf.write(H / f"stem-{letter}.wav", np.concatenate(sum([[c, stil] for c in out], [])), SR); print(letter, v, flush=True)
