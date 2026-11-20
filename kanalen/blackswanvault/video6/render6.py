"""BlackSwanVault video 6 (werkt AI?). Zelfde stijl als video 5. Gebruik: python render6.py [--van s --tot s | --plaat uit.jpg]"""
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

# ---------- video 6: werkt AI? (zinnummers = script.txt, zie bronnen.md) ----------
NUM = lambda v: f"{v:,.0f}"
MLD = lambda v: f"${v:.0f}B"
PC = lambda v: f"+{v:.0f}%" if v >= 0 else f"{v:.1f}%"
HB = "Source: Chen & Stratton, Harvard (working paper, Nov. 19, 2026)"
SHOTS = [
 # --- opening ---
 (0.0, fasen(F("ai-bouw-dc", (1.0, 1.1), 0.55), [(0, GR("$700 BILLION+", "AI spending by 4 tech giants, 2026", ORANJE, 150)), (2, ON("It all rests on one promise")),
                                                (3, GR("MORE PRODUCTIVE", None, WIT, 130))])),
 (ZR(4) - 0.15, fasen(F("harvard-a", (1.0, 1.08), 0.5), [(4, EN(LT("HARVARD UNIVERSITY", "New study, latest version November 19, 2026"), ST("NOVEMBER 19"))),
                                                       (5, GR("655", "companies", WIT, 190)), (6, GR("720,000+", "workers", WIT, 170)), (7, GR("445 MILLION", "pieces of real work", WIT, 140))])),
 (ZR(8) - 0.15, fasen(F("ai-engineer-ai", (1.0, 1.08), 0.5), [(8, ON("What they found is strange")), (9, GR("+44%", "more code with AI agents", ORANJE, 190)),
                                                            (10, GR("FINISHED WORK?", "barely moved", ROOD, 130))])),
 (ZR(11) - 0.15, fasen(F("ai-stapel", (1.0, 1.08), 0.5), [(11, GR("Is AI actually working?", None, WIT, 90)), (12, GR("YES, AND NO", None, ORANJE, 150)),
                                                        (13, ON("AI works on the task")), (14, ON("But the company around it cannot keep up")),
                                                        (15, ON("And that could decide the $700 billion bet"))])),
 # --- h1 geld ---
 (ZR(17) - 0.15, balken([("Amazon", 220), ("Alphabet", 200), ("Microsoft", 170), ("Meta", 140)], "PLANNED SPENDING IN 2026", "Capital expenditures, mostly for AI. Alphabet and Meta: middle of their range",
                        "Source: company reports, via CNBC (Oct. 2026)", MLD, [18, 19, 20, 21], kleur=ORANJE)),
 (ZR(22) - 0.15, fasen(F("dc-a", (1.0, 1.08), 0.5), [(22, ON("Chips, servers and data centers")), (24, GR("+48%", "Microsoft Azure, cloud revenue growth", GROEN, 170))])),
 (ZR(25) - 0.15, fasen(F("ai-geld-chips", (1.0, 1.08), 0.5), [(25, ON("That spending is starting to hurt")), (26, GR("NEGATIVE", "free cash flow: Amazon, Alphabet, Meta", ROOD, 150)),
                                                            (27, ON("They spent more cash than their businesses brought in")), (28, ON("Only Microsoft stayed positive"))])),
 (ZR(29) - 0.15, balken([("Q1 2025", 26), ("Q1 2026", 1.2)], "META: FREE CASH FLOW", "In one quarter, billions of dollars", "Source: CNBC (April 30, 2026)",
                        lambda v: f"${v:.1f}B" if v < 10 else f"${v:.0f}B", [29, 29], hl=1, kleur=ROOD)),
 (ZR(30) - 0.15, fasen(F("google", (1.0, 1.08), 0.5), [(30, ON("Investors noticed")), (31, GR("-10%", "Alphabet stock, after its October report", ROOD, 180)),
                                                     (32, ON("Alphabet: spending will rise significantly in 2027"))])),
 (ZR(33) - 0.15, fasen(F("ai-belegger", (1.0, 1.08), 0.5), [(33, GR("$1 TRILLION", "possible AI spending in 2027 (Bank of America, Evercore)", ORANJE, 150)),
                                                          (34, ON("So the question is simple")), (35, GR("What are companies getting back?", None, WIT, 90))])),
 # --- h2 onderzoek ---
 (ZR(36) - 0.15, fasen(F("harvard-b", (1.0, 1.08), 0.5), [(36, ON("The Harvard study tried to measure exactly that")),
                                                        (37, LT("FIONA CHEN & JAMES STRATTON", "Economics researchers, Harvard University")), (38, ON("A working paper: not peer reviewed yet"))])),
 (ZR(40) - 0.15, fasen(F("code", (1.0, 1.08), 0.5), [(40, LT("JELLYFISH", "Platform that tracks the work of software teams")), (41, ON("Every piece of code, every finished task, every meeting")),
                                                    (42, ON("And when a company starts using AI tools")), (43, ST("JANUARY 2021 TO AUGUST 2026"))])),
 (ZR(44) - 0.15, fasen(F("ai-engineer-ai", (1.1, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(44, ON("Software: the best place to test AI")),
                                                    (45, GR("~80%", "of their own code is written by AI, the big AI labs say", ORANJE, 170)), (46, ON("If it works anywhere, it should be here"))])),
 (ZR(47) - 0.15, balken([("AI assistants", 30.4), ("+ AI agents", 44.0)], "MORE LINES OF CODE", "Per firm, about a year after adoption", HB, PC, [48, 50], kleur=ORANJE)),
 (ZR(51) - 0.15, fasen(F("ai-stapel", (1.08, 1.0), 0.45), [(51, GR("+36%", "code changes sent in for approval", ORANJE, 170)), (52, ON("But writing code is not the goal")),
                                                        (53, GR("WORKING SOFTWARE", None, WIT, 120))])),
 (ZR(54) - 0.15, balken([("AI assistants", -1.5), ("AI agents", 13.7)], "FINISHED TASKS", "Tasks completed and shipped to production", HB, PC, [55, 56], hl=1, kleur=ORANJE, schaal=44)),
 (ZR(57) - 0.15, fasen(F("ai-vergadering", (1.0, 1.08), 0.5), [(57, ON("And even that result was borderline")), (58, GR("Bigger tasks?", None, WIT, 100)),
                                                             (59, ON("Checked with AI reading the task descriptions")), (60, GR("NO", "the tasks did not get bigger", ROOD, 170))])),
 (ZR(61) - 0.15, balken([("More code", 44.0), ("More finished work", 13.7)], "AI AGENTS: CODE VS FINISHED WORK", "Increase after adoption, at best", HB, PC, [61, 61], hl=1, kleur=ROOD)),
 # --- h3 flessenhals ---
 (ZR(62) - 0.15, fasen(F("ai-file", (1.0, 1.08), 0.5), [(62, GR("Where did the extra code go?", None, WIT, 90)), (63, GR("A TRAFFIC JAM", None, ORANJE, 150))])),
 (ZR(64) - 0.15, fasen(F("ai-senior", (1.0, 1.08), 0.5), [(64, ON("Before new code goes live, another engineer checks it")), (65, GR("CODE REVIEW", None, ORANJE, 150)), (66, ON("Read it, test it, approve it")),
                                                        (67, ON("Still done mostly by humans"))])),
 (ZR(68) - 0.15, balken([("Waiting for review", 59.9), ("Active review", 58.5), ("Submit to approval", 56.1), ("Comments per change", 38.6)], "AFTER AI AGENTS: CODE REVIEW",
                        "Change after adoption", HB, PC, [68, 69, 70, 71], hl=2, kleur=ROOD)),
 (ZR(72) - 0.15, fasen(F("ai-vergadering", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(72, ON("Why this is hard to fix")), (73, ON("Engineers usually review code they already know")),
                                                        (74, GR("83%", "of reviews: by someone who knows the code", WIT, 190)), (75, ON("You cannot hand the extra work to anyone"))])),
 (ZR(76) - 0.15, doc("Interview in the study", "An engineer at a software company",
                     ["\"People could make a huge number of", "commits quickly, but code review was", "still the bottleneck.\"", "", "One senior engineer could only review once a week."],
                     mark=2, achter="ai-senior", mark_na=76)),
 (ZR(78) - 0.15, fasen(F("ai-wachten", (1.0, 1.08), 0.5), [(78, ON("After outages caused by AI-written code: senior approval required")), (79, GR("EVEN SLOWER", None, ROOD, 140))])),
 (ZR(80) - 0.15, fasen(F("nersc", (1.0, 1.08), 0.5), [(80, GR("AI reviewing code?", None, WIT, 100)), (81, GR("79%", "of companies already use AI review tools", ORANJE, 190)),
                                                    (82, ON("But humans still write the overwhelming majority of reviews"))])),
 (ZR(83) - 0.15, fasen(F("fabriek", (1.0, 1.08), 0.5), [(83, ON("Think of a factory")), (84, ON("One machine becomes twice as fast")), (85, ON("The next station: same speed as before"))])),
 (ZR(86) - 0.15, fasen(F("ai-lopendeband", (1.0, 1.08), 0.5), [(86, ON("The factory does not produce twice as much")), (87, GR("A BIGGER PILE", "in front of the slow station", ORANJE, 140))])),
 (ZR(88) - 0.15, fasen(F("ai-vergadering", (1.0, 1.06), 0.5, pan=(0.3, 0.5, 0.5, 0.5)), [(88, ON("Writing code is only part of the job")),
                                                        (89, GR("30-40%", "of engineers' time goes to writing code", WIT, 170)), (90, ON("The rest: planning, meetings, reviewing, testing")),
                                                        (91, ON("AI speeds up the part that was never the whole job"))])),
 (ZR(92) - 0.15, balken([("Coding productivity", 73.7), ("Time spent coding", -22.7), ("Time spent reviewing", 43.4)], "WHAT AI AGENTS CHANGE INSIDE FIRMS",
                        "Model estimates by the researchers", HB, PC, [93, 95, 95], kleur=ORANJE, schaal=74)),
 # --- h4 banen ---
 (ZR(96) - 0.15, fasen(F("ai-kantoor-leeg", (1.0, 1.08), 0.5), [(96, ON("The question everyone is asking")), (97, GR("Is AI taking jobs?", None, WIT, 100)),
                                                              (99, GR("NO CLEAR EFFECT", "on employment, in this data", ORANJE, 130)), (102, ON("Only software engineers: not other jobs"))])),
 (ZR(104) - 0.15, fasen(F("ai-bouw-dc", (1.08, 1.0), 0.45), [(104, ON("That may not last")), (106, ON("Simulations: more output, fewer jobs over time")),
                                                           (107, ON("Smaller effects if the review bottleneck stays"))])),
 (ZR(108) - 0.15, fasen(portret("stiglitz"), [(109, LT("JOSEPH STIGLITZ", "Nobel prize in economics · November 14, 2026")), (109.6, ON("He called the AI boom a bubble")), (110, ON("Speaking at a business summit in New Delhi")),
                                             (111, ON("Massive investors will not get the returns they expect")), (112, ON('"Really good at replacing coders, programmers"'))])),
 (ZR(113) - 0.15, fasen(F("ai-kantoor-leeg", (1.08, 1.0), 0.45, pan=(0.6, 0.5, 0.4, 0.5)), [(113, ON("A deeper problem")),
                                                              (114, GR("Who buys what AI makes?", "if AI destroys the jobs", WIT, 90))])),
 # --- h5 Solow ---
 (ZR(115) - 0.15, fasen(portret("solow"), [(116, LT("ROBERT SOLOW (LEFT)", "Nobel prize in economics, 1987")),
                                          (117, ON('"You can see the computer age everywhere but in the productivity statistics."')),
                                          (118, ON("Computers everywhere, but no productivity gain to show for it"))])),
 (ZR(119) - 0.15, fasen(F("pc1987", (1.0, 1.08), 0.5), [(119, ST("1987")), (119.5, ON("Years of buying computers")), (120, ON("And for a long time, the numbers did not show it"))])),
 (ZR(121) - 0.15, fasen(F("ford1923", (1.0, 1.08), 0.5, grijs=True), [(121, GR("LATE 1990s", "US productivity growth finally sped up", ORANJE, 140)),
                                                                     (122, ON("Companies changed how they worked around the machines"))])),
 (ZR(123) - 0.15, fasen(F("ai-belegger", (1.08, 1.0), 0.45), [(123, ON("The real lesson")), (124, ON("A new tool is not enough")), (125, ON("The work around it has to change too")),
                                                            (126, GR("YEARS", None, ORANJE, 170)), (127, GR("Can $700B a year wait?", None, WIT, 100))])),
 # --- h6 wat nu ---
 (ZR(128) - 0.15, lijst("ai-geld-chips", "What to watch", [(129, "Earnings in late January: 2027 spending"), (130, "Cash flow"),
                                                           (131, "AI tools that review and test code"), (132, "Finished work, not just code")])),
 (ZR(133) - 0.15, slot_fade("ai-engineer-ai", "The hard part was never just writing it")),
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
