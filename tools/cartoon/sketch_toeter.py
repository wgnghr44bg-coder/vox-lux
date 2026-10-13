"""Test-sketch (Short, 1080x1920, ± 12 s): Kees wekt Ome Gert met een toeter.

Ome Gert slaapt, Kees sluipt naar hem toe, TOEEET!, Gert vliegt de lucht in, landt,
wordt rood van woede en jaagt Kees weg. Bram en Lotte liggen dubbel.
Beeld en geluid zijn helemaal met code gemaakt (gratis, geen auteursrecht).

Gebruik: python3 tools/cartoon/sketch_toeter.py [uit.mp4] [--tot SECONDEN]
"""
import argparse
import math
import random
import subprocess
import sys
import wave
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from poppetjes2 import INK, bram, gert, kees, lotte  # noqa: E402

W, H, FPS, DUUR = 1080, 1920, 30, 12.5
S = 2  # poppetjes op dubbele grootte tekenen, dan verkleinen
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
VLOER = 1350
ACHTER_Y, VOOR_Y = 1440, 1790
ACHTER_S, VOOR_S = 72, 100


def klem(v, a=0.0, b=1.0):
    return max(a, min(b, v))


def fase(t, a, b):
    """0..1 tussen tijd a en b."""
    return klem((t - a) / (b - a))


def zacht(x):
    return x * x * (3 - 2 * x)


# ---------------------------------------------------------------- achtergrond
def achtergrond():
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    for y in range(VLOER):
        d.line((0, y, W, y), fill=tuple(int(a + (b - a) * y / VLOER) for a, b in zip((246, 230, 204), (232, 208, 176))))
    for x in range(0, W, 90):  # behang
        d.line((x, 0, x, VLOER), fill=(238, 220, 192), width=18)
    d.rectangle((0, VLOER, W, H), fill=(178, 128, 88))
    for y in range(VLOER + 70, H, 95):  # planken
        d.line((0, y, W, y), fill=(160, 112, 76), width=4)
        off = (y * 7) % 300
        for x in range(off, W, 300):
            d.line((x, y, x, y + 95), fill=(160, 112, 76), width=3)
    d.rectangle((0, VLOER - 30, W, VLOER), fill=(250, 245, 235), outline=INK, width=5)
    # raam
    d.rectangle((600, 420, 980, 820), fill=(160, 210, 245), outline=INK, width=8)
    d.ellipse((860, 470, 940, 550), fill=(255, 230, 120))
    d.ellipse((640, 640, 800, 700), fill=(250, 250, 255))
    d.ellipse((700, 610, 820, 680), fill=(250, 250, 255))
    d.line((790, 420, 790, 820), fill=(250, 245, 235), width=14)
    d.line((600, 620, 980, 620), fill=(250, 245, 235), width=14)
    d.rectangle((600, 420, 980, 820), outline=INK, width=8)
    d.rectangle((580, 815, 1000, 845), fill=(250, 245, 235), outline=INK, width=5)
    # schilderij
    d.rectangle((110, 470, 410, 700), fill=(200, 230, 210), outline=(120, 80, 50), width=16)
    d.polygon([(130, 685), (230, 540), (300, 640), (340, 590), (395, 685)], fill=(110, 150, 120))
    d.rectangle((110, 470, 410, 700), outline=INK, width=4)
    # plant
    d.polygon([(905, 1180), (1015, 1180), (995, 1330), (925, 1330)], fill=(200, 110, 70), outline=INK)
    for a in range(-60, 61, 30):
        r = math.radians(a - 90)
        d.ellipse((960 + math.cos(r) * 90 - 35, 1150 + math.sin(r) * 110 - 60,
                   960 + math.cos(r) * 90 + 35, 1150 + math.sin(r) * 110 + 60), fill=(90, 160, 90), outline=INK, width=4)
    return img


