"""21 nov: variaties op de stem van de eigenaar (richard-nl, kloon via OmniVoice, alleen op de pc). Geen toonhoogte/tempo-trucs achteraf."""
import sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
import b1
inst = b1.standaard()
UIT = Path(r"C:/Users/rane/vox-lux-stemmen/richard")
TEST = ("Op twaalf november liep de machtigste man uit de chipindustrie weg bij het bedrijf dat hij zelf had gebouwd. "
        "Drieëndertig jaar lang was Jensen Huang Nvidia. Dus wat is er gebeurd? En wat betekent dit voor ASML?")
VAR = [("r1-gewoon", 1.0, 1), ("r2-rustig", 0.92, 1), ("r3-andere-toon", 1.0, 7), ("r4-levendig", 1.06, 3)]
for naam, speed, seed in VAR:
    cfg = VoiceConfig(voice="richard-nl", speed=speed, seed=seed, num_step=inst["model"]["num_step"],
                      guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    a = ov.speak([TEST], cfg, seed=seed)[0]
    sf.write(UIT / f"{naam}.wav", a, ov.SR); print(naam, round(len(a) / ov.SR, 1), "s", flush=True)
