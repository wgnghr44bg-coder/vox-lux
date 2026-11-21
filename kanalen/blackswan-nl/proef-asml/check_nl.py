"""Whisper (taal nl) per zin: toont wat er verstaan wordt, voor controle."""
import json, soundfile as sf, librosa, torch
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = sf.read("stem.wav", dtype="float32")
for i, (s, e, z, sc) in enumerate(json.load(open("zinnen.json", encoding="utf-8"))):
    stuk = librosa.resample(a[int(s * sr):int(e * sr)], orig_sr=sr, target_sr=16000)
    h = asr({"raw": stuk, "sampling_rate": 16000}, generate_kwargs={"language": "dutch", "task": "transcribe"})["text"].strip()
    print(f"{i:2} {z}\n   -> {h}")
