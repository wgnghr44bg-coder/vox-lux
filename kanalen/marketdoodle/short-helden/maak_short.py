"""What If Superheroes Were Real? — Short, staand 1080x1920 (28 nov 2026), oude 2D pop_short-stijl (eigenaar: "de oude 2D style
ook goed ... beter zo door"). Hype: Avengers: Doomsday final trailer (68M views in 5 dagen, film 18 dec); eigen helden, geen Marvel.
Regels Studio-analyse: vraag in seconde 1, 35-45 s, laatste zin loopt terug naar de eerste (shortregels.py).
Zelfde opzet en controles als Black Friday: naamlabels, plaatskaarten, scènewachter (ondergrond, maat), tekstwachter (genoemd =
gezien, spreker, gevoel, RIJDEN, DOEN), LAYOUT, geluidcheck, TEKSTCONTROLE.jpg.
Gebruik: <omnivoice-venv>/python maak_short.py [--tekst | --plaat]  -> short-helden.mp4"""
import json, math, os, re, subprocess, sys, difflib
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageChops
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools"))
from scenewachter import Scenewachter
from tekstwachter import Tekstwachter, blad
from shortregels import controleer

W, H, FPS, SS = 1080, 1920, 30, ps.SS
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
INK = (40, 35, 40)
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def _script_woorden():
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
from lipsync import Lipsync; ps.LIPSYNC = Lipsync(SW)                  # 27 nov: lip sync vast in elke nieuwe video
EIND = Z[-1][1] + 0.7                                      # kort: de laatste zin loopt terug naar de eerste (loop)
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
if AUD.ndim > 1: AUD = AUD.mean(axis=1)
LAYOUT = set()
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in SW:
        if i == zin and _norm(w).startswith(_norm(woord)): return t0 + na
    print("LET OP: niet gevonden", zin, woord); LAYOUT.add(f"woord '{woord}' niet gevonden in zin {zin}"); return Z[zin][0] + na
LIJF = {"YOU": "you", "DAD": "dad", "SIS": "sis"}
NAAM = {"you": ("YOU", (255, 215, 60)), "dad": ("DAD", (120, 220, 140)), "sis": ("SISTER", (255, 150, 200))}
def luid(t, naam):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == naam for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

