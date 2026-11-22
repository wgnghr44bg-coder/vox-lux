"""Whisper-controle per zin (stem.wav + zinnen.json). Getallen in cijfers tellen als goed. Print FOUT: <nrs>."""
import json, re, sys, soundfile as sf, torch, librosa
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
a, sr = sf.read("stem.wav", dtype="float32")
GET = {"zero":"0","one":"1","two":"2","three":"3","four":"4","five":"5","six":"6","seven":"7","eight":"8","nine":"9","ten":"10"}
def norm(s):
    s = s.lower().replace("%", " percent").replace("$", " dollars ").replace("&", " and ")
    s = re.sub(r"[^a-z0-9 ]", " ", s); w = s.split()
    return [x for x in w if not x.isdigit() and x not in GET and x not in ("dollars", "dollar", "billion", "million", "percent", "point", "and", "hundred", "thousand", "trillion", "the", "a")]
fout = []
for i, (s, e, z, sc) in enumerate(json.load(open("zinnen.json", encoding="utf-8"))):
    x = librosa.resample(a[int(s * sr):int(e * sr)], orig_sr=sr, target_sr=16000)
    t = asr({"raw": x, "sampling_rate": 16000}, generate_kwargs={"language": "en"})["text"].strip()
    v, h = norm(z), norm(t)
    import difflib
    r = difflib.SequenceMatcher(None, v, h).ratio()
    if r < 0.9: fout.append(i); print(f"{i:3} {r:.2f} | {z} \n      -> {t}")
print("FOUT:", ",".join(map(str, fout)) if fout else "geen")
