"""Voice-over voor een bodycam-video met de eigen stem (OmniVoice, lokaal, gratis).

Elke alinea in script.txt (zonder '#'- en '[BEELD'-regels) wordt een los blok: <map>/stem/blok01.wav ...
plus stem/blokken.json (tekst + duur), zodat de montage elk blok op het juiste beeld kan leggen.
Zelfde stem en klank als B1 (audio_engine/B1.json), maar snelheid 1.0 en korte pauzes (geen slaaptempo),
zonder muziek of haard eronder.

  C:/Users/rane/omnivoice-venv/Scripts/python.exe kanalen/bodycam/maak_voiceover.py kanalen/bodycam/videos/<map> [--speed 1.0] [--pauze 0.45] [--stem-map <map>] [--alleen 2,4 --seed-extra 1]
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
# Uitspraak: alleen de tekst voor de stem wordt aangepast (script.txt en ondertitels blijven gewoon).
# Aanvullen in kanalen/bodycam/uitspraak.json, gecontroleerd met Whisper.
UITSPRAAK = json.loads((Path(__file__).parent / "uitspraak.json").read_text(encoding="utf-8"))


def voor_stem(z):
    for woord, klank in UITSPRAAK.items():
        z = re.sub(r"(?<![A-Za-z])" + re.escape(woord) + r"(?![A-Za-z])", klank, z)
    return z


# --alleen 2,4 : alleen deze blokken opnieuw (andere seed met --seed-extra n), de rest blijft staan
ALLEEN = {int(x) for x in sys.argv[sys.argv.index("--alleen") + 1].split(",")} if "--alleen" in sys.argv else None
PAUZE = float(sys.argv[sys.argv.index("--pauze") + 1]) if "--pauze" in sys.argv else 0.45  # s tussen zinnen
EXTRA = int(sys.argv[sys.argv.index("--seed-extra") + 1]) if "--seed-extra" in sys.argv else 0

# Elke zin wordt meteen met Whisper nagelopen (eigenaar 17 nov: ingeslikte woorden, "Sierra Faboon"): pas als de stem
# precies de zin zegt, wordt hij gebruikt. Getallen tellen niet mee (Whisper schrijft "24th" voor "twenty-fourth").
import difflib, librosa, torch
from transformers import pipeline
ASR = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo",
               device="cuda:0" if torch.cuda.is_available() else "cpu",
               torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32)
GETAL = {"one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "twenty",
         "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "first", "second",
         "third", "fourth", "fifth", "and", "a"}


def woorden(t):
    w = re.findall(r"[a-z']+", t.lower().replace("-", " "))
    return [x for x in w if x not in GETAL and not (len(x) <= 4 and re.fullmatch(r"(?:th|st|nd|rd|s)", x))]


def klopt(wav, zin):
    a = librosa.resample(np.asarray(wav, dtype="float32"), orig_sr=SR, target_sr=16000)
    a = np.concatenate([np.zeros(8000, np.float32), a, np.zeros(8000, np.float32)])
    gehoord = ASR({"raw": a, "sampling_rate": 16000}, generate_kwargs={"language": "en"})["text"].strip()
    w1, w2 = [x for x in woorden(zin) if not x.isdigit()], [x for x in woorden(gehoord) if not x.isdigit()]
    return difflib.SequenceMatcher(None, w1, w2).ratio(), gehoord


regels = [r for r in (map_ / "script.txt").read_text(encoding="utf-8").splitlines()
          if not r.startswith("#") and not r.startswith("[")]   # [BEELD …], [ORIGINEEL …] = aanwijzingen, niet uitspreken
alineas = [" ".join(a.split()) for a in re.split(r"\n\s*\n", "\n".join(regels)) if a.strip()]
uit = map_ / "stem"
uit.mkdir(exist_ok=True)
oud = {b["blok"]: b for b in json.loads((uit / "blokken.json").read_text(encoding="utf-8"))} if ALLEEN else {}
blokken = []
for n, alinea in enumerate(alineas, 1):
    if ALLEEN and n not in ALLEEN and n in oud:
        blokken.append(oud[n])
        continue
    zinnen = [z for z in re.split(r"(?<=[.!?])\s+", alinea) if z]
    clips = []
    for i, z in enumerate(zinnen):
        beste = None
        for poging in range(10):
            wav = edge_fade(trim(ov.speak([voor_stem(z)], cfg, seed=seed + 1000 * poging + 37 * n + i + 7919 * EXTRA)[0], SR), SR)
            d, w = len(wav) / SR, len(z.split())
            if d < 0.25 or w / (d / 60) > (250 if w >= 8 else 320):      # afgekapt of veel te snel
                print(f"blok {n} zin {i + 1} afgekapt, opnieuw", flush=True)
                continue
            score, gehoord = klopt(wav, z)                              # Whisper: zegt de stem precies de zin?
            if beste is None or score > beste[0]:
                beste = (score, wav, gehoord)
            if score >= 0.999:
                break
            print(f"blok {n} zin {i + 1} niet precies ({score:.2f}): \"{gehoord}\" -> opnieuw", flush=True)
        if beste is None:
            sys.exit(f"blok {n} zin {i + 1}: geen bruikbare opname")
        if beste[0] < 0.999:
            print(f"LET OP blok {n} zin {i + 1}: beste poging {beste[0]:.2f}: \"{beste[2]}\"", flush=True)
        clips += [beste[1], np.zeros(int(PAUZE * SR), np.float32)]
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
