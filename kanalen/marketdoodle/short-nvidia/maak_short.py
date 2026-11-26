"""Short 'What If You Invested $100 in NVIDIA?' (26 nov 2026), staand 1080x1920. Echt verhaal (Denny's 1993, NV1, Sega, beursgang 1999, AI),
elke scène eigen personages met eigen stem (eigenaar 26 nov). Zelfde controles als de Black Friday-Short.
Gebruik: <omnivoice-venv>/python maak_short.py [--plaat]  -> short-nvidia.mp4"""
import json, math, os, re, subprocess, sys, difflib
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageChops
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools"))
from scenewachter import Scenewachter

W, H, FPS, SS = 1080, 1920, 30, ps.SS
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
INK = (40, 35, 40)
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def _script_woorden():                                   # woorden van het script (goede spelling) met Whisper-tijden
    uit = []
    for i, z in enumerate(Z):
        sw = z[2].replace('"', "").split(); ww = [w for w in WO if w[0] == i] or [[i, z[2], z[0], z[1]]]
        t0s, t1s = [None] * len(sw), [None] * len(sw)
        sm = difflib.SequenceMatcher(None, [_norm(w) for w in sw], [_norm(w[1]) for w in ww], autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): t0s[a + k], t1s[a + k] = ww[b + k][2], ww[b + k][3]
        begin, eind = ww[0][2], ww[-1][3]; k = 0
        while k < len(sw):
            if t0s[k] is not None: k += 1; continue
            j = k
            while j < len(sw) and t0s[j] is None: j += 1
            a = t1s[k - 1] if k > 0 else begin; b = t0s[j] if j < len(sw) else eind
            if b <= a: b = a + 0.25 * (j - k)
            lens = [max(1, len(_norm(w))) for w in sw[k:j]]; tot = sum(lens); t = a
            for q in range(k, j):
                d = (b - a) * lens[q - k] / tot; t0s[q], t1s[q] = t, t + d; t += d
            k = j
        uit += [[i, w, round(t0s[q], 2), round(t1s[q], 2)] for q, w in enumerate(sw)]
    return uit
SW = _script_woorden()
EIND = Z[-1][1] + 1.6
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
if AUD.ndim > 1: AUD = AUD.mean(axis=1)
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in SW:
        if i == zin and _norm(w).startswith(_norm(woord)): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0] + na
# ---------- losse voorwerpen ----------
def los(im, tol=30):
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox())
SPR = {}
def sprite(n, hoogte, spiegel=False):
    k = (n, hoogte, spiegel)
    if k not in SPR:
        im = los(Image.open(HIER / "afbeeldingen" / f"{n}.png"))
        im = im.resize((max(1, int(im.width * hoogte / im.height)), hoogte), Image.LANCZOS)
        SPR[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if spiegel else im
    return SPR[k]
WACHT = Scenewachter(HIER.parent / "achtergronden.json")
def zet(img, n, hoogte, x, voet, op=None, voor=False, naam=None, punt=None):
    s = sprite(n, hoogte)
    dx, dy = WACHT.plaats(naam or n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, voor=voor, punt=punt)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]

# ---------- personages v2 (eigenaar 26 nov: "gebruik betere personages die er meer op lijken", "laten zitten", "camera bewegen") ----------
# Uitgewerkte cartoon-portretten (ComfyUI, personages/prompts.txt), bovenlijf. Mond = (x, y) als fractie van het bijgesneden plaatje.
MOND = {"jensen-1993": (0.49, 0.405), "jensen-nu": (0.55, 0.487), "chris-1993": (0.50, 0.41), "curtis-1993": (0.48, 0.355),
        "jij-1993": (0.47, 0.375), "jij-1999": (0.50, 0.27), "jij-nu": (0.55, 0.32), "serveerster": (0.50, 0.30),
        "sega-baas": (0.49, 0.31), "onderzoeker": (0.48, 0.28), "collega": (0.50, 0.32)}
LIJF = {"YOU": "jij-1993", "YOU2": "jij-nu", "JENSEN": "jensen-1993", "JENSEN2": "jensen-nu", "SERVEERSTER": "serveerster",
        "CURTIS": "curtis-1993", "SEGA": "sega-baas", "ONDERZOEKER": "onderzoeker"}
def luid(t, naam):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == naam for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

