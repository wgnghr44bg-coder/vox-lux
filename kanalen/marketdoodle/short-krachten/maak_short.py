"""What If Your Family Had Superpowers? — Short, staand 1080x1920 (28 nov 2026), 2D pop_short-stijl. Hype: Avengers: Doomsday (final trailer
68M views, film 18 dec), zonder Marvel. Eigenaar 28 nov: snelle grappen zoals de GTA-short, geen "Day 1/2/3".
Regels (28 nov, Studio-vergelijking): vraag in seconde 1, 30-38 s, loop, keuzevraag in beeld aan het eind (shortregels.py).
Zelfde opzet en controles als Black Friday: naamlabels, plaatskaarten, scènewachter (ondergrond, maat), tekstwachter (genoemd =
gezien, spreker, gevoel, RIJDEN, DOEN), LAYOUT, geluidcheck, TEKSTCONTROLE.jpg.
Gebruik: <omnivoice-venv>/python maak_short.py [--tekst | --plaat]  -> short-krachten.mp4"""
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
LIJF = {"YOU": "you", "DAD": "dad", "SIS": "sis", "MOM": "mom"}
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
I_HOOK, I_DAD, I_MAMA, I_MOM, I_ZUS, I_SIS, I_JIJ, I_YOU, I_SLOT = (zi("What if"), zi("Who makes"), zi("Mom has"), zi("Done!"), zi("Your sister"),
                                                                   zi("You ate"), zi("And your superpower"), zi("Hello?"), zi("And that's why"))
T_KRACHT, T_OPEN, T_RIP = kw(I_HOOK, "strength", -0.4), kw(I_HOOK, "opens", -0.1), kw(I_HOOK, "rips", -0.1)
T_SPEED, T_DINER, T_HUISWERK, T_FOUT = kw(I_MAMA, "speed", -0.4), kw(I_MAMA, "Dinner", -0.1), kw(I_MAMA, "homework", -0.25), kw(I_MAMA, "wrong", -0.25)
T_LEZEN, T_JOUW = kw(I_ZUS, "read", -0.2), kw(I_ZUS, "Especially", -0.1)
T_ONZ, T_NIEMAND = kw(I_JIJ, "invisible", -0.2), kw(I_JIJ, "Nobody", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="keuken", bg="keuken"), dict(t=Zs(I_MAMA), naam="eetkamer", bg="eetkamer"), dict(t=Zs(I_ZUS), naam="woonkamer", bg="woonkamer"),
      dict(t=Zs(I_SLOT), naam="slot", bg="keuken")]
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
PLAATS = {}                                                # geen "Day 1/2/3" (eigenaar 28 nov)
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)
SCHRIK = ("Who makes", "Hello?")
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]
    if any(tekst.startswith(f_) for f_ in SCHRIK): return "schrik"
    return None
ACTIE = {I_DAD: "juich", I_MOM: "duim", I_SIS: "wijs", I_YOU: "zwaai"}
NAAM["mom"] = ("MOM", (200, 160, 255))

# ---------- keuken: papa, augurkenpot, koelkastdeur ----------
KOEL = (835, 420, 1060, 955)                               # koelkast in de keuken-achtergrond (achtergronden.json v-keuken)
def koelkast_open(img, t):
    if t < T_RIP + 0.15 and scene(t)["naam"] != "slot": WACHT.plaats("koelkast", KOEL, op="beeld"); return
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = KOEL
    d.rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12), fill=(235, 245, 248), outline=INK, width=5)       # binnenkant met licht
    for k_ in range(3): d.line((x0 + 20, y0 + 150 + k_ * 130, x1 - 20, y0 + 150 + k_ * 130), fill=(170, 200, 210), width=8)
    for k_, (kx, kl) in enumerate(((x0 + 50, (240, 200, 60)), (x0 + 120, (220, 80, 70)), (x0 + 170, (120, 190, 110)))):
        d.rounded_rectangle((kx, y0 + 80 + 130 * (k_ % 3), kx + 40, y0 + 145 + 130 * (k_ % 3)), 8, fill=kl, outline=INK, width=3)
    WACHT.plaats("koelkast", KOEL, op="beeld")
