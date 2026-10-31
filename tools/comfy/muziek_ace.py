"""Slaapmuziek maken met ACE-Step 1.5 in ComfyUI (gratis, lokaal; eigenaar 31 okt 2026: "achtergrond muziek voor elke
video waar je rustig van wordt en in slaap valt"). Nieuwe muziek, van ons zelf: geen claim-risico (licentie Apache 2.0).

Eenmalig: models/checkpoints/ace_step_1.5_turbo_aio.safetensors (10 GB, Comfy-Org/ace_step_1.5_ComfyUI_files).
Gebruik:
  python tools/comfy/muziek_ace.py uitmap --stukken 3 --sec 180 [--seed 1] [--tags "..."] [--toon "A minor"]
Schrijft uitmap/ace-<seed>.flac per stuk. Daarna aan elkaar met zachte overgangen (tools/muziek_lang.py).
"""
import argparse, json, shutil, time, urllib.request
from pathlib import Path

COMFY = "http://127.0.0.1:8188"
OUT = Path(r"C:\Users\rane\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\ComfyUI\output")
TAGS = ("ambient, sleep music, very slow, calm, warm soft synth pads, gentle strings, deep soft drone, "
        "no drums, no percussion, no vocals, no melody lead, long sustained chords, dreamy, peaceful, lullaby, 432 hz")

ap = argparse.ArgumentParser()
ap.add_argument("uit", type=Path)
ap.add_argument("--stukken", type=int, default=1); ap.add_argument("--sec", type=float, default=180)
ap.add_argument("--seed", type=int, default=1); ap.add_argument("--tags", default=TAGS)
ap.add_argument("--toon", default="A minor"); ap.add_argument("--bpm", type=int, default=60)
ap.add_argument("--steps", type=int, default=8)
a = ap.parse_args()
a.uit.mkdir(parents=True, exist_ok=True)


def post(path, data=None):
    req = urllib.request.Request(COMFY + path, json.dumps(data).encode() if data else None,
                                 {"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))


for k in range(a.stukken):
    seed = a.seed + k
    g = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "ace_step_1.5_turbo_aio.safetensors"}},
        "2": {"class_type": "ModelSamplingAuraFlow", "inputs": {"model": ["1", 0], "shift": 3}},
        "3": {"class_type": "TextEncodeAceStepAudio1.5", "inputs": {
            "clip": ["1", 1], "tags": a.tags, "lyrics": "[Instrumental]", "seed": seed, "bpm": a.bpm,
            "duration": a.sec, "timesignature": "4", "language": "en", "keyscale": a.toon,
            "generate_audio_codes": True, "cfg_scale": 2.0, "temperature": 0.85, "top_p": 0.9, "top_k": 0, "min_p": 0.0}},
        "4": {"class_type": "ConditioningZeroOut", "inputs": {"conditioning": ["3", 0]}},
        "5": {"class_type": "EmptyAceStep1.5LatentAudio", "inputs": {"seconds": a.sec, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0],
              "latent_image": ["5", 0], "seed": seed, "steps": a.steps, "cfg": 1, "sampler_name": "euler",
              "scheduler": "simple", "denoise": 1}},
        "7": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveAudio", "inputs": {"audio": ["7", 0], "filename_prefix": f"audio/ace-{seed}"}},
    }
    pid = post("/prompt", {"prompt": g})["prompt_id"]
    t0 = time.time()
    while True:
        time.sleep(3)
        h = post(f"/history/{pid}")
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("status_str") == "error":
                raise SystemExit(f"ComfyUI fout: {json.dumps(st)[:800]}")
            outs = [f for o in h[pid]["outputs"].values() for f in o.get("audio", [])]
            if outs:
                f = outs[0]
                src = OUT / f.get("subfolder", "") / f["filename"]
                dst = a.uit / f"ace-{seed}{src.suffix}"
                shutil.copy(src, dst)
                print(f"{dst} ({time.time() - t0:.0f} s)", flush=True)
                break
