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
import b1                                                  # vaste B1-instellingen (audio_engine/B1.json, eigenaar 8 nov 2026)
inst = b1.laad(m)
cfg = VoiceConfig(voice=inst["engine_voice"], speed=inst["speed"], seed=inst["seed"],      # alles vast uit B1.json
                  num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"],
                  denoise=inst["model"]["denoise"])
xv.PAUSE_MS, xv.LONG_PAUSE_MS, xv.SENTENCE_PAUSE_MS = 1500, 2800, 1100
pieces = xv.split_script((m / "script-cues.txt").read_text(encoding="utf-8"))
# "pauze" in stem.json (eigenaar 7 nov 2026, proef B1: pauzes 40% langer): de stilte die na add_pauses --kort
# overblijft (alles boven 0,4 s) wordt zoveel keer langer.
f = float(inst.get("pauze", 1.0))
ALINEA = {i for i, p in enumerate(pieces) if p.silence_after_ms >= xv.PAUSE_MS}   # na [pause]/[long-pause]: einde alinea
LANG = {i for i, p in enumerate(pieces) if p.silence_after_ms >= xv.LONG_PAUSE_MS}
pieces = [xv.Piece(" ".join(xv.TAG_RE.sub("", p.text).split()),
                   round((p.silence_after_ms - 400) * f + 400) if p.silence_after_ms > 400 else p.silence_after_ms, p.cue)
          for p in pieces]
# "max_pauze" (eigenaar 11 nov 2026, Gettysburg-proef: 3,5 s stilte bij een nieuw stuk "best lang stil"): na
# add_pauses --kort (0,4 s eraf) nergens langer stil dan dit
if inst.get("max_pauze"):
    grens = round(float(inst["max_pauze"]) * 1000 + 400)
    pieces = [xv.Piece(p.text, min(p.silence_after_ms, grens), p.cue) for p in pieces]

# Verteller F (eigenaar 11 nov 2026: "F zoals nu kan dat"; B1.json "verteller"): niet elke zin even snel, alles door
# OmniVoice zelf. Slotgedachte van een alinea (laatste 2 zinnen, niet de eerste) trager en zachter; vragen iets trager;
# korte beeldzinnen ("The town below.") trager; lange zinnen iets vloeiender. Pauzes: na een zin 1,15 s (korte zin
# langer, lange zin iets korter), na een vraag 1,8 s, na een alinea 2,5 s. Gelijk aan tools/b1_proef.py --verteller.
V = inst.get("verteller")
SPEED, SLOT = {}, set()
if V:
    base = float(inst["speed"])
    vorige = -1
    for e in sorted(ALINEA | {len(pieces) - 1}):
        SLOT |= {k for k in range(e - int(V["slot_zinnen"]) + 1, e + 1) if k > vorige + 1}
        vorige = e
    for i, p in enumerate(pieces):
        w = len(p.text.split())
        if i in SLOT:
            SPEED[i] = float(V["slot_speed"])
        elif p.text.rstrip().endswith("?"):
            SPEED[i] = round(base + float(V["vraag_delta"]), 2)
        elif w <= int(V["kort_woorden"]):
            SPEED[i] = round(base + float(V["kort_delta"]), 2)
        elif w >= int(V["lang_woorden"]):
            SPEED[i] = round(base + float(V["lang_delta"]), 2)
        # pauze zoals die na add_pauses --kort (0,4 s eraf) moet overblijven
        if i in ALINEA:
            eind = max(float(V["alinea_pauze"]), (p.silence_after_ms - 400) / 1000 if i in LANG else 0)
        elif p.text.rstrip().endswith("?"):
            eind = float(V["vraag_pauze"])
        else:
            eind = float(V["zin_pauze"]) * (float(V["kort_pauze_factor"]) if w <= int(V["kort_woorden"]) else 0.85 + 0.3 * min(1.0, w / 18))
        if i < len(pieces) - 1:
            p.silence_after_ms = round(eind * 1000 + 400)
print(f"{len(pieces)} zinnen, stem {cfg.voice}, speed {cfg.speed}" + (f", verteller: {len(SPEED)} zinnen eigen tempo, "
      f"{len(SLOT)} slotzinnen zachter" if V else ""), flush=True)


