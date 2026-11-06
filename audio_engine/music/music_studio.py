"""Music: compose + render (Python, GPU) -> effects (FFmpeg) -> loudness -> 24-bit WAV, MP3, stems, JSON."""
import json
import time
from dataclasses import asdict
from pathlib import Path

from effects import compressor, filters, reverb, stereo, volume_control as vc
from export.mp3_export import to_mp3
from export.stems_export import export_stems
from export.wav_export import to_wav24

from .composition_engine import MusicConfig, render


def effects_chain(cfg, ir_path):
    pre = f"{filters.highpass(cfg.highpass_hz)},{filters.lowpass(cfg.lowpass_hz)}"
    post = [stereo.widen(cfg.width)]
    if cfg.compression:
        post.append(compressor.gentle())
    fd = vc.fades(cfg.duration, cfg.fade_in, cfg.fade_out)
    if fd:
        post.append(fd)
    wet = max(cfg.reverb_mix, 0.0)
    graph = (f"[0:a]{pre},asplit=2[dry][snd];[snd][1:a]afir=dry=10:wet=10:irnorm=-1,volume={wet:.3f}[wet];"
             f"[dry][wet]amix=inputs=2:normalize=0,{','.join(post)}[out]")
    return graph


def generate(cfg: MusicConfig, out_dir, stems=None, progress=None):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    stems = cfg.duration <= 900 if stems is None else stems     # stems of hours of audio fill the disk
    t0 = time.time()
    say = progress or (lambda f, m="": None)
    info = render(cfg, out, stems=stems, progress=lambda f: say(0.7 * f, "muziek renderen"))
    say(0.72, "effecten (galm, filters, breedte)")
    ir = reverb.make_ir(out / "ir.wav", rt60=cfg.reverb_size, sr=cfg.sample_rate, seed=cfg.seed)
    wet = out / "music-fx.wav"
    vc.ffmpeg(["-i", str(out / "music-dry.wav"), "-i", str(ir), "-filter_complex", effects_chain(cfg, ir),
               "-map", "[out]", "-c:a", "pcm_f32le", str(wet)])
    say(0.9, "luidheid")
    m = vc.measure(wet)
    gain = cfg.target_lufs - m["lufs"]
    final = to_wav24(wet, out / "music.wav", af=f"volume={gain:.2f}dB,alimiter=limit=0.89:level=false")
    to_mp3(final, out / "music.mp3")
    if stems:
        dry = vc.measure(out / "music-dry.wav")
        export_stems(out, cfg.target_lufs - dry["lufs"])
    for f in (out / "music-dry.wav", wet, ir):
        f.unlink(missing_ok=True)
    res = {"type": "music", "config": asdict(cfg), "chords": info["chords"], "sections": info["sections"],
           "render_peak": info["peak"], "loudness": vc.measure(final), "seconds": round(time.time() - t0, 1),
           "files": sorted(p.name for p in out.iterdir())}
    (out / "config.json").write_text(json.dumps(res, indent=2), encoding="utf-8")
    say(1.0, "klaar")
    return res
