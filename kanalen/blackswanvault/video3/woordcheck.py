"""Uitspraakcontrole per woord: Whisper met woordtijden. Meldt woorden die raar lang/kort duren of verkeerd verstaan worden.
Gebruik: woordcheck.py [zin-nrs]   (zonder nrs: alle zinnen)"""
import json, re, sys, soundfile as sf, torch, librosa, numpy as np
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = sf.read("stem.wav", dtype="float32")
Z = json.load(open("zinnen.json", encoding="utf-8"))
nrs = [int(x) for x in sys.argv[1].split(",")] if len(sys.argv) > 1 else range(len(Z))
for i in nrs:
    s, e, z, sc = Z[i]
    x = librosa.resample(a[int(s * sr):int(e * sr)], orig_sr=sr, target_sr=16000)
    r = asr({"raw": x, "sampling_rate": 16000}, return_timestamps="word", generate_kwargs={"language": "en"})
    raar = []
    for c in r["chunks"]:
        w = c["text"].strip(); t0, t1 = c["timestamp"]; t1 = t1 if t1 is not None else e - s
        d = t1 - t0; n = max(1, len(re.sub(r"[^a-zA-Z0-9]", "", w)))
        if d / n > 0.16 and d > 0.6: raar.append(f"{w}({d:.2f}s)")
    print(f"{i:3} {'LET OP ' + ' '.join(raar) if raar else 'ok'} | {r['text'].strip()}", flush=True)
