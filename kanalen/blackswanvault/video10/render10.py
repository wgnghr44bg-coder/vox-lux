"""BlackSwanVault video 10 (Nvidia, Huang weg en terug). Zelfde stijl als video 9. Gebruik: python render10.py [--van s --tot s | --plaat uit.jpg]"""
import json, sys, datetime as DT
import render as R
from render import *   # noqa: F401,F403

Z = R.Z
def ZR(i, f=0.0):
    k = int(i); f += i - k                                 # 20 nov: 49.5 = halverwege zin 49
    return Z[k][0] + f * (Z[k][1] - Z[k][0])
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

ORANJE = (245, 158, 11)                                    # accentkleur (amber)
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
                dr.rectangle([x, Y0 - max(h, 6), x + bw, Y0], fill=k + (255,))   # 20 nov: negatieve waarde = dun streepje
                txt(dr, (x + bw / 2, Y0 - max(h, 6) - 14), fmt(v * p), font(BOLD, 40), WIT, min(1, p * 2), "ms")
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

# ---------- video 10 v2 (record-opening): Jensen Huang weg en terug (zinnummers = script.txt, zie bronnen.md) ----------
NV = lambda van, tot, titel, sub, **k: koersgrafiek("nvda", van, tot, titel, sub, YB, eenheid="$", **k)
SHOTS = [
 # --- opening ---
 (0.0, fasen(portret("huang-g"), [(0, GR("HE'S BACK", None, GROEN, 190)), (1, EN(ST("11 DAYS LATER"), LT("JENSEN HUANG", "Nvidia founder · CEO again")))])),
 (ZR(2) - 0.15, fasen(F("ces2025", (1.0, 1.08), 0.5), [(2, ON("Investors loved it")), (3, GR("~$1 TRILLION", "Nvidia market value added, Monday, November 23, 2026", GROEN, 160)),
                                                     (4, GR("RECORD", "biggest one-day gain ever (our calculation)", ORANJE, 190))])),
 (ZR(5) - 0.15, lijst("ai-beurs-rood", "How did it happen?", [(7, "Huang admitted an affair"), (8, "Reports: ties to Chinese intelligence"),
                                                          (9, "He resigned. The stock kept falling"), (10, "The White House stepped in")])),
 (ZR(11) - 0.15, fasen(F("hq-entry", (1.0, 1.08), 0.5), [(11, ON("How big was that day?"))])),
 # --- h1 het record ---
 (ZR(12) - 0.15, balken([("Nvidia, Apr 2025", 440), ("Microsoft, Jul 2026", 450), ("Nvidia, Aug 2026", 442), ("Nvidia, Nov 23, 2026", 960)],
                        "BIGGEST ONE-DAY GAINS IN MARKET VALUE", "Billions of dollars, approximate",
                        "Sources: Al Jazeera, Bloomberg Línea, Crypto Briefing; Nov 23: Yahoo Finance close x shares (our calculation)",
                        lambda v: f"${v:,.0f}B", [13, 14, 15, 16], hl=3, kleur=GROEN)),
 (ZR(17) - 0.15, fasen(F("hq-wall", (1.0, 1.08), 0.45), [(17, ON("But this was not a normal good day")), (18, ON("A rebound from one of the worst crashes in Nvidia's history")),
                                                       (19, EN(ST("SINCE 1993"), ON("It was all about one man")))])),
 (ZR(20) - 0.15, fasen(F("huang-c", (1.0, 1.08), 0.6), [(20, GR("30+ YEARS", "the only CEO Nvidia ever had", WIT, 160)), (21, ON("The face of the company: every new chip, on stage")),
                                                       (22, ON("To investors: Nvidia = Jensen Huang")), (23, ON("That is why the next weeks were so dangerous"))])),
 # --- h2 de val ---
 (ZR(24) - 0.15, fasen(F("ai-memo", (1.0, 1.08), 0.55), [(24, EN(ST("NOVEMBER 8"), ON("A note to Nvidia employees"))), (25, ON("He admitted an extramarital affair")),
                                                        (26, ON('"There is no excuse for what I did."'))])),
 (ZR(27) - 0.15, fasen(F("ai-spion", (1.0, 1.08), 0.55), [(27, ON("Then the story got much bigger")), (28, ON("Reports: the woman was suspected of ties to Chinese intelligence")),
                                                         (29, GR("NATIONAL SECURITY", None, ROOD, 120)), (30, GR("ALLEGATION", "not proven", WIT, 150)),
                                                         (31, ON("Huang admitted the affair, nothing else"))])),
 (ZR(32) - 0.15, fasen(F("nyt", (1.0, 1.08), 0.45), [(32, EN(ST("NOVEMBER 22"), LT("THE NEW YORK TIMES", "reported more details"))),
                                                    (33, ON("Contact with an officer of China's Ministry of State Security, it reported"))])),
 (ZR(34) - 0.15, doc("Nvidia filing with the SEC, November 12, 2026", "NVIDIA Announces CEO Transition",
                     ["Jensen Huang has resigned as President,", "Chief Executive Officer, and a member", "of the Board, effective immediately.", "",
                      "No reason given."], mark=4, achter="hq-hq", mark_na=36)),
 (ZR(37) - 0.15, fasen(portret("kress"), [(37, LT("COLETTE KRESS", "Interim CEO · Nvidia finance chief since 2013")),
                                         (39, ON("Harvey Jones: the first chairman in Nvidia's history"))])),
 (ZR(40) - 0.15, NV("2026-11-02", "2026-11-12", "NVIDIA (NVDA)", "Daily close in US dollars, November 2 to 12, 2026",
                    labels=[("2026-11-09", 1000, 330, "-4%", ROOD), ("2026-11-10", 1350, 330, "-6%", ROOD)], teken=0.85, eind_label=False)),
 (ZR(43) - 0.15, fasen(F("hq-hq", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(43, GR("-14%", "intraday, November 12", ROOD, 200)), (44, ON("And it kept sliding, day after day"))])),
 # --- h3 het nee ---
 (ZR(45) - 0.15, fasen(F("ai-boardroom", (1.0, 1.08), 0.55), [(45, ON("Many investors hoped he would come back")), (46, EN(ST("NOVEMBER 17"), ON("The board gave its answer"))),
                                                             (47, ON('Harvey Jones: the board "does not intend to reinstate Jensen as CEO"')), (48, ON("Colette Kress said the same to CNBC"))])),
 (ZR(49) - 0.15, fasen(F("ai-rapport", (1.0, 1.08), 0.5), [(49, ON("Then came more bad news")), (50, LT("SEC INVESTIGATION", "reported by The Wall Street Journal and Reuters")),
                                                          (51, ON("The SEC declined to comment"))])),
 (ZR(52) - 0.15, fasen(F("ai-trader-rood", (1.0, 1.08), 0.5), [(52, EN(ST("FRIDAY, NOVEMBER 20"), ON("The whole tech sector was selling off"))), (53, GR("-14%", "Nvidia in one day", ROOD, 200)),
                                                              (54, GR("$125.53", "closing price", WIT, 180)), (55, ON("Same day: Nasdaq 100 -5.6%")), (56, ON("Longest weekly losing streak since 2008"))])),
 (ZR(57) - 0.15, NV("2026-10-01", "2026-11-20", "NVIDIA (NVDA)", "Daily close in US dollars, October 1 to November 20, 2026",
                    markers=[("2026-10-06", "Peak"), ("2026-11-06", "Before the scandal")], labels=[("2026-11-20", 1700, 330, "-33%", ROOD)], teken=0.8, eind_label=False)),
 (ZR(59) - 0.15, fasen(F("hq-atrium", (1.0, 1.08), 0.4), [(59, GR("~$1.5 TRILLION", "market value lost in 2 weeks (estimate)", ROOD, 140)),
                                                         (60, GR("-48%", "from the October peak", ROOD, 190))])),
 (ZR(61) - 0.15, fasen(F("ai-datacenter", (1.0, 1.08), 0.5), [(61, ON("It was not just Nvidia")), (62, ON("CoreWeave and Nebius, which rent out Nvidia chips, fell too")),
                                                             (63, GR("THE AI TRADE", None, ORANJE, 140)), (64, ON("Without Huang, it looked shaky"))])),
 # --- h4 de ommekeer ---
 (ZR(65) - 0.15, fasen(F("capitol", (1.0, 1.08), 0.5), [(65, ON("Behind the scenes, something was changing")), (66, ON("CNBC: senior government officials briefed the board")),
                                                       (67, ON("No national security laws broken, they said (per sources)")), (68, ON("The board reached out to Huang")),
                                                       (69, ON("Investors Brad Gerstner and Gavin Baker pushed for his return"))])),
 (ZR(70) - 0.15, fasen(F("v:trump", (1.0, 1.06), 0.55), [(70, ON("Weekend talks")), (71, LT("PRESIDENT DONALD TRUMP", "got involved")),
                                                        (72, ON('"Directly and indirectly" (to CNBC)')), (73, GR('"I MADE THE DEAL"', "Donald Trump to CNBC", WIT, 120))])),
 (ZR(74) - 0.15, fasen(F("ai-boardroom", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(74, ON("The board wanted guarantees about national security")),
                                                         (75, ON('"We gave them assurances, at least with everything we know"')), (76, ON('He asked Huang to promise to "work hard"'))])),
 (ZR(77) - 0.15, doc("Nvidia filing with the SEC, November 23, 2026", "NVIDIA Board Reinstates Jensen Huang",
                     ["Unanimous vote: President, CEO", "and member of the Board.", "", "Input from senior levels of the", "United States government."], mark=3,
                     achter="hq-wall", mark_na=79)),
 (ZR(80) - 0.15, fasen(portret("huang-h"), [(80, ON('Huang: "honored to return"')), (81, ON("He fully supports the board's investigation"))])),
 (ZR(82) - 0.15, NV("2026-10-01", "2026-11-23", "NVIDIA (NVDA)", "Daily close in US dollars, October 1 to November 23, 2026",
                    labels=[("2026-11-23", 1700, 330, "+31%", GROEN)], teken=0.75, eind_label=False)),
 (ZR(84) - 0.15, fasen(F("ces2025", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(84, GR("$165.05", "closing price, November 23", GROEN, 180)),
                                                         (85, LT("MIZUHO", "His return restores confidence in the AI trade")), (86, ON("Several analysts raised their ratings"))])),
 (ZR(87) - 0.15, fasen(F("huang-e", (1.0, 1.08), 0.55), [(87, ON('Trump: "a Great Patriot and National Treasure"')),
                                                        (88, ON('"Does not possess evidence" of any unlawful conduct')), (89, ON("Elon Musk: the mistake has been corrected"))])),
 # --- h5 nog niet voorbij ---
 (ZR(90) - 0.15, fasen(F("wallst", (1.0, 1.08), 0.45), [(90, ON("Tuesday: the excitement cooled")), (91, GR("-5.9%", "Nvidia, November 24", ROOD, 200)),
                                                       (92, ON("AMD, Arm, Micron, CoreWeave: -9% to -12%")), (93, GR("$155.38", "closing price", WIT, 180)),
                                                       (94, LT("BANK OF AMERICA", '"Reinstatement should not be confused with the end of scrutiny"'))])),
 (ZR(95) - 0.15, fasen(F("ai-warroom", (1.0, 1.08), 0.5), [(95, GR("NOT OVER", None, ROOD, 170)), (96, ON("New board committee: national security and export control")),
                                                          (97, ON("Were company secrets or national security put at risk?")), (98, LT("WACHTELL, LIPTON, ROSEN & KATZ", "independent counsel")),
                                                          (99, ON('"Will proceed to conclusion"')), (100, ON("Also searching: a new chief compliance officer"))])),
 (ZR(101) - 0.15, fasen(F("ca-capitol", (1.0, 1.08), 0.5), [(101, LT("CALIFORNIA ATTORNEY GENERAL", "still probing Nvidia")), (102, ON('"Whether Nvidia misled investors and the public"'))])),
 (ZR(103) - 0.15, lijst("capitol", "Congress", [(104, "Dec 1: Huang, closed-door, 3 House committees"), (105, "Dec 2: Nvidia's general counsel"),
                                                (106, "Dec 3: Senate Banking hearing, Huang only witness")])),
 (ZR(107) - 0.15, fasen(F("ai-hoorzaal", (1.0, 1.08), 0.5), [(107, ON("Not everyone in Washington is convinced")), (108, LT("SEN. JOHN CORNYN", '"No national security risk? Based on what?"')),
                                                            (109, LT("SEN. ELIZABETH WARREN", 'Called the decision "reckless"')), (110, LT("PIPER SANDLER", "Expects little impact on the stock"))])),
 # --- h6 waarom één man ---
 (ZR(111) - 0.15, fasen(F("huang-g", (1.0, 1.08), 0.55), [(111, ON("Why does one man move a company this much?")), (112, GR("KEY PERSON RISK", None, ORANJE, 130)),
                                                         (113, GR("~3.5%", "of Nvidia owned by Huang", WIT, 190)), (114, ON("But he shaped its products, customers and AI vision"))])),
 (ZR(115) - 0.15, fasen(F("ai-lege-stoel", (1.0, 1.08), 0.55), [(115, ON("No clear successor")), (116, LT("RENE HAAS", "Arm CEO · reportedly considered (NBC News)")),
                                                               (117, ON("He chose to stay at Arm")), (118, ON("If secrets were shared, the question returns (analyst, CNBC)")),
                                                               (119, ON("Crash and comeback: what Nvidia is worth without him"))])),
 # --- h7 wat nu ---
 (ZR(120) - 0.15, lijst("hq-atrium", "What to watch", [(121, "Hearings: December 1, 2 and 3"), (122, "The board's own investigation"),
                                                       (123, "The California probe"), (124, "The stock: still well below October")])),
 (ZR(125) - 0.15, fasen(F("dgx-gb200", (1.08, 1.0), 0.45, pan=(0.5, 0.4, 0.5, 0.5)), [(125, GR("NOT FINANCIAL ADVICE", None, WIT, 110))])),
 (ZR(126) - 0.15, slot_fade("huang-a", "Jensen Huang is back. The story is not over.")),
]
SHOTS.sort(key=lambda x: x[0])

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