# ---------- tijden ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_START, I_JEN, I_NEE, I_KOF = zi("San Jose"), zi("Hey kid"), zi("For a napkin"), zi("More coffee")
I_FLOP, I_CUR, I_SEGA, I_SEGA2 = zi("Two years"), zi("Most games"), zi("But the boss"), zi("I like")
I_BEURS, I_AI, I_ONDZ, I_NU, I_WOW, I_SLOT = zi("1999"), zi("Then AI"), zi("We need"), zi("Today"), zi("Six hundred"), zi("Still want")
T_SERV = Z[I_KOF][0] - 1.1; T_SCHENK = Z[I_KOF][0] - 0.1
T_DRIE = kw(I_START, "three", -0.1); T_FLOP = kw(I_FLOP, "flops", -0.1)
T_5M = kw(I_SEGA, "five", -0.1); T_KOOP = kw(I_BEURS, "buy", -0.1); T_12 = Z[I_BEURS][0] + 0.2
T_620 = kw(I_NU, "six", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="denny", bg="denny"), dict(t=Zs(I_FLOP), naam="kantoor", bg="kantoor"), dict(t=Zs(I_SEGA), naam="sega", bg="sega"),
      dict(t=Zs(I_BEURS), naam="beurs", bg="beurs"), dict(t=Zs(I_AI), naam="ai", bg="ai"), dict(t=Zs(I_NU), naam="nu", bg="denny")]
KOP = {"denny": "1993", "kantoor": "1995", "sega": "1995", "beurs": "1999", "ai": "2023", "nu": "TODAY"}
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]

# ---------- indeling per scène: (plaatje, x, voet, hoogte); voet ligt achter de tafel of onder de rand (bovenlijf) ----------
TAFEL_Y = 1450
def V(h): return TAFEL_Y + 0.42 * h                       # voet zo dat het middel net achter de tafel zit
def figuren(n, t):
    if n == "denny":
        f = [("chris-1993", 830, V(640) - 40, 640), ("curtis-1993", 1010, V(660), 660), ("jensen-1993", 610, V(720), 720), ("jij-1993", 215, V(660), 660)]
        if t >= T_SERV: f.append(("serveerster", -300 + 700 * ps.ease((t - T_SERV) / 1.0), H + 430, 1150))
        return f
    if n == "kantoor": return [("jensen-1993", 300, V(820), 820), ("curtis-1993", 790, V(800), 800)]
    if n == "sega": return [("jensen-1993", 280, V(800), 800), ("sega-baas", 800, V(820), 820)]
    if n == "beurs": return [("jij-1999", 760, V(820), 820)]
    if n == "ai": return [("collega", 280, H + 380, 1100), ("onderzoeker", 790, H + 400, 1120)]
    if n == "nu": return [("jij-nu", 290, V(800), 800), ("jensen-nu", 800, V(820), 820)]
    return []
def hoofd(naam, x, voet, h):                              # midden van het gezicht (voor de camera)
    s = sprite(naam, h); mx, my = MOND[naam]
    return x - s.width / 2 + mx * s.width, voet - h + (my - 0.08) * h

def figuur(img, naam, x, voet, h, t):
    s = sprite(naam, h); l = luid(t, naam)
    dy = -abs(math.sin(t * 11)) * h * 0.008 if l > 0.05 else math.sin(t * 1.7 + x) * h * 0.002     # wippen bij praten, ademen anders
    x0, y0 = int(x - s.width / 2), int(voet - h + dy); img.paste(s, (x0, y0), s)
    if l > 0.08:                                          # mond open, mee met het geluid
        mx, my = x0 + MOND[naam][0] * s.width, y0 + MOND[naam][1] * h; bw = s.width * 0.055; bh = s.width * (0.012 + 0.03 * l)
        ImageDraw.Draw(img).ellipse((mx - bw, my - bh * 0.6, mx + bw, my + bh), fill=(95, 35, 40), outline=INK, width=3)
    GEZ[naam] = (*hoofd(naam, x, voet, h), h / 520)

SCHRIK, BLIJ, VERDRIET = (), (), ()
ZOOM_AAN = True; TEKST_AAN = True
# ---------- tekst ----------
def _start(i, frase):
    w0 = _norm(frase.split()[0])
    for j, w, t0, t1 in SW:
        if j == i and _norm(w) == w0: return t0
    return Z[i][0]
