"""BlackSwanVault video 2 (Anthropic): basis-helpers, gekopieerd van video 1 (goedgekeurde stijl). Oorspronkelijk: video 1 (Nvidia): beeld per scene uit zinnen.json, met Wan-clips (clips/clips/*.mp4), echte vrije foto's
(foto/, credit in beeld), bewegende grafieken uit echte cijfers (SEC-filings; koers Yahoo Finance in data/nvda.json),
tijdlijn, citaatkaarten en hoofdstukkaarten. Schrijft video-ruw.mp4 (zonder geluid) of met --plaat een controleplaat.
Gebruik: python render.py [--plaat uit.jpg] [--van sec --tot sec]"""
import datetime as D, json, math, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

H = Path(__file__).parent
W, HH, FPS = 1920, 1080, 25
F = "C:/Windows/Fonts/"
_fc = {}
def font(n, s):
    if (n, s) not in _fc: _fc[(n, s)] = ImageFont.truetype(F + n, int(s))
    return _fc[(n, s)]
BOLD, REG, LIGHT, ITAL, BLACK = "segoeuib.ttf", "segoeui.ttf", "segoeuil.ttf", "segoeuiz.ttf", "seguibl.ttf"
if not Path(F + BLACK).exists(): BLACK = BOLD
ROOD, GROEN, WIT, GRIJS, DONKER, GOUD, BG = (225, 35, 45), (70, 200, 120), (242, 242, 242), (150, 152, 158), (90, 92, 98), (214, 175, 90), (9, 10, 13)

def ease(x): x = min(max(x, 0.0), 1.0); return 1 - (1 - x) ** 3
def eio(x): x = min(max(x, 0.0), 1.0); return x * x * (3 - 2 * x)

# ---------- tijden ----------
import os
Z = json.load(open(H / os.environ.get("ZINNEN", "zinnen.json"), encoding="utf-8"))
SCENES = []
for s, e, z, sc in Z:
    if not SCENES or SCENES[-1][0] != sc: SCENES.append([sc, s, e, [z]])
    else: SCENES[-1][2] = e; SCENES[-1][3].append(z)
EIND = Z[-1][1] + 3.5   # 19 nov: iets langer uitfaden (boven 8:00)
for i, sc in enumerate(SCENES):                         # scene loopt tot de volgende begint
    sc[1] = 0.0 if i == 0 else sc[1] - 0.15
for i, sc in enumerate(SCENES):
    sc[2] = SCENES[i + 1][1] if i + 1 < len(SCENES) else EIND
def zin_t(scene, k):                                    # starttijd van de k-de zin in een scene (relatief)
    zs = [x for x in Z if x[3] == scene]; s0 = [x for x in SCENES if x[0] == scene][0][1]
    return zs[min(k, len(zs) - 1)][0] - s0

# ---------- beeldbronnen ----------
VIG = None
def vignet(img, k=0.75):
    global VIG
    if VIG is None:
        y, x = np.mgrid[0:HH, 0:W]
        d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - HH / 2) / (HH / 2)) ** 2)
        VIG = np.clip(1 - (d - 0.5) * 0.7, 0.3, 1)[..., None].astype(np.float32)
    a = np.asarray(img).astype(np.float32) * VIG
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))

VBRON = {"rtx": "rtx5090", "huang-praat": "huang-spreekt", "gh": "gracehopper", "qct": "qct", "die": "die", "trump": "trump"}
_vinfo = json.load(open(H / "echt/video/info.json", encoding="utf-8")) if (H / "echt/video/info.json").exists() else {}
def vcredit(naam):
    if naam.startswith("mk-"): return "Video: Mixkit (free licence)"
    k = next(v for p, v in VBRON.items() if naam.startswith(p)); i = _vinfo[k]
    if k == "trump": return "Video: The White House / Public domain"
    return f"Video: {i['artist']} / {i['lic']} / Wikimedia Commons"

