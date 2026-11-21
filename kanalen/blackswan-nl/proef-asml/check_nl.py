"""Whisper (taal nl) per zin: toont wat er verstaan wordt, voor controle."""
import json, sys, soundfile as sf, librosa, torch
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = sf.read("stem.wav", dtype="float32")
Z = json.load(open("zinnen.json", encoding="utf-8"))
if "--alinea" in sys.argv:                                   # per alinea (scene) controleren
    from itertools import groupby
    Z = [[g[0][0], g[-1][1], " ".join(x[2] for x in g), sc] for sc, g in ((k, list(v)) for k, v in groupby(Z, key=lambda x: x[3]))]
for i, (s, e, z, sc) in enumerate(Z):
    stuk = librosa.resample(a[int(s * sr):int(e * sr)], orig_sr=sr, target_sr=16000)
    h = asr({"raw": stuk, "sampling_rate": 16000}, generate_kwargs={"language": "dutch", "task": "transcribe"})["text"].strip()
    print(f"{i:2} {z}\n   -> {h}")