def deur_boven(img, x, y, sch=1.0):                        # de afgerukte koelkastdeur boven papa's hoofd
    w_, h_ = int(225 * sch), int(535 * sch); laag = Image.new("RGBA", (w_ + 20, h_ + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.rounded_rectangle((5, 5, w_, h_), 22, fill=(170, 220, 210), outline=INK, width=6)
    d.line((30, int(h_ * 0.42), w_ - 25, int(h_ * 0.42)), fill=INK, width=5)
    d.rounded_rectangle((w_ - 45, int(h_ * 0.15), w_ - 30, int(h_ * 0.35)), 6, fill=(120, 130, 145), outline=INK, width=3)
    laag = laag.rotate(78, expand=True, resample=Image.BICUBIC)
    img.paste(laag, (int(x - laag.width / 2), int(y - laag.height / 2)), laag)
    WACHT.plaats("koelkastdeur", (x - laag.width / 2, y - laag.height / 2, x + laag.width / 2, y + laag.height / 2), op="beeld")
def pot(img, x, y, t):                                      # augurkenpot in papa's hand, deksel vliegt eraf bij "opens"
    s_ = sprite("augurkpot", 150); img.paste(s_, (int(x - s_.width / 2), int(y - s_.height / 2)), s_)
    WACHT.plaats("augurkenpot", (x - s_.width / 2, y - s_.height / 2, x + s_.width / 2, y + s_.height / 2), op="beeld")
    if T_OPEN + 0.2 <= t < T_RIP + 1.5 and scene(t)["naam"] == "keuken":
        u = t - T_OPEN - 0.2; d = ImageDraw.Draw(img); lx, ly = x + 180 * u, y - s_.height / 2 - 380 * u + 400 * u * u
        d.ellipse((lx - 55, ly - 18, lx + 55, ly + 18), fill=(190, 195, 205), outline=INK, width=4)

# ---------- eetkamer: mama met supersnelheid ----------
TAFEL_Y = 790
def eten(img, t):
    if t >= T_DINER + 0.3:
        s_ = sprite("diner", 380); img.paste(s_, (int(540 - s_.width / 2), int(TAFEL_Y + 25 - s_.height)), s_)
        WACHT.plaats("diner", (540 - s_.width / 2, TAFEL_Y + 25 - s_.height, 540 + s_.width / 2, TAFEL_Y + 25), op="beeld")
    if t >= T_HUISWERK + 0.2:                               # huiswerk: blad met rode kruisjes
        d = ImageDraw.Draw(img); x0, y0 = 250, TAFEL_Y - 130
        d.polygon(((x0, y0), (x0 + 190, y0 - 20), (x0 + 210, y0 + 140), (x0 + 20, y0 + 160)), fill=(252, 250, 240), outline=INK)
        for k_ in range(4): d.line((x0 + 30, y0 + 25 + k_ * 32, x0 + 150, y0 + 15 + k_ * 32), fill=(150, 160, 190), width=5)
        if t >= T_FOUT:
            for k_ in range(4):
                cx, cy = x0 + 170, y0 + 22 + k_ * 32
                d.line((cx - 12, cy - 12, cx + 12, cy + 12), fill=(220, 40, 40), width=6); d.line((cx - 12, cy + 12, cx + 12, cy - 12), fill=(220, 40, 40), width=6)
        WACHT.plaats("huiswerk", (x0, y0 - 20, x0 + 210, y0 + 160), op="beeld")
def snel(img, t):                                           # snelheidsstrepen achter mama
    if not (T_SPEED <= t < Z[I_MOM][0]): return
    d = ImageDraw.Draw(img)
    for k_ in range(7):
        y = 700 + k_ * 60; x1 = 885 - 120 - (k_ % 3) * 30; x0 = x1 - 260 - ((t * 900 + k_ * 77) % 140)
        d.line((x0, y, x1, y), fill=(255, 255, 255), width=10); d.line((x0, y + 12, x1 - 40, y + 12), fill=(200, 160, 255), width=6)

# ---------- woonkamer: zus leest gedachten, jij bent onzichtbaar ----------
def gedachte(img, x, y, t, inhoud):
    d = ImageDraw.Draw(img)
    for k_, r in enumerate((14, 22)): d.ellipse((x - 40 - k_ * 35 - r, y + 150 - k_ * 50 - r, x - 40 - k_ * 35 + r, y + 150 - k_ * 50 + r), fill=(255, 255, 255), outline=INK, width=4)
    d.ellipse((x - 150, y - 150, x + 150, y + 60), fill=(255, 255, 255), outline=INK, width=6)
    if inhoud == "koekje":
        s_ = sprite("koekje", 150); img.paste(s_, (int(x - s_.width / 2), int(y - 45 - s_.height / 2)), s_)
        WACHT.plaats("koekje", (x - 75, y - 120, x + 75, y + 30), op="beeld")
def gloed(img, x, y, t):                                    # paarse ringen om het hoofd van de zus (gedachten lezen)
    d = ImageDraw.Draw(img)
    for k_ in range(3):
        r = 110 + ((t * 120 + k_ * 50) % 150); d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), outline=(190, 120, 255), width=6)

