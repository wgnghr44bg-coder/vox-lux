"""Vergelijkt Chatterbox-stemmen (natuurlijker, MIT-licentie, gratis, lokaal) voor de bodycam-verteller.
Elke stem spreekt de proeftekst per ALINEA in één keer in (natuurlijke zinsmelodie, eigenaar 17 nov: "te robot achtig"),
gecontroleerd met Whisper; niets na het laatste woord. Uitvoer: stemproeven/chatterbox.mp3 (piepjes = nummer).

  C:/Users/rane/chatterbox-venv/Scripts/python.exe kanalen/bodycam/chatterbox_proef.py
"""
import difflib, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf, torch

HIER = Path(__file__).resolve().parent
UIT = HIER / "stemproeven"
UIT.mkdir(exist_ok=True)
S = Path("C:/Users/rane/vox-lux-stemmen")
TEKST = ("On the night of April second, 2023, a driver went around a Border Patrol checkpoint on Interstate 10. "
         "Agents followed him for almost fifty minutes. When he finally stepped out of his car, he was holding a "
         "wooden club. In today's documentary, we're covering what happened next.")
STEMMEN = [  # (naam, referentie, exaggeration, cfg_weight); lage cfg = rustiger, meer vertellend tempo
    ("jouw stem (Chatterbox)", S / "bodycam-stem-2" / "ref.wav", 0.5, 0.25),
    ("jouw stem, meer gevoel (Chatterbox)", S / "bodycam-stem-2" / "ref.wav", 0.65, 0.2),
    ("Amerikaanse man 1 (Chatterbox)", S / "ontwerp-us-man-laag-1" / "ref.wav", 0.5, 0.25),
    ("Amerikaanse man 2 (Chatterbox)", S / "ontwerp-us-man-laag-2" / "ref.wav", 0.5, 0.25),
    ("Amerikaanse man 3 (Chatterbox)", S / "ontwerp-us-man-laag-3" / "ref.wav", 0.5, 0.25),
]

from chatterbox.tts import ChatterboxTTS
from transformers import pipeline
import librosa

model = ChatterboxTTS.from_pretrained(device="cuda")
SR = model.sr
ASR = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)


def woorden(t):
    return [w for w in re.findall(r"[a-z']+", t.lower().replace("-", " ")) if w not in
            {"one", "two", "three", "four", "ten", "twenty", "fifty", "second", "and", "a", "nd", "th"}]


resultaat = []
for nr, (naam, ref, ex, cfg) in enumerate(STEMMEN, 1):
    beste = None
    for poging in range(5):
        torch.manual_seed(100 + poging)
        wav = model.generate(TEKST, audio_prompt_path=str(ref), exaggeration=ex, cfg_weight=cfg)
        a = wav.squeeze(0).cpu().numpy().astype(np.float32)
        x = librosa.resample(a, orig_sr=SR, target_sr=16000)
        x = np.concatenate([np.zeros(8000, np.float32), x, np.zeros(8000, np.float32)])
        r = ASR({"raw": x, "sampling_rate": 16000}, generate_kwargs={"language": "en"}, return_timestamps="word")
        sc = difflib.SequenceMatcher(None, woorden(TEKST), woorden(r["text"])).ratio()
        ch = [c for c in r["chunks"] if c["text"].strip()]
        if ch:   # alles voor het eerste en na het laatste woord eraf
            b = max(0.0, ch[0]["timestamp"][0] - 0.58)
            e = (ch[-1]["timestamp"][1] or ch[-1]["timestamp"][0] + 0.4) - 0.5 + 0.2
            a = a[int(b * SR):int(e * SR)]
        if beste is None or sc > beste[0]:
            beste = (sc, a, r["text"].strip())
        if sc >= 0.999:
            break
    sc, a, gehoord = beste
    sf.write(UIT / f"chatterbox-{nr}.wav", a, SR)
    tempo = len(TEKST.split()) / (len(a) / SR / 60)
    resultaat.append((naam, sc, round(tempo), gehoord))
    print(f"{nr}. {naam}: woorden {'ok' if sc >= 0.999 else f'{sc:.2f}'} | {tempo:.0f} w/min | {gehoord}", flush=True)

piep = (0.25 * np.sin(2 * np.pi * 880 * np.arange(int(0.18 * SR)) / SR)).astype(np.float32)
stukken = []
for nr in range(1, len(resultaat) + 1):
    a, _ = sf.read(UIT / f"chatterbox-{nr}.wav", dtype="float32")
    stukken += [piep, np.zeros(int(0.15 * SR), np.float32)] * nr + [np.zeros(int(0.6 * SR), np.float32), a,
                                                                   np.zeros(int(1.5 * SR), np.float32)]
sf.write(UIT / "chatterbox-alle.wav", np.concatenate(stukken), SR)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(UIT / "chatterbox-alle.wav"), "-af", "loudnorm=I=-16:TP=-1.5",
                "-ar", "44100", "-b:a", "160k", str(UIT / "chatterbox.mp3")], check=True)
(UIT / "chatterbox-volgorde.txt").write_text("\n".join(f"{i}. {n} – woorden {s:.2f}, {t} w/min" for i, (n, s, t, _)
                                                       in enumerate(resultaat, 1)), encoding="utf-8")
print("klaar")
