"""Voice-over voor een bodycam-video met de eigen stem (OmniVoice, lokaal, gratis).

Elke alinea in script.txt (zonder '#'- en '[BEELD'-regels) wordt een los blok: <map>/stem/blok01.wav ...
plus stem/blokken.json (tekst + duur), zodat de montage elk blok op het juiste beeld kan leggen.
Zelfde stem en klank als B1 (audio_engine/B1.json), maar snelheid 1.0 en korte pauzes (geen slaaptempo),
zonder muziek of haard eronder.

  C:/Users/rane/omnivoice-venv/Scripts/python.exe kanalen/bodycam/maak_voiceover.py kanalen/bodycam/videos/<map> [--speed 1.0] [--stem-map <map>]
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig

map_ = Path(sys.argv[1])
speed = float(sys.argv[sys.argv.index("--speed") + 1]) if "--speed" in sys.argv else 1.0
inst = b1.standaard()
seed = int(inst["seed"])
# --stem-map <map met ref.wav + voice.json (ref_text)>: een andere stem (alleen stemmen waar de eigenaar de rechten op
# heeft). Standaard de eigen stem. Stemmen staan buiten de openbare repo (C:/Users/rane/vox-lux-stemmen/<naam>).
if "--stem-map" in sys.argv:
    stem_map = Path(sys.argv[sys.argv.index("--stem-map") + 1])
    meta = json.loads((stem_map / "voice.json").read_text(encoding="utf-8"))
else:
    stem_map = Path("C:/Users/rane/vox-lux-stemmen/eigen-stem")
    meta = json.loads((ROOT / "audio_engine/voices/eigen-stem/voice.json").read_text(encoding="utf-8"))
ov._prompts["bodycam"] = ov.model().create_voice_clone_prompt(ref_audio=str(stem_map / "ref.wav"),
                                                              ref_text=meta["ref_text"])
cfg = VoiceConfig(voice="bodycam", speed=speed, seed=seed, num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
SR = ov.SR

regels = [r for r in (map_ / "script.txt").read_text(encoding="utf-8").splitlines()
          if not r.startswith("#") and not r.startswith("[BEELD")]
alineas = [" ".join(a.split()) for a in re.split(r"\n\s*\n", "\n".join(regels)) if a.strip()]
uit = map_ / "stem"
uit.mkdir(exist_ok=True)
blokken = []
for n, alinea in enumerate(alineas, 1):
    zinnen = [z for z in re.split(r"(?<=[.!?])\s+", alinea) if z]
    clips = []
    for i, z in enumerate(zinnen):
        for poging in range(8):  # afgekapte of veel te snelle zinnen opnieuw (zoals tools/engine_stem.py)
            wav = edge_fade(trim(ov.speak([z], cfg, seed=seed + 1000 * poging + 37 * n + i)[0], SR), SR)
            d, w = len(wav) / SR, len(z.split())
            if d >= 0.25 and w / (d / 60) <= (250 if w >= 8 else 320):
                break
            print(f"blok {n} zin {i + 1} afgekapt, opnieuw", flush=True)
        clips += [wav, np.zeros(int(0.45 * SR), np.float32)]
    ruw = uit / f"ruw{n:02d}.wav"
    sf.write(ruw, np.concatenate(clips[:-1]), SR)
    doel = uit / f"blok{n:02d}.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(ruw), "-af", inst["klank"], "-ar", "48000", "-ac", "1",
                    str(doel)], check=True)
    ruw.unlink()
    duur = sf.info(doel).duration
    blokken.append({"blok": n, "bestand": doel.name, "duur": round(duur, 2), "tekst": alinea})
    print(f"blok {n:02d}: {duur:5.1f} s  {alinea[:70]}", flush=True)
(uit / "blokken.json").write_text(json.dumps(blokken, indent=1, ensure_ascii=False), encoding="utf-8")
tot = sum(b["duur"] for b in blokken)
print(f"klaar: {len(blokken)} blokken, {tot:.0f} s stem, {sum(len(b['tekst'].split()) for b in blokken) / (tot / 60):.0f} woorden/min")
