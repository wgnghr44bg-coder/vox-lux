"""Rustige motion graphics over een sleep documentary, plus (optioneel) de zachte effecten.

Eén renderronde: leest de video, tekent intro, hoofdstuktitels, datumkaartjes, oude kaart met
route, citaat, tijdlijn en afsluiting erover, en schrijft een nieuw bestand (geluid blijft gelijk).
Werkt voor 16:9 (lange video) en 9:16 (Shorts). Gratis, geen xAI.

Gebruik:
  python3 tools/motion.py in.mp4 uit.mp4 --plan stories/<map>/motion.json \
      [--effecten stories/<map>/effecten.tsv]
  python3 tools/motion.py in.mp4 proef.png --plan ... --proef 812.5   (één beeld, om na te kijken)

motion.json (tijden in seconden in de video, dus mét de extra pauzes):
{
  "onderwerp": "Pompeii: The Last Day",        # onder SLEEP ARCHIVES in de intro
  "intro": true,                               # eerste 9 s: sterren, maan, naam, onderwerp
  "slot": true,                                # laatste 14 s: Goodnight / Sleep well
  "items": [
    {"soort": "hoofdstuk", "tijd": 787, "nummer": 2, "titel": "Painted Houses and Gardens"},
    {"soort": "datum", "tijd": 1990, "regel1": "24 August, 79 AD  ·  Midday",
     "regel2": "Misenum, Bay of Naples"},
    {"soort": "kaart", "tijd": 3800, "titel": "The Bay of Naples, 79 AD",
     "gebied": [13.9, 14.62, 40.49, 40.92],          # lon_min, lon_max, lat_min, lat_max
     "plaatsen": [{"naam": "Misenum", "lon": 14.085, "lat": 40.785, "kant": "links"},
                  {"naam": "Vesuvius", "lon": 14.426, "lat": 40.821, "berg": true, "rook": true}],
     "route": [[14.09, 40.775], [14.30, 40.725], [14.47, 40.703]]},
    {"soort": "citaat", "tijd": 3300, "tekst": "A cloud of unusual size and appearance was rising from a mountain…",
     "bron": "Pliny the Younger, letter to Tacitus"},
    {"soort": "tijdlijn", "tijd": 7000, "punten": [["79 AD", "Buried by Vesuvius"], ["1748", "Rediscovered"], ["Today", "Walking the streets again"]]}
  ]
}
kant = rechts (standaard) / links / boven / onder: waar de naam naast de stip staat.
Duur: hoofdstuk 7 s, datum 8 s, kaart 16 s, citaat ± 9-12 s, tijdlijn 9 s.
De kustlijnen komen uit Natural Earth (publiek domein); de eerste keer wordt
ne_10m_land.geojson (10 MB) gedownload naar tools/.cache/.
"""
import argparse, csv, json, math, re, subprocess, sys, urllib.request
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from effects import PRESETS, Particles  # noqa: E402

FF = imageio_ffmpeg.get_ffmpeg_exe()
ROOT = Path(__file__).resolve().parent.parent
LIB = "/usr/share/fonts/truetype/liberation/"
FB, FR, FI = LIB + "LiberationSerif-Bold.ttf", LIB + "LiberationSerif-Regular.ttf", LIB + "LiberationSerif-Italic.ttf"
CREAM = np.array([245, 238, 222], np.float32) / 255
INK = (0.30, 0.20, 0.12)
LAND_URL = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_land.geojson"
DUUR = {"hoofdstuk": 7.0, "datum": 8.0, "kaart": 16.0, "tijdlijn": 9.0}
INTRO, SLOT = 9.0, 14.0


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def fade(t, a, b, fi=1.2, fo=1.2):
    return min(ease((t - a) / fi), ease((b - t) / fo))


def roman(n):
    out = ""
    for v, s in [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]:
        while n >= v:
            out, n = out + s, n - v
    return out