def emotie(t, nu_i):
    if nu_i is None: return None
    tekst = Z[nu_i][2]; best = (None, -1)
    for soort, lijst in (("schrik", SCHRIK), ("verdriet", VERDRIET), ("blij", BLIJ)):
        for f_ in lijst:
            if f_.lower() in tekst.lower():
                st = _start(nu_i, f_)
                if st - 0.15 <= t and st > best[1]: best = (soort, st)
    return best[0]

# ---------- tekeningen ----------
LAYOUT = set()
def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if x is None: x = 50 + w / 2
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = [w for w in SW if w[0] == i]
    f = font(FS, 58); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        if cur and sum(d.textlength(v[1].upper() + " ", font=f) for v in cur + [w]) > W - 60: stukken.append(cur); cur = []   # te breed: nieuwe regel
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1].upper() + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1500
    if br > W - 40: LAYOUT.add(f"ondertitel te breed: {' '.join(w[1] for w in stuk)}")
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)

# ---------- meubels en spullen ----------
def bank_achter(d, x0, x1):
    d.rounded_rectangle((x0, TAFEL_Y - 520, x1, TAFEL_Y + 20), 30, fill=(205, 60, 60), outline=INK, width=5)
    for k in range(int((x1 - x0) / 90)): d.line((x0 + 45 + k * 90, TAFEL_Y - 490, x0 + 45 + k * 90, TAFEL_Y), fill=(175, 45, 45), width=4)
def tafel(d, x0, x1, blad=(235, 230, 220), voor=(205, 60, 60), naam="tafel"):   # tafelblad + voorkant (bankje of bureau): bovenlijf erachter
    WACHT.vlak(naam, [x0, x1, TAFEL_Y - 10, TAFEL_Y + 16])
    d.rectangle((x0, TAFEL_Y, x1, TAFEL_Y + 40), fill=blad, outline=INK, width=5)
    d.rectangle((x0 + 10, TAFEL_Y + 40, x1 - 10, TAFEL_Y + 58), fill=(180, 180, 185), outline=INK, width=3)
    d.rounded_rectangle((x0 - 10, TAFEL_Y + 58, x1 + 10, H + 40), 26, fill=voor, outline=INK, width=5)
    if voor == (205, 60, 60):
        for k in range(int((x1 - x0) / 90)): d.line((x0 + 45 + k * 90, TAFEL_Y + 80, x0 + 45 + k * 90, H), fill=(175, 45, 45), width=4)
def mok(d, x, naam="tafel"):
    WACHT.plaats("koffiemok", (x - 22, TAFEL_Y - 44, x + 22, TAFEL_Y), op=naam)
    d.rectangle((x - 22, TAFEL_Y - 44, x + 22, TAFEL_Y + 2), fill=(250, 250, 250), outline=INK, width=4); d.arc((x + 12, TAFEL_Y - 36, x + 40, TAFEL_Y - 10), -90, 90, fill=INK, width=5)
def servet(d, x0, t_start, t, naam="tafel"):             # servet plat op tafel; de chip-schets komt er lijn voor lijn bij
    y0 = TAFEL_Y - 6; WACHT.plaats("servet", (x0 - 70, y0 - 4, x0 + 80, TAFEL_Y), op=naam)
    d.polygon([(x0 - 70, y0), (x0 + 60, y0 - 4), (x0 + 80, y0 + 30), (x0 - 60, y0 + 34)], fill=(252, 252, 248), outline=INK)
    n = min(6, int(max(0, t - t_start) / 0.5))
    for a, b, c, e in [(-30, 6, 10, 6), (10, 6, 10, 26), (10, 26, -30, 26), (-30, 26, -30, 6), (-40, 12, -30, 12), (10, 20, 20, 20)][:n]:
        d.line((x0 + a, y0 + b, x0 + c, y0 + e), fill=(60, 80, 170), width=3)
def rook(d, x, y, t, t0):                                 # rookwolkjes boven de mislukte kaart
    for k in range(4):
        f = ((t - t0) * 0.8 + k * 0.25) % 1.0; r = 18 + 30 * f
        d.ellipse((x - r + 20 * math.sin(k * 2 + t), y - 40 - 160 * f - r, x + r + 20 * math.sin(k * 2 + t), y - 40 - 160 * f + r), fill=(120, 120, 125))
