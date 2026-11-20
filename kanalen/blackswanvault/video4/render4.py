"""BlackSwanVault video 4 (de markt valt). Zelfde stijl als video 3 (render3.py). Gebruik: python render4.py [--van s --tot s | --plaat uit.jpg]"""
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

ORANJE = (245, 158, 11)                                    # accentkleur video 4 (amber)
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



# ---------- koersen (Yahoo, data/*.json) ----------
import datetime as _D
def reeks(naam):
    k = json.load(open(H / f"data/{naam}.json"))["chart"]["result"][0]
    return [(_D.datetime.fromtimestamp(a, _D.UTC).date(), v) for a, v in zip(k["timestamp"], k["indicators"]["quote"][0]["close"]) if v]
_REEKS = {}
def koersgrafiek(naam, van, tot, titel, sub, bron_s, markers=(), labels=(), teken=0.75, kleur=ROOD, eind_label=True, eenheid="", log=False):
    """labels = [(datum, x, y, tekst, kleur)]: verschijnt pas als de lijn bij die datum is (vaste regel eigenaar 20 nov)."""
    assert all(isinstance(l[0], str) for l in labels), "koerslabel moet een datum zijn, geen zinnummer"
    if naam not in _REEKS: _REEKS[naam] = reeks(naam)
    def f(t, d, T0):
        R.KOERS[:] = _REEKS[naam]
        img, _ = lijn(t, d, van, tot, titel, sub, markers=markers, kleur=kleur, teken=teken, eind_label=eind_label, eenheid=eenheid, log=log)
        dr = ImageDraw.Draw(img, "RGBA"); pts = R.koers(van, tot)
        n = max(2, int(len(pts) * eio(t / (d * teken))))
        for z, x, y, s, k in labels:
            i = next((q for q, (dd, _) in enumerate(pts) if str(dd) >= z), len(pts) - 1)
            if n > i: txt(dr, (x, y), s, font(BLACK, 120), k, ease((n - i) / 6), "rm")
        bron(img, bron_s); return img
    return f
YB = "Source: Yahoo Finance, daily closing prices"

