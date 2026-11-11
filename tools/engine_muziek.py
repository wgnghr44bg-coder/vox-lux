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
# Vaste muziek W3 uit audio_engine/B1.json via tools/b1.py (eigenaar 8 nov 2026: geen fouten in stem en geluid):
# 11 LUFS onder de stem ("muziek_onder"), elke video dezelfde akkoordenreeks ("muziek_seed" 1939), en de W3-klank
# "diep en donker-warm" ("muziek": instellingen bovenop de stijl "referentie").
sys.path.insert(0, str(HIER))
import b1
_j = b1.laad(m)
mix.music_below_voice_db = float(_j["muziek_onder"])
VAST_SEED = int(_j["muziek_seed"])
KLANK = _j["muziek"]
dur = sf.info(stem).duration + 60


def lus(bron, n0, n, X):
    """Stuk [n0, n0+n) van de bron eindeloos herhaald, elke naad X samples gelijk-vermogen overvloeid."""
    P = len(bron) - X
    p = np.arange(n0, n0 + n)
    k, o = p // P, p % P
    uit = bron[o].copy()
    naad = (k > 0) & (o < X)
    a = (o[naad] / X * np.pi / 2)[:, None]
    uit[naad] = bron[o[naad]] * np.sin(a) + bron[P + o[naad]] * np.cos(a)
    return uit


if _j.get("achtergrond"):
    # Vaste achtergrond van de eigenaar (11 nov 2026: open haard + B effect, 14 onder): alleen die geluiden, geen
    # ducking of filter, zoals de goedgekeurde proef. Ontbreekt een bestand, dan stoppen (niet stil W3 gebruiken).
    import librosa
    ag = _j["achtergrond"]
    lagen = []
    for l in ag["lagen"]:
        p = Path(ag["map"]).expanduser() / l["bestand"]
        if not p.exists():
            sys.exit(f"ACHTERGROND ONTBREEKT: {p}")
        y, _ = librosa.load(p, sr=44100, mono=False)
        y = np.atleast_2d(y).T if y.ndim == 1 else y.T
        y = np.repeat(y, 2, axis=1) if y.shape[1] == 1 else y[:, :2]
        # -12 dB vooraf: de open haard heeft eigen harde knapjes (piek 0,73), +9 dB zou ze afknippen; muziek-db zet
        # het volume daarna toch goed
        lagen.append((y.astype(np.float32) * 10 ** ((float(l["db"]) - 12) / 20), int(float(l["overvloei"]) * 44100)))
    uit = v / "muziek432.wav"
    N, B = int(dur * 44100), 44100 * 30
    fi, fo = 3 * 44100, 6 * 44100
    with sf.SoundFile(uit, "w", 44100, 2, subtype="PCM_24") as f:
        for n0 in range(0, N, B):
            n = min(B, N - n0)
            blok = sum(lus(y, n0, n, X) for y, X in lagen)
            p = np.arange(n0, n0 + n)
            blok *= np.clip(p / fi, 0, 1)[:, None] * np.clip((N - p) / fo, 0, 1)[:, None]
            f.write(np.clip(blok, -1, 1))
    lv, lm = vc.measure(stem), vc.measure(uit)
    db = (lv["lufs"] - mix.music_below_voice_db) - lm["lufs"]
    (v / "muziek-db.txt").write_text(f"{db:.2f}\n", encoding="utf-8")
    print(f"achtergrond -> {uit} ({', '.join(l['bestand'] for l in ag['lagen'])}); stem {lv['lufs']} LUFS, "
          f"achtergrond {lm['lufs']} LUFS -> --muziek-db {db:.2f}")
    sys.exit(0)
seed =VAST_SEED if VAST_SEED is not None else zlib.crc32(m.name.encode()) % 1000              # elke video eigen akkoordenreeks, wel steeds dezelfde
werk = v / "engine-muziek"
generate(preset("referentie", duration=dur, seed=seed, **KLANK), werk, stems=False,
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