# ---------- figuren ----------
def figuren(n, t):
    if n in ("keuken", "slot"):
        y = 1330; geb = "juich" if t >= T_RIP and n == "keuken" else "vast"
        return [("dad", 330, y, schaal("keuken", "dad", y), geb, 0.9, None)]
    if n == "eetkamer":
        y = 1230; return [("mom", 885, y, schaal("eetkamer", "mom", y), None, -0.6, None)]
    if n == "woonkamer":
        figs = [("sis", 300, 1560, schaal("woonkamer", "sis", 1560, 1.0), "wijs" if Z[I_SIS][0] - 0.1 <= t else None, 0.6, None)]
        figs.append(("you", 780, 1560, schaal("woonkamer", "you", 1560), None, -0.5, None))
        return figs
    return []
def onzichtbaar(t): return scene(t)["naam"] == "woonkamer" and t >= T_ONZ

# ---------- camera ----------
def _doel(t):
    sc = scene(t); n = sc["naam"]
    cx, cy, zm = 540, 1000, 1.0 + min(0.12, (t - sc["t"]) * 0.03)
    if n == "keuken":
        cx, cy, zm = 540, 950, 1.0 + t * 0.02
        if T_OPEN <= t < T_RIP: cx, cy, zm = 380, 900, 1.5
        elif T_RIP <= t: cx, cy, zm = 560, 820, 1.1
    if n == "eetkamer": cx, cy, zm = (600, 1000, 1.15) if t < T_DINER else (560, 850, 1.05)
    if n == "woonkamer": cx, cy, zm = (540, 1100, 1.0) if t < T_ONZ else (700, 1150, 1.25)
    if n == "slot": cx, cy, zm = 540, 950, 1.0
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz
        a = 0.12
        cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter: wat genoemd wordt, moet in beeld zijn