def scherm(img, x, t):                                    # CRT met beurskoers (eigen tekst, klopt: NVDA $12 bij de beursgang)
    s = sprite("crt", 420); x0, y0 = int(x - s.width / 2), int(TAFEL_Y - s.height + 6); img.paste(s, (x0, y0), s)
    WACHT.plaats("computer", (x0, y0, x0 + s.width, TAFEL_Y), op="bureau")
    d = ImageDraw.Draw(img); sx0, sy0, sx1, sy1 = x0 + s.width * 0.17, y0 + s.height * 0.16, x0 + s.width * 0.8, y0 + s.height * 0.6
    d.rectangle((sx0, sy0, sx1, sy1), fill=(10, 25, 60))
    d.text(((sx0 + sx1) / 2, sy0 + 28), "NVDA $12", font=font(FB, 36), fill=(120, 255, 140), anchor="mm")
    pts = [(sx0 + 12 + k * (sx1 - sx0 - 24) / 7, sy1 - 18 - (k * 9 + (k % 2) * 8)) for k in range(8)]
    d.line(pts, fill=(120, 255, 140), width=4)
    if t >= T_KOOP:
        d.rounded_rectangle((sx0 + 40, sy1 - 62, sx1 - 40, sy1 - 22), 8, fill=(40, 170, 70)); d.text(((sx0 + sx1) / 2, sy1 - 42), "BUY", font=font(FB, 28), fill="white", anchor="mm")

# ---------- camera: zacht naar wie praat; bij de verteller rustig inzoomen op de scène ----------
SCENE_MID = {"denny": (560, 1150), "kantoor": (560, 1150), "sega": (540, 1150), "beurs": (560, 1150), "ai": (540, 1250), "nu": (540, 1150)}
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.2), default=None)
    cx, cy = SCENE_MID[n]; zm = 1.0 + min(0.18, (t - sc["t"]) * 0.03)
    if n == "denny" and nu == I_START and t >= T_DRIE: cx, cy, zm = 780, 1150, 1.25          # "three engineers"
    if nu is not None and Z[nu][4] in LIJF:
        naam = LIJF[Z[nu][4]]
        for f in figuren(n, t):
            if f[0] == naam: hx, hy = hoofd(*f); cx, cy, zm = hx, hy + 200, 1.3
    for tt, c in ((T_5M, "sega"), (T_620, "nu")):
        if n == c and t >= tt and nu is not None and Z[nu][4] == "N": zm = 1.3
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz * 0.92                               # nieuwe scène: meteen erheen (iets wijder)
        a = 0.06; cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

