"""Stemproef met OmniVoice (de engine van VoiceStudio), gratis en lokaal.

Per stemontwerp: eerst één referentiezin maken met `instruct`, daarna de rest
van de tekst klonen van die zin, zodat de stem over alle zinnen gelijk blijft
(zo zou ook een hele video gaan). Pauzes zoals make_voice_local.py.

Gebruik: omnivoice-venv/Scripts/python.exe tools/comfy/omnivoice_proef.py uitmap
"""
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
import torch
from omnivoice import OmniVoice

SR = 24000
REF = "The evening is quiet now, and the kettle is warming slowly on the stove."
TEKST = """Tonight we are going nearly ninety years back, to a quiet street in an English town, in the late summer of 1939.
[long-pause]
The hedges are heavy with blackberries, the milkman is on his round, and in the front rooms, the wireless sets are warming up.
[pause]
Over the next few hours, we will wander gently through the years of the Second World War, not through its battles, but through the everyday lives of ordinary people, at home and far away."""
# (naam, instruct, seed): hetzelfde ontwerp met een ander seed geeft een andere stem
ONTWERPEN = [
    ("slaap-1", "male, elderly, very low pitch, british accent", 11),
    ("slaap-2", "male, elderly, very low pitch, british accent", 23),
    ("slaap-3", "male, elderly, very low pitch, british accent", 37),
    ("slaap-4", "male, elderly, very low pitch, british accent", 51),
    ("slaap-5", "male, elderly, very low pitch, british accent", 64),
    ("slaap-6", "male, elderly, very low pitch, british accent", 78),
]
STIL = {"zin": 0.6, "[pause]": 0.9, "[long-pause]": 1.7}

uit = Path(sys.argv[1]); uit.mkdir(parents=True, exist_ok=True)
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
if len(sys.argv) > 3:  # eigen opname klonen: uitmap ref.wav "tekst van ref.wav"
    ONTWERPEN = [("eigen-mp3", None, 7)]
for naam, instruct, seed in ONTWERPEN:
    torch.manual_seed(seed)
    if instruct:
        ref = model.generate(text=REF, instruct=instruct, speed=0.85)[0]
        sf.write(uit / f"{naam}-ref.wav", ref, SR)
        prompt = model.create_voice_clone_prompt(ref_audio=str(uit / f"{naam}-ref.wav"), ref_text=REF)
    else:
        prompt = model.create_voice_clone_prompt(ref_audio=sys.argv[2], ref_text=sys.argv[3])
    stukken = []
    for regel in TEKST.splitlines():
        regel = regel.strip()
        if regel in STIL:
            stukken.append(np.zeros(int(STIL[regel] * SR), dtype=np.float32)); continue
        audio = model.generate(text=regel, voice_clone_prompt=prompt, speed=0.85)[0]
        stukken += [audio.astype(np.float32), np.zeros(int(STIL["zin"] * SR), dtype=np.float32)]
    sf.write(uit / f"{naam}.wav", np.concatenate(stukken), SR)
    print("klaar", naam, flush=True)
