"""Audio Engine: local documentary narration (OmniVoice) + 432 Hz music (Python) + mix (FFmpeg).

  python main.py ui                                   # interface on http://127.0.0.1:7865
  python main.py voice script.txt [--out map] [--speed 0.64] [--voice narrator-b]
  python main.py music --minutes 120 [--preset referentie|cinematic] [--seed 7] [--key A] [--no-stems]
  python main.py mix stem.wav [muziek.wav] [--below 11] [--no-ducking]     # without music: made to length
  python main.py music --config output/music/<map>/config.json            # same music again
"""
import argparse
import json
import sys
import time
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "output"


def out_dir(kind, given):
    if given:
        return Path(given)
    d = OUT / kind / time.strftime("%Y%m%d-%H%M%S")
    d.mkdir(parents=True, exist_ok=True)
    return d


def show(f, m=""):
    print(f"\r{f * 100:5.1f}% {m:<40}", end="", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ui").add_argument("--port", type=int, default=7865)
    v = sub.add_parser("voice")
    v.add_argument("script"); v.add_argument("--out"); v.add_argument("--voice", default="narrator-b")
    v.add_argument("--speed", type=float, default=0.64); v.add_argument("--seed", type=int, default=7)
    m = sub.add_parser("music")
    m.add_argument("--minutes", type=float, default=2.0); m.add_argument("--preset", default="referentie")
    m.add_argument("--seed", type=int, default=7); m.add_argument("--key", default="A"); m.add_argument("--out")
    m.add_argument("--no-stems", action="store_true"); m.add_argument("--config")
    x = sub.add_parser("mix")
    x.add_argument("voice"); x.add_argument("music", nargs="?"); x.add_argument("--out")
    x.add_argument("--below", type=float, default=11.0); x.add_argument("--no-ducking", action="store_true")
    x.add_argument("--preset", default="referentie")
    a = ap.parse_args()

    if a.cmd == "ui":
        from interface.app import launch
        launch(a.port)
    elif a.cmd == "voice":
        from voice.batch_generator import narrate
        from voice.voice_config import VoiceConfig
        r = narrate(Path(a.script).read_text(encoding="utf-8"), VoiceConfig(voice=a.voice, speed=a.speed, seed=a.seed),
                    out_dir("voice", a.out), show)
        print("\n", {k: r[k] for k in ("sentences", "words", "duration", "words_per_min", "seconds")})
    elif a.cmd == "music":
        from music.composition_engine import MusicConfig, preset
        from music.music_studio import generate
        if a.config:
            js = json.loads(Path(a.config).read_text(encoding="utf-8"))["config"]
            cfg = MusicConfig(**{f.name: js[f.name] for f in fields(MusicConfig) if f.name in js})
        else:
            cfg = preset(a.preset, duration=a.minutes * 60, seed=a.seed, key=a.key)
        r = generate(cfg, out_dir("music", a.out), stems=False if a.no_stems else None, progress=show)
        print("\n", r["loudness"], f"{r['seconds']} s")
    elif a.cmd == "mix":
        import soundfile as sf
        from mixer.final_mix import mix
        from mixer.voice_music_mixer import MixConfig
        from music.composition_engine import preset
        from music.music_studio import generate
        d = out_dir("mix", a.out)
        music = a.music
        if not music:
            generate(preset(a.preset, duration=sf.info(a.voice).duration + 6), d / "music", stems=False, progress=show)
            music = d / "music" / "music.wav"
        r = mix(a.voice, music, MixConfig(music_below_voice_db=a.below, ducking=not a.no_ducking), d, progress=show)
        print("\n", r["result"])


if __name__ == "__main__":
    main()
