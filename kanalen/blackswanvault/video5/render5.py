"""BlackSwanVault video 5 (storingen in Amerika). Zelfde stijl als video 4. Gebruik: python render5.py [--van s --tot s | --plaat uit.jpg]"""
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

# ---------- video 5: storingen (zinnummers = script.txt, zie bronnen.md) ----------
NUM = lambda v: f"{v:,.0f}"
SHOTS = [
 # --- opening ---
 (0.0, fasen(F("yyz-b", (1.0, 1.1), 0.55), [(0, ST("NOVEMBER 13, 2026")), (1, GR("4+ HOURS", "the US air traffic system, effectively shut down", ROOD, 170)),
                                           (2, GR("25 YEARS", "the longest nationwide ground stop in 25 years", WIT, 170))])),
 (ZR(3) - 0.15, lijst("ai-kaart-vs", "One week in America", [(4, "Thursday: Microsoft email down worldwide"), (5, "Monday: JPMorgan payments delayed"),
                                                            (6, "Tuesday: NSA internal network offline"), (7, "Tuesday: Apple services disrupted")])),
 (ZR(8) - 0.15, fasen(F("ai-doomscroll", (1.0, 1.08), 0.5), [(8, GR("4 FAILURES", "in 4 business days", ROOD, 170)), (10, GR("Is America under attack?", None, WIT, 90))])),
 (ZR(11) - 0.15, fasen(F("ai-generators", (1.0, 1.08), 0.5), [(11, ON("Some did not wait for the answer")), (12, ON("They bought generators"))])),
 (ZR(13) - 0.15, fasen(F("ai-warroom", (1.0, 1.08), 0.5), [(13, GR("What is actually going on?", None, WIT, 90)), (15, GR("NOT A CYBERATTACK", "according to the US government", ORANJE, 130)),
                                                         (17, ON("A rush to fix more security holes than ever"))])),
 (ZR(18) - 0.15, fasen(F("ai-code-scan", (1.0, 1.08), 0.5), [(18, ON("Many of those holes were found by AI")), (19, GR("SOME FIXES BROKE THINGS", None, ROOD, 110))])),
 # --- h1 Microsoft ---
 (ZR(21) - 0.15, fasen(F("ms-b92", (1.0, 1.08), 0.55), [(21, EN(LT("MICROSOFT", "Redmond, Washington"), ST("THURSDAY, NOVEMBER 12"))),
                                                       (22, ON("Outlook, Teams and other Microsoft 365 services stopped working"))])),
 (ZR(23) - 0.15, fasen(F("ai-email-down", (1.0, 1.08), 0.5), [(23, GR("MILLIONS", "of users lost access to their email (CNBC)", WIT, 170)), (24, ON("Across two workdays"))])),
 (ZR(25) - 0.15, doc("Microsoft, via ABC News, November 16, 2026", "Charles Lamanna, Executive Vice President at Microsoft",
                     ["\"A latent defect caused servers", "to become overwhelmed and unresponsive", "under certain load conditions.\"", "", "The bug came from a fix prepared in July."],
                     mark=1, achter="ms-campus", mark_na=27)),
 (ZR(28) - 0.15, fasen(F("ai-serverdruk", (1.0, 1.08), 0.5), [(28, ON("For months, nobody noticed")), (29, ON("Peak US traffic, fewer servers available")),
                                                            (30, GR("BUG TRIGGERED", None, ROOD, 140)), (31, ON("Requests piled up until servers stopped responding"))])),
 (ZR(32) - 0.15, fasen(F("racks", (1.08, 1.0), 0.5), [(32, ON("Fixing it was harder than it sounds")), (33, ON("Servers came back, and were flooded by waiting traffic")),
                                                    (34, GR("DOWN AGAIN", None, ROOD, 150))])),
 (ZR(35) - 0.15, fasen(F("ms-campus", (1.0, 1.08), 0.5), [(35, ON('Microsoft: "We are deeply sorry"')), (36, GR("NOT A HACK", "according to Microsoft", WIT, 140))])),
 # --- h2 FAA ---
 (ZR(37) - 0.15, fasen(F("atc-washington", (1.0, 1.08), 0.55), [(37, ST("FRIDAY, NOVEMBER 13")), (38, ON("Chicago controllers start losing communications")),
                                                              (39, ON("Within about half an hour, it spreads across the country"))])),
 (ZR(40) - 0.15, fasen(F("ai-stil-vliegveld", (1.0, 1.08), 0.5), [(40, GR("3:54 PM", "Eastern time: all flights to US airports stopped", ROOD, 170))])),
 (ZR(41) - 0.15, balken([("Canceled", 8000), ("Delayed", 10000)], "FRIDAY, NOVEMBER 13", "US flights, approximately", "Source: FlightAware, via Wikipedia", lambda v: f"{v:,.0f}+" if v >= 9999 else f"~{v:,.0f}",
                        [41, 42], kleur=ROOD)),
 (ZR(43) - 0.15, fasen(F("yyz-a", (1.0, 1.08), 0.5), [(43, ON("Flights from Europe to the US: suspended until morning")), (44, ON("The trouble continued all weekend"))])),
 (ZR(45) - 0.15, fasen(F("ai-router", (1.0, 1.1), 0.45), [(45, GR("What caused it?", None, WIT, 100)), (46, GR("ONE ROUTER", None, ORANJE, 170))])),
 (ZR(47) - 0.15, fasen(F("glasvezel", (1.0, 1.08), 0.5), [(47, EN(LT("SOUTHERN ARKANSAS", "Contractor L3Harris: copper cables to fiber optic"), ST("AIR TRAFFIC NETWORK"))),
                                                        (48, ON("A new router was installed"))])),
 (ZR(49) - 0.15, fasen(portret("duffy"), [(49, LT("SEAN DUFFY", "US Transportation Secretary")), (49.5, GR("1,000", "connection attempts every 4 to 5 seconds", ORANJE, 170)),
                                         (50, GR("17", "air traffic control centers disrupted", ROOD, 190))])),
 (ZR(51) - 0.15, fasen(F("eqiad", (1.0, 1.08), 0.5), [(51, ON("Not the full story yet")), (52, ON("Maker: the router worked exactly as configured")),
                                                    (53, ON("FAA stopped installing these routers")), (54, GR("ROOT CAUSE?", "not officially announced yet (November 20)", ORANJE, 140))])),
 (ZR(55) - 0.15, fasen(F("atc-tower", (1.0, 1.08), 0.5, pan=(0.5, 0.3, 0.5, 0.5)), [(55, ON("An uncomfortable detail")),
                                                    (56, ON("A watchdog warned: the FAA was not properly supervising its contractors")),
                                                    (57, GR("$50 BILLION", "what Duffy is asking Congress for", WIT, 150))])),
 # --- h3 maandag/dinsdag ---
 (ZR(58) - 0.15, fasen(F("jpm", (1.0, 1.08), 0.55), [(58, ST("MONDAY, NOVEMBER 16")), (59, LT("JPMORGAN CHASE", "Biggest US bank · customer payments delayed")),
                                                   (60, ON('"A software bug in on-premise hardware systems"')), (61, ON("Payments to those accounts delayed too: jitters across the financial system"))])),
 (ZR(62) - 0.15, fasen(F("united", (1.0, 1.08), 0.55), [(62, LT("UNITED AIRLINES", "A system failure delayed departing flights"))])),
 (ZR(63) - 0.15, fasen(F("nsa", (1.0, 1.08), 0.55), [(63, EN(LT("NATIONAL SECURITY AGENCY", "Fort Meade, Maryland"), ST("TUESDAY, NOVEMBER 17"))),
                                                   (64, ON("Network for classified information: offline")), (65, ON('NSA: "scheduled routine maintenance"'))])),
 (ZR(66) - 0.15, fasen(F("apple", (1.0, 1.08), 0.55), [(66, LT("APPLE", "Apple Music, App Store, support: disrupted after an internal update")),
                                                     (67, ON("Marriott: customers could not sign in"))])),
 # --- h4 paniek ---
 (ZR(68) - 0.15, fasen(F("ai-doomscroll", (1.08, 1.0), 0.45), [(68, ON("Many stopped believing in coincidence")), (69, ON("Videos: stock up before the next blackout")),
                                                             (70, ON("And many listened"))])),
 (ZR(71) - 0.15, fasen(F("costco", (1.0, 1.08), 0.5), [(71, GR("21 OF 26", "expensive generators on Costco's website: sold out", ORANJE, 170)),
                                                     (72, GR("+10%", "expected Costco US sales growth in November (Mizuho)", WIT, 170))])),
 (ZR(73) - 0.15, fasen(F("ai-garage-generator", (1.0, 1.08), 0.5), [(73, ON("Also: Sam's Club, Home Depot, Lowe's")), (74, ON("Mizuho: anxiety after the outages, and \"apocalyptic\" talk online")), (75, GR("DECEMBER 10", "Costco reports its results", WIT, 140))])),
 # --- h5 aanval? ---
 (ZR(76) - 0.15, fasen(F("ai-kaart-vs", (1.08, 1.0), 0.45), [(76, GR("Was it an attack?", None, WIT, 100)), (78, ON("Government and companies: no evidence of a cyberattack"))])),
 (ZR(79) - 0.15, fasen(portret("clayton"), [(79, LT("JAY CLAYTON", "Director of National Intelligence")),
                                           (80, ON('"This is not cyberattack, and this is not a coordinated effort by a nation state."')),
                                          (81, ON("Upgrades like these are common; he wants a nationwide upgrade"))])),
 (ZR(82) - 0.15, fasen(portret("jeffries"), [(83, LT("HAKEEM JEFFRIES", "House Democratic leader: too early to rule anything out"))])),
 (ZR(84) - 0.15, fasen(portret("warner"), [(85, LT("SEN. MARK WARNER", "Co-chair, Senate Cybersecurity Caucus")),
                                          (85.5, ON('"...the unintended consequences of efforts to make our systems safer"'))])),
 (ZR(86) - 0.15, fasen(F("ai-code-scan", (1.08, 1.0), 0.5), [(86, ON("What AI has been doing to software this year")), (87, ON("Every piece of software has weak spots")),
                                                          (88, GR("VULNERABILITIES", None, ORANJE, 130)), (89, ON("Each one found gets an official number"))])),
 # --- h6 AI ---
 (ZR(90) - 0.15, balken([("2025, full year", 50000), ("2026, by mid-November", 100222)], "PUBLISHED SOFTWARE VULNERABILITIES", "Official CVE numbers",
                        "Source: VulnCheck, via The Register", lambda v: "< 50,000" if v < 60000 else f"{v:,.0f}", [90, 91], hl=1, kleur=ROOD)),
 (ZR(92) - 0.15, fasen(F("nersc", (1.0, 1.08), 0.5), [(92, GR("MORE THAN DOUBLE", None, ROOD, 140)), (93, ON("Researchers: AI-driven bug hunting drives much of the surge"))])),
 (ZR(94) - 0.15, balken([("January", 5045), ("July", 10477), ("August", 10740)], "NEW VULNERABILITIES PER MONTH, 2026", "Published CVEs",
                        "Source: Google Threat Intelligence Group", NUM, [94, 95, 95], kleur=ORANJE)),
 (ZR(96) - 0.15, fasen(F("ms-b92", (1.1, 1.0), 0.45), [(96, GR("206", "fixes in one Microsoft monthly update, June: a record", WIT, 190))])),
 (ZR(97) - 0.15, fasen(F("ai-code-scan", (1.0, 1.1), 0.45, pan=(0.3, 0.5, 0.6, 0.5)), [(97, ST("OCTOBER 2026")), (98, LT("PHP", "Software behind a huge part of the web · 2 critical flaws, found with AI")),
                                                                               (99, ON("Attackers could take over a server from anywhere"))])),
 (ZR(100) - 0.15, fasen(F("capitol", (1.0, 1.08), 0.5), [(100, ON("US government: update right away, or go offline")), (101, GR("ALREADY EXPLOITED", None, ROOD, 130)), (102, GR("1.5 MILLION", "of 2.6 million servers watched by Censys: still unpatched", ROOD, 150))])),
 (ZR(103) - 0.15, fasen(F("ai-warroom", (1.08, 1.0), 0.5), [(103, GR("A RACE", None, ORANJE, 170)), (104, ON("Fix every system before attackers find it")),
                                                        (105, ON("Change thousands of systems in a hurry, and some break"))])),
 (ZR(106) - 0.15, fasen(F("nsa-b", (1.0, 1.08), 0.5), [(106, ON("Clayton (Fox News): some systems did not come back up after patching")),
                                                     (107, ON('"That is what has happened at the NSA today"'))])),
 (ZR(108) - 0.15, fasen(F("ai-slot-schild", (1.0, 1.08), 0.5), [(108, ON("The strange part")), (109, ON("AI helps defenders find holes faster than ever")),
                                                              (110, GR("AND ATTACKERS", None, ROOD, 150)), (111, ON("Google: hackers use AI agents to study new security fixes")), (113, ON("The pressure to fix everything keeps growing"))])),
 (ZR(114) - 0.15, fasen(F("racks", (1.0, 1.08), 0.5, pan=(0.6, 0.5, 0.4, 0.5)), [(114, LT("TOM HEGEL", "Research head, SentinelOne")),
                                                                              (115, GR('"The weird teenage phase"', "of technology", WIT, 100))])),
 # --- h7 wat nu ---
 (ZR(116) - 0.15, lijst("ai-terminal", "What happens next", [(117, "FAA: the root cause of the ground stop"), (118, "Congress: briefings and answers"),
                                                            (119, "December 10: Costco's results"), (120, "Thanksgiving, November 26: busiest travel week")])),
 (ZR(121) - 0.15, fasen(F("ai-serverdruk", (1.08, 1.0), 0.5), [(121, ON('"We are likely to witness more incidents of this nature"'))])),
 (ZR(122) - 0.15, slot_fade("ai-slot-schild", "The fixes themselves")),
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
