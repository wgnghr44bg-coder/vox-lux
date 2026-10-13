"""GAMING VS. WIFE: 2D-cartoon (16:9, ± 33 s) zonder tekst of stemmen.

Bram (de gamer) en Lotte (zijn vrouw) uit poppetjes2.py. Alleen gebaren, gezichten,
emoji's, camerabewegingen (zooms, volgen, harde cuts, freeze frame) en geluidseffecten.
Alles met code gemaakt: gratis en zonder auteursrecht.

Scènes: 1 gamen  2 ze wil aandacht  3 het bord valt  4 wifi-stekker eruit
        5 sorry + bloem + knuffel  6 wifi terug, hij duikt weg, deegroller, freeze.

Gebruik: python3 tools/cartoon/gaming_vs_wife.py [uit.mp4] [--beeld SEC] [--van SEC --tot SEC]
"""
import argparse
import math
import random
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from poppetjes2 import INK, bram, lotte  # noqa: E402

W, H, FPS = 1920, 1080, 30
Z = 2  # wereld wordt op 2x getekend, de camera snijdt eruit en verkleint
DUUR = 33.6
FREEZE = 32.3
EMOJI_FONT = "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf"
VLOER = 760


# ================================================================ kleine hulpjes
def klem(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def fase(t, a, b):
    return klem((t - a) / (b - a))


def zacht(x):
    x = klem(x)
    return x * x * (3 - 2 * x)


def lerp(a, b, u):
    return a + (b - a) * u


def terug(u):  # ease-out-back: schiet iets door en veert terug
    c1 = 1.70158
    return 1 + (c1 + 1) * (u - 1) ** 3 + c1 * (u - 1) ** 2


def pad(t, keys):
    """Lineair pad door (t, x, y). Geeft x, y en of er bewogen wordt."""
    if t <= keys[0][0]:
        return keys[0][1], keys[0][2], False
    for (t0, x0, y0), (t1, x1, y1) in zip(keys, keys[1:]):
        if t0 <= t < t1:
            u = (t - t0) / (t1 - t0)
            return lerp(x0, x1, u), lerp(y0, y1, u), (x0, y0) != (x1, y1)
    return keys[-1][1], keys[-1][2], False


def schaal_lotte(y):  # verder weg = kleiner
    return 62 + (y - 762) * 0.1212


def schouders(x, y, s, hop=0.0, zak=0.0):
    bw = 0.62 * s
    top = y - hop - 2.75 * s + zak * 0.8 * s
    sy = top + 0.28 * s
    return (x - 0.85 * bw, sy), (x + 0.85 * bw, sy)


def ik(sch, doel, s, kant):
    """Arm (2 stukken van 0.6 s) naar een doel; elleboog naar buiten. Geeft (hoek, knik)."""
    L = 0.6 * s
    dx, dy = doel[0] - sch[0], doel[1] - sch[1]
    d = min(math.hypot(dx, dy), 2 * L * 0.999)
    phi = math.atan2(dy, dx)
    a = math.acos(d / (2 * L))
    beste = None
    for buig in (1, -1):
        h1 = phi - buig * a
        ex = sch[0] + math.cos(h1) * L
        if beste is None or ex * kant > beste[0] * kant:
            beste = (ex, math.degrees(h1), math.degrees(2 * a) * buig)
    return beste[1], beste[2]


def armen_naar(x, y, s, links, rechts, hop=0.0, zak=0.0):
    sl, sr = schouders(x, y, s, hop, zak)
    return (ik(sl, links, s, -1), ik(sr, rechts, s, 1))


# ================================================================ emoji's
@lru_cache(maxsize=None)
def emoji_basis(ch):
    f = ImageFont.truetype(EMOJI_FONT, 109)
    im = Image.new("RGBA", (260, 180), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((20, 10), ch, font=f, embedded_color=True)
    return im.crop(im.getbbox())


def emoji(frame, ch, x, y, grootte, alpha=1.0, flip=False, rot=0.0):
    """Emoji op wereldpositie (x, y) = midden, grootte in wereldeenheden."""
    if grootte <= 1 or alpha <= 0:
        return
    im = emoji_basis(ch)
    h = max(2, int(grootte * Z))
    im = im.resize((max(2, int(im.width * h / im.height)), h), Image.LANCZOS)
    if flip:
        im = im.transpose(Image.FLIP_LEFT_RIGHT)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1:
        a = im.getchannel("A").point(lambda v: int(v * alpha))
        im.putalpha(a)
    frame.paste(im, (int(x * Z - im.width / 2), int(y * Z - im.height / 2)), im)


def pop(frame, t, a, b, ch, x, y, grootte, flip=False, zweef=True):
    """Emoji die opploft (met doorschieten), zachtjes zweeft en aan het eind vervaagt."""
    if not a <= t < b:
        return
    u = (t - a) / 0.25
    k = terug(klem(u)) if u < 1 else 1.0
    al = klem((b - t) / 0.2)
    dy = math.sin((t - a) * 5) * 6 if zweef else 0
    emoji(frame, ch, x, y + dy, grootte * k, al, flip)


# ================================================================ decor
def R(*v):
    return [c * Z for c in v]


def achtergrond():
    img = Image.new("RGB", (W * Z, H * Z))
    d = ImageDraw.Draw(img)
    for y in range(VLOER * Z):
        d.line((0, y, W * Z, y), fill=tuple(int(lerp(a, b, y / (VLOER * Z))) for a, b in zip((246, 230, 204), (234, 210, 178))))
    for x in range(0, W * Z, 100 * Z):  # behang
        d.line((x, 0, x, VLOER * Z), fill=(238, 220, 192), width=22 * Z)
    d.rectangle(R(0, VLOER, W, H), fill=(178, 128, 88))
    for y in range(VLOER + 60, H, 80):  # planken
        d.line(R(0, y, W, y), fill=(160, 112, 76), width=4 * Z)
        off = (y * 7) % 340
        for x in range(off, W, 340):
            d.line(R(x, y, x, y + 80), fill=(160, 112, 76), width=3 * Z)
    d.rectangle(R(0, VLOER - 22, W, VLOER), fill=(250, 245, 235), outline=INK, width=4 * Z)
    # keuken achterwand: tegels en kastjes
    d.rectangle(R(600, 470, 1100, 600), fill=(225, 238, 240))
    for x in range(600, 1100, 40):
        d.line(R(x, 470, x, 600), fill=(200, 215, 220), width=2 * Z)
    for y in range(470, 600, 40):
        d.line(R(600, y, 1100, y), fill=(200, 215, 220), width=2 * Z)
    for x0 in (610, 770, 930):
        d.rectangle(R(x0, 300, x0 + 150, 450), fill=(130, 175, 160), outline=INK, width=5 * Z)
        d.ellipse(R(x0 + 120, 360, x0 + 134, 374), fill=INK)
    # afzuigkap
    d.polygon(R(850, 380, 960, 380, 990, 470, 820, 470), fill=(190, 190, 200), outline=INK)
    d.line(R(820, 470, 990, 470), fill=INK, width=5 * Z)
    # schilderij boven de bank
    d.rectangle(R(1390, 250, 1640, 430), fill=(200, 225, 240), outline=(120, 80, 50), width=14 * Z)
    d.ellipse(R(1560, 280, 1610, 330), fill=(255, 215, 90))
    d.polygon(R(1405, 415, 1480, 330, 1530, 380, 1570, 345, 1625, 415), fill=(110, 150, 120))
    d.rectangle(R(1390, 250, 1640, 430), outline=INK, width=4 * Z)
    # staande lamp rechts
    d.line(R(1880, 760, 1880, 360), fill=INK, width=6 * Z)
    d.polygon(R(1830, 360, 1930, 360, 1905, 290, 1855, 290), fill=(255, 235, 170), outline=INK)
    # tv-meubel en tv
    d.rectangle(R(90, 690, 480, 800), fill=(150, 100, 70), outline=INK, width=5 * Z)
    d.line(R(285, 690, 285, 800), fill=INK, width=4 * Z)
    for x in (180, 380):
        d.rounded_rectangle(R(x - 30, 735, x + 30, 748), radius=5 * Z, fill=(230, 200, 140), outline=INK)
    d.rectangle(R(110, 800, 130, 820), fill=INK)
    d.rectangle(R(440, 800, 460, 820), fill=INK)
    d.rectangle(R(230, 675, 290, 690), fill=(40, 40, 48))
    d.rounded_rectangle(R(105, 415, 395, 680), radius=10 * Z, fill=(30, 30, 38), outline=INK, width=5 * Z)
    # stopcontact
    d.rounded_rectangle(R(530, 712, 562, 752), radius=5 * Z, fill=(250, 250, 250), outline=INK, width=3 * Z)
    d.ellipse(R(540, 722, 546, 728), fill=INK)
    d.ellipse(R(546, 735, 552, 741), fill=INK)
    # salontafel
    d.rounded_rectangle(R(1110, 852, 1340, 880), radius=8 * Z, fill=(170, 115, 75), outline=INK, width=5 * Z)
    for x in (1130, 1310):
        d.rectangle(R(x, 880, x + 14, 960), fill=(140, 95, 62), outline=INK, width=3 * Z)
    return img


def laag_aanrecht():
    im = Image.new("RGBA", (W * Z, H * Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle(R(600, 600, 1100, 765), fill=(240, 240, 235), outline=INK, width=5 * Z)
    d.rectangle(R(590, 588, 1110, 606), fill=(120, 120, 130), outline=INK, width=4 * Z)
    for x0 in (615, 780, 945):
        d.rectangle(R(x0, 625, x0 + 140, 745), outline=INK, width=4 * Z)
        d.line(R(x0 + 55, 640, x0 + 85, 640), fill=INK, width=5 * Z)
    # pan op het fornuis
    d.rectangle(R(870, 545, 960, 590), fill=(70, 70, 80), outline=INK, width=4 * Z)
    d.line(R(960, 560, 1010, 552), fill=INK, width=8 * Z)
    d.ellipse(R(866, 535, 964, 555), fill=(200, 120, 70), outline=INK, width=3 * Z)
    return im


def laag_bank():
    im = Image.new("RGBA", (W * Z, H * Z), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    blauw, donker = (95, 125, 180), (75, 100, 150)
    d.rounded_rectangle(R(1205, 600, 1795, 770), radius=40 * Z, fill=blauw, outline=INK, width=5 * Z)
    d.rounded_rectangle(R(1185, 740, 1815, 880), radius=20 * Z, fill=donker, outline=INK, width=5 * Z)
    d.rounded_rectangle(R(1225, 728, 1505, 785), radius=18 * Z, fill=blauw, outline=INK, width=4 * Z)
    d.rounded_rectangle(R(1495, 728, 1775, 785), radius=18 * Z, fill=blauw, outline=INK, width=4 * Z)
    for x0 in (1150, 1745):
        d.rounded_rectangle(R(x0, 665, x0 + 75, 880), radius=30 * Z, fill=blauw, outline=INK, width=5 * Z)
    for x in (1210, 1780):
        d.rectangle(R(x, 880, x + 16, 900), fill=INK)
    return im


# ================================================================ spel op de tv
def spel(t, staat, bw, bh):
    """Kleurrijk ruimteschietspel. staat: speel, weg (verbinding kwijt), terug (flits)."""
    im = Image.new("RGB", (bw, bh))
    d = ImageDraw.Draw(im)
    tt = 20.0 if staat == "weg" else t
    for y in range(bh):
        d.line((0, y, bw, y), fill=(int(lerp(25, 70, y / bh)), int(lerp(10, 30, y / bh)), int(lerp(70, 120, y / bh))))
    rng = random.Random(3)
    for _ in range(40):
        sx, sy = rng.uniform(0, 1), rng.uniform(0, 1)
        y = ((sy + tt * 0.3) % 1) * bh
        r = max(1, bw // 220)
        d.ellipse((sx * bw - r, y - r, sx * bw + r, y + r), fill=(255, 255, 255))
    px = bw * (0.5 + 0.3 * math.sin(tt * 2.3))
    py = bh * 0.82
    u = bw * 0.05
    d.polygon([(px, py - u), (px - u * 0.8, py + u * 0.6), (px + u * 0.8, py + u * 0.6)], fill=(80, 230, 255))
    for k in range(3):
        ex = bw * (0.2 + 0.3 * k + 0.08 * math.sin(tt * 3 + k))
        ey = bh * (0.22 + 0.05 * math.sin(tt * 4 + k * 2))
        d.ellipse((ex - u * 0.7, ey - u * 0.5, ex + u * 0.7, ey + u * 0.5), fill=(255, 80, 200))
        d.ellipse((ex - u * 0.25, ey - u * 0.2, ex + u * 0.25, ey + u * 0.2), fill=(255, 255, 120))
    for k in range(4):  # lasers
        ly = py - u - ((tt * 3 + k * 0.25) % 1) * bh * 0.7
        d.line((px, ly, px, ly - u * 0.6), fill=(255, 255, 80), width=max(2, bw // 160))
    for k in range(2):  # ontploffingen
        ph = (tt * 1.3 + k * 0.5) % 1
        ex = bw * (0.3 + 0.4 * k)
        ey = bh * 0.3
        r = u * (0.5 + ph * 2)
        d.ellipse((ex - r, ey - r, ex + r, ey + r), outline=(255, 160, 40), width=max(2, int(bw / 80 * (1 - ph))))
    if staat == "weg":
        ov = Image.new("RGB", (bw, bh), (0, 0, 0))
        im = Image.blend(im, ov, 0.5)
        d = ImageDraw.Draw(im)
        cx, cy, r = bw / 2, bh / 2, bh * 0.3
        knip = 1 if int(t * 4) % 2 == 0 else 0.85
        for k in range(3):  # wifi-boogjes
            rr = r * (0.35 + 0.3 * k) * knip
            d.arc((cx - rr, cy - rr * 0.2, cx + rr, cy + rr * 1.8), 225, 315, fill=(200, 200, 210), width=int(bh / 30))
        d.ellipse((cx - r * 1.05, cy - r * 1.05, cx + r * 1.05, cy + r * 1.05), outline=(230, 30, 40), width=int(bh / 22))
        w = int(bh / 14)
        d.line((cx - r * 0.6, cy - r * 0.6, cx + r * 0.6, cy + r * 0.6), fill=(230, 30, 40), width=w)
        d.line((cx - r * 0.6, cy + r * 0.6, cx + r * 0.6, cy - r * 0.6), fill=(230, 30, 40), width=w)
    elif staat == "terug":
        wit = Image.new("RGB", (bw, bh), (255, 255, 255))
        im = Image.blend(im, wit, klem(1 - (t - 27.0) / 0.25) * 0.8)
    return im


# ================================================================ de verhaallijn
TV_SCHERM = (120, 430, 380, 665)
ROUTER = (405, 652, 465, 690)
STOP = (546, 732)
BORD_TAFEL = (1180, 850)
BORD_VLOER = (1150, 1005)
BANK_LIG = (1770, 752)
BANK_ZIT = (1450, 935)


def router_aan(t):
    return not (20.0 <= t < 26.65)


def tv_staat(t):
    if 20.0 <= t < 27.0:
        return "weg"
    if 27.0 <= t < 27.3:
        return "terug"
    return "speel"


def man(t, seed):
    """Positie en pose van Bram."""
    s = 90
    x, y = BANK_ZIT
    st = dict(fn=bram, x=x, y=y, s=s, rot=0.0, hop=0.0, sx=1.0, sy=1.0, diepte=935, controller="beide")
    p = {"seed": seed}
    jit = random.Random(int(t * FPS))

    def gamen(wild=1.0):
        sl, sr = schouders(st["x"], st["y"], s, st["hop"], p.get("zak", 0))
        dl = (st["x"] - 0.17 * s + jit.uniform(-3, 3) * wild, sl[1] + 0.72 * s + jit.uniform(-3, 3) * wild)
        dr = (st["x"] + 0.17 * s + jit.uniform(-3, 3) * wild, sr[1] + 0.72 * s + jit.uniform(-3, 3) * wild)
        p["armen"] = (ik(sl, dl, s, -1), ik(sr, dr, s, 1))

    def juich(hoog=1.0):
        w = math.sin(t * 22) * 25
        p["armen"] = ((-120 + w, -25 * hoog), (-60 - w, 25 * hoog))
        p["mond"] = "lach"
        st["hop"] = abs(math.sin(t * 14)) * 22

    if t < 3.0:  # ligt languit op de bank te gamen
        st.update(x=BANK_LIG[0] + jit.uniform(-2, 2), y=BANK_LIG[1] + jit.uniform(-2, 2), rot=80.0)
        p["loop"] = (t * 16, 0.18)
        gamen(1.5)
    elif t < 3.4:  # springt rechtop
        u = zacht(fase(t, 3.0, 3.4))
        st.update(x=lerp(BANK_LIG[0], x, u), y=lerp(BANK_LIG[1], y, u), rot=80 * (1 - u))
        st["hop"] = math.sin(u * math.pi) * 150
        juich()
        st["controller"] = "rechts"
    elif t < 4.8:
        juich()
        st["controller"] = "rechts"
    elif t < 13.0:
        gamen()
        if 7.5 <= t < 8.1:  # duim omhoog zonder te kijken
            sl, sr = schouders(x, y, s)
            p["armen"] = (p["armen"][0], ik(sr, (x + 0.9 * s, sr[1] - 0.5 * s), s, 1))
            st["controller"] = "links"
            st["duim"] = "👍"
        elif 9.3 <= t < 9.9:  # 'wacht even'
            sl, sr = schouders(x, y, s)
            p["armen"] = (p["armen"][0], ik(sr, (x + 0.75 * s, sr[1] - 0.65 * s), s, 1))
            st["controller"] = "links"
            st["duim"] = "☝️"
        elif 11.9 <= t < 12.4:  # ongeduldig gebaar: zet maar neer
            sl, sr = schouders(x, y, s)
            pomp = math.sin(t * 30) * 0.15 * s
            p["armen"] = (ik(sl, (x - 1.05 * s, sl[1] + 0.55 * s + pomp), s, -1), p["armen"][1])
            st["controller"] = "rechts"
    elif t < 13.6:  # juicht en slaat het bord van tafel
        juich()
        st["hop"] = math.sin(fase(t, 13.0, 13.6) * math.pi) * 60
        st["controller"] = "rechts"
        if t < 13.35:
            sl, _ = schouders(x, y, s, st["hop"])
            sw = fase(t, 13.0, 13.35)
            p["armen"] = (ik(sl, (x - lerp(0.4, 1.2, sw) * s, sl[1] + lerp(-0.8, 0.6, sw) * s), s, -1), p["armen"][1])
    elif t < 15.8:
        gamen()
    elif t < 17.0:  # merkt haar boze blik
        gamen(0)
        u = fase(t, 15.8, 16.1)
        p.update(bril=u, kijk=(-0.85, 0.0), mond="plat" if t < 16.2 else "o", pupil=0.35)
        st["sx"] = 1 + math.sin(t * 50) * 0.01
    elif t < 20.7:
        gamen()
    elif t < 21.3:  # SCHOK
        p.update(bril=1.0, pupil=0.17, kijk=(0, 0), mond="open", wenk="op")
        st["x"] += jit.uniform(-4, 4)
        st["controller"] = "vallend"
        if t >= 20.95:
            sl, sr = schouders(x, y, s)
            ky = y - 2.75 * s - 0.95 * s
            p["armen"] = armen_naar(x, y, s, (x - 0.95 * s, ky), (x + 0.95 * s, ky))
        else:
            gamen(0)
    elif t < 21.6:  # valt achterover op de bank
        u = zacht(fase(t, 21.3, 21.6))
        st.update(x=lerp(x, BANK_LIG[0], u), y=lerp(y, BANK_LIG[1], u), rot=80 * u)
        ky = y - 2.75 * s - 0.95 * s
        p.update(bril=1.0, pupil=0.17, mond="open", wenk="op",
                 armen=armen_naar(x, y, s, (x - 0.95 * s, ky), (x + 0.95 * s, ky)))
        st["controller"] = None
    elif t < 22.2:
        st.update(x=BANK_LIG[0], y=BANK_LIG[1], rot=80.0)
        p.update(bril=1.0, lid=1, mond="open", armen=((200, -20), (-20, 20)))
        st["controller"] = None
    elif t < 22.6:  # glijdt van de bank op zijn knieën
        u = zacht(fase(t, 22.2, 22.6))
        st.update(x=lerp(BANK_LIG[0], 1450, u), y=lerp(BANK_LIG[1], 965, u), rot=80 * (1 - u))
        p.update(bril=1.0, zak=u, pupil=0.5, kijk=(-0.8, 0), mond="o", wenk="op")
        st["controller"] = None
    elif t < 24.5:
        kx, _, beweegt = pad(t, [(22.6, 1450, 965), (23.1, 800, 965)])
        st.update(x=kx, y=965, diepte=965)
        p.update(bril=1.0, zak=1.0, pupil=0.72, kijk=(-0.7, -0.6), wenk="op", mond="o")
        if beweegt:
            p["loop"] = (t * 20, 0.1)
            st["hop"] = abs(math.sin(t * 20)) * 8
        st["controller"] = None
        sl, sr = schouders(kx, 965, s, 0, 1)
        borst = (kx, sl[1] + 0.35 * s)
        if 23.1 <= t < 23.6:  # handen gevouwen 🙏
            p["armen"] = armen_naar(kx, 965, s, (borst[0] - 0.05 * s, borst[1]), (borst[0] + 0.05 * s, borst[1]), zak=1)
            st["handen_emoji"] = "🙏"
        elif 23.6 <= t < 24.1:  # biedt de controller aan
            p["armen"] = (ik(sl, (kx - 1.15 * s, sl[1] - 0.1 * s), s, -1), ik(sr, (kx + 0.3 * s, sr[1] + 0.9 * s), s, 1))
            st["controller"] = "links"
        elif t >= 24.1:  # hartje met de handen
            p["armen"] = armen_naar(kx, 965, s, (kx - 0.12 * s, sl[1] - 0.25 * s), (kx + 0.12 * s, sl[1] - 0.25 * s), zak=1)
            st["hart"] = (kx, sl[1] - 0.3 * s)
    elif t < 27.8:  # staat op en knuffelt
        u = zacht(fase(t, 24.5, 24.8))
        kx = lerp(800, 700, u)
        if 25.3 <= t < 25.7:
            kx = 730
        st.update(x=kx, y=lerp(965, 945, u), diepte=946)
        p.update(bril=1.0, zak=1 - u, pupil=0.6, kijk=(-0.8, -0.2), mond="lach" if t < 27.3 else None,
                 lid=2 if 25.7 <= t < 27.3 else 0)
        st["controller"] = None
        sl, sr = schouders(kx, st["y"], s, 0, p["zak"])
        p["armen"] = (ik(sl, (kx - 1.15 * s, sl[1] + 0.25 * s), s, -1), ik(sr, (kx - 0.75 * s, sr[1] + 0.35 * s), s, 1))
        if 25.3 <= t < 25.7:  # tovert een roosje tevoorschijn
            p["armen"] = (p["armen"][0], ik(sr, (kx - 0.45 * s, sr[1] - 0.35 * s), s, 1))
            st["bloem"] = True
            p["mond"] = None
        if t >= 27.3:  # ogen schieten naar de tv, grijns komt terug
            p.update(kijk=(-1.0, -0.1), pupil=0.4, lid=0)
    elif t < 28.3:  # DUIK terug naar de bank
        u = fase(t, 27.8, 28.3)
        st.update(x=lerp(700, x, zacht(u)), y=lerp(945, y, u), rot=-35 * math.sin(u * math.pi))
        st["hop"] = math.sin(u * math.pi) * 220
        p.update(bril=1 - u, mond="lach", armen=((-160, 10), (-20, -10)), loop=(t * 30, 0.3))
        st["controller"] = None
    elif t < 31.2:
        if t < 29.0:
            juich()
            st["controller"] = "rechts"
        else:
            gamen(1.6)
            p["mond"] = "lach"
    else:  # merkt de schaduw
        gamen(0)
        u = fase(t, 31.2, 31.55)
        p.update(bril=u, kijk=(0.6, -0.8), pupil=lerp(0.45, 0.18, fase(t, 31.5, 31.9)),
                 mond=None if t < 31.5 else ("plat" if t < 31.8 else "open"), wenk="op" if t > 31.6 else None)
        st["x"] += math.sin(t * 60) * 2.5 * fase(t, 31.6, 31.9)
    st["p"] = p
    return st


def vrouw(t, seed):
    """Positie en pose van Lotte, plus wat ze vasthoudt."""
    st = dict(fn=lotte, rot=0.0, hop=0.0, sx=1.0, sy=1.0, houd=None)
    p = {"seed": seed}
    NEER = ((100, -10), (80, 10))
    sluip = ((-150, 70), (-30, -70))
    keys = [(0, 850, 762), (5.0, 850, 762), (5.35, 1100, 775), (5.65, 1080, 960), (6.3, 1600, 955),
            (10.6, 1600, 955), (11.05, 1130, 790), (11.15, 1130, 790), (11.8, 1090, 940),
            (17.4, 1090, 940), (19.0, 600, 905), (29.6, 600, 905), (30.3, 1110, 790), (30.4, 1110, 790),
            (30.75, 1210, 748), (31.2, 1640, 745)]
    x, y, beweegt = pad(t, keys)
    s = schaal_lotte(y)
    st.update(x=x, y=y, s=s)
    if beweegt:
        sluipt = 17.4 <= t < 19.0
        p["loop"] = (t * (7 if sluipt else 13), 0.45 if sluipt else 0.25)
        st["hop"] = abs(math.sin(t * (7 if sluipt else 13))) * (14 if sluipt else 8)
        p["armen"] = sluip if sluipt else ((95 + 25 * math.sin(t * 13), -10), (85 - 25 * math.sin(t * 13), 10))
        if sluipt:
            p.update(kijk=(-0.9, 0), lid=0.35, wenk="boos")
    sl, sr = schouders(x, y, s, st["hop"])
    borst = (x, sl[1] + 0.35 * s)

    def gekruist():
        return armen_naar(x, y, s, (x + 0.32 * s, sl[1] + 0.38 * s), (x - 0.32 * s, sr[1] + 0.42 * s), st["hop"])

    if t < 5.0:  # roert in de pan
        w = t * 6
        p["armen"] = (NEER[0], ik(sr, (912 + 14 * math.cos(w), 545 + 5 * math.sin(w)), s, 1))
        p["kijk"] = (0.6, 0.6)
        if 1.5 <= t < 2.6:
            p["kijk"] = (1.0, -0.1)
    elif t < 6.3:
        p.setdefault("kijk", (-0.6, 0))
    elif t < 7.0:  # zwaait met twee handen voor zijn gezicht
        w = math.sin(t * 16) * 30
        p["armen"] = armen_naar(x, y, s, (1505 + w, 655), (1530 - w, 670))
        p["kijk"] = (-0.9, -0.3)
    elif t < 7.5:  # tikt op zijn schouder
        tik = abs(math.sin(t * 14)) * 12
        p["armen"] = (ik(sl, (1505 + tik, 712 - tik * 0.5), s, -1), NEER[1])
        p["kijk"] = (-0.9, -0.3)
    elif t < 8.1:
        p.update(kijk=(-0.9, -0.3), armen=NEER)
    elif t < 8.5:  # wijst naar zichzelf
        p["armen"] = (NEER[0], ik(sr, (x + 0.05 * s, borst[1]), s, 1))
        p["kijk"] = (-0.5, -0.2)
    elif t < 9.0:  # hartje met haar handen
        p["armen"] = armen_naar(x, y, s, (x - 0.12 * s, sl[1] - 0.2 * s), (x + 0.12 * s, sl[1] - 0.2 * s))
        st["hart"] = (x, sl[1] - 0.25 * s)
    elif t < 9.3:  # wijst naar hem
        p["armen"] = (ik(sl, (x - 2 * s, sl[1] - 0.15 * s), s, -1), NEER[1])
        p["kijk"] = (-0.9, -0.2)
    elif t < 10.6:
        p.update(kijk=(-0.8, -0.3), armen=NEER)
        if t >= 9.6:  # glimlach weg, wenkbrauw omhoog, oog trilt
            p["mond"] = "plat"
            p["kijk"] = (0, 0)
        if t >= 9.9:
            p["wenk"] = "een"
            p["lid"] = 0.3 + 0.25 * (math.sin(t * 70) > 0.3) if t >= 10.0 else 0
    elif t < 11.8:  # haalt het bord
        if t >= 11.15:
            p["armen"] = armen_naar(x, y, s, (x - 0.15 * s, borst[1] + 0.25 * s), (x + 0.15 * s, borst[1] + 0.25 * s), st["hop"])
            st["houd"] = "bord"
        p["kijk"] = (0.5, 0) if t < 11.15 else (0.9, -0.1)
        p["mond"] = None
    elif t < 12.1:  # zet het bord neer, trots
        u = fase(t, 11.8, 12.1)
        doel = (lerp(x + 0.2 * s, BORD_TAFEL[0], u), lerp(borst[1] + 0.25 * s, BORD_TAFEL[1], u))
        p["armen"] = armen_naar(x, y, s, (doel[0] - 0.15 * s, doel[1]), (doel[0] + 0.15 * s, doel[1]))
        st["rot"] = -8 * u
        st["houd"] = "bord"
        st["bord_pos"] = doel
        p["kijk"] = (0.9, 0.3)
    elif t < 13.3:  # armen over elkaar, tikt met haar voet
        p["armen"] = gekruist()
        p.update(mond="plat", lid=0.3, kijk=(0.9, -0.1), loop=(t * 16, 0.08))
    elif t < 15.0:  # kijkt het vliegende bord na
        bx, by, _ = bord_vlucht(t)
        p.update(kijk=(klem((bx - x) / 200, -1, 1), klem((by - (y - 4 * s)) / 300, -1, 1)), mond="o", armen=NEER)
        if t >= 14.6:
            p["mond"] = "plat"
    elif t < 16.6:  # woedend
        p.update(kijk=(0.9, 0), lid=0.4, wenk="boos", pupil=0.3, rood=0.55 * fase(t, 15.0, 15.5), mond="boos",
                 armen=gekruist())
        st["x"] += math.sin(t * 60) * 2
    elif t < 17.4:  # het idee
        p.update(kijk=(-1.0, -0.2), lid=0.35, wenk="boos", rood=0.55 * (1 - fase(t, 16.6, 17.0)), armen=gekruist())
    elif t < 19.0:
        pass  # sluipt (zie boven)
    elif t < 19.5:  # kijkt links, kijkt rechts
        p.update(kijk=(-1, 0) if t < 19.25 else (1, 0), lid=0.35, wenk="boos", armen=sluip)
    elif t < 22.2:  # trekt de stekker eruit
        u = fase(t, 19.8, 20.05)
        doel = (lerp(STOP[0], STOP[0] + 40, u), lerp(STOP[1], STOP[1] - 15, u))
        if t >= 21.5:
            doel = None
        p["armen"] = (ik(sl, doel, s, -1) if doel else NEER[0], NEER[1])
        st["stekker"] = doel
        p.update(kijk=(-0.7, 0.6) if t < 20.1 else (1, 0), lid=0.35, wenk="boos" if t < 20.1 else None)
    elif t < 25.3:  # doet alsof ze boos blijft
        p.update(armen=gekruist(), kijk=(-0.9, -0.4), mond="plat", wenk="boos", lid=0.3)
        st["hop"] = 0
    elif t < 25.7:  # ziet het roosje
        p.update(armen=gekruist(), kijk=(0.9, 0.2), pupil=0.68, mond=None)
    elif t < 28.9:  # knuffelt terug (en blijft zo staan als hij weg is)
        p["armen"] = armen_naar(x, y, s, (x + 0.9 * s, sl[1] + 0.35 * s), (x + 1.25 * s, sr[1] + 0.3 * s))
        p.update(lid=2 if t < 27.9 else 0, kijk=(0.6, 0))
        if t >= 27.9:
            p.update(pupil=0.3, mond="o")
    elif t < 29.6:  # draait naar de camera
        armen_uit = armen_naar(x, y, s, (x + 0.9 * s, sl[1] + 0.35 * s), (x + 1.25 * s, sr[1] + 0.3 * s))
        p["armen"] = armen_uit if t < 29.3 else NEER
        p.update(kijk=(0, 0), mond="plat" if t < 29.3 else None)
        if t >= 29.3:
            p.update(lid=0.35, wenk="boos")
    elif t < 30.4:
        if t >= 30.25:
            st["houd"] = "deegroller"
            p["armen"] = armen_naar(x, y, s, (x - 0.35 * s, sl[1] + 0.2 * s), (x + 0.35 * s, sr[1] + 0.2 * s), st["hop"])
        p.update(lid=0.35, wenk="boos", kijk=(1, 0))
    else:  # achter de bank met de deegroller, lief glimlachen
        tik = math.sin(t * 8) * 0.12 * s if not beweegt else 0
        p["armen"] = armen_naar(x, y, s, (x - 0.3 * s, sl[1] + 0.5 * s), (x + 1.1 * s, sr[1] - 0.4 * s + tik), st["hop"])
        st["houd"] = "deegroller"
        if not beweegt:
            p.update(lid=2, mond=None)
        else:
            p.update(lid=0.35, wenk="boos", kijk=(1, 0))
    st["p"] = p
    return st


def bord_vlucht(t):
    """Slow motion: bord vliegt van tafel naar de vloer."""
    u = fase(t, 13.3, 14.6)
    x = lerp(BORD_TAFEL[0], BORD_VLOER[0], u) + math.sin(u * math.pi) * 60
    y = lerp(BORD_TAFEL[1], BORD_VLOER[1], u) - math.sin(u * math.pi) * 230
    return x, y, u * 540


# ================================================================ camera
CAM = [  # (t, x, y, zoom)
    (0, 960, 540, 1.0), (0.8, 960, 540, 1.0), (3.0, 1350, 640, 1.45), (3.4, 1350, 640, 1.45),
    (3.6, 1450, 600, 2.5), (4.7, 1450, 600, 2.5), (5.0, 1150, 640, 1.35), (6.3, 1550, 640, 1.55),
    (9.55, 1550, 640, 1.55), (9.62, 1600, 640, 3.0), (10.6, 1600, 640, 3.1), (10.601, 1450, 700, 1.45),
    (11.1, 1200, 700, 1.5), (11.8, 1180, 720, 1.5), (13.0, 1260, 700, 1.4), (14.6, 1170, 820, 1.7),
    (14.99, 1170, 820, 1.75), (15.0, 1040, 600, 3.4), (15.8, 1040, 600, 3.7), (15.801, 1260, 660, 1.5),
    (16.6, 1260, 660, 1.65), (16.601, 1050, 570, 2.6), (17.4, 1040, 570, 2.7), (17.401, 1060, 870, 2.3),
    (19.0, 640, 870, 2.3), (19.001, 600, 690, 2.1), (19.5, 600, 690, 2.2), (19.501, 548, 735, 4.5),
    (20.1, 548, 735, 5.0), (20.7, 1450, 640, 1.3), (20.9, 1450, 600, 2.8), (21.3, 1450, 600, 2.8),
    (21.6, 1500, 650, 1.8), (22.2, 1500, 650, 1.6), (22.6, 1200, 640, 1.3), (23.1, 800, 640, 1.6),
    (25.3, 760, 640, 1.7), (26.6, 760, 600, 1.2), (26.601, 435, 668, 4.5), (27.0, 435, 668, 5.0),
    (27.3, 700, 600, 2.6), (27.8, 700, 600, 2.6), (28.3, 1450, 640, 1.5), (28.9, 1450, 640, 1.5),
    (28.901, 600, 620, 2.4), (29.6, 600, 620, 2.6), (29.601, 960, 560, 1.0), (31.2, 1380, 560, 1.35),
    (31.95, 1500, 600, 1.5), (32.25, 1490, 585, 2.6), (40, 1490, 585, 2.6),
]


def camera(t):
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAM, CAM[1:]):
        if t0 <= t < t1:
            u = zacht((t - t0) / (t1 - t0))
            return lerp(x0, x1, u), lerp(y0, y1, u), lerp(z0, z1, u)
    return CAM[-1][1:]


# ================================================================ tekenen
BG = AANRECHT = BANK = None


def init():
    global BG, AANRECHT, BANK
    BG, AANRECHT, BANK = achtergrond(), laag_aanrecht(), laag_bank()


def plak_laag(st):
    """Teken een poppetje op een eigen laag (wereld-pixels). Geeft laag, plek en info terug."""
    s = st["s"] * Z
    lw, lh = int(6.4 * s), int(7.8 * s)
    voet = lh - int(0.4 * s)
    laag = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    info = st["fn"](laag, lw / 2, voet, s, {**st["p"], "schaduw": False})
    sx, sy = st["sx"], st["sy"]
    if (sx, sy) != (1.0, 1.0):
        laag = laag.resize((max(1, int(lw * sx)), max(1, int(lh * sy))), Image.LANCZOS)
    ax, ay = laag.width / 2, voet * sy
    rot = st["rot"]
    th = math.radians(rot)
    cx0, cy0 = laag.width / 2, laag.height / 2
    if rot:  # draaien met 'expand', anders valt het hoofd buiten de laag
        laag = laag.rotate(rot, resample=Image.BICUBIC, expand=True)
    cx1, cy1 = laag.width / 2, laag.height / 2

    def draai(px, py):  # punt in de (geschaalde) laag -> punt in de gedraaide laag
        qx, qy = px - cx0, py - cy0
        return cx1 + qx * math.cos(th) + qy * math.sin(th), cy1 - qx * math.sin(th) + qy * math.cos(th)

    vx, vy = draai(ax, ay)
    ox, oy = int(st["x"] * Z - vx), int((st["y"] - st["hop"]) * Z - vy)

    def naar(px, py):  # laagpunt -> wereldeenheden
        qx, qy = draai(px * sx, py * sy)
        return (ox + qx) / Z, (oy + qy) / Z

    info["naar"] = naar
    return laag, ox, oy, info


def grondschaduw(d, x, y, s, hop):
    k = klem(1 - hop / 500, 0.3, 1)
    d.ellipse(R(x - s * 0.9 * k, y - s * 0.12 * k, x + s * 0.9 * k, y + s * 0.12 * k), fill=(150, 104, 70))


def controller(d, x, y, s, hoek=0.0):
    w, h = 0.75 * s, 0.32 * s
    c, sn = math.cos(math.radians(hoek)), math.sin(math.radians(hoek))

    def p(dx, dy):
        return ((x + dx * c - dy * sn) * Z, (y + dx * sn + dy * c) * Z)
    d.polygon([p(-w / 2, -h / 2), p(w / 2, -h / 2), p(w / 2 + 0.06 * s, h / 2), p(-w / 2 - 0.06 * s, h / 2)],
              fill=(45, 45, 55), outline=INK)
    for k, kl in enumerate([(240, 70, 70), (70, 200, 90), (70, 140, 240), (250, 210, 60)]):
        bx, by = p(w * 0.25 + (k % 2) * 0.1 * s, -0.05 * s + (k // 2) * 0.1 * s)
        r = 0.035 * s * Z
        d.ellipse((bx - r, by - r, bx + r, by + r), fill=kl)
    bx, by = p(-w * 0.25, 0)
    r = 0.05 * s * Z
    d.rectangle((bx - r * 1.6, by - r * 0.5, bx + r * 1.6, by + r * 0.5), fill=(200, 200, 210))
    d.rectangle((bx - r * 0.5, by - r * 1.6, bx + r * 0.5, by + r * 1.6), fill=(200, 200, 210))


def bord(d, x, y, s, hoek=0.0, eten=True):
    w, h = 0.95 * s, 0.3 * s
    d.ellipse(R(x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(250, 250, 250), outline=INK, width=4 * Z)
    if eten:
        d.ellipse(R(x - w * 0.3, y - h * 0.75, x + w * 0.05, y + h * 0.1), fill=(200, 120, 60), outline=INK, width=3 * Z)
        d.ellipse(R(x, y - h * 0.6, x + w * 0.3, y + h * 0.1), fill=(90, 170, 80), outline=INK, width=3 * Z)
        d.ellipse(R(x - w * 0.12, y - h * 0.35, x + w * 0.12, y + h * 0.25), fill=(240, 200, 80), outline=INK, width=3 * Z)


def deegroller(d, x, y, s):
    d.rounded_rectangle(R(x - 0.55 * s, y - 0.1 * s, x + 0.55 * s, y + 0.1 * s), radius=0.08 * s * Z,
                        fill=(215, 170, 110), outline=INK, width=4 * Z)
    for k in (-1, 1):
        d.rounded_rectangle(R(x + k * 0.55 * s - (0.25 * s if k < 0 else 0), y - 0.045 * s,
                              x + k * 0.55 * s + (0.25 * s if k > 0 else 0), y + 0.045 * s),
                            radius=0.04 * s * Z, fill=(180, 130, 80), outline=INK, width=3 * Z)


def wolk(d, x, y, r, kleur=(110, 110, 125)):
    for dx, dy, f in ((-0.8, 0.1, 0.7), (0, -0.25, 1.0), (0.8, 0.1, 0.75), (0.3, 0.3, 0.7), (-0.4, 0.3, 0.7)):
        rr = r * f
        d.ellipse(R(x + dx * r - rr, y + dy * r - rr, x + dx * r + rr, y + dy * r + rr), fill=kleur, outline=INK, width=3 * Z)


def scene(t, i):
    seed = (i // 4) % 3 * 10
    rng = random.Random(i)
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    m, v = man(t, seed), vrouw(t, seed)

    # tv en router
    x0, y0, x1, y1 = TV_SCHERM
    frame.paste(spel(t, tv_staat(t), (x1 - x0) * Z, (y1 - y0) * Z), (x0 * Z, y0 * Z))
    rx0, ry0, rx1, ry1 = ROUTER
    for ax, bx in ((rx0 + 8, rx0 - 4), (rx1 - 8, rx1 + 4)):
        d.line(R(ax, ry0, bx, ry0 - 40), fill=INK, width=5 * Z)
    d.rounded_rectangle(R(*ROUTER), radius=6 * Z, fill=(60, 62, 72), outline=INK, width=4 * Z)
    for k in range(3):
        aan = router_aan(t) and (k < 2 or int(t * 6) % 2 == 0)
        kl = (90, 255, 120) if aan else (60, 60, 60)
        cx = rx0 + 14 + k * 16
        d.ellipse(R(cx - 4, ry0 + 16, cx + 4, ry0 + 24), fill=kl)
        if aan and 26.6 <= t < 27.3:
            d.ellipse(R(cx - 9, ry0 + 11, cx + 9, ry0 + 29), outline=(150, 255, 170), width=2 * Z)
    stekker = v.get("stekker")
    if t < 19.8:
        d.line(R(rx1, ry1 - 8, 505, 728, STOP[0] - 6, STOP[1]), fill=INK, width=5 * Z, joint="curve")
        d.rectangle(R(STOP[0] - 10, STOP[1] - 8, STOP[0] + 4, STOP[1] + 8), fill=(240, 240, 240), outline=INK, width=2 * Z)
    else:
        eind = stekker if stekker else (585, 792)
        d.line(R(rx1, ry1 - 8, 500, 760, eind[0], eind[1]), fill=INK, width=5 * Z, joint="curve")
        d.rectangle(R(eind[0] - 7, eind[1] - 8, eind[0] + 7, eind[1] + 8), fill=(240, 240, 240), outline=INK, width=2 * Z)

    # grote schaduw van Lotte op de muur (finale)
    if t >= 30.9:
        laag, ox, oy, _ = plak_laag(v)
        a = laag.getchannel("A").point(lambda q: int(q * 0.5 * fase(t, 30.9, 31.4)))
        k = 1.9
        a = a.resize((int(a.width * k), int(a.height * k)), Image.BILINEAR).filter(ImageFilter.GaussianBlur(6 * Z))
        voet_x, voet_y = v["x"] * Z, v["y"] * Z
        sx0 = int(voet_x - (voet_x - ox) * k - 120 * Z)
        sy0 = int(voet_y - (voet_y - oy) * k - 120 * Z)
        a = a.crop((0, 0, a.width, max(1, VLOER * Z - sy0)))
        frame.paste((60, 40, 50), (sx0, sy0), a)

    # Lotte achter het aanrecht of achter de bank
    achter = v["y"] < 770
    if achter:
        laag, ox, oy, vi = plak_laag(v)
        frame.paste(laag, (ox, oy), laag)
    frame.paste(AANRECHT, (0, 0), AANRECHT)
    if t < 5.2:  # stoom uit de pan
        for k in range(3):
            u = (t * 0.7 + k / 3) % 1
            cx, cy, r = 915 + math.sin(u * 6 + k) * 15, 530 - u * 110, 10 + u * 18
            d.ellipse(R(cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255), outline=(225, 225, 225))
    frame.paste(BANK, (0, 0), BANK)
    if 12.1 <= t < 13.3:
        bord(d, *BORD_TAFEL, 84)
    if t >= 14.6:  # scherven en eten op de vloer
        bx, by = BORD_VLOER
        for k, (dx, dy, kl) in enumerate(((-70, 5, (250, 250, 250)), (40, -10, (250, 250, 250)), (95, 12, (250, 250, 250)),
                                           (-10, 15, (200, 120, 60)), (60, 22, (90, 170, 80)), (-60, 25, (240, 200, 80)))):
            r = 18 if k < 3 else 22
            d.polygon(R(bx + dx - r, by + dy, bx + dx, by + dy - r * 0.5, bx + dx + r, by + dy + 3, bx + dx, by + dy + r * 0.4),
                      fill=kl, outline=INK)

    # personages vooraan, op diepte gesorteerd
    figs = []
    if not achter:
        figs.append((v["y"], "v"))
    figs.append((m["diepte"], "m"))
    for _, wie in sorted(figs):
        st = v if wie == "v" else m
        grondschaduw(d, st["x"], st["y"], st["s"], st["hop"] if st["rot"] == 0 else 0)
        laag, ox, oy, info = plak_laag(st)
        frame.paste(laag, (ox, oy), laag)
        st["info"] = info
    if achter:
        v["info"] = vi

    # wat ze vasthouden
    mi, vi = m["info"], v["info"]
    hl, hr = (mi["naar"](*h) for h in mi["handen"])
    c = m.get("controller")
    if c == "beide":
        controller(d, (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2, m["s"], m["rot"] * -1)
    elif c in ("links", "rechts"):
        hx, hy = hl if c == "links" else hr
        controller(d, hx, hy - 0.05 * m["s"], m["s"], -20 if c == "links" else 20)
    elif c == "vallend":
        u = fase(t, 20.8, 21.3)
        cx = lerp((hl[0] + hr[0]) / 2, 1440, u)
        cy = lerp((hl[1] + hr[1]) / 2, 1000, u * u)
        controller(d, cx, cy, m["s"], u * 200)
    if 21.3 <= t < 23.6:
        controller(d, 1440, 1000, m["s"], 200)
    if m.get("duim"):
        emoji(frame, m["duim"], hr[0], hr[1] - 25, 70)
    if m.get("handen_emoji"):
        pop(frame, t, 23.15, 23.6, "🙏", (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2 - 70, 70)
    if m.get("bloem"):
        emoji(frame, "🌹", hr[0], hr[1] - 30, 80, rot=20)
    vl, vr = (vi["naar"](*h) for h in vi["handen"])
    if v["houd"] == "bord":
        bp = v.get("bord_pos") or ((vl[0] + vr[0]) / 2, (vl[1] + vr[1]) / 2)
        bord(d, bp[0], bp[1] - 8, v["s"])
    elif v["houd"] == "deegroller" and t < 30.4:
        deegroller(d, (vl[0] + vr[0]) / 2, (vl[1] + vr[1]) / 2, v["s"])
    elif v["houd"] == "deegroller":  # rechtop in haar hand, naast haar hoofd
        hx, hy, s_ = vr[0] + 0.45 * v["s"], vr[1] + 0.2 * v["s"], v["s"] * 1.5
        d.rounded_rectangle(R(hx - 0.06 * s_, hy, hx + 0.06 * s_, hy + 0.35 * s_), radius=0.05 * s_ * Z,
                            fill=(180, 130, 80), outline=INK, width=3 * Z)
        d.rounded_rectangle(R(hx - 0.14 * s_, hy - 1.25 * s_, hx + 0.14 * s_, hy + 0.02 * s_), radius=0.12 * s_ * Z,
                            fill=(215, 170, 110), outline=INK, width=4 * Z)
        d.rounded_rectangle(R(hx - 0.06 * s_, hy - 1.55 * s_, hx + 0.06 * s_, hy - 1.23 * s_), radius=0.05 * s_ * Z,
                            fill=(180, 130, 80), outline=INK, width=3 * Z)
    if 13.3 <= t < 14.6:  # slow-motion bord en rondvliegend eten
        bx, by, hoek = bord_vlucht(t)
        u = fase(t, 13.3, 14.6)
        bord(d, bx, by, 84, eten=False)
        for k, kl in enumerate(((200, 120, 60), (90, 170, 80), (240, 200, 80))):
            ex = bx + (k - 1) * 70 * u + math.sin(u * 5 + k) * 20
            ey = by - 40 - 90 * math.sin(u * math.pi) * (0.6 + 0.3 * k) + 40 * u
            r = 16 + k * 3
            d.ellipse(R(ex - r, ey - r, ex + r, ey + r), fill=kl, outline=INK, width=3 * Z)

    # ---------------- emoji's en effecten
    mk = mi["kop"]
    mkx, mky = mi["naar"](mk[0], mk[1])
    mr = mk[2] / Z
    vk = vi["kop"]
    vkx, vky = vi["naar"](vk[0], vk[1])
    vr_ = vk[2] / Z
    pop(frame, t, 0.4, 2.8, "🎮", mkx - 40, mky - mr - 60, 80)
    for k, (tt, ex, ey) in enumerate(((0.6, 90, 400), (1.2, 410, 450), (1.8, 120, 640), (2.3, 400, 620), (2.8, 250, 395))):
        pop(frame, t, tt, tt + 0.5, "💥" if k % 2 == 0 else "✨", ex, ey, 70, zweef=False)
    pop(frame, t, 3.45, 4.8, "🏆", mkx - 120, mky - mr - 40, 100)
    pop(frame, t, 3.6, 4.8, "🔥", mkx + 120, mky - mr - 30, 90)
    if t < 2.6:
        pop(frame, t, 1.7, 2.6, "❤️", vkx + 60, vky - vr_ - 30, 45)
    if v.get("hart"):
        pop(frame, t, 8.55, 9.1, "❤️", v["hart"][0], v["hart"][1] - 30, 60)
    pop(frame, t, 9.0, 9.4, "➡️", vkx - vr_ - 50, vky, 60, flip=True)
    pop(frame, t, 9.65, 10.0, "😐", vkx + vr_ + 30, vky - vr_, 55)
    pop(frame, t, 9.95, 10.6, "💢", vkx + vr_ * 0.7, vky - vr_ * 0.8, 55)
    pop(frame, t, 13.4, 14.6, "🍽️", 1280, 700, 70)
    pop(frame, t, 14.6, 15.0, "💥", BORD_VLOER[0], BORD_VLOER[1] - 30, 120, zweef=False)
    if 15.0 <= t < 16.6:  # onweerswolkje
        cx, cy = vkx, vky - vr_ - 75
        wolk(d, cx, cy, 34)
        if int(t * 8) % 3 != 0:
            d.polygon(R(cx - 5, cy + 20, cx + 12, cy + 20, cx + 2, cy + 45, cx + 16, cy + 45, cx - 10, cy + 80, cx - 2, cy + 52,
                        cx - 14, cy + 52), fill=(255, 220, 40), outline=INK)
        for k in range(5):
            ry = cy + 30 + ((t * 3 + k * 0.2) % 1) * 50
            rx = cx - 40 + k * 20
            d.line(R(rx, ry, rx - 4, ry + 12), fill=(90, 140, 230), width=3 * Z)
    if 15.8 <= t < 17.0:
        pop(frame, t, 16.0, 17.0, "💦", mkx + mr + 10, mky - mr * 0.5, 50)
        pop(frame, t, 16.1, 17.0, "😳", mkx - mr - 40, mky - mr, 55)
    if 16.65 <= t < 17.6:  # gloeilamp met gloed
        u = fase(t, 16.65, 16.9)
        gx, gy = vkx, vky - vr_ - 70
        r = 60 * terug(u) * (1 + 0.08 * math.sin(t * 20))
        gl = Image.new("RGBA", (int(r * 4 * Z), int(r * 4 * Z)), (0, 0, 0, 0))
        ImageDraw.Draw(gl).ellipse((r * Z, r * Z, 3 * r * Z, 3 * r * Z), fill=(255, 240, 120, 110))
        gl = gl.filter(ImageFilter.GaussianBlur(r * Z * 0.35))
        frame.paste(gl, (int(gx * Z - 2 * r * Z), int(gy * Z - 2 * r * Z)), gl)
        pop(frame, t, 16.65, 17.6, "💡", gx, gy, 85)
        pop(frame, t, 17.0, 17.6, "😈", gx + 80, gy + 30, 45)
    if 20.05 <= t < 20.5:
        pop(frame, t, 20.0, 20.5, "🔌", STOP[0] + 50, STOP[1] - 40, 40)
    pop(frame, t, 20.8, 21.6, "😱", mkx - mr - 60, mky - mr * 0.6, 70)
    pop(frame, t, 21.1, 22.2, "💀", mkx + mr + 50, mky - mr * 0.8, 70)
    pop(frame, t, 23.1, 24.0, "🥺", mkx + mr + 35, mky - mr * 0.6, 55)
    if m.get("hart"):
        pop(frame, t, 24.15, 24.6, "❤️", m["hart"][0], m["hart"][1] - 55, 60)
    if 25.6 <= t < 27.3:  # hartjes en sterretjes
        for k in range(6):
            u = ((t - 25.6) * 0.6 + k / 6) % 1
            hx = 650 + math.sin(k * 2.1 + t) * 110
            hy = 520 - u * 220
            emoji(frame, "❤️" if k % 2 == 0 else "✨", hx, hy, 40 + 15 * math.sin(u * math.pi), klem(math.sin(u * math.pi) * 1.5))
    pop(frame, t, 26.65, 27.0, "📶", 435, 590, 40)
    pop(frame, t, 26.7, 27.0, "✨", 475, 620, 35)
    pop(frame, t, 27.8, 28.2, "💨", 680, 860, 90, zweef=False)
    pop(frame, t, 28.4, 29.4, "🏆", mkx - 120, mky - mr - 40, 90)
    pop(frame, t, 28.5, 29.4, "🎮", mkx + 120, mky - mr - 30, 80)
    pop(frame, t, 29.35, 30.3, "😈", vkx + vr_ + 30, vky - vr_, 55)
    if 31.25 <= t < 31.7:
        pop(frame, t, 31.25, 31.7, "😇", vkx, vky - vr_ - 50, 55)
    elif t >= 31.7:
        pop(frame, t, 31.7, 40, "😈", vkx, vky - vr_ - 50, 55)
    if t >= 31.6:
        pop(frame, t, 31.6, 40, "💦", mkx + mr + 5, mky - mr * 0.4, 35)
    pop(frame, t, 31.95, 40, "💀", mkx, mky - mr - 70, 110)
    return frame


def beeld(i):
    t = i / FPS
    tp = min(t, FREEZE)
    rng = random.Random(i)
    if 20.1 <= t < 20.7 or 27.0 <= t < 27.3:  # harde cut naar het tv-scherm
        out = Image.new("RGB", (W, H), (30, 26, 34))
        bw, bh = 1500, 840
        zoom = 1 + 0.06 * fase(t, 20.1, 20.7)
        bw2, bh2 = int(bw * zoom), int(bh * zoom)
        ImageDraw.Draw(out).rounded_rectangle(((W - bw2) / 2 - 30, (H - bh2) / 2 - 30, (W + bw2) / 2 + 30, (H + bh2) / 2 + 30),
                                              radius=30, fill=(18, 18, 24), outline=(0, 0, 0), width=8)
        out.paste(spel(t, tv_staat(t), bw2, bh2), ((W - bw2) // 2, (H - bh2) // 2))
        return out.tobytes()
    frame = scene(tp, int(tp * FPS))
    cx, cy, z = camera(t)
    sch = 0
    if 20.75 <= t < 21.2:
        sch = 14 * (1 - fase(t, 20.75, 21.2))
    elif 21.5 <= t < 21.8:
        sch = 12 * (1 - fase(t, 21.5, 21.8))
    elif 15.0 <= t < 15.15:
        sch = 8
    elif FREEZE <= t < FREEZE + 0.2:
        sch = 10 * (1 - fase(t, FREEZE, FREEZE + 0.2))
    cx += rng.uniform(-sch, sch) / z
    cy += rng.uniform(-sch, sch) / z
    vw, vh = W / z, H / z
    cx = klem(cx, vw / 2, W - vw / 2)
    cy = klem(cy, vh / 2, H - vh / 2)
    box = tuple(int(c * Z) for c in (cx - vw / 2, cy - vh / 2, cx + vw / 2, cy + vh / 2))
    out = frame.crop(box).resize((W, H), Image.BICUBIC)
    if t >= FREEZE:  # freeze frame: witte flits, daarna 😂
        u = fase(t, FREEZE, FREEZE + 0.15)
        if u < 1:
            out = Image.blend(out, Image.new("RGB", (W, H), (255, 255, 255)), 0.7 * (1 - u))
        if t >= FREEZE + 0.35:
            e = emoji_basis("😂")
            k = terug(fase(t, FREEZE + 0.35, FREEZE + 0.6))
            hh = max(2, int(200 * k))
            e = e.resize((int(e.width * hh / e.height), hh), Image.LANCZOS)
            out.paste(e, (W - 300 - e.width // 2, H - 230 - hh // 2), e)
    return out.tobytes()


# ================================================================ geluid
SR = 44100


def geluid(duur):
    n = int(duur * SR)
    mx = np.zeros(n)
    rng = np.random.default_rng(7)

    def zet(start, sig, vol=1.0):
        a = int(start * SR)
        b = min(n, a + len(sig))
        if 0 <= a < b:
            mx[a:b] += sig[: b - a] * vol

    def tt(d):
        return np.arange(int(d * SR)) / SR

    def env(d, aan=0.01, uit=0.1):
        t = tt(d)
        return np.minimum(1, t / aan) * np.clip(np.minimum(1, (d - t) / uit), 0, 1)

    def zaag(f, t):
        return 2 * ((f * t) % 1) - 1

    def blok(f, t):
        return np.sign(np.sin(2 * np.pi * f * t))

    def sweep(f0, f1, d):
        t = tt(d)
        return np.cumsum(f0 * (f1 / f0) ** (t / d)) / SR

    def ruis(d):
        return rng.standard_normal(int(d * SR))

    def tokkel(f, d=0.4, demp=10):
        t = tt(d)
        return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(6 * np.pi * f * t)) * np.exp(-t * demp)

    # chiptune tijdens het gamen
    akk = [(261.6, 329.6, 392.0), (220.0, 261.6, 329.6), (174.6, 220.0, 261.6), (196.0, 246.9, 293.7)]
    for a, b in ((0, 5.0), (10.6, 13.3), (27.05, 31.2)):
        st, k = a, 0
        while st < b - 0.05:
            ch = akk[(k // 8) % 4]
            t = tt(0.11)
            zet(st, blok(ch[k % 3] * 2, t) * env(0.11, 0.003, 0.04), 0.05)
            if k % 2 == 0:
                t = tt(0.2)
                zet(st, blok(ch[0] / 2, t) * env(0.2, 0.003, 0.05), 0.05)
            st += 0.125
            k += 1
    # knopjes rammen
    for a, b, dicht in ((0, 3.0, 0.06), (4.8, 7.5, 0.1), (10.6, 13.0, 0.09), (13.6, 15.8, 0.1), (17.0, 20.0, 0.12),
                        (29.0, 31.2, 0.055)):
        st = a
        while st < b:
            t = tt(0.015)
            zet(st, ruis(0.015) * np.exp(-t * 300), 0.12)
            st += dicht * rng.uniform(0.7, 1.3)
    for st in (0.6, 1.2, 1.8, 2.3, 2.8):  # ontploffingen op de tv
        t = tt(0.4)
        zet(st, np.convolve(ruis(0.4), np.ones(20) / 20, "same") * np.exp(-t * 9) * 3, 0.25)
    def jingle(st, vol=0.18):  # overwinning
        for k, f in enumerate((523.3, 659.3, 784.0, 1046.5)):
            d = 0.12 if k < 3 else 0.45
            t = tt(d)
            zet(st + k * 0.1, blok(f, t) * env(d, 0.005, 0.1), vol)
    jingle(3.4)
    jingle(13.05)
    jingle(28.35)
    t = tt(0.3)
    zet(3.0, np.sin(2 * np.pi * sweep(250, 900, 0.3)) * env(0.3, 0.01, 0.05), 0.2)  # sprong
    # voetstappen
    for a, b, dt, f in ((5.0, 6.3, 0.27, 1.0), (10.6, 11.8, 0.27, 1.0), (29.6, 31.2, 0.42, 0.55)):
        for st in np.arange(a, b, dt):
            t = tt(0.08)
            zet(st, np.sin(2 * np.pi * 120 * f * t) * np.exp(-t * 50) + ruis(0.08) * np.exp(-t * 90) * 0.3, 0.35)
    # romantische harp (5.0-9.6) en later (22.9-26.6)
    harp = [261.6, 329.6, 392.0, 523.3, 659.3, 523.3, 392.0, 329.6, 349.2, 440.0, 523.3, 698.5, 880.0, 698.5, 523.3, 440.0]
    for a, b in ((5.0, 9.6), (22.9, 26.6)):
        for k, st in enumerate(np.arange(a, b, 0.14)):
            zet(st, tokkel(harp[k % len(harp)], 0.9, 4) * env(0.9, 0.003, 0.3), 0.09)
        t = tt(b - a)
        pad_ = sum(np.sin(2 * np.pi * f * t) for f in (130.8, 196.0, 261.6)) / 3
        zet(a, pad_ * env(b - a, 0.6, 0.05), 0.06)
    # gebaartjes
    for st in (6.35, 6.65):
        zet(st, np.convolve(ruis(0.18), np.ones(40) / 40, "same") * env(0.18, 0.05, 0.1) * 2, 0.15)
    for st in (7.08, 7.3):
        t = tt(0.05)
        zet(st, np.sin(2 * np.pi * 1200 * t) * np.exp(-t * 80), 0.25)
    zet(7.55, tokkel(1568, 0.5, 8), 0.2)
    zet(8.55, np.sin(2 * np.pi * sweep(500, 900, 0.18)) * env(0.18, 0.01, 0.05), 0.2)
    zet(9.35, tokkel(1046.5, 0.25, 15), 0.2)
    # platenkras
    def kras(st, vol=0.4):
        t = tt(0.45)
        f = 300 + 900 * np.abs(np.sin(2 * np.pi * 3 * t))
        zet(st, np.convolve(ruis(0.45), np.ones(6) / 6, "same") * np.sin(2 * np.pi * np.cumsum(f) / SR) * env(0.45, 0.01, 0.1), vol)
    kras(9.6)
    for st in (10.0, 10.15, 10.3, 10.45):  # oog trilt
        zet(st, tokkel(2400, 0.08, 40), 0.12)
    for k, st in enumerate(np.arange(12.15, 13.3, 0.25)):  # tik-tak + voet
        t = tt(0.04)
        zet(st, np.sin(2 * np.pi * (1800 if k % 2 else 1400) * t) * np.exp(-t * 120), 0.25)
    t = tt(1.3)  # slow motion zoef
    zet(13.3, np.convolve(ruis(1.3), np.ones(80) / 80, "same") * np.sin(np.pi * t / 1.3) * 4, 0.2)
    zet(13.3, np.sin(2 * np.pi * sweep(300, 90, 1.3)) * env(1.3, 0.2, 0.2), 0.12)
    t = tt(0.8)  # bord kapot
    scherven = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * rng.uniform(8, 20)) for f in (2300, 3100, 3900, 4700, 5600))
    zet(14.6, scherven * 0.4 + ruis(0.8) * np.exp(-t * 14) * 0.8, 0.45)
    t = tt(2.0)  # donder
    zet(15.0, np.convolve(ruis(2.0), np.ones(300) / 300, "same") * np.exp(-t * 1.6) * 25, 0.6)
    for st in np.arange(15.8, 16.6, 0.4):  # hartslag
        for dt in (0, 0.13):
            t = tt(0.12)
            zet(st + dt, np.sin(2 * np.pi * sweep(70, 45, 0.12)) * np.exp(-t * 25), 0.55)
    zet(16.65, tokkel(1760, 0.8, 5) + tokkel(2637, 0.8, 6), 0.18)  # ding! idee
    for k, st in enumerate(np.arange(17.4, 19.0, math.pi / 7)):  # sluipmuziek
        zet(st, tokkel([164.8, 196.0, 174.6, 207.7][k % 4], 0.3, 14), 0.35)
    for st in (19.03, 19.28):
        zet(st, np.convolve(ruis(0.15), np.ones(30) / 30, "same") * env(0.15, 0.03, 0.08) * 2, 0.2)
    t = tt(0.5)  # spanning
    zet(19.5, zaag(110, t) * (0.5 + 0.5 * np.sin(2 * np.pi * 14 * t)) * env(0.5, 0.05, 0.05), 0.12)
    t = tt(0.03)
    zet(20.0, ruis(0.03) * np.exp(-t * 200), 0.6)  # klik
    for k, f in enumerate((880, 660, 440)):  # verbinding weg
        t = tt(0.12)
        zet(20.15 + k * 0.14, blok(f, t) * env(0.12, 0.005, 0.03), 0.15)
    t = tt(0.9)  # schrik-akkoord
    zet(20.75, sum(zaag(f, t) for f in (98, 116.5, 146.8)) / 3 * np.exp(-t * 3), 0.35)
    t = tt(0.5)  # plof achterover
    zet(21.55, np.sin(2 * np.pi * sweep(100, 40, 0.5)) * np.exp(-t * 7) + ruis(0.5) * np.exp(-t * 25) * 0.4, 0.7)
    zet(22.2, np.sin(2 * np.pi * sweep(600, 200, 0.4)) * env(0.4, 0.02, 0.1), 0.12)  # glijden
    t = tt(0.6)
    zet(23.1, np.sin(2 * np.pi * (sweep(950, 700, 0.6) + 0.004 * np.sin(2 * np.pi * 8 * t))) * env(0.6, 0.05, 0.1), 0.12)
    zet(24.15, np.sin(2 * np.pi * sweep(500, 900, 0.18)) * env(0.18, 0.01, 0.05), 0.2)
    for k, f in enumerate((1318.5, 1568, 2093, 2637, 3136)):  # tover-glitter bij het roosje
        zet(25.3 + k * 0.06, tokkel(f, 0.6, 7), 0.08)
    zet(26.65, tokkel(1318.5, 0.6, 6), 0.2)  # router ding-dong
    zet(26.8, tokkel(1760, 0.8, 5), 0.2)
    for k, f in enumerate((392, 523.3, 659.3, 784, 1046.5)):  # spel weer verbonden
        t = tt(0.08)
        zet(27.0 + k * 0.05, blok(f, t) * env(0.08, 0.003, 0.02), 0.13)
    zet(27.8, np.convolve(ruis(0.45), np.ones(25) / 25, "same") * env(0.45, 0.05, 0.2) * 3, 0.3)  # duik
    t = tt(0.3)
    zet(28.25, np.sin(2 * np.pi * sweep(120, 50, 0.3)) * np.exp(-t * 12), 0.6)
    t = tt(0.5)
    zet(29.35, zaag(73.4, t) * np.exp(-t * 4), 0.25)  # duivelse 'dun'
    t = tt(1.0)  # horror
    hor = sum(zaag(f, t) for f in (220, 233.1, 311.1, 466.2)) / 4 * (0.6 + 0.4 * np.sin(2 * np.pi * 11 * t))
    zet(31.3, hor * env(1.0, 0.2, 0.1), 0.3)
    for st in np.arange(31.5, 32.3, 0.27):
        for dt in (0, 0.1):
            t = tt(0.1)
            zet(st + dt, np.sin(2 * np.pi * sweep(70, 45, 0.1)) * np.exp(-t * 28), 0.55)
    t = tt(0.8)  # klap bij de freeze
    zet(FREEZE, np.sin(2 * np.pi * sweep(150, 35, 0.8)) * np.exp(-t * 5) + ruis(0.8) * np.exp(-t * 20) * 0.5, 0.8)
    t = tt(0.15)  # ba-dum-tss
    trom = np.sin(2 * np.pi * sweep(220, 120, 0.15)) * np.exp(-t * 25)
    zet(FREEZE + 0.55, trom, 0.5)
    zet(FREEZE + 0.72, trom, 0.5)
    t = tt(0.9)
    zet(FREEZE + 0.9, np.diff(ruis(0.9 + 1 / SR)[: len(t) + 1]) * np.exp(-t * 4), 0.15)
    mx /= max(1e-9, np.abs(mx).max()) / 0.89
    return mx


def schrijf_wav(pad_, sig):
    with wave.open(str(pad_), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((sig * 32767).astype(np.int16).tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uit", nargs="?", default="poppetjes/gaming-vs-wife.mp4")
    ap.add_argument("--beeld", type=float, help="alleen een still op deze tijd (png)")
    ap.add_argument("--van", type=float, default=0.0)
    ap.add_argument("--tot", type=float, default=DUUR)
    a = ap.parse_args()
    uit = Path(a.uit)
    uit.parent.mkdir(parents=True, exist_ok=True)
    if a.beeld is not None:
        init()
        Image.frombytes("RGB", (W, H), beeld(int(round(a.beeld * FPS)))).save(uit)
        print(uit)
        return
    wav = uit.with_suffix(".wav")
    sig = geluid(DUUR)[int(a.van * SR): int(a.tot * SR)]
    schrijf_wav(wav, sig)
    frames = range(int(a.van * FPS), int(a.tot * FPS))
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                           "-movflags", "+faststart", str(uit)], stdin=subprocess.PIPE)
    with Pool(initializer=init) as pool:
        for k, data in enumerate(pool.imap(beeld, frames, chunksize=3)):
            ff.stdin.write(data)
            if k % 150 == 0:
                print(f"  {a.van + k / FPS:.0f} s", flush=True)
    ff.stdin.close()
    ff.wait()
    wav.unlink()
    print(uit)


if __name__ == "__main__":
    main()
