"""Stem met de Audio Engine (eigenaar 6 nov 2026: "Deze wil ik" = audio-engine-rustiger): zelfde in- en uitvoer
als tools/comfy/make_voice_omni.py (voice.mp3 + voice-times.tsv, stem start op 0,8 s), zodat de rest van de
videostraat gelijk blijft, maar met de Audio Engine-stem, in groepjes van 4 zinnen op de GPU (dat geeft het
rustige tempo van de proef, ±125 woorden/min) en met stilte voor/na elke zin weggeknipt.

Instellingen uit <map>/stem.json (anders de standaard hieronder):
  {"engine_voice": "narrator-b", "speed": 0.62, "seed": 7, "klank": "highpass=f=60"}
Pauzes zoals make_voice_omni (zin 1,1 s, [pause] 1,5 s, [long-pause] 2,8 s); add_pauses.py --kort haalt er
daarna 0,4 s af, dus tussen zinnen ±0,7 s, zoals de gekozen proef.

Gebruik: C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_stem.py stories/<map>
"""
import json, os, subprocess, sys, tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent / "audio_engine"))
import xai_voiceover as xv                                 # alleen het opsplitsen van het script (geen xAI)

import numpy as np
import soundfile as sf

from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig

LEAD, SR = 0.8, ov.SR
STANDAARD = {"engine_voice": "narrator-e", "speed": 0.54, "seed": 7, "pauze": 1.4, "klank": "highpass=f=60"}

m = Path(sys.argv[1])
inst = {**STANDAARD, **(json.loads((m / "stem.json").read_text(encoding="utf-8")) if (m / "stem.json").exists() else {})}
cfg = VoiceConfig(voice=inst["engine_voice"], speed=inst["speed"], seed=inst["seed"])
xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = 1500, 2800, 1100
pieces = xv.split_script((m / "script-cues.txt").read_text(encoding="utf-8"))
# "pauze" in stem.json (eigenaar 7 nov 2026, proef B1: pauzes 40% langer): de stilte die na add_pauses --kort
# overblijft (alles boven 0,4 s) wordt zoveel keer langer.
f = float(inst.get("pauze", 1.0))
pieces = [xv.Piece(" ".join(xv.TAG_RE.sub("", p.text).split()),
                   round((p.silence_after_ms - 400) * f + 400) if p.silence_after_ms > 400 else p.silence_after_ms, p.cue)
          for p in pieces]
print(f"{len(pieces)} zinnen, stem {cfg.voice}, speed {cfg.speed}", flush=True)

clips = [None] * len(pieces)
if "--hergebruik" in sys.argv and (m / "voice-times.tsv").exists():
    # alleen nieuwe of gewijzigde zinnen inspreken; de rest uit de bestaande voice.mp3 knippen (bv. kortere intro/outro)
    oud = subprocess.run(["ffmpeg", "-v", "error", "-i", str(m / "voice.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    oud = np.frombuffer(oud, np.float32)
    knip = {}
    for r in (m / "voice-times.tsv").read_text(encoding="utf-8").splitlines()[1:]:
        c = r.split("\t")
        if len(c) >= 5 and c[4] not in knip:
            knip[c[4]] = oud[int(float(c[1]) * SR): int(float(c[2]) * SR)].copy()
    for i, p in enumerate(pieces):
        if p.text in knip:
            clips[i] = knip[p.text]
    print(f"hergebruikt: {sum(c is not None for c in clips)} zinnen, nieuw: {sum(c is None for c in clips)}", flush=True)
nieuw = [i for i, c in enumerate(clips) if c is None]
for b in range(0, len(nieuw), 4):
    idx = nieuw[b:b + 4]
    for i, wav in zip(idx, ov.speak([pieces[i].text for i in idx], cfg, seed=cfg.seed + b)):
        clips[i] = edge_fade(trim(wav, SR), SR)
    for i in idx:                                          # korte zinnen komen soms leeg terug: los opnieuw
        poging = 0
        while len(clips[i]) < 0.25 * SR and poging < 10:
            poging += 1
            clips[i] = edge_fade(trim(ov.speak([pieces[i].text], cfg, seed=cfg.seed + 1000 * poging + i)[0], SR), SR)
    print(f"klaar {idx[-1] + 1}/{len(pieces)}", flush=True)

parts, rows, t = [np.zeros(int(LEAD * SR), np.float32)], [], LEAD
for i, (p, wav) in enumerate(zip(pieces, clips), 1):
    d = len(wav) / SR
    rows.append(f"{i}\t{t:.2f}\t{t + d:.2f}\t{p.cue}\t{p.text}")
    parts += [wav, np.zeros(int(p.silence_after_ms / 1000 * SR), np.float32)]
    t += d + p.silence_after_ms / 1000
with tempfile.TemporaryDirectory() as tmp:
    sf.write(os.path.join(tmp, "voice.wav"), np.concatenate(parts), SR)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(tmp, "voice.wav"), "-b:a", "192k",
                    str(m / "voice.mp3")], check=True)
with open(m / "voice-times.tsv", "w", encoding="utf-8") as f:
    f.write("#\tstart\tend\timage\ttext\n" + "\n".join(rows) + "\n")
words = sum(len(p.text.split()) for p in pieces)
print(f"voice.mp3 + voice-times.tsv: {len(rows)} regels, stem eindigt op {t:.1f} s, {words / (t / 60):.0f} woorden/min")
