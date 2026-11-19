"""BlackSwanVault video 1 (Nvidia): beeld per scene uit zinnen.json, met Wan-clips (clips/clips/*.mp4), echte vrije foto's
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
Z = json.load(open(H / "zinnen.json", encoding="utf-8"))
SCENES = []
for s, e, z, sc in Z:
    if not SCENES or SCENES[-1][0] != sc: SCENES.append([sc, s, e, [z]])
    else: SCENES[-1][2] = e; SCENES[-1][3].append(z)
EIND = Z[-1][1] + 1.8
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
_vinfo = json.load(open(H / "echt/video/info.json", encoding="utf-8"))
def vcredit(naam):
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
for r in (H / "foto/bronnen.tsv").read_text(encoding="utf-8").splitlines():
    f, t, a, lic, u = r.split("\t"); CRED[Path(f).stem] = f"Photo: {a} / {lic} / Wikimedia Commons"
for r in (H / "echt/bronnen.tsv").read_text(encoding="utf-8").splitlines():
    f, t, a, lic, u = r.split("\t"); CRED[f] = f"Photo: {a or 'unknown'} / {lic} / Wikimedia Commons"
_foto = {}
def foto(nr, t, dur, zoom=(1.0, 1.1), pan=(0.5, 0.5, 0.5, 0.5), grijs=False, donker=0.6, crop=None):
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
_k = json.load(open(H / "data/nvda.json"))["chart"]["result"][0]
KOERS = [(D.datetime.fromtimestamp(t, D.UTC).date(), v) for t, v in zip(_k["timestamp"], _k["indicators"]["quote"][0]["close"]) if v]
def koers(van, tot): return [(d, v) for d, v in KOERS if D.date.fromisoformat(van) <= d <= D.date.fromisoformat(tot)]

def lijn(t, dur, van, tot, titel, sub, markers=(), log=False, kleur=ROOD, eind_label=True, teken=0.75):
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
        txt(d, (X0 - 20, y), f"${v:,.0f}", font(REG, 24), GRIJS, 1, "rm")
    for i in range(0, len(pts), max(1, len(pts) // 6)):
        x, _ = xy(i, pts[i][1]); txt(d, (x, Y0 + 30), pts[i][0].strftime("%b %d" if len(pts) < 60 else "%b %Y"), font(REG, 24), GRIJS, 1, "ma")
    p = eio(t / (dur * teken)); n = max(2, int(len(pts) * p))
    xys = [xy(i, pts[i][1]) for i in range(n)]
    # vlak onder de lijn
    poly = xys + [(xys[-1][0], Y0), (xys[0][0], Y0)]
    d.polygon(poly, fill=kleur + (38,)); d.line(xys, fill=kleur + (255,), width=6, joint="curve")
    x, y = xys[-1]; d.ellipse([x - 11, y - 11, x + 11, y + 11], fill=kleur + (255,))
    if eind_label: txt(d, (x + 20, y - 30), f"${pts[n - 1][1]:,.2f}", font(BOLD, 36), WIT, 1)
    for datum, label in markers:
        i = next((k for k, (dd, _) in enumerate(pts) if str(dd) >= datum), None)
        if i is None or i >= n: continue
        mx, my = xy(i, pts[i][1]); a = ease((n - i) / 8)
        d.line([(mx, my - 18), (mx, Y1 - 30)], fill=(255, 255, 255, int(90 * a)), width=2)
        txt(d, (mx, Y1 - 40), label, font(BOLD, 26), WIT, a, "ms")
    bron(img, "Source: Nvidia closing prices (NASDAQ: NVDA), adjusted for splits, via Yahoo Finance")
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

# ---------- scenes ----------
def S(naam, t, dur):
    g = globals()
    if naam == "open-capitol":
        img = clip("capitol", t, dur); stempel(img, t - 0.3, "NOVEMBER 12, 2026"); return img
    if naam == "open-huang":
        img = foto("gtc-a", t, dur, (1.0, 1.08)); lower_third(img, t - 0.3, "JENSEN HUANG", "Co-founder and CEO of Nvidia, 1993 to 2026")
        if t > zin_t(naam, 1): onder(img, t - zin_t(naam, 1), "The man who sold the shovels in the AI gold rush")
        return img
    if naam in ("open-koers", "h5-koers"):
        img, (a, b) = lijn(t, dur, "2026-10-20", "2026-11-18", "NVIDIA STOCK", "Daily closing price, October 20 to November 18, 2026",
                           markers=[("2026-10-29", "First report"), ("2026-11-08", "Letter"), ("2026-11-12", "Resigns"), ("2026-11-17", "Earnings")])
        if t > dur * 0.6:
            d = ImageDraw.Draw(img, "RGBA"); txt(d, (1700, 330), "-29%", font(BLACK, 150), ROOD, ease((t - dur * 0.6) / 0.4), "rm")
            txt(d, (1700, 420), "Oct 29 to Nov 18", font(REG, 30), GRIJS, ease((t - dur * 0.6) / 0.4), "rm")
        return img
    if naam == "open-datacenter":
        img = clip("datacenter", t, dur); t0 = zin_t(naam, 2)
        if t > t0:
            teller(img, t, 115.8, lambda v: f"${v:.1f}B", HH // 2 - 30, 190, GROEN, 1.6, t0)
            caption(img, t, ["", "revenue in one quarter"], y=HH // 2 + 60, start=t0 + 0.6)
        else: caption(img, t, ["Five days later..."], start=zin_t(naam, 1))
        return img
    if naam == "open-vraag":
        img = clip("boardroom", t, dur, donker=0.45)
        regels = ["A record quarter.", "A crashing stock.", "A founder gone."]
        d = ImageDraw.Draw(img, "RGBA")
        for k, r in enumerate(regels):
            a = ease((t - 0.3 - k * 0.9) / 0.4); txt(d, (W // 2, 380 + k * 120), r, font(BLACK, 86), ROOD if k == 1 else WIT, a, "mm")
        return img
    if naam == "open-dennys":
        img = clip("diner", t, dur); stempel(img, t - 0.4, "SAN JOSE, CALIFORNIA, 1993", DONKER); return img
    if naam == "titel":
        img = clip("swan", t, dur, donker=0.45); d = ImageDraw.Draw(img, "RGBA")
        a = ease(t / 0.8); txt(d, (W // 2, 520), "THE MAN WHO", font(BOLD, 64), GRIJS, a, "mm")
        txt(d, (W // 2, 620), "BUILT NVIDIA", font(BLACK, 150), WIT, ease((t - 0.4) / 0.8), "mm")
        logo_klein(img, ease((t - 0.8) / 0.6)); return img
    for nr, (h, titel, cl) in enumerate([("h1", "A booth at Denny's", "diner"), ("h2", "The bet", "circuit"), ("h3", "The gold rush", "stage"),
                                         ("h4", "The China problem", "port"), ("h5", "November", "press"),
                                         ("h6", "The strangest earnings", "datacenter"), ("h7", "What happens next", "wallstreet")], 1):
        if naam == h: return hoofdstuk(cl, nr, titel, t, dur)
    if naam == "h1-taiwan":
        img = clip("taipei", t, dur); onder(img, t, "Born in Taiwan, 1963")
        if t > zin_t(naam, 2): stempel(img, t - zin_t(naam, 2), "OREGON STATE  /  STANFORD  /  AMD  /  LSI LOGIC", DONKER)
        return img
    if naam == "h1-booth":
        img = clip("diner", t, dur, donker=0.5); d = ImageDraw.Draw(img, "RGBA")
        for k, (n, r) in enumerate([("JENSEN HUANG", "30, chip designer"), ("CHRIS MALACHOWSKY", "engineer"), ("CURTIS PRIEM", "engineer")]):
            a = ease((t - 0.5 - k * 0.6) / 0.5); x = 360 + k * 600
            d.rectangle([x - 250, 380, x + 250, 560], fill=(0, 0, 0, int(150 * a)), outline=(255, 255, 255, int(60 * a)))
            txt(d, (x, 445), n, font(BOLD, 40), WIT, a, "mm"); txt(d, (x, 505), r, font(REG, 30), GRIJS, a, "mm")
        if t > zin_t(naam, 1): onder(img, t - zin_t(naam, 1), "One idea: a chip made only for 3D graphics", 0)
        stempel(img, t - 0.2, "APRIL 1993", DONKER); return img
    if naam == "h1-concurrentie":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA"); weg = ease((t - zin_t(naam, 1)) / 2.5)
        txt(d, (W // 2, 150), "3D GRAPHICS CHIP COMPANIES, 1990s", font(BOLD, 44), WIT, ease(t / 0.4), "mm")
        rng = np.random.default_rng(4)
        for i in range(48):
            x = 330 + (i % 12) * 105; y = 330 + (i // 12) * 130; nv = i == 17
            a = ease((t - i * 0.03) / 0.3); al = a * (1 if nv else max(0.0, 1 - weg * (0.6 + rng.random())))
            d.rounded_rectangle([x, y, x + 80, y + 80], 12, fill=(GROEN if nv and weg > 0.5 else (70, 72, 80)) + (int(255 * al),))
        if t > zin_t(naam, 2): txt(d, (W // 2, 930), "Most of them would not survive.", font(BOLD, 48), WIT, ease((t - zin_t(naam, 2)) / 0.4), "mm")
        return img
    if naam == "h1-flop":
        img = clip("office", t, dur); stempel(img, t - 0.2, "1995: NV1", DONKER)
        caption(img, t, ["A flop.", "The money was running out"], start=0.4); return img
    if naam == "h1-riva":
        img = clip("chip", t, dur); stempel(img, t - 0.2, "1997: RIVA 128", GROEN)
        teller(img, t, 1_000_000, lambda v: f"{v:,.0f}", HH // 2 - 20, 150, WIT, 1.6, zin_t(naam, 1))
        caption(img, t, ["", "units in four months"], y=HH // 2 + 60, start=zin_t(naam, 1) + 0.5)
        if t > zin_t(naam, 3): onder(img, t - zin_t(naam, 3), "\u201CThirty days from going out of business\u201D", 0)
        return img
    if naam == "h1-geforce":
        img = clip("retro", t, dur); stempel(img, t - 0.2, "1999: NVIDIA GOES PUBLIC", DONKER)
        if t > zin_t(naam, 0) + 3: lower_third(img, t - zin_t(naam, 0) - 3, "GEFORCE 256", "Marketed as \u201Cthe world's first GPU\u201D")
        return img
    if naam == "h2-idee":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (480, 210), "CPU", font(BLACK, 70), WIT, ease(t / 0.4), "mm"); txt(d, (480, 270), "a few powerful cores", font(REG, 30), GRIJS, ease(t / 0.4), "mm")
        txt(d, (1400, 210), "GPU", font(BLACK, 70), GROEN, ease((t - 0.6) / 0.4), "mm"); txt(d, (1400, 270), "thousands of small cores", font(REG, 30), GRIJS, ease((t - 0.6) / 0.4), "mm")
        for i in range(4):
            x = 330 + (i % 2) * 160; y = 380 + (i // 2) * 160; a = ease((t - 0.3 - i * 0.15) / 0.3)
            d.rounded_rectangle([x, y, x + 140, y + 140], 10, fill=(90, 92, 100, int(255 * a)))
        rng = np.random.default_rng(1)
        for i in range(24 * 14):
            x = 1080 + (i % 24) * 27; y = 360 + (i // 24) * 27; a = ease((t - 0.8 - i * 0.004) / 0.3)
            aan = 0.5 + 0.5 * math.sin(t * 6 + rng.random() * 6) if t > zin_t(naam, 1) else 0.3
            c = tuple(int(70 + (cc - 70) * aan) for cc in GROEN)
            d.rectangle([x, y, x + 22, y + 22], fill=c + (int(255 * a),))
        if t > zin_t(naam, 2): txt(d, (W // 2, 930), "What if it could do more than draw pictures?", font(BOLD, 50), WIT, ease((t - zin_t(naam, 2)) / 0.4), "mm")
        return img
    if naam == "h2-cuda":
        img = clip("lab", t, dur); stempel(img, t - 0.2, "2006: CUDA", GROEN)
        if t > zin_t(naam, 1): caption(img, t - zin_t(naam, 1), ["Wall Street didn't get it.", "Expensive to build, almost no money for years"])
        return img
    if naam == "h2-alexnet":
        img = clip("lab", t, dur, zoom=(1.08, 1.0)); stempel(img, t - 0.2, "2012: ALEXNET", DONKER)
        if t > zin_t(naam, 1): lower_third(img, t - zin_t(naam, 1), "KRIZHEVSKY  \u00B7  SUTSKEVER  \u00B7  HINTON", "University of Toronto, trained on two Nvidia gaming cards")
        if t > zin_t(naam, 3): caption(img, t - zin_t(naam, 3), ["Hinton: Nobel Prize, 2024", "Sutskever: co-founder of OpenAI"], y=420)
        return img
    if naam == "h2-openai":
        img = clip("sfskyline", t, dur); stempel(img, t - 0.2, "2016: DGX-1", GROEN)
        if t > zin_t(naam, 1): caption(img, t - zin_t(naam, 1), ["OpenAI"], size=150)
        return img
    if naam == "h3-chatgpt":
        img = clip("sfskyline", t, dur, donker=0.45); stempel(img, t - 0.2, "NOVEMBER 30, 2022", ROOD)
        teller(img, t, 100_000_000, lambda v: f"{v:,.0f}", HH // 2 - 20, 140, WIT, 2.0, zin_t(naam, 1))
        caption(img, t, ["", "users in about two months (estimated)"], y=HH // 2 + 70, start=zin_t(naam, 1) + 0.6); return img
    if naam == "h3-iedereen":
        img = clip("datacenter", t, dur, donker=0.5); d = ImageDraw.Draw(img, "RGBA")
        for k, n in enumerate(["MICROSOFT", "GOOGLE", "META", "AMAZON"]):
            a = ease((t - zin_t(naam, 1) - k * 0.35) / 0.35); txt(d, (W // 2, 300 + k * 110), n, font(BLACK, 80), WIT, a, "mm")
        if t > zin_t(naam, 3): onder(img, t - zin_t(naam, 3), "All needed the same thing: Nvidia chips", 0)
        if t > zin_t(naam, 4):
            img = clip("chip", t, dur); caption(img, t - zin_t(naam, 4), ["Months-long waiting lists", "Nvidia chips became a currency of their own"])
        return img
    if naam == "h3-omzet":
        return staven(t, dur, ["FY2023", "FY2024", "FY2025", "FY2026"], [27.0, 60.9, 130.5, 215.9], "NVIDIA ANNUAL REVENUE",
                      "Fiscal years, in billions of US dollars", lambda v: f"${v:.1f}B", "Source: Nvidia annual reports (SEC filings)",
                      stap=None if True else 0, kleur=GROEN, schaal=230)
    if naam == "h3-marge":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA"); p = ease((t - 0.6) / 1.2)
        txt(d, (W // 2, 260), "EVERY $1 OF SALES", font(BOLD, 50), WIT, ease(t / 0.4), "mm")
        d.rectangle([360, 420, 1560, 600], outline=(255, 255, 255, 80), width=3)
        d.rectangle([360, 420, 360 + 1200 * 0.71 * p, 600], fill=GROEN + (255,))
        txt(d, (360 + 1200 * 0.71 * p / 2, 510), "~71\u00A2 gross profit", font(BOLD, 44), (10, 10, 10), min(1, p * 2), "mm")
        txt(d, (1560 - 1200 * 0.29 / 2, 510), "cost", font(REG, 40), GRIJS, p, "mm")
        bron(img, "Source: Nvidia Q4 FY2027 outlook, gross margin 71-72% (8-K, Nov 17, 2026)"); return img
    if naam == "h3-koers":
        img, _ = lijn(t, dur, "2022-11-01", "2026-10-31", "NVIDIA STOCK SINCE CHATGPT", "Weekly view of daily closes, adjusted for splits",
                      markers=[("2022-11-30", "ChatGPT"), ("2025-07-09", "$4T"), ("2025-10-29", "$5T"), ("2026-10-06", "Peak $239")], kleur=GROEN, teken=0.8)
        return img
    if naam == "h3-biljoen":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 150), "NVIDIA MARKET VALUE MILESTONES", font(BOLD, 46), WIT, ease(t / 0.4), "mm")
        stappen = [("2023", 1, 0), ("JULY 2025", 4, 1), ("OCT 2025", 5, 2)]
        for k, (j, v, zi) in enumerate(stappen):
            st = zin_t(naam, zi) + 0.3; a = ease((t - st) / 0.6); x = 420 + k * 540; h = 110 * v * a
            d.rectangle([x - 120, 880 - h, x + 120, 880], fill=(GROEN if k < 2 else ROOD) + (255,))
            txt(d, (x, 860 - h), f"${v} TRILLION", font(BLACK, 54), WIT, a, "ms"); txt(d, (x, 905), j, font(REG, 32), GRIJS, a, "ma")
        if t > zin_t(naam, 1) + 2: txt(d, (W // 2, 230), "First company in history worth $4 trillion", font(REG, 34), GRIJS, ease((t - zin_t(naam, 1) - 2) / 0.5), "mm")
        return img
    if naam == "h3-ster":
        if t < zin_t(naam, 2):
            img = foto("huang-c" if t < zin_t(naam, 1) else "huang-b", t, dur, (1.05, 1.15)); onder(img, t, "A CEO treated like a rock star", 0.4); return img
        img = clip("stage", t, dur); d = ImageDraw.Draw(img, "RGBA"); t2 = t - zin_t(naam, 3)
        for k, n in enumerate(["HOPPER", "BLACKWELL", "VERA RUBIN"]):
            a = ease((t2 - k * 0.5) / 0.4); txt(d, (420 + k * 540, HH // 2), n, font(BLACK, 72), GROEN if k == 2 else WIT, a, "mm")
            if k < 2: txt(d, (690 + k * 540, HH // 2), "\u2192", font(BOLD, 60), GRIJS, a, "mm")
        return img
    if naam == "h3-maar":
        img = leeg(); d = ImageDraw.Draw(img, "RGBA")
        if t > zin_t(naam, 1): txt(d, (W // 2, HH // 2), "CHINA", font(BLACK, 260), ROOD, ease((t - zin_t(naam, 1)) / 0.3), "mm")
        else: txt(d, (W // 2, HH // 2), "One market Nvidia could never control...", font(LIGHT, 60), WIT, ease(t / 0.5), "mm")
        return img
    if naam == "h4-regels":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA"); a = ease(t / 0.5)
        for x, n, k in ((520, "USA", WIT), (1400, "CHINA", ROOD)):
            d.ellipse([x - 170, 370, x + 170, 710], outline=k + (int(255 * a),), width=6); txt(d, (x, 540), n, font(BLACK, 72), k, a, "mm")
        p = ease((t - 0.8) / 1.0); d.line([(700, 540), (700 + 520 * p, 540)], fill=(255, 255, 255, 200), width=8)
        if p > 0.95: d.polygon([(1220, 520), (1220, 560), (1250, 540)], fill=(255, 255, 255, 220))
        if t > zin_t(naam, 1):
            b = ease((t - zin_t(naam, 1)) / 0.4); d.rectangle([945, 420, 975, 660], fill=ROOD + (int(255 * b),))
            txt(d, (960, 360), "EXPORT LIMITS SINCE 2022", font(BOLD, 36), WIT, b, "mm")
        return img
    if naam == "h4-h20":
        img = clip("chip", t, dur, donker=0.5); d = ImageDraw.Draw(img, "RGBA")
        for k, (n, s, c) in enumerate([("TOP AI CHIPS", "Banned for China", ROOD), ("H20", "Weaker version, made for China", GROEN)]):
            a = ease((t - 0.3 - k * 1.2) / 0.5); x = 560 + k * 800
            d.rectangle([x - 320, 380, x + 320, 640], fill=(0, 0, 0, int(170 * a)), outline=c + (int(255 * a),), width=4)
            txt(d, (x, 470), n, font(BLACK, 64), c, a, "mm"); txt(d, (x, 560), s, font(REG, 34), WIT, a, "mm")
        if t > zin_t(naam, 1): onder(img, t - zin_t(naam, 1), "Security for Washington. Billions for Nvidia.", 0)
        return img
    if naam == "h4-h200":
        img = clip("capitol", t, dur, zoom=(1.1, 1.18)); stempel(img, t - 0.2, "DECEMBER 2025", DONKER)
        caption(img, t, ["H200 allowed for China", "President Trump"], start=0.5); return img
    if naam == "h4-megaspeed":
        img = clip("port", t, dur, donker=0.5); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 300), "MEGASPEED", font(BLACK, 110), WIT, ease(t / 0.5), "mm")
        txt(d, (W // 2, 380), "AI computing centers in Asia", font(REG, 36), GRIJS, ease(t / 0.5), "mm")
        if t > zin_t(naam, 1) + 1.5:
            teller(img, t, 4.8, lambda v: f"${v:.1f} BILLION", 600, 120, GROEN, 1.4, zin_t(naam, 1) + 1.5)
            txt(d, (W // 2, 700), "of Nvidia equipment, according to The New York Times", font(REG, 34), GRIJS, ease((t - zin_t(naam, 1) - 2) / 0.5), "mm")
            tag(img, t - zin_t(naam, 1) - 1.5, "REPORTED", 150, 860)
        return img
    if naam == "h4-onderzoek":
        img = clip("office", t, dur, donker=0.45); d = ImageDraw.Draw(img, "RGBA")
        for k, n in enumerate(["UNITED STATES", "SINGAPORE"]):
            a = ease((t - 0.3 - k * 0.5) / 0.4); txt(d, (W // 2, 300 + k * 100), n, font(BLACK, 76), WIT, a, "mm")
        txt(d, (W // 2, 480), "investigating possible export violations (Oct 2025)", font(REG, 34), GRIJS, ease((t - 1.2) / 0.4), "mm")
        if t > zin_t(naam, 1): txt(d, (W // 2, 640), "Huang: dealings were \u201Ccompletely normal\u201D", font(ITAL, 48), WIT, ease((t - zin_t(naam, 1)) / 0.4), "mm")
        if t > zin_t(naam, 2): txt(d, (W // 2, 740), "Nvidia: \u201Cno reason to believe products had been diverted\u201D", font(ITAL, 40), GRIJS, ease((t - zin_t(naam, 2)) / 0.4), "mm")
        return img
    if naam == "h4-vrouw":
        img = clip("taipei", t, dur, donker=0.4, blur=2)
        caption(img, t, ["A former senior executive at Megaspeed", "who knew Jensen Huang personally"], start=0.3); return img
    if naam == "h5-nyt":
        img = clip("press", t, dur, donker=0.5); stempel(img, t - 0.2, "OCTOBER 29", ROOD)
        caption(img, t, ["The New York Times reports", "a close relationship with the executive"], start=0.4, y=380)
        if t > zin_t(naam, 1): txt(ImageDraw.Draw(img, "RGBA"), (W // 2, 700), "Nvidia: \u201Cnot unusual or unexpected\u201D", font(ITAL, 54), WIT, ease((t - zin_t(naam, 1)) / 0.4), "mm")
        return img
    if naam == "h5-spion":
        img = raster(leeg()); tag(img, t, "REPORTED, NOT PROVEN", 260, 260)
        caption(img, t, ["U.S. intelligence officials believed China", "recruited her to gather information on Huang,",
                         "and possibly to influence Nvidia's chip sales"], y=470, size=60, start=zin_t(naam, 1), stap=0.6, x=260, anchor="lm")
        bron(img, "Source: The New York Times, as reported by AFP and Al Jazeera"); return img
    if naam == "h5-ontkenning":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 420), "China: \u201Cunsubstantiated\u201D", font(BOLD, 80), WIT, ease(t / 0.4), "mm")
        if t > zin_t(naam, 1): txt(d, (W // 2, 580), "NOT PROVEN.  NO CHARGES.", font(BLACK, 90), ROOD, ease((t - zin_t(naam, 1)) / 0.3), "mm")
        return img
    if naam == "h5-congres":
        if t < zin_t(naam, 1):
            img = clip("hearing", t, dur); stempel(img, t - 0.2, "NOVEMBER 5", ROOD)
            caption(img, t, ["Republican committee chairmen", "request a closed-door briefing"], start=0.4); return img
        img, _ = lijn(t - zin_t(naam, 1), dur - zin_t(naam, 1), "2026-11-03", "2026-11-05", "NVIDIA STOCK", "November 3 to 5, 2026", teken=0.4)
        txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-9.3%", font(BLACK, 140), ROOD, ease((t - zin_t(naam, 1) - 1) / 0.4), "rm"); return img
    if naam == "h5-brief":
        achter = foto("hq-entry", t, dur, (1.0, 1.05), donker=0.18)
        img = citaat(t - zin_t(naam, 1), dur, ["I was unfaithful to my wife.", "My actions hurt her and our children."] if t > zin_t(naam, 2) else ["I was unfaithful to my wife."],
                     "Jensen Huang, letter to Nvidia employees, November 8, 2026", achter)
        stempel(img, t - 0.2, "SUNDAY, NOVEMBER 8", DONKER); return img
    if naam == "h5-board":
        img = clip("boardroom", t, dur); stempel(img, t - 0.2, "NVIDIA BOARD", DONKER)
        caption(img, t, ["Independent investigation", "Was Huang targeted by a foreign intelligence service?"], start=0.4)
        if t > zin_t(naam, 2):
            img = clip("capitol", t, dur, zoom=(1.15, 1.22), donker=0.5)
            caption(img, t - zin_t(naam, 2), ["Trump: Huang is \u201Ca fine person\u201D", "and should stay on as CEO"])
        if t > zin_t(naam, 3):
            img, _ = lijn(t - zin_t(naam, 3), dur - zin_t(naam, 3), "2026-11-06", "2026-11-09", "NVIDIA STOCK", "November 6 to 9, 2026", teken=0.4)
            txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-4.3%", font(BLACK, 140), ROOD, ease((t - zin_t(naam, 3) - 1.2) / 0.4), "rm")
        return img
    if naam == "h5-druk":
        img = clip("press", t, dur, donker=0.4); d = ImageDraw.Draw(img, "RGBA")
        for k, (s, r) in enumerate([("More reports", False), ("Talk of a subpoena", False), ("Justice Department takes over the investigation", True)]):
            a = ease((t - zin_t(naam, 1) - k * 1.1) / 0.4); txt(d, (W // 2, 360 + k * 130), s, font(BOLD, 66), WIT, a, "mm")
            if r and a > 0: tag(img, t - zin_t(naam, 1) - k * 1.1, "REPORTED", W // 2 - 90, 640)
        return img
    if naam == "h5-ontslag":
        if t < zin_t(naam, 1):
            img = foto("huang-h", t, dur, (1.05, 1.15), (0.6, 0.45, 0.62, 0.42), grijs=True); stempel(img, t - 0.2, "NOVEMBER 12: RESIGNS", ROOD); return img
        img = clip("campus", t, dur, donker=0.5); t2 = t - zin_t(naam, 1); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 330), "COLETTE KRESS", font(BLACK, 96), WIT, ease(t2 / 0.4), "mm")
        txt(d, (W // 2, 410), "Interim CEO  \u00B7  CFO since 2013", font(REG, 38), GRIJS, ease(t2 / 0.4), "mm")
        if t > zin_t(naam, 4): txt(d, (W // 2, 560), "HARVEY JONES", font(BLACK, 70), WIT, ease((t - zin_t(naam, 4)) / 0.4), "mm"); txt(d, (W // 2, 625), "First chair of the board", font(REG, 34), GRIJS, ease((t - zin_t(naam, 4)) / 0.4), "mm")
        if t > zin_t(naam, 2) and t < zin_t(naam, 4): onder(img, t - zin_t(naam, 2), "Huang agrees to testify before Congress", 0)
        if t > zin_t(naam, 5): onder(img, t - zin_t(naam, 5), "Democrats open their own investigation", 0)
        return img
    if naam == "h6-cijfers":
        img = clip("datacenter", t, dur, donker=0.4); stempel(img, t - 0.2, "NOVEMBER 17", GROEN)
        teller(img, t, 115.8, lambda v: f"${v:.1f}B", HH // 2 - 40, 200, GROEN, 1.8, zin_t(naam, 1))
        if t > zin_t(naam, 2): caption(img, t - zin_t(naam, 2), ["+103% vs. a year earlier"], y=HH // 2 + 110, size=64)
        return img
    if naam == "h6-kwartalen":
        q = [7.2, 13.5, 18.1, 22.1, 26.0, 30.0, 35.1, 39.3, 44.1, 46.7, 57.0, 68.1, 81.6, 96.2, 115.8]
        lab = ["Q1 FY24", "Q2", "Q3", "Q4", "Q1 FY25", "Q2", "Q3", "Q4", "Q1 FY26", "Q2", "Q3", "Q4", "Q1 FY27", "Q2", "Q3"]
        return staven(t, dur, lab, q, "NVIDIA QUARTERLY REVENUE", "In billions of US dollars", lambda v: f"{v:.0f}",
                      "Source: Nvidia quarterly reports (SEC filings); Q1 FY27 derived from six-month total", hl=14, kleur=GROEN, stap=0.22)
    if naam == "h6-datacenter":
        img = clip("datacenter", t, dur, donker=0.45); d = ImageDraw.Draw(img, "RGBA")
        teller(img, t, 107.6, lambda v: f"${v:.1f}B", 330, 150, GROEN, 1.5, 0.2)
        txt(d, (W // 2, 430), "from data center chips alone", font(REG, 38), GRIJS, ease((t - 0.6) / 0.4), "mm")
        if t > zin_t(naam, 1):
            t2 = t - zin_t(naam, 1); txt(d, (W // 2, 620), "NEXT QUARTER: ~$130B", font(BLACK, 80), WIT, ease(t2 / 0.4), "mm")
            txt(d, (W // 2, 700), "with no data center chip sales to China", font(REG, 38), GRIJS, ease((t2 - 0.4) / 0.4), "mm")
        bron(img, "Source: Nvidia 8-K, November 17, 2026"); return img
    if naam == "h6-kress":
        if t < zin_t(naam, 2):
            img = clip("stage", t, dur); caption(img, t, ["No more H200 sales in China", "Colette Kress, interim CEO"], start=0.3); return img
        return citaat(t - zin_t(naam, 2), dur, ["Vera Rubin is off to an explosive start.", "Our roadmap is on track, and our", "ambition has never been greater."],
                      "Colette Kress, interim CEO, November 17, 2026", clip("stage", t, dur, donker=0.2, blur=4))
    if naam == "h6-terug":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (520, 330), "HUANG", font(BLACK, 70), WIT, ease(t / 0.4), "mm")
        txt(d, (520, 440), "\u201CHonored\u201D to return", font(ITAL, 54), WIT, ease((t - 0.4) / 0.4), "mm")
        txt(d, (520, 510), "if the board decides it is best", font(REG, 32), GRIJS, ease((t - 0.6) / 0.4), "mm")
        if t > zin_t(naam, 1):
            t2 = t - zin_t(naam, 1); txt(d, (1400, 330), "THE BOARD", font(BLACK, 70), WIT, ease(t2 / 0.4), "mm")
            txt(d, (1400, 440), "Not considering it", font(BOLD, 54), ROOD, ease((t2 - 0.3) / 0.4), "mm")
        d.line([(W // 2, 280), (W // 2, 560)], fill=(255, 255, 255, 50), width=2); return img
    if naam == "h6-daling":
        img, _ = lijn(t, dur, "2026-11-10", "2026-11-18", "NVIDIA STOCK", "November 10 to 18, 2026", markers=[("2026-11-17", "Record earnings")], teken=0.7)
        if t > zin_t(naam, 1): txt(ImageDraw.Draw(img, "RGBA"), (1700, 330), "-2.9%", font(BLACK, 140), ROOD, ease((t - zin_t(naam, 1)) / 0.4), "rm")
        return img
    if naam == "h7-waarom":
        img = clip("trading", t, dur, donker=0.5)
        if t > zin_t(naam, 1): caption(img, t - zin_t(naam, 1), ["Markets don't pay for the past.", "They pay for the future."])
        if t > zin_t(naam, 3):
            d = ImageDraw.Draw(img, "RGBA")
            for k in range(3): txt(d, (660 + k * 300, 860), "?", font(BLACK, 160), ROOD, ease((t - zin_t(naam, 3) - k * 0.3) / 0.3), "mm")
        return img
    vragen = {"h7-china": (1, "CHINA", "port"), "h7-leider": (2, "LEADERSHIP", "boardroom"), "h7-bubbel": (3, "THE AI BOOM", "datacenter")}
    if naam in vragen:
        nr, titel, cl = vragen[naam]; img = clip(cl, t, dur, donker=0.45); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (200, 230), f"QUESTION {nr}", font(BOLD, 40), ROOD, ease(t / 0.4)); txt(d, (200, 280), titel, font(BLACK, 110), WIT, ease((t - 0.2) / 0.4))
        if naam == "h7-leider" and t > zin_t(naam, 3):
            for k, (a_, b_) in enumerate([("APPLE", "after Steve Jobs"), ("MICROSOFT", "after Bill Gates")]):
                a = ease((t - zin_t(naam, 3) - k * 0.5) / 0.4); txt(d, (200, 520 + k * 120), a_, font(BLACK, 60), WIT, a); txt(d, (620, 540 + k * 120), b_, font(REG, 40), GRIJS, a)
        if naam == "h7-bubbel" and t > zin_t(naam, 3):
            for k, n in enumerate(["AMD", "GOOGLE", "AMAZON", "MICROSOFT"]):
                a = ease((t - zin_t(naam, 3) - k * 0.35) / 0.35); txt(d, (200 + k * 400, 620), n, font(BLACK, 56), WIT, a)
            txt(d, (200, 700), "all building AI chips of their own", font(REG, 38), GRIJS, ease((t - zin_t(naam, 3) - 1.5) / 0.4))
        return img
    if naam == "h7-jij":
        img = raster(leeg()); d = ImageDraw.Draw(img, "RGBA")
        txt(d, (W // 2, 330), "S&P 500", font(BLACK, 130), WIT, ease((t - zin_t(naam, 1)) / 0.4), "mm")
        txt(d, (W // 2, 430), "Nvidia is one of its largest companies", font(REG, 40), GRIJS, ease((t - zin_t(naam, 1) - 0.3) / 0.4), "mm")
        if t > zin_t(naam, 2): txt(d, (W // 2, 620), "Own an index fund? You likely own Nvidia.", font(BOLD, 56), GROEN, ease((t - zin_t(naam, 2)) / 0.4), "mm")
        return img
    if naam == "h7-getuigenis":
        img = clip("hearing", t, dur); stempel(img, t - 0.2, "BEFORE THANKSGIVING", ROOD)
        caption(img, t, ["Jensen Huang testifies before Congress"], start=0.4); return img
    if naam == "slot-zwaan":
        img = clip("swan", t, dur)
        if t > zin_t(naam, 1): caption(img, t - zin_t(naam, 1), ["BLACK SWAN", "an event nobody sees coming, that changes everything"], size=120)
        return img
    if naam == "slot-twee":
        return clip("campus", t, dur, zoom=(1.0, 1.1))
    if naam == "slot-dennys":
        img = clip("diner", t, dur, zoom=(1.12, 1.0)); stempel(img, t - 0.2, "1993", DONKER); return img
    if naam == "slot-abonneer":
        img = clip("swan", t, dur, donker=0.3, blur=3); d = ImageDraw.Draw(img, "RGBA"); logo_klein(img, ease(t / 0.6))
        txt(d, (W // 2, 420), "BLACKSWANVAULT", font(BLACK, 90), WIT, ease((t - 0.3) / 0.5), "mm")
        txt(d, (W // 2, 500), "Subscribe and step inside the vault", font(REG, 40), GRIJS, ease((t - 0.6) / 0.5), "mm")
        if t > dur - 1.0: img = Image.blend(img, Image.new("RGB", (W, HH)), (t - (dur - 1.0)) / 1.0)
        return img
    raise KeyError(naam)

def frame(t):
    for naam, s, e, _ in SCENES:
        if s <= t < e: HUIDIG[0] = naam; return S(naam, t - s, e - s), naam
    return S(SCENES[-1][0], t - SCENES[-1][1], SCENES[-1][2] - SCENES[-1][1]), SCENES[-1][0]

def main():
    van = float(sys.argv[sys.argv.index("--van") + 1]) if "--van" in sys.argv else 0
    tot = float(sys.argv[sys.argv.index("--tot") + 1]) if "--tot" in sys.argv else EIND
    uit = H / ("video-ruw.mp4" if van == 0 and tot == EIND else f"stuk-{van:.0f}-{tot:.0f}.mp4")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{HH}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", str(uit)], stdin=subprocess.PIPE)
    vorige, wissel, laatste, laatste_vorige = None, -1, None, None
    n0, n1 = int(van * FPS), int(tot * FPS)
    for i in range(n0, n1):
        t = i / FPS; img, naam = frame(t)
        if naam != vorige and vorige is not None: wissel = i
        if 0 <= i - wissel < 6 and laatste is not None:          # korte overvloeiing (0,24 s) tussen scenes
            img = Image.blend(laatste_vorige, img, (i - wissel + 1) / 7)
        else: laatste_vorige = img
        laatste = img; vorige = naam
        p.stdin.write(img.tobytes())
        if i % (FPS * 30) == 0: print(f"{t / 60:.1f}/{tot / 60:.1f} min", flush=True)
    p.stdin.close(); p.wait(); print("KLAAR", uit.name)

laatste = None
if __name__ == "__main__":
    if "--plaat" in sys.argv:
        uit = sys.argv[sys.argv.index("--plaat") + 1]; kies = SCENES
        kol = 6; rij = math.ceil(len(kies) / kol)
        s = Image.new("RGB", (kol * 400, rij * 245), (30, 30, 30)); dd = ImageDraw.Draw(s)
        for k, (naam, a, b, _) in enumerate(kies):
            t = min(b - a - 0.1, (b - a) * 0.75)
            HUIDIG[0] = naam; Vid._open.clear(); s.paste(S(naam, t, b - a).resize((400, 225)), ((k % kol) * 400, (k // kol) * 245))
            dd.text(((k % kol) * 400 + 4, (k // kol) * 245 + 226), f"{naam} {a:.0f}s", fill=(255, 255, 0))
        s.save(uit); print("plaat", len(kies))
    else:
        main()
