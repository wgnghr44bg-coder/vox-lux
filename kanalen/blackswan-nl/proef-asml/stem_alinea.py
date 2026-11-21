"""Geldverhaal (eigenaar 21 nov: "niet stoppen als je een zin afmaakt"): per @scene de hele alinea in één keer inspreken,
zodat zinnen in elkaar overlopen. Daarna Whisper (woordtijden) om het begin/eind van elke zin te vinden -> zinnen.json.
Stem richard-nl, speed 1.1, seed 1. Afkortingen als losse letters in script.txt (A S M L, A E X)."""
import json, re, sys
from pathlib import Path
ROOT = Path(r"C:/Users/rane/Documents/vox-lux-routine")
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "audio_engine"))
import numpy as np, soundfile as sf, librosa, torch
from voice import omnivoice_engine as ov
from voice.voice_config import VoiceConfig
import b1
H = Path(__file__).parent; inst = b1.standaard(); SR = ov.SR
cfg = VoiceConfig(voice="richard-nl", speed=1.1, seed=1, num_step=inst["model"]["num_step"],
                  guidance_scale=inst["model"]["guidance_scale"], denoise=inst["model"]["denoise"])
alineas, scene = [], None
for r in (H / "script.txt").read_text(encoding="utf-8").splitlines():
    r = r.strip()
    if not r or r.startswith("#"): continue
    if r.startswith("@scene"): scene = r.split()[1]; alineas.append([scene, []]); continue
    alineas[-1][1].append(r)
seed_extra = int(sys.argv[sys.argv.index("--seed") + 1]) if "--seed" in sys.argv else 0
def trim(a, drempel=0.01):
    idx = np.where(np.abs(a) > drempel)[0]
    return a[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)] if len(idx) else a
stukken, t, uit = [np.zeros(int(0.5 * SR), np.float32)], 0.5, []
from transformers import pipeline
asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
def norm(w): return re.sub(r"[^a-z0-9à-ü]", "", w.lower())
for k, (sc, zinnen) in enumerate(alineas):
    tekst = " ".join(zinnen)
    cache = H / "cache" / f"alinea-{k}.wav"; cache.parent.mkdir(exist_ok=True)
    opnieuw = "--opnieuw" in sys.argv and str(k) in sys.argv[sys.argv.index("--opnieuw") + 1].split(",")
    if cache.exists() and not opnieuw:
        a = sf.read(cache, dtype="float32")[0]
    else:
        a = trim(ov.speak([tekst], cfg, seed=1 + k + seed_extra)[0]); sf.write(cache, a, SR)
    # woordtijden om zinsgrenzen te vinden
    r = asr({"raw": librosa.resample(a, orig_sr=SR, target_sr=16000), "sampling_rate": 16000}, return_timestamps="word",
            generate_kwargs={"language": "dutch", "task": "transcribe"})
    woorden = [(c["timestamp"][0] or 0.0, c["timestamp"][1] or 0.0) for c in r["chunks"]]
    nw = [len(z.split()) for z in zinnen]; totaal = sum(nw); dur = len(a) / SR
    # zinsgrens = woordindex volgens aandeel woorden (Whisper telt getallen anders, dus naar verhouding)
    grens, acc = [], 0
    for i, n in enumerate(nw):
        b = round(acc / totaal * len(woorden)); e = round((acc + n) / totaal * len(woorden)) - 1; acc += n
        s0 = 0.0 if i == 0 else woorden[min(b, len(woorden) - 1)][0]
        e0 = dur if i == len(nw) - 1 else woorden[max(0, min(e, len(woorden) - 1))][1]
        grens.append((s0, e0))
    for z, (s0, e0) in zip(zinnen, grens):
        uit.append([round(t + s0, 3), round(t + e0, 3), z, sc])
    p = 0.6 if k + 1 < len(alineas) else 1.2          # korte adempauze tussen alinea's
    stukken += [a, np.zeros(int(p * SR), np.float32)]; t += dur + p
    print(sc, round(dur, 1), "s |", r["text"][:90], flush=True)
sf.write(H / "stem.wav", np.concatenate(stukken), SR)
(H / "zinnen.json").write_text(json.dumps(uit, indent=0, ensure_ascii=False), encoding="utf-8")
print(f"KLAAR {t / 60:.2f} min")