def over(frame, m, col, a):
    if a <= 0.002:
        return frame
    mm = (m * a)[..., None]
    return frame * (1 - mm) + np.asarray(col, np.float32) * mm


class Canvas:
    """Maakt maskers en lettertypes voor één beeldformaat."""

    def __init__(self, w, h):
        self.W, self.H = w, h
        self.U = min(w, h) / 1080
        self.vert = h > w

    def font(self, path, size, text=None, maxw=None):
        size = int(size * self.U)
        f = ImageFont.truetype(path, size)
        while text and maxw and f.getlength(text) > maxw and size > 10:
            size -= 2
            f = ImageFont.truetype(path, size)
        return f

    def mask(self, fn, blur=0):
        m = Image.new("L", (self.W, self.H), 0)
        fn(ImageDraw.Draw(m))
        if blur:
            m = m.filter(ImageFilter.GaussianBlur(blur))
        return np.asarray(m, np.float32) / 255

    def text(self, fn, glow=0, shadow=0):
        return (self.mask(fn), self.mask(fn, glow) if glow else None, self.mask(fn, shadow) if shadow else None)


def put_text(frame, layer, a, col=CREAM, glow_col=(0.66, 0.75, 0.94), glow_a=0.6, shadow_a=0.75):
    t, g, s = layer
    if s is not None:
        frame = over(frame, np.clip(s * 2.5, 0, 1), (0, 0, 0), a * shadow_a)
    if g is not None:
        frame = over(frame, np.clip(g * 1.5, 0, 1), glow_col, a * glow_a)
    return over(frame, t, col, a)


def wrap(font, text, maxw):
    lines, cur = [], ""
    for w in text.split():
        test = f"{cur} {w}".strip()
        if font.getlength(test) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


# ---------------- onderdelen ----------------
class Sky:
    """Sterrenhemel + maan (intro en slot)."""

    def __init__(self, c, rng):
        self.c = c
        W, H, U = c.W, c.H, c.U
        n = int(500 * W * H / (1920 * 1080))
        self.stars = [(rng.uniform(0, W), rng.uniform(0, H), rng.uniform(0.6, 2.2) * max(U, 0.8),
                       rng.uniform(0, 6.28), rng.uniform(0, 3)) for _ in range(n)]
        moon = Image.open(ROOT / "branding" / "profielfoto-zwart.png").convert("RGB").crop((320, 90, 490, 260))
        self.ms = int(260 * U)
        self.moon = np.asarray(moon.resize((self.ms, self.ms), Image.LANCZOS), np.float32) / 255
        self.moon_a = np.clip((self.moon.mean(2) * 255 - 70) / 80, 0, 1)
        self.y = int(H * (0.30 if c.vert else 0.24))
        self.glow = c.mask(lambda d: d.ellipse((W / 2 - 200 * U, self.y - 200 * U, W / 2 + 200 * U, self.y + 200 * U), fill=70), 90 * U)

    def stars_frame(self, t):
        im = Image.new("RGB", (self.c.W, self.c.H), (4, 5, 10))
        d = ImageDraw.Draw(im)
        for x, y, r, ph, delay in self.stars:
            a = ease((t - delay * 0.6) / 1.5) * (0.55 + 0.45 * math.sin(t * 1.5 + ph))
            if a > 0.02:
                v = int(230 * a)
                d.ellipse((x - r, y - r, x + r, y + r), fill=(v, v, min(255, int(v * 1.05))))
        return np.asarray(im, np.float32) / 255

    def moon_on(self, frame, a, dy=0):
        if a <= 0.002:
            return frame
        frame = over(frame, np.roll(self.glow, dy, 0) if dy else self.glow, (0.63, 0.7, 0.9), a)
        x0, y0 = self.c.W // 2 - self.ms // 2, self.y - self.ms // 2 + dy
        m = (self.moon_a * a)[..., None]
        sub = frame[y0:y0 + self.ms, x0:x0 + self.ms]
        frame[y0:y0 + self.ms, x0:x0 + self.ms] = sub * (1 - m) + self.moon * m
        return frame


