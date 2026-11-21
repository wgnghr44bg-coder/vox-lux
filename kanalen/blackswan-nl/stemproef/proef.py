"""21 nov 2026: Nederlandse zakelijke stem voor de NL-versie van BlackswanVault (OmniVoice voice design, gratis, lokaal).
Geen kloon van iemand; ontworpen stem met Nederlandse referentietekst. Uitvoer: <naam>.wav + alles.mp3 (achter elkaar)."""
import sys, json
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
import b1
inst = b1.standaard()
H = Path(__file__).parent
REF = "Uiteindelijk draait elk groot bedrijf om één simpel idee, en heel veel hard werken."
TEST = ("Op twaalf november liep de machtigste man uit de chipindustrie weg bij het bedrijf dat hij zelf had gebouwd. "
        "Drieëndertig jaar lang was Jensen Huang Nvidia. Dus wat is er gebeurd? En wat betekent dit voor ASML?")
KAND = [("nl-a", "male, middle-aged, moderate pitch", 23), ("nl-b", "male, middle-aged, low pitch", 41),
        ("nl-c", "male, young adult, moderate pitch", 77), ("nl-d", "female, middle-aged, moderate pitch", 12)]
stukken = []
for naam, instruct, seed in KAND:
    try:
        import torch
        torch.manual_seed(seed)
        with torch.no_grad():
            ref = ov.model().generate(text=REF, instruct=instruct, speed=1.0)[0]
        d = ov.VOICES / naam; d.mkdir(parents=True, exist_ok=True)
        sf.write(d / "ref.wav", np.asarray(ref, dtype=np.float32), ov.SR)
        (d / "voice.json").write_text(json.dumps({"name": naam, "description": "designed with OmniVoice voice design (Nederlands)",
            "ref_text": REF, "instruct": instruct, "seed": seed, "design_speed": 1.0, "default_speed": 0.64}, indent=2), encoding="utf-8")
        ov._prompts.pop(naam, None)
    except Exception as e:
        print(naam, "ontwerp mislukt:", e); continue
    cfg = VoiceConfig(voice=naam, speed=1.0, seed=seed, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    a = ov.speak([TEST], cfg, seed=seed)[0]
    sf.write(H / f"{naam}.wav", a, ov.SR); print(naam, round(len(a) / ov.SR, 1), "s", flush=True)
    stukken += [a, np.zeros(int(ov.SR * 1.2), dtype=np.float32)]
if stukken: sf.write(H / "alles.wav", np.concatenate(stukken), ov.SR)
