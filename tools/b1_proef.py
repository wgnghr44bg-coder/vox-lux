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
# --tekst <bestand>: eigen tekst (alinea's gescheiden door een lege regel), bv. om een nieuwe schrijfstijl te horen
ALINEA_EIND = set()
if "--tekst" in sys.argv:
    import re
    TEKST = []
    for alinea in re.split(r"\n\s*\n", Path(sys.argv[sys.argv.index("--tekst") + 1]).read_text(encoding="utf-8")):
        zinnen = [z.strip() for z in re.split(r"(?<=[.!?])\s+", " ".join(alinea.split())) if z.strip()]
        TEKST += zinnen
        if zinnen:
            ALINEA_EIND.add(len(TEKST) - 1)
# --komma-pauze 0.3: korte adempauze bij komma's (eigenaar 11 nov: grote kanalen ademen vaker kort midden in de zin).
# De zin wordt bij de komma's in stukjes gesplitst (stukjes van minstens 3 woorden, komma blijft staan) en de stukjes
# krijgen een korte stilte ertussen. --zin-pauze <s>: andere stilte na een zin (standaard 0,7 × B1-pauze).
KOMMA_NA = set()
if "--komma-pauze" in sys.argv:
    import re
    nieuw, alinea_nieuw = [], set()
    for i, z in enumerate(TEKST):
        stukken = []
        for s in re.split(r"(?<=,)\s+", z):
            if stukken and (len(s.split()) < 3 or len(stukken[-1].split()) < 3):
                stukken[-1] += " " + s
            else:
                stukken.append(s)
        for k, s in enumerate(stukken):
            nieuw.append(s)
            if k < len(stukken) - 1:
                KOMMA_NA.add(len(nieuw) - 1)
        if i in ALINEA_EIND:
            alinea_nieuw.add(len(nieuw) - 1)
    TEKST, ALINEA_EIND = nieuw, alinea_nieuw
inst = b1.standaard()
if "--pauze" in sys.argv:                                   # alleen voor proeven: andere pauzefactor (zelfde stem)
    inst["pauze"] = float(sys.argv[sys.argv.index("--pauze") + 1])
V = inst.get("verteller")
if V and "--zonder-verteller" not in sys.argv and "--verteller" not in sys.argv:   # standaard sinds 11 nov: verteller F
    sys.argv += ["--rustpunten", "--verteller", "--traag-speed", str(V["slot_speed"]), "--zin-pauze", str(V["zin_pauze"]),
                 "--alinea-pauze", str(V["alinea_pauze"]), "--vraag-pauze", str(V["vraag_pauze"])]
if "--speed" in sys.argv:                                   # alleen voor proeven: andere spreeksnelheid van OmniVoice zelf
    inst["speed"] = float(sys.argv[sys.argv.index("--speed") + 1])
