"""BlackSwanVault video 2 (Anthropic IPO). Zelfde aanpak als video 1 (eigenaar 19 nov: "Ja zo is het goed"): per zin een
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
    txt(d, (W // 2, y), s, font(BLACK, int(size * sc)), kleur, a, "mm")
    if sub: txt(d, (W // 2, y + size * 0.75), sub, font(REG, 40), GRIJS, ease((t - start - 0.3) / 0.4), "mm")
    return img
def regels(img, t, rr, start=0.0, y=None, size=64, stap=0.5):
    d = ImageDraw.Draw(img, "RGBA"); y = y or HH // 2 - (len(rr) - 1) * size * 0.7
    for k, r in enumerate(rr):
        a = ease((t - start - k * stap) / 0.4)
        txt(d, (W // 2, y + k * size * 1.4 + 20 * (1 - a)), r, font(BOLD if k == 0 else REG, size if k == 0 else size * 0.7), WIT if k == 0 else GRIJS, a, "mm")
    return img

ORANJE = (217, 119, 87)                                    # accentkleur voor Anthropic-kaarten
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

def verlies(t, d, T0):                                     # zin 74-78: omzet, nettoverlies, operationele kasstroom
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (200, 110), "ANTHROPIC, FIRST NINE MONTHS OF 2026", font(BOLD, 50), a=ease(t / 0.4))
    txt(dr, (200, 175), "Billions of dollars", font(REG, 30), GRIJS, ease(t / 0.4))
    Y0 = 600; sch = 2.6
    rij = [("Revenue", 33.2, GROEN, 103), ("Net loss", -104.0, ROOD, 104), ("Cash from operations", 6.6, GROEN, 106)]
    for i, (lab, v, k, z) in enumerate(rij):
        if not na(z, T0, t): continue
        p = ease(sinds(z, T0, t) / 0.9); x = 420 + i * 420; h = v * sch * p
        dr.rectangle([x, min(Y0, Y0 - h), x + 230, max(Y0, Y0 - h)], fill=k + (255,))
        txt(dr, (x + 115, Y0 - h - 16 if v > 0 else Y0 - h + 16), f"{'-' if v < 0 else '+'}${abs(v) * p:.1f}B", font(BOLD, 44), WIT, min(1, p * 2), "ms" if v > 0 else "ma")
        txt(dr, (x + 115, Y0 + 20 if v > 0 else Y0 - 50), lab, font(REG, 30), GRIJS, min(1, p * 2), "ma" if v > 0 else "ms")
    dr.line([(300, Y0), (1650, Y0)], fill=(255, 255, 255, 90), width=2)
    if na(105, T0, t): txt(dr, (W // 2, 990), "Most of the loss: a non-cash accounting charge", font(BOLD, 36), WIT, ease(sinds(105, T0, t) / 0.4), "mm")
    bron(img, "Source: Anthropic S-1 (amended), via Fox Business"); return img

def intraday(t, d, T0):
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (200, 110), "ANTHROPIC (NASDAQ: ANT)", font(BOLD, 50), a=ease(t / 0.4))
    txt(dr, (200, 175), "First day of trading, November 19, 2026 (New York time)", font(REG, 30), GRIJS, ease(t / 0.4))
    pts = INTRA
    X0, X1, Y0, Y1 = 220, 1700, 880, 300
    lo, hi = min(min(v for _, v in pts), 83) - 4, max(v for _, v in pts) + 4
    def xy(k, v): return X0 + (X1 - X0) * k / max(1, len(pts) - 1), Y0 + (Y1 - Y0) * (v - lo) / (hi - lo)
    for k in range(5):
        v = lo + (hi - lo) * k / 4; y = Y0 + (Y1 - Y0) * k / 4
        dr.line([(X0, y), (X1, y)], fill=(255, 255, 255, 18)); txt(dr, (X0 - 20, y), f"${v:,.0f}", font(REG, 24), GRIJS, 1, "rm")
    _, yi = xy(0, 83); dr.line([(X0, yi), (X1, yi)], fill=(255, 255, 255, 110), width=2)
    txt(dr, (X1, yi + 12), "IPO price $83", font(BOLD, 28), GRIJS, 1, "ra")
    p = eio(sinds(116, T0, t) / max(0.5, ZR(118) - ZR(116))) if na(116, T0, t) else 0.02
    n = max(2, int(len(pts) * p)); xs = [xy(k, pts[k][1]) for k in range(n)]
    dr.polygon(xs + [(xs[-1][0], Y0), (xs[0][0], Y0)], fill=ORANJE + (40,)); dr.line(xs, fill=ORANJE + (255,), width=6, joint="curve")
    x, y = xs[-1]; dr.ellipse([x - 11, y - 11, x + 11, y + 11], fill=ORANJE + (255,)); txt(dr, (x + 18, y - 30), f"${pts[n - 1][1]:,.2f}", font(BOLD, 36), WIT, 1)
    for k in range(0, len(pts), max(1, len(pts) // 5)):
        txt(dr, (xy(k, 0)[0], Y0 + 30), pts[k][0], font(REG, 24), GRIJS, 1, "ma")
    bron(img, "Source: Yahoo Finance, 5-minute prices"); return img
try:
    _q = json.load(open(H / "data/ant-intraday.json"))["chart"]["result"][0]
    from zoneinfo import ZoneInfo
    INTRA = [(DT.datetime.fromtimestamp(ts, ZoneInfo("America/New_York")).strftime("%H:%M"), v)
             for ts, v in zip(_q["timestamp"], _q["indicators"]["quote"][0]["close"]) if v]
except Exception:
    INTRA = [("11:48", 111.5), ("16:00", 100.0)]

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

def duo(t, d, T0):                                          # Amazon links, Google rechts (zin 28-32)
    img = leeg(); a_ = foto("amazon", t, d, (1.0, 1.05), donker=0.6); g_ = foto("google", t, d, (1.0, 1.05), donker=0.6)
    img.paste(a_.crop((W // 4, 0, W // 4 + W // 2, HH)), (0, 0)); img.paste(g_.crop((W // 4, 0, W // 4 + W // 2, HH)), (W // 2, 0))
    dr = ImageDraw.Draw(img, "RGBA"); dr.rectangle([W // 2 - 3, 0, W // 2 + 3, HH], fill=(0, 0, 0, 255))
    def kaart(x, kop, regel, z):
        if not na(z, T0, t): return
        a = ease(sinds(z, T0, t) / 0.45); dr.rectangle([x - 380, 380, x + 380, 640], fill=(0, 0, 0, int(170 * a)))
        txt(dr, (x, 450), kop, font(BLACK, 80), WIT, a, "mm"); txt(dr, (x, 560), regel, font(BOLD, 46), ORANJE, a, "mm")
    if not na(44, T0, t): txt(dr, (W // 2, 160), "Two of the richest companies on Earth", font(BLACK, 64), WIT, ease(t / 0.4), "mm")
    kaart(W // 4, "AMAZON", "Up to $4B · Sept 2023" if not na(46, T0, t) else "+$4B more · Nov 2024", 29)
    kaart(3 * W // 4, "GOOGLE", "Up to $2B · Oct 2023", 30)
    if na(47, T0, t): onder(img, sinds(47, T0, t), "Two rivals, one bet", 0.1)
    credit_s = "Photos: Buiobuione / CC BY-SA 4.0 · Asoundd / CC BY-SA 4.0 / Wikimedia Commons"
    bron(img, credit_s)
    return img

def prijs(t, d, T0):                                        # zin 5-6
    img = foto("nasdaq-a", t, d, (1.0, 1.06), donker=0.3).filter(ImageFilter.GaussianBlur(3)); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (W // 2, 330), "FIRST TRADE", font(BOLD, 44), GRIJS, ease(t / 0.4), "mm")
    teller(img, t, 111.5, lambda v: f"${v:,.2f}", 470, 190, WIT, 1.2, 0.1)
    if na(6, T0, t):
        a = ease(sinds(6, T0, t) / 0.4)
        txt(dr, (W // 2, 640), "+34%", font(BLACK, 120), GROEN, a, "mm"); txt(dr, (W // 2, 740), "above the IPO price of $83", font(REG, 42), GRIJS, a, "mm")
    return img

def range_kaart(t, d, T0):                                  # zin 83-86
    img = foto("nasdaq-c", t, d, (1.0, 1.06), donker=0.3).filter(ImageFilter.GaussianBlur(3)); dr = ImageDraw.Draw(img, "RGBA")
    a = ease(t / 0.4); txt(dr, (W // 2, 300), "PLANNED PRICE RANGE", font(BOLD, 40), GRIJS, a, "mm")
    txt(dr, (W // 2, 400), "$70 – $78", font(BLACK, 130), WIT, a, "mm")
    if na(112, T0, t):
        b = ease(sinds(112, T0, t) / 0.4); dr.line([(W // 2 - 300, 405), (W // 2 - 300 + 600 * b, 405)], fill=ROOD + (255,), width=10)
        txt(dr, (W // 2, 560), "PRICED AT $83", font(BLACK, 110), GROEN, b, "mm")
    if na(113, T0, t):
        c = ease(sinds(113, T0, t) / 0.4); txt(dr, (W // 2, 700), "980 million shares", font(BOLD, 48), WIT, c, "mm")
    if na(114, T0, t):
        e = ease(sinds(114, T0, t) / 0.4); txt(dr, (W // 2, 790), "Up to 20% for ordinary investors", font(BOLD, 48), ORANJE, e, "mm")
    return img

def macht(t, d, T0):                                         # zin 91-94
    img = raster(leeg()); dr = ImageDraw.Draw(img, "RGBA")
    txt(dr, (W // 2, 200), "Who controls Anthropic?", font(BLACK, 80), WIT, ease(t / 0.4), "mm")
    if na(120, T0, t):
        p = ease(sinds(120, T0, t) / 0.9); X0, X1 = 300, 1620
        dr.rectangle([X0, 400, X1, 500], fill=(60, 62, 68, 255)); dr.rectangle([X0, 400, X0 + (X1 - X0) * 0.501 * p, 500], fill=ORANJE + (255,))
        txt(dr, (X0, 380), "Founders' share of the votes", font(BOLD, 36), WIT, 1, "ls"); txt(dr, (X0 + (X1 - X0) * 0.501 * p, 450), f" {50.1 * p:.1f}%", font(BLACK, 56), WIT, 1, "lm")
    if na(121, T0, t):
        a = ease(sinds(121, T0, t) / 0.4); txt(dr, (W // 2, 650), "LONG-TERM BENEFIT TRUST", font(BLACK, 70), ORANJE, a, "mm")
        txt(dr, (W // 2, 730), "picks most of the board", font(REG, 44), GRIJS, a, "mm")
    if na(122, T0, t): txt(dr, (W // 2, 830), "Meant to put the long-term good of people first", font(BOLD, 44), WIT, ease(sinds(122, T0, t) / 0.4), "mm")
    bron(img, "Source: Anthropic S-1, via Fox Business"); return img

def twee_lijnen(t, d, T0):                                   # zin 50-53
    img = foto("pentagon", t, d, (1.0, 1.06), donker=0.3).filter(ImageFilter.GaussianBlur(4)); dr = ImageDraw.Draw(img, "RGBA")
    if not na(79, T0, t):
        onder(img, t, "The Pentagon wanted Claude with fewer limits", 0.2); return img
    txt(dr, (W // 2, 300), "Anthropic's two red lines", font(BLACK, 80), WIT, ease(sinds(79, T0, t) / 0.4), "mm")
    for k, (z, s) in enumerate([(80, "No mass surveillance of Americans"), (81, "No fully autonomous weapons")]):
        if na(z, T0, t):
            a = ease(sinds(z, T0, t) / 0.4); y = 470 + k * 150
            dr.rectangle([360, y - 50, 1560, y + 50], fill=ROOD + (int(200 * a),)); txt(dr, (W // 2, y), s, font(BOLD, 56), WIT, a, "mm")
    return img

def eind_staart(t, d, T0):
    img = foto("sf", t, d, (1.0, 1.1), donker=0.45, grijs=True)
    onder(img, t, "From a handful of researchers to Wall Street", 0.3)
    if t > d - 1.8: img = Image.blend(img, Image.new("RGB", (W, HH)), min(1, (t - (d - 1.8)) / 1.8))
    return img

SLOTKOERS = json.load(open(H / "data/slot.json")) if (H / "data/slot.json").exists() else None

SHOTS = [
 (0.0, doc("Anthropic, PBC · Form S-1 · SEC", "Registration statement for an initial public offering",
           ["Filed publicly: October 26, 2026", "Proposed Nasdaq symbol: ANT", "Risk factors"], mark=2, achter="nasdaq-c", mark_na=1)),
 (ZR(1, 0.35), fasen(lambda t, d: raster(leeg()), [(1, EN(lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 360), "RISK FACTORS", font(BOLD, 44), ORANJE, ease(t / 0.3), "mm"),
                                                      lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 500), "“end of humanity”", font(ITAL, 120), WIT, ease((t - 0.3) / 0.5), "mm"),
                                                      lambda img, t: bron(img, "Anthropic IPO filing, as reported by Fox Business")))])),
 (ZR(2) - 0.15, fasen(F("nasdaq-c", (1.0, 1.1), 0.45), [(2, GR("$81 BILLION", "asked from investors", WIT, 170)), (3, GR("$81 BILLION", "They got it", GROEN, 170))])),
 (ZR(4) - 0.15, fasen(F("nasdaq-a", (1.0, 1.12), 0.7), [(4, EN(ST("NOVEMBER 19, 2026 · 11:48 AM"), LT("ANTHROPIC · NASDAQ: ANT", "First day of trading")))])),
 (ZR(5) - 0.15, prijs),
 (ZR(7) - 0.15, fasen(F("nasdaq-a", (1.0, 1.08), 0.4), [(7, GR("THE BIGGEST IPO", "in history", WIT, 140))])),
 (ZR(8) - 0.15, balken([("Facebook · 2012", 16.0), ("Alibaba · 2014", 25.0), ("Saudi Aramco · 2019", 29.4), ("SpaceX · 2026", 75.0), ("Anthropic · 2026", 81.3)],
                       "THE BIGGEST IPOs EVER", "Money raised in the offering, billions of dollars", "Sources: Fox Business, Reuters", lambda v: f"${v:.1f}B", [8, 9, 10, 11, 11], hl=4)),
 (ZR(12) - 0.15, fot("openai", "2021: a handful of researchers walk out of OpenAI", donker=0.6)),
 (ZR(13) - 0.15, fasen(F("sf", (1.0, 1.08), 0.45), [(13, GR("~$1.5 TRILLION", "Worth, fully diluted, at the IPO", WIT, 150)), (14, GR("What did investors buy?", None, WIT, 100))])),
 (ZR(15) - 0.15, fot("sf-b", stamp="SAN FRANCISCO, 2021", donker=0.6)),
 (ZR(16) - 0.15, fasen(F("dario-a", (1.0, 1.1), 0.75, pan=(0.45, 0.4, 0.45, 0.38)), [(16, LT("DARIO AMODEI", "Research leader at OpenAI, then co-founder and CEO of Anthropic")),
                                                                          (19, ON("With his sister Daniela and a small group of colleagues"))])),
 (ZR(20) - 0.15, fasen(F("dario-e", (1.05, 1.15), 0.4, grijs=True), [(20, GR("Maybe too fast.", None, WIT, 120))])),
 (ZR(21) - 0.15, fasen(F("openai", (1.08, 1.0), 0.55), [(21, ON("A disagreement about safety")), (22, ON("So they left, and started their own company"))])),
 (ZR(23) - 0.15, fasen(lambda t, d: logo_kaart("sf-b")(t, d, 0),
                      [(24, lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 660), "PUBLIC BENEFIT CORPORATION", font(BLACK, 90), ORANJE, ease(t / 0.4), "mm")),
                       (25, EN(lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 660), "PUBLIC BENEFIT CORPORATION", font(BLACK, 90), ORANJE, 1, "mm"),
                               lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 760), "On paper: the good of society, not just profit", font(REG, 44), GRIJS, ease(t / 0.4), "mm")))])),
 (ZR(26) - 0.15, fasen(F("sf", (1.08, 1.0), 0.35), [(26, GR("$124 MILLION", "First big funding round, May 2021", WIT, 150)), (27, GR("$124 MILLION", "For an AI lab, almost nothing", GRIJS, 150))])),
 (ZR(28) - 0.15, doc("arXiv · Anthropic research", "Constitutional AI: Harmlessness from AI Feedback",
                     ["Published December 15, 2022", "Trained to follow a written list of principles"], mark=1, achter="code", mark_na=30)),
 (ZR(32) - 0.15, doc("Anthropic · September 19, 2023", "Responsible Scaling Policy",
                     ["Rules for building more powerful AI", "More powerful AI: stricter safety rules"], mark=1, achter="dc-a", mark_na=35)),
 (ZR(36) - 0.15, fasen(F("sf", (1.0, 1.08), 0.4), [(36, GR("Marketing?", None, WIT, 130)), (37, GR("Or a real plan?", "for the whole AI industry", ORANJE, 120))])),
 (ZR(38) - 0.15, fot("sf-b", "Two quiet years", donker=0.55, zoom=(1.1, 1.0))),
 (ZR(39) - 0.15, logo_kaart("code", "CLAUDE", "Released in March 2023", "MARCH 2023")),
 (ZR(40) - 0.15, fasen(F("code", (1.0, 1.1), 0.45), [(40, ON("Built to compete directly with ChatGPT")), (41, ON("It was not the first")), (42, ON("ChatGPT launched just months earlier, in November 2022"))])),
 (ZR(43) - 0.15, duo),
 (ZR(48) - 0.15, fasen(lambda t, d: logo_kaart("dc-baltic")(t, d, 0), [(48, lambda img, t: None), (49, lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 660), "CLAUDE 3 · MARCH 2024", font(BLACK, 80), ORANJE, ease(t / 0.4), "mm")),
                                                                          (50, lambda img, t: txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 660), "CLAUDE 4.5 · SEPTEMBER 2025", font(BLACK, 80), ORANJE, ease(t / 0.4), "mm")),
                                                                          (51, ON("Smarter, and more expensive to build"))])),
 (ZR(52) - 0.15, balken([("Mar 2025", 61.5), ("Sep 2025", 183), ("Feb 2026", 380), ("May 2026", 965)],
                        "WHAT ANTHROPIC WAS WORTH", "Valuation in private funding rounds, billions of dollars", "Source: Reuters", lambda v: f"${v:,.0f}B" if v >= 100 else f"${v:.1f}B", [53, 54, 55, 56])),
 (ZR(57) - 0.15, fasen(F("code", (1.1, 1.0), 0.35), [(57, GR("The reason was simple.", None, WIT, 100)), (58, GR("Businesses were paying.", None, ORANJE, 100))])),
 (ZR(59) - 0.15, balken([("All of 2025", 4.585), ("First 9 months of 2026", 33.2)], "ANTHROPIC REVENUE", "Billions of dollars", "Sources: Anthropic S-1, Fox Business",
                        lambda v: f"${v:.1f}B", [59, 60], extra=lambda img, t, T0: txt(ImageDraw.Draw(img, "RGBA"), (760, 420), "+1,206%", font(BLACK, 110), GROEN, ease(sinds(61, T0, t) / 0.4) if na(61, T0, t) else 0, "rm"))),
 (ZR(62) - 0.15, fasen(F("dc-baltic", (1.0, 1.1), 0.35), [(62, GR("$65 BILLION+", "Yearly revenue pace by the end of July 2026 · Reuters", WIT, 150))])),
 (ZR(63) - 0.15, fasen(F("code", (1.0, 1.08), 0.5), [(63, ON("Not from people chatting for fun")), (64, ON("Companies paying to use Claude inside their own products"))])),
 (ZR(65) - 0.15, lambda t, d, T0: regels(foto("dc-a", t, d, (1.0, 1.08), donker=0.35), sinds(65, T0, t),
                                         ["It adds up."] if na(68, T0, t) else ["Every question.", "Every line of code.", "Every answer costs a little."][:1 + na(66, T0, t) + na(67, T0, t)], stap=0)),
 (ZR(69) - 0.15, logo_kaart("code", "CLAUDE CODE", "Released February 2025", "FEBRUARY 2025")),
 (ZR(71) - 0.15, fasen(F("code", (1.08, 1.18), 0.5), [(71, ON("Give Claude a task: it writes, tests and fixes the code")),
                                                     (72, GR("$1 BILLION", "a year, within six months · reported", WIT, 150)),
                                                     (73, GR("$2.5 BILLION+", "a year by early 2026 · reported", ORANJE, 150)),
                                                     (74, ON("No longer a chatbot")), (75, ON("A coworker"))])),
 (ZR(76) - 0.15, fasen(F("pentagon", (1.0, 1.1), 0.65), [(76, ST("FEBRUARY 2026")), (77, EN(ST("FEBRUARY 2026"), ON("The United States government")))])),
 (ZR(78) - 0.15, twee_lijnen),
 (ZR(82) - 0.15, fasen(portret("trump"), [(82, ON("The response was fast")),
                                                                                (83, LT("DONALD TRUMP", "Directs the government to stop working with Anthropic"))])),
 (ZR(84) - 0.15, fot("pentagon", stamp="LABELED A SUPPLY CHAIN RISK", kleur=ROOD, zoom=(1.08, 1.18), donker=0.55)),
 (ZR(85) - 0.15, fasen(F("burton", (1.0, 1.08), 0.6), [(85, ST("MARCH 2026: ANTHROPIC SUES")), (86, EN(ST("MARCH 2026: ANTHROPIC SUES"), ON("A federal judge in San Francisco blocks the label")))])),
 (ZR(87) - 0.15, fot("prettyman", "Appeals court in Washington sides with the Pentagon, 2 to 1", stamp="SEPTEMBER 2026", kleur=ROOD, donker=0.6)),
 (ZR(88) - 0.15, fot("supreme", "Anthropic: it could take the case to the Supreme Court", donker=0.6)),
 (ZR(89) - 0.15, fasen(F("pentagon", (1.1, 1.2), 0.35, grijs=True), [(89, GR("For most startups: the end.", None, WIT, 90)),
                                                                     (90, GR("$380B  →  $965B", "Anthropic's value, February to May 2026", GROEN, 137))])),
 (ZR(91) - 0.15, logo_kaart("dc-baltic", "MYTHOS", "Its most advanced AI model so far", "APRIL 2026")),
 (ZR(93) - 0.15, fasen(F("code", (1.08, 1.18), 0.45, pan=(0.6, 0.5, 0.5, 0.5)), [(93, ON("So good at finding weaknesses in software, it was not released to everyone")),
                                                                                   (94, ON("A small group of organizations: find and fix security holes")),
                                                                                   (95, ST("PROJECT GLASSWING"))])),
 (ZR(96) - 0.15, fasen(F("boeken", (1.0, 1.08), 0.55), [(96, ON("There were other problems too")), (97, ON("Authors: our books were used to train Claude without permission")),
                                                         (98, GR("$1.5 BILLION", "Settlement with authors, approved by a judge", WIT, 150))])),
 (ZR(99) - 0.15, doc("Anthropic, PBC · SEC filings", "The road to Wall Street",
                     ["June 2026: confidential IPO filing", "October 26, 2026: public S-1 filing", "For the first time, the numbers are public"], mark=2, achter="nasdaq-a", mark_na=101)),
 (ZR(102) - 0.15, verlies),
 (ZR(107) - 0.15, fasen(F("dc-us", (1.0, 1.08), 0.3), [(107, GR("The real number to watch", None, WIT, 90)),
                                                       (108, GR("~$900 BILLION", "Promised for computing power, in deals stretching to 2045", ORANJE, 160)),
                                                       (109, GR("$70.7 BILLION", "Due within 12 months of September 30, 2026", ROOD, 160))])),
 (ZR(110) - 0.15, fasen(F("nasdaq-a", (1.08, 1.0), 0.45), [(110, GR("Investors did not seem worried.", None, WIT, 90))])),
 (ZR(111) - 0.15, range_kaart),
 (ZR(115) - 0.15, fasen(F("nasdaq-c", (1.0, 1.1), 0.45), [(115, GR("Thursday", "November 19, 2026", WIT, 140))])),
 (ZR(116) - 0.15, intraday),
 (ZR(119) - 0.15, macht),
 (ZR(123) - 0.15, lijst("wallst", "What happens next", [(125, "~315 million insider shares: can sell from day one"), (126, "Founders: locked in for up to a year"),
                                                      (127, "The Pentagon fight: not over"), (128, "Computing bills: ~$900 billion")])),
 (ZR(129) - 0.15, fot("openai", "OpenAI: also expected to go public", donker=0.6)),
 (ZR(130) - 0.15, fot("google", naamkaart=("GOOGLE", "Alphabet"), donker=0.65)),
 (ZR(131) - 0.15, fot("meta-hq", naamkaart=("META", "Facebook, Instagram, WhatsApp"), donker=0.65)),
 (ZR(132) - 0.15, fasen(F("dc-baltic", (1.0, 1.1), 0.4), [(132, ON("And many others")), (133, GR("HUNDREDS OF BILLIONS", "spent on AI by the biggest tech companies", WIT, 120))])),
 (ZR(134) - 0.15, fot("dc-a", "The race is far from finished", donker=0.55, zoom=(1.1, 1.0))),
 (ZR(135) - 0.15, fasen(F("nasdaq-c", (1.0, 1.08), 0.4), [(135, ON("The question is not whether Anthropic matters")),
                                                        (136, GR("This much, this early?", None, WIT, 100)),
                                                        (137, GR("$190–200 BILLION", "Anthropic's expected revenue in 2028 · Reuters", ORANJE, 140)),
                                                        (138, ON("If it happens: today's price may look cheap")), (139, ON("If not: a historic fall"))])),
 (ZR(140) - 0.15, fot("sf-b", "2021: worried about how fast AI was moving", grijs=True, donker=0.55)),
 (ZR(141) - 0.15, eind_staart),
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
        if k != vorige and vorige is not None: wissel = i
        if 0 <= i - wissel < 6 and oud is not None: img = Image.blend(oud, img, (i - wissel + 1) / 7)
        else: oud = img
        vorige = k; p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit.name)

if __name__ == "__main__":
    main()
