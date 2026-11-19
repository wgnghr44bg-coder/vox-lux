"""BlackSwanVault video 1, versie 3 (eigenaar 19 nov 12:55: "kijk hoe ColdFusion het opbouwt"): per zin een beeld dat letterlijk
past: persoon -> echte foto met naam, bedrijf -> gebouw/logo, document -> eigen documentkaart met de echte zin gemarkeerd,
getal -> grafiek. Elke 3-6 s een nieuw beeld. Geen geluidseffecten, geen hoofdstukken.
Gebruik: python render3.py --van 0 --tot 62"""
import sys
import render as R
from render import *   # noqa: F401,F403

Z = R.Z
def zs(i): return Z[i][0]
def ze(i): return Z[i + 1][0] - 0.1 if i + 1 < len(Z) else R.EIND

# ---------- bouwstenen ----------
def ft(naam, zoom=(1.0, 1.08), pan=(0.5, 0.5, 0.5, 0.5), donker=0.7, grijs=False):
    return lambda t, d: foto(naam, t, d, zoom, pan, grijs=grijs, donker=donker)

def doc(bron, titel, regels, mark=0, achter="hq-wall"):
    """Eigen documentkaart (geen kopie van een webpagina): bron, titel, regels; regel 'mark' wordt gemarkeerd."""
    def f(t, d):
        img = foto(achter, t, d, (1.0, 1.04), donker=0.25); img = img.filter(ImageFilter.GaussianBlur(6))
        dr = ImageDraw.Draw(img, "RGBA"); z = 1.0 + 0.03 * eio(t / d)
        x0, y0, x1, y1 = W // 2 - 560 * z, 200 - 10 * z, W // 2 + 560 * z, 880 + 10 * z
        a = ease(t / 0.4)
        dr.rectangle([x0, y0 + 30 * (1 - a), x1, y1 + 30 * (1 - a)], fill=(246, 246, 242, int(255 * a)))
        dr.rectangle([x0, y0 + 30 * (1 - a), x1, y0 + 8 + 30 * (1 - a)], fill=(118, 185, 0, int(255 * a)) if "NVIDIA" in bron.upper() else ROOD + (int(255 * a),))
        txt(dr, (x0 + 60, y0 + 50), bron.upper(), font(BOLD, 26), (110, 110, 110), a)
        yy = y0 + 110
        import textwrap
        for r in textwrap.wrap(titel, 38):
            txt(dr, (x0 + 60, yy), r, font(BOLD, 50), (20, 20, 20), a); yy += 64
        yy += 40
        for k, r in enumerate(regels):
            if k == mark:
                p = ease((t - 0.8) / 0.7); w = dr.textlength(r, font=font(REG, 38))
                dr.rectangle([x0 + 50, yy - 6, x0 + 70 + w * p, yy + 50], fill=(255, 226, 60, int(220 * a)))
            txt(dr, (x0 + 60, yy), r, font(BOLD if k == mark else REG, 38), (30, 30, 30), a); yy += 76
        return img
    return f

def naam(onder_f, titel, sub):
    def f(t, d):
        img = onder_f(t, d); lower_third(img, t - 0.2, titel, sub); return img
    return f
def stempel_op(onder_f, s, kleur=ROOD):
    def f(t, d):
        img = onder_f(t, d); stempel(img, t - 0.2, s, kleur); return img
    return f
def tekst_op(onder_f, s):
    def f(t, d):
        img = onder_f(t, d); onder(img, t, s, 0.2); return img
    return f

def koers_kort(t, d):
    img, _ = lijn(t, d, "2026-10-20", "2026-11-18", "NVIDIA STOCK", "Daily closing price, October 20 to November 18, 2026",
                  markers=[("2026-10-29", "First report"), ("2026-11-08", "Letter"), ("2026-11-12", "Resigns"), ("2026-11-17", "Earnings")], teken=0.75)
    a = ease((t - d * 0.75) / 0.4); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (1700, 330), "-29%", font(BLACK, 150), ROOD, a, "rm"); txt(dr, (1700, 420), "Oct 29 to Nov 18", font(REG, 30), GRIJS, a, "rm")
    return img