class Vid:                                               # echte video (echt/video/naam.mp4), vertraagd, loopt door
    _open = {}
    def __init__(self, naam, speed):
        self.naam, self.speed, self.p, self.t = naam, speed, None, -1
    def _start(self):
        if self.p: self.p.kill()
        self.p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(H / "echt/video" / f"{self.naam}.mp4"), "-vf",
                                   f"setpts=PTS/{self.speed},fps={FPS}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    def frame(self):
        if self.p is None: self._start()
        b = self.p.stdout.read(W * HH * 3)
        if len(b) < W * HH * 3: self._start(); b = self.p.stdout.read(W * HH * 3)
        return Image.frombytes("RGB", (W, HH), b)

_vsleutel = None
def vid(naam, t, dur, donker=0.7, blur=0, speed=0.8, zoom=(1.0, 1.06), sleutel=None):
    global _vsleutel
    k = (naam, sleutel or id(dur) if False else (naam, round(dur, 3)))
    if k not in Vid._open:
        for oud in list(Vid._open.values()):
            if oud.p: oud.p.kill()
        Vid._open.clear(); Vid._open[k] = Vid(naam, speed)
    im = Vid._open[k].frame()
    z = zoom[0] + (zoom[1] - zoom[0]) * eio(t / max(dur, 0.1))
    if z != 1.0:
        cw, ch = W / z, HH / z; im = im.resize((W, HH), Image.BICUBIC, box=((W - cw) / 2, (HH - ch) / 2, (W + cw) / 2, (HH + ch) / 2))
    if blur: im = im.filter(ImageFilter.GaussianBlur(blur))
    im = vignet(ImageEnhance.Brightness(im).enhance(donker))
    ImageDraw.Draw(im).text((W - 26, HH - 22), vcredit(naam), font=font(REG, 19), fill=(170, 170, 170), anchor="rs")
    return im

CRED = {}
for r in (H / "echt/bronnen.tsv").read_text(encoding="utf-8").splitlines():
    f, t, a, lic, u = r.split("\t"); CRED[f] = "Beeld gemaakt met AI" if lic == "AI" else f"Foto: {a or 'onbekend'} / {lic} / Wikimedia Commons"
_foto = {}
def foto(nr, t, dur, zoom=(1.0, 1.1), pan=(0.5, 0.5, 0.5, 0.5), grijs=False, donker=0.6, crop=None):
    if str(nr).startswith("v:"):                         # echte stockvideo (echt/video/<naam>.mp4)
        im = vid(nr[2:], t, dur, donker=donker, zoom=zoom)
        return ImageEnhance.Color(im).enhance(0.15) if grijs else im
    k = (nr, grijs, crop)
    if k not in _foto:
        im = Image.open(H / (f"foto/{nr}.jpg" if str(nr).isdigit() else f"echt/{nr}.jpg")).convert("RGB")
        if crop: im = im.crop(crop)
        sc = max(W * 1.15 / im.width, HH * 1.15 / im.height)
        im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
        if grijs: im = ImageEnhance.Color(im).enhance(0.12)
        _foto[k] = im
    im = _foto[k]; p = eio(t / max(dur, 0.1))
    z = zoom[0] + (zoom[1] - zoom[0]) * p
    cw = min(im.width, im.height * W / HH) / 1.15 / z; ch = cw * HH / W   # ook voor hele brede foto's (Capitool)
    cx = (pan[0] + (pan[2] - pan[0]) * p) * im.width; cy = (pan[1] + (pan[3] - pan[1]) * p) * im.height
    x0 = min(max(cx - cw / 2, 0), im.width - cw); y0 = min(max(cy - ch / 2, 0), im.height - ch)
    out = ImageEnhance.Brightness(im.resize((W, HH), Image.BICUBIC, box=(x0, y0, x0 + cw, y0 + ch))).enhance(donker)
    out = vignet(out); credit(out, nr); return out