SR = ov.SR
cfg = VoiceConfig(voice=inst["engine_voice"], speed=inst["speed"], seed=inst["seed"], num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
clips = []
for i in range(0, len(TEKST), 4):                           # groepjes van 4, zoals tools/engine_stem.py
    clips += [edge_fade(trim(w, SR), SR) for w in ov.speak(TEKST[i:i + 4], cfg, seed=cfg.seed + i)]
# --rustpunten (eigenaar 11 nov: "het mag wel tussendoor iets langzamer"): de laatste 2 zinnen van elke alinea (de stille
# slotgedachte) iets trager ingesproken door OmniVoice zelf (speed 0.48 i.p.v. 0.54, geen nabewerking), en langere stilte
# na een vraag (1,6 s) en na een alinea (2,2 s).
TRAAG = set()
if "--rustpunten" in sys.argv:
    vorige = -1
    for e in sorted(ALINEA_EIND):
        TRAAG |= {k for k in (e - 1, e) if k > vorige + 1 and k not in KOMMA_NA}
        vorige = e
    cfg_traag = VoiceConfig(voice=inst["engine_voice"], speed=float(sys.argv[sys.argv.index("--traag-speed") + 1]) if "--traag-speed" in sys.argv else 0.48, seed=inst["seed"], num_step=inst["model"]["num_step"],
                            guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    for i in sorted(TRAAG):
        clips[i] = edge_fade(trim(ov.speak([TEKST[i]], cfg_traag, seed=cfg.seed + 300 + i)[0], SR), SR)
    print(f"rustpunten: {len(TRAAG)} zinnen trager", flush=True)
# --verteller (eigenaar 11 nov: "de stem nog iets meer variaties geven als een slaapverteller"): niet elke zin even snel.
# Korte beeldzinnen ("The town below.") trager, vragen iets trager, lange beschrijvende zinnen vloeien iets door; de
# slotgedachte van een alinea (zie --rustpunten) ook iets zachter. Alles door OmniVoice zelf (speed), geen nabewerking.
SPEED, ZACHT = {}, set()
if "--verteller" in sys.argv:
    base = float(inst["speed"])
    for i, z in enumerate(TEKST):
        w = len(z.split())
        if i in TRAAG:
            ZACHT.add(i)
        elif z.rstrip().endswith("?"):
            SPEED[i] = round(base - 0.03, 2)
        elif w <= 5:
            SPEED[i] = round(base - 0.06, 2)
        elif w >= 15:
            SPEED[i] = round(base + 0.01, 2)
    for sp in sorted(set(SPEED.values())):
        c2 = VoiceConfig(voice=inst["engine_voice"], speed=sp, seed=inst["seed"], num_step=inst["model"]["num_step"],
                         guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
        idx = [i for i, v in SPEED.items() if v == sp]
        for b in range(0, len(idx), 4):
            for i, wav in zip(idx[b:b + 4], ov.speak([TEKST[i] for i in idx[b:b + 4]], c2, seed=cfg.seed + 700 + b)):
                clips[i] = edge_fade(trim(wav, SR), SR)
    for i in ZACHT:
        clips[i] = clips[i] * 0.84                           # ± 1,5 dB zachter
    print(f"verteller: {len(SPEED)} zinnen ander tempo, {len(ZACHT)} slotzinnen zachter", flush=True)
# afgekapte zinnen los opnieuw (zoals tools/engine_stem.py): korter dan 0,25 s of sneller dan 250 woorden/min
for i, z in enumerate(TEKST):
    for poging in range(1, 8):
        d, w = len(clips[i]) / SR, len(z.split())
        if d >= 0.25 and w / (d / 60) <= (250 if w >= 8 else 320):
            break
        clips[i] = edge_fade(trim(ov.speak([z], cfg_traag if i in TRAAG else cfg, seed=cfg.seed + 1000 * poging + i)[0], SR), SR)
        print(f"zin {i + 1} was afgekapt, opnieuw ({poging}x)", flush=True)
zp = float(sys.argv[sys.argv.index("--zin-pauze") + 1]) if "--zin-pauze" in sys.argv else 0.7 * float(inst["pauze"])
stil = np.zeros(int(zp * SR), np.float32)                   # pauze na een zin
stil_alinea = np.zeros(int(1.1 * float(inst["pauze"]) * SR), np.float32)
stil_komma = np.zeros(int(float(sys.argv[sys.argv.index("--komma-pauze") + 1]) * SR), np.float32) if KOMMA_NA else None
delen = [np.zeros(int(0.5 * SR), np.float32)]
if "--rustpunten" in sys.argv:
    stil_alinea = np.zeros(int((float(sys.argv[sys.argv.index("--alinea-pauze") + 1]) if "--alinea-pauze" in sys.argv else 2.2) * SR), np.float32)
stil_vraag = np.zeros(int((float(sys.argv[sys.argv.index("--vraag-pauze") + 1]) if "--vraag-pauze" in sys.argv else 1.6) * SR), np.float32)
for i, c in enumerate(clips):
    na = stil_komma if i in KOMMA_NA else stil_alinea if i in ALINEA_EIND else \
        stil_vraag if "--rustpunten" in sys.argv and TEKST[i].rstrip().endswith("?") else stil
    if "--verteller" in sys.argv and na is stil:             # pauze ademt mee met de zin: kort beeld = langer stil
        w = len(TEKST[i].split())
        na = np.zeros(int(zp * (1.3 if w <= 5 else 0.85 + 0.3 * min(1.0, w / 18)) * SR), np.float32)
    delen += [c, na]
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