GEZ = {}
def frame(t):
    sc = scene(t); n = sc["naam"]
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t); GEZ.clear(); d = ImageDraw.Draw(img)
    figs = figuren(n, t)
    if n in ("denny", "nu"): bank_achter(d, 0, 400) if n == "denny" else None; bank_achter(d, 470 if n == "denny" else 0, 1080)
    for f in figs:
        if f[0] != "serveerster": figuur(img, *f, t)
    d = ImageDraw.Draw(img)
    if n == "denny":
        tafel(d, 0, 400, naam="tafel-links"); tafel(d, 470, 1080)
        servet(d, 640, 0.6, t); mok(d, 870); mok(d, 1010); mok(d, 560)
        zet(img, "pannenkoek", 100, 330, TAFEL_Y + 4, op="tafel-links", naam="pannenkoeken")
        for f in figs:
            if f[0] == "serveerster":
                figuur(img, *f, t); kx, ky = f[1] + 250, 1330
                schenk = T_SCHENK <= t < T_SCHENK + 1.6
                kan = sprite("koffiekan", 150).rotate(-40 if schenk else 0, expand=True, resample=Image.BICUBIC)
                px, py = int(kx - kan.width * 0.3), int(ky - kan.height * 0.6); img.paste(kan, (px, py), kan)
                WACHT.plaats("koffiekan", (px, py, px + kan.width, py + kan.height), op="aan:hand")
                if schenk: ImageDraw.Draw(img).line((px + kan.width * 0.92, py + kan.height * 0.32, 560, TAFEL_Y - 44), fill=(110, 65, 35), width=8)
    if n == "nu":
        tafel(d, 0, 1080); servet(d, 560, -99, t); mok(d, 330); mok(d, 880)
    if n in ("kantoor", "beurs"):
        tafel(d, 0, 1080, blad=(200, 200, 205), voor=(150, 150, 160), naam="bureau")
    if n == "kantoor":
        zet(img, "videokaart", 170, 550, TAFEL_Y + 2, op="bureau", naam="videokaart")
        if t >= T_FLOP: rook(ImageDraw.Draw(img), 550, TAFEL_Y - 90, t, T_FLOP)
    if n == "beurs": scherm(img, 290, t)
    if n == "sega": tafel(d, 0, 1080, blad=(120, 80, 50), voor=(95, 60, 38), naam="vergadertafel")
    if n == "ai":
        for f in figs: figuur(img, *f, t)
        zet(img, "videokaart", 230, 790, 1890, op="aan:hand", naam="videokaart", punt=(790, 1860))
    img = camera(img, t)
    if TEKST_AAN:
        if n in KOP: kop(img, KOP[n], None, 150, 84, KL["geel"], ps.pop((t - sc["t"]) / 0.3))
        if n == "kantoor" and t >= T_FLOP: kop(img, "FIRST CHIP: FLOP", W / 2, 330, 90, (255, 90, 80), ps.pop((t - T_FLOP) / 0.3))
        if n == "sega" and t >= T_5M: kop(img, "$5,000,000", W / 2, 330, 130, (90, 220, 110), ps.pop((t - T_5M) / 0.3))
        if n == "beurs" and t >= T_KOOP: kop(img, "YOU BUY: $100", W / 2, 330, 100, (90, 220, 110), ps.pop((t - T_KOOP) / 0.3))
        if n == "ai" and t >= Z[I_AI][0] + 0.3: kop(img, "AI", W / 2, 330, 160, (118, 185, 0), ps.pop((t - Z[I_AI][0] - 0.3) / 0.3))
        if n == "nu" and t >= T_620: kop(img, "$620,000", W / 2, 330, 150, (90, 220, 110), ps.pop((t - T_620) / 0.35))
        ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1], 60 * v[2]) for k_, v in GEZ.items()})
    return img

# ---------- geluid: ECHTE opnames (CC0, freesound.org, ../geluiden/gekozen.json), alleen wat je ziet ----------
GSR = 48000
def _laad(n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HIER.parent / "geluiden" / f"{n}.mp3"), "-ac", "1", "-ar", str(GSR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
def _drukste(x, dur):
    n = min(len(x) - 1, int(dur * GSR)); e = np.convolve(x ** 2, np.ones(GSR // 10), "same")
    best = max(range(0, max(1, len(x) - n), GSR // 20), key=lambda i: e[i:i + n].sum()); return x[best:best + n]
def _fade(x, f=0.04):
    k = min(len(x) // 3, int(f * GSR)); x = x.copy(); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
GELUIDEN = []
def geluid():
    uit = np.zeros(int((EIND + 1) * GSR), np.float32)
    def zet_(t, n, x, g, zie):
        i = int(t * GSR); j = min(len(uit), i + len(x)); uit[i:j] += x[:j - i] * g; GELUIDEN.append((t, n, zie))
    for q in np.arange(T_SERV, T_SERV + 0.9, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.3, "serveerster")   # serveerster loopt
    zet_(T_KOOP + 0.2, "klik", _fade(_laad("klik")), 0.5, "computer")                                                             # kopen met de muis
    uit /= max(1, np.abs(uit).max() / 0.9)
    sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
        frame(t + 0.15); gezien = {k[0] for k, v in WACHT.gezien.items() if any(abs(tt - (t + 0.15)) < 1e-6 for tt, _ in v)} | set(GEZ)
        if zie != "winkel-app" and zie not in gezien: fout.append(f"{t:.1f} s: geluid '{n}' maar '{zie}' is niet in beeld")
        if n == "krekels":
            vrij = min([z[0] for z in Z if z[0] > t] or [EIND]) - max([z[1] for z in Z if z[1] <= t] or [0])
            if vrij < 1.5: fout.append(f"{t:.1f} s: krekels maar maar {vrij:.1f} s stilte (minstens 1,5 s)")
    return fout

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 7, 480 * 2)); [pl.paste(im, (270 * (i % 7), 480 * (i // 7))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); sys.exit()
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-nvidia.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); print("KLAAR short-nvidia.mp4", round(EIND, 1), "s")