# ---------- plaatjes ----------
def los(im, tol=30):
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox())
SPR = {}
def sprite(n, breed, spiegel=False):                       # op BREEDTE (de haai is lang)
    k = (n, int(breed), spiegel)
    if k not in SPR:
        im = los(Image.open(HIER / "sprites" / "afbeeldingen" / f"{n}.png"))
        im = im.resize((max(1, int(breed)), max(1, int(im.height * breed / im.width))), Image.LANCZOS)
        SPR[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if spiegel else im
    return SPR[k]
WACHT = Scenewachter(HIER.parent / "achtergronden.json")
MAAT = json.load(open(HIER.parent / "achtergronden.json", encoding="utf-8"))
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
def schaal(bgn, naam, y, f=0.92):
    m = MAAT["v-" + bgn]["maat"]; return f * m["k"] * (y - m["horizon"]) / (306 * ps.C[naam].get("groot", 1.0))
def pxm(bgn, y):
    m = MAAT["v-" + bgn]["maat"]; return m["k"] * (y - m["horizon"]) / 1.75

# ---------- tekst ----------
TEKST_AAN = True; SCHERM = []; GEB = {}; CROP = [None]; LABELS = []; GEZ = {}; GEZICHTEN = []
def kop(img, s, x, y, m, kl, sch):
    SCHERM.append(s)
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if x is None: x = 50 + w / 2
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    if sch >= 1:
        for ln, (a0, b0, a1, b1) in LABELS:
            if x - w / 2 < a1 and x + w / 2 > a0 and y - h / 2 < b1 and y + h / 2 > b0: LAYOUT.add(f"kop '{s}' valt over naamlabel {ln}")
        for gn, (fx, fy, fr) in GEZICHTEN:                 # 27 nov: kop over een gezicht (papa bij FRIDGE: GONE)
            ox = max(x - w / 2, min(fx, x + w / 2)); oy = max(y - h / 2, min(fy, y + h / 2))
            if (ox - fx) ** 2 + (oy - fy) ** 2 < fr ** 2: LAYOUT.add(f"kop '{s}' valt over het gezicht van {gn}")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = [w for w in SW if w[0] == i]
    f = font(FS, 58); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        if cur and sum(d.textlength(v[1].upper() + " ", font=f) for v in cur + [w]) > W - 60: stukken.append(cur); cur = []
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,:": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1].upper() + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1500
    if br > W - 40: LAYOUT.add(f"ondertitel te breed: {' '.join(w[1] for w in stuk)}")
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)
def plaatskaart(img, t, sc):
    if sc["naam"] not in PLAATS or sc.get("kaart") is False: return
    dt = t - sc["t"]; r1, r2 = PLAATS[sc["naam"]]
    if dt > 2.8:
        kop(img, r1, None, 150, 70, KL["geel"], 1.0); return
    f1, f2 = font(FB, 74), font(FS, 44); d0 = ImageDraw.Draw(img); SCHERM.extend([r1, r2])
    w = max(d0.textlength(r1, font=f1), d0.textlength(r2, font=f2)) + 110
    inn = ps.ease(dt / 0.4); uit = ps.ease(max(0.0, dt - 2.4) / 0.4); x0 = 40 - (w + 60) * (1 - inn) - (w + 60) * uit; y0 = 110
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.rounded_rectangle((x0 + 8, y0 + 10, x0 + w + 8, y0 + 190), 22, fill=(0, 0, 0, 110))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + 180), 22, fill=(18, 20, 26, 235))
    d.rectangle((x0, y0 + 14, x0 + 14, y0 + 166), fill=(235, 45, 45, 255))
    lijn = min(1.0, max(0.0, (dt - 0.25) / 0.5)); d.rectangle((x0 + 44, y0 + 104, x0 + 44 + (w - 90) * lijn, y0 + 108), fill=(235, 45, 45, 255))
    d.text((x0 + 44, y0 + 18), r1, font=f1, fill=(255, 255, 255, 255))
    n_ = int(len(r2) * min(1.0, max(0.0, (dt - 0.45) / 0.6)))
    d.text((x0 + 46, y0 + 118), r2[:n_], font=f2, fill=(255, 215, 60, 255))
    img.paste(laag, (0, 0), laag)

# ---------- poppetjes ----------
def hoofd(naam, x, y, s, *_):
    S = s * ps.C[naam].get("groot", 1.0); return x, y - 246 * S
def teken(img, figs, t, nu):                                # figs: (naam, x, y, s, gebaar, kijk, loop)
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    for naam, x, y, s, geb, kijk, loop in figs:
        if sp == naam and nu in ACTIE: geb = ACTIE[nu]
        emo = emotie(t, nu) if (sp is None or naam == sp) else None
        hx, hy = ps.poppetje(d, naam, x, y, s, t, loop=loop, kijk=kijk, mond=luid(t, naam), knipper=(t + hash(naam) % 7 * 0.4) % 3.4 < 0.13,
                             verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=geb if loop is None else "rennen")
        koppen[naam] = (hx, hy); S = s * ps.C[naam].get("groot", 1)
        GEZ[naam] = (*hoofd(naam, x, y, s), S); GEB[naam] = "rennen" if loop is not None else geb
        WACHT.persoon(naam, y, 306 * S)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); return koppen

# ---------- tijden ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_HOOK, I_BUS, I_AUTO, I_KEUKEN, I_DAD, I_BILL, I_GANG, I_SIS, I_SLOT = (zi("What if"), zi("Day one"), zi("That was my"), zi("Day two"), zi("Not covered"),
                                                                       zi("Then the city"), zi("Day three"), zi("It smells"), zi("And that's why"))
