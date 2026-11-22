"""Mooiere grafieken voor de tekenstijl (eigenaar 21 nov: "maak het wat mooier, die grafieken vind ik niet zo mooi; logo van het
bedrijf mag je ook gebruiken"). Alles wordt op dubbele grootte getekend en dan verkleind (zachte randen), op een licht kaartje
met schaduw, logo linksboven. Cijfers altijd uit echte slotkoersen; lijngrafiek toont top en laagste/nu (vaste regel)."""
import datetime as dt, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = 2
DONKER = False
KAART, RAND, GRIJS, INKT = (250, 248, 244), (225, 220, 212), (150, 146, 140), (30, 30, 36)
ROOD, GROEN, BLAUW = (222, 49, 49), (46, 160, 90), (36, 110, 210)
FB = "C:/Windows/Fonts/segoeuib.ttf"; FS = "C:/Windows/Fonts/seguisb.ttf"; FH = "C:/Windows/Fonts/segoeprb.ttf"
MAAND_EN = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
MAAND = ['jan', 'feb', 'mrt', 'apr', 'mei', 'jun', 'jul', 'aug', 'sep', 'okt', 'nov', 'dec']


def thema_donker():
    """BlackswanVault: donkere kaartjes op het bord"""
    global KAART, RAND, GRIJS, INKT, DONKER
    DONKER = True
    KAART, RAND, GRIJS, INKT = (40, 46, 43), (78, 86, 82), (170, 176, 170), (236, 236, 228)


def f(pad, maat): return ImageFont.truetype(pad, int(maat * S))
def eur(v, dec=0): return "€" + f"{v:,.{dec}f}".replace(",", "X").replace(".", ",").replace("X", ".")
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3


def koersen(pad):
    r = json.load(open(pad))["chart"]["result"][0]
    return [(dt.date.fromtimestamp(a), b) for a, b in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if b]


def plak(doek, laag, x, y, alpha=1.0):
    """laag (RGBA, dubbele grootte) verkleinen en op het doek leggen"""
    k = laag.reduce(S)                                                  # 22 nov: snel verkleinen (box), oogt gelijk
    a = np.asarray(k).astype(np.float32) / 255
    H, W = doek.shape[:2]
    x0, y0, x1, y1 = max(0, x), max(0, y), min(W, x + k.width), min(H, y + k.height)
    if x1 <= x0 or y1 <= y0: return
    a = a[y0 - y:y1 - y, x0 - x:x1 - x]; al = a[..., 3:4] * alpha
    vak = doek[y0:y1, x0:x1].astype(np.float32)
    doek[y0:y1, x0:x1] = (vak * (1 - al) + a[..., :3] * 255 * al).astype(np.uint8)


_KAART = {}


def kaartje(w, h):
    """(22 nov: snelheid) kaart + schaduw één keer maken per maat en thema, daarna een kopie"""
    sleutel = (w, h, KAART, RAND)
    if sleutel not in _KAART: _KAART[sleutel] = _kaartje(w, h)
    laag, m = _KAART[sleutel]; laag = laag.copy()
    return laag, ImageDraw.Draw(laag), m


def _kaartje(w, h):
    """lichte kaart met zachte schaduw; geeft laag + draw (dubbele grootte, 24 px marge voor de schaduw)"""
    m = 24 * S
    laag = Image.new("RGBA", (w * S + 2 * m, h * S + 2 * m), (0, 0, 0, 0))
    sch = Image.new("RGBA", laag.size, (0, 0, 0, 0))
    ImageDraw.Draw(sch).rounded_rectangle((m + 6 * S, m + 10 * S, m + w * S + 6 * S, m + h * S + 10 * S), 26 * S, fill=(0, 0, 0, 60))
    laag = Image.alpha_composite(laag, sch.filter(ImageFilter.GaussianBlur(12 * S)))
    d = ImageDraw.Draw(laag)
    d.rounded_rectangle((m, m, m + w * S, m + h * S), 26 * S, fill=KAART + (255,), outline=RAND + (255,), width=2 * S)
    return laag, m