def biljoen(t, d):
    img, _ = lijn(d, d, "2026-10-20", "2026-11-18", "NVIDIA STOCK", "Daily closing price, October 20 to November 18, 2026", teken=0.01)
    img = Image.blend(img, leeg(), 0.55); dr = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.35); s = 1.2 - 0.2 * a
    txt(dr, (W // 2, HH // 2 - 30), "-$1 TRILLION+", font(BLACK, int(180 * s)), ROOD, a, "mm")
    txt(dr, (W // 2, HH // 2 + 90), "in market value", font(REG, 44), GRIJS, ease((t - 0.3) / 0.4), "mm")
    return img
def kwartaal(t, d):
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (W // 2, 130), "NVIDIA REVENUE, ONE QUARTER", font(BOLD, 46), WIT, 1, "ma")
    for i, (lab, v, k) in enumerate([("Q3 2025", 57.0, (90, 90, 95)), ("Q3 2026", 115.8, GROEN)]):
        p = ease((t - 0.2 - i * 0.7) / 0.8); x = 620 + i * 460; h = v * 5.0 * p
        if p > 0:
            dr.rectangle([x, 900 - h, x + 220, 900], fill=k + (255,))
            txt(dr, (x + 110, 900 - h - 18), f"${v * p:.1f}B", font(BOLD, 52), WIT, min(1, p * 2), "ms")
        txt(dr, (x + 110, 935), lab, font(REG, 34), GRIJS, 1, "ma")
    if t > 1.8: txt(dr, (1500, 420), "+103%", font(BLACK, 110), GROEN, ease((t - 1.8) / 0.35), "mm")
    bron(img, "Source: Nvidia press release, November 17, 2026"); return img
def drie_regels(achter):
    def f(t, d):
        img = foto(achter, t, d, (1.0, 1.06), donker=0.3, grijs=True); dr = ImageDraw.Draw(img, "RGBA")
        for i, (r, start) in enumerate([("It lost its founder.", 0.2), ("It lost its crown.", zt8(1)), ("And over a trillion dollars.", zt8(2)), ("While making more money than ever.", zt8(3))]):
            txt(dr, (W // 2, 330 + i * 120), r, font(BLACK, 76), GROEN if i == 3 else (ROOD if i == 2 else WIT), ease((t - start) / 0.35), "mm")
        return img
    return f
def zt8(k):                                     # tijd binnen zin 8 waarop de woorden ongeveer vallen
    d = Z[8][1] - Z[8][0]; return [0.2, d * 0.32, d * 0.5, d * 0.68][k]
def tijdlijn_nov(t, d):
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    pts = [("OCT 29", "First report"), ("NOV 5", "Congress"), ("NOV 8", "The letter"), ("NOV 12", "Resigns"), ("NOV 17", "Earnings")]
    y = 520; x0, x1 = 220, 1700; p = ease(t / 1.2)
    dr.line([(x0, y), (x0 + (x1 - x0) * p, y)], fill=(255, 255, 255, 120), width=4)
    for i, (a_, b_) in enumerate(pts):
        x = x0 + i * (x1 - x0) / 4; a = ease((t - 0.2 - i * 0.25) / 0.3)
        dr.ellipse([x - 14, y - 14, x + 14, y + 14], fill=ROOD + (int(255 * a),))
        txt(dr, (x, y - 50), a_, font(BOLD, 40), WIT, a, "ms"); txt(dr, (x, y + 50), b_, font(REG, 30), GRIJS, a, "ma")
    txt(dr, (W // 2, 230), "What really happened?", font(BLACK, 80), WIT, ease((t - 0.5) / 0.4), "mm"); return img
def titel(t, d):
    img = foto("gtc-a", t, d, (1.0, 1.05), donker=0.3); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (W // 2, 500), "THE MAN WHO", font(BOLD, 60), GRIJS, ease(t / 0.6), "mm")
    txt(dr, (W // 2, 600), "BUILT NVIDIA", font(BLACK, 150), WIT, ease((t - 0.3) / 0.6), "mm"); logo_klein(img, ease((t - 0.6) / 0.5)); return img

def taiwan_vs(t, d):
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.4)
    for x, n in ((1500, "TAIWAN"), (420, "UNITED STATES")):
        dr.ellipse([x - 120, 420, x + 120, 660], outline=(255, 255, 255, int(200 * a)), width=5); txt(dr, (x, 700), n, font(BOLD, 44), WIT, a, "ma")
    p = ease((t - 0.4) / 1.4); x = 1380 - 840 * p
    dr.line([(1380, 540), (x, 540)], fill=ROOD + (255,), width=8)
    if p > 0.05: dr.polygon([(x, 515), (x, 565), (x - 40, 540)], fill=ROOD + (255,))
    txt(dr, (W // 2, 300), "Sent to America as a young boy", font(BOLD, 60), WIT, ease((t - 0.3) / 0.4), "mm"); return img

# ---------- plan: per zin een of meer beelden (fractie van de zin waarop het beeld begint) ----------
def ZR(i, f=0.0): return Z[i][0] + f * (Z[i][1] - Z[i][0])     # absolute tijd binnen zin i

def doc_laat(start_abs, *args, **kw):            # documentkaart die pas op een bepaalde zin verschijnt
    f = doc(*args, **kw); ach = kw.get("achter", args[3] if len(args) > 3 else "hq-wall")
    def g(t, d, T0):
        if T0 + t < start_abs:
            return foto(ach, t, d, (1.0, 1.04), donker=0.3).filter(ImageFilter.GaussianBlur(6))
        return f(T0 + t - start_abs, d)
    return g

def opening_huang(t, d, T0):
    img = foto("gtc-a", t, d, (1.0, 1.1)); ab = T0 + t
    if ab < ZR(2): lower_third(img, ab - ZR(1) - 0.2, "JENSEN HUANG", "Co-founder and CEO of Nvidia, 1993 to 2026")
    elif ab < ZR(2, 0.5): onder(img, ab - ZR(2), "The leather jacket. The giant keynotes.", 0)
    else: onder(img, ab - ZR(2, 0.5), "The man who sold the shovels in the AI gold rush", 0)
    return img
def koers_en_biljoen(t, d, T0):
    ab = T0 + t
    img, _ = lijn(min(ab - ZR(3), ZR(4) - ZR(3)), ZR(4) - ZR(3) + 0.01, "2026-10-20", "2026-11-18", "NVIDIA STOCK",
                  "Daily closing price, October 20 to November 18, 2026",
                  markers=[("2026-10-29", "First report"), ("2026-11-08", "Letter"), ("2026-11-12", "Resigns"), ("2026-11-17", "Earnings")], teken=0.8)
    dr = ImageDraw.Draw(img, "RGBA"); a = ease((ab - ZR(3, 0.85)) / 0.4)
    txt(dr, (1700, 330), "-29%", font(BLACK, 150), ROOD, a, "rm"); txt(dr, (1700, 420), "Oct 29 to Nov 18", font(REG, 30), GRIJS, a, "rm")
    if ab >= ZR(4):
        b = ease((ab - ZR(4)) / 0.5); img = Image.blend(img, leeg(), 0.5 * b); dr = ImageDraw.Draw(img, "RGBA")
        txt(dr, (W // 2, HH // 2 - 30), "-$1 TRILLION+", font(BLACK, 170), ROOD, b, "mm")
        txt(dr, (W // 2, HH // 2 + 90), "in market value", font(REG, 44), GRIJS, b, "mm")
    return img
def dennys(t, d, T0):
    img = foto("dennys-b", t, d, (1.0, 1.1)); stempel(img, t - 0.3, "SAN JOSE, 1993", DONKER); onder(img, t, "A booth at Denny's", 1.2); return img
def taiwan_vs_2(t, d, T0):
    img = taiwan_vs(t, d)
    if T0 + t > ZR(13, 0.5): txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 860), "As a teenager: washing dishes at Denny's", font(BOLD, 50), GROEN, ease((T0 + t - ZR(13, 0.5)) / 0.4), "mm")
    return img
def gewoon(fn): return lambda t, d, T0: fn(t, d)

# 19 nov 13:05 (eigenaar: "niet te snel afwisselen, vooral in de eerste minuut"): een beeld per 1-2 zinnen, tekst wisselt op hetzelfde beeld
SHOTS = [   # zoals proef v4, alleen zin 1-2 (sec 10-12) op een beeld (eigenaar: "Sec 10-11-12 gaan beelden heel snel dat is het enige")
 (0.0, gewoon(stempel_op(ft("gtc-a", (1.05, 1.15), grijs=True), "NOVEMBER 12, 2026"))),
 (ZR(0, 0.5), gewoon(doc("Nvidia press release, November 12, 2026", "NVIDIA Announces CEO Transition",
                ["Jensen Huang resigns", "Colette Kress appointed Interim CEO", "Harvey C. Jones appointed first-ever Chair of the Board"], 0))),
 (ZR(1) - 0.15, opening_huang),
 (ZR(3) - 0.15, gewoon(koers_kort)),
 (ZR(4) - 0.15, gewoon(biljoen)),
 (ZR(5) - 0.15, gewoon(ft("hq-wall", (1.0, 1.1), donker=0.6))),
 (ZR(6) - 0.15, gewoon(doc("Nvidia press release, November 17, 2026", "NVIDIA Announces Financial Results for Third Quarter Fiscal 2027",
                ["Revenue of $115.8 billion, up 103% from a year ago", "Data Center revenue of $107.6 billion, up 110% from a year ago"], 0, "hq-entry"))),
 (ZR(7) - 0.15, gewoon(kwartaal)),
 (ZR(8) - 0.15, gewoon(drie_regels("huang-h"))),
 (ZR(9) - 0.15, gewoon(tijdlijn_nov)),
 (ZR(10) - 0.15, gewoon(stempel_op(ft("dennys-a", (1.0, 1.1)), "SAN JOSE, 1993", DONKER))),
 (ZR(10, 0.45), gewoon(tekst_op(ft("dennys-b", (1.1, 1.0)), "A booth at Denny's"))),
 (ZR(11) - 0.15, gewoon(ft("gtc-a", (1.0, 1.08)))),   # 19 nov: geen intro-titelscherm (eigenaar)
 (ZR(12) - 0.15, gewoon(tekst_op(ft("taipei-1963", (1.0, 1.08), donker=0.75), "Taiwan, 1963"))),
 (ZR(13) - 0.15, gewoon(taiwan_vs)),
 (ZR(13, 0.5), gewoon(tekst_op(ft("dennys-a", (1.08, 1.0)), "Washing dishes at Denny's"))),
]


# ---------- rest van de video (eigenaar 19 nov: "Ja zo is het goed") ----------
import render2 as R2
SC = {n: (a, b) for n, a, b, _ in R.SCENES}
def scene(naam):                                  # bestaande scene (grafiek/tekst) met scene-tijd
    def f(t, d, T0):
        a, b = SC[naam]; R.HUIDIG[0] = naam; return R2.S(naam, T0 + t - a, b - a)
    return f
def fot(naam, cap=None, stamp=None, kleur=DONKER, zoom=(1.0, 1.08), pan=(0.5, 0.5, 0.5, 0.5), donker=0.7, grijs=False, naamkaart=None):
    def f(t, d, T0):
        img = foto(naam, t, d, zoom, pan, grijs=grijs, donker=donker)
        if stamp: stempel(img, t - 0.2, stamp, kleur)
        if naamkaart: lower_third(img, t - 0.2, *naamkaart)
        elif cap: onder(img, t, cap, 0.3)
        return img
    return f
def fot_groot(naam, s_, sub=None, kleur=WIT, donker=0.45, size=150):
    def f(t, d, T0):
        img = foto(naam, t, d, (1.0, 1.08), donker=donker); return R2.groot(img, t, s_, kleur, size=size, sub=sub, start=0.2)
    return f
def citaat_op(naam, regels, wie):
    def f(t, d, T0): return citaat(t, d, regels, wie, foto(naam, t, d, (1.0, 1.05), donker=0.22).filter(ImageFilter.GaussianBlur(4)))
    return f
def naamkaart_dark(titel, sub, achter="hq-hq"):
    def f(t, d, T0):
        img = foto(achter, t, d, (1.0, 1.06), donker=0.32); dr = ImageDraw.Draw(img, "RGBA")
        txt(dr, (W // 2, 470), titel, font(BLACK, 100), WIT, ease(t / 0.4), "mm"); txt(dr, (W // 2, 565), sub, font(REG, 40), GRIJS, ease((t - 0.3) / 0.4), "mm")
        return img
    return f
def alexnet_namen(t, d, T0):
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    for i, (n, r) in enumerate([("ALEX KRIZHEVSKY", ""), ("ILYA SUTSKEVER", ""), ("GEOFFREY HINTON", "")]):
        a = ease((t - 0.2 - i * 0.6) / 0.4); txt(dr, (W // 2, 360 + i * 130), n, font(BLACK, 80), WIT, a, "mm")
    txt(dr, (W // 2, 780), "University of Toronto, 2012", font(REG, 40), GRIJS, ease((t - 1.6) / 0.4), "mm"); return img
def zelf(fn): return lambda t, d, T0: fn(t, d)

def duo(t, d, T0):                               # Hinton (echte foto) en Sutskever (naamkaart), zin 42-43
    img = leeg(); eerst = T0 + t < ZR(43)
    f = foto("hinton", t, d, (1.0, 1.06), (0.5, 0.45, 0.5, 0.45), donker=0.8 if eerst else 0.35)
    img.paste(f.crop((W // 4, 0, W // 4 + W // 2, HH)), (0, 0))
    dr = ImageDraw.Draw(img, "RGBA")
    if eerst: lower_third(img, t - 0.2, "GEOFFREY HINTON", "Nobel Prize in Physics, 2024")
    else:
        a = ease((T0 + t - ZR(43)) / 0.4)
        txt(dr, (W * 3 // 4, 470), "ILYA SUTSKEVER", font(BLACK, 76), WIT, a, "mm"); txt(dr, (W * 3 // 4, 550), "Co-founder of OpenAI", font(REG, 40), GROEN, a, "mm")
    return img
def kress(t, d, T0):
    img = foto("hq-hq", t, d, (1.0, 1.1), donker=0.32); dr = ImageDraw.Draw(img, "RGBA"); ab = T0 + t
    txt(dr, (W // 2, 430), "COLETTE KRESS", font(BLACK, 100), WIT, ease(t / 0.4), "mm")
    sub = "Interim CEO" if ab < ZR(108) else "Nvidia's CFO since 2013, now leading a company worth trillions"
    txt(dr, (W // 2, 525), sub, font(REG, 40), GRIJS, ease((t - 0.3) / 0.4), "mm")
    if ZR(107) <= ab < ZR(108): onder(img, ab - ZR(107), "And Huang agrees to testify before Congress", 0)
    return img

def slot(t, d, T0):
    img = foto("dennys-b", t, d, (1.1, 1.0), grijs=True, donker=0.55); onder(img, t, "It started in a booth at Denny's", 0.3)
    if t > d - 1.8: img = Image.blend(img, Image.new("RGB", (W, HH)), min(1, (t - (d - 1.8)) / 1.8))
    return img
def eind(t, d, T0):                               # laatste beeld, rustig uitfaden
    img = foto("hq-entry", t, d, (1.0, 1.1), donker=0.6)
    if t > d - 1.5: img = Image.blend(img, Image.new("RGB", (W, HH)), min(1, (t - (d - 1.5)) / 1.5))
    return img

SHOTS += [
 (ZR(14) - 0.15, fot("osu", "Electrical engineering: Oregon State University, then Stanford")),
 (ZR(15) - 0.15, fot("lsi-chip", "Chip designer at AMD and LSI Logic", donker=0.6)),
 (ZR(16) - 0.15, fot("huang-f", "He wanted to build something of his own")),
 (ZR(17) - 0.15, fot("dennys-b", stamp="APRIL 1993", zoom=(1.08, 1.0))),
 (ZR(17, 0.5), fot("malach", naamkaart=("CHRIS MALACHOWSKY", "Co-founder of Nvidia, with Curtis Priem"), donker=0.75)),
 (ZR(18) - 0.15, fot("nv1", "One idea: a chip made only for 3D graphics", donker=0.6)),
 (ZR(19) - 0.15, scene("h1-concurrentie")),
 (ZR(23) - 0.15, lambda t, d, T0: (lambda img: (stempel(img, t - 0.2, "1995: NV1", DONKER), onder(img, t if T0 + t < ZR(24) else T0 + t - ZR(24), "A flop" if T0 + t < ZR(24) else "Close to running out of money", 0.2), img)[2])(foto("nv1", t, d, (1.0, 1.1), donker=0.6))),
 (ZR(25) - 0.15, scene("h1-riva")),
 (ZR(29) - 0.15, scene("h1-geforce")),
 (ZR(32) - 0.15, scene("h2-idee")),
 (ZR(35) - 0.15, scene("h2-cuda")),
 (ZR(38) - 0.15, fot_groot("geforce-vt", "2012: ALEXNET", "Trained on two Nvidia gaming cards", donker=0.35, size=130)),
 (ZR(39) - 0.15, alexnet_namen),
 (ZR(40) - 0.15, fot_groot("gtc-b", "AI discovers Nvidia", "AlexNet crushed a famous computer vision contest", GROEN, size=110)),
 (ZR(42) - 0.15, duo),
 (ZR(44) - 0.15, lambda t, d, T0: (lambda img: (stempel(img, t - 0.2, "2016: THE FIRST DGX-1", GROEN), onder(img, t, "Delivered by Jensen Huang himself", 0.3) if T0 + t < ZR(45) else R2.groot(img, T0 + t - ZR(45), "OpenAI", WIT, size=150), img)[2])(foto("openai", t, d, (1.0, 1.08), donker=0.5))),
 (ZR(46) - 0.15, scene("h3-chatgpt")),
 (ZR(48) - 0.15, fot_groot("meta-hq", "Everyone wanted AI", donker=0.4, size=110)),
 (ZR(49) - 0.15, scene("h3-iedereen")),
 (ZR(55) - 0.15, scene("h3-omzet")),
 (ZR(60) - 0.15, scene("h3-marge")),
 (ZR(62) - 0.15, scene("h3-koers")),
 (ZR(64) - 0.15, scene("h3-biljoen")),
 (ZR(67) - 0.15, lambda t, d, T0: (lambda img: (onder(img, t if T0 + t < ZR(68) else T0 + t - ZR(68), "A celebrity CEO" if T0 + t < ZR(68) else "Sold-out keynotes. Crowds of fans. A rock star CEO.", 0.2), img)[1])(foto("huang-c", t, d, (1.0, 1.1)))),
 (ZR(69) - 0.15, fot("ces2025", "Every year, a look at what's coming next", donker=0.8)),
 (ZR(70) - 0.15, scene("h3-ster")),
 (ZR(72) - 0.15, scene("h3-maar")),
 (ZR(74) - 0.15, scene("h4-regels")),
 (ZR(76) - 0.15, scene("h4-h20")),
 (ZR(81) - 0.15, scene("h4-h200")),
 (ZR(82) - 0.15, scene("h4-megaspeed")),
 (ZR(84) - 0.15, fot("singapore", "United States and Singapore: investigating possible export violations", donker=0.6)),
 (ZR(85) - 0.15, citaat_op("huang-f", ["Completely normal."], "Jensen Huang to Bloomberg, October 2026, about his dealings with Megaspeed")),
 (ZR(86) - 0.15, citaat_op("hq-wall", ["No reason to believe", "products had been diverted."], "Nvidia")),
 (ZR(87) - 0.15, scene("h4-vrouw")),
 (ZR(88) - 0.15, fot("nyt", "The New York Times: a close relationship with the executive", stamp="OCTOBER 29", kleur=ROOD, donker=0.6)),
 (ZR(89) - 0.15, citaat_op("hq-entry", ["Not unusual or unexpected."], "Nvidia spokesperson")),
 (ZR(90) - 0.15, fot("nyt", "Something far more serious", zoom=(1.1, 1.2), donker=0.45)),
 (ZR(91) - 0.15, scene("h5-spion")),
 (ZR(92) - 0.15, scene("h5-ontkenning")),
 (ZR(94) - 0.15, fot("capitol", "Republican committee chairmen ask Huang for a closed-door briefing", stamp="NOVEMBER 5", kleur=ROOD)),
 (ZR(95) - 0.15, lambda t, d, T0: (lambda img: (txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-9.3%", font(BLACK, 140), ROOD, ease((t - 1) / 0.4), "rm"), img)[1])(lijn(t, d, "2026-11-03", "2026-11-05", "NVIDIA STOCK", "November 3 to 5, 2026", teken=0.4)[0])),
 (ZR(96) - 0.15, scene("h5-brief")),
 (ZR(99) - 0.15, scene("h5-board")),
 (ZR(103) - 0.15, scene("h5-druk")),
 (ZR(105) - 0.15, fot("huang-h", stamp="NOVEMBER 12: RESIGNS", kleur=ROOD, zoom=(1.05, 1.15), pan=(0.6, 0.45, 0.62, 0.42), grijs=True)),
 (ZR(106) - 0.15, kress),
 (ZR(109) - 0.15, naamkaart_dark("HARVEY C. JONES", "First-ever chair of the Nvidia board", "hq-atrium")),
 (ZR(110) - 0.15, fot("capitol", "Democrats open their own investigation", zoom=(1.12, 1.2))),
 (ZR(111) - 0.15, scene("h5-koers")),
 (ZR(113) - 0.15, scene("h6-cijfers")),
 (ZR(116) - 0.15, scene("h6-kwartalen")),
 (ZR(118) - 0.15, scene("h6-datacenter")),
 (ZR(119) - 0.15, scene("h6-kress")),
 (ZR(122) - 0.15, scene("h6-terug")),
 (ZR(124) - 0.15, scene("h6-daling")),
 (ZR(126) - 0.15, fot_groot("wallst", "Why sell?", donker=0.4)),
 (ZR(127) - 0.15, lambda t, d, T0: R2.regels(foto("wallst", t, d, (1.08, 1.0), donker=0.35), T0 + t - ZR(127), ["Markets don't pay for the past.", "They pay for the future."] if T0 + t > ZR(128) else ["Markets don't pay for the past."])),
 (ZR(129) - 0.15, scene("h7-waarom")),
 (ZR(130) - 0.15, lambda t, d, T0: (lambda img: (txt(ImageDraw.Draw(img, "RGBA"), (200, 230), "QUESTION 1", font(BOLD, 40), ROOD, ease(t / 0.4)), txt(ImageDraw.Draw(img, "RGBA"), (200, 280), "CHINA", font(BLACK, 110), WIT, ease((t - 0.2) / 0.4)), onder(img, T0 + t - ZR(131), "Was American technology put at risk?", 0) if T0 + t > ZR(131) else None, img)[3])(foto("capitol", t, d, (1.0, 1.08), donker=0.4))),
 (ZR(132) - 0.15, scene("h7-leider")),
 (ZR(136) - 0.15, lambda t, d, T0: (lambda img: (onder(img, t if T0 + t < ZR(137) else T0 + t - ZR(137), "Apple after Steve Jobs. Microsoft after Bill Gates." if T0 + t < ZR(137) else "But not every company is that lucky", 0.2), img)[1])(foto("jobs-gates", t, d, (1.0, 1.08), donker=0.7))),
 (ZR(138) - 0.15, scene("h7-bubbel")),
 (ZR(141) - 0.15, fot("amd-hq", "AMD, Google, Amazon, Microsoft: building AI chips of their own", donker=0.6)),
 (ZR(142) - 0.15, fot("capitol", "Jensen Huang is expected to testify before Congress", stamp="BEFORE THANKSGIVING", kleur=ROOD, zoom=(1.0, 1.12))),
 (ZR(144) - 0.15, slot),   # 19 nov: geen zwaan, geen outro (eigenaar); laatste beeld fadet uit
]

def shot_op(t):
    k = max(i for i, (s0, _) in enumerate(SHOTS) if s0 <= t) if t >= SHOTS[0][0] else 0
    s0, fn = SHOTS[k]; e = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else R.EIND
    return (lambda tt, dd: fn(tt, dd, s0)), t - s0, e - s0, k

def main():
    van = float(sys.argv[sys.argv.index("--van") + 1]) if "--van" in sys.argv else 0.0
    tot = float(sys.argv[sys.argv.index("--tot") + 1]) if "--tot" in sys.argv else R.EIND
    uit = R.H / (f"v3-{van:.0f}-{tot:.0f}.mp4" if "--van" in sys.argv else "video-v3.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{HH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(uit)], stdin=subprocess.PIPE)
    vorige, wissel, oud = None, -99, None
    for i in range(int(van * FPS), int(tot * FPS)):
        t = i / FPS; fn, tt, dd, k = shot_op(t)
        img = fn(tt, max(dd, 0.5))
        if k != vorige and vorige is not None: wissel = i
        if 0 <= i - wissel < 6 and oud is not None: img = Image.blend(oud, img, (i - wissel + 1) / 7)   # zachtere overgang (0,4 s)
        else: oud = img
        vorige = k; p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit.name)

if __name__ == "__main__":
    main()
