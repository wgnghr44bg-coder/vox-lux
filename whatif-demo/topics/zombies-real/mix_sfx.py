#!/usr/bin/env python3
"""#48: put the ElevenLabs sound effects (sfx/*.mp3) on the video's timeline and remux the final mp4.

    python3 whatif-demo/topics/zombies-real/mix_sfx.py

Reads timing.json (the measured voice times), uses the same moments as scenario.js (hear, people, out, q),
mixes the effects under mix.wav (voice + engine bed) and writes zombies-real.mp4 (1080x1920) again.
"""
import json
import subprocess
from pathlib import Path

import numpy as np

D = Path(__file__).resolve().parent
SR = 44100


def load(path: Path) -> np.ndarray:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).copy()


def fade(x: np.ndarray, fin: float, fout: float) -> np.ndarray:
    n = len(x)
    a, b = min(n, int(fin * SR)), min(n, int(fout * SR))
    if a: x[:a] *= np.linspace(0, 1, a)[:, None]
    if b: x[n - b:] *= np.linspace(1, 0, b)[:, None]
    return x


def main():
    tm = json.loads((D / "timing.json").read_text())
    off = tm.get("VO_OFFSET", 1.0)
    S = lambda k: tm["lines"][k][0] + off
    Ee = lambda k: tm["lines"][k][1] + off
    H, PE, O, Q = S("hear"), S("people"), S("out"), S("q")
    T_END = Ee("q") + 2.6

    bed = load(D / "mix.wav")
    n = max(len(bed), int(T_END * SR) + SR)
    out = np.zeros((n, 2), np.float32)
    out[:len(bed)] += bed

    def place(name, t0, t1=None, db=0.0, fin=.05, fout=.3, loop=False):
        x = load(D / "sfx" / f"{name}.mp3")
        if t1 is not None:
            want = int((t1 - t0) * SR)
            if loop and len(x) < want: x = np.tile(x, (want // len(x) + 1, 1))
            x = x[:want]
        x = fade(x.copy(), fin, fout) * (10 ** (db / 20))
        i = int(t0 * SR); j = min(n, i + len(x))
        out[i:j] += x[:j - i]

    place("roomtone", 0, PE - 1.2, -20, fin=.5, fout=1, loop=True)            # the quiet room
    place("game", 0, H + 2.2, -13, fin=.3, fout=.15, loop=True)               # the game on TV, until you pause it
    place("crash", Ee("play") + .8, db=-7)                                    # something outside
    place("controller", H + 2.6, db=-9)
    place("alarm", H + 3.6, H + 9.5, -15, fin=.4, fout=1.5)                   # a second sound, far away
    place("steps_in", H + 4.4, PE - 1.0, -15)
    place("window", PE - 1.4, db=-14)                                         # balcony door
    place("balcony", PE - 1.0, PE + 5.8, -6, fin=.6, fout=1.2, loop=True)     # the crowd below
    place("roomtone", PE + 5.6, O + 2.2, -20, fin=.5, fout=.5, loop=True)
    place("steps_in", PE + 5.8, PE + 9.6, -16)                                # slowly to your door
    place("scratch", PE + 6.0, PE + 10.2, -13, fin=1.5, fout=.2, loop=True)   # scratching, louder as you come closer
    place("scratch", PE + 10.2, O + 2.0, -6, fin=.05, fout=1.0, loop=True)
    place("groans", PE + 8.4, O + 2.0, -10, fin=1.0, fout=1.0, loop=True)
    place("sting", PE + 10.35, db=-1)                                         # the peephole
    place("window", O + 1.9, db=-6)                                           # out through the side window
    place("firestairs", O + 2.6, Q - .5, -5, fin=.2, fout=.3, loop=True)      # down the fire escape
    place("landing", Q - .55, db=-5)
    place("alley", Q + .2, T_END, -5, fin=.3, fout=.6, loop=True)             # the snowy alley, running

    peak = np.abs(out).max()
    if peak > .98: out *= .98 / peak
    wav = D / "mix-sfx.wav"
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-",
                    "-af", "loudnorm=I=-14:TP=-1:LRA=11", "-ar", str(SR), str(wav)], input=out.tobytes(), check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(D / "silent.mp4"), "-i", str(wav),
                    "-vf", "scale=1080:1920:flags=lanczos", "-c:v", "libx264", "-preset", "slow", "-crf", "19", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", str(D / "zombies-real.mp4")], check=True)
    print("ready:", D / "zombies-real.mp4")


if __name__ == "__main__":
    main()
