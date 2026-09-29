"""Zachte deeltjes-effecten over een stuk video: as, sneeuw, gloeiende vonkjes, twinkelende sterren.

Rustig en traag, geschikt voor slaapvideo's. Werkt op een bestaand videobestand: leest
de beelden, tekent de deeltjes erover en schrijft een nieuw bestand (geluid blijft gelijk).

Gebruik:
  python3 tools/effects.py in.mp4 uit.mp4 --effect as [--van 3726 --tot 3816] [--sterkte 1.0]
  python3 tools/effects.py in.mp4 uit.mp4 --lijst stories/<map>/effecten.tsv
     (tsv met kolommen: van, tot, effect[, sterkte] — tijden in seconden; meerdere
      stukken in één keer)
Effecten: as, sneeuw, vonken, sterren. Zonder --van/--tot: de hele video.
Alleen het stuk tussen --van en --tot krijgt het effect (met 3 s in- en uitfaden);
de rest wordt ongewijzigd doorgegeven.
"""
import argparse, json, subprocess

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()

# per effect: aantal, grootte (px), snelheid (px/s, y), zijwaartse drift, kleur, dekking
PRESETS = {
    "as":     dict(n=260, size=(1.5, 4.5), vy=(18, 45), vx=(-8, 8), sway=14, color=(205, 200, 195), alpha=(0.25, 0.7), blur=True),
    "sneeuw": dict(n=320, size=(1.5, 5.0), vy=(25, 60), vx=(-10, 10), sway=18, color=(245, 248, 255), alpha=(0.35, 0.85), blur=True),
    "vonken": dict(n=70, size=(1.2, 3.0), vy=(-35, -12), vx=(-10, 10), sway=10, color=(255, 170, 80), alpha=(0.35, 0.9), blur=True, flicker=True),
    "sterren": dict(n=160, size=(0.8, 2.2), vy=(0, 0), vx=(0, 0), sway=0, color=(235, 240, 255), alpha=(0.2, 0.8), blur=True, twinkle=True, top=0.55),
}


def probe(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    import re
    w, h = map(int, re.search(r", (\d{3,5})x(\d{3,5})", out).groups())
    fps = float(re.search(r"([\d.]+) fps", out).group(1))
    return w, h, fps


def sprite(r):
    """Zacht rond vlekje (gaussisch) met straal r, waarden 0..1."""
    k = int(np.ceil(r * 3)) | 1
    y, x = np.mgrid[-k:k + 1, -k:k + 1]
    return np.exp(-(x * x + y * y) / (2 * r * r))


class Particles:
    def __init__(self, p, w, h, rng):
        self.p, self.w, self.h, self.rng = p, w, h, rng
        n = p["n"]
        self.x = rng.uniform(0, w, n)
        top = p.get("top", 1.0)
        self.y = rng.uniform(0, h * top, n)
        self.r = rng.uniform(*p["size"], n)
        self.vy = rng.uniform(*p["vy"], n) * (self.r / p["size"][1] * 0.6 + 0.4)  # grote = dichtbij = sneller
        self.vx = rng.uniform(*p["vx"], n)
        self.a = rng.uniform(*p["alpha"], n)
        self.phase = rng.uniform(0, 2 * np.pi, n)
        self.sprites = {}

    def step(self, dt, t):
        p = self.p
        self.y += self.vy * dt
        self.x += self.vx * dt + p["sway"] * np.sin(t * 0.6 + self.phase) * dt
        m = 40
        down, up = self.y > self.h + m, self.y < -m
        self.y[down] = -m; self.y[up] = self.h + m
        self.x[down | up] = self.rng.uniform(0, self.w, (down | up).sum())
        self.x %= self.w

    def draw(self, layer, t):
        p = self.p
        a = self.a.copy()
        if p.get("twinkle"):
            a *= 0.55 + 0.45 * np.sin(t * 1.3 + self.phase * 3)
        if p.get("flicker"):
            a *= 0.6 + 0.4 * np.sin(t * 5 + self.phase * 7)
        for x, y, r, al in zip(self.x, self.y, self.r, a):
            key = round(r * 2) / 2
            s = self.sprites.get(key)
            if s is None:
                s = self.sprites[key] = sprite(max(key, 0.6))
            k = s.shape[0] // 2
            xi, yi = int(x), int(y)
            x0, y0, x1, y1 = xi - k, yi - k, xi + k + 1, yi + k + 1
            sx0, sy0 = max(0, -x0), max(0, -y0)
            x0c, y0c, x1c, y1c = max(x0, 0), max(y0, 0), min(x1, self.w), min(y1, self.h)
            if x0c >= x1c or y0c >= y1c:
                continue
            patch = s[sy0:sy0 + (y1c - y0c), sx0:sx0 + (x1c - x0c)] * al
            np.maximum(layer[y0c:y1c, x0c:x1c], patch, out=layer[y0c:y1c, x0c:x1c])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--effect", choices=PRESETS)
    ap.add_argument("--lijst", help="tsv: van, tot, effect[, sterkte]")
    ap.add_argument("--van", type=float, default=0.0)
    ap.add_argument("--tot", type=float, default=None)
    ap.add_argument("--sterkte", type=float, default=1.0)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()

    w, h, fps = probe(a.inp)
    segs = []
    if a.lijst:
        import csv
        for r in csv.DictReader(open(a.lijst), delimiter="\t"):
            segs.append((float(r["van"]), float(r["tot"]), r["effect"].strip(), float(r.get("sterkte") or 1)))
    elif a.effect:
        segs.append((a.van, a.tot if a.tot is not None else float("inf"), a.effect, a.sterkte))
    else:
        ap.error("geef --effect of --lijst")
    rng = np.random.default_rng(a.seed)
    systems = []
    for van, tot, eff, sterkte in segs:
        p = dict(PRESETS[eff]); p["n"] = max(1, int(p["n"] * sterkte))
        systems.append((van, tot, Particles(p, w, h, rng), np.array(p["color"], dtype=np.float32) / 255))
    dec = subprocess.Popen([FF, "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", a.inp,
                            "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    fb = w * h * 3
    i, dt = 0, 1 / fps
    fade = 3.0
    while True:
        buf = dec.stdout.read(fb)
        if len(buf) < fb:
            break
        t = i * dt
        active = [x for x in systems if x[0] <= t <= x[1]]
        if active:
            frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
            for van, tot, parts, col in active:
                parts.step(dt, t)
                g = min(1, (t - van) / fade, (tot - t) / fade)
                layer = np.zeros((h, w), np.float32)
                parts.draw(layer, t)
                m = (layer * g)[..., None]
                frame = frame * (1 - m) + col * m          # zachte "over"-menging
            buf = (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
        enc.stdin.write(buf)
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(json.dumps({"frames": i, "stukken": len(segs), "out": a.out}))


if __name__ == "__main__":
    main()
