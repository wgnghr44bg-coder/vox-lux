"""Stem What If You Invested $100 in NVIDIA? (26 nov), zelfde stemmen als Swapped Lives en $1 Million. Iedereen eigen stem.
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
ONTWERP = {"whatif-jensen": ("male", "young adult", "moderate pitch", "american accent"),          # NVIDIA-Short 26 nov: elke scène eigen stemmen
           "whatif-serveerster": ("female", "middle-aged", "moderate pitch", "american accent"),
           "whatif-curtis": ("male", "young adult", "low pitch", "american accent"),
           "whatif-sega": ("male", "elderly", "low pitch", "japanese accent"),
           "whatif-onderzoeker": ("female", "young adult", "high pitch", "american accent"),
           "whatif-jijoud": ("male", "middle-aged", "moderate pitch", "american accent")}
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
STEM = {"N": ("eigen-stem-swan", 1.05), "YOU": ("whatif-zoon", 1.0), "YOU2": ("whatif-jijoud", 1.0), "JENSEN": ("whatif-jensen", 1.0),
        "JENSEN2": ("whatif-jensen", 0.95), "SERVEERSTER": ("whatif-serveerster", 1.0), "CURTIS": ("whatif-curtis", 1.0),
        "SEGA": ("whatif-sega", 0.95), "ONDERZOEKER": ("whatif-onderzoeker", 1.0)}
regels, STILTE = [], {}                                  # "STILTE|2.0" in het script = echte stilte na de vorige regel (eigenaar 25 nov: krekels)
for r in SCRIPT.read_text(encoding="utf-8").splitlines():
    if not r.strip() or r.startswith("#"): continue
    if r.startswith("STILTE|"): STILTE[len(regels) - 1] = float(r.split("|")[1]); continue
    regels.append(r.rstrip(chr(10)).split("|", 2))
import os
OPNIEUW = {int(x) for x in os.environ.get("OPNIEUW", "").split(",") if x.strip()}   # zinnen met een andere seed (Whisper hoorde iets anders)
MAXWPM, ZINPAUZE = 195, 0.32                              # per zin; pauze tussen zinnen binnen één regel
# 26 nov (eigenaar: "de stemmen lijken veel op elkaar ... iedere personage een eigen stem die past"): bijfiguren via Kokoro (echte stemmen)
KOKORO = {"JENSEN": "am_michael", "JENSEN2": "am_michael", "SERVEERSTER": "af_sarah", "CURTIS": "am_puck", "SEGA": "am_santa",
          "ONDERZOEKER": "af_sky", "YOU2": "am_eric", "YOU": "am_liam"}
import subprocess, tempfile
_kk = Path(tempfile.mkdtemp()); _taken = [{"stem": KOKORO[sp], "tekst": z, "uit": str(_kk / f"{k}.wav"), "speed": 0.95 if sp == "JENSEN2" else 1.0}
                                         for k, (sp, sc, z) in enumerate(regels) if sp in KOKORO]
if _taken:
    (_kk / "o.json").write_text(json.dumps(_taken), encoding="utf-8")
    subprocess.run([r"C:/Users/rane/kokoro-venv/Scripts/python.exe", str(ROOT / "tools" / "kokoro_zeg.py"), str(_kk / "o.json")], check=True)
clips = []
for k, (sp, sc, z) in enumerate(regels):
    if sp in KOKORO:                                      # Kokoro geeft 24 kHz, net als OmniVoice
        c, _sr = sf.read(_kk / f"{k}.wav", dtype="float32"); c = edge_fade(trim(c, SR), SR); clips.append(c)
        print(k, sp, "kokoro", KOKORO[sp], round(len(c) / SR, 2), flush=True); continue
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
