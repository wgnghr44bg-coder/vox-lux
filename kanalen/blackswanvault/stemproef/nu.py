import sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import soundfile as sf, b1
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
from ontwerp import TEST
inst = b1.standaard()
cfg = VoiceConfig(voice="zakelijk-23", speed=1.0, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
sf.write("zakelijk-23.wav", ov.speak([TEST], cfg, seed=23)[0], ov.SR)
