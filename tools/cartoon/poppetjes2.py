"""Eigen cartoonpoppetjes, ronde 2: krabbelstijl met grote koppen, wenkbrauwen en schaduw.

Lijnen wiebelen een beetje (alsof ze met de hand getekend zijn), vlakken krijgen een
donkerdere schaduwrand. Alles met Pillow, gratis.

Gebruik: python3 tools/cartoon/poppetjes2.py [uitvoer.png]
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont

SS = 3
INK = (28, 24, 32)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def donker(c, f=0.82):
    return tuple(int(v * f) for v in c)


class Pen:
    """Tekent wiebelige, handgetekende vormen op een afbeelding."""

    def __init__(self, img, s, seed):
        self.img, self.d, self.s = img, ImageDraw.Draw(img), s
        self.w = max(2, int(s * 0.075))
        self.rng = random.Random(seed)

    def wiebel(self, pts, kracht=0.012, dicht=False):
        """Punten fijner verdelen en een beetje laten wiebelen."""
        out = []
        n = len(pts) if dicht else len(pts) - 1
        fase = self.rng.uniform(0, 6.28)
        for i in range(n):
            (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
            stappen = max(1, int(math.hypot(x1 - x0, y1 - y0) / (self.s * 0.08)))
            for k in range(stappen):
                t = k / stappen
                j = len(out) * 0.35 + fase
                a = self.s * kracht
                out.append((x0 + (x1 - x0) * t + math.sin(j) * a, y0 + (y1 - y0) * t + math.cos(j * 1.3) * a))
        if not dicht:
            out.append(pts[-1])
        return out

    def ellips(self, cx, cy, rx, ry, n=48):
        return [(cx + math.cos(2 * math.pi * i / n) * rx, cy + math.sin(2 * math.pi * i / n) * ry) for i in range(n)]

    def vorm(self, pts, kleur, schaduw=True, rand=True, wiebel=True):
        """Gevuld vlak met schaduw aan de rechteronderkant en een inktrand."""
        p = self.wiebel(pts, dicht=True) if wiebel else pts
        if kleur is not None:
            self.d.polygon(p, fill=kleur)
            if schaduw:
                m = Image.new("L", self.img.size, 0)
                ImageDraw.Draw(m).polygon(p, fill=255)
                dx = int(self.s * 0.16)
                verschoven = ImageChops.offset(m, -dx, -dx)
                rand_m = ImageChops.subtract(m, verschoven)
                self.img.paste(donker(kleur), mask=rand_m)
        if rand:
            self.d.line(p + p[:2], fill=INK, width=self.w, joint="curve")

    def lijn(self, pts, w=None, kleur=INK):
        w = w or self.w
        p = self.wiebel(pts)
        self.d.line(p, fill=kleur, width=w, joint="curve")
        for x, y in (p[0], p[-1]):
            self.d.ellipse((x - w / 2, y - w / 2, x + w / 2, y + w / 2), fill=kleur)

    def boog(self, cx, cy, rx, ry, a0, a1, w=None, kleur=INK):
        n = max(6, int(abs(a1 - a0) / 8))
        pts = [(cx + math.cos(math.radians(a0 + (a1 - a0) * i / n)) * rx,
                cy + math.sin(math.radians(a0 + (a1 - a0) * i / n)) * ry) for i in range(n + 1)]
        self.lijn(pts, w, kleur)

    def stip(self, x, y, r, kleur=INK):
        self.d.ellipse((x - r, y - r, x + r, y + r), fill=kleur)


def arm(pen, x, y, hoek1, hoek2, lengte, hand=None):
    a1, a2 = math.radians(hoek1), math.radians(hoek1 + hoek2)
    x1, y1 = x + math.cos(a1) * lengte, y + math.sin(a1) * lengte
    x2, y2 = x1 + math.cos(a2) * lengte, y1 + math.sin(a2) * lengte
    pen.lijn([(x, y), (x1, y1), (x2, y2)])
    if hand:
        r = pen.s * 0.15
        pen.vorm(pen.ellips(x2, y2, r, r, 16), hand, schaduw=False)
    return x2, y2


def schoen(pen, x, y, kleur, richting=1):
    s = pen.s
    pts = [(x - s * 0.18 * richting, y - s * 0.16), (x + s * 0.2 * richting, y - s * 0.18),
           (x + s * 0.36 * richting, y - s * 0.02), (x + s * 0.3 * richting, y + s * 0.06),
           (x - s * 0.2 * richting, y + s * 0.06)]
    pen.vorm(pts, kleur, schaduw=False)


def oog(pen, cx, cy, rx, ry, kijk=(0.3, 0.1), lid=0.0, pupil=0.45, glans=True):
    pen.vorm(pen.ellips(cx, cy, rx, ry, 32), (255, 255, 255), schaduw=False)
    pr = min(rx, ry) * pupil
    px, py = cx + kijk[0] * (rx - pr), cy + kijk[1] * (ry - pr)
    pen.stip(px, py, pr)
    if glans:
        pen.stip(px - pr * 0.35, py - pr * 0.4, pr * 0.3, (255, 255, 255))
    if lid > 0:  # hangend ooglid (slaperig / verveeld)
        h = ry * 2 * lid
        pts = [(cx - rx * 1.05, cy - ry * 1.05), (cx + rx * 1.05, cy - ry * 1.05),
               (cx + rx * 1.05, cy - ry + h), (cx - rx * 1.05, cy - ry + h)]
        m = Image.new("L", pen.img.size, 0)
        ImageDraw.Draw(m).polygon(pen.ellips(cx, cy, rx, ry, 32), fill=255)
        lm = Image.new("L", pen.img.size, 0)
        ImageDraw.Draw(lm).polygon(pts, fill=255)
        pen.img.paste(pen.huid, mask=ImageChops.multiply(m, lm))
        pen.lijn([(cx - rx, cy - ry + h), (cx + rx, cy - ry + h)])
        pen.vorm(pen.ellips(cx, cy, rx, ry, 32), None, schaduw=False)


def lijf_basis(pen, x, y, shirt, broek, schoenen, dik=1.0, armen=((150, -40), (30, 40)), hand=None):
    s = pen.s
    pen.d.ellipse((x - s * 0.9, y - s * 0.12, x + s * 0.9, y + s * 0.12), fill=(222, 214, 200))
    heup = y - s * 1.35
    for kant in (-1, 1):
        bx = x + kant * s * 0.25
        pen.lijn([(bx, heup), (bx + kant * s * 0.08, y - s * 0.65), (bx + kant * s * 0.05, y - s * 0.08)],
                 w=int(pen.w * 1.15), kleur=broek or INK)
        schoen(pen, bx + kant * s * 0.05, y, schoenen, kant)
    bw = s * 0.62 * dik
    top = y - s * 2.75
    pts = [(x - bw * 0.75, top), (x + bw * 0.75, top), (x + bw, top + s * 0.5), (x + bw * 1.02, heup - s * 0.15),
           (x + bw * 0.85, heup + s * 0.12), (x - bw * 0.85, heup + s * 0.12), (x - bw * 1.02, heup - s * 0.15),
           (x - bw, top + s * 0.5)]
    pen.vorm(pts, shirt)
    sy = top + s * 0.28
    arm(pen, x - bw * 0.85, sy, armen[0][0], armen[0][1], s * 0.6, hand)
    arm(pen, x + bw * 0.85, sy, armen[1][0], armen[1][1], s * 0.6, hand)
    return top


def kees(img, x, y, s):
    """Krabbelkop met warrig haar, scheve grijns, groene hoodie."""
    pen = Pen(img, s, 1)
    pen.huid = (252, 226, 200)
    top = lijf_basis(pen, x, y, (95, 175, 125), None, (245, 245, 245),
                     armen=((115, 40), (20, -110)), hand=pen.huid)
    pen.lijn([(x - s * 0.15, top + s * 0.1), (x - s * 0.18, top + s * 0.55)], w=int(pen.w * 0.6))  # koordjes
    pen.lijn([(x + s * 0.15, top + s * 0.1), (x + s * 0.18, top + s * 0.5)], w=int(pen.w * 0.6))
    pen.lijn([(x - s * 0.35, top + s * 0.95), (x + s * 0.35, top + s * 0.95)], w=int(pen.w * 0.6))  # buidelzak
    kx, ky, r = x, top - s * 0.95, s * 1.12
    pen.vorm(pen.ellips(kx, ky, r, r * 0.95), pen.huid)
    # warrig haar: krullen bovenop
    rng = random.Random(5)
    for i in range(22):
        a = math.radians(rng.uniform(200, 340))
        hx, hy = kx + math.cos(a) * r * 0.8, ky + math.sin(a) * r * 0.82
        rr = s * rng.uniform(0.12, 0.2)
        pen.boog(hx, hy, rr, rr, rng.uniform(0, 90), rng.uniform(250, 380), w=int(pen.w * 0.8))
    oog(pen, kx - s * 0.38, ky + s * 0.05, s * 0.3, s * 0.36, kijk=(0.6, 0.2))
    oog(pen, kx + s * 0.38, ky - s * 0.02, s * 0.36, s * 0.42, kijk=(0.6, 0.2))
    pen.lijn([(kx - s * 0.65, ky - s * 0.42), (kx - s * 0.15, ky - s * 0.32)])  # wenkbrauwen
    pen.lijn([(kx + s * 0.08, ky - s * 0.55), (kx + s * 0.68, ky - s * 0.7)])
    pen.boog(kx + s * 0.1, ky + s * 0.45, s * 0.42, s * 0.22, 10, 150)  # scheve grijns
    pen.lijn([(kx + s * 0.5, ky + s * 0.45), (kx + s * 0.6, ky + s * 0.38)], w=int(pen.w * 0.8))


def bram(img, x, y, s):
    """Stoere gast met stekelhaar, zonnebril, rode hoodie en gouden ketting."""
    pen = Pen(img, s, 2)
    pen.huid = (226, 168, 122)
    top = lijf_basis(pen, x, y, (214, 64, 60), (40, 50, 80), (250, 250, 250),
                     armen=((160, -70), (20, 70)), hand=pen.huid)
    for i in range(9):  # ketting
        a = math.radians(30 + i * 15)
        pen.stip(x + math.cos(a) * s * 0.35, top + s * 0.05 + math.sin(a) * s * 0.35, s * 0.055, (240, 190, 50))
    kx, ky, r = x, top - s * 0.95, s * 1.08
    pen.vorm(pen.ellips(kx, ky, r * 0.98, r), pen.huid)
    # stekelhaar
    pts = []
    for i in range(11):
        a = math.radians(190 + i * 16)
        rr = r * (1.0 if i % 2 == 0 else 1.45)
        pts.append((kx + math.cos(a) * rr, ky - s * 0.12 + math.sin(a) * rr))
    pts += [(kx + r * 0.95, ky - s * 0.25), (kx - r * 0.95, ky - s * 0.25)]
    pen.vorm(pts, (70, 45, 35))
    # zonnebril
    for dx in (-0.4, 0.4):
        bx, by = kx + dx * s, ky + s * 0.05
        pts = [(bx - s * 0.33, by - s * 0.2), (bx + s * 0.33, by - s * 0.2), (bx + s * 0.28, by + s * 0.18),
               (bx - s * 0.28, by + s * 0.18)]
        pen.vorm(pts, (20, 20, 28), schaduw=False)
        pen.lijn([(bx - s * 0.18, by - s * 0.08), (bx - s * 0.05, by - s * 0.12)], w=int(pen.w * 0.6), kleur=(255, 255, 255))
    pen.lijn([(kx - s * 0.08, ky - s * 0.08), (kx + s * 0.08, ky - s * 0.08)])
    # grote grijns met tanden
    mx, my = kx + s * 0.05, ky + s * 0.5
    pts = [(mx - s * 0.42, my - s * 0.05), (mx + s * 0.42, my - s * 0.1), (mx + s * 0.3, my + s * 0.22),
           (mx, my + s * 0.3), (mx - s * 0.3, my + s * 0.2)]
    pen.vorm(pts, (255, 255, 255), schaduw=False)
    pen.lijn([(mx - s * 0.38, my + s * 0.05), (mx + s * 0.38, my + s * 0.02)], w=int(pen.w * 0.6))


def lotte(img, x, y, s):
    """Meisje met paardenstaart, grote ogen met wimpers, roze trui."""
    pen = Pen(img, s, 3)
    pen.huid = (255, 222, 204)
    top = lijf_basis(pen, x, y, (240, 130, 170), None, (140, 90, 200),
                     armen=((140, -20), (60, -150)), hand=pen.huid)
    kx, ky, r = x, top - s * 0.95, s * 1.08
    haar = (205, 105, 55)
    # paardenstaart achter het hoofd
    pen.vorm([(kx + r * 0.6, ky - r * 0.6), (kx + r * 1.5, ky - r * 0.3), (kx + r * 1.6, ky + r * 0.5),
              (kx + r * 1.25, ky + r * 0.9), (kx + r * 1.15, ky + r * 0.2), (kx + r * 0.8, ky - r * 0.1)], haar)
    pen.vorm(pen.ellips(kx, ky, r, r * 0.97), pen.huid)
    pen.vorm([(kx - r * 1.02, ky - r * 0.05), (kx - r * 0.9, ky - r * 0.75), (kx - r * 0.3, ky - r * 1.05),
              (kx + r * 0.5, ky - r * 1.0), (kx + r * 1.02, ky - r * 0.35), (kx + r * 0.55, ky - r * 0.5),
              (kx - r * 0.1, ky - r * 0.45), (kx - r * 0.75, ky - r * 0.3)], haar)
    pen.stip(kx + r * 1.0, ky - r * 0.5, s * 0.12, (255, 210, 60))  # haarelastiek
    for dx, k in ((-0.38, -1), (0.38, 1)):
        ox, oy = kx + dx * s, ky + s * 0.12
        oog(pen, ox, oy, s * 0.3, s * 0.38, kijk=(-0.2, -0.2), pupil=0.6)
        for i in range(3):  # wimpers
            a = math.radians(-90 + k * (25 + i * 22))
            pen.lijn([(ox + math.cos(a) * s * 0.3, oy + math.sin(a) * s * 0.36),
                      (ox + math.cos(a) * s * 0.44, oy + math.sin(a) * s * 0.5)], w=int(pen.w * 0.6))
    pen.boog(kx, ky + s * 0.62, s * 0.18, s * 0.1, 10, 170)
    for dx in (-0.68, 0.68):
        pen.d.ellipse((kx + dx * s - s * 0.13, ky + s * 0.48, kx + dx * s + s * 0.13, ky + s * 0.62), fill=(255, 150, 160))


def gert(img, x, y, s):
    """Oom Gert: kaal, grote neus, snor, slaperige ogen, hemd en slippers."""
    pen = Pen(img, s, 4)
    pen.huid = (240, 190, 158)
    top = lijf_basis(pen, x, y, (250, 250, 245), (90, 110, 160), (90, 80, 70), dik=1.35,
                     armen=((100, 10), (80, -10)), hand=pen.huid)
    pen.boog(x, top + s * 0.2, s * 0.35, s * 0.3, 20, 160, w=int(pen.w * 0.7))  # hemdhals
    kx, ky, r = x, top - s * 0.9, s * 1.02
    pen.vorm(pen.ellips(kx, ky, r, r * 1.05), pen.huid)
    grijs = (200, 200, 205)
    for kant in (-1, 1):
        pen.vorm([(kx + kant * r * 0.97, ky - r * 0.15), (kx + kant * r * 1.15, ky + r * 0.05),
                  (kx + kant * r * 0.98, ky + r * 0.4)], grijs, schaduw=False)
    pen.boog(kx - s * 0.2, ky - r * 0.75, s * 0.25, s * 0.08, 200, 330, w=int(pen.w * 0.6))  # glans op de kale kop
    oog(pen, kx - s * 0.35, ky - s * 0.08, s * 0.28, s * 0.3, kijk=(0, 0.4), lid=0.5)
    oog(pen, kx + s * 0.35, ky - s * 0.08, s * 0.28, s * 0.3, kijk=(0, 0.4), lid=0.5)
    pen.vorm(pen.ellips(kx, ky + s * 0.3, s * 0.26, s * 0.22), (235, 150, 130))  # neus
    pen.vorm([(kx - s * 0.5, ky + s * 0.62), (kx - s * 0.1, ky + s * 0.48), (kx, ky + s * 0.55),
              (kx + s * 0.1, ky + s * 0.48), (kx + s * 0.5, ky + s * 0.62), (kx + s * 0.35, ky + s * 0.72),
              (kx, ky + s * 0.66), (kx - s * 0.35, ky + s * 0.72)], (120, 110, 105))  # snor
    pen.lijn([(kx - s * 0.12, ky + s * 0.85), (kx + s * 0.12, ky + s * 0.85)])


POPPETJES = [("Kees", kees), ("Bram", bram), ("Lotte", lotte), ("Ome Gert", gert)]


def ontwerpvel(uit):
    W, H = 1920, 1080
    img = Image.new("RGB", (W * SS, H * SS), (246, 240, 228))
    d = ImageDraw.Draw(img)
    d.text((W * SS / 2, 64 * SS), "Kies je poppetje (ronde 2)", font=ImageFont.truetype(FONT, 56 * SS),
           fill=INK, anchor="mm")
    font = ImageFont.truetype(FONT, 44 * SS)
    for i, (naam, fn) in enumerate(POPPETJES):
        cx = (W / 4) * (i + 0.5)
        fn(img, cx * SS, 920 * SS, 118 * SS)
        d.text((cx * SS, 1005 * SS), f"{i + 1}. {naam}", font=font, fill=INK, anchor="mm")
    img.resize((W, H), Image.LANCZOS).save(uit)
    print(uit)


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "poppetjes/ontwerpen-2.png")
    out.parent.mkdir(parents=True, exist_ok=True)
    ontwerpvel(out)
