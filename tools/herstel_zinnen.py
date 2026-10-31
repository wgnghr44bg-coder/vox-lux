"""Zinnen opnieuw laten inspreken (Slaap 3, OmniVoice) en precies op dezelfde plek terugzetten, zonder de video
opnieuw te monteren (eigenaar, 31 okt 2026: Oregon zei "Tonight we are, we are going").

Gebruik na tools/check_stem_tekst.py, die de zinnummers meldt:
  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/herstel_zinnen.py stories/<map> 1 435 ...
Werkt in <map>/video/stem-met-pauzes-voor-tikjes.wav (de stem vóór tools/stil_tikjes.py; ontbreekt hij, dan
stem-met-pauzes.wav). Per zin worden seeds geprobeerd tot Whisper letterlijk de tekst hoort en de zin in zijn
plek past (tot 0,3 s voor de volgende zin); zelfde zachte klank en zelfde volume als de oude zin. Het origineel
blijft als ...-voor-herstel.wav. Daarna: tools/stil_tikjes.py, check_video.py, check_stem_tekst.py, eind_volume.py.
"""
import argparse, difflib, os, re, shutil, subprocess, sys, wave
from pathlib import Path

import numpy as np

HIER = Path(__file__).parent
sys.path.insert(0, str(HIER))
import check_video as cv
from zachte_stem import KLANK

ap = argparse.ArgumentParser()
ap.add_argument("story", type=Path); ap.add_argument("zinnen", type=int, nargs="+")
ap.add_argument("--pogingen", type=int, default=8)
a = ap.parse_args()
v = a.story / "video"
wav = v / "stem-met-pauzes-voor-tikjes.wav"
wav = wav if wav.exists() else v / "stem-met-pauzes.wav"
reserve = wav.with_name(wav.stem + "-voor-herstel.wav")
if not reserve.exists():
    shutil.copy(wav, reserve)

rows = [l.split("\t") for l in open(a.story / "tijdlijn-pauzes.tsv", encoding="utf-8").read().splitlines()[1:] if l.strip()]
sec = lambda s: sum(float(p) * f for p, f in zip(s.split(":"), (3600, 60, 1)))
with wave.open(str(wav)) as w:
    sr = w.getframerate()
    x = np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float32)

import torch
from omnivoice import OmniVoice
from transformers import pipeline
model = OmniVoice.from_pretrained("k2-fsa/OmniVoice", device_map="cuda:0", dtype=torch.float16)
prompt = model.create_voice_clone_prompt(ref_audio=str(HIER / "comfy" / "stem" / "slaapstem-3.wav"),
                                         ref_text="The evening is quiet now, and the kettle is warming slowly on the stove.")
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", torch_dtype=torch.float16)
LETTERLIJK = asr.tokenizer.get_prompt_ids("Um, so, so we we went, uh, to to the the old house. I I mean, it it was",
                                          return_tensors="pt").to("cuda:0")
norm = lambda t: [re.sub(r"[^a-z0-9']", "", w) for w in re.sub(r"[\u2014\u2013-]", " ", t.lower()).split() if re.sub(r"[^a-z0-9']", "", w)]
ff = cv.FF


def klank(y24):
    """24 kHz OmniVoice -> 44,1 kHz met dezelfde zachte klank als de rest (zachte_stem.py)."""
    r = subprocess.run([ff, "-v", "error", "-f", "f32le", "-ar", "24000", "-ac", "1", "-i", "-", "-af", KLANK,
                        "-ar", str(sr), "-ac", "1", "-f", "f32le", "-"], input=y24.astype(np.float32).tobytes(),
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, np.float32) * 32767


for nr in a.zinnen:
    i = nr - 1
    t0, t1 = sec(rows[i][1]), sec(rows[i][2])
    ruimte = (sec(rows[i + 1][1]) if i + 1 < len(rows) else len(x) / sr) - 0.3 - t0
    oud = x[int(t0 * sr):int(t1 * sr)]
    doel = norm(rows[i][4])
    for p in range(a.pogingen):
        torch.manual_seed(1000 + 37 * nr + p)
        y = klank(model.generate(text=rows[i][4], voice_clone_prompt=prompt, speed=0.8)[0])
        y = y[np.argmax(np.abs(y) > 300):]                       # stilte vooraan eraf: begint op dezelfde tijd
        y16 = np.interp(np.arange(0, len(y), sr / 16000), np.arange(len(y)), y / 32768).astype(np.float32)
        hoor = asr({"raw": y16, "sampling_rate": 16000},
                   generate_kwargs={"language": "en", "prompt_ids": LETTERLIJK, "num_beams": 1})["text"]
        past = len(y) / sr <= ruimte
        hw = norm(hoor)
        dubbel = any(hw[k:k + n] == hw[k + n:k + 2 * n] and doel.count(hw[k]) < 2
                     for n in (1, 2, 3) for k in range(len(hw) - 2 * n + 1))
        goed = not dubbel and difflib.SequenceMatcher(None, doel, hw).ratio() >= 0.85
        print(f"zin {nr} poging {p + 1}: {len(y) / sr:.1f} s (ruimte {ruimte:.1f}), {'tekst goed' if goed else 'tekst: ' + hoor.strip()[:60]}")
        if goed and past:
            y *= np.sqrt(np.mean(oud ** 2) / max(np.mean(y ** 2), 1e-9))   # zelfde volume als de oude zin
            s = int(t0 * sr)
            x[s:s + int(ruimte * sr)] = 0
            x[s:s + len(y)] = y
            break
    else:
        sys.exit(f"zin {nr}: na {a.pogingen} pogingen geen goede versie; probeer meer --pogingen")

with wave.open(str(wav), "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(np.clip(x, -32768, 32767).astype("<i2").tobytes())
print(f"klaar: {len(a.zinnen)} zinnen vervangen in {wav} (origineel: {reserve.name})")
