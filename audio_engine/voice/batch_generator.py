"""Script -> narration: split, speak in GPU batches, trim, join with pauses, export WAV/MP3 + timings + JSON."""
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import soundfile as sf

from export.mp3_export import to_mp3
from export.wav_export import to_wav24

from . import omnivoice_engine as ov
from .script_processor import pieces


def trim(a, sr, floor_db=-45.0, keep=0.03):
    """Cut silence/breath noise before and after the speech (threshold relative to the peak)."""
    if not len(a):
        return a
    env = np.convolve(np.abs(a), np.ones(int(0.01 * sr)) / int(0.01 * sr), mode="same")
    on = np.nonzero(env > np.abs(a).max() * 10 ** (floor_db / 20))[0]
    if not len(on):
        return a[:0]
    k = int(keep * sr)
    return a[max(on[0] - k, 0): on[-1] + k]


def edge_fade(a, sr, ms=8):
    n = min(int(ms / 1000 * sr), len(a) // 2)
    if n:
        a[:n] *= np.linspace(0, 1, n)
        a[-n:] *= np.linspace(1, 0, n)
    return a


def narrate(script, cfg, out_dir, progress=None, name="voice"):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    say = progress or (lambda f, m="": None)
    t_start = time.time()
    parts = pieces(script, cfg)
    if not parts:
        raise ValueError("Het script is leeg.")
    sr = ov.SR
    audio = [np.zeros(int(cfg.lead_in * sr), np.float32)]
    rows, pos = [], cfg.lead_in
    for b in range(0, len(parts), cfg.batch_size):
        batch = parts[b:b + cfg.batch_size]
        clips = ov.speak([t for t, _ in batch], cfg, seed=cfg.seed + b)
        for (text, pause), clip in zip(batch, clips):
            clip = edge_fade(trim(clip, sr), sr)
            audio += [clip, np.zeros(int(pause * sr), np.float32)]
            rows.append((len(rows) + 1, round(pos, 3), round(pos + len(clip) / sr, 3), text))
            pos += len(clip) / sr + pause
        say(min(0.9, (b + len(batch)) / len(parts) * 0.9), f"zin {b + len(batch)}/{len(parts)}")
    raw = out / f"{name}-24k.wav"
    sf.write(raw, np.concatenate(audio), sr, subtype="FLOAT")
    say(0.93, "exporteren")
    wav = to_wav24(raw, out / f"{name}.wav", af="highpass=f=60")
    to_mp3(wav, out / f"{name}.mp3")
    raw.unlink()
    with open(out / f"{name}-tijden.tsv", "w", encoding="utf-8") as f:
        f.write("nr\tstart\teinde\ttekst\n")
        for r in rows:
            f.write("\t".join(map(str, r)) + "\n")
    words = sum(len(t.split()) for t, _ in parts)
    res = {"type": "voice", "config": asdict(cfg), "sentences": len(parts), "words": words,
           "duration": round(pos, 2), "words_per_min": round(words / (pos / 60), 1),
           "seconds": round(time.time() - t_start, 1), "script": script}
    (out / f"{name}-config.json").write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    say(1.0, "klaar")
    return res


def batch(scripts, cfg, out_dir, progress=None):
    """scripts: {name: text}. Each gets its own files in out_dir/<name>/, all with the same voice."""
    results = {}
    for i, (name, text) in enumerate(scripts.items()):
        sub = (lambda f, m="", i=i: progress((i + f) / len(scripts), f"{name}: {m}")) if progress else None
        results[name] = narrate(text, cfg, Path(out_dir) / name, sub, name=name)
    return results