T_CAPES, T_STRENGTH, T_BROKEN = kw(I_HOOK, "Capes", -0.1), kw(I_HOOK, "Super", -0.1), kw(I_HOOK, "broken", -0.1)
T_SAVES, T_DROPS = kw(I_BUS, "saves", -0.1), kw(I_BUS, "drops", -0.1)
T_SORRY = kw(I_KEUKEN, "Sorry", -0.1)
T_BILL, T_TAX = kw(I_BILL, "bill", -0.15), kw(I_BILL, "Taxes", -0.1)
T_NEIGH, T_WORLD, T_TRASH = kw(I_GANG, "neighbor", -0.1), kw(I_GANG, "saves", -0.1), kw(I_GANG, "trash", -0.3)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="stad0", bg="stad"), dict(t=Zs(I_BUS), naam="stad", bg="stad"), dict(t=Zs(I_KEUKEN), naam="keuken", bg="keuken"),
      dict(t=Zs(I_GANG), naam="gang", bg="gang"), dict(t=Zs(I_SLOT), naam="slot", bg="stad")]
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
PLAATS = {"stad": ("DAY 1", "THE CITY"), "keuken": ("DAY 2", "THE BILL"), "gang": ("DAY 3", "THE NEIGHBOR")}
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)
SCHRIK = ("That was my", "Not covered", "It smells")
BLIJ = ()
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]
    if any(tekst.startswith(f_) for f_ in SCHRIK): return "schrik"
    return None
ACTIE = {I_AUTO: "hoofdhanden", I_DAD: "haar", I_SIS: "nee"}       # papa: hand bij het oor (telefoon wordt erbij getekend)

# ---------- held, bus, auto ----------
HELD_B = 380                                               # breedte van de vliegende held (px)
def held_pos(t):
    """waar de held hangt (midden x, bovenkant handen y) per moment"""
    bob = math.sin(t * 3.0) * 14
    n = scene(t)["naam"]
    if n == "stad0": return 520, 520 + bob
    if n == "stad":
        if t < T_SAVES: return 700, 470 + bob
        a = ps.ease(min(1, (t - T_SAVES) / 0.8)); return 700 + (330 - 700) * a, 470 + 120 * a + bob
    if n == "slot": a = ps.ease(min(1, (t - SC[4]["t"]) / 1.5)); return 820 + (520 - 820) * a, 520 + bob
    return None
def held(img, t):
    p = held_pos(t)
    if p is None: return None
    x, yh = p; s_ = sprite("held", HELD_B); top = yh - 0.06 * s_.height
    img.paste(s_, (int(x - s_.width / 2), int(top)), s_); box = (x - s_.width / 2, top, x + s_.width / 2, top + s_.height)
    WACHT.plaats("held", box, op="beeld")
    if T_SAVES <= t < T_DROPS + 0.8: GEB["held"] = "hoek"           # de held vangt de bus en laat hem vallen (DOEN: "drops")
    return box
AUTO_X, AUTO_V, AUTO_B = 215, 1440, 470                     # auto op de straat (links)
def auto(img, t):
    s_ = sprite("auto", AUTO_B); plat = 0.0
    if t >= T_DROPS + 0.45: plat = ps.ease(min(1, (t - T_DROPS - 0.45) / 0.15))
    h = int(s_.height * (1 - 0.55 * plat)); a_ = s_.resize((s_.width, max(1, h)), Image.LANCZOS)
    x0 = int(AUTO_X - a_.width / 2); img.paste(a_, (x0, AUTO_V - h), a_)
    WACHT.plaats("auto", (x0, AUTO_V - h, x0 + a_.width, AUTO_V), op="straat"); return AUTO_V - h
def bus(img, t, auto_top):
    if t < T_SAVES - 0.6: return None
    s_ = sprite("bus", 620)
    hp = held_pos(t)
    if t < T_SAVES:                                        # valt van boven het beeld in
        a = ps.ease((t - (T_SAVES - 0.6)) / 0.6); x, onder = 560, -100 + (hp[1] + 30 + 100) * a if hp else 400
    elif t < T_DROPS + 0.05:                               # rust op de handen van de held
        x, onder = hp[0], hp[1] + 30
    else:                                                  # laat los en valt op de auto
        hx, hy = held_pos(T_DROPS + 0.05); a = min(1, (t - T_DROPS - 0.05) / 0.4) ** 2
        x, onder = hx + (AUTO_X + 40 - hx) * a, hy + 30 + (auto_top + 20 - hy - 30) * a
    schuin = 0.0 if t < T_DROPS else min(8.0, (t - T_DROPS) * 25)
    b_ = s_.rotate(-schuin, expand=True, resample=Image.BICUBIC) if schuin else s_
    img.paste(b_, (int(x - b_.width / 2), int(onder - b_.height)), b_)
    WACHT.plaats("bus", (x - b_.width / 2, onder - b_.height, x + b_.width / 2, onder), op="beeld"); return True
