"""Proef met een ANDERE stem, verteld zoals verteller F (eigenaar 11 nov 2026). Alleen een proef: B1.json en de
videostraat blijven zoals ze zijn. Zelfde werkwijze als tools/b1_proef.py --tekst (verteller F + W3-muziek), maar de stem
komt uit een eigen map met ref.wav + voice.json (ref_text), die ook buiten de repo mag staan (bv. de eigen stem van de
eigenaar, die niet op GitHub hoort). Alleen stemmen waar de eigenaar de rechten op heeft of die zelf ontworpen zijn.

Tempo: verteller F werkt met de spreeksnelheid van OmniVoice zelf. B1 vertelt op speed 0.50; de andere stem op zijn eigen
normale speed (--speed, standaard 1.0). De F-verschillen worden naar verhouding omgerekend (slotzinnen 0.45/0.50 = x0.9,
vraag -0.03/0.50 = -6 %, kort -12 %, lang +2 %). Pauzes, zachtere slotzinnen, muziek en eindvolume zijn precies als F.
--vast-tempo: elke zin op de normale speed van de stem (geen tempo per zin), F alleen met pauzes en zachtere slotzinnen.
--zonder-verteller: helemaal zonder F: normale speed, geen zachtere slotzinnen, gewone pauzes (0,7 / 1,1 x B1-pauze).

  C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/proef_andere_stem.py <uit.mp3> --stem-map <map> \
      --tekst stories/_toon-proef/gettysburg-begin-en-hoofdstuk1.txt [--speed 1.0] [--seed 7] [--vast-tempo | --zonder-verteller]
"""
import json, re, subprocess, sys, tempfile
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


def arg(naam, standaard=None):
    return sys.argv[sys.argv.index(naam) + 1] if naam in sys.argv else standaard


uit = Path(sys.argv[1])
stem_map = Path(arg("--stem-map"))
meta = json.loads((stem_map / "voice.json").read_text(encoding="utf-8"))
naam = "proef-" + stem_map.name
# clone-prompt rechtstreeks uit de map, zodat de stem niet in audio_engine/voices hoeft te staan
ov._prompts[naam] = ov.model().create_voice_clone_prompt(ref_audio=str(stem_map / "ref.wav"), ref_text=meta["ref_text"])

TEKST, ALINEA_EIND = [], set()
for alinea in re.split(r"\n\s*\n", Path(arg("--tekst")).read_text(encoding="utf-8")):
    zinnen = [z.strip() for z in re.split(r"(?<=[.!?])\s+", " ".join(alinea.split())) if z.strip()]
    TEKST += zinnen
    if zinnen:
        ALINEA_EIND.add(len(TEKST) - 1)

inst = b1.standaard()
V = inst["verteller"]
B1_SPEED = float(inst["speed"])
base = float(arg("--speed", 1.0))
seed = int(arg("--seed", inst["seed"]))
r = base / B1_SPEED                                          # omrekenen van B1-tempo naar het tempo van deze stem
SR = ov.SR


def cfg(sp):
    return VoiceConfig(voice=naam, speed=round(sp, 3), seed=seed, num_step=inst["model"]["num_step"],
                       guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])


# tempo per zin zoals verteller F: slotzinnen van een alinea trager (en zachter), vragen en korte zinnen iets trager,
# lange zinnen vloeien iets door
TRAAG, vorige = set(), -1
for e in sorted(ALINEA_EIND):
    TRAAG |= {k for k in range(e - int(V["slot_zinnen"]) + 1, e + 1) if k > vorige + 1}   # zoals b1_proef.py
    vorige = e
SPEED = {}
for i, z in enumerate(TEKST):
    w = len(z.split())
    if i in TRAAG:
        SPEED[i] = float(V["slot_speed"]) * r
    elif z.rstrip().endswith("?"):
        SPEED[i] = base + float(V["vraag_delta"]) * r
    elif w <= int(V["kort_woorden"]):
        SPEED[i] = base + float(V["kort_delta"]) * r
    elif w >= int(V["lang_woorden"]):
        SPEED[i] = base + float(V["lang_delta"]) * r
    else:
        SPEED[i] = base
