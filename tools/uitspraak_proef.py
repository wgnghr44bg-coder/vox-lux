"""Proef voor de uitspraaklijst (stap 6, eigenaar 17 nov 2026): per naam één zin met de vaste B1-stem, eerst zoals
het er staat, dan met de fonetische spelling uit audio_engine/uitspraak.json. Zo hoort de eigenaar welke beter is.

  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/uitspraak_proef.py <uit.mp3> [Naam1,Naam2]
"""
import json, subprocess, sys, tempfile, os
from pathlib import Path
HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER)); sys.path.insert(0, str(HIER.parent / "audio_engine"))
import numpy as np, soundfile as sf
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig

uit = Path(sys.argv[1])
lijst = {k: v for k, v in json.loads((HIER.parent / "audio_engine" / "uitspraak.json").read_text(encoding="utf-8")).items()
         if not k.startswith("_")}
if len(sys.argv) > 2:
    lijst = {k: lijst[k] for k in sys.argv[2].split(",")}
inst = b1.standaard()
cfg = VoiceConfig(voice=inst["engine_voice"], speed=inst["speed"], seed=inst["seed"], num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
SR, delen = ov.SR, []
for naam, klank in lijst.items():
    a, b = ov.speak([f"This is {naam}.", f"This is {klank}."], cfg, seed=cfg.seed)
    delen += [edge_fade(trim(a, SR), SR), np.zeros(int(0.7 * SR), np.float32),
              edge_fade(trim(b, SR), SR), np.zeros(int(1.6 * SR), np.float32)]
    print(naam, "->", klank, flush=True)
with tempfile.TemporaryDirectory() as t:
    sf.write(os.path.join(t, "p.wav"), np.concatenate(delen), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(t, "p.wav"), "-b:a", "128k", str(uit)], check=True)
print("klaar:", uit)