class Intro:
    def __init__(self, c, sky, onderwerp):
        self.sky = sky
        W, U = c.W, c.U
        ty = sky.y + int(250 * U)
        fn = c.font(FB, 150, "SLEEP ARCHIVES", W * 0.86)
        fs = c.font(FR, 46, onderwerp, W * 0.86)
        self.name = c.text(lambda d: d.text((W / 2, ty), "SLEEP ARCHIVES", font=fn, fill=255, anchor="mm"), glow=18 * U)
        self.sub = c.text(lambda d: d.text((W / 2, ty + 120 * U), onderwerp, font=fs, fill=255, anchor="mm"))
        self.a, self.b = 0.0, INTRO

    def draw(self, frame, t):
        sky = self.sky.stars_frame(t)
        sky = self.sky.moon_on(sky, ease((t - 1.0) / 2))
        sky = put_text(sky, self.name, ease((t - 2.4) / 1.8))
        sky = put_text(sky, self.sub, ease((t - 4.0) / 1.5), glow_a=0)
        k = ease((INTRO - t) / 2.0)          # laatste 2 s: sterren wijken voor het eerste beeld
        return frame * (1 - k) + sky * k


class Slot:
    def __init__(self, c, sky, einde):
        self.sky, self.c = sky, c
        W, H, U = c.W, c.H, c.U
        gy = sky.y + int(230 * U)
        fg = c.font(FB, 110, "Goodnight", W * 0.8)
        fs = c.font(FI, 44)
        fu = c.font(FR, 38, "Subscribe for more quiet stories", W * 0.8)
        self.gn = c.text(lambda d: d.text((W / 2, gy), "Goodnight", font=fg, fill=255, anchor="mm"), glow=16 * U)
        self.sl = c.text(lambda d: d.text((W / 2, gy + 95 * U), "Sleep well", font=fs, fill=255, anchor="mm"))
        self.sub = c.text(lambda d: d.text((W / 2, H * (0.78 if c.vert else 0.88)), "Subscribe for more quiet stories", font=fu, fill=255, anchor="mm"))
        self.a, self.b = einde - SLOT, einde + 1

    def draw(self, frame, t):
        k = ease(t / 2.5)
        sky = self.sky.stars_frame(t + 20)
        sky = self.sky.moon_on(sky, ease((t - 2.0) / 1.5), dy=-int(20 * self.c.U * ease((t - 2) / 6)))
        sky = put_text(sky, self.gn, ease((t - 3.0) / 1.5))
        sky = put_text(sky, self.sl, ease((t - 4.2) / 1.5), glow_a=0)
        sky = put_text(sky, self.sub, 0.85 * ease((t - 5.5) / 1.5), glow_a=0)
        return (frame * (1 - k) + sky * k) * ease((SLOT - t) / 1.5)


class Hoofdstuk:
    def __init__(self, c, it):
        W, H, U = c.W, c.H, c.U
        f1 = c.font(FR, 38)
        titel = it["titel"]
        f2 = c.font(FB, 86, titel, W * 0.86)
        y = H * 0.45
        label = f"CHAPTER  {roman(int(it['nummer']))}" if it.get("nummer") else ""
        self.l = c.text(lambda d: (d.text((W / 2, y - 70 * U), label, font=f1, fill=255, anchor="mm"),
                                   d.text((W / 2, y + 15 * U), titel, font=f2, fill=255, anchor="mm"),
                                   d.line((W / 2 - 160 * U, y + 85 * U, W / 2 + 160 * U, y + 85 * U), fill=200, width=max(2, int(2 * U)))),
                        shadow=10 * U)
        self.a, self.b = it["tijd"], it["tijd"] + it.get("duur", DUUR["hoofdstuk"])

    def draw(self, frame, t):
        a = fade(t, 0, self.b - self.a, 1.5, 1.5)
        return put_text(frame * (1 - 0.4 * a), self.l, a)