def leeg(): return Image.new("RGB", (W, HH), BG)
def raster(img, a=1.0):                               # subtiel raster als achtergrond van grafieken
    d = ImageDraw.Draw(img, "RGBA")
    for x in range(0, W, 80): d.line([(x, 0), (x, HH)], fill=(255, 255, 255, int(7 * a)))
    for y in range(0, HH, 80): d.line([(0, y), (W, y)], fill=(255, 255, 255, int(7 * a)))
    return img


# ---------- echte bronnen per scene (eigenaar 19 nov: "echt beelden ... niet ai", "dit gaat echt over nvidia") ----------
BRON = {
 ("open-capitol","capitol"):"v:huang-praat-a", ("open-datacenter","datacenter"):"v:gh-servers", ("open-vraag","boardroom"):"f:hq-atrium",
 ("open-dennys","diner"):"f:riva-kaart", ("titel","swan"):"v:rtx-donker", ("h1","diner"):"f:riva-chip", ("h1-taiwan","taipei"):"f:huang-g",
 ("h1-booth","diner"):"f:riva-kaart", ("h1-flop","office"):"v:die-a", ("h1-riva","chip"):"f:riva-chip", ("h1-geforce","retro"):"f:geforce-kaart",
 ("h2","circuit"):"v:die-b", ("h2-cuda","lab"):"v:die-c", ("h2-alexnet","lab"):"v:die-b", ("h2-openai","sfskyline"):"f:gtc-b",
 ("h3","stage"):"f:gtc-c", ("h3-chatgpt","sfskyline"):"f:gtc-d", ("h3-iedereen","datacenter"):"v:qct-rek", ("h3-iedereen","chip"):"v:qct-mgx",
 ("h3-ster","stage"):"f:computex-b", ("h4","port"):"f:computex-a", ("h4-h20","chip"):"v:rtx-b", ("h4-h200","capitol"):"v:trump",
 ("h4-megaspeed","port"):"v:gh-rek", ("h4-onderzoek","office"):"f:dc-b", ("h4-vrouw","taipei"):"f:dc-a", ("h5","press"):"f:hq-wall",
 ("h5-nyt","press"):"f:hq-entry", ("h5-board","boardroom"):"f:hq-atrium", ("h5-board","capitol"):"v:trump", ("h5-druk","press"):"f:hq-hq",
 ("h5-ontslag","campus"):"f:hq-entry", ("h5-congres","hearing"):"v:huang-praat-b", ("h6","datacenter"):"f:dc-a",
 ("h6-cijfers","datacenter"):"v:gh-servers", ("h6-datacenter","datacenter"):"v:gh-servers", ("h6-kress","stage"):"v:rtx-c",
 ("h7","wallstreet"):"f:hq-entry", ("h7-waarom","trading"):"f:dc-b", ("h7-china","port"):"f:computex-a", ("h7-leider","boardroom"):"f:huang-a",
 ("h7-bubbel","datacenter"):"v:qct-rek", ("h7-getuigenis","hearing"):"v:huang-praat-b", ("slot-zwaan","swan"):"v:rtx-donker",
 ("slot-twee","campus"):"f:hq-entry", ("slot-dennys","diner"):"f:riva-chip", ("slot-abonneer","swan"):"v:rtx-donker",
}
STANDAARD = {"capitol":"v:huang-praat-a","datacenter":"v:gh-servers","boardroom":"f:hq-atrium","diner":"f:riva-chip","swan":"v:rtx-donker",
 "taipei":"f:huang-g","office":"f:dc-b","chip":"v:rtx-b","retro":"f:geforce-kaart","circuit":"v:die-b","lab":"v:die-c","sfskyline":"f:gtc-b",
 "stage":"f:gtc-c","port":"f:computex-a","press":"f:hq-wall","campus":"f:hq-entry","hearing":"v:huang-praat-b","trading":"f:dc-b","wallstreet":"f:hq-entry"}
