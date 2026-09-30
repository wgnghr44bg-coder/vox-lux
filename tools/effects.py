"""Zachte effecten over een stuk video, rustig en traag, geschikt voor slaapvideo's.

Deeltjes: as, sneeuw, vonken, sterren, stof (zwevende stofjes in het licht), vuurvliegjes.
Weer en licht: regen, mist (extra mistbank), vuur (warme flakkerende gloed van onderen +
vonkjes), kaarslicht (warm flakkerend licht op één plek), lichtstralen (zacht schuivende
zon- of maanstralen).

Werkt op een bestaand videobestand: leest de beelden, tekent het effect erover en schrijft
een nieuw bestand (geluid blijft gelijk). Lange video's gebruiken dezelfde effecten via
tools/motion.py --effecten (één renderronde samen met de motion graphics).

Gebruik:
  python3 tools/effects.py in.mp4 uit.mp4 --effect regen [--van 3726 --tot 3816] [--sterkte 1.0]
  python3 tools/effects.py in.mp4 uit.mp4 --lijst stories/<map>/effecten.tsv
     (tsv met kolommen: van, tot, effect[, sterkte[, x, y]] — tijden in seconden;
      x/y = plek van het kaarslicht of vuur, 0..1 van breedte/hoogte)
Zonder --van/--tot: de hele video. Alleen het stuk tussen --van en --tot krijgt het
effect (met 3 s in- en uitfaden); de rest wordt ongewijzigd doorgegeven.
"""
import argparse, csv, json, math, re, subprocess

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FF = imageio_ffmpeg.get_ffmpeg_exe()
FADE = 3.0

# deeltjes: aantal (bij 1920x1080), grootte (px), snelheid (px/s), zijwaartse drift, kleur, dekking
PRESETS = {
    "as":     dict(n=260, size=(1.5, 4.5), vy=(18, 45), vx=(-8, 8), sway=14, color=(205, 200, 195), alpha=(0.25, 0.7), blur=True),
    "sneeuw": dict(n=320, size=(1.5, 5.0), vy=(25, 60), vx=(-10, 10), sway=18, color=(245, 248, 255), alpha=(0.35, 0.85), blur=True),
    "vonken": dict(n=70, size=(1.2, 3.0), vy=(-35, -12), vx=(-10, 10), sway=10, color=(255, 170, 80), alpha=(0.35, 0.9), blur=True, flicker=True),
    "sterren": dict(n=160, size=(0.8, 2.2), vy=(0, 0), vx=(0, 0), sway=0, color=(235, 240, 255), alpha=(0.2, 0.8), blur=True, twinkle=True, top=0.55),
    "stof":   dict(n=170, size=(1.0, 2.6), vy=(-5, 5), vx=(-6, 6), sway=9, color=(255, 240, 210), alpha=(0.3, 0.8), blur=True, twinkle=True),
    "vuurvliegjes": dict(n=35, size=(1.8, 3.2), vy=(-8, 8), vx=(-10, 10), sway=25, color=(215, 255, 150), alpha=(0.4, 1.0), blur=True, twinkle=True, top=0.95),
}
EFFECTEN = sorted(list(PRESETS) + ["regen", "mist", "vuur", "kaarslicht", "lichtstralen"])


def probe(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r", (\d{3,5})x(\d{3,5})", out).groups())
    fps = float(re.search(r"([\d.]+) fps", out).group(1))
    return w, h, fps


def sprite(r):
    """Zacht rond vlekje (gaussisch) met straal r, waarden 0..1."""
    k = int(np.ceil(r * 3)) | 1
    y, x = np.mgrid[-k:k + 1, -k:k + 1]
    return np.exp(-(x * x + y * y) / (2 * r * r))


def mix(frame, layer, col, g):
    """Zachte "over"-menging van een kleur met dekking layer*g."""
    m = (layer * g)[..., None]
    return frame * (1 - m) + np.asarray(col, np.float32) * m


def flicker(t, seed):
    """Onregelmatig, zacht flakkeren rond 1 (vlam)."""
    return (1 + 0.10 * math.sin(t * 7.3 + seed) + 0.07 * math.sin(t * 11.1 + 2 * seed)
            + 0.05 * math.sin(t * 17.7 + 3 * seed) + 0.03 * math.sin(t * 29.3 + seed))


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