def logo_op(laag, pad, x, y, hoog):
    lg = Image.open(pad).convert("RGBA")
    if lg.mode == "RGBA" and np.asarray(lg)[..., 3].min() == 255:         # wit weg (ASML-logo heeft witte achtergrond)
        a = np.asarray(lg).copy(); wit = a[..., :3].min(axis=2) > 235; a[wit, 3] = 0; lg = Image.fromarray(a)
    if DONKER:                                                        # zwart logo op donker bord -> licht
        a = np.asarray(lg).copy(); zicht = a[..., 3] > 0
        if zicht.any() and a[..., :3][zicht].mean() < 90: a[..., :3][zicht] = INKT; lg = Image.fromarray(a)
    lg = lg.resize((int(lg.width * hoog * S / lg.height), int(hoog * S)), Image.LANCZOS)
    laag.alpha_composite(lg, (int(x), int(y)))
    return lg.width


def pil(d, xy, tekst, maat, bg, fg=None, anker="mm"):
    """getal in een pilletje"""
    if fg is None: fg = (25, 25, 30) if sum(bg[:3]) > 450 else (255, 255, 255)
    ft = f(FB, maat); b = d.textbbox((0, 0), tekst, font=ft); w, h = b[2] - b[0], b[3] - b[1]
    px, py = 0.55 * maat * S, 0.35 * maat * S; cx, cy = xy
    if anker == "lm": cx += w / 2 + px
    if anker == "rm": cx -= w / 2 + px
    d.rounded_rectangle((cx - w / 2 - px, cy - h / 2 - py, cx + w / 2 + px, cy + h / 2 + py), (h / 2 + py), fill=bg)
    d.text((cx, cy), tekst, font=ft, fill=fg, anchor="mm")


def staaf(laag, box, kleur, rond="boven"):
    """staaf met ronde kant en zacht verloop (licht boven, donkerder onder)"""
    x0, y0, x1, y1 = [int(v) for v in box]
    if x1 - x0 < 2 or y1 - y0 < 2: return
    m = Image.new("L", (x1 - x0, y1 - y0), 0); r = min(16 * S, (x1 - x0) // 2, (y1 - y0))
    ImageDraw.Draw(m).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), r, fill=255,
                                        corners=(True, True, False, False) if rond == "boven" else (False, False, True, True))
    t = np.linspace(0, 1, y1 - y0)[:, None, None]
    licht = np.array([min(255, c + 45) for c in kleur], float); donker = np.array(kleur, float) * 0.88
    kl = (licht * (1 - t) + donker * t) if rond == "boven" else (donker * (1 - t) + licht * t)
    kl = np.broadcast_to(kl, (y1 - y0, x1 - x0, 3)).astype(np.uint8)
    blok = Image.fromarray(np.dstack([kl, np.asarray(m)]), "RGBA")
    laag.alpha_composite(blok, (x0, y0))


