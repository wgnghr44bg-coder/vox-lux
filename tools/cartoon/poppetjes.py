"""Eigen cartoonpoppetjes (gratis, alleen Pillow).

Elk poppetje is opgebouwd uit losse onderdelen (hoofd, ogen, mond, lijf, armen, benen) met
een pose-dict, zodat dezelfde tekenfunctie later per beeldje kan animeren.

Gebruik: python3 tools/cartoon/poppetjes.py [uitvoer.png]
Maakt een ontwerpvel met alle poppetjes naast elkaar.
"""
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SS = 3  # supersampling: groot tekenen, daarna verkleinen voor gladde lijnen
INK = (25, 22, 30)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

# Ontwerpen: kleuren en vorm per poppetje.
POPPETJES = {
    "Boontje": dict(huid=(140, 200, 255), vorm="boon", haar="krul", lijf=None),
    "Tosti": dict(huid=(255, 170, 90), vorm="vierkant", haar="pet", pet=(220, 50, 60), lijf=(60, 70, 90)),
    "Blobbie": dict(huid=(130, 220, 120), vorm="blob", haar="sprietjes", lijf=None),
    "Mutsje": dict(huid=(255, 214, 190), vorm="rond", haar="muts", muts=(120, 80, 200), lijf=(250, 200, 60)),
}

POSE_STANDAARD = dict(kijk=(0.0, 0.0), oog_open=1.0, mond="lach", mond_open=0.0,
                      arm_l=(200, 30), arm_r=(-20, -30), been_l=100, been_r=80, kop_hoek=0.0, hop=0.0)


def lijn(d, pts, w):
    """Dikke lijn met ronde uiteinden en knikken."""
    d.line(pts, fill=INK, width=w, joint="curve")
    for x, y in (pts[0], pts[-1]):
        d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=INK)


def ledemaat(d, start, hoek1, hoek2, lengte, w):
    """Arm of been met één knik (hoeken in graden, 0 = rechts, 90 = omlaag)."""
    x0, y0 = start
    a1, a2 = math.radians(hoek1), math.radians(hoek1 + hoek2)
    x1, y1 = x0 + math.cos(a1) * lengte, y0 + math.sin(a1) * lengte
    x2, y2 = x1 + math.cos(a2) * lengte, y1 + math.sin(a2) * lengte
    lijn(d, [(x0, y0), (x1, y1), (x2, y2)], w)
    return x2, y2


def oog(d, cx, cy, r, kijk, open_, w):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill="white", outline=INK, width=w)
    if open_ > 0.15:
        pr = r * 0.42
        px, py = cx + kijk[0] * r * 0.45, cy + kijk[1] * r * 0.45
        d.ellipse((px - pr, py - pr, px + pr, py + pr), fill=INK)
        d.ellipse((px - pr * 0.15 + pr * 0.35, py - pr * 0.55, px + pr * 0.35 + pr * 0.25, py - pr * 0.15), fill="white")
    # ooglid van boven naar beneden
    if open_ < 1:
        h = 2 * r * (1 - open_)
        d.chord((cx - r, cy - r, cx + r, cy - r + 2 * h), 180, 360, fill=d._huid, outline=INK, width=w)
        if open_ <= 0.15:
            d.line((cx - r, cy, cx + r, cy), fill=INK, width=w)


def mond(d, cx, cy, s, soort, open_, w):
    if open_ > 0.1:
        h = s * 0.5 * open_
        d.ellipse((cx - s * 0.35, cy - h * 0.3, cx + s * 0.35, cy + h), fill=(120, 30, 40), outline=INK, width=w)
    elif soort == "lach":
        d.arc((cx - s * 0.45, cy - s * 0.35, cx + s * 0.45, cy + s * 0.3), 20, 160, fill=INK, width=w)
    elif soort == "boos":
        d.arc((cx - s * 0.35, cy, cx + s * 0.35, cy + s * 0.5), 200, 340, fill=INK, width=w)
    else:
        d.line((cx - s * 0.25, cy, cx + s * 0.25, cy), fill=INK, width=w)


