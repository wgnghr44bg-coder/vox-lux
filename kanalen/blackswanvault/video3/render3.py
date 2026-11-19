"""BlackSwanVault video 3 (GTA 6 / Take-Two). Gebaseerd op video 2. Zelfde aanpak als video 1 (eigenaar 19 nov: "Ja zo is het goed"): per zin een
beeld dat letterlijk past (persoon -> echte foto met naam, bedrijf -> gebouw/logo, getal -> grafiek), 1 beeld per 1-2 zinnen,
geen geluidseffecten, geen hoofdstukken, geen intro of outro. Feiten: bronnen.md.
Gebruik: python render3.py [--van s --tot s]"""
import json, sys, datetime as DT
import render as R
from render import *   # noqa: F401,F403

Z = R.Z
def ZR(i, f=0.0): return Z[i][0] + f * (Z[i][1] - Z[i][0])
def na(i, T0, t): return T0 + t >= ZR(i) - 0.1           # is zin i al begonnen?
def sinds(i, T0, t): return T0 + t - ZR(i)

def groot(img, t, s, kleur=WIT, y=HH // 2, size=150, sub=None, start=0.0):
    d = ImageDraw.Draw(img, "RGBA"); a = ease((t - start) / 0.35); sc = 1.25 - 0.25 * a
    if s:                                                   # 19 nov: donkere balk achter grote tekst (leesbaar op drukke beelden)
        bw = max(d.textlength(s, font=font(BLACK, size)), d.textlength(sub or "", font=font(REG, 40))) + 120
        y0, y1 = y - size * 0.75, y + (size * 0.75 + 70 if sub else size * 0.7)
        d.rounded_rectangle([W // 2 - bw / 2, y0, W // 2 + bw / 2, y1], 18, fill=(0, 0, 0, int(165 * a)))
    txt(d, (W // 2, y), s, font(BLACK, int(size * sc)), kleur, a, "mm")
    if sub: txt(d, (W // 2, y + size * 0.75), sub, font(REG, 40), GRIJS, ease((t - start - 0.3) / 0.4), "mm")
    return img
def regels(img, t, rr, start=0.0, y=None, size=64, stap=0.5):
    d = ImageDraw.Draw(img, "RGBA"); y = y or HH // 2 - (len(rr) - 1) * size * 0.7
    for k, r in enumerate(rr):
        a = ease((t - start - k * stap) / 0.4)
        txt(d, (W // 2, y + k * size * 1.4 + 20 * (1 - a)), r, font(BOLD if k == 0 else REG, size if k == 0 else size * 0.7), WIT if k == 0 else GRIJS, a, "mm")
    return img

ORANJE = (236, 72, 153)                                    # accentkleur GTA 6 (Vice City-roze)
_logo = None
def logo_wit(img, a, y=420, breed=900):
    global _logo
    if _logo is None:
        l = Image.open(H / "echt/logo.png").convert("RGBA"); al = l.split()[3]
        w = Image.new("RGBA", l.size, (242, 242, 242, 255)); w.putalpha(al); _logo = w
    l = _logo.resize((breed, int(breed * _logo.height / _logo.width)), Image.LANCZOS)
    m = l.split()[3].point(lambda v: int(v * max(0, min(1, a))))
    img.paste(l, (W // 2 - breed // 2, y - l.height // 2), m)

def fot(naam, cap=None, stamp=None, kleur=DONKER, zoom=(1.0, 1.08), pan=(0.5, 0.5, 0.5, 0.5), donker=0.7, grijs=False, naamkaart=None):
    def f(t, d, T0):
        img = foto(naam, t, d, zoom, pan, grijs=grijs, donker=donker)
        if stamp: stempel(img, t - 0.2, stamp, kleur)
        if naamkaart: lower_third(img, t - 0.2, *naamkaart, kleur=ORANJE)
        elif cap: onder(img, t, cap, 0.3)
        return img
    return f

def portret(naam, donker=0.75):
    """Staande foto: scherp in het midden-links op volle hoogte, wazige versie als achtergrond."""
    def a(t, d):
        if naam not in _portret:
            im = Image.open(H / f"echt/{naam}.jpg").convert("RGB"); _portret[naam] = im
        im = _portret[naam]; z = 1.0 + 0.05 * eio(t / d)
        bg = im.resize((W, int(W * im.height / im.width))).crop((0, 0, W, HH)).filter(ImageFilter.GaussianBlur(30))
        bg = ImageEnhance.Brightness(bg).enhance(0.35)
        h = int(HH * z); fg = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
        fg = ImageEnhance.Brightness(fg).enhance(donker); bg.paste(fg, (W // 2 - fg.width // 2, (HH - h) // 2)); credit(bg, naam); return bg
    return a
_portret = {}

def fasen(achter, stappen):
    """Eén achtergrond, tekst wisselt per zin: stappen = [(zin, overlay(img, t_sinds_zin))...]"""
    def f(t, d, T0):
        img = achter(t, d); act = None
        for i, ov in stappen:
            if na(i, T0, t): act = (i, ov)
        if act: act[1](img, sinds(act[0], T0, t) + 0.1)
        return img
    return f
def F(naam, zoom=(1.0, 1.08), donker=0.7, grijs=False, pan=(0.5, 0.5, 0.5, 0.5), blur=0):
    def a(t, d):
        im = foto(naam, t, d, zoom, pan, grijs=grijs, donker=donker)
        return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im
    return a
def ON(s): return lambda img, t: onder(img, t, s, 0.1)
def ST(s, k=ORANJE): return lambda img, t: stempel(img, t, s, k)
def GR(s, sub=None, kleur=WIT, size=140): return lambda img, t: groot(img, t, s, kleur, size=size, sub=sub)
def LT(a_, b_): return lambda img, t: lower_third(img, t, a_, b_, kleur=ORANJE)
def EN(*fs):
    def g(img, t):
        for f_ in fs: f_(img, t)
    return g

def doc(bron_s, titel, regels_, mark=None, achter="nasdaq-a", mark_na=None):
    def f(t, d, T0):
        img = foto(achter, t, d, (1.0, 1.04), donker=0.25).filter(ImageFilter.GaussianBlur(6))
        dr = ImageDraw.Draw(img, "RGBA"); z = 1.0 + 0.03 * eio(t / d)
        x0, y0, x1, y1 = W // 2 - 560 * z, 200 - 10 * z, W // 2 + 560 * z, 880 + 10 * z; a = ease(t / 0.4)
        dr.rectangle([x0, y0 + 30 * (1 - a), x1, y1 + 30 * (1 - a)], fill=(246, 246, 242, int(255 * a)))
        dr.rectangle([x0, y0 + 30 * (1 - a), x1, y0 + 8 + 30 * (1 - a)], fill=ORANJE + (int(255 * a),))
        txt(dr, (x0 + 60, y0 + 50), bron_s.upper(), font(BOLD, 26), (110, 110, 110), a)
        yy = y0 + 110
        import textwrap
        for r in textwrap.wrap(titel, 38):
            txt(dr, (x0 + 60, yy), r, font(BOLD, 50), (20, 20, 20), a); yy += 64
        yy += 40
        for k, r in enumerate(regels_):
            if k == mark and (mark_na is None or na(mark_na, T0, t)):
                t0 = 0.8 if mark_na is None else sinds(mark_na, T0, t) + 0.3
                p = ease((t0 - 0.0) / 0.7) if mark_na is not None else ease((t - 0.8) / 0.7)
                w = dr.textlength(r, font=font(REG, 38))
                dr.rectangle([x0 + 50, yy - 6, x0 + 70 + w * p, yy + 50], fill=(255, 226, 60, int(220 * a)))
            txt(dr, (x0 + 60, yy), r, font(BOLD if k == mark else REG, 38), (30, 30, 30), a); yy += 76
        return img
    return f

# ---------- grafieken ----------
def balken(items, titel, sub, bron_s, fmt, tijden, hl=None, kleur=ORANJE, schaal=None, extra=None):
    """items = [(label, waarde)], tijden = per balk de zin waarop hij verschijnt."""
    def f(t, d, T0):
        img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
        txt(dr, (200, 110), titel, font(BOLD, 50), a=ease(t / 0.4)); txt(dr, (200, 175), sub, font(REG, 30), GRIJS, ease(t / 0.4))
        n = len(items); X0, X1, Y0, Yt = 260, 1680, 900, 330; bw = (X1 - X0) / n * 0.62; mx = schaal or max(v for _, v in items)
        for i, (lab, v) in enumerate(items):
            p = ease(sinds(tijden[i], T0, t) / 0.8) if na(tijden[i], T0, t) else 0
            x = X0 + (X1 - X0) * (i + 0.19) / n; h = (Y0 - Yt) * v / mx * p
            k = kleur if hl is None or i == hl else (95, 97, 104)
            if p > 0:
                dr.rectangle([x, Y0 - h, x + bw, Y0], fill=k + (255,))
                txt(dr, (x + bw / 2, Y0 - h - 14), fmt(v * p), font(BOLD, 40), WIT, min(1, p * 2), "ms")
                txt(dr, (x + bw / 2, Y0 + 24), lab, font(REG, 30), GRIJS, min(1, p * 2), "ma")
        if extra: extra(img, t, T0)
        bron(img, bron_s); return img
    return f


def lijst(achter, titel, items):                           # items = [(zin, tekst)]
    def f(t, d, T0):
        img = foto(achter, t, d, (1.0, 1.06), donker=0.28).filter(ImageFilter.GaussianBlur(3)); dr = ImageDraw.Draw(img, "RGBA")
        txt(dr, (240, 210), titel, font(BLACK, 76), WIT, ease(t / 0.4))
        for k, (z, s) in enumerate(items):
            if not na(z, T0, t): continue
            a = ease(sinds(z, T0, t) / 0.45); y = 360 + k * 120
            dr.rectangle([240, y + 4, 254, y + 66], fill=ORANJE + (int(255 * a),))
            txt(dr, (290 + 30 * (1 - a), y), s, font(BOLD, 52), WIT, a)
        return img
    return f

def slot_fade(naam, cap):
    def f(t, d, T0):
        img = foto(naam, t, d, (1.0, 1.1), grijs=True, donker=0.5); onder(img, t, cap, 0.3)
        if t > d - 1.8: img = Image.blend(img, Image.new("RGB", (W, HH)), min(1, (t - (d - 1.8)) / 1.8))
        return img
    return f

def logo_kaart(achter, kop=None, sub=None, stamp=None):
    def f(t, d, T0):
        img = foto(achter, t, d, (1.0, 1.06), donker=0.22).filter(ImageFilter.GaussianBlur(5)); a = ease(t / 0.5)
        logo_wit(img, a, 400 if kop else 520, 760); dr = ImageDraw.Draw(img, "RGBA")
        if kop: txt(dr, (W // 2, 590), kop, font(BLACK, 96), ORANJE, ease((t - 0.35) / 0.4), "mm")
        if sub: txt(dr, (W // 2, 685), sub, font(REG, 42), GRIJS, ease((t - 0.6) / 0.4), "mm")
        if stamp: stempel(img, t - 0.2, stamp, ORANJE)
        return img
    return f


# ---------- Take-Two koers (Yahoo, data/ttwo.json) ----------
import datetime as _D
_k = json.load(open(H / "data/ttwo.json"))["chart"]["result"][0]
R.KOERS[:] = [(_D.datetime.fromtimestamp(a, _D.UTC).date(), v) for a, v in zip(_k["timestamp"], _k["indicators"]["quote"][0]["close"]) if v]

def koers(van, tot, titel, sub, markers=(), labels=(), teken=0.75, kleur=ORANJE):
    """labels = [(zin, x, y, tekst, kleur)] verschijnen op een zin."""
    def f(t, d, T0):
        img, _ = lijn(t, d, van, tot, titel, sub, markers=markers, kleur=kleur, teken=teken)
        dr = ImageDraw.Draw(img, "RGBA")
        for z, x, y, s, k in labels:
            if na(z, T0, t): txt(dr, (x, y), s, font(BLACK, 120), k, ease(sinds(z, T0, t) / 0.4), "rm")
        bron(img, "Source: Take-Two Interactive (NASDAQ: TTWO) closing prices, via Yahoo Finance")
        return img
    return f

def tijdlijn(t, d, T0):                                    # zin 35-37: de beloofde datums
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (W // 2, 230), "The release date kept moving", font(BLACK, 76), WIT, ease(t / 0.4), "mm")
    pts = [(85, "FALL 2025", "First promise"), (86, "MAY 26, 2026", "Delay 1"), (88, "NOV 19, 2026", "Delay 2")]
    y = 560; x0, x1 = 300, 1620
    dr.line([(x0, y), (x1, y)], fill=(255, 255, 255, 70), width=4)
    for i, (z, a_, b_) in enumerate(pts):
        x = x0 + i * (x1 - x0) / 2
        if not na(z, T0, t) and i > 0: continue
        a = ease(sinds(z, T0, t) / 0.4) if i > 0 else ease(t / 0.4)
        weg = i < 2 and na(pts[i + 1][0], T0, t)
        dr.ellipse([x - 16, y - 16, x + 16, y + 16], fill=(ROOD if weg else ORANJE) + (int(255 * a),))
        txt(dr, (x, y - 60), a_, font(BOLD, 46), GRIJS if weg else WIT, a, "ms"); txt(dr, (x, y + 50), b_, font(REG, 32), GRIJS, a, "ma")
        if weg: dr.line([(x - 150, y - 78), (x + 150, y - 78)], fill=ROOD + (255,), width=6)
    return img

SHOTS = [
 (0.0, fasen(F("open-woonkamer", (1.0, 1.15), 0.4), [(0, ST("NOVEMBER 19, 2026")), (1, GR("GRAND THEFT AUTO VI", None, WIT, 130))])),
 (ZR(2) - 0.15, fasen(F("gta-vc-skyline", (1.12, 1.0), 0.45), [(2, GR("13 YEARS", "since Grand Theft Auto V", WIT, 170))])),
 (ZR(3) - 0.15, fasen(F("open-feest", (1.0, 1.12), 0.45), [(3, GR("19 MILLION+", "copies on day one · Sensor Tower estimate", WIT, 160))])),
 (ZR(4) - 0.15, fasen(F("open-geld", (1.12, 1.0), 0.45), [(4, GR("~$1.8 BILLION", "in 24 hours · Sensor Tower estimate", ORANJE, 160)),
                                                         (5, GR("THE BIGGEST LAUNCH EVER?", "in entertainment history", WIT, 110))])),
 (ZR(6) - 0.15, fasen(F("open-bios", (1.0, 1.12), 0.45), [(6, GR("Bigger than any movie.", None, WIT, 110))])),
 (ZR(7) - 0.15, fasen(F("open-concert", (1.12, 1.0), 0.45), [(7, GR("Bigger than any album.", None, WIT, 110))])),
 (ZR(8) - 0.15, koers("2025-12-31", "2026-11-19", "TAKE-TWO INTERACTIVE STOCK", "Daily closing price, 2026", labels=[(9, 1700, 330, "-16%", ROOD)], teken=0.6, kleur=ROOD)),
 (ZR(10) - 0.15, fasen(F("v:mk-5456", (1.0, 1.06), 0.5), [(10, GR("So why are investors cold?", None, WIT, 90))])),
 (ZR(11) - 0.15, fasen(F("open-2013", (1.1, 1.0), 0.5), [(11, ST("2013")), (12, EN(ST("SEPTEMBER 2013"), ON("Grand Theft Auto V is released")))])),
 (ZR(13) - 0.15, balken([("Day 1", 0.8), ("Day 3", 1.0)], "GRAND THEFT AUTO V SALES, 2013", "Billions of dollars", "Source: Take-Two Interactive",
                        lambda v: f"${v:.1f}B" if v >= 1 else f"${v * 1000:.0f}M", [13, 14])),
 (ZR(15) - 0.15, fasen(F("dundee", (1.0, 1.08), 0.6), [(15, ON("Where it all began")), (16, LT("DMA DESIGN", "Dundee, Scotland · the first Grand Theft Auto, 1997"))])),
 (ZR(17) - 0.15, fasen(F("v:mk-48272", (1.0, 1.06), 0.55), [(17, ON("A simple game, seen from above")), (18, ON("Controversial, and people got curious"))])),
 (ZR(19) - 0.15, fasen(F("v:mk-4442", (1.0, 1.06), 0.5), [(19, ST("NEW YORK, 1998")), (20, GR("ROCKSTAR GAMES", None, WIT, 130)), (21, LT("SAM HOUSER", "President of Rockstar Games"))])),
 (ZR(22) - 0.15, fasen(F("v:mk-30544", (1.0, 1.06), 0.55), [(22, ON("His brother Dan Houser left in 2020")), (23, LT("TAKE-TWO INTERACTIVE", "Founded in New York in 1993"))])),
 (ZR(24) - 0.15, fasen(F("rockstar-north-b", (1.0, 1.08), 0.6), [(24, EN(ST("1999"), ON("Take-Two buys DMA Design"))), (25, LT("ROCKSTAR NORTH", "Formerly DMA Design"))])),
 (ZR(26) - 0.15, lijst("gta-vc-skyline-nacht", "Bigger every time", [(26, "2001: GTA III, a full 3D city"), (27, "2002: Vice City, 1980s Miami"), (28, "2004: San Andreas, best-selling PS2 game"), (29, "2008: GTA IV, a version of New York")])),
 (ZR(30) - 0.15, fasen(F("v:mk-47140", (1.0, 1.06), 0.5), [(30, ON("Each game bigger than the last")), (31, ON("And more important to Take-Two"))])),
 (ZR(32) - 0.15, fasen(F("gta5-trio", (1.0, 1.08), 0.5), [(32, ON("But the real surprise came later")), (33, ON("GTA V never stopped selling")), (34, ON("Released again and again"))])),
 (ZR(35) - 0.15, fasen(F("v:mk-23501", (1.0, 1.06), 0.5), [(35, ON("2013: PlayStation 3 and Xbox 360")), (36, ON("2014-2015: PlayStation 4, Xbox One and PC")), (37, ON("2022: PlayStation 5 and the newest Xbox"))])),
 (ZR(38) - 0.15, fasen(F("v:mk-43538", (1.0, 1.06), 0.45), [(38, GR("230 MILLION+", "copies of GTA V sold · Take-Two", WIT, 160)), (39, GR("230 MILLION+", "One of the best-selling games of all time", WIT, 160))])),
 (ZR(40) - 0.15, lijst("gta5-online", "GTA Online: players kept paying", [(41, "Cars"), (42, "Houses"), (43, "In-game money")])),
 (ZR(44) - 0.15, fasen(F("gta-vc-auto", (1.08, 1.0), 0.55), [(44, ST("OCTOBER 2013: GTA ONLINE")), (45, ON("Shark Cards: virtual money for real money")), (46, ON("Still earning, more than ten years later")),
                                                         (47, ON("Long after most games are forgotten")), (48, ON("GTA VI could do the same"))])),
 (ZR(49) - 0.15, fasen(F("rockstar-north", (1.0, 1.08), 0.7), [(49, ON("Made by Rockstar Games")), (50, LT("ROCKSTAR NORTH", "Edinburgh, Scotland"))])),
 (ZR(51) - 0.15, fasen(F("edinburgh", (1.0, 1.08), 0.55), [(51, ON("Known for huge, detailed worlds, built over many years")), (52, ON("Studios in Britain, the US, Canada and India")), (53, ON("All those years, Take-Two relied on GTA V"))])),
 (ZR(54) - 0.15, fot("v:mk-11712", naamkaart=("TAKE-TWO INTERACTIVE", "Owner of Rockstar Games · New York"), donker=0.6)),
 (ZR(55) - 0.15, fasen(portret("zelnick"), [(55, LT("STRAUSS ZELNICK", "Take-Two chairman since 2007, CEO since 2011")), (57, ON("For him, GTA VI is not just a game")),
                                            (58, ON("The biggest bet the company has ever made"))])),
 (ZR(59) - 0.15, fasen(F("zynga", (1.0, 1.08), 0.55), [(59, ON("Take-Two also grew by buying companies")), (60, GR("$12.7 BILLION", "Take-Two buys Zynga, 2022", WIT, 150)),
                                                       (61, ON("One of the biggest deals in gaming history"))])),
 (ZR(62) - 0.15, fasen(F("v:mk-45735", (1.0, 1.06), 0.5), [(62, ON("A giant in mobile games")), (63, ON("Also owns 2K, publisher of NBA 2K")),
                                                       (64, ON("Nothing comes close to Grand Theft Auto"))])),
 (ZR(65) - 0.15, fasen(F("miami-night", (1.1, 1.0), 0.35), [(65, ST("DECEMBER 2023: TRAILER 1")), (66, EN(ST("DECEMBER 2023: TRAILER 1"), ON("Released a day early, after it leaked"))), (67, EN(ST("DECEMBER 2023: TRAILER 1"), ON("Music: Tom Petty, Love Is a Long Road")))])),
 (ZR(68) - 0.15, fasen(F("v:mk-12028", (1.0, 1.06), 0.45), [(68, GR("90 MILLION+", "YouTube views in 24 hours", WIT, 160)),
                                                           (69, GR("WORLD RECORD", "most viewed video game reveal in 24 hours · Guinness", ORANJE, 140))])),
 (ZR(70) - 0.15, fasen(F("v:mk-11814", (1.0, 1.06), 0.45), [(70, ON("The second trailer did even better")), (71, GR("475 MILLION", "views in 24 hours, all platforms · Rockstar", WIT, 160))])),
 (ZR(72) - 0.15, fasen(F("gta-vc-politie", (1.0, 1.1), 0.5), [(72, ON("The road to launch was not smooth")), (73, ST("FEBRUARY 2022: CONFIRMED")), (74, ST("SEPTEMBER 2022: THE LEAK", ROOD)),
                                                     (75, GR("THE BIGGEST LEAK", "in video game history", ROOD, 125))])),
 (ZR(76) - 0.15, fasen(F("v:mk-31378", (1.0, 1.06), 0.5), [(76, ON("A young Lapsus hacker, held responsible by a British court")),
                                                     (77, ON("Rockstar: extremely disappointed, but work continues"))])),
 (ZR(78) - 0.15, fasen(F("gta-vc-nacht", (1.0, 1.08), 0.7), [(78, LT("LEONIDA", "Rockstar's version of Florida")), (79, ON("At its center: Vice City")), (80, ON("Last visit: a story set in 1986"))])),
 (ZR(81) - 0.15, fasen(F("gta-lucia-jason", (1.0, 1.08), 0.75), [(81, ON("Two main characters: Lucia and Jason"))])),
 (ZR(82) - 0.15, fasen(F("gta-moeras", (1.0, 1.08), 0.7), [(82, ON("City, swamps, beaches and small towns"))])),
 (ZR(83) - 0.15, fasen(F("gta-jason-motor", (1.0, 1.08), 0.7), [(83, ST("PS5 AND XBOX SERIES ONLY"))])),
 (ZR(84) - 0.15, tijdlijn),
 (ZR(87) - 0.15, koers("2025-04-01", "2025-12-31", "TAKE-TWO INTERACTIVE STOCK", "Daily closing price, April to December 2025",
                       markers=[("2025-05-02", "Delay 1"), ("2025-11-07", "Delay 2")], labels=[(38, 700, 330, "-7%", ROOD), (40, 1700, 330, "-8%", ROOD)], teken=0.9)),
 (ZR(90) - 0.15, fasen(portret("zelnick", 0.6), [(90, ON("Strauss Zelnick stayed calm")), (91, ON("Never regretted a delay, looking back")),
                                                  (92, ON("Highly confident in the new date"))])),
 (ZR(93) - 0.15, koers("2026-11-09", "2026-11-19", "TAKE-TWO INTERACTIVE STOCK", "Daily closing price, November 9 to 19, 2026",
                       markers=[("2026-11-18", "Reviews"), ("2026-11-19", "Launch")], labels=[(46, 1700, 330, "+6%", GROEN)], teken=0.9)),
 (ZR(96) - 0.15, fasen(F("gta6-cover", (1.0, 1.06), 0.6), [(96, ST("NOVEMBER 19: LAUNCH")), (97, ON("Many fans had paid in advance")), (98, ON("Pre-orders opened in June 2026")), (99, GR("~75%", "of first-day sales on PlayStation · Sensor Tower", WIT, 170)),
                                                    (100, ON("Sony and Microsoft shares went up")), (101, ST("TAKE-TWO STOCK: DOWN", ROOD))])),
 (ZR(102) - 0.15, balken([("RDR2 · first 3 days", 0.725), ("Endgame · opening weekend", 1.2), ("GTA VI · day one (est.)", 1.8)], "BIG LAUNCHES COMPARED",
                        "Billions of dollars", "Sources: Take-Two, Disney, Sensor Tower estimate", lambda v: f"${v:.2f}B" if v < 1 else f"${v:.1f}B", [103, 105, 106], hl=2)),
 (ZR(107) - 0.15, fasen(F("v:mk-9607", (1.0, 1.06), 0.35), [(107, GR("Why?", None, WIT, 170)), (108, GR("An old Wall Street saying", None, WIT, 90)),
                                                       (109, GR("Buy the rumor,", "sell the news.", ORANJE, 120)), (110, ON("Investors had been betting on this game for years"))])),
 (ZR(111) - 0.15, koers("2024-11-19", "2026-11-19", "TAKE-TWO INTERACTIVE STOCK", "Daily closing price, two years", markers=[("2025-10-20", "High")], labels=[(107, 1300, 330, "$262", GROEN)], teken=0.9)),
 (ZR(113) - 0.15, fasen(F("v:mk-47012", (1.0, 1.06), 0.45), [(113, ON("By launch day, the good news was already in the price"))])),
 (ZR(114) - 0.15, lijst("v:mk-43540", "What comes after", [(117, "How long people keep playing"), (118, "How much they spend in the game"), (119, "Rockstar's next big game")])),
 (ZR(120) - 0.15, fasen(F("gta-vc-zwembad", (1.08, 1.0), 0.55), [(120, ON("No PC version announced yet")), (121, ON("In the past: PC came later, sometimes years later"))])),
 (ZR(122) - 0.15, fasen(F("nasdaq-a", (1.0, 1.08), 0.35), [(122, GR("~$9.8 BILLION", "Take-Two bookings this fiscal year · Wells Fargo forecast", WIT, 150)),
                                                          (123, ON("Bookings: money from sales, before accounting spreads it out")), (124, GR("A RECORD", None, GROEN, 150)), (125, ON("But much of it depends on one game"))])),
 (ZR(126) - 0.15, fasen(F("v:mk-47213", (1.0, 1.06), 0.35), [(126, GR("What happens next?", None, WIT, 100)), (127, GR("OFFICIAL NUMBERS", "not published yet", WIT, 130)),
                                                        (128, GR("WITHIN DAYS", "expected by Bank of America", ORANJE, 130))])),
 (ZR(129) - 0.15, fasen(F("v:mk-4330", (1.0, 1.06), 0.45), [(130, GR("FEBRUARY", "Take-Two reports its holiday quarter", WIT, 140)), (131, ON("The real numbers")), (132, ON("Was the long wait worth it?"))])),
 (ZR(133) - 0.15, fot("v:mk-24550", "In the end, Rockstar did it again", donker=0.6)),
 (ZR(134) - 0.15, fasen(F("gta-vc-skyline", (1.08, 1.0), 0.55), [(134, ON("The players came")), (135, ON("The money came"))])),
 (ZR(136) - 0.15, slot_fade("miami-night-b", "What comes next?")),
]

def shot_op(t):
    k = max(i for i, (s0, _) in enumerate(SHOTS) if s0 <= t) if t >= SHOTS[0][0] else 0
    s0, fn = SHOTS[k]; e = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else R.EIND
    return (lambda tt, dd: fn(tt, dd, s0)), t - s0, e - s0, k

def main():
    van = float(sys.argv[sys.argv.index("--van") + 1]) if "--van" in sys.argv else 0.0
    tot = float(sys.argv[sys.argv.index("--tot") + 1]) if "--tot" in sys.argv else R.EIND
    if "--plaat" in sys.argv:                              # controleplaat: één frame per shot (midden)
        uit = sys.argv[sys.argv.index("--plaat") + 1]; ims = []
        for k, (s0, fn) in enumerate(SHOTS):
            e = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else R.EIND; tm = s0 + (e - s0) * 0.8
            ims.append(fn(tm - s0, max(e - s0, 0.5), s0).resize((480, 270)))
        cols = 6; rows = (len(ims) + cols - 1) // cols; pl = Image.new("RGB", (cols * 480, rows * 270))
        for k, im in enumerate(ims): pl.paste(im, ((k % cols) * 480, (k // cols) * 270))
        pl.save(uit, quality=82); print("plaat", uit, len(ims)); return
    uit = R.H / (f"v-{van:.0f}-{tot:.0f}.mp4" if "--van" in sys.argv else "video.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{HH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", str(uit)], stdin=subprocess.PIPE)
    vorige, wissel, oud = None, -99, None
    for i in range(int(van * FPS), int(tot * FPS)):
        t = i / FPS; fn, tt, dd, k = shot_op(t)
        img = fn(tt, max(dd, 0.5))
        z = 1.0 + 0.03 * eio(tt / max(dd, 0.5))          # 19 nov: altijd rustige beweging, ook op grafieken (geen stilstand)
        cw, ch = W / z, HH / z; img = img.resize((W, HH), Image.BICUBIC, box=((W - cw) / 2, (HH - ch) / 2, (W + cw) / 2, (HH + ch) / 2))
        if k != vorige and vorige is not None: wissel = i
        if 0 <= i - wissel < 6 and oud is not None: img = Image.blend(oud, img, (i - wissel + 1) / 7)
        else: oud = img
        vorige = k; p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit.name)

if __name__ == "__main__":
    main()