ZONDER = "--zonder-verteller" in sys.argv                    # eigenaar 11 nov: "laat verteller F weg, pak de normale stem"
if ZONDER:
    TRAAG = set()
if ZONDER or "--vast-tempo" in sys.argv:                     # elke zin op de normale snelheid van de stem
    SPEED = {i: base for i in SPEED}
SPEED = {i: round(s, 3) for i, s in SPEED.items()}

clips = [None] * len(TEKST)
for sp in sorted(set(SPEED.values())):
    idx = [i for i, v in SPEED.items() if v == sp]
    for b in range(0, len(idx), 4):                          # groepjes van 4, zoals tools/engine_stem.py
        for i, wav in zip(idx[b:b + 4], ov.speak([TEKST[i] for i in idx[b:b + 4]], cfg(sp), seed=seed + 700 + b)):
            clips[i] = edge_fade(trim(wav, SR), SR)
# afgekapte zinnen los opnieuw (zoals tools/engine_stem.py): korter dan 0,25 s of veel te snel
for i, z in enumerate(TEKST):
    for poging in range(1, 8):
        d, w = len(clips[i]) / SR, len(z.split())
        if d >= 0.25 and w / (d / 60) <= (250 if w >= 8 else 320):
            break
        clips[i] = edge_fade(trim(ov.speak([z], cfg(SPEED[i]), seed=seed + 1000 * poging + i)[0], SR), SR)
        print(f"zin {i + 1} was afgekapt, opnieuw ({poging}x)", flush=True)
for i in TRAAG:
    clips[i] = clips[i] * float(V["slot_volume"])            # ± 1,5 dB zachter
print(f"verteller: {sum(1 for i, s in SPEED.items() if s != base)} zinnen ander tempo, {len(TRAAG)} slotzinnen zachter",
      flush=True)

zp = float(V["zin_pauze"])
delen = [np.zeros(int(0.5 * SR), np.float32)]
for i, c in enumerate(clips):
    w = len(TEKST[i].split())
    if ZONDER:                                               # gewone pauzes zoals b1_proef.py --zonder-verteller
        p = 1.1 * float(inst["pauze"]) if i in ALINEA_EIND else 0.7 * float(inst["pauze"])
    elif i in ALINEA_EIND:
        p = float(V["alinea_pauze"])
    elif TEKST[i].rstrip().endswith("?"):
        p = float(V["vraag_pauze"])
    else:                                                    # pauze ademt mee met de zin: kort beeld = langer stil
        p = zp * (float(V["kort_pauze_factor"]) if w <= int(V["kort_woorden"]) else 0.85 + 0.3 * min(1.0, w / 18))
    delen += [c, np.zeros(int(p * SR), np.float32)]
delen.append(np.zeros(2 * SR, np.float32))

with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    sf.write(tmp / "ruw.wav", np.concatenate(delen), SR)
    st = tmp / "stem.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(tmp / "ruw.wav"), "-af", inst["klank"], "-ar", "44100", "-ac", "1", str(st)], check=True)
    duur = sf.info(st).duration
    mix = MixConfig()
    mix.music_below_voice_db = float(inst["muziek_onder"])
    generate(preset("referentie", duration=duur + 1, seed=int(inst["muziek_seed"]), **inst["muziek"]),
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
woorden = sum(len(z.split()) for z in TEKST)
print(f"klaar: {uit} ({duur:.0f} s, {woorden / (duur / 60):.0f} woorden/min), stem {stem_map.name} speed {base} seed {seed}, "
      f"muziek {inst['muziek_onder']} LUFS onder, seed {inst['muziek_seed']}")