def teken(img, naam, x, y, schaal=1.0, pose=None):
    """Teken poppetje `naam` met de voeten op (x, y) in `img` (al in SS-pixels)."""
    p = {**POSE_STANDAARD, **(pose or {})}
    o = POPPETJES[naam]
    d = ImageDraw.Draw(img)
    d._huid = o["huid"]
    s = 100 * schaal * SS
    w = max(2, int(7 * schaal * SS))
    y = y - p["hop"] * s

    # benen
    heup = (x, y - s * 1.6)
    ledemaat(d, (heup[0] - s * 0.2, heup[1]), p["been_l"], 0, s * 0.8, w)
    ledemaat(d, (heup[0] + s * 0.2, heup[1]), p["been_r"], 0, s * 0.8, w)

    # lijf
    rug = (x, y - s * 2.4)
    if o["vorm"] in ("boon", "blob"):
        # één vorm: hoofd en lijf samen
        top = y - s * 3.9
        bw = s * (0.95 if o["vorm"] == "boon" else 1.15)
        d.rounded_rectangle((x - bw, top, x + bw, y - s * 1.45), radius=bw * 0.95,
                            fill=o["huid"], outline=INK, width=w)
        kop = (x, top + s * 0.95)
    else:
        lw = s * 0.55
        kleur = o["lijf"] or o["huid"]
        d.rounded_rectangle((x - lw, rug[1] - s * 0.25, x + lw, y - s * 1.45), radius=lw * 0.6,
                            fill=kleur, outline=INK, width=w)
        kop = (x, y - s * 3.35)

    # armen
    schouder = s * (0.85 if o["vorm"] in ("boon", "blob") else 0.5)
    sy = (y - s * 2.35) if o["vorm"] not in ("boon", "blob") else (y - s * 2.25)
    ledemaat(d, (x - schouder, sy), p["arm_l"][0], p["arm_l"][1], s * 0.55, w)
    ledemaat(d, (x + schouder, sy), p["arm_r"][0], p["arm_r"][1], s * 0.55, w)

    kx, ky = kop
    # hoofd (alleen bij losse kop)
    if o["vorm"] == "rond":
        r = s * 0.95
        d.ellipse((kx - r, ky - r, kx + r, ky + r), fill=o["huid"], outline=INK, width=w)
    elif o["vorm"] == "vierkant":
        r = s * 0.9
        d.rounded_rectangle((kx - r, ky - r * 0.9, kx + r, ky + r * 0.9), radius=r * 0.35,
                            fill=o["huid"], outline=INK, width=w)

    # haar / accessoires
    if o["haar"] == "krul":
        for dx, kant in ((-0.18, -1), (0.0, 0), (0.18, 1)):
            bx, by = kx + dx * s, ky - s * 0.93
            lijn(d, [(bx, by), (bx + kant * s * 0.1, by - s * 0.22), (bx + kant * s * 0.2 + s * 0.05, by - s * 0.32)], w)
    elif o["haar"] == "pet":
        r = s * 0.9
        d.chord((kx - r * 1.02, ky - r * 1.6, kx + r * 1.02, ky - r * 0.2), 180, 360, fill=o["pet"], outline=INK, width=w)
        d.rounded_rectangle((kx - r * 0.2, ky - r * 0.98, kx + r * 1.55, ky - r * 0.72), radius=r * 0.12,
                            fill=o["pet"], outline=INK, width=w)
    elif o["haar"] == "sprietjes":
        for dx in (-0.45, 0.45):
            bx, by = kx + dx * s, ky - s * 0.95
            lijn(d, [(bx, by), (bx + dx * s * 0.5, by - s * 0.6)], w)
            ex, ey, rr = bx + dx * s * 0.5, by - s * 0.6, s * 0.14
            d.ellipse((ex - rr, ey - rr, ex + rr, ey + rr), fill=(255, 220, 60), outline=INK, width=w)
    elif o["haar"] == "muts":
        r = s * 0.95
        d.chord((kx - r * 1.03, ky - r * 1.25, kx + r * 1.03, ky + r * 0.25), 180, 360, fill=o["muts"], outline=INK, width=w)
        d.rounded_rectangle((kx - r * 1.05, ky - r * 0.55, kx + r * 1.05, ky - r * 0.3), radius=r * 0.1,
                            fill=o["muts"], outline=INK, width=w)
        pr = r * 0.22
        d.ellipse((kx - pr, ky - r * 1.25 - pr * 1.4, kx + pr, ky - r * 1.25 + pr * 0.6), fill="white", outline=INK, width=w)

    # gezicht
    er = s * (0.32 if o["vorm"] != "blob" else 0.36)
    ey = ky - s * 0.05
    gap = s * 0.36
    if o["vorm"] == "blob":
        oog(d, kx, ey, er * 1.25, p["kijk"], p["oog_open"], w)  # één groot oog
    else:
        oog(d, kx - gap, ey, er, p["kijk"], p["oog_open"], w)
        oog(d, kx + gap, ey, er, p["kijk"], p["oog_open"], w)
    mond(d, kx, ky + s * (0.4 if o["vorm"] == "vierkant" else 0.5), s, p["mond"], p["mond_open"], w)
    # blosjes
    if o["vorm"] in ("rond", "boon"):
        for dx in (-0.62, 0.62):
            bx, by, br = kx + dx * s, ky + s * 0.38, s * 0.12
            d.ellipse((bx - br, by - br * 0.6, bx + br, by + br * 0.6), fill=(255, 130, 140))


def ontwerpvel(uit):
    W, H = 1920, 1080
    img = Image.new("RGB", (W * SS, H * SS), (245, 240, 230))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT, 46 * SS)
    titel = ImageFont.truetype(FONT, 60 * SS)
    d.text((W * SS / 2, 70 * SS), "Kies je poppetje", font=titel, fill=INK, anchor="mm")
    for i, naam in enumerate(POPPETJES):
        cx = (W / 4) * (i + 0.5)
        teken(img, naam, cx * SS, 900 * SS, schaal=1.3)
        d.text((cx * SS, 990 * SS), f"{i + 1}. {naam}", font=font, fill=INK, anchor="mm")
    img.resize((W, H), Image.LANCZOS).save(uit)
    print(uit)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "poppetjes/ontwerpen.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    ontwerpvel(out)