class ParticleEffect:
    def __init__(self, name, w, h, rng, sterkte):
        p = dict(PRESETS[name])
        p["n"] = max(1, int(p["n"] * sterkte * w * h / (1920 * 1080)))
        self.parts = Particles(p, w, h, rng)
        self.col = np.array(p["color"], np.float32) / 255
        self.w, self.h = w, h

    def apply(self, frame, t, dt, g):
        self.parts.step(dt, t)
        layer = np.zeros((self.h, self.w), np.float32)
        self.parts.draw(layer, t)
        return mix(frame, layer, self.col, g)


class Regen:
    """Zachte, lichte regen: dunne schuine strepen, beeld iets koeler."""

    def __init__(self, w, h, rng, sterkte):
        self.w, self.h, self.rng = w, h, rng
        n = int(260 * sterkte * w * h / (1920 * 1080))
        self.x = rng.uniform(-0.2 * w, w, n)
        self.y = rng.uniform(-h, h, n)
        self.v = rng.uniform(750, 1150, n) * h / 1080
        self.len = rng.uniform(16, 38, n) * h / 1080
        self.a = rng.uniform(70, 150, n)
        self.slant = 0.16
        self.col = np.array([0.80, 0.84, 0.90], np.float32)

    def apply(self, frame, t, dt, g):
        self.y += self.v * dt
        self.x += self.v * self.slant * dt
        out = self.y > self.h + 40
        self.y[out] = self.rng.uniform(-200, -20, out.sum())
        self.x[out] = self.rng.uniform(-0.2 * self.w, self.w, out.sum())
        im = Image.new("L", (self.w, self.h), 0)
        d = ImageDraw.Draw(im)
        for x, y, l, a in zip(self.x, self.y, self.len, self.a):
            d.line((x, y, x - l * self.slant, y - l), fill=int(a), width=2 if a > 120 else 1)
        layer = np.asarray(im, np.float32) / 255
        frame = frame * (1 - 0.07 * g) + self.col * (0.03 * g)     # grijzer, koeler licht
        return mix(frame, layer, self.col, g)


class Mistbank:
    """Extra, dikkere mist die langzaam door het beeld drijft (onderin het dichtst)."""

    def __init__(self, w, h, rng, sterkte):
        self.w, self.h = w, h
        lw, lh = 64, max(8, round(64 * h / w))
        big = []
        for sc, amp in [(1, 0.65), (3, 0.35)]:
            n = rng.random((lh * sc, lw * 2 * sc)).astype(np.float32)
            im = Image.fromarray((n * 255).astype(np.uint8)).resize((2 * w, h), Image.BICUBIC)
            big.append(np.asarray(im.filter(ImageFilter.GaussianBlur(40 / sc)), np.float32) / 255 * amp)
        n = big[0] + big[1]
        n = np.clip((n - 0.35) * 2.2, 0, 1)
        n *= (0.25 + 0.75 * np.linspace(0, 1, h) ** 1.5)[:, None]
        n = np.concatenate([n, n[:, ::-1]], 1)        # naadloos herhaalbaar
        self.tex = n
        self.alpha = 0.55 * sterkte
        self.col = np.array([0.88, 0.88, 0.90], np.float32)

    def apply(self, frame, t, dt, g):
        x = int(t * 14 * self.w / 1920) % (self.tex.shape[1] - self.w)
        return mix(frame, self.tex[:, x:x + self.w], self.col, g * self.alpha)


class Gloed:
    """Warm, flakkerend licht: kaarslicht (op één plek) of vuur (van onderen, met vonkjes)."""

    def __init__(self, soort, w, h, rng, sterkte, x=None, y=None):
        self.w, self.h = w, h
        vuur = soort == "vuur"
        cx = (0.5 if x is None else x) * w
        cy = ((1.05 if vuur else 0.6) if y is None else y) * h
        rx, ry = (0.75 * w, 0.6 * h) if vuur else (0.33 * w, 0.4 * h)
        yy, xx = np.mgrid[0:h, 0:w]
        self.mask = np.exp(-(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)).astype(np.float32)
        self.col = np.array([1.0, 0.62, 0.28] if vuur else [1.0, 0.72, 0.40], np.float32)
        self.amp = (0.55 if vuur else 0.25) * sterkte
        self.seed = rng.uniform(0, 10)
        self.sparks = ParticleEffect("vonken", w, h, rng, 0.8 * sterkte) if vuur else None

    def apply(self, frame, t, dt, g):
        f = flicker(t, self.seed)
        k = (self.mask * (self.amp * f * g))[..., None]
        frame = frame * (1 + k * 0.5 * self.col) + k * 0.25 * self.col    # warmer en lichter
        frame = frame * (1 - 0.04 * g * (f - 1))                          # hele beeld flakkert heel licht
        if self.sparks:
            frame = self.sparks.apply(frame, t, dt, g)
        return frame