class Lijn:
    """{"data": json, "logo": png, "onder": "slotkoers in euro", x, y, breed, hoog, start, teken}"""
    def __init__(self, it):
        self.it = it; self.p = koersen(it["data"]); v = [b for _, b in self.p]
        lo, hi = min(v), max(v); stap = [s for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500, 1000, 2000, 2500, 5000, 10000, 20000, 25000, 50000, 100000, 250000, 500000) if (hi - lo) / s <= 5][0]
        self.grid = [g for g in range(int(lo // stap) * stap, int(hi // stap + 2) * stap, stap) if lo - stap * 0.6 <= g <= hi + stap * 0.6]
        self.lo, self.hi = min(self.grid[0], lo) - stap * 0.15, max(self.grid[-1], hi) + stap * 0.15
        self.itop = max(range(len(v)), key=lambda i: v[i]); self.ilaag = min(range(len(v)), key=lambda i: v[i])

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        en = it.get("taal") == "en"; MD = MAAND_EN if en else MAAND
        val = it.get("valuta", "€")
        geld = (lambda v: f"${v:,.0f}") if val == "$" else ((lambda v: f"{v:,.0f}") if val == "" else eur)   # "" = punten (index)
        q = t - it["start"]; w, h = it["breed"], it["hoog"]
        laag, d, m = kaartje(w, h)
        L, R, T, B = m + 40 * S, m + (w - 110) * S, m + 110 * S, m + (h - 60) * S
        lw = logo_op(laag, it["logo"], m + 32 * S, m + 26 * S, it.get("logohoog", 40)) if it.get("logo") else 0
        if it.get("onder"): d.text((m + 32 * S + lw + 18 * S, m + 46 * S), it["onder"], font=f(FS, 24), fill=GRIJS, anchor="lm")
        X = lambda i: L + i / (len(self.p) - 1) * (R - L)
        Y = lambda v: T + (self.hi - v) / (self.hi - self.lo) * (B - T)
        for g in self.grid:                                       # hulplijnen met bedrag rechts
            y = Y(g)
            for xs in range(int(L), int(R), 18 * S): d.line((xs, y, min(xs + 9 * S, R), y), fill=RAND, width=2 * S)
            d.text((R + 12 * S, y), geld(g), font=f(FS, 20), fill=GRIJS, anchor="lm")
        gezien = set(); jaren = it.get("jaren")                    # 22 nov: "jaren": n -> elk n-de jaar onderaan (lange grafiek)
        for i, (dag, _) in enumerate(self.p):
            if jaren:
                if dag.year not in gezien and dag.month == 1 and dag.year % jaren == 0:
                    gezien.add(dag.year); d.text((X(i), B + 26 * S), str(dag.year), font=f(FS, 20), fill=GRIJS, anchor="mm")
                continue
            sl = (dag.year, dag.month)                                  # 22 nov: per jaar+maand, en nooit te dicht op elkaar
            if sl not in gezien and dag.day <= 7:                       # maanden onderaan
                gezien.add(sl)
                if X(i) - getattr(self, "_vorige_x", -1e9) >= 70 * S:
                    label = MD[dag.month - 1] + (f" {str(dag.year)[2:]}" if dag.month == 1 else "")
                    d.text((X(i), B + 26 * S), label, font=f(FS, 20), fill=GRIJS, anchor="mm"); self._vorige_x = X(i)
        self._vorige_x = -1e9
        p = ease((q - 0.3) / it.get("teken", 3.0)) if q > 0.3 else 0
        n = max(2, int(len(self.p) * p))
        if p > 0:
            pts = [(X(i), Y(v)) for i, (_, v) in enumerate(self.p[:n])]
            vlak = Image.new("RGBA", laag.size, (0, 0, 0, 0))
            ImageDraw.Draw(vlak).polygon(pts + [(pts[-1][0], B), (pts[0][0], B)], fill=ROOD + (38,))
            laag.alpha_composite(vlak)
            d = ImageDraw.Draw(laag)
            d.line(pts, fill=ROOD, width=5 * S, joint="curve")
            if p < 1:
                cx, cy = pts[-1]; d.ellipse((cx - 8 * S, cy - 8 * S, cx + 8 * S, cy + 8 * S), fill=INKT)
        for i, naam, kl in ((self.itop, "Top", INKT), (self.ilaag, ("Now" if en else "Nu") if self.ilaag == len(self.p) - 1 else ("Low" if en else "Laagste"), ROOD)):
            if n - 1 >= i:
                cx, cy = X(i), Y(self.p[i][1]); dag = self.p[i][0]
                d.ellipse((cx - 11 * S, cy - 11 * S, cx + 11 * S, cy + 11 * S), fill=(255, 255, 255), outline=kl, width=5 * S)
                tekst = f"{naam} {geld(self.p[i][1])} · " + (f"{MD[dag.month - 1]} {dag.day}" if en else f"{dag.day} {MD[dag.month - 1]}") + (f", {dag.year}" if jaren else "")
                boven = cy - T > 60 * S
                links = cx > (L + R) / 2
                if naam == "Top" and not boven:                       # weinig ruimte boven: pilletje naast de top
                    pil(d, (cx + (-22 * S if links else 22 * S), cy), tekst, 24, kl, anker="rm" if links else "lm")
                elif naam != "Top" and cy + 70 * S > B:                # laagste dicht bij de onderkant: ernaast
                    pil(d, (cx + (-22 * S if links else 22 * S), cy), tekst, 24, kl, anker="rm" if links else "lm")
                else:
                    pil(d, (cx + (-20 * S if links else 20 * S), cy - 44 * S if boven else cy + 44 * S), tekst, 24, kl, anker="rm" if links else "lm")
        plak(doek, laag, it["x"] - m // S, it["y"] - m // S, alpha=ease(q / 0.3))


class Balken:
    """{"balken": [[naam, waarde, label], ...], "logo", "onder", x, y, breed, hoog, start, starts}"""
    KLEUREN = [BLAUW, GROEN, (240, 150, 30), ROOD]

    def __init__(self, it): self.it = it

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        q = t - it["start"]; w, h = it["breed"], it["hoog"]
        laag, d, m = kaartje(w, h)
        lw = logo_op(laag, it["logo"], m + 32 * S, m + 26 * S, it.get("logohoog", 40)) if it.get("logo") else 0
        if it.get("onder"): d.text((m + 32 * S + lw + 18 * S, m + 46 * S), it["onder"], font=f(FS, 24), fill=GRIJS, anchor="lm")
        L, R, T, B = m + 50 * S, m + (w - 50) * S, m + 150 * S, m + (h - 70) * S
        d.line((L, B, R, B), fill=RAND, width=3 * S)
        bs = it["balken"]; mx = max(b[1] for b in bs); n = len(bs); slot = (R - L) / n; bw = slot * 0.5
        for k, (naam, v, label) in enumerate(bs):
            st = it.get("starts", [it["start"] + 0.3 + k * 0.7] * n)[k]
            cx = L + slot * (k + 0.5)
            d.text((cx, B + 32 * S), naam, font=f(FB, 26), fill=INKT, anchor="mm")
            if t < st: continue
            g = ease((t - st) / 0.8); top = B - (B - T) * v / mx * g
            staaf(laag, (cx - bw / 2, top, cx + bw / 2, B), self.KLEUREN[k % 4]); d = ImageDraw.Draw(laag)
            if g > 0.95: pil(d, (cx, top - 30 * S), label, 26, INKT)
        plak(doek, laag, it["x"] - m // S, it["y"] - m // S, alpha=ease(q / 0.3))


class Dagen:
    """{"dagen": json, "n": 7, "logo", "onder", x, y, breed, hoog, start, per}: dagelijkse verandering in % (slot op slot)"""
    def __init__(self, it):
        self.it = it; p = koersen(it["dagen"]); n = it.get("n", 7)
        self.d = [(p[i][0], (p[i][1] / p[i - 1][1] - 1) * 100) for i in range(len(p) - n, len(p))]

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        q = t - it["start"]; w, h = it["breed"], it["hoog"]
        laag, d, m = kaartje(w, h)
        lw = logo_op(laag, it["logo"], m + 32 * S, m + 26 * S, it.get("logohoog", 34)) if it.get("logo") else 0
        if it.get("onder"): d.text((m + 32 * S + lw + 18 * S, m + 44 * S), it["onder"], font=f(FS, 24), fill=GRIJS, anchor="lm")
        L, R, Z, B = m + 36 * S, m + (w - 36) * S, m + 140 * S, m + (h - 60) * S
        d.line((L, Z, R, Z), fill=INKT, width=3 * S)
        mx = max(abs(v) for _, v in self.d); n = len(self.d); slot = (R - L) / n; bw = slot * 0.62
        for k, (dag, v) in enumerate(self.d):
            cx = L + slot * (k + 0.5)
            en = it.get("taal") == "en"                              # 22 nov: Engels (Market Doodle): "Nov 20", "-14.0%"
            d.text((cx, Z - 24 * S), f"{MAAND_EN[dag.month - 1]} {dag.day}" if en else f"{dag.day} {MAAND[dag.month - 1]}", font=f(FS, 20), fill=GRIJS, anchor="mm")
            st = it["start"] + 0.3 + k * it.get("per", 0.35)
            if t < st: continue
            g = ease((t - st) / 0.4); bh = (B - Z - 50 * S) * abs(v) / mx * g
            laatste = k == n - 1
            staaf(laag, (cx - bw / 2, Z + 2 * S, cx + bw / 2, Z + 2 * S + bh), (176, 24, 24) if laatste else ROOD, rond="onder")
            d = ImageDraw.Draw(laag)
            if g > 0.95:
                tekst = f"{v:+.1f}%".replace("-", "−") if en else f"{v:+.1f}%".replace(".", ",").replace("-", "−")
                if laatste: pil(d, (cx, Z + bh + 34 * S), tekst, 26, (176, 24, 24))
                else: d.text((cx, Z + bh + 24 * S), tekst, font=f(FB, 22), fill=ROOD, anchor="mm")
        plak(doek, laag, it["x"] - m // S, it["y"] - m // S, alpha=ease(q / 0.3))


class Logo:
    """{"logo": png, x, y, hoog, start}: logo veegt van links naar rechts in beeld"""
    def __init__(self, it):
        self.it = it; self.laag = Image.new("RGBA", (1, 1)); lg = Image.new("RGBA", (4000, int(it["hoog"] * S) + 4), (0, 0, 0, 0))
        w = logo_op(lg, it["logo"], 0, 0, it["hoog"]); self.laag = lg.crop((0, 0, w, lg.height))

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        p = ease((t - it["start"]) / 0.6); la = self.laag.copy()
        a = np.asarray(la).copy(); a[:, int(la.width * p):, 3] = 0
        plak(doek, Image.fromarray(a), it["x"], it["y"])
