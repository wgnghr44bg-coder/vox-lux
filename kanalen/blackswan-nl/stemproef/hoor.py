import sys, soundfile as sf, librosa, torch
from transformers import pipeline
src = open("../../blackswanvault/video9/check_stem.py", encoding="utf-8").read()
import re
m = re.search(r'pipeline\((.*?)\)\n', src, re.S); print("model:", m.group(1)[:120])
asr = eval("pipeline(" + m.group(1) + ")")
for n in ["nl-a", "nl-b", "nl-c", "nl-d"]:
    a, sr = sf.read(n + ".wav", dtype="float32"); a = librosa.resample(a, orig_sr=sr, target_sr=16000)
    print(n, "|", asr({"raw": a, "sampling_rate": 16000}, generate_kwargs={"language": "dutch", "task": "transcribe"})["text"])