class Lichtstralen:
    """Brede, zachte schuine stralen die heel langzaam opzij schuiven."""

    def __init__(self, w, h, rng, sterkte):
        self.w, self.h = w, h
        u = min(w, h) / 1080
        pad = int(600 * u)
        im = Image.new("L", (w + pad, h), 0)
        d = ImageDraw.Draw(im)
        for _ in range(7):
            x = rng.uniform(0, w + pad)
            bw = rng.uniform(40, 130) * u
            sk = h * 0.55
            d.polygon([(x, 0), (x + bw, 0), (x + bw - sk, h), (x - sk, h)], fill=int(rng.uniform(160, 255)))
        r = np.asarray(im.filter(ImageFilter.GaussianBlur(35 * u)), np.float32) / 255
        self.rays = r * np.linspace(1, 0.25, h, dtype=np.float32)[:, None]
        self.pad, self.u = pad, u
        self.alpha = 0.5 * sterkte
        self.col = np.array([1.0, 0.93, 0.78], np.float32)

    def apply(self, frame, t, dt, g):
        span = self.pad
        off = int((t * 18 * self.u) % (2 * span))
        off = off if off < span else 2 * span - off                     # heen en weer
        a = self.alpha * g * (0.8 + 0.2 * math.sin(t * 0.7))
        return mix(frame, self.rays[:, off:off + self.w], self.col, a)


def make_effect(name, w, h, rng, sterkte=1.0, x=None, y=None):
    if name in PRESETS:
        return ParticleEffect(name, w, h, rng, sterkte)
    if name == "regen":
        return Regen(w, h, rng, sterkte)
    if name == "mist":
        return Mistbank(w, h, rng, sterkte)
    if name in ("vuur", "kaarslicht"):
        return Gloed(name, w, h, rng, sterkte, x, y)
    if name == "lichtstralen":
        return Lichtstralen(w, h, rng, sterkte)
    raise SystemExit(f"onbekend effect: {name} (kies uit {', '.join(EFFECTEN)})")


def read_list(path, w, h, rng):
    """effecten.tsv -> [(van, tot, effect-object)]"""
    out = []
    for r in csv.DictReader(open(path), delimiter="\t"):
        num = lambda k: float(r[k]) if r.get(k) not in (None, "") else None  # noqa: E731
        out.append((float(r["van"]), float(r["tot"]),
                    make_effect(r["effect"].strip(), w, h, rng, num("sterkte") or 1.0, num("x"), num("y"))))
    return out


def apply_all(frame, systems, t, dt):
    """frame (float 0..1) met alle effecten die op tijd t actief zijn; None als er geen zijn."""
    act = [s for s in systems if s[0] <= t <= s[1]]
    for van, tot, eff in act:
        g = min(1, (t - van) / FADE, (tot - t) / FADE)
        frame = eff.apply(frame, t, dt, g)
    return frame, bool(act)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--effect", choices=EFFECTEN)
    ap.add_argument("--lijst", help="tsv: van, tot, effect[, sterkte[, x, y]]")
    ap.add_argument("--van", type=float, default=0.0)
    ap.add_argument("--tot", type=float, default=None)
    ap.add_argument("--sterkte", type=float, default=1.0)
    ap.add_argument("--x", type=float); ap.add_argument("--y", type=float)
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()

    w, h, fps = probe(a.inp)
    rng = np.random.default_rng(a.seed)
    if a.lijst:
        systems = read_list(a.lijst, w, h, rng)
    elif a.effect:
        systems = [(a.van, a.tot if a.tot is not None else float("inf"),
                    make_effect(a.effect, w, h, rng, a.sterkte, a.x, a.y))]
    else:
        ap.error("geef --effect of --lijst")
    dec = subprocess.Popen([FF, "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                           stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{w}x{h}", "-r", str(fps), "-i", "-", "-i", a.inp,
                            "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "24", "-pix_fmt", "yuv420p", "-c:a", "copy",
                            "-movflags", "+faststart", a.out], stdin=subprocess.PIPE)
    fb = w * h * 3
    i, dt = 0, 1 / fps
    while True:
        buf = dec.stdout.read(fb)
        if len(buf) < fb:
            break
        t = i * dt
        if any(s[0] <= t <= s[1] for s in systems):
            frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
            frame, _ = apply_all(frame, systems, t, dt)
            buf = (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()
        enc.stdin.write(buf)
        i += 1
    enc.stdin.close(); enc.wait(); dec.wait()
    print(json.dumps({"frames": i, "stukken": len(systems), "out": a.out}))


if __name__ == "__main__":
    main()
