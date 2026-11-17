"""Ontwerpt nieuwe vertellerstemmen met OmniVoice (voice design: niet nagemaakt van iemand) en laat elke stem dezelfde
proeftekst inspreken, gecontroleerd met Whisper (woorden + niets na de laatste zin). Uitvoer: één mp3 met alle stemmen
achter elkaar (piepje + korte stilte ertussen) en een lijst met de volgorde.

  C:/Users/rane/omnivoice-venv/Scripts/python.exe kanalen/bodycam/stem_proeven.py
Stemmen komen in C:/Users/rane/vox-lux-stemmen/ontwerp-<naam>/ (ref.wav + voice.json), bruikbaar met
maak_voiceover.py --stem-map.
"""
import json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, torch, librosa, difflib
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
from transformers import pipeline

UIT = Path("C:/Users/rane/vox-lux-stemmen")
PROEF_DIR = ROOT / "kanalen" / "bodycam" / "stemproeven"
PROEF_DIR.mkdir(exist_ok=True)
SR = ov.SR
REF_TEKST = ("The call came in just after midnight. Two officers were sent to a quiet street on the edge of town. "
             "What they found there would change the case completely.")
PROEF = ("On the night of April second, 2023, a driver went around a Border Patrol checkpoint on Interstate 10. "
         "Agents followed him for almost fifty minutes. When he finally stepped out of his car, he was holding a "
         "wooden club. In today's documentary, we're covering what happened next.")
# naam: (instruct-delen, seed)
ONTWERPEN = {
    "us-man-laag-1": (("male", "middle-aged", "low pitch", "american accent"), 11),
    "us-man-laag-2": (("male", "middle-aged", "low pitch", "american accent"), 23),
    "us-man-laag-3": (("male", "middle-aged", "low pitch", "american accent"), 37),
    "us-man-midden-1": (("male", "middle-aged", "moderate pitch", "american accent"), 41),
    "us-man-midden-2": (("male", "middle-aged", "moderate pitch", "american accent"), 53),
    "us-man-jong-1": (("male", "young adult", "low pitch", "american accent"), 67),
    "us-vrouw-1": (("female", "middle-aged", "low pitch", "american accent"), 71),
    "us-vrouw-2": (("female", "middle-aged", "moderate pitch", "american accent"), 83),
}

inst = b1.standaard()
ASR = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)


def gehoord(wav):
    a = librosa.resample(np.asarray(wav, dtype="float32"), orig_sr=SR, target_sr=16000)
    a = np.concatenate([np.zeros(8000, np.float32), a, np.zeros(8000, np.float32)])
    r = ASR({"raw": a, "sampling_rate": 16000}, generate_kwargs={"language": "en"}, return_timestamps="word")
    return r["text"].strip(), [c for c in r["chunks"] if c["text"].strip()]


def woorden(t):
    return [w for w in re.findall(r"[a-z']+", t.lower().replace("-", " ")) if w not in
            {"one", "two", "three", "four", "five", "ten", "twenty", "fifty", "second", "and", "a", "nd", "th"}]


def knip(wav, ch):
    b = max(0.0, ch[0]["timestamp"][0] - 0.5 - 0.08)
    e = (ch[-1]["timestamp"][1] or ch[-1]["timestamp"][0] + 0.4) - 0.5 + 0.18
    return edge_fade(np.asarray(wav, dtype="float32")[int(b * SR):int(e * SR)].copy(), SR, ms=15)


resultaat = []
for naam, (delen, seed) in ONTWERPEN.items():
    d = UIT / f"ontwerp-{naam}"
    d.mkdir(parents=True, exist_ok=True)
    instruct = ", ".join(delen)
    torch.manual_seed(seed)
    with torch.no_grad():
        ref = np.asarray(ov.model().generate(text=REF_TEKST, instruct=instruct, speed=0.95)[0], dtype=np.float32)
    ref = edge_fade(trim(ref, SR), SR)
    sf.write(d / "ref.wav", np.concatenate([np.zeros(2400, np.float32), ref, np.zeros(4800, np.float32)]), SR)
    (d / "voice.json").write_text(json.dumps({"name": f"ontwerp-{naam}", "description":
        f"Ontworpen met OmniVoice voice design (niet nagemaakt van iemand), bodycam-proef 17 nov 2026: {instruct}",
        "ref_text": REF_TEKST, "instruct": instruct, "seed": seed}, indent=1), encoding="utf-8")
    ov._prompts[naam] = ov.model().create_voice_clone_prompt(ref_audio=str(d / "ref.wav"), ref_text=REF_TEKST)
    cfg = VoiceConfig(voice=naam, speed=0.95, seed=7, num_step=inst["model"]["num_step"],
                      guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
    zinnen = re.split(r"(?<=[.!?])\s+", PROEF)
    clips, ok = [], True
    for i, z in enumerate(zinnen):
        beste = None
        for poging in range(6):
            w = edge_fade(trim(ov.speak([z], cfg, seed=7 + 1000 * poging + i)[0], SR), SR)
            t, ch = gehoord(w)
            sc = difflib.SequenceMatcher(None, woorden(z), woorden(t)).ratio()
            if ch and (beste is None or sc > beste[0]):
                beste = (sc, knip(w, ch), t)
            if sc >= 0.999:
                break
        ok &= beste[0] >= 0.999
        clips += [beste[1], np.zeros(int(0.8 * SR), np.float32)]
    stem = np.concatenate(clips)
    sf.write(PROEF_DIR / f"{naam}.wav", stem, SR)
    woorden_n = len(PROEF.split())
    tempo = woorden_n / (len(stem) / SR / 60)
    resultaat.append((naam, instruct, ok, round(tempo)))
    print(f"{naam}: {instruct} | woorden kloppen: {'ja' if ok else 'NEE'} | {tempo:.0f} w/min", flush=True)

# alles achter elkaar in één mp3, met een piepje tussen de stemmen
piep = (0.25 * np.sin(2 * np.pi * 880 * np.arange(int(0.18 * SR)) / SR)).astype(np.float32)
stukken = []
for nr, (naam, *_rest) in enumerate(resultaat, 1):
    a, _ = sf.read(PROEF_DIR / f"{naam}.wav", dtype="float32")
    stukken += [piep] * nr + [np.zeros(int(0.15 * SR), np.float32)] * nr   # 1 piep = stem 1, 2 piepjes = stem 2 ...
    stukken += [np.zeros(int(0.6 * SR), np.float32), a, np.zeros(int(1.5 * SR), np.float32)]
sf.write(PROEF_DIR / "alle.wav", np.concatenate(stukken), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(PROEF_DIR / "alle.wav"), "-af", "loudnorm=I=-16:TP=-1.5",
                "-ar", "44100", "-b:a", "160k", str(PROEF_DIR / "stemproeven.mp3")], check=True)
(PROEF_DIR / "volgorde.txt").write_text("\n".join(f"{i}. {n} ({ins}) – woorden {'ok' if o else 'NIET ok'}, {t} w/min"
                                                  for i, (n, ins, o, t) in enumerate(resultaat, 1)), encoding="utf-8")
print("klaar:", PROEF_DIR / "stemproeven.mp3")
