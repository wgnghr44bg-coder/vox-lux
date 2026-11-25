"""Woordtijden per zin (eigenaar 22 nov: "zorg dat de afbeeldingen echt overeenkomen met wat er gezegd wordt").
Leest stem.wav + zinnen.json in de huidige map, laat Whisper per zin de woorden met tijden geven en schrijft woorden.json:
[[zin_nr, woord, start_s, eind_s], ...]. maak.py gebruikt dit om elk beeld te laten beginnen op het kernwoord.
  <omnivoice-venv>/python woordtijden.py [taal]   (taal: en (standaard) of nl)"""
import json, sys
import librosa, soundfile as sf, torch
from transformers import pipeline

taal = sys.argv[1] if len(sys.argv) > 1 else "en"
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = sf.read("stem.wav", dtype="float32")
if a.ndim > 1: a = a.mean(axis=1)
uit = []
for i, (s, e, z, sc, *_) in enumerate(json.load(open("zinnen.json", encoding="utf-8"))):
    stuk = a[int(s * sr):int(e * sr)]
    stuk = librosa.resample(stuk, orig_sr=sr, target_sr=16000)
    r = asr({"raw": stuk, "sampling_rate": 16000}, return_timestamps="word", generate_kwargs={"language": taal})
    for c in r.get("chunks", []):
        t0, t1 = c["timestamp"]
        uit.append([i, c["text"].strip(), round(s + (t0 or 0), 2), round(s + (t1 if t1 is not None else (t0 or 0) + 0.3), 2)])
json.dump(uit, open("woorden.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("woorden:", len(uit))
