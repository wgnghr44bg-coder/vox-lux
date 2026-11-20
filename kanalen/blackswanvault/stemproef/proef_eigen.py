"""Proef eigen-stem-swan: opening van video 5 (zin 0-20) + vergelijkingstekst."""
import sys, json
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, librosa, b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
inst = b1.standaard()
cfg = VoiceConfig(voice=(sys.argv[1] if len(sys.argv) > 1 else "eigen-stem-swan"), speed=1.0, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
Z = json.load(open(ROOT / "kanalen/blackswanvault/video5/zinnen.json", encoding="utf-8"))[:21]
zin = [z[2] for z in Z]
clips = []
for b in range(0, len(zin), 4):
    clips += [edge_fade(trim(w, ov.SR), ov.SR) for w in ov.speak(zin[b:b + 4], cfg, seed=23 + b)]
delen = []; t = 0.5; tijden = []; delen.append(np.zeros(int(0.5 * ov.SR), np.float32))
for k, c in enumerate(clips):
    p = 0.6 if k + 1 < len(Z) and Z[k + 1][3] != Z[k][3] else (0.6 if len(zin[k].split()) <= 3 else 0.35)
    tijden.append([round(t, 3), round(t + len(c) / ov.SR, 3), zin[k], Z[k][3]]); t += len(c) / ov.SR + p
    delen += [c, np.zeros(int(p * ov.SR), np.float32)]
a = np.concatenate(delen); sf.write(f"proef-{cfg.voice}.wav", a, ov.SR)
json.dump(tijden, open(f"zinnen-{cfg.voice}.json", "w", encoding="utf-8"), ensure_ascii=False)
f0, v, _ = librosa.pyin(a, fmin=60, fmax=400, sr=ov.SR); f = f0[~np.isnan(f0)]
print("duur", round(len(a) / ov.SR, 1), "s; Hz", round(float(np.median(f))), "spreiding", round(float(np.std(f))), "wpm", round(sum(len(z.split()) for z in zin) / (len(a) / ov.SR / 60)))
