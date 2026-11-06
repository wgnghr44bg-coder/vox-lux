"""Test round for the Audio Engine. Writes output/tests/test-report.json and prints PASS/FAIL per check.

  python tests/run_tests.py            # everything except the 2-hour test
  python tests/run_tests.py --lang     # also: 2 hours of music + a 2-hour mix
"""
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "output" / "tests"
OUT.mkdir(parents=True, exist_ok=True)
REPORT = {}


def check(name, ok, **info):
    REPORT[name] = {"ok": bool(ok), **info}
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {json.dumps(info, default=str)[:300]}", flush=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def probe(p):
    from effects.volume_control import ffmpeg
    import re
    r = ffmpeg(["-i", str(p), "-f", "null", "-"], quiet=False).stderr
    return re.search(r"Audio: ([^\n]+)", r).group(1)


def t_gpu():
    import torch
    ok = torch.cuda.is_available()
    check("gpu", ok, device=torch.cuda.get_device_name(0) if ok else None, torch=torch.__version__)
    import omnivoice
    check("omnivoice installed", True, version=getattr(omnivoice, "__version__", "0.2.1"))


def t_432():
    import torch
    from music.note_calculator import midi_to_hz
    from music.oscillator import additive
    ok = abs(midi_to_hz(69) - 432.0) < 1e-9 and abs(midi_to_hz(57) - 216.0) < 1e-9 and abs(midi_to_hz(60) - 256.869) < 1e-3
    sr = 48000
    t = torch.arange(sr * 4, dtype=torch.float32) / sr
    s = additive(t, midi_to_hz(69), [1.0], 0.0, sr).numpy()
    spec = np.abs(np.fft.rfft(s * np.hanning(len(s)), n=len(s) * 8))
    peak = np.fft.rfftfreq(len(s) * 8, 1 / sr)[spec.argmax()]
    check("432 Hz tuning", ok and abs(peak - 432.0) < 0.1, a4=midi_to_hz(69), c4=round(midi_to_hz(60), 3), measured_a4=round(float(peak), 3))