# ---------------------------------------------------------------- poppetjes plakken
def plak(frame, fn, x, y, s, p, sx=1.0, sy=1.0, rot=0.0, hop=0.0):
    """Teken poppetje op een eigen laag, rek/pers/draai het en plak het met de voeten op (x, y - hop).
    Geeft een functie terug die laagpunten (bv. handen) naar beeldcoördinaten omrekent."""
    ls = s * S
    lw, lh = int(6.4 * ls), int(7.8 * ls)
    voet = lh - int(0.4 * ls)
    laag = Image.new("RGBA", (lw, lh), (0, 0, 0, 0))
    info = fn(laag, lw / 2, voet, ls, {**p, "schaduw": False})
    nw, nh = max(1, int(lw / S * sx)), max(1, int(lh / S * sy))
    laag = laag.resize((nw, nh), Image.LANCZOS)
    ax, ay = nw / 2, voet / S * sy
    if rot:
        laag = laag.rotate(rot, resample=Image.BICUBIC, center=(ax, ay))
    ox, oy = int(x - ax), int(y - hop - ay)
    frame.paste(laag, (ox, oy), laag)
    th = math.radians(rot)

    def naar(px, py):
        qx, qy = px / S * sx - ax, py / S * sy - ay
        return (ox + ax + qx * math.cos(th) + qy * math.sin(th), oy + ay - qx * math.sin(th) + qy * math.cos(th))

    info["naar"] = naar
    return info


def grondschaduw(d, x, y, s, hop=0.0):
    k = klem(1 - hop / 900, 0.3, 1)
    d.ellipse((x - s * 0.95 * k, y - s * 0.13 * k, x + s * 0.95 * k, y + s * 0.13 * k), fill=(150, 104, 70))


def tekst(d, xy, t, grootte, kleur=(255, 255, 255), rand=10, anchor="mm"):
    f = ImageFont.truetype(FONT, int(grootte))
    d.text(xy, t, font=f, fill=kleur, stroke_width=rand, stroke_fill=INK, anchor=anchor)


def ondertitel(d, t, alpha=1.0):
    if alpha <= 0:
        return
    f = ImageFont.truetype(FONT, 58)
    l, tp, r, b = d.textbbox((W / 2, 230), t, font=f, anchor="mm")
    d.rounded_rectangle((l - 34, tp - 24, r + 34, b + 24), radius=26, fill=(255, 255, 255), outline=INK, width=6)
    d.text((W / 2, 230), t, font=f, fill=INK, anchor="mm")


# ---------------------------------------------------------------- de scène per beeldje
BG = None


def init():
    global BG
    BG = achtergrond()