def cfg_voor(i):
    if i not in SPEED:
        return cfg
    return VoiceConfig(voice=cfg.voice, speed=SPEED[i], seed=cfg.seed, num_step=cfg.num_step,
                       guidance_scale=cfg.guidance_scale, denoise=cfg.denoise)

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

# --opnieuw 8,23,42 (nummers uit check_stem_tekst.py): die zinnen los opnieuw inspreken (7 nov 2026: OmniVoice kapt in een
# groepje van 4 soms een zin af, bv. 15 woorden in 0,9 s; herstel_zinnen.py kan dat niet, want de goede zin past niet in het gat)
if "--opnieuw" in sys.argv:
    for n in sys.argv[sys.argv.index("--opnieuw") + 1].split(","):
        clips[int(n) - 1] = None


def te_kort(i):
    """Afgekapt of leeg: korter dan 0,25 s, of meer dan 250 woorden/min zonder pauzes (normaal ± 150-210)."""
    d, w = len(clips[i]) / SR, len(pieces[i].text.split())
    return d < 0.25 or w / (d / 60) > (250 if w >= 8 else 320)    # korte zinnen klinken vanzelf iets sneller


nieuw_of_opnieuw = {i for i, c in enumerate(clips) if c is None}
opnieuw = {i for i, c in enumerate(clips) if c is None and "--opnieuw" in sys.argv}
nieuw = [i for i, c in enumerate(clips) if c is None and i not in opnieuw]
for sp in sorted({cfg_voor(i).speed for i in nieuw}):        # per tempo in groepjes van 4 (verteller F)
    groep = [i for i in nieuw if cfg_voor(i).speed == sp]
    c = cfg_voor(groep[0])
    for b in range(0, len(groep), 4):
        idx = groep[b:b + 4]
        for i, wav in zip(idx, ov.speak([pieces[i].text for i in idx], c, seed=cfg.seed + b + (0 if sp == cfg.speed else 700))):
            clips[i] = edge_fade(trim(wav, SR), SR)
        print(f"klaar {b + len(idx)}/{len(groep)} (speed {sp})", flush=True)
extra = int(sys.argv[sys.argv.index("--seed-extra") + 1]) if "--seed-extra" in sys.argv else 0   # andere poging
for i in sorted(opnieuw):
    clips[i] = edge_fade(trim(ov.speak([pieces[i].text], cfg_voor(i), seed=cfg.seed + 500 + i + extra)[0], SR), SR)
for i in range(len(pieces)):                               # afgekapte of lege zinnen: los opnieuw, andere seed
    if not te_kort(i):
        continue
    poging = 0
    nieuw_of_opnieuw.add(i)                                # opnieuw ingesproken: krijgt ook het tempo
    while te_kort(i) and poging < 10:
        poging += 1
        clips[i] = edge_fade(trim(ov.speak([pieces[i].text], cfg_voor(i), seed=cfg.seed + 1000 * poging + i)[0], SR), SR)
    print(f"zin {i + 1} was afgekapt, los opnieuw ({poging}x)", flush=True)
if V:                                                      # slotgedachte zachter (alleen nieuw ingesproken zinnen)
    for i in SLOT & nieuw_of_opnieuw:
        clips[i] = clips[i] * float(V["slot_volume"])

# "tempo" in stem.json (eigenaar 7 nov 2026: "mag hij iets rustiger vertellen"): nieuw ingesproken zinnen worden met
# rubberband trager gemaakt (klank blijft gelijk). Hergebruikte zinnen uit voice.mp3 zijn dat al, behalve met
# --tempo-alles (eenmalig, als het tempo voor een bestaande stem verandert).
tempo = float(inst.get("tempo", 1.0))


def rek(wav):
    r = subprocess.run(["ffmpeg", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "1", "-i", "-",
                        "-af", f"rubberband=tempo={tempo}:pitchq=quality:window=long", "-f", "f32le", "-"],
                       input=wav.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return edge_fade(np.frombuffer(r, np.float32).copy(), SR)


if tempo != 1.0:
    hergebruikt = set() if "--tempo-alles" in sys.argv else {i for i in range(len(pieces)) if i not in nieuw_of_opnieuw}
    for i in range(len(pieces)):
        if i not in hergebruikt:
            clips[i] = rek(clips[i])
    print(f"tempo {tempo}: {len(pieces) - len(hergebruikt)} zinnen trager gemaakt", flush=True)

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
