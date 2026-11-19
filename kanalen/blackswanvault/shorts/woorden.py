"""Woordtijden met Whisper (CPU) voor een stuk van stem.wav: python woorden.py <stem.wav> <t0> <t1> <uit.json>"""
import json, sys, soundfile as sf, librosa, torch
from transformers import pipeline
src, t0, t1, uit = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
a, sr = sf.read(src, dtype="float32")
if a.ndim > 1: a = a.mean(1)
x = librosa.resample(a[int(t0 * sr):int(t1 * sr)], orig_sr=sr, target_sr=16000)
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cpu", dtype=torch.float32)
r = asr({"raw": x, "sampling_rate": 16000}, return_timestamps="word", generate_kwargs={"language": "en"}, chunk_length_s=30)
w = [{"w": c["text"].strip(), "s": c["timestamp"][0], "e": c["timestamp"][1]} for c in r["chunks"]]
json.dump(w, open(uit, "w", encoding="utf-8"), ensure_ascii=False, indent=0); print(len(w), "woorden:", " ".join(c["w"] for c in w)[:300])
