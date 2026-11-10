"""Proef van 1 minuut met de vaste B1-stem en W3-muziek (eigenaar 10 nov 2026: "of hij hetzelfde doet als hier").
Altijd dezelfde tekst, dezelfde instellingen uit audio_engine/B1.json, geen keuzes. Twee pc's (of accounts) met dezelfde
repo en dezelfde programmaversies maken zo hetzelfde geluid; vergelijk daarna met tools/b1_check.py (B1 GOED).

  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/b1_proef.py <uit.mp3>
"""
import subprocess, sys, tempfile
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER.parent / "audio_engine"))
import numpy as np, soundfile as sf
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
from effects import volume_control as vc
from mixer import ducking
from mixer.voice_music_mixer import MixConfig, music_shaping
from music.composition_engine import preset
from music.music_studio import generate

TEKST = [
    "Imagine a small wooden box in the corner of a front room.",
    "Its dial glows a soft yellow.",
    "Outside, the evening is quiet, and the street lamps are just coming on.",
    "A family sits close together, waiting for a voice they know.",
    "The kettle has been filled, and the cups are set out on the table.",
    "Nobody speaks very much.",
    "Then the voice comes, calm and slow, and the room grows very still.",
    "In the morning, life will carry on, as it always does.",
    "But tonight, for a little while, everyone listens together.",
    "The fire settles in the grate, and the clock on the shelf ticks softly.",
    "One by one, the lamps along the street go out.",
    "And the house, at last, falls asleep.",
]

uit = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("b1-proef.mp3")
inst = b1.standaard()
SR = ov.SR
cfg = VoiceConfig(voice=inst["engine_voice"], speed=inst["speed"], seed=inst["seed"], num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
clips = []
for i in range(0, len(TEKST), 4):                           # groepjes van 4, zoals tools/engine_stem.py
    clips += [edge_fade(trim(w, SR), SR) for w in ov.speak(TEKST[i:i + 4], cfg, seed=cfg.seed + i)]
stil = np.zeros(int(0.7 * float(inst["pauze"]) * SR), np.float32)   # pauze na een zin × B1-pauzefactor
delen = [np.zeros(int(0.5 * SR), np.float32)]
for c in clips:
    delen += [c, stil]
delen.append(np.zeros(2 * SR, np.float32))

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    sf.write(tmp / "ruw.wav", np.concatenate(delen), SR)
    st = tmp / "stem.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "ruw.wav"), "-af", inst["klank"], "-ar", "44100", "-ac", "1", str(st)], check=True)
    duur = sf.info(st).duration
    mix = MixConfig()
    mix.music_below_voice_db = float(inst["muziek_onder"])
    generate(preset("referentie", duration=sf.info(st).duration + 1, seed=int(inst["muziek_seed"]), **inst["muziek"]),
             tmp / "m", stems=False, progress=lambda *a: None)
    vorm = tmp / "vorm.wav"
    vc.ffmpeg(["-i", str(tmp / "m/music.wav"), "-af", music_shaping(mix), "-ar", "44100", "-c:a", "pcm_f32le", str(vorm)])
    curve = ducking.gain_curve(st, mix.duck_amount_db, mix.duck_attack, mix.duck_release)
    gm = tmp / "gm.wav"
    with sf.SoundFile(vorm) as fi, sf.SoundFile(gm, "w", 44100, 2, subtype="PCM_24") as fo:
        pos = 0
        for blok in fi.blocks(blocksize=44100 * 30, always_2d=True, dtype="float32"):
            fo.write(ducking.apply(blok, pos, 44100, curve))
            pos += len(blok)
    db = (vc.measure(st)["lufs"] - mix.music_below_voice_db) - vc.measure(gm)["lufs"]
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(st), "-i", str(gm), "-filter_complex",
                    f"[0:a]aformat=channel_layouts=stereo[s];[1:a]volume={db:.2f}dB[m];"
                    f"[s][m]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1:LRA=11[a]",
                    "-map", "[a]", "-c:a", "libmp3lame", "-b:a", "128k", str(uit)], check=True)
print(f"klaar: {uit} ({duur:.0f} s), stem {inst['engine_voice']} speed {inst['speed']} seed {inst['seed']}, "
      f"muziek {inst['muziek_onder']} LUFS onder, seed {inst['muziek_seed']}")