def stof(img, t):                                           # stofwolk + sterretjes bij de klap
    u = (t - T_DROPS - 0.45) / 0.9
    if not 0 <= u < 1: return
    d = ImageDraw.Draw(img)
    for k_ in range(9):
        a = k_ / 9 * math.pi * 2; r = 60 + 260 * u; x = AUTO_X + 40 + math.cos(a) * r; y = AUTO_V - 60 + math.sin(a) * r * 0.35
        rr = 50 * (1 - u) + 15; d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(225, 220, 210), outline=INK, width=3)

# ---------- keuken: telefoon, stempel, rekening ----------
def rekening(img, t):
    if t < T_BILL: return
    a = ps.ease(min(1, (t - T_BILL) / 0.4)); w_, h_ = 440, 600; x0 = 760 - w_ / 2; y0 = 330 + (1 - a) * -1000
    d = ImageDraw.Draw(img)
    d.rectangle((x0 + 12, y0 + 14, x0 + w_ + 12, y0 + h_ + 14), fill=(60, 55, 60))
    d.rectangle((x0, y0, x0 + w_, y0 + h_), fill=(250, 248, 238), outline=INK, width=6)
    f1, f2 = font(FB, 64), font(FS, 40); d.text((x0 + 40, y0 + 30), "CITY BILL", font=f1, fill=(30, 30, 40)); SCHERM.append("CITY BILL")
    for k_ in range(6):
        y = y0 + 150 + k_ * 62; d.line((x0 + 40, y, x0 + w_ - 160, y), fill=(160, 160, 170), width=8)
        d.text((x0 + w_ - 140, y - 26), "$$$", font=f2, fill=(200, 60, 60))
    d.text((x0 + 40, y0 + h_ - 110), "TOTAL: $$$$$$", font=font(FB, 54), fill=(200, 40, 40))
    WACHT.plaats("rekening", (x0, y0, x0 + w_, y0 + h_), op="beeld")

# ---------- gang: buurman-held en zijn vuilnis ----------
def buurman(img, t):
    s_ = sprite("buurman", 330); v = 1380; x = 800
    img.paste(s_, (int(x - s_.width / 2), int(v - s_.height)), s_); WACHT.plaats("buurman", (x - s_.width / 2, v - s_.height, x + s_.width / 2, v), op="vloer")
def vuilnis(img, t):
    s_ = sprite("vuilnis", 430); v = 1470; x = 270
    img.paste(s_, (int(x - s_.width / 2), int(v - s_.height)), s_); WACHT.plaats("vuilnis", (x - s_.width / 2, v - s_.height, x + s_.width / 2, v), op="vloer")
    d = ImageDraw.Draw(img)                                # stanklijnen
    for k_ in range(4):
        x0 = x - 120 + k_ * 80; y0 = v - s_.height - 40 - (t * 40 + k_ * 30) % 80
        pts = [(x0 + 18 * math.sin(j * 0.9 + t * 4), y0 - j * 18) for j in range(8)]
        d.line(pts, fill=(120, 190, 80), width=9)

# ---------- figuren ----------
def figuren(n, t):
    if n == "stad" and t >= Z[I_AUTO][0] - 1.2:
        y = 1760; return [("you", 790, y, schaal("stad", "you", y), None, -0.9, None)]
    if n == "keuken":
        y = 1330; geb = "haar" if t < Z[I_BILL][0] else None
        return [("dad", 250, y, schaal("keuken", "dad", y), geb, 0.9, None)]
    if n == "gang":
        y = 1640; return [("sis", 470, y, schaal("gang", "sis", y, 0.85), None, 0.3, None)] if t >= T_TRASH - 0.6 else []
    return []