PCT = lambda v: f"-{v:.1f}%"
PROC = lambda v: f"{v:.0f}%"
SHOTS = [
 # --- opening (proef goedgekeurd 20 nov) ---
 (0.0, fasen(F("nasdaq-b", (1.0, 1.1), 0.55), [(0, ST("NOVEMBER 19, 2026")), (1, GR("+17%", "Anthropic's first day, vs its offering price", GROEN, 170))])),
 (ZR(2) - 0.15, fasen(F("ai-feest-beurs", (1.08, 1.0), 0.5), [(2, ON("It was supposed to be a celebration")), (3, GR("THEN THE MARKET FELL", None, ROOD, 110))])),
 (ZR(4) - 0.15, lijst("wallst", "Thursday, November 19", [(4, "S&P 500: -2%"), (5, "Nasdaq: -2.25%"), (6, "Dow: below 50,000, first time since June")])),
 (ZR(7) - 0.15, koersgrafiek("nasdaq", "2026-09-01", "2026-11-19", "NASDAQ COMPOSITE", "Daily close, September to November 2026", YB,
                             markers=[("2026-10-06", "Peak")], labels=[("2026-11-18", 1700, 330, "-13.5%", ROOD)], teken=0.8, eind_label=False)),
 (ZR(8) - 0.15, fasen(F("nasdaq-a", (1.0, 1.08), 0.35), [(8, GR("-10%", None, WIT, 190)), (9, GR("CORRECTION", "a fall of 10% from the peak", ORANJE, 150)),
                                                       (10, GR("-20%", None, WIT, 190)), (11, GR("BEAR MARKET", "a fall of 20% from the peak", ROOD, 150))])),
 (ZR(12) - 0.15, fasen(F("ai-trader-rood", (1.0, 1.08), 0.5), [(12, GR("What are investors afraid of?", None, WIT, 90)), (14, GR("4 FEARS", None, ORANJE, 190))])),
 (ZR(15) - 0.15, koersgrafiek("sp500", "2026-11-03", "2026-11-19", "S&P 500", "Daily close, November 3 to 19, 2026", YB,
                              labels=[("2026-11-19", 1700, 330, "6 DAYS DOWN", ROOD)], teken=0.85)),
 (ZR(17) - 0.15, balken([("Dow Jones", 6.2), ("S&P 500", 5.0), ("Nasdaq", 5.0)], "THIS WEEK, MONDAY TO THURSDAY", "Percent lost", "Source: CNBC", PCT, [17, 18, 18], kleur=ROOD)),
 (ZR(19) - 0.15, lijst("ai-tokyo-nacht", "Friday in Asia", [(20, "Nikkei: -5.06%"), (21, "Kospi: -5.21%"), (22, "Samsung: -7%")])),
 # --- h1: chips, SoftBank, nergens veilig, VIX ---
 (ZR(23) - 0.15, fasen(F("ai-chipfabriek", (1.0, 1.08), 0.5), [(23, ON("Chip companies were hit the hardest")), (24, GR("-7%", "Tokyo Electron", ROOD, 170)), (25, GR("-9%", "Lasertec", ROOD, 170))])),
 (ZR(26) - 0.15, fasen(F("tsmc", (1.0, 1.08), 0.55), [(26, EN(LT("TSMC", "Makes most of the world's advanced chips"), ST("-4.8%", ROOD)))])),
 (ZR(27) - 0.15, fasen(portret("son"), [(27, LT("MASAYOSHI SON", "Founder of SoftBank · $64.6 billion invested in OpenAI")),
                                       (28, GR("-14.5%", "SoftBank, worst day since August 2024", ROOD, 170))])),
 (ZR(29) - 0.15, fasen(F("wallst", (1.08, 1.0), 0.5), [(29, ON("Usually, investors run to safety")), (30, GR("NOWHERE TO RUN", None, ROOD, 120))])),
 (ZR(31) - 0.15, balken([("Gold", 11.4), ("Bitcoin", 24.4)], "THE PAST MONTH", "Percent lost, October 19 to November 19", YB, PCT, [31, 32], kleur=ROOD)),
 (ZR(33) - 0.15, fasen(F("ai-goud", (1.0, 1.08), 0.55), [(33, ON("One reason for gold is simple")), (34, GR("NO INTEREST", "gold pays nothing while you hold it", WIT, 130)),
                                                       (35, ON("Higher rates make holding gold less attractive"))])),
 (ZR(36) - 0.15, koersgrafiek("vix", "2026-08-20", "2026-11-19", "VIX, WALL STREET'S FEAR GAUGE", "Expected swings of the S&P 500 over the next 30 days", YB,
                              markers=[("2026-10-19", "A month ago: 18")], labels=[("2026-11-18", 1700, 330, "28", ROOD)], teken=0.8, eind_label=False)),
 # --- h2: angst 1, AI ---
 (ZR(40) - 0.15, fasen(F("ai-ai-chip", (1.0, 1.08), 0.5), [(40, GR("FEAR 1", "Doubts about AI", ORANJE, 160)), (41, ON("For three years, AI carried the stock market")),
                                                         (42, ON("Now investors are starting to doubt it"))])),
 (ZR(43) - 0.15, balken([("Amazon", 3.9), ("Alphabet", 3.5), ("Meta", 3.3)], "THURSDAY, NOVEMBER 19", "Percent lost in one day", YB, PCT, [43, 44, 44], kleur=ROOD)),
 (ZR(45) - 0.15, koersgrafiek("nvda", "2026-11-03", "2026-11-19", "NVIDIA STOCK", "Daily close, November 3 to 19, 2026", YB,
                              labels=[("2026-11-18", 1700, 330, "-16%", ROOD)], teken=0.75, eenheid="$")),
 (ZR(47) - 0.15, fasen(F("nasdaq-c", (1.0, 1.08), 0.4), [(47, GR("~$670 BILLION", "in market value, gone in 6 trading days", ROOD, 140))])),
 (ZR(48) - 0.15, koersgrafiek("nvda", "2026-07-01", "2026-11-19", "NVIDIA STOCK", "Daily close, July to November 2026", YB,
                              markers=[("2026-10-06", "Peak")], labels=[("2026-11-18", 1700, 330, "-39%", ROOD)], teken=0.75, eenheid="$", eind_label=False)),
 (ZR(49) - 0.15, fasen(F("huang-g", (1.0, 1.06), 0.6), [(49, LT("JENSEN HUANG", "Co-founder, stepped down as CEO on November 12")), (51, ON("The selling did not stop with him"))])),
 (ZR(52) - 0.15, fasen(F("amd-hq", (1.0, 1.08), 0.55), [(52, EN(LT("AMD", "Santa Clara, California"), ST("NOVEMBER 19"))),
                                                      (53, ON("Hunterbrook: AMD tech kept reaching a blacklisted Chinese firm"))])),
 (ZR(54) - 0.15, fasen(F("ai-short-rapport", (1.0, 1.08), 0.55), [(54, ON("A short seller makes money when a stock falls")), (55, ON("So a report like this is never neutral")),
                                                                (56, ON("Claim: AMD bills more than 20% of its revenue to China and Hong Kong"))])),
 (ZR(57) - 0.15, fasen(F("amd-hq", (1.1, 1.0), 0.45), [(57, ON('AMD: the claims "misrepresent" its business')), (58, GR("-7.7%", "AMD, November 19", ROOD, 170))])),
 (ZR(59) - 0.15, balken([("Q2 2026", 75), ("Q3 2026", 48)], "OPENAI + ANTHROPIC: REVENUE GROWTH", "Combined, as cited by CNBC", "Source: CNBC", PROC, [60, 60], kleur=ORANJE)),
 (ZR(61) - 0.15, fasen(F("dc-a", (1.0, 1.08), 0.45), [(61, GR("~$8.4 BILLION", "combined losses in the third quarter, up from $7.9 billion", ROOD, 140)),
                                                     (62, ON("The whole AI boom rests on one bet")), (63, ON("That chips and data centers will one day pay for themselves"))])),
 (ZR(64) - 0.15, fasen(F("ai-datacenter", (1.0, 1.08), 0.5), [(64, ON("AI data centers, built with borrowed money")), (65, EN(LT("COREWEAVE", "AI data center company"), ST("-6%", ROOD)))])),
 (ZR(66) - 0.15, balken([("Spring 2026", 50), ("Fall 2026", 87)], "AI NAMED AS A MAJOR RISK", "Market experts surveyed for the Fed's financial stability report",
                        "Source: Federal Reserve, via CNBC", PROC, [68, 67], hl=1, kleur=ROOD)),
 (ZR(69) - 0.15, fasen(F("fed", (1.0, 1.08), 0.5), [(69, ON("Hedge funds are borrowing to invest more than at any time since 2013"))])),
 # --- h3: angst 2, inflatie ---
 (ZR(70) - 0.15, fasen(F("ai-supermarkt", (1.0, 1.08), 0.5), [(70, GR("FEAR 2", "Inflation", ORANJE, 160)), (71, ON("Inflation is coming back")),
                                                            (72, GR("+0.4%", "US consumer prices, October, in one month", WIT, 170))])),
 (ZR(73) - 0.15, balken([("Expected", 0.3), ("Actual", 0.4), ("Core, expected", 0.2), ("Core, actual", 0.3)],
                        "US CONSUMER PRICES, OCTOBER", "Change in one month. Core = without food and energy", "Source: Bureau of Labor Statistics, via CNBC", lambda v: f"+{v:.1f}%", [73, 73, 74, 74], kleur=ORANJE)),
 (ZR(76) - 0.15, fasen(F("ai-fabriek-goederen", (1.0, 1.08), 0.5), [(76, ON("Prices that companies pay rose even faster")),
                                                                  (77, ON("Wholesale prices: what businesses pay before goods reach the shelves")), (78, ON("When they rise, shop prices often follow"))])),
 (ZR(79) - 0.15, fasen(F("ai-fabriek-goederen", (1.12, 1.04), 0.35, pan=(0.3, 0.6, 0.4, 0.5)), [(79, GR("6.5%", "US wholesale prices, past year", WIT, 190)),
                                                                  (80, GR("6.5%", "highest since November 2022", WIT, 190)), (81, GR("10%+", "for goods alone", ROOD, 190))])),
 (ZR(82) - 0.15, fasen(F("ai-diesel", (1.0, 1.08), 0.5), [(82, ON("And it is not just America")), (83, GR("3.6%", "UK inflation, highest in a year, record diesel prices", WIT, 170))])),
 (ZR(84) - 0.15, fasen(F("boe", (1.0, 1.08), 0.55), [(84, LT("BANK OF ENGLAND", "Expects UK inflation of about 5% by mid-2027"))])),
 # --- h4: angst 3, rente ---
 (ZR(85) - 0.15, fasen(F("fed", (1.08, 1.0), 0.45), [(85, GR("FEAR 3", "Interest rates", ORANJE, 160)), (86, ON("Interest rates may go up, not down"))])),
 (ZR(87) - 0.15, doc("CNBC, November 17, 2026", "Alberto Musalem, President of the Federal Reserve Bank of St. Louis",
                     ["\"The economy will likely require", "several interest rate increases", "before the spring of 2027.\"", "", "Up to four hikes may be needed."], mark=1, achter="fed", mark_na=87)),
 (ZR(89) - 0.15, fasen(F("capitol", (1.0, 1.08), 0.45), [(89, GR("3.75% to 4%", "the Fed's key rate", WIT, 140)), (90, ON("Unchanged in October")),
                                                       (91, GR("+0.25%", "fully expected at the Fed meeting, December 8 and 9", ORANJE, 160))])),
 (ZR(92) - 0.15, fasen(F("boe", (1.1, 1.0), 0.4, pan=(0.6, 0.5, 0.4, 0.5)), [(92, ON("In Britain, the Bank of England already did it")),
                                                       (93, GR("4%", "Bank of England rate, since November 5", WIT, 190)), (94, ON("Its first increase since August 2023")),
                                                       (95, GR("8 TO 1", "the vote; one member wanted an even bigger hike", WIT, 160))])),
 (ZR(97) - 0.15, fasen(F("ai-spaargeld", (1.0, 1.08), 0.5), [(97, GR("Why does this hurt tech?", None, WIT, 100)), (98, ON("Tech stocks are valued on profits years from now")),
                                                          (99, ON("Higher rates make future money worth less today")), (100, ON("And safe savings start to pay more"))])),
 (ZR(101) - 0.15, fasen(F("nasdaq-c", (1.1, 1.0), 0.45), [(101, ON("Investors pay less for a promise")), (102, ON("That's why the Nasdaq usually falls harder than the Dow"))])),
 # --- h5: angst 4, chips en China ---
 (ZR(103) - 0.15, fasen(F("commerce", (1.0, 1.08), 0.5), [(103, GR("FEAR 4", "Chips and China", ORANJE, 160)), (104, ON("AI chips going to China")),
                                                        (105, EN(LT("U.S. DEPARTMENT OF COMMERCE", "Approved sales of 879,000+ AI chips to Chinese companies"), ST("HOUSE FOREIGN AFFAIRS DOCUMENTS")))])),
 (ZR(106) - 0.15, fasen(portret("bessent"), [(106, EN(LT("SCOTT BESSENT", "U.S. Treasury Secretary"), ON('"A lot of leakage in the system"'))),
                                            (107, ON("Others wanted Megaspeed on a trade blacklist for months"))])),
 (ZR(108) - 0.15, fasen(portret("bonta"), [(108, LT("ROB BONTA", "California Attorney General · subpoena to Nvidia")), (109, ON("Did Nvidia chips reach China? Were investors misled?")),
                                          (110, ON('"Bright red flags"'))])),
 # --- h6: geschiedenis ---
 (ZR(111) - 0.15, fasen(F("ai-trader-rood", (1.1, 1.0), 0.4), [(111, GR("The start of something worse?", None, WIT, 90)), (112, GR("NOBODY KNOWS", None, ORANJE, 130)),
                                                             (113, ON("But history can tell us something"))])),
 (ZR(114) - 0.15, koersgrafiek("nasdaq-hist", "1971-01-01", "2026-11-19", "NASDAQ COMPOSITE SINCE 1971", "Weekly close, log scale", YB, teken=0.6, log=True, kleur=ORANJE, eind_label=False)),
 (ZR(115) - 0.15, balken([("Corrections of 10% or more", 31), ("Became a fall of 20% or more", 13), ("Recovered before that", 18)], "NASDAQ CORRECTIONS SINCE 1971",
                         "Our count, based on closing prices", "Source: Yahoo Finance, own calculation", lambda v: f"{v:.0f}", [115, 116, 117], hl=1, kleur=ROOD)),
 (ZR(118) - 0.15, lijst("nasdaq-a", "How the Nasdaq recovered", [(119, "Spring 2026: -13%, a record by mid-April"), (120, "2020: -30%, recovered within months"),
                                                              (121, "2024: -13%, a record by the end of October"), (123, "2022: -36%, more than two years")])),
 # --- h7: wat nu ---
 (ZR(124) - 0.15, lijst("ai-blackfriday", "What to watch now", [(125, "The Fed meeting: December 8 and 9"), (126, "The next inflation numbers"),
                                                              (127, "Black Friday: November 27"), (129, "Senate hearings on AI chips")])),
 (ZR(130) - 0.15, slot_fade("nasdaq-b", "Stocks can also go down")),
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
        if 0 <= i - wissel < 18 and oud is not None: img = Image.blend(oud, img, eio((i - wissel + 1) / 19))   # 20 nov: rustiger overgang (eigenaar: niet te snel, te druk)
        else: oud = img
        vorige = k; p.stdin.write(img.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit.name)

if __name__ == "__main__":
    main()