ZIE = {"super strength": ["tekst:SUPER STRENGTH"], "jar of pickles": ["augurkenpot"], "fridge door": ["koelkastdeur"], "these jars": ["augurkenpot"],
       "mom has": ["mom"], "super speed": ["tekst:SUPER SPEED"], "dinner": ["diner"], "homework": ["huiswerk"], "all wrong": ["huiswerk"],
       "your sister": ["sis"], "read minds": ["tekst:MIND READER"], "last cookie": ["koekje"], "invisible": ["tekst:INVISIBLE"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)
EIND_VRAAG = "WHICH POWER WOULD YOU PICK? 👇"
EINDTEKSTEN = set()

def frame(t):
    t_b = min(t, Z[-1][1] + 0.4)
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b); bgn = sc["bg"]
    img = bg(bgn).copy(); WACHT.begin("v-" + bgn, t_b); GEZ.clear(); GEB.clear(); SCHERM.clear()
    if n in ("keuken", "slot"): koelkast_open(img, t_b)
    if n == "eetkamer": eten(img, t_b); snel(img, t_b)
    figs = figuren(n, t_b)
    zicht = [f for f in figs if not (f[0] == "you" and onzichtbaar(t_b))]
    koppen = teken(img, zicht, t_b, nu)
    if len(zicht) < len(figs):                             # jij: doorzichtig (onzichtbaar), wel in beeld voor de controles
        laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); kk = teken(laag, [f for f in figs if f[0] == "you"], t_b, nu)
        a = laag.getchannel("A").point(lambda v: int(v * 0.28)); laag.putalpha(a); img.paste(laag, (0, 0), laag); koppen.update(kk)
    if n in ("keuken", "slot") and "dad" in GEZ:
        hx, hy, S_ = GEZ["dad"]
        if n == "keuken" and t_b >= T_RIP + 0.15:
            u = min(1, (t_b - T_RIP - 0.15) / 0.3); x = KOEL[0] + 110 + (hx - KOEL[0] - 110) * u; y = 690 + (hy - 95 * S_ - 690) * u
            deur_boven(img, x, y, 0.75)
        else: pot(img, hx + 8 * S_, hy + 118 * S_, t_b)
    if n == "woonkamer":
        if "sis" in GEZ and t_b >= T_LEZEN: gloed(img, GEZ["sis"][0], GEZ["sis"][1], t_b)
        if "you" in GEZ and T_JOUW <= t_b < T_ONZ: gedachte(img, GEZ["you"][0] + 40, GEZ["you"][1] - 330 * GEZ["you"][2], t_b, "koekje")
    img = camera(img, t)
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    GEZICHTEN[:] = [(k_, ((v[0] - cx0) * zm_, (v[1] + 60 * v[2] - cy0) * zm_, 66 * v[2] * zm_)) for k_, v in GEZ.items()]
    if TEKST_AAN:
        for naam, (hx_, top_) in koppen.items():
            if naam == "you" and onzichtbaar(t_b): continue
            tekst, kl = NAAM[naam]; X = (hx_ - cx0) * zm_; Y = (top_ - cy0) * zm_
            ps.W, ps.H = W, H; ps.label(img, tekst, X, Y - 45, kl, 0.55)
            bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, (X - bw_ / 2, Y - 70, X + bw_ / 2, Y - 20)))
        if n == "keuken" and T_KRACHT <= t_b < Z[I_DAD][1]: kop(img, "SUPER STRENGTH", W / 2, 1300, 96, KL["geel"], ps.pop((t_b - T_KRACHT) / 0.25))
        if n == "eetkamer" and T_SPEED <= t_b: kop(img, "SUPER SPEED", W / 2, 1300, 96, KL["geel"], ps.pop((t_b - T_SPEED) / 0.25))
        if n == "woonkamer" and T_LEZEN <= t_b < T_ONZ: kop(img, "MIND READER", W / 2, 300, 96, KL["geel"], ps.pop((t_b - T_LEZEN) / 0.25))
        if n == "woonkamer" and T_ONZ <= t_b: kop(img, "INVISIBLE", W / 2, 300, 96, KL["geel"], ps.pop((t_b - T_ONZ) / 0.25))
        if t_b >= EIND - 3.2:                              # keuzevraag voor de reacties (shortregels 4)
            p_ = ps.pop((t_b - (EIND - 3.2)) / 0.3); kop(img, "WHICH POWER", W / 2, 1160, 78, (255, 255, 255), p_); kop(img, "WOULD YOU PICK?", W / 2, 1260, 78, (255, 255, 255), p_)
            EINDTEKSTEN.add(EIND_VRAAG); d = ImageDraw.Draw(img); ax = W / 2; ay = 1330 + 10 * math.sin(t * 8)
            d.polygon(((ax - 40, ay), (ax + 40, ay), (ax, ay + 55)), fill=KL["geel"], outline=(20, 20, 30))
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
    x = np.arange(int(0.7 * GSR)) / GSR
    suis = np.convolve(rng.normal(0, 1, len(x)), np.ones(30) / 30, "same") * np.sin(np.pi * x / x[-1]) * 1.4
    tt = np.arange(int(0.5 * GSR)) / GSR; ting_ = np.sin(2 * np.pi * (900 + 900 * tt) * tt) * np.exp(-tt * 6) * 0.6
    plof = _fade(_laad("plof")); klap = _fade(_laad("deur-dicht")); ting = _fade(_laad("ting")); papier = _fade(_laad("papier")); hap = _fade(_laad("hap"))
    zet_(T_OPEN + 0.2, "plop", plof, 0.7, "augurkenpot")
    zet_(T_RIP + 0.1, "krak", klap, 1.0, "koelkastdeur")
    zet_(T_SPEED + 0.1, "suis", suis, 0.6, "mom"); zet_(T_DINER + 0.3, "ting", ting, 0.6, "diner"); zet_(T_HUISWERK + 0.2, "papier", papier, 0.6, "huiswerk")
    zet_(T_LEZEN + 0.1, "woeoe", ting_, 0.5, "sis"); zet_(T_ONZ + 0.1, "woeoe", ting_, 0.5, "you")
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
    frame(EIND - 1.0)
    sr = controleer(Z, EIND, voorwerpen_bij_start=start, woorden=WO, teksten_eind=list(EINDTEKSTEN)); print("SHORTREGELS:", sr or "alles goed", "| eerste beeld:", start)
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-krachten.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-krachten.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-krachten.mp4"), "-vf", "scale=720:1280", "-c:v", "libx264", "-b:v", "1100k",
                    "-c:a", "aac", "-b:a", "128k", str(HIER / "short-krachten-720.mp4")])
    print("KLAAR short-krachten.mp4", round(EIND, 1), "s")
