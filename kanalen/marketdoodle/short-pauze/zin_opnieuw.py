"""Eén zin opnieuw inspreken en in stem.wav zetten (rest blijft exact hetzelfde). Gebruik: python zin_opnieuw.py <zinnr>"""
import json, sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
STEM = {"N": ("eigen-stem-swan", 1.05), "YOU": ("whatif-zoon", 1.0)}
nr = int(sys.argv[1])
regels = [r.rstrip("\n").split("|", 2) for r in (H / "script.txt").read_text(encoding="utf-8").splitlines() if r.strip() and not r.startswith("#")]
Z = json.load(open(H / "zinnen.json", encoding="utf-8")); a, _ = sf.read(H / "stem.wav", dtype="float32")
clips = [a[int(s * SR):int(e * SR)] for s, e, *_ in Z]
sp, sc, z = regels[nr]; v, spd = STEM[sp]
cfg = VoiceConfig(voice=v, speed=spd, seed=23, num_step=inst["model"]["num_step"], guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
for p in range(6):
    c = edge_fade(trim(ov.speak([z], cfg, seed=100 * nr + p + 50)[0], SR), SR); d = len(c) / SR
    if d >= 0.3 and len(z.split()) / (d / 60) <= 230: break
clips[nr] = c; print("zin", nr, round(d, 2))
t = 0.3; delen = [np.zeros(int(t * SR), np.float32)]; tijden = []
for k, ((sp, sc, z), c) in enumerate(zip(regels, clips)):
    tijden.append([round(t, 3), round(t + len(c) / SR, 3), z, sc, sp])
    p = 0.35 if k + 1 < len(regels) and regels[k + 1][0] != sp else 0.45
    if z.endswith("?") and sp == "N": p = 0.8
    if k + 1 == len(regels): p = 1.2
    delen += [c, np.zeros(int(p * SR), np.float32)]; t += len(c) / SR + p
sf.write(H / "stem.wav", np.concatenate(delen), SR)
(H / "zinnen.json").write_text(json.dumps(tijden, indent=0, ensure_ascii=False), encoding="utf-8")
print("KLAAR", round(t, 1), "s")