HUIDIG = [None]
def clip(naam, t, dur, zoom=(1.0, 1.08), donker=0.72, blur=0, speed=0.8):
    b = BRON.get((HUIDIG[0], naam)) or STANDAARD[naam]
    if b.startswith("v:"): return vid(b[2:], t, dur, donker=donker, blur=blur, speed=speed, zoom=zoom)
    im = foto(b[2:], t, dur, zoom=zoom, donker=donker * 0.85)
    return im.filter(ImageFilter.GaussianBlur(blur)) if blur else im

# ---------- tekst en overlays ----------
_MND = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"]
def nl_datum(dg, n):                                       # Geldverhaal: Nederlandse datums op grafieken
    return f"{dg.day} {_MND[dg.month - 1]}" if n < 200 else f"{_MND[dg.month - 1]} {dg.year}" if n < 1100 else str(dg.year)   # tot ± 4 jaar maand + jaar (anders dubbele jaartallen)
def txt(d, xy, s, f, kleur=WIT, a=1.0, anchor="la"):
    d.text(xy, s, font=f, fill=tuple(kleur) + (int(255 * max(0, min(1, a))),), anchor=anchor)
def credit(img, nr):
    ImageDraw.Draw(img).text((W - 26, HH - 22), CRED[str(nr)], font=font(REG, 19), fill=(170, 170, 170), anchor="rs")
def bron(img, s):
    ImageDraw.Draw(img).text((W - 26, HH - 22), s, font=font(REG, 19), fill=(130, 130, 135), anchor="rs")

def lower_third(img, t, titel, sub, kleur=ROOD):
    d = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.5); x = -650 + 740 * a
    for k in range(50): d.rectangle([0, 720 + k * 7, W, 727 + k * 7], fill=(0, 0, 0, int(150 * a * min(1, k / 22))))
    d.rectangle([x, 815, x + 9, 925], fill=kleur)
    txt(d, (x + 32, 805), titel, font(BOLD, 64), a=a); txt(d, (x + 34, 884), sub, font(REG, 34), GRIJS, a=a)

def stempel(img, t, s, kleur=ROOD, y=96, x=90):
    d = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.4); f = font(BOLD, 40); w = d.textlength(s, font=f)
    d.rectangle([x - 18, y - 12, x - 18 + (w + 36) * a, y + 58], fill=kleur + (235,))
    if a > 0.6: d.text((x, y), s, font=f, fill=(255, 255, 255))