def beeld(i):
    t = i / FPS
    seed = (i // 4) % 3 * 10  # 'kokende' lijnen: elke 4 beeldjes een andere wiebel
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    rng = random.Random(i)

    # ---- posities en poses
    TOET, PIEK, LAND, BOOS, REN = 5.0, 5.6, 6.2, 6.45, 7.6
    # Ome Gert
    gx, ghop, gsx, gsy, grot = 640.0, 0.0, 1.0, 1.0, 0.0
    gp = {"seed": seed}
    if t < TOET:
        gsy = 1 + 0.025 * math.sin(2 * math.pi * t / 2)
        gsx = 1 - 0.012 * math.sin(2 * math.pi * t / 2)
        gp.update(lid=1)
    elif t < LAND:
        u = (t - PIEK) / (PIEK - TOET)
        ghop = 650 * (1 - u * u)
        gsy, gsx = 1.15, 0.9
        w = math.sin(t * 34) * 30
        gp.update(lid=0, pupil=0.2, kijk=(0, 0), mond="open", armen=((-125 + w, -20), (-55 - w, 20)))
    elif t < BOOS:
        k = 1 - fase(t, LAND, BOOS)
        gsy, gsx = 1 - 0.3 * k, 1 + 0.25 * k
        gp.update(lid=0, pupil=0.2, kijk=(0, 0.3), mond="open")
    else:
        rood = 0.75 * zacht(fase(t, BOOS, BOOS + 0.4))
        gp.update(lid=0.3, wenk="boos", mond="boos", kijk=(-0.8, 0), rood=rood,
                  armen=((105, -25), (75, 25)))
        if t < REN + 0.3:
            gx += rng.uniform(-5, 5)
        else:
            u = fase(t, REN + 0.3, 9.3)
            gx = 640 - 960 * u
            gp.update(loop=(t * 20, 0.3), armen=((190, -10), (170, 10)))
            grot = 12
            ghop = abs(math.sin(t * 20)) * 14
    # Kees
    kx, khop, krot = -250.0, 0.0, 0.0
    kp = {"seed": seed}
    hoorn = False
    if 2.0 <= t < 4.3:
        u = fase(t, 2.0, 4.3)
        kx = -150 + 480 * u
        kp.update(loop=(t * 9, 0.25), armen=((-150, 70), (-30, -70)), kijk=(0.8, 0.3))
        khop = abs(math.sin(t * 9)) * 12
    elif 4.3 <= t < REN:
        kx = 330
        hoorn = True
        kp.update(armen=((115, 40), (-35, -15)))
        if t < TOET:
            kp.update(kijk=(-0.1, 0), lid=0.4)  # gemeen naar de kijker
        elif t < BOOS:
            kp.update(kijk=(0.4, -0.9 if t < PIEK + 0.3 else -0.2))
            if t < TOET + 0.85:
                kx += rng.uniform(-3, 3)
        else:
            hoorn = t < 7.0
            kp.update(pupil=0.22, wenk="op", mond="o", kijk=(0.8, 0))
            kx += rng.uniform(-2.5, 2.5)
            if not hoorn:
                kp.update(armen=((-120, -30), (-60, 30)))
    elif t >= REN:
        u = fase(t, REN, 8.5)
        kx = 330 - 650 * u
        w = math.sin(t * 25) * 40
        kp.update(loop=(t * 25, 0.4), pupil=0.22, wenk="op", mond="open", kijk=(-0.8, 0),
                  armen=((200 + w, -40), (160 - w, 40)))
        krot = 14
        khop = abs(math.sin(t * 25)) * 18
    # Bram en Lotte
    bp, lp = {"seed": seed}, {"seed": seed}
    bx, lx, bhop, lhop = 270.0, 820.0, 0.0, 0.0
    if t < 2.0:
        lp.update(kijk=(-0.4, 0.5))
    elif t < TOET:
        sh = math.sin(t * 70) * 3
        bx += sh
        lx -= sh
        bp.update(armen=((-60, -30), (-120, 30)))
        lp.update(armen=((-60, -30), (-120, 30)), kijk=(-0.8, 0.4), lid=0.35)
    elif t < BOOS:
        bp.update(mond="o", armen=((-130, -20), (-50, 20)))
        lp.update(mond="open", pupil=0.25, kijk=(-0.4, 0), armen=((-130, -20), (-50, 20)))
        bhop = lhop = 30 * math.sin(fase(t, TOET, TOET + 0.4) * math.pi)
    elif t < REN:
        bp.update(mond="o")
        lp.update(mond="o", kijk=(-0.6, 0.5))
    else:
        bhop = abs(math.sin(t * 14)) * 16
        lhop = abs(math.sin(t * 14 + 1.2)) * 16
        bp.update(mond="lach", armen=((65, 60), (115, -60)))
        lp.update(mond="lach", lid=2, armen=((180, 0), (115, -60)))

    # ---- tekenen: schaduwen, achterste rij, voorste rij
    for x, y, s, hp in ((bx, ACHTER_Y, ACHTER_S, bhop), (lx, ACHTER_Y, ACHTER_S, lhop),
                        (gx, VOOR_Y, VOOR_S, ghop), (kx, VOOR_Y, VOOR_S, khop)):
        if -200 < x < W + 200:
            grondschaduw(d, x, y, s, hp)
    plak(frame, bram, bx, ACHTER_Y, ACHTER_S, bp, hop=bhop)
    li = plak(frame, lotte, lx, ACHTER_Y, ACHTER_S, lp, hop=lhop)
    gi = plak(frame, gert, gx, VOOR_Y, VOOR_S, gp, gsx, gsy, grot, ghop) if gx > -300 else None
    ki = plak(frame, kees, kx, VOOR_Y, VOOR_S, kp, rot=krot, hop=khop) if kx > -240 else None
    d = ImageDraw.Draw(frame)

    # ---- effecten
    if gi and t < TOET:  # Zzz
        kxg, kyg, r = gi["kop"]
        hx, hy = gi["naar"](kxg - r * 0.4, kyg - r * 1.1)
        for n in range(8):
            t0 = n * 0.65
            u = (t - t0) / 1.9
            if 0 <= u <= 1:
                tekst(d, (hx - u * 110 + math.sin(u * 7) * 18, hy - u * 300), "Z", 40 + 50 * u,
                      kleur=(110, 140, 230), rand=6)
    if hoorn and ki:  # toeter in Kees' rechterhand
        hx, hy = ki["naar"](*ki["handen"][1])
        trill = rng.uniform(-4, 4) if TOET <= t < TOET + 0.85 else 0
        hx, hy = hx + trill, hy + trill
        d.rounded_rectangle((hx - 28, hy - 60, hx + 28, hy + 10), radius=10, fill=(220, 50, 50), outline=INK, width=5)
        d.polygon([(hx - 10, hy - 75), (hx + 10, hy - 75), (hx + 70, hy - 130), (hx + 95, hy - 105)],
                  fill=(245, 245, 245), outline=INK)
        d.line([(hx + 70, hy - 130), (hx + 95, hy - 105)], fill=INK, width=6)
        if TOET <= t < TOET + 0.85:  # geluidsgolven
            for n in range(3):
                u = ((t - TOET) * 3 + n / 3) % 1
                r = 40 + u * 220
                d.arc((hx + 80 - r, hy - 120 - r, hx + 80 + r, hy - 120 + r), -80, 10,
                      fill=(255, 210, 40), width=int(14 * (1 - u)) + 2)
    if TOET <= t < TOET + 1.0:  # TOEEET!!
        u = fase(t, TOET, TOET + 0.15)
        tekst(d, (W / 2 + rng.uniform(-8, 8), 470 + rng.uniform(-8, 8)), "TOEEET!!", 60 + 90 * u,
              kleur=(255, 220, 40), rand=12)
    if gi and LAND <= t < LAND + 0.7:  # stofwolkjes bij de landing
        u = fase(t, LAND, LAND + 0.7)
        for kant in (-1, 1):
            for n in range(3):
                cx = gx + kant * (90 + u * (120 + n * 60))
                r = 30 + u * 40 - n * 6
                c = int(235 - u * 40)
                d.ellipse((cx - r, VOOR_Y - r - n * 20, cx + r, VOOR_Y + r * 0.4 - n * 20), fill=(c, c, c - 10))
    if gi and BOOS + 0.2 <= t < REN + 0.5:  # stoom uit de oren
        kxg, kyg, r = gi["kop"]
        for kant in (-1, 1):
            ox, oy = gi["naar"](kxg + kant * r * 1.1, kyg)
            for n in range(4):
                u = ((t - BOOS) * 1.6 + n / 4) % 1
                rr = 14 + u * 34
                cx, cy = ox + kant * u * 70, oy - u * 150
                d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(250, 250, 250), outline=(200, 200, 200), width=3)
    if t >= REN:  # snelheidsstrepen achter de renners
        for x, hp, aan in ((kx, khop, ki), (gx, ghop, gi)):
            if aan and -150 < x < W + 100:
                for n in range(5):
                    y = VOOR_Y - 120 - n * 85 - hp
                    lg = 90 + (n * 37 + i * 13) % 80
                    d.line((x + 140, y, x + 140 + lg, y), fill=(255, 255, 255), width=8)
                    d.line((x + 140, y, x + 140 + lg, y), fill=INK, width=2)
    if t >= REN + 0.4:  # HAHAHA
        for x, y, f in ((bx, ACHTER_Y - 470, 0), (lx, ACHTER_Y - 470, 1.3)):
            for n in range(3):
                bounce = abs(math.sin(t * 9 + f + n)) * 22
                tekst(d, (x - 90 + n * 90, y - bounce), "HA", 52, kleur=(255, 120, 150) if f else (90, 200, 255), rand=7)
    if 0.3 <= t < 2.0:
        ondertitel(d, "Ome Gert doet een dutje...")
    elif 2.2 <= t < 4.8:
        ondertitel(d, "Kees heeft een plan")
    elif REN <= t < 9.4:
        ondertitel(d, "RENNEN!!!")
    elif t >= 10.2:
        ondertitel(d, "Deel 2: de wraak van Ome Gert")

    # schermschudden bij de toeter en de landing
    sch = 0
    if TOET <= t < TOET + 0.6:
        sch = 22 * (1 - fase(t, TOET, TOET + 0.6))
    elif LAND <= t < LAND + 0.35:
        sch = 26 * (1 - fase(t, LAND, LAND + 0.35))
    if sch:
        dx, dy = int(rng.uniform(-sch, sch)), int(rng.uniform(-sch, sch))
        f2 = Image.new("RGB", (W, H), (178, 128, 88))
        f2.paste(frame, (dx, dy))
        frame = f2
    return frame.tobytes()


