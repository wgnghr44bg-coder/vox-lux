"""Gratis bewegende effectlagen voor Alteraqon-shots (geen API, alles lokaal getekend).

Gebruik (normaal via make_video.py, 6e veld in een shot):  python3 fx.py <effect> <seconden> <uit.mov>
Effecten (combineren met +, bijv. "embers+ash"):
  embers  gloeiende vonken die opstijgen en flakkeren (vuur, lava)
  ash     grijze asvlokken die langzaam vallen en zwaaien
  dust    fijne lichte stofjes die zweven (binnen, mist)
  rain    schuine regenstrepen
Schrijft een transparante laag (1080x1920, 30 fps, qtrle .mov) die over het beeld wordt gelegd.
"""
import subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H, FPS, K = 540, 960, 30, 2          # tekenen op halve maat, ffmpeg schaalt op naar 1080x1920


def particles(kind, n, rng):
    if kind == "embers":
        return dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), vx=rng.normal(0, 12, n), vy=-rng.uniform(40, 140, n),
                    r=rng.uniform(1.0, 3.2, n), ph=rng.uniform(0, 6.3, n))
    if kind == "ash":
        return dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), vx=rng.normal(8, 6, n), vy=rng.uniform(20, 60, n),
                    r=rng.uniform(1.2, 3.8, n), ph=rng.uniform(0, 6.3, n))
    if kind == "dust":
        return dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), vx=rng.normal(3, 4, n), vy=rng.normal(-2, 4, n),
                    r=rng.uniform(0.6, 1.6, n), ph=rng.uniform(0, 6.3, n))
    if kind == "rain":
        return dict(x=rng.uniform(0, W, n), y=rng.uniform(0, H, n), vx=np.full(n, -120.0), vy=rng.uniform(900, 1300, n),
                    r=rng.uniform(0.6, 1.2, n), ph=np.zeros(n))
    raise SystemExit(f"onbekend effect: {kind}")


COUNT = {"embers": 190, "ash": 220, "dust": 160, "rain": 260}


def frame(t, layers):
    sharp = Image.new("RGBA", (W, H)); glow = Image.new("RGBA", (W, H))
    ds, dg = ImageDraw.Draw(sharp), ImageDraw.Draw(glow)
    for kind, p in layers:
        x = (p["x"] + p["vx"] * t) % W
        y = (p["y"] + p["vy"] * t) % H
        if kind == "ash":
            x = (x + 10 * np.sin(t * 1.3 + p["ph"])) % W
        for i in range(len(x)):
            r = p["r"][i]
            if kind == "embers":
                a = int(255 * (0.55 + 0.45 * np.sin(t * 9 + p["ph"][i])))
                col = (255, 150 + int(70 * (r / 3.2)), 60, a)
                dg.ellipse((x[i] - r * 4, y[i] - r * 4, x[i] + r * 4, y[i] + r * 4), fill=(255, 110, 30, a // 2))
                ds.ellipse((x[i] - r, y[i] - r, x[i] + r, y[i] + r), fill=col)
            elif kind == "ash":
                ds.ellipse((x[i] - r, y[i] - r * 0.7, x[i] + r, y[i] + r * 0.7), fill=(95, 90, 86, 200))
            elif kind == "dust":
                a = int(120 * (0.5 + 0.5 * np.sin(t * 2 + p["ph"][i])))
                ds.ellipse((x[i] - r, y[i] - r, x[i] + r, y[i] + r), fill=(235, 230, 220, a))
            elif kind == "rain":
                ds.line((x[i], y[i], x[i] - 4, y[i] + 26), fill=(200, 210, 230, 90), width=1)
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    sharp = sharp.filter(ImageFilter.GaussianBlur(0.6))
    return Image.alpha_composite(glow, sharp)


def main():
    kinds, dur, out = sys.argv[1].split("+"), float(sys.argv[2]), sys.argv[3]
    rng = np.random.default_rng(7)
    layers = [(k, particles(k, COUNT[k], rng)) for k in kinds]
    n = round(dur * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                           "-i", "-", "-vf", f"scale={W*K}:{H*K}", "-c:v", "qtrle", out], stdin=subprocess.PIPE)
    for f in range(n):
        ff.stdin.write(frame(f / FPS, layers).tobytes())
    ff.stdin.close(); ff.wait()


if __name__ == "__main__":
    main()
