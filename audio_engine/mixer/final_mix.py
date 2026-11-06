"""Final mix: narration + music -> one master at -14 LUFS, -1 dBTP, 48 kHz / 24-bit WAV and MP3, plus JSON."""
import json
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
import soundfile as sf

from effects import volume_control as vc
from export.mp3_export import to_mp3
from export.wav_export import to_wav24

from . import ducking
from .voice_music_mixer import MixConfig, music_gain_db, music_shaping

SR = 48000


def mix(voice_path, music_path, cfg: MixConfig, out_dir, name="mix", progress=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    say = progress or (lambda f, m="": None)
    t0 = time.time()
    tmp_v, tmp_m = out / "_voice48.wav", out / "_music48.wav"
    vdur = float(sf.info(voice_path).duration)
    total = vdur + cfg.tail
    say(0.05, "stem en muziek klaarzetten")
    to_wav24(voice_path, tmp_v)
    mdur = float(sf.info(music_path).duration)
    loop = ["-stream_loop", "-1"] if mdur < total else []              # too short: loop it (warned in JSON)
    vc.ffmpeg(loop + ["-i", str(music_path), "-t", f"{total:.3f}", "-af",
                      f"{music_shaping(cfg)},{vc.fades(total, 0, min(6.0, cfg.tail + 2))}",
                      "-ar", str(SR), "-ac", "2", "-c:a", "pcm_f32le", str(tmp_m)])
    say(0.25, "luidheid meten")
    lv, lm = vc.measure(tmp_v), vc.measure(tmp_m)
    mg = music_gain_db(lv["lufs"], lm["lufs"], cfg)
    curve = ducking.gain_curve(tmp_v, cfg.duck_amount_db, cfg.duck_attack, cfg.duck_release) if cfg.ducking else None
    say(0.4, "mixen")
    raw = out / "_mix-float.wav"
    vg, mgl = 10 ** (cfg.voice_gain_db / 20), 10 ** (mg / 20)
    block = SR * 30
    with sf.SoundFile(tmp_m) as fm, sf.SoundFile(tmp_v) as fv, sf.SoundFile(raw, "w", SR, 2, subtype="FLOAT") as fo:
        pos = 0
        while True:
            m = fm.read(block, dtype="float32", always_2d=True)
            if not len(m):
                break
            v = fv.read(len(m), dtype="float32", always_2d=True)
            if len(v) < len(m):
                v = np.vstack([v, np.zeros((len(m) - len(v), 2), np.float32)])
            if curve is not None:
                m = ducking.apply(m, pos, SR, curve)
            fo.write(v * vg + m * mgl)
            pos += len(m)
    say(0.8, "eindluidheid")
    lm2 = vc.measure(raw)
    gain = cfg.target_lufs - lm2["lufs"]
    lim = 10 ** ((cfg.true_peak - 0.5) / 20)          # margin: the limiter works on sample peaks
    final = to_wav24(raw, out / f"{name}.wav", af=f"volume={gain:.2f}dB,alimiter=limit={lim:.3f}:level=false:asc=1")
    to_mp3(final, out / f"{name}.mp3")
    for f in (tmp_v, tmp_m, raw):
        f.unlink(missing_ok=True)
    res = {"type": "mix", "config": asdict(cfg), "voice": str(voice_path), "music": str(music_path),
           "voice_lufs": lv["lufs"], "music_lufs_before": lm["lufs"], "music_gain_db": round(mg, 2),
           "music_looped": bool(loop), "result": vc.measure(final), "seconds": round(time.time() - t0, 1)}
    (out / f"{name}-config.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    say(1.0, "klaar")
    return res