# ---------------------------------------------------------------- geluid
SR = 44100


def geluid(duur):
    n = int(duur * SR)
    mixb = np.zeros(n)
    rng = np.random.default_rng(1)

    def zet(start, sig, vol=1.0):
        a = int(start * SR)
        b = min(n, a + len(sig))
        if b > a:
            mixb[a:b] += sig[: b - a] * vol

    def tt(d):
        return np.arange(int(d * SR)) / SR

    def env(d, aan=0.01, uit=0.1):
        t = tt(d)
        return np.minimum(1, t / aan) * np.minimum(1, (d - t) / uit).clip(0)

    def zaag(f, t):
        return 2 * ((f * t) % 1) - 1

    def sweep(f0, f1, d):
        t = tt(d)
        f = f0 * (f1 / f0) ** (t / d)
        return np.cumsum(f) / SR

    # snurken (0-5 s): ruis-inademing + brommende uitademing
    for c in np.arange(0.2, 5.0, 2.0):
        t = tt(1.0)
        ruis = np.convolve(rng.standard_normal(len(t)), np.ones(30) / 30, "same")
        zet(c, ruis * np.sin(np.pi * t / 1.0) ** 2 * 0.9, 0.5)
        t = tt(0.8)
        brom = zaag(85 + 10 * np.sin(t * 40), t) * np.sin(np.pi * t / 0.8) ** 2
        zet(c + 1.0, brom, 0.12)
    # sluip-tokkels (2.0-4.3 s)
    noten = [164.8, 196.0, 174.6, 207.7]
    for k, st in enumerate(np.arange(2.0, 4.3, math.pi / 9)):
        t = tt(0.3)
        f = noten[k % 4]
        sig = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(4 * np.pi * f * t)) * np.exp(-t * 16)
        zet(st, sig, 0.35)
    # toeter tevoorschijn (4.35 s): 'tsjing'
    t = tt(0.35)
    zet(4.35, np.sin(2 * np.pi * sweep(1800, 3200, 0.35)) * np.exp(-t * 9), 0.15)
    # TOEEET (5.0-5.85 s)
    t = tt(0.85)
    vib = 1 + 0.01 * np.sin(2 * np.pi * 6 * t)
    toet = sum(zaag(f * vib, t) for f in (466, 587, 698)) / 3
    zet(5.0, np.tanh(toet * 3) * env(0.85, 0.02, 0.08), 0.55)
    # boing (5.05 s) en fluit naar beneden (5.6-6.2 s)
    t = tt(0.6)
    ph = sweep(180, 520, 0.6) + 0.01 * np.sin(2 * np.pi * 18 * t)
    zet(5.05, np.sin(2 * np.pi * ph) * np.exp(-t * 3), 0.4)
    zet(5.62, np.sin(2 * np.pi * sweep(1500, 350, 0.58)) * env(0.58, 0.02, 0.05), 0.22)
    # plof bij de landing (6.2 s)
    t = tt(0.45)
    zet(6.2, (np.sin(2 * np.pi * sweep(90, 35, 0.45)) + 0.4 * rng.standard_normal(len(t)) * np.exp(-t * 30))
        * np.exp(-t * 7), 0.9)
    # stoom/fluitketel (6.6-7.8 s)
    t = tt(1.2)
    sis = np.diff(rng.standard_normal(len(t) + 1)) * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * t))
    zet(6.6, sis * env(1.2, 0.15, 0.2), 0.12)
    zet(6.6, np.sin(2 * np.pi * sweep(900, 1700, 1.2)) * env(1.2, 0.3, 0.2), 0.08)
    # zip + rennende voetjes (7.6-9.3 s)
    t = tt(0.25)
    zet(7.6, np.sin(2 * np.pi * sweep(300, 1600, 0.25)) * env(0.25, 0.01, 0.05), 0.3)
    for st in np.arange(7.62, 9.3, 0.075):
        t = tt(0.04)
        zet(st, rng.standard_normal(len(t)) * np.exp(-t * 120), 0.18)
    # lachen (7.9-12.5 s): 'ha'-stootjes, twee stemmen
    for f0, start, vol in ((330, 7.9, 0.22), (150, 8.05, 0.28)):
        st = start
        while st < duur - 0.3:
            for k in range(6):
                t = tt(0.14)
                f = f0 * (1 - 0.03 * k) * (1 + 0.04 * np.sin(2 * np.pi * 7 * t))
                stem = sum(np.sin(2 * np.pi * h * np.cumsum(f) / SR) * w
                           for h, w in ((1, 0.5), (2, 0.6), (3, 0.9), (4, 0.7), (5, 0.4), (6, 0.2)))
                h_ruis = rng.standard_normal(len(t)) * np.exp(-t * 60) * 0.5
                zet(st, (stem / 2 + h_ruis) * np.sin(np.pi * t / 0.14) ** 1.5, vol)
                st += 0.19
            st += 0.5
    mixb /= max(1e-9, np.abs(mixb).max()) / 0.89
    return mixb


