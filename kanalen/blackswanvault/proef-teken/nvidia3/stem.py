"""BlackSwanVault video 6 (werkt AI?): script.txt inspreken met stem zakelijk-23 (ontworpen, niet gekloond).
Schrijft stem.wav (24 kHz) + zinnen.json: [start, eind, zin, scene]. Met --opnieuw 3,17 alleen die zinnen opnieuw
(rest uit de bestaande stem.wav)."""
import json, sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf
import b1
from voice import omnivoice_engine as ov
from voice.batch_generator import edge_fade, trim
from voice.voice_config import VoiceConfig
H = Path(__file__).parent
inst = b1.standaard(); SR = ov.SR
cfg = VoiceConfig(voice="zakelijk-23", speed=0.9,   # tekenproef 22 nov: "het gaat heel snel" -> rustiger
 seed=23, num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
zinnen, scene = [], None
for r in (H / "script.txt").read_text(encoding="utf-8").splitlines():
    r = r.strip()
    if not r or r.startswith("#") or r == "{SLOT}": continue
    if r.startswith("@scene"): scene = r.split()[1]; continue
    zinnen.append((r, scene))
opnieuw = set()
if "--opnieuw" in sys.argv:
    opnieuw = {int(x) for x in sys.argv[sys.argv.index("--opnieuw") + 1].split(",")}
oud = {}
if opnieuw and (H / "zinnen.json").exists():
    a, _ = sf.read(H / "stem.wav", dtype="float32")
    for i, (s, e, z, sc) in enumerate(json.load(open(H / "zinnen.json", encoding="utf-8"))):
        if i not in opnieuw: oud[z] = a[int(s * SR):int(e * SR)]
clips = [oud.get(z) for z, _ in zinnen]
todo = [i for i, c in enumerate(clips) if c is None]
extra = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
for b in range(0, len(todo), 4):
    groep = todo[b:b + 4]
    out = ov.speak([zinnen[i][0] for i in groep], cfg, seed=23 + b + extra)
    for i, w in zip(groep, out): clips[i] = edge_fade(trim(w, SR), SR)
    print(f"{min(b + 4, len(todo))}/{len(todo)}", flush=True)
for i in todo:                                   # afgekapt of veel te snel: opnieuw
    z = zinnen[i][0]
    for p in range(1, 6):
        d = len(clips[i]) / SR
        if d >= 0.3 and len(z.split()) / (d / 60) <= 230: break
        clips[i] = edge_fade(trim(ov.speak([z], cfg, seed=1000 * p + i + extra)[0], SR), SR)
t = 0.5; delen = [np.zeros(int(t * SR), np.float32)]; tijden = []
for k, ((z, sc), c) in enumerate(zip(zinnen, clips)):
    tijden.append([round(t, 3), round(t + len(c) / SR, 3), z, sc])
    volgende = zinnen[k + 1][1] if k + 1 < len(zinnen) else None
    if volgende is None: p = 1.5
    elif volgende != sc and (volgende.startswith("h") and "-" not in volgende or volgende == "titel"): p = 1.3   # voor een hoofdstuk
    elif volgende != sc: p = 1.2   # tekenproef: nieuw bord, adem
    else: p = 0.8 if len(z.split()) <= 3 else 0.7   # tekenproef 22 nov: rustiger
    if z.endswith("?"): p += 0.3   # 19 nov: tempo zoals eerste proef (eigenaar)
    if z.endswith("?") and len(z.split()) <= 2: p = max(p, 1.6)   # 20 nov: na een korte vraag ("Why?") een echte pauze (eigenaar)
    if k + 1 < len(zinnen) and zinnen[k + 1][0].endswith("?") and len(zinnen[k + 1][0].split()) <= 2: p = max(p, 1.2)   # en ervoor
    delen += [c, np.zeros(int(p * SR), np.float32)]; t += len(c) / SR + p
sf.write(H / "stem.wav", np.concatenate(delen), SR)
(H / "zinnen.json").write_text(json.dumps(tijden, indent=0, ensure_ascii=False), encoding="utf-8")
w = sum(len(z.split()) for z, _ in zinnen)
print(f"KLAAR {t / 60:.1f} min, {w / (t / 60):.0f} woorden/min, {len(zinnen)} zinnen")