# ---------- camera ----------
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = nu_i(t)
    cx, cy, zm = 540, 1000, 1.0 + min(0.12, (t - sc["t"]) * 0.03)
    if n == "stad0":
        cx, cy, zm = 540, 900, 1.0 + t * 0.03
        if T_CAPES <= t < T_STRENGTH: cx, cy, zm = 520, 760, 1.6
        elif T_STRENGTH <= t < T_BROKEN: cx, cy, zm = 520, 650, 1.9
        elif T_BROKEN <= t: cx, cy, zm = 800, 980, 1.7
    if n == "stad":
        cx, cy, zm = 560, 900, 1.05
        if T_DROPS <= t < Z[I_AUTO][0]: cx, cy, zm = 420, 1150, 1.15
        if nu == I_AUTO: cx, cy, zm = 560, 1300, 1.15
    if n == "keuken": cx, cy, zm = 540, 960, 1.0
    if n == "gang": cx, cy, zm = 540, 1150, 1.0 + min(0.15, (t - sc["t"]) * 0.03)
    if n == "slot": cx, cy, zm = 540, 900, 1.0 + min(0.2, (t - sc["t"]) * 0.06)
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz
        a = 0.12 if n == "stad0" else 0.08
        cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter: wat genoemd wordt, moet in beeld zijn
ZIE = {"superheroes": ["held"], "capes": ["held"], "super strength": ["held"], "broken buildings": ["gat"], "a hero": ["held"],
       "falling bus": ["bus"], "your car": ["auto"], "my car": ["auto"], "dad calls": ["dad", "telefoon"], "hero damage": ["tekst:INSURANCE: DENIED"],
       "the bill": ["rekening"], "taxes": ["tekst:TAXES +300%"], "your new neighbor": ["buurman"], "neighbor is a superhero": ["buurman"],
       "saves the world": ["tekst:WORLD SAVED: 3x TODAY"], "trash": ["vuilnis"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)

def frame(t):
    t_b = min(t, Z[-1][1] + 0.4)
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b); bgn = sc["bg"]
    img = bg(bgn).copy(); WACHT.begin("v-" + bgn, t_b); GEZ.clear(); GEB.clear(); SCHERM.clear()
    if bgn == "stad": WACHT.plaats("gat", (760, 800, 900, 1130), op="beeld")
    if n in ("stad", "slot"):
        at = auto(img, t_b)
        if n == "stad": bus(img, t_b, at); stof(img, t_b)
        else:                                              # de platte auto met de bus erop blijft liggen (loop: zelfde stad)
            s_ = sprite("bus", 620).rotate(-8, expand=True, resample=Image.BICUBIC); img.paste(s_, (int(AUTO_X + 40 - s_.width / 2), int(at + 20 - s_.height)), s_)
    if n == "gang": vuilnis(img, t_b); buurman(img, t_b)
    koppen = teken(img, figuren(n, t_b), t_b, nu)
    if n == "keuken" and t_b < Z[I_BILL][0] and "dad" in GEZ:      # telefoon aan het oor
        hx, hy, S_ = GEZ["dad"]; d_ = ImageDraw.Draw(img); px, py = hx + 58 * S_, hy + 20 * S_
        d_.rounded_rectangle((px - 14 * S_, py - 34 * S_, px + 14 * S_, py + 34 * S_), int(6 * S_), fill=(40, 45, 60), outline=INK, width=4)
        d_.rectangle((px - 9 * S_, py - 26 * S_, px + 9 * S_, py + 24 * S_), fill=(120, 200, 255)); WACHT.plaats("telefoon", (px - 15 * S_, py - 35 * S_, px + 15 * S_, py + 35 * S_), op="beeld")
    held(img, t_b)
    if n == "keuken": rekening(img, t_b)
    img = camera(img, t)
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    GEZICHTEN[:] = [(k_, ((v[0] - cx0) * zm_, (v[1] + 60 * v[2] - cy0) * zm_, 66 * v[2] * zm_)) for k_, v in GEZ.items()]
    if TEKST_AAN:
        d = ImageDraw.Draw(img)
        for naam, (hx_, top_) in koppen.items():
            tekst, kl = NAAM[naam]; X = (hx_ - cx0) * zm_; Y = (top_ - cy0) * zm_
            ps.W, ps.H = W, H; ps.label(img, tekst, X, Y - 45, kl, 0.55)
            bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, (X - bw_ / 2, Y - 70, X + bw_ / 2, Y - 20)))
        plaatskaart(img, t_b, sc)
        if n == "keuken" and T_SORRY <= t_b < T_BILL: kop(img, "INSURANCE: DENIED", W / 2 + 40, 1250, 78, (235, 60, 60), ps.pop((t_b - T_SORRY) / 0.25))
        if n == "keuken" and t_b >= T_TAX: kop(img, "TAXES +300%", W / 2 + 60, 1250, 110, (235, 60, 60), ps.pop((t_b - T_TAX) / 0.3))
        if n == "gang" and T_WORLD <= t_b < T_TRASH: kop(img, "WORLD SAVED: 3x TODAY", W / 2, 400, 62, KL["groen"], ps.pop((t_b - T_WORLD) / 0.3))
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1] + 60 * v[2], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1] + 60 * v[2]) for k_, v in GEZ.items()},
           gebaren=dict(GEB), crop=CROP[0])
    return img