def caption(img, t, regels, y=None, size=58, kleur=WIT, start=0.0, stap=0.45, anchor="mm", x=W // 2):
    d = ImageDraw.Draw(img, "RGBA"); regels = [regels] if isinstance(regels, str) else regels
    y = y or HH // 2 - (len(regels) - 1) * size * 0.65
    for k, r in enumerate(regels):
        a = ease((t - start - k * stap) / 0.45)
        txt(d, (x, y + k * size * 1.3 + 25 * (1 - a)), r, font(BOLD if k == 0 else REG, size if k == 0 else size * 0.72),
            kleur if k == 0 else GRIJS, a, anchor)

def onder(img, t, s, start=0.2):                     # ondertitel-achtige tekst onderin met donkere band
    d = ImageDraw.Draw(img, "RGBA"); a = ease((t - start) / 0.4)
    for k in range(40): d.rectangle([0, 760 + k * 8, W, 768 + k * 8], fill=(0, 0, 0, int(140 * a * min(1, k / 18))))
    txt(d, (W // 2, 925), s, font(BOLD, 52), a=a, anchor="mm")

def tag(img, t, s="REPORTED", x=150, y=150, kleur=(205, 145, 20)):
    d = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.4); f = font(BOLD, 30); w = d.textlength(s, font=f)
    d.rectangle([x, y, x + w + 36, y + 50], fill=kleur + (int(235 * a),)); txt(d, (x + 18, y + 25), s, f, (12, 12, 12), a, "lm")

def teller(img, t, waarde, fmt, y, size, kleur=WIT, dur=1.4, start=0.0, x=W // 2):
    d = ImageDraw.Draw(img, "RGBA"); p = ease((t - start) / dur)
    if t < start: return
    txt(d, (x, y), fmt(waarde * p), font(BLACK, size), kleur, min(1, (t - start) * 3), "mm")

def hoofdstuk(naam, nr, titel, t, dur):
    img = clip(naam, t, dur, donker=0.38, blur=3)
    d = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.6); b = ease((t - 0.35) / 0.6)
    txt(d, (W // 2, 455), f"CHAPTER {nr}", font(BOLD, 38), ROOD, a, "mm")
    d.rectangle([W // 2 - 260 * a, 492, W // 2 + 260 * a, 496], fill=ROOD + (int(255 * a),))
    txt(d, (W // 2, 570), titel.upper(), font(BLACK, 96), WIT, b, "mm")
    if t > dur - 0.4: img = Image.blend(img, leeg(), (t - (dur - 0.4)) / 0.4)
    return img

def citaat(t, dur, regels, wie, achter=None):
    img = achter if achter is not None else raster(leeg())
    d = ImageDraw.Draw(img, "RGBA")
    a = ease(t / 0.5); txt(d, (W // 2, 300), "\u201C", font("georgiab.ttf", 220), ROOD, a, "mm")
    for k, r in enumerate(regels):
        b = ease((t - 0.3 - k * 0.9) / 0.6)
        txt(d, (W // 2, 470 + k * 95), r, font(ITAL, 64), WIT, b, "mm")
    txt(d, (W // 2, 470 + len(regels) * 95 + 40), wie, font(REG, 32), GRIJS, ease((t - 0.8) / 0.6), "mm")
    return img

def logo_klein(img, a=1.0):
    if not hasattr(logo_klein, "im"):
        l = Image.open(H / "logo.png").convert("RGB").resize((150, 150)); logo_klein.im = l
    m = Image.new("L", (150, 150), 0); ImageDraw.Draw(m).ellipse([0, 0, 149, 149], fill=int(255 * a))
    img.paste(logo_klein.im, (W // 2 - 75, 140), m)

# ---------- data ----------
KOERS = []   # video 2: geen dagkoersen; intraday-grafiek staat in render3.py (data/ant-intraday.json)
def koers(van, tot): return [(d, v) for d, v in KOERS if D.date.fromisoformat(van) <= d <= D.date.fromisoformat(tot)]

def lijn(t, dur, van, tot, titel, sub, markers=(), log=False, kleur=ROOD, eind_label=True, teken=0.75, eenheid="$", hoog_laag=True):
    img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
    pts = koers(van, tot); vs = [v for _, v in pts]
    lo, hi = min(vs), max(vs)
    f = (lambda v: math.log(v)) if log else (lambda v: v)
    flo, fhi = f(lo), f(hi); marge = (fhi - flo) * 0.1; flo -= marge; fhi += marge
    X0, X1, Y0, Y1 = 200, 1720, 880, 260
    def xy(i, v): return X0 + (X1 - X0) * i / (len(pts) - 1), Y0 + (Y1 - Y0) * (f(v) - flo) / (fhi - flo)
    txt(d, (200, 110), titel, font(BOLD, 50), a=ease(t / 0.4)); txt(d, (200, 175), sub, font(REG, 30), GRIJS, ease(t / 0.4))
    for k in range(5):                                   # as-labels
        fv = flo + (fhi - flo) * k / 4; v = math.exp(fv) if log else fv; y = Y0 + (Y1 - Y0) * k / 4
        d.line([(X0, y), (X1, y)], fill=(255, 255, 255, 18), width=1)
        txt(d, (X0 - 20, y), f"{eenheid}{v:,.0f}".replace(",", "."), font(REG, 24), GRIJS, 1, "rm")
    for i in range(0, len(pts), max(1, len(pts) // 6)):
        x, _ = xy(i, pts[i][1]); txt(d, (x, Y0 + 30), nl_datum(pts[i][0], len(pts)), font(REG, 24), GRIJS, 1, "ma")
    p = eio(t / (dur * teken)); n = max(2, int(len(pts) * p))
    xys = [xy(i, pts[i][1]) for i in range(n)]
    # vlak onder de lijn
    poly = xys + [(xys[-1][0], Y0), (xys[0][0], Y0)]
    d.polygon(poly, fill=kleur + (38,)); d.line(xys, fill=kleur + (255,), width=6, joint="curve")
    x, y = xys[-1]; d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=kleur + (255,))
    if eind_label: txt(d, (x + 20, y - 30), (f"€{pts[n - 1][1]:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".") if eenheid == "€" else f"${pts[n - 1][1]:,.2f}" if eenheid == "$" else f"{pts[n - 1][1]:,.0f}"), font(BOLD, 36), WIT, 1)
    # eigenaar 21 nov: in elke grafiek de top en het laagste punt laten zien (verschijnt pas als de lijn er is)
    def geld(v):
        if eenheid == "€": return f"€{v:,.0f}".replace(",", ".") if v >= 100 else f"€{v:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
        return f"{eenheid}{v:,.0f}" if v >= 100 else f"{eenheid}{v:,.2f}"
    if hoog_laag:
        ih = max(range(len(pts)), key=lambda i: pts[i][1]); il = min(range(len(pts)), key=lambda i: pts[i][1])
        for i, woord, boven, k in ((ih, "Top", True, GROEN), (il, "Laagste", False, ROOD)):
            if i >= n: continue
            mx, my = xy(i, pts[i][1]); a = ease((n - i) / 6)
            d.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=k + (int(255 * a),), outline=(255, 255, 255, int(255 * a)), width=3)
            ly = my - 34 if boven else my + 34
            ax = "ms" if boven else "ma"
            lx = min(max(mx, X0 + 120), X1 - 120)
            if not boven and my + 34 + 40 > Y0: lx, ly, ax = mx - 24, my, "rm"     # dicht bij de as: links naast de punt
            txt(d, (lx, ly), f"{woord} {geld(pts[i][1])}", font(BOLD, 30), WIT, a, ax)
    for datum, label in markers:
        i = next((k for k, (dd, _) in enumerate(pts) if str(dd) >= datum), None)
        if i is None or i >= n: continue
        mx, my = xy(i, pts[i][1]); a = ease((n - i) / 8)
        d.line([(mx, my - 18), (mx, Y1 - 4)], fill=(255, 255, 255, int(90 * a)), width=2)
        txt(d, (mx, Y1 - 10), label, font(BOLD, 26), WIT, a, "ms")   # niet over de ondertitel (y 175)
    return img, (pts[0][1], pts[n - 1][1])

def staven(t, dur, labels, waarden, titel, sub, fmt, bron_s, hl=None, kleur=GROEN, stap=None, schaal=None):
    img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
    txt(d, (200, 110), titel, font(BOLD, 50), a=ease(t / 0.4)); txt(d, (200, 175), sub, font(REG, 30), GRIJS, ease(t / 0.4))
    n = len(waarden); X0, X1, Y0, Yt = 220, 1720, 900, 300
    bw = (X1 - X0) / n * 0.68; mx = schaal or max(waarden)
    stap = stap or (dur * 0.7 / n)
    for i, (lab, v) in enumerate(zip(labels, waarden)):
        p = ease((t - 0.3 - i * stap) / 0.7)
        x = X0 + (X1 - X0) * (i + 0.16) / n; h = (Y0 - Yt) * v / mx * p
        k = ROOD if hl is not None and i == hl else kleur
        if i != hl and hl is not None: k = tuple(int(c * 0.55) for c in kleur)
        if p > 0:
            d.rectangle([x, Y0 - h, x + bw, Y0], fill=k + (255,))
            txt(d, (x + bw / 2, Y0 - h - 12), fmt(v * p), font(BOLD, 30 if n < 9 else 22), WIT, min(1, p * 2), "ms")
        txt(d, (x + bw / 2, Y0 + 22), lab, font(REG, 28 if n < 9 else 20), GRIJS, 1, "ma")
    bron(img, bron_s); return img