class Datum:
    def __init__(self, c, it):
        W, H, U = c.W, c.H, c.U
        r1, r2 = it["regel1"], it.get("regel2", "")
        f1 = c.font(FI, 46, r1, W * 0.8)
        f2 = c.font(FR, 38, r2, W * 0.8)
        x, y = (W * 0.0625, H * 0.815) if not c.vert else (W * 0.08, H * 0.70)
        self.l = c.text(lambda d: (d.line((x, y - 10 * U, x, y + (90 if r2 else 50) * U), fill=220, width=max(3, int(3 * U))),
                                   d.text((x + 30 * U, y), r1, font=f1, fill=255),
                                   d.text((x + 30 * U, y + 52 * U), r2, font=f2, fill=205)), shadow=6 * U)
        self.a, self.b = it["tijd"], it["tijd"] + it.get("duur", DUUR["datum"])

    def draw(self, frame, t):
        return put_text(frame, self.l, fade(t, 0.3, self.b - self.a, 1.3, 1.2))


class Citaat:
    def __init__(self, c, it):
        W, H, U = c.W, c.H, c.U
        self.c = c
        maxw = W * (0.84 if c.vert else 0.70)
        fq = c.font(FI, 70 if c.vert else 64)
        lines = wrap(fq, "“" + it["tekst"].strip("\"“” ") + "”", maxw)
        fa = c.font(FR, 36, "—  " + it.get("bron", ""), maxw)
        lh = fq.size * 1.3
        y0 = H * 0.42 - (len(lines) - 1) * lh / 2
        self.lines = [c.mask(lambda d, s=s, i=i: d.text((W / 2, y0 + i * lh), s, font=fq, fill=255, anchor="mm")) for i, s in enumerate(lines)]
        self.shadow = c.mask(lambda d: [d.text((W / 2, y0 + i * lh), s, font=fq, fill=255, anchor="mm") for i, s in enumerate(lines)], 10 * U)
        self.auth = c.mask(lambda d: d.text((W / 2, y0 + len(lines) * lh + 30 * U), "—  " + it.get("bron", ""), font=fa, fill=255, anchor="mm")) if it.get("bron") else None
        self.ext = []
        for m in self.lines:
            cols = np.where(m.max(0) > 0.05)[0]
            self.ext.append((cols.min(), cols.max()) if len(cols) else (0, W))
        self.xx = np.arange(W, dtype=np.float32)[None, :]
        self.per = 2.2
        dur = it.get("duur", 1.0 + self.per * len(lines) + 1.5 + 4.0)
        self.a, self.b = it["tijd"], it["tijd"] + dur

    def draw(self, frame, t):
        U = self.c.U
        a = fade(t, 0, self.b - self.a, 1.2, 1.2)
        frame = over(frame * (1 - 0.45 * a), np.clip(self.shadow * 2, 0, 1), (0, 0, 0), 0.6 * a)
        for i, (m, (x0, x1)) in enumerate(zip(self.lines, self.ext)):
            p = (t - 1.0 - i * self.per) / self.per
            if p > 0:
                edge = x0 + (x1 - x0 + 60 * U) * min(p, 1)
                frame = over(frame, m * np.clip((edge - self.xx) / (60 * U), 0, 1), CREAM, a)
        if self.auth is not None:
            frame = over(frame, self.auth, (0.85, 0.8, 0.7), a * ease((t - 1.0 - len(self.lines) * self.per) / 1.2))
        return frame