# ---------- geluid: echte opnames (CC0, ../geluiden) + zelfgemaakt suizen; alleen wat je ziet ----------
GSR = 48000
def _laad(n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HIER.parent / "geluiden" / f"{n}.mp3"), "-ac", "1", "-ar", str(GSR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
def _fade(x, f=0.04):
    k = min(len(x) // 3, int(f * GSR)); x = x.copy(); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
GELUIDEN = []
def geluid():
    rng = np.random.default_rng(3); uit = np.zeros(int((EIND + 1) * GSR), np.float32); GELUIDEN.clear()
    def zet_(t, n, x, g, zie):
        i = int(t * GSR); j = min(len(uit), i + len(x))
        if j > i >= 0: uit[i:j] += x[:j - i] * g; GELUIDEN.append((t, n, zie))
    x = np.arange(int(1.0 * GSR)) / GSR
    suis = np.convolve(rng.normal(0, 1, len(x)), np.ones(40) / 40, "same") * np.sin(np.pi * x / x[-1]) * 1.4     # held die langs vliegt
    plof = _fade(_laad("plof")); klap = _fade(_laad("deur-dicht")); stempel = _fade(_laad("stempel")); kassa = _fade(_laad("kassa")); papier = _fade(_laad("papier"))
    zet_(0.2, "suis", suis, 0.5, "held")
    zet_(T_SAVES - 0.1, "suis", suis, 0.5, "held")
    zet_(T_SAVES + 0.05, "plof", plof, 0.6, "bus")
    zet_(T_DROPS + 0.45, "krak", klap, 1.0, "auto"); zet_(T_DROPS + 0.5, "plof", plof, 0.8, "bus")
    zet_(T_SORRY + 0.1, "stempel", stempel, 0.9, "tekst:INSURANCE: DENIED")
    zet_(T_BILL + 0.05, "papier", papier, 0.6, "rekening"); zet_(T_TAX + 0.1, "kassa", kassa, 0.7, "tekst:TAXES +300%")
    zet_(SC[4]["t"] + 0.1, "suis", suis, 0.5, "held")
    uit /= max(1, np.abs(uit).max() / 0.9); sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
        frame(t + 0.15); gezien = {x[0] for x in WACHT.dit_frame} | set(GEZ) | {"tekst:" + s for s in SCHERM}
        if zie not in gezien: fout.append(f"{t:.1f} s: geluid '{n}' maar '{zie}' is niet in beeld")
    return fout

if __name__ == "__main__":
    if "--tekst" in sys.argv:
        for i in range(int(EIND * 6)): frame(i / 6)
        print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); print("LAYOUT:", sorted(LAYOUT) or "alles past"); sys.exit()
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.7 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 6, 480 * 2)); [pl.paste(im, (270 * (i % 6), 480 * (i // 6))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); sys.exit()
    frame(0.3); start = sorted({x[0] for x in WACHT.dit_frame})
    sr = controleer(Z, EIND, voorwerpen_bij_start=start, woorden=WO); print("SHORTREGELS:", sr or "alles goed", "| eerste beeld:", start)
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-helden.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-helden.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-helden.mp4"), "-vf", "scale=720:1280", "-c:v", "libx264", "-b:v", "1100k",
                    "-c:a", "aac", "-b:a", "128k", str(HIER / "short-helden-720.mp4")])
    print("KLAAR short-helden.mp4", round(EIND, 1), "s")
