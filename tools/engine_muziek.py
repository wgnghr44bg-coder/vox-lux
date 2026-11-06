"""Achtergrondmuziek met de Audio Engine (eigenaar 6 nov 2026: "de achtergrond muziek is perfect"): zacht koor met
strijkers in 432 Hz, elke 7 s een ander akkoord (stijl "referentie"), al gedukt onder de stem en met dezelfde
vorm als in de gekozen proef (laag eraf onder 120 Hz, dipje rond 2,5 kHz voor verstaanbaarheid).

Schrijft <map>/video/muziek432.wav (zelfde naam als vroeger, dus make_video.py pakt hem zo op) en
<map>/video/muziek-db.txt: het --muziek-db voor make_video/check_video/qc_video, zo gekozen dat de muziek
11 LUFS onder de stem staat (zoals het voorbeeld van de eigenaar).

Gebruik (na add_pauses + zachte_stem): C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_muziek.py stories/<map>
"""
import sys, zlib
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "audio_engine"))

import numpy as np
import soundfile as sf

from effects import volume_control as vc
from mixer import ducking
from mixer.voice_music_mixer import MixConfig, music_shaping
from music.composition_engine import preset
from music.music_studio import generate

m = Path(sys.argv[1])
v = m / "video"
stem = v / "stem-met-pauzes.wav"
mix = MixConfig()
dur = sf.info(stem).duration + 60
seed = zlib.crc32(m.name.encode()) % 1000              # elke video eigen akkoordenreeks, wel steeds dezelfde
werk = v / "engine-muziek"
generate(preset("referentie", duration=dur, seed=seed), werk, stems=False,
         progress=lambda f, s="": print(f"\r{f * 100:5.1f}% {s:<30}", end="", flush=True))
print()
vorm = v / "_muziek-vorm.wav"
vc.ffmpeg(["-i", str(werk / "music.wav"), "-af", music_shaping(mix), "-ar", "44100", "-c:a", "pcm_f32le", str(vorm)])
curve = ducking.gain_curve(stem, mix.duck_amount_db, mix.duck_attack, mix.duck_release)
uit = v / "muziek432.wav"
with sf.SoundFile(vorm) as fi, sf.SoundFile(uit, "w", 44100, 2, subtype="PCM_24") as fo:
    pos = 0
    for blok in fi.blocks(blocksize=44100 * 30, always_2d=True, dtype="float32"):
        fo.write(ducking.apply(blok, pos, 44100, curve))
        pos += len(blok)
vorm.unlink()
lv, lm = vc.measure(stem), vc.measure(uit)
db = (lv["lufs"] - mix.music_below_voice_db) - lm["lufs"]
(v / "muziek-db.txt").write_text(f"{db:.2f}\n", encoding="utf-8")
for f in werk.glob("*"):
    f.unlink()
werk.rmdir()
print(f"muziek -> {uit} (seed {seed}); stem {lv['lufs']} LUFS, muziek {lm['lufs']} LUFS -> --muziek-db {db:.2f}")
