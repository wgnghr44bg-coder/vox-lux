"""16mm-documentairelook (jaren 60/70) over een hele video, snel via ffmpeg (eigenaar 3 nov 2026: "die proef
video wel heel mooi en past ook echt erbij", zonder de rode lichtvlek; op tv, iPhone en tablet vloeiend).

Warme vale kleuren, zacht contrast (zwart iets opgetild), fijne zachte korrel, donkere randen met ronde hoeken,
heel licht flikkeren en af en toe een stofje. Geen krassen, geen lichtvlek, geen trillen: de beweging blijft gelijk.
Geluid wordt ongewijzigd gekopieerd.

Gebruik: python tools/film16.py in.mp4 uit.mp4
In de montage: na tools/eind_volume.py (<map>-14.mp4 -> <map>-16mm.mp4), daarna qc_video.py op het 16mm-bestand.
"""
import subprocess, sys, tempfile
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 30


def masker(pad):
    """Vignet met ronde, donkere filmhoeken (zoals een projectievenster)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    v = np.clip(1.05 - 0.38 * (nx ** 2 + ny ** 2) ** 1.3, 0.3, 1)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([10, 8, W - 10, H - 8], radius=70, fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    Image.fromarray((np.clip(v * (0.08 + 0.92 * m), 0, 1) * 255).astype(np.uint8)).convert("RGB").save(pad)


def stof(pad, sec=12):
    """Lus van een paar seconden met af en toe een klein licht stofje op zwart (wordt er 'opgeteld')."""
    rng = np.random.default_rng(16)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(pad)],
                         stdin=subprocess.PIPE)
    for _ in range(sec * FPS):
        f = np.zeros((H, W), np.uint8)
        for _ in range(rng.poisson(1.2)):
            x, y, s = int(rng.uniform(0, W)), int(rng.uniform(0, H)), int(rng.integers(1, 3))
            f[max(0, y - s):y + s + 1, max(0, x - s):x + s + 1] = int(rng.uniform(40, 90))
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("stof-lus mislukt")


def main():
    inp, out = Path(sys.argv[1]), Path(sys.argv[2])
    # kleur: 22 % grijs erdoor (vaal), dan warm (r 1.06, g 0.99, b 0.84)
    a, g = 0.78, 0.22 * np.array([0.30, 0.59, 0.11])
    rij = lambda i, k: " ".join(f"{k * ((a if j == i else 0) + g[j]):.4f}" for j in range(3))
    r, gg, b = rij(0, 1.06).split(), rij(1, 0.99).split(), rij(2, 0.84).split()
    mixer = (f"colorchannelmixer=rr={r[0]}:rg={r[1]}:rb={r[2]}:gr={gg[0]}:gg={gg[1]}:gb={gg[2]}"
             f":br={b[0]}:bg={b[1]}:bb={b[2]}")
    with tempfile.TemporaryDirectory() as tmp:
        mpad, spad = Path(tmp) / "masker.png", Path(tmp) / "stof.mp4"
        masker(mpad); stof(spad)
        fc = (f"[0:v]format=rgb24,{mixer},lutrgb=r='val*0.88+18':g='val*0.88+18':b='val*0.88+18',"
              "eq=brightness='0.006*sin(n*0.9)':eval=frame,"           # heel licht flikkeren
              "noise=c0s=10:c0f=t+u[k];"                                 # fijne korrel (alleen helderheid)
              "[k]format=gbrp[k2];[1:v]format=gbrp[m];[k2][m]blend=all_mode=multiply[v];"
              "[2:v]format=gbrp[s];[v][s]blend=all_mode=addition,format=yuv420p[uit]")
        cmd = [FF, "-v", "error", "-y", "-i", str(inp), "-loop", "1", "-framerate", str(FPS), "-i", str(mpad),
               "-stream_loop", "-1", "-i", str(spad), "-filter_complex", fc, "-map", "[uit]", "-map", "0:a?",
               "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "copy",
               "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)
    print(f"16mm-look -> {out}")


if __name__ == "__main__":
    main()