def schrijf_wav(pad, sig):
    data = (sig * 32767).astype(np.int16)
    with wave.open(str(pad), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("uit", nargs="?", default="poppetjes/sketch-toeter.mp4")
    ap.add_argument("--tot", type=float, default=DUUR)
    ap.add_argument("--beeld", type=float, help="alleen één still op deze tijd (png)")
    a = ap.parse_args()
    uit = Path(a.uit)
    uit.parent.mkdir(parents=True, exist_ok=True)
    if a.beeld is not None:
        init()
        Image.frombytes("RGB", (W, H), beeld(int(a.beeld * FPS))).save(uit)
        print(uit)
        return
    duur = min(a.tot, DUUR)
    wav = uit.with_suffix(".wav")
    schrijf_wav(wav, geluid(duur))
    n = int(duur * FPS)
    ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                           "-r", str(FPS), "-i", "-", "-i", str(wav), "-c:v", "libx264", "-preset", "medium",
                           "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                           "-movflags", "+faststart", str(uit)], stdin=subprocess.PIPE)
    with Pool(initializer=init) as pool:
        for k, data in enumerate(pool.imap(beeld, range(n), chunksize=4)):
            ff.stdin.write(data)
            if k % 60 == 0:
                print(f"  {k / FPS:.0f} s", flush=True)
    ff.stdin.close()
    ff.wait()
    wav.unlink()
    print(uit)


if __name__ == "__main__":
    main()