class Tijdlijn:
    def __init__(self, c, it):
        W, H, U = c.W, c.H, c.U
        self.c = c
        pts = it["punten"]
        fy = c.font(FB, 54)
        self.y = y = H * (0.62 if c.vert else 0.72)
        self.x0, self.x1 = W * 0.15, W * 0.85
        n = len(pts)
        self.xs = [self.x0 + (self.x1 - self.x0) * i / max(n - 1, 1) for i in range(n)]
        maxw = (self.x1 - self.x0) / max(n - 1, 1) * 0.9
        self.line = c.mask(lambda d: d.line((self.x0, y, self.x1, y), fill=255, width=max(3, int(3 * U))))
        self.nodes = []
        for x, (jaar, label) in zip(self.xs, pts):
            fl = c.font(FI, 32, label, maxw)
            self.nodes.append(c.mask(lambda d, x=x, j=jaar, l=label, fl=fl: (
                d.ellipse((x - 11 * U, y - 11 * U, x + 11 * U, y + 11 * U), fill=255),
                d.text((x, y - 30 * U), j, font=fy, fill=255, anchor="mb"),
                d.text((x, y + 30 * U), l, font=fl, fill=255, anchor="mt"))))
        self.band = c.mask(lambda d: d.rectangle((0, y - 120 * U, W, y + 110 * U), fill=255), 60 * U)
        self.xx = np.arange(W, dtype=np.float32)[None, :]
        self.a, self.b = it["tijd"], it["tijd"] + it.get("duur", DUUR["tijdlijn"])

    def draw(self, frame, t):
        U = self.c.U
        a = fade(t, 0, self.b - self.a, 1.0, 1.0)
        frame = over(frame, self.band, (0, 0, 0), 0.55 * a)
        edge = self.x0 + (self.x1 - self.x0) * ease((t - 1.0) / 4.5)
        frame = over(frame, self.line * np.clip((edge - self.xx) / (10 * U), 0, 1), CREAM, 0.9 * a)
        for m, x in zip(self.nodes, self.xs):
            frame = over(frame, m, CREAM, a * ease((edge - x + 20 * U) / (60 * U)))
        return frame


_LAND = None


def land_polygons():
    global _LAND
    if _LAND is None:
        cache = Path(__file__).parent / ".cache" / "ne_10m_land.geojson"
        if not cache.exists():
            cache.parent.mkdir(exist_ok=True)
            print("kustlijnen downloaden (Natural Earth, 10 MB)...", flush=True)
            tmp = cache.with_suffix(".part")
            urllib.request.urlretrieve(LAND_URL, tmp)
            tmp.replace(cache)
        polys = []
        for f in json.load(open(cache))["features"]:
            g = f["geometry"]
            for poly in (g["coordinates"] if g["type"] == "MultiPolygon" else [g["coordinates"]]):
                ring = np.array(poly[0], np.float64)
                polys.append((ring[:, 0].min(), ring[:, 0].max(), ring[:, 1].min(), ring[:, 1].max(), ring))
        _LAND = polys
    return _LAND