def t_music_and_effects():
    from dataclasses import replace
    from effects import volume_control as vc
    from music.composition_engine import build, preset
    from music.music_studio import generate
    for p in ("referentie", "cinematic"):
        cfg = preset(p, duration=150, seed=11)
        d = OUT / f"music-{p}"
        r = generate(cfg, d, stems=True)
        starts = sorted({e["start"] for e in build(cfg)["events"]["strings"]})
        gaps = np.diff(starts)
        check(f"music {p}: 7 s chord changes (plan)", np.allclose(gaps, cfg.chord_len), chords=r["chords"],
              gaps=sorted(set(np.round(gaps, 3).tolist())))
        # measured: when does the harmony change? chroma of the string stem, frame-to-frame difference
        y, sr = sf.read(d / "stems" / "stem-strings.wav", always_2d=True)
        y = y.mean(axis=1)
        hop = sr // 10
        frames = len(y) // hop
        ch = []
        for i in range(frames):
            seg = y[i * hop:(i + 1) * hop]
            sp = np.abs(np.fft.rfft(seg * np.hanning(len(seg))))
            f = np.fft.rfftfreq(len(seg), 1 / sr)
            ok = (f > 80) & (f < 2000)
            pc = np.round(12 * np.log2(f[ok] / 432.0)) % 12
            v = np.bincount(pc.astype(int), weights=sp[ok], minlength=12)
            ch.append(v / (np.linalg.norm(v) + 1e-9))
        ch = np.array(ch)
        # novelty: harmony of the 2 s before vs the 2 s after each moment (a crossfade is one change, not two)
        w = 20
        nov = np.zeros(len(ch))
        for i in range(w, len(ch) - w):
            a, b = ch[i - w:i].mean(0), ch[i:i + w].mean(0)
            nov[i] = np.linalg.norm(a / (np.linalg.norm(a) + 1e-9) - b / (np.linalg.norm(b) + 1e-9))
        peaks = [i / 10 for i in range(1, len(nov) - 1) if nov[i] > nov[i - 1] and nov[i] >= nov[i + 1] and nov[i] > np.percentile(nov, 70)]
        merged = []
        for p_ in peaks:
            if merged and p_ - merged[-1] < 4.5:
                if nov[int(p_ * 10)] > nov[int(merged[-1] * 10)]:
                    merged[-1] = p_
            else:
                merged.append(p_)
        md = np.median(np.diff(merged)) if len(merged) > 2 else 0
        # a change sits in the crossfade, just after a multiple of the chord length
        on_grid = np.mean([abs(((x - cfg.fade / 2) % cfg.chord_len) - cfg.chord_len / 2) > cfg.chord_len / 2 - 1.8 for x in merged])
        check(f"music {p}: chord changes heard every ±7 s (measured)", 6.0 <= md <= 8.0 and on_grid > 0.8,
              median_gap_s=round(float(md), 2), n_changes=len(merged), on_7s_grid=round(float(on_grid), 2))
        fin = d / "music.wav"
        info = probe(fin)
        check(f"music {p}: WAV 48 kHz stereo 24-bit", "48000 Hz" in info and "stereo" in info and "s32" in info or "s24" in info, probe=info)
        check(f"music {p}: MP3", (d / "music.mp3").exists() and "mp3" in probe(d / "music.mp3"), probe=probe(d / "music.mp3"))
        m = vc.measure(fin)
        pk = vc.peak_db(fin)
        check(f"music {p}: loudness and no clipping", abs(m["lufs"] - cfg.target_lufs) < 0.6 and pk < -0.5,
              lufs=m["lufs"], true_peak=m["true_peak"], sample_peak_db=pk)
        # clicks: largest jump of the high-passed signal relative to its typical size
        z, _ = sf.read(fin, always_2d=True)
        hp = np.diff(z[:, 0], n=2)
        ratio = float(np.abs(hp).max() / (np.percentile(np.abs(hp), 99.9) + 1e-12))
        check(f"music {p}: no clicks", ratio < 8, max_jump_vs_p999=round(ratio, 2))
        # filtering: energy above the low-pass vs below
        Z = np.abs(np.fft.rfft(z[: sr * 60, 0]))
        fz = np.fft.rfftfreq(sr * 60, 1 / sr)
        above = 10 * np.log10((Z[fz > cfg.lowpass_hz * 2] ** 2).sum() / (Z[fz < cfg.lowpass_hz] ** 2).sum())
        check(f"music {p}: low-pass works", above < -30, energy_above_2x_cutoff_db=round(float(above), 1))
        check(f"music {p}: stems", len(list((d / "stems").glob("stem-*.wav"))) == 5, stems=sorted(x.name for x in (d / "stems").glob("*.wav")))
    # reverb: impulse through the effects chain, measure the decay time
    from music.composition_engine import MusicConfig
    from music.music_studio import effects_chain
    from effects import reverb
    sr = 48000
    imp = np.zeros((sr * 6, 2), np.float32)
    imp[sr // 2] = 0.5
    sf.write(OUT / "impulse.wav", imp, sr, subtype="FLOAT")
    c = MusicConfig(duration=6, reverb_mix=1.0, reverb_size=3.0, compression=False, fade_in=0, fade_out=0, width=1.0,
                    highpass_hz=20, lowpass_hz=20000)
    ir = reverb.make_ir(OUT / "ir.wav", rt60=3.0)
    vc.ffmpeg(["-i", str(OUT / "impulse.wav"), "-i", str(ir), "-filter_complex", effects_chain(c, ir), "-map", "[out]",
               "-c:a", "pcm_f32le", str(OUT / "impulse-wet.wav")])
    w, _ = sf.read(OUT / "impulse-wet.wav", always_2d=True)
    e = np.cumsum((w[sr // 2 + int(0.03 * sr):, 0] ** 2)[::-1])[::-1]
    edc = 10 * np.log10(e / e[0] + 1e-20)
    i5, i35 = np.argmax(edc < -5), np.argmax(edc < -35)
    rt60 = (i35 - i5) / sr * 2
    check("reverb decay (RT60 ±3 s)", 2.0 < rt60 < 4.0, rt60_measured_s=round(rt60, 2))


def t_reproducible():
    from music.composition_engine import preset
    from music.music_studio import generate
    a = generate(preset("cinematic", duration=40, seed=5), OUT / "repro-a", stems=False)
    b = generate(preset("cinematic", duration=40, seed=5), OUT / "repro-b", stems=False)
    same = sha(OUT / "repro-a" / "music.wav") == sha(OUT / "repro-b" / "music.wav")
    # also from the saved JSON (as main.py music --config does)
    from dataclasses import fields
    from music.composition_engine import MusicConfig
    js = json.loads((OUT / "repro-a" / "config.json").read_text())["config"]
    c = generate(MusicConfig(**{f.name: js[f.name] for f in fields(MusicConfig)}), OUT / "repro-c", stems=False)
    same_json = sha(OUT / "repro-a" / "music.wav") == sha(OUT / "repro-c" / "music.wav")
    check("music reproducible (same seed, and from config.json)", same and same_json,
          a=sha(OUT / "repro-a" / "music.wav"), b=sha(OUT / "repro-b" / "music.wav"), from_json=sha(OUT / "repro-c" / "music.wav"))


SCRIPT = """Far beneath the ice of the Arctic Ocean, in the winter of 1958, a long grey submarine moves slowly through the dark. Mr. Anderson, her captain, stands quietly in the control room, watching the depth gauge and the slow sweep of the sonar.

Inside, the crew sleep in narrow bunks, three high, with a curtain and a small reading lamp each. The engines hum softly, the air smells of oil and coffee, and somewhere a radio plays very quietly. [pause]

Above them, the ice is many metres thick, and nobody has ever crossed beneath the North Pole before. If anything goes wrong down here, there is no way to come up, no open water, no sky. And yet, the men are calm. They have trained for months, they trust the boat, and they trust each other.

At eleven fifteen at night, on the third of August, the navigator looks up from his charts and says, very simply, that they are now at the top of the world."""


def t_voice():
    from voice.batch_generator import narrate
    from voice.voice_config import VoiceConfig
    from voice import omnivoice_engine as ov
    cfg = VoiceConfig()
    r = narrate(SCRIPT, cfg, OUT / "voice", name="voice")
    info = probe(OUT / "voice" / "voice.wav")
    check("voice generated", r["sentences"] >= 9 and r["duration"] > 40, sentences=r["sentences"], duration=r["duration"],
          words_per_min=r["words_per_min"], seconds=r["seconds"])
    check("voice WAV 48 kHz 24-bit + MP3", "48000 Hz" in info and (OUT / "voice" / "voice.mp3").exists(), probe=info)
    # long-script splitting: one 600-char sentence must be split at commas with the pieces in order
    from voice.script_processor import pieces
    long = "The ship sailed on, " * 30 + "and then it was quiet."
    ps = pieces(long, cfg)
    check("long sentences split", len(ps) > 1 and all(len(t) <= cfg.max_chars for t, _ in ps), pieces=len(ps))
    # same seed -> same audio?
    a = ov.speak(["The sea was calm that night."], cfg, seed=3)[0]
    b = ov.speak(["The sea was calm that night."], cfg, seed=3)[0]
    same = len(a) == len(b) and float(np.abs(a - b).max()) < 1e-3
    check("voice reproducible (same seed)", same, len_a=len(a), len_b=len(b),
          max_diff=float(np.abs(a[: min(len(a), len(b))] - b[: min(len(a), len(b))]).max()))
    # consistency: pitch of each sentence close to the others
    import librosa
    y, sr = sf.read(OUT / "voice" / "voice.wav", always_2d=True)
    y = librosa.resample(y.mean(axis=1), orig_sr=sr, target_sr=16000)
    rows = [l.split("\t") for l in (OUT / "voice" / "voice-tijden.tsv").read_text(encoding="utf-8").splitlines()[1:]]
    f0s = []
    for _, s, e, _ in rows:
        seg = y[int(float(s) * 16000): int(float(e) * 16000)]
        f0, vf, _ = librosa.pyin(seg, fmin=60, fmax=250, sr=16000)
        f0s.append(float(np.nanmedian(f0[vf])))
    check("voice consistent between sentences (pitch)", np.std(f0s) < 8, median_f0_per_sentence=[round(x) for x in f0s])
    return r


def t_whisper():
    import torch
    from transformers import pipeline
    asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", dtype=torch.float16)
    heard = asr(str(OUT / "voice" / "voice.wav"), chunk_length_s=30, batch_size=4, return_timestamps=True)["text"]
    import re
    norm = lambda s: re.sub(r"[^a-z0-9 ]", " ", s.lower().replace("mr.", "mister")).split()
    ref = norm(SCRIPT.replace("[pause]", "")); hyp = norm(heard)
    # word error rate (Levenshtein on words)
    d = np.arange(len(hyp) + 1)
    for i, w in enumerate(ref, 1):
        prev, d[0] = d.copy(), i
        for j, h in enumerate(hyp, 1):
            d[j] = min(prev[j] + 1, d[j - 1] + 1, prev[j - 1] + (w != h))
    wer = d[-1] / len(ref)
    check("voice intelligible (Whisper word error rate)", wer < 0.08, wer=round(float(wer), 3), heard=heard[:200])


def t_mix():
    from effects import volume_control as vc
    from mixer.final_mix import mix
    from mixer.voice_music_mixer import MixConfig
    r = mix(OUT / "voice" / "voice.wav", OUT / "music-referentie" / "music.wav", MixConfig(), OUT / "mix")
    pk = vc.peak_db(OUT / "mix" / "mix.wav")
    check("mix: -14 LUFS, true peak <= -1 dBTP", abs(r["result"]["lufs"] + 14) < 0.6 and r["result"]["true_peak"] <= -0.9,
          lufs=r["result"]["lufs"], true_peak=r["result"]["true_peak"], sample_peak=pk, music_gain_db=r["music_gain_db"])
    r2 = mix(OUT / "voice" / "voice.wav", OUT / "music-referentie" / "music.wav", MixConfig(ducking=False), OUT / "mix-noduck")
    check("mix: ducking on/off both work", (OUT / "mix-noduck" / "mix.wav").exists(), with_ducking=r["result"]["lufs"],
          without=r2["result"]["lufs"])


def t_long():
    from music.composition_engine import preset
    from music.music_studio import generate
    from mixer.final_mix import mix
    from mixer.voice_music_mixer import MixConfig
    t = time.time()
    r = generate(preset("referentie", duration=7200, seed=21), OUT / "long-music", stems=False)
    check("2 hours of music", r["loudness"]["true_peak"] < -0.5, seconds=round(time.time() - t), loudness=r["loudness"],
          size_mb=round((OUT / "long-music" / "music.wav").stat().st_size / 1e6))
    # 2-hour narration made by repeating the test narration, to test the mixer on long files
    v, sr = sf.read(OUT / "voice" / "voice.wav", always_2d=True)
    reps = int(np.ceil(7150 / (len(v) / sr)))
    with sf.SoundFile(OUT / "long-voice.wav", "w", sr, 2, subtype="PCM_24") as f:
        for _ in range(reps):
            f.write(v)
    t = time.time()
    m = mix(OUT / "long-voice.wav", OUT / "long-music" / "music.wav", MixConfig(), OUT / "long-mix")
    check("2-hour mix", abs(m["result"]["lufs"] + 14) < 0.6 and not m["music_looped"], seconds=round(time.time() - t),
          result=m["result"])


if __name__ == "__main__":
    steps = sys.argv[1:] or ["gpu", "432", "music", "repro", "voice", "whisper", "mix"]
    for s in steps:
        {"gpu": t_gpu, "432": t_432, "music": t_music_and_effects, "repro": t_reproducible, "voice": t_voice,
         "whisper": t_whisper, "mix": t_mix, "long": t_long}[s.lstrip("-")]()
    rep = OUT / "test-report.json"
    old = json.loads(rep.read_text()) if rep.exists() else {}
    old.update(REPORT)
    rep.write_text(json.dumps(old, indent=2, default=str))
    print(f"\n{sum(v['ok'] for v in REPORT.values())}/{len(REPORT)} geslaagd")
