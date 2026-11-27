"""Stem What If GTA 6 Was Real Life (27 nov), zelfde stemmen als Swapped Lives en $1 Million. Iedereen eigen stem.
Gebruik: <omnivoice-venv>/python stem.py [script-bestand]  -> stem.wav + zinnen.json [start, eind, tekst, scene, spreker]"""
import json, re, sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, b1, torch
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig, VOICES
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
SCRIPT = H / (sys.argv[1] if len(sys.argv) > 1 else "script.txt")
ONTWERP = {"whatif-jongen": ("male", "teenager", "moderate pitch", "american accent"),
           "whatif-mama": ("female", "young adult", "moderate pitch", "american accent"),
           "whatif-baas": ("male", "middle-aged", "low pitch", "american accent"),
           "whatif-kassa": ("female", "young adult", "high pitch", "american accent"),       # 26 nov: kassière (eigenaar: meer eigen stemmen)
           "whatif-agent": ("male", "middle-aged", "moderate pitch", "american accent"),
           "whatif-piraat": ("male", "middle-aged", "low pitch", "british accent"),
           "whatif-mascotte": ("male", "young adult", "high pitch", "american accent"),
           "whatif-buur": ("male", "middle-aged", "high pitch", "american accent"),        # 27 nov: buurman Gary
           "whatif-zuster": ("female", "middle-aged", "moderate pitch", "american accent"), # 27 nov: respawn-zuster
           "whatif-ober": ("male", "young adult", "low pitch", "british accent"),           # 27 nov: deftige ober
           "whatif-radio": ("male", "young adult", "moderate pitch", "american accent"),
           "whatif-wasbeer": ("male", "young adult", "high pitch", "american accent")}   # 27 nov: wasbeer-explainer (proef)    # 27 nov: radioreclame
asr = None
for naam, (g, a, p, acc) in ONTWERP.items():
    if (VOICES / naam / "ref.wav").exists(): continue
    if asr is None:
        from transformers import pipeline
        asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
    for sd in (3, 4, 9, 17, 30):                     # ontwerp mislukt soms (onzin): controleren met Whisper
        ref = ov.design_voice(naam, g, a, p, acc, sd, ref_text="Okay, everybody, sit down please. We have a lot to do today.", speed=1.0)
        w, sr = sf.read(ref, dtype="float32")
        if "sit down" in asr({"raw": w, "sampling_rate": sr}, generate_kwargs={"language": "en"})["text"].lower(): print("stem", naam, "seed", sd); break
# stem van het LIJF
STEM = {"N": ("eigen-stem-swan", 1.05), "YOU": ("whatif-zoon", 1.0), "DAD": ("whatif-papa", 1.0), "MOM": ("whatif-moeder2", 1.0),   # 23 nov: iedereen EIGEN stem (optie A)
        "SIS": ("whatif-meisje", 1.0), "TEACH": ("whatif-juf", 1.0), "BOSS": ("whatif-baas", 1.0),
        "KASSA": ("whatif-kassa", 1.0), "AGENT": ("whatif-agent", 1.0), "PIRAAT": ("whatif-piraat", 1.0), "MASCOTTE": ("whatif-mascotte", 1.0),
        "BUUR": ("whatif-buur", 1.0), "ZUSTER": ("whatif-zuster", 1.0), "OBER": ("whatif-ober", 1.0), "RADIO": ("whatif-radio", 1.12), "WASBEER": ("whatif-wasbeer", 1.05)}
regels, STILTE = [], {}                                  # "STILTE|2.0" in het script = echte stilte na de vorige regel (eigenaar 25 nov: krekels)
for r in SCRIPT.read_text(encoding="utf-8").splitlines():
    if not r.strip() or r.startswith("#"): continue
    if r.startswith("STILTE|"): STILTE[len(regels) - 1] = float(r.split("|")[1]); continue
    regels.append(r.rstrip(chr(10)).split("|", 2))
import os
OPNIEUW = {int(x) for x in os.environ.get("OPNIEUW", "").split(",") if x.strip()}   # zinnen met een andere seed (Whisper hoorde iets anders)
MAXWPM, ZINPAUZE = 195, 0.32                              # per zin; pauze tussen zinnen binnen één regel
clips = []
for k, (sp, sc, z) in enumerate(regels):
    v, spd = STEM[sp]
    cfg = VoiceConfig(voice=v, speed=spd, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    # 25 nov (eigenaar: "It's 6 a.m. Your bank app gaat te snel in een zin, klinkt heel raar"): elke ZIN los inspreken en er een
    # echte pauze tussen zetten; per zin niet sneller dan MAXWPM (anders andere seed, en anders de rustigste poging).
    zinnen_ = [z] if sp != "N" else [x for x in re.split(r'(?<=[.!?])\s+(?=["A-Z0-9])', z) if x.strip()]                  # personages (roepen/uitroepen) in één adem, verteller per zin
    stukken = []
    for q, zz in enumerate(zinnen_):
        poging = []
        for p in range(6):
            c = edge_fade(trim(ov.speak([zz], cfg, seed=100 * k + 10 * q + p + (7 if k in OPNIEUW else 0))[0], SR), SR); d = len(c) / SR
            wpm = len(zz.split()) / (d / 60) if d > 0 else 999; poging.append((wpm if d >= 0.3 else 999, c))
            if d >= 0.3 and (wpm <= MAXWPM or len(zz.split()) < 4): break
        best = min(poging, key=lambda x: x[0])
        if best[0] > MAXWPM + 15 and len(zz.split()) >= 6:    # nog steeds te snel (tempowachter): rustiger inspreken
            for f_ in (0.88, 0.78):
                cfg2 = VoiceConfig(voice=v, speed=spd * f_, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
                for p in range(4):
                    c = edge_fade(trim(ov.speak([zz], cfg2, seed=100 * k + 10 * q + 50 + p)[0], SR), SR); d = len(c) / SR
                    if d >= 0.3: poging.append((len(zz.split()) / (d / 60), c))
                    if d >= 0.3 and len(zz.split()) / (d / 60) <= MAXWPM + 10: break
                if min(x[0] for x in poging) <= MAXWPM + 15: break
            best = min(poging, key=lambda x: x[0])
        stukken.append(best[1])
    c = stukken[0]
    for st in stukken[1:]: c = np.concatenate([c, np.zeros(int((ZINPAUZE if sp == "N" else ZINPAUZE * 0.75) * SR), np.float32), st])
    d = len(c) / SR; clips.append(c); print(k, sp, round(d, 2), f"{len(z.split()) / (d / 60):.0f} w/min", flush=True)
t = 0.3; delen = [np.zeros(int(t * SR), np.float32)]; tijden = []
for k, ((sp, sc, z), c) in enumerate(zip(regels, clips)):
    tijden.append([round(t, 3), round(t + len(c) / SR, 3), z, sc, sp])
    p = 0.35 if k + 1 < len(regels) and regels[k + 1][0] != sp else 0.45
    if z.endswith("?") and sp == "N": p = 0.8
    if k + 1 == len(regels): p = 1.2
    p = max(p, STILTE.get(k, 0))
    delen += [c, np.zeros(int(p * SR), np.float32)]; t += len(c) / SR + p
sf.write(H / "stem.wav", np.concatenate(delen), SR)
(H / "zinnen.json").write_text(json.dumps(tijden, indent=0, ensure_ascii=False), encoding="utf-8")
print("KLAAR", round(t, 1), "s")