class Kaart:
    def __init__(self, c, it, rng):
        W, H, U = c.W, c.H, c.U
        self.c = c
        lon0, lon1, lat0, lat1 = it["gebied"]
        coslat = math.cos(math.radians((lat0 + lat1) / 2))
        # gebied past binnen 80 % (liggend) / 88 % (staand) van het beeld; de kaart vult het hele beeld
        bw, bh = W * (0.88 if c.vert else 0.80), H * 0.72
        s = min(bw / ((lon1 - lon0) * coslat), bh / (lat1 - lat0))
        cx, cy = (lon0 + lon1) / 2, (lat0 + lat1) / 2
        oy = H * 0.04

        def P(lon, lat):
            return (W / 2 + (lon - cx) * coslat * s, H / 2 + oy - (lat - cy) * s)
        self.P = P
        # zichtbaar gebied in graden (voor het selecteren van land)
        vl0, vl1 = cx - W / 2 / (coslat * s), cx + W / 2 / (coslat * s)
        va0, va1 = cy - (H / 2 + oy) / s, cy + (H / 2 - oy) / s
        self.parch = self.parchment(rng)
        land_img, coast_img = Image.new("L", (W, H), 0), Image.new("L", (W, H), 0)
        dl, dc = ImageDraw.Draw(land_img), ImageDraw.Draw(coast_img)
        lw = max(2, int(3 * U))
        for x0, x1, y0, y1, ring in land_polygons():
            if x1 < vl0 or x0 > vl1 or y1 < va0 or y0 > va1:
                continue
            pts = [P(x, y) for x, y in ring]
            if len(pts) > 2:
                dl.polygon(pts, fill=255)
                dc.line(pts + [pts[0]], fill=255, width=lw, joint="curve")
        self.land = np.asarray(land_img.filter(ImageFilter.GaussianBlur(1.2)), np.float32) / 255
        self.coast = np.asarray(coast_img.filter(ImageFilter.GaussianBlur(0.8)), np.float32) / 255
        waves = Image.new("L", (W, H), 0)
        dw = ImageDraw.Draw(waves)
        for _ in range(int(90 * W * H / (1920 * 1080))):
            x, y = rng.uniform(0, W), rng.uniform(0, H)
            sz = 14 * U
            dw.arc((x - sz, y - sz / 2, x, y + sz / 2), 200, 340, fill=150, width=max(1, int(2 * U)))
            dw.arc((x, y - sz / 2, x + sz, y + sz / 2), 200, 340, fill=150, width=max(1, int(2 * U)))
        self.waves = np.asarray(waves, np.float32) / 255 * (1 - np.clip(self.land * 1.5, 0, 1))
        ft = c.font(FB, 56, it.get("titel", ""), W * 0.86)
        ty = H * (0.14 if c.vert else 0.09)
        self.title = c.mask(lambda d: d.text((W / 2, ty), it.get("titel", ""), font=ft, fill=255, anchor="mm"))
        fl = c.font(FI, 34)
        self.labels, self.bergen, self.rook = [], [], []
        for i, p in enumerate(it.get("plaatsen", [])):
            x, y = P(p["lon"], p["lat"])
            kant = p.get("kant", "rechts")
            berg = p.get("berg")

            def dr(d, x=x, y=y, n=p["naam"], kant=kant, berg=berg):
                if berg:
                    d.polygon([(x - 60 * U, y + 30 * U), (x - 12 * U, y - 40 * U), (x + 12 * U, y - 40 * U), (x + 60 * U, y + 30 * U)],
                              outline=255, width=max(3, int(3 * U)))
                    g = 70 * U
                else:
                    d.ellipse((x - 6 * U, y - 6 * U, x + 6 * U, y + 6 * U), fill=255)
                    g = 16 * U
                if kant == "links":
                    d.text((x - g, y), n, font=fl, fill=255, anchor="rm")
                elif kant == "boven":
                    d.text((x, y - (50 if berg else 16) * U), n, font=fl, fill=255, anchor="mb")
                elif kant == "onder":
                    d.text((x, y + (40 if berg else 16) * U), n, font=fl, fill=255, anchor="mt")
                else:
                    d.text((x + g, y), n, font=fl, fill=255, anchor="lm")
            self.labels.append((c.mask(dr), 1.0 + 0.4 * i))
            if p.get("rook"):
                self.rook.append(c.mask(lambda d, x=x, y=y: [d.ellipse((x + o * U - r * U, y - 60 * U - h * U - r * U, x + o * U + r * U, y - 60 * U - h * U + r * U), fill=255)
                                                             for r, h, o in [(18, 0, 0), (26, 30, 8), (34, 66, 18), (42, 108, 30)]], 8 * U))
        self.route = []
        pts = [P(lon, lat) for lon, lat in it.get("route", [])]
        for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
            n = int(math.hypot(x1 - x0, y1 - y0) / (3 * U)) + 1
            self.route += [(x0 + (x1 - x0) * k / n, y0 + (y1 - y0) * k / n) for k in range(n)]
        if pts:
            self.route.append(pts[-1])
        self.r0 = 1.0 + 0.4 * len(self.labels) + 0.5
        self.a, self.b = it["tijd"], it["tijd"] + it.get("duur", DUUR["kaart"])

    def parchment(self, rng):
        W, H = self.c.W, self.c.H
        base = np.array([0.86, 0.78, 0.62], np.float32)
        n = rng.normal(0, 1, (H // 8 + 1, W // 8 + 1)).astype(np.float32)
        n = np.asarray(Image.fromarray(((n * 30) + 128).clip(0, 255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
                       .filter(ImageFilter.GaussianBlur(6)), np.float32) / 255 - 0.5
        fine = rng.normal(0, 0.02, (H, W)).astype(np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        v = ((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2
        vig = 1 - 0.45 * np.clip(v, 0, 1.4) / 1.4
        return ((base[None, None] * (1 + n[..., None] * 0.18 + fine[..., None])) * vig[..., None]).clip(0, 1).astype(np.float32)

    def draw(self, frame, t):
        U, W, H = self.c.U, self.c.W, self.c.H
        dur = self.b - self.a
        f = self.parch.copy()
        a0 = ease(t / 1.5)
        f = over(f, 1 - self.land, (0.42, 0.52, 0.55), 0.22 * a0)
        f = over(f, self.land, (0.55, 0.42, 0.27), 0.30 * a0)
        f = over(f, self.waves, INK, 0.4 * ease((t - 0.5) / 1.5))
        f = over(f, self.coast, INK, 0.9 * a0)
        f = over(f, self.title, INK, ease((t - 0.3) / 1.5))
        for m in self.rook:
            f = over(f, m, (0.45, 0.42, 0.40), 0.35 * ease((t - 2.4) / 2) * (0.85 + 0.15 * math.sin(t)))
        for m, t0 in self.labels:
            f = over(f, m, INK, ease((t - t0) / 1.0))
        if self.route:
            p = ease((t - self.r0) / max(dur - self.r0 - 4.0, 2.0))
            k = int(p * (len(self.route) - 1))
            if p > 0:
                img = Image.new("L", (W, H), 0)
                d = ImageDraw.Draw(img)
                for i in range(0, k, 7):
                    d.line(self.route[i:min(i + 4, k) + 1], fill=255, width=max(3, int(4 * U)))
                x, y = self.route[k]
                dot = Image.new("L", (W, H), 0)
                ImageDraw.Draw(dot).ellipse((x - 26 * U, y - 26 * U, x + 26 * U, y + 26 * U), fill=255)
                f = over(f, np.asarray(img, np.float32) / 255, (0.55, 0.12, 0.08), 0.9)
                f = over(f, np.asarray(dot.filter(ImageFilter.GaussianBlur(14 * U)), np.float32) / 255, (1.0, 0.85, 0.55), 0.8)
                f = over(f, self.c.mask(lambda d: d.ellipse((x - 7 * U, y - 7 * U, x + 7 * U, y + 7 * U), fill=255)), (0.55, 0.12, 0.08), 1)
        k = fade(t, 0, dur, 1.5, 1.5)
        return frame * (1 - k) + f * k


# ---------------- hoofdprogramma ----------------
def probe(path):
    out = subprocess.run([FF, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    w, h = map(int, re.search(r", (\d{3,5})x(\d{3,5})", out).groups())
    fps = float(re.search(r"([\d.]+) fps", out).group(1))
    hh, mm, ss = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()
    return w, h, fps, int(hh) * 3600 + int(mm) * 60 + float(ss)


def build(plan, c, einde, rng):
    parts = []
    sky = Sky(c, rng) if plan.get("intro") or plan.get("slot") else None
    if plan.get("intro"):
        parts.append(Intro(c, sky, plan.get("onderwerp", "")))
    for it in plan.get("items", []):
        s = it["soort"]
        parts.append({"hoofdstuk": lambda: Hoofdstuk(c, it), "datum": lambda: Datum(c, it),
                      "citaat": lambda: Citaat(c, it), "tijdlijn": lambda: Tijdlijn(c, it),
                      "kaart": lambda: Kaart(c, it, rng)}[s]())
    if plan.get("slot"):
        parts.append(Slot(c, sky, einde))
    parts.sort(key=lambda p: p.a)
    for p, q in zip(parts, parts[1:]):
        if q.a < p.b:
            print(f"let op: {type(p).__name__} ({p.a:.0f}-{p.b:.0f} s) overlapt met {type(q).__name__} ({q.a:.0f} s)")
    return parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inp"); ap.add_argument("out")
    ap.add_argument("--plan", help="motion.json")
    ap.add_argument("--effecten", help="effecten.tsv (van, tot, effect[, sterkte]) — zelfde als tools/effects.py")
    ap.add_argument("--proef", type=float, help="alleen het beeld op deze tijd opslaan (out = .png/.jpg)")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()

    w, h, fps, dur = probe(a.inp)
    c = Canvas(w, h)
    rng = np.random.default_rng(a.seed)
    plan = json.load(open(a.plan)) if a.plan else {}
    parts = build(plan, c, dur, rng)
    systems = []
    if a.effecten:
        for r in csv.DictReader(open(a.effecten), delimiter="\t"):
            p = dict(PRESETS[r["effect"].strip()])
            p["n"] = max(1, int(p["n"] * float(r.get("sterkte") or 1)))
            systems.append((float(r["van"]), float(r["tot"]), Particles(p, w, h, rng), np.array(p["color"], np.float32) / 255))

    def render(buf, t, dt):
        act_p = [p for p in parts if p.a <= t < p.b]
        act_s = [s for s in systems if s[0] <= t <= s[1]]
        if not act_p and not act_s:
            return buf
        frame = np.frombuffer(buf, np.uint8).reshape(h, w, 3).astype(np.float32) / 255
        for van, tot, ps, col in act_s:
            ps.step(dt, t)
            g = min(1, (t - van) / 3.0, (tot - t) / 3.0)
            layer = np.zeros((h, w), np.float32)
            ps.draw(layer, t)
            frame = over(frame, layer, col, g)
        for p in act_p:
            frame = p.draw(frame, t - p.a)
        return (np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes()

    if a.proef is not None:
        raw = subprocess.run([FF, "-v", "error", "-ss", str(a.proef), "-i", a.inp, "-frames:v", "1",
                              "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], capture_output=True).stdout
        out = render(raw[:w * h * 3], a.proef, 1 / fps)
        Image.frombytes("RGB", (w, h), out).save(a.out)
        print(a.out)
        return

    dec = subprocess.Popen([FF, "-v", "error", "-i", a.inp, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}", "-r", str(fps),
                            "-i", "-", "-i", a.inp, "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-preset", "medium",
                            "-crf", "22", "-pix_fmt", "yuv420p", "-c:a", "copy", "-movflags", "+faststart", a.out],
                           stdin=subprocess.PIPE)
    fb, dt, i = w * h * 3, 1 / fps, 0
    while True:
        buf = dec.stdout.read(fb)
        if len(buf) < fb:
            break
        enc.stdin.write(render(buf, i * dt, dt))
        i += 1
        if i % int(fps * 600) == 0:
            print(f"  {i / fps / 60:.0f} min", flush=True)
    enc.stdin.close()
    if enc.wait() or dec.wait():
        sys.exit("ffmpeg gaf een fout")
    print(json.dumps({"frames": i, "onderdelen": len(parts), "effecten": len(systems), "out": a.out}))


if __name__ == "__main__":
    main()
