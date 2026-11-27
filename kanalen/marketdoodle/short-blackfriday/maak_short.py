"""v7 (26 nov 2026): productiescript van de eigenaar ("WHAT IF BLACK FRIDAY NEVER ENDED?", 11 scènes). Achtergronden ComfyUI,
personages/voorwerpen/camera in Python. Zelfde opzet en controles als de NVIDIA-Short: naamlabels, plaatstitels met animatie,
camera volgt de spreker, scènewachter (ondergrond, zweven, gezichten), maatwachter, tekstwachter (beeld past bij de zin),
LAYOUT (tekst niet over labels), geluidcheck, TEKSTCONTROLE.jpg.  v6 = maak_short-v6.py / script-v6.txt.
Gebruik: <omnivoice-venv>/python maak_short.py [--tekst | --plaat]  -> short-blackfriday.mp4"""
import json, math, os, re, subprocess, sys, difflib
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageChops
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools"))
from scenewachter import Scenewachter
from tekstwachter import Tekstwachter, blad

W, H, FPS, SS = 1080, 1920, 30, ps.SS
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
INK = (40, 35, 40)
ps.C["agent"] = dict(broek=(30, 35, 60), shirt=(40, 50, 95), haar=(70, 50, 40), kapsel="kort", pet=(30, 35, 70), groot=1.12)      # politie, jaren 60
ps.C["kassa"] = dict(broek=(50, 55, 70), shirt=(200, 40, 50), haar=(60, 40, 30), kapsel="paard", groot=1.0)                   # kassamedewerker
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
LIJF = {"YOU": "you", "DAD": "dad", "SIS": "sis", "KASSA": "kassa", "AGENT": "agent", "MASCOTTE": "mascotte"}
NAAM = {"you": ("YOU", (255, 215, 60)), "dad": ("DAD", (120, 220, 140)), "sis": ("SISTER", (255, 150, 200)),
        "kassa": ("CASHIER", (255, 120, 110)), "agent": ("OFFICER", (130, 180, 255))}
def luid(t, naam):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == naam for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

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
MAAT = json.load(open(HIER.parent / "achtergronden.json", encoding="utf-8"))
def zet(img, n, hoogte, x, voet, op=None, voor=False, naam=None, punt=None):
    s = sprite(n, int(hoogte))
    dx, dy = WACHT.plaats(naam or n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, voor=voor, punt=punt)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
def schaal(bgn, naam, y, f=0.92):                          # maatwachter: schaal zodat het poppetje f x de echte maat op die diepte is
    m = MAAT["v-" + bgn]["maat"]; return f * m["k"] * (y - m["horizon"]) / (306 * ps.C[naam].get("groot", 1.0))
def pxm(bgn, y):                                           # pixels per meter op die diepte (voor voorwerpen)
    m = MAAT["v-" + bgn]["maat"]; return m["k"] * (y - m["horizon"]) / 1.75

# ---------- tijden ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_HOOK, I_TWINTIG = zi("What if"), zi("Nine-dollar")
I_WEEK2, I_SIS, I_WEEK3, I_RESTOCK = zi("Week two"), zi("Dad! Can"), zi("Week three"), zi("If they")
I_HOND = I_WAAROM = I_FEIT = I_AGENT = -1          # 27 nov: hond- en feit-scène eruit (short naar ± 40 s, Studio-analyse)
I_KERST, I_ELF, I_FAIL, I_SALE = zi("Christmas"), zi("Wow"), zi("Month six"), zi("Where's")
I_LAATST, I_ROOF, I_KASSA, I_SLOT = zi("Then Dad"), zi("A thousand"), zi("Relax"), zi("And it never")
T_NOOIT = kw(I_HOOK, "never", -0.1); T_90 = kw(I_HOOK, "ninety", -0.1)
T_9 = kw(I_TWINTIG, "nine", -0.1); T_20 = kw(I_TWINTIG, "twenty", -0.1)
T_SISIN = Z[I_SIS][0] - 1.3;                            # 26 nov (eigenaar): zus komt aanlopen
T_BED = T_POLITIE = 1e9
T_TVK = kw(I_KERST, "another", -0.1); T_ELFDE = kw(I_ELF, "eleventh", -0.1)
T_BANK = kw(I_FAIL, "bankrupt", -0.1); T_DADIN = Z[I_LAATST][0]; T_PRIJS = kw(I_LAATST, "full", -0.1); T_1000 = kw(I_LAATST, "thousand", -0.1)
T_CYBER = kw(I_KASSA, "cyber", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="winkel", bg="mall-tv"), dict(t=Zs(I_WEEK2), naam="dozen", bg="woonkamer"), dict(t=Zs(I_WEEK3), naam="tent", bg="buiten-nacht"),
      dict(t=Zs(I_KERST), naam="kerst", bg="kerst"),
      dict(t=Zs(I_FAIL), naam="failliet", bg="failliet"), dict(t=Zs(I_LAATST), naam="laatst", bg="winkeltje")]
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
PLAATS = {"winkel": ("BLACK FRIDAY", "WEEK 1"), "dozen": ("YOUR HOUSE", "WEEK 2"), "tent": ("THE PARKING LOT", "WEEK 3"),
          "hond": ("YOUR HOUSE", "WEEK 4"), "feit": ("PHILADELPHIA", "1960s"), "kerst": ("CHRISTMAS", "DECEMBER 25"),
          "failliet": ("THE MALL", "MONTH 6"), "laatst": ("THE LAST STORE", "ON EARTH")}
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)

# ---------- gezicht past bij de zin ----------
SCHRIK = ("Nine-dollar", "Why is he", "Not again", "A thousand", "Where's", "And it never")
BLIJ = ("What if", "If they", "Relax", "Your dog", "Wow")
VERDRIET = ("really", "Can you move")
def _start(i, frase):
    w0 = _norm(frase.split()[0])
    for j, w, t0, t1 in SW:
        if j == i and _norm(w) == w0: return t0
    return Z[i][0]
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]; best = (None, -1)
    for soort, lijst in (("schrik", SCHRIK), ("verdriet", VERDRIET), ("blij", BLIJ)):
        for f_ in lijst:
            if f_.lower() in tekst.lower():
                st = _start(nu, f_)
                if st - 0.15 <= t and st > best[1]: best = (soort, st)
    return best[0]

# ---------- tekst ----------
LAYOUT = set(); TEKST_AAN = True; SCHERM = []; GEB = {}; CROP = [None]; LABELS = []
def kop(img, s, x, y, m, kl, sch):
    SCHERM.append(s)
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if x is None: x = 50 + w / 2
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    if sch >= 1:
        for ln, (a0, b0, a1, b1) in LABELS:
            if x - w / 2 < a1 and x + w / 2 > a0 and y - h / 2 < b1 and y + h / 2 > b0: LAYOUT.add(f"kop '{s}' valt over naamlabel {ln}")
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
def plaatskaart(img, t, sc):                               # titel schuift in (typemachine) en krimpt na 2,8 s tot het hoekje
    dt = t - sc["t"]; r1, r2 = PLAATS[sc["naam"]]
    if dt > 2.8:
        kop(img, r2, None, 150, 70, KL["geel"], 1.0); return
    f1, f2 = font(FB, 74), font(FS, 44); d0 = ImageDraw.Draw(img); SCHERM.extend([r1, r2])
    w = max(d0.textlength(r1, font=f1), d0.textlength(r2, font=f2)) + 110
    if w > W - 60: LAYOUT.add(f"plaatskaart '{r1}' te breed")
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
def rhand(naam, x, y, s, hoek):                            # rechterhand bij armhoek (0 = omlaag, 90 = opzij)
    S = s * ps.C[naam].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S
GEZ = {}
def teken(img, figs, t, nu):                                # figs: (naam, x, y, s, gebaar, zit[, kijk[, loop]])
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    for f_ in figs:
        naam, x, y, s, geb, zit = f_[:6]
        kijk = f_[6] if len(f_) > 6 and f_[6] is not None else (0.5 if x < 540 else -0.5)
        loop = f_[7] if len(f_) > 7 else None
        emo = emotie(t, nu) if (sp is None or naam == sp) else None
        koppen[naam] = ps.poppetje(d, naam, x, y, s, t, loop=loop, kijk=kijk, mond=luid(t, naam), knipper=(t + hash(naam) % 7 * 0.4) % 3.4 < 0.13,
                                   verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=geb if loop is None else "rennen")
        GEZ[naam] = (*hoofd(naam, x, y, s), s * ps.C[naam].get("groot", 1)); GEB[naam] = geb
        WACHT.persoon(naam, y, 306 * s * ps.C[naam].get("groot", 1), zit=zit)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); return koppen

# ---------- voorwerpen ----------
def winkelkar(d, x, voet, h, inhoud=0.0, naam="winkelkar", op="vloer"):   # winkelwagen (zelf getekend), x = midden, h = hoogte; inhoud 0..1 vol dozen
    w = h * 1.05; x0 = x - w / 2; bak = voet - h * 0.22; lw = max(3, int(h / 40))
    WACHT.plaats(naam, (x0, voet - h, x0 + w, voet), op=op)
    for k_ in range(int(inhoud * 6)):                      # dozen in de kar
        bx = x0 + w * 0.12 + (k_ % 3) * w * 0.26; by = bak - h * 0.5 - (k_ // 3) * h * 0.24
        d.rectangle((bx, by, bx + w * 0.24, by + h * 0.24), fill=(200, 160, 105), outline=INK, width=3)
    d.line([(x0, voet - h * 0.85), (x0 + w, voet - h * 0.85), (x0 + w * 0.88, bak), (x0 + w * 0.1, bak), (x0, voet - h * 0.85)], fill=(120, 125, 135), width=lw)
    for k_ in range(1, 5): d.line((x0 + w * k_ / 5, voet - h * 0.85, x0 + w * 0.1 + (w * 0.78) * k_ / 5, bak), fill=(170, 175, 185), width=max(2, lw - 1))
    d.line((x0 - w * 0.12, voet - h, x0, voet - h * 0.85), fill=(90, 95, 105), width=lw + 2)
    d.line((x0 + w * 0.1, bak, x0 + w * 0.15, voet - h * 0.08), fill=(120, 125, 135), width=lw)
    d.line((x0 + w * 0.88, bak, x0 + w * 0.85, voet - h * 0.08), fill=(120, 125, 135), width=lw)
    for wx in (x0 + w * 0.15, x0 + w * 0.85): d.ellipse((wx - h * 0.06, voet - h * 0.12, wx + h * 0.06, voet), fill=INK)
def tvdoos(d, x, y, w, h):                                 # kartonnen doos met een plaatje van een tv erop (geen letters)
    d.rectangle((x, y, x + w, y + h), fill=(200, 160, 105), outline=INK, width=4)
    d.rectangle((x + w * 0.22, y + h * 0.25, x + w * 0.78, y + h * 0.68), fill=(30, 30, 38), outline=INK, width=3)
    d.rectangle((x + w * 0.45, y + h * 0.68, x + w * 0.55, y + h * 0.78), fill=(30, 30, 38))
def twintig(img, t):                                       # "I'll take twenty!": 20 tv-dozen (5 x 4) verschijnen achter papa op de vloer
    if t < T_20: return
    d = ImageDraw.Draw(img); v = 1500; m = pxm("mall-tv", v); w_, h_ = 0.62 * m, 0.46 * m; x0 = 540 - 2.5 * w_
    n = min(20, 1 + int((t - T_20) / 0.04))
    WACHT.plaats("tvdoos", (x0, v - 4 * h_, x0 + 5 * w_, v), op="vloer")
    for k_ in range(n): c, r = k_ % 5, k_ // 5; tvdoos(d, x0 + c * w_, v - (r + 1) * h_, w_ - 5, h_ - 4)
def prijskaart(d, x, y, tekst, sch):                       # prijsbordje (grafiek bovenop het beeld)
    w = 130 + 34 * len(tekst); SCHERM.append(tekst)
    d.rounded_rectangle((x - w / 2 * sch, y - 60 * sch, x + w / 2 * sch, y + 60 * sch), int(18 * sch) + 1, fill=(255, 255, 255), outline=INK, width=5)
    if sch > 0.3: d.text((x, y), tekst, font=font(FB, int(78 * sch)), fill=(220, 40, 40), anchor="mm")
def doos(d, x, voet, w, h):
    x0, y0 = x - w / 2, voet - h
    d.rectangle((x0, y0, x0 + w, voet), fill=(200, 160, 105), outline=INK, width=4)
    d.rectangle((x - w * 0.09, y0, x + w * 0.09, y0 + h * 0.35), fill=(225, 200, 150), outline=(160, 120, 75), width=2)
    d.line((x0 + 6, y0 + h * 0.18, x0 + w - 6, y0 + h * 0.18), fill=(170, 130, 85), width=3)
DOZEN_ACHTER = [(x, 1270, 190, 150) for x in (100, 290, 480, 670, 860, 1030)] + [(x, 1430, 210, 170) for x in (60, 260, 470, 980)]
DOZEN_VOOR = [(x, 1960, 250, 230) for x in (80, 580, 830, 1060)]
def dozenzee(img, voor):
    d = ImageDraw.Draw(img)
    for x, v, w, h in (DOZEN_VOOR if voor else DOZEN_ACHTER):
        WACHT.plaats("doos", (x - w / 2, v - h, x + w / 2, min(v, H - 4)), op="vloer"); doos(d, x, v, w, h)
TENT_VOET = 1395
def tentkamp(img, t, voor):                                # papa's kamp op de parkeerplaats: tent, slaapzak, kar, koffie, bordje op de deur
    d = ImageDraw.Draw(img)
    if not voor:
        bx, by = 540, 900; WACHT.plaats("bord-restock", (bx - 95, by - 70, bx + 95, by + 70), op="muur")   # bordje achter het glas van de deur
        d.rectangle((bx - 95, by - 70, bx + 95, by + 70), fill=(255, 250, 235), outline=INK, width=4)
        d.text((bx, by - 28), "RESTOCK", font=font(FB, 40), fill=(220, 40, 40), anchor="mm"); d.text((bx, by + 26), "6 AM", font=font(FB, 52), fill=INK, anchor="mm")
        SCHERM.append("RESTOCK 6 AM")
        zet(img, "tent", 380, 300, TENT_VOET, op="stoep", naam="tent")
    else:                                                  # slaapzak over papa's benen (hij zit in de tentopening)
        x0, x1, y0, y1 = 170, 470, 1290, 1400; WACHT.plaats("slaapzak", (x0, y0, x1, y1), op="stoep")
        d.rounded_rectangle((x0, y0, x1, y1), 40, fill=(60, 110, 170), outline=INK, width=5)
        d.line((x0 + 30, y0 + 30, x1 - 30, y0 + 30), fill=(40, 80, 130), width=5)
def koffie(img, hx, hy, S, t):                              # koffiebeker in papa's hand, met damp
    d = ImageDraw.Draw(img); w, h = 22 * S, 30 * S
    WACHT.plaats("koffie", (hx - w / 2, hy - h, hx + w / 2, hy + 4), op="hand:dad", punt=(hx, hy), voor=True)
    d.polygon([(hx - w / 2, hy - h), (hx + w / 2, hy - h), (hx + w * 0.38, hy + 4), (hx - w * 0.38, hy + 4)], fill=(250, 250, 245), outline=INK)
    d.rectangle((hx - w / 2, hy - h * 0.62, hx + w / 2, hy - h * 0.38), fill=(170, 110, 70))
    for k_ in range(3):
        pts = [(hx - 8 * S + k_ * 8 * S + math.sin(t * 3 + q * 0.8 + k_) * 4 * S, hy - h - 6 * S - q * 7 * S) for q in range(5)]
        d.line(pts, fill=(235, 235, 240), width=max(2, int(1.6 * S)))
MANDEN = []                                                # 47 hondenmanden (er staan er echt 47)
for y_, h_, xs in ((1060, 70, range(240, 800, 92)), (1175, 85, range(240, 800, 92)), (1300, 100, range(60, 1040, 108)),
                   (1440, 115, range(70, 1040, 120)), (1600, 130, [80, 240, 860, 1010]), (1780, 145, [90, 260, 830, 1000]),
                   (1915, 150, [80, 260, 440, 620, 800, 980])):
    MANDEN += [(x_, y_, h_) for x_ in xs]
assert len(MANDEN) == 47, len(MANDEN)
def manden(img):
    for x_, y_, h_ in MANDEN: zet(img, "hondenmand", h_, x_, y_, op="vloer", naam="hondenmand")
def hond(img, t):                                          # de hond ligt op de kale vloer
    zet(img, "hond", 360, 470, 1790, op="vloer", naam="hond")
MUUR_TV = [(x, 50, 150, 100) for x in (60, 230, 400, 570, 740, 910)] + [(495, 200, 150, 100), (495, 330, 150, 100), (915, 200, 150, 100), (915, 330, 150, 100)]
assert len(MUUR_TV) == 10                                   # 26 nov (eigenaar): bij kerst hangen er al 10 tv's aan de muur; het cadeau is de 11e
def tv_muur(img):
    d = ImageDraw.Draw(img)
    for x, y, w, h in MUUR_TV:
        WACHT.plaats("tv-muur", (x, y, x + w, y + h), op="muur")
        d.rounded_rectangle((x, y, x + w, y + h), 8, fill=(30, 30, 38), outline=INK, width=4); d.rectangle((x + 8, y + 8, x + w - 8, y + h - 8), fill=(45, 55, 85))
        d.line((x + 14, y + 16, x + 40, y + 16), fill=(90, 105, 150), width=3)
KADO = (540, 1330)
def cadeau(img, t):                                        # papa geeft het cadeau; bij "another TV" is het papier eraf en staat er een tv
    d = ImageDraw.Draw(img); x, v = KADO; m = pxm("kerst", v); w, h = 0.7 * m, 0.55 * m
    if t < T_TVK:
        WACHT.plaats("cadeau", (x - w / 2, v - h, x + w / 2, v), op="vloer")
        d.rectangle((x - w / 2, v - h, x + w / 2, v), fill=(215, 45, 55), outline=INK, width=5)
        d.rectangle((x - 22, v - h, x + 22, v), fill=(255, 210, 60)); d.rectangle((x - w / 2, v - h / 2 - 20, x + w / 2, v - h / 2 + 20), fill=(255, 210, 60))
        d.ellipse((x - 90, v - h - 55, x - 6, v - h + 10), fill=(255, 210, 60), outline=INK, width=3); d.ellipse((x + 6, v - h - 55, x + 90, v - h + 10), fill=(255, 210, 60), outline=INK, width=3)
    else:
        zet(img, "tv", int(h * 1.1), x, v, op="vloer", naam="tv")
        for dx, dy in ((-w * 0.7, -10), (w * 0.65, -25), (-w * 0.5, 25), (w * 0.75, 20)):
            px, py = x + dx, v + dy; d.polygon([(px - 40, py), (px + 32, py - 22), (px + 42, py + 14), (px - 26, py + 28)], fill=(215, 45, 55), outline=INK)
def failliet(img, t):                                       # lege mall: omgevallen SALE-bord, rollende papiertjes, lege kar die wegrolt
    d = ImageDraw.Draw(img); bx, bv = 760, 1380; m = pxm("failliet", bv)
    WACHT.plaats("sale-bord", (bx - 0.8 * m, bv - 0.35 * m, bx + 0.8 * m, bv), op="vloer")
    d.polygon([(bx - 0.8 * m, bv - 0.1 * m), (bx + 0.7 * m, bv - 0.35 * m), (bx + 0.8 * m, bv - 0.05 * m), (bx - 0.7 * m, bv)], fill=(235, 60, 60), outline=INK)
    d.text((bx, bv - 0.18 * m), "SALE", font=font(FB, int(0.26 * m)), fill=(255, 255, 255), anchor="mm")
    d.line((bx - 0.05 * m, bv - 0.3 * m, bx + 0.15 * m, bv - 0.05 * m), fill=INK, width=4)                  # barst
    for k_ in range(2):                                    # papiertjes waaien over de vloer
        px = (200 + k_ * 380 + (t - Z[I_FAIL][0]) * 140) % 640 + 240; pv = 1560 + k_ * 160; r = 22 + k_ * 6
        WACHT.plaats("papiertje", (px - r, pv - 2 * r, px + r, pv), op="vloer"); a = t * 5 + k_
        d.polygon([(px + math.cos(a + q * 2.1) * r, pv - r + math.sin(a + q * 2.1) * r) for q in range(3)], fill=(240, 235, 220), outline=INK)
def winkeltje(img, t, stap):                               # laatste winkel: telefoon in de vitrine, prijskaartje, tv met CYBER MONDAY
    d = ImageDraw.Draw(img)
    if stap == "achter":
        tx0, ty0, tx1, ty1 = 330, 300, 600, 420                                                      # tv op de bovenste plank
        WACHT.plaats("tv-scherm", (tx0, ty0, tx1, ty1 + 10), op="plank")
        d.rectangle((tx0, ty0, tx1, ty1), fill=(25, 25, 32), outline=INK, width=5); d.rectangle((tx0 + 12, ty0 + 12, tx1 - 12, ty1 - 12), fill=(20, 30, 60) if t < T_CYBER else (30, 140, 210))
        d.rectangle(((tx0 + tx1) / 2 - 15, ty1, (tx0 + tx1) / 2 + 15, ty1 + 10), fill=(25, 25, 32))
        if t >= T_CYBER:
            s_ = ps.pop((t - T_CYBER) / 0.3); SCHERM.append("CYBER MONDAY")
            d.text(((tx0 + tx1) / 2, ty0 + 40), "CYBER", font=font(FB, int(44 * s_) + 1), fill=(255, 255, 255), anchor="mm")
            d.text(((tx0 + tx1) / 2, ty0 + 84), "MONDAY", font=font(FB, int(40 * s_) + 1), fill=(255, 230, 80), anchor="mm")
        zet(img, "telefoon", 72, 455, 872, op="toonbank", naam="telefoon")                        # één telefoon in de glazen vitrine
        if t >= T_PRIJS:
            s_ = ps.pop((t - T_PRIJS) / 0.3); px, py = 560, 852
            WACHT.plaats("prijskaartje", (px - 52, py - 26, px + 52, py + 20), op="toonbank")
            d.rounded_rectangle((px - 52 * s_, py - 24 * s_, px + 52 * s_, py + 18 * s_), 6, fill=(255, 255, 255), outline=INK, width=3)
            if s_ > 0.3: d.text((px, py - 3), "$1,000", font=font(FB, int(24 * s_)), fill=(220, 40, 40), anchor="mm"); SCHERM.append("$1,000")
    else:                                                  # toonbank vóór de kassière (stuk achtergrond opnieuw erover)
        img.paste(bg("winkeltje").crop((560, 868, 1080, 1300)), (560, 868))

# ---------- indeling per scène: (naam, x, voet, schaal, gebaar, zit, kijk, loop) ----------
def figuren(n, t):
    nu = nu_i(t)
    if n == "winkel":
        y = 1720; s = schaal("mall-tv", "dad", y)
        if t >= Z[I_TWINTIG][0] - 0.3: return [("dad", 330, y, s, "juich", False, 0.3)]
        a = ps.ease(min(1, max(0, t - 3.6) / 0.8)); x = 540 + (330 - 540) * a; loop = (t - 3.6) * 2.2 if 0 < a < 1 else None
        return [("dad", x, y, s, "armen-open" if t >= T_90 and loop is None else None, False, math.sin(t * 2.2) * 0.9, loop)]
    if n == "dozen":
        f = [("dad", 780, 1600, schaal("woonkamer", "dad", 1600), "armen-open" if nu == I_WEEK2 else None, False, -0.9 if t >= T_SISIN else 0.0)]
        if t >= T_SISIN:                                   # zus loopt van links tussen de dozen naar papa
            a = ps.ease(min(1, (t - T_SISIN) / 1.1)); x = -120 + (430 + 120) * a; loop = (t - T_SISIN) * 2.2 if a < 1 else None
            f.append(("sis", x, 1680, schaal("woonkamer", "sis", 1680), "armen-open" if nu == I_SIS else None, False, 0.9, loop))
        return f
    if n == "tent":
        return [("dad", 320, 1400, schaal("buiten-nacht", "dad", 1400), "wijs" if nu == I_RESTOCK else ("hoek", -16, 55), True, 0.9 if nu == I_RESTOCK else 0.3)]
    if n == "hond":
        return [("you", 760, 1600, schaal("woonkamer", "you", 1600), "wijslinks" if nu == I_WAAROM else None, False, -0.9)]
    if n == "feit":
        return [("agent", 640, 1850, schaal("straat-oud", "agent", 1850), "hoofdhanden" if nu == I_AGENT else None, False, 0.0 if nu == I_AGENT else -0.4)]
    if n == "kerst":
        y = 1300                                            # iets kleiner, zodat de 10 tv's aan de muur boven hun hoofd te zien zijn
        return [("dad", 250, y, schaal("kerst", "dad", y, 0.8), ("hoek", -16, 60) if t < T_TVK else None, False, 0.9),
                ("you", 830, y, schaal("kerst", "you", y, 0.8), None, False, -0.6 if nu != I_ELF else 0.0)]
    if n == "failliet":
        y = 1500; a = ps.ease(min(1, (t - Z[I_FAIL][0]) / 3.0)); x = 140 + (500 - 140) * a; loop = (t - Z[I_FAIL][0]) * 2.0 if a < 1 else None
        kijk = math.sin(t * 2.5) * 0.9 if nu != I_SALE else 0.0
        return [("dad", x, y, schaal("failliet", "dad", y), "armen-open" if nu == I_SALE else None, False, kijk, loop)]
    if n == "laatst":
        y = 1350; a = ps.ease(min(1, (t - T_DADIN) / 1.2)); x = -150 + (190 + 150) * a; loop = (t - T_DADIN) * 2.2 if a < 1 else None
        dg = ("hoek", -16, 140) if nu == I_LAATST and t >= T_PRIJS else ("schrik" if nu == I_ROOF else None)
        kg = ("hoek", -150, -16) if nu == I_KASSA and t >= T_CYBER else None                # kassière wijst naar de tv
        dkijk = 0.0 if t >= Z[I_SLOT][0] else 0.8
        return [("kassa", 760, 1150, schaal("winkeltje", "kassa", 1150), kg, True, -0.6),
                ("dad", x, y, schaal("winkeltje", "dad", y), dg, False, dkijk, loop)]
    return []

# ---------- camera (volgt de spreker, zacht) ----------
SCENE_MID = {"winkel": (540, 1250), "dozen": (540, 1300), "tent": (500, 1150), "hond": (540, 1300), "feit": (540, 1350),
             "kerst": (540, 1050), "failliet": (540, 1200), "laatst": (540, 1100)}
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = nu_i(t)
    cx, cy = SCENE_MID[n]; zm = 1.0 + min(0.12, (t - sc["t"]) * 0.03)
    if n == "winkel" and t < 3.6: zm = 1.0 + t * 0.06                                       # opening: rustig inzoomen op papa
    if nu is not None and Z[nu][4] in LIJF and LIJF[Z[nu][4]] != "mascotte":
        naam = LIJF[Z[nu][4]]
        for f in figuren(n, t):
            if f[0] == naam: hx, hy = hoofd(*f[:4]); cx, cy, zm = hx, hy + 300, 1.3
    if n == "winkel" and nu == I_TWINTIG and t >= T_20: cx, cy, zm = 540, 1300, 1.05       # de 20 dozen
    if n == "tent": zm = 1.0 + min(0.2, (t - sc["t"]) * 0.05); cx, cy = 420, 1150         # langzaam naar de tent
    if n == "kerst": cx, cy, zm = 540, 960, 1.0                                            # wijd: alle 10 tv's aan de muur in beeld
    if n == "laatst" and T_PRIJS <= t < Z[I_ROOF][0]: cx, cy, zm = 470, 900, 1.6           # vitrine met telefoon en prijskaartje
    if n == "laatst" and nu == I_KASSA: cx, cy, zm = 560, 800, 1.25
    if n == "laatst" and t >= Z[I_SLOT][0]: cx, cy, zm = 260, 900, 1.5                      # papa draait naar de camera
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz * (1.0 if i == 0 else 0.92)
        a = 0.06 if not (n == "laatst" and T_PRIJS <= t < T_PRIJS + 0.6) else 0.18
        cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter: wat genoemd wordt, moet in beeld zijn
ZIE = {"ninety percent": ["tekst:-90%"], "tvs": ["tvdoos", "tekst:TV $9"], "twenty": ["tvdoos"], "warehouse": ["doos"],
       "parking lot": ["tent"], "restock": ["bord-restock"], "forty-seven": ["hondenmand"], "dog": ["hond"],
       "the floor": ["hond"], "police": ["agent"], "philadelphia": ["tekst:PHILADELPHIA"], "another tv": ["tv", "cadeau"],
       "eleventh": ["tv-muur"], "boxes": ["doos"], "bankrupt": ["tekst:CLOSED"], "sale?!": ["sale-bord"], "phone": ["telefoon"],
       "thousand dollars": ["tekst:$1,000", "prijskaartje"], "cyber monday": ["tekst:CYBER MONDAY"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)

def frame(t):
    t_b = min(t, Z[-1][1] + 0.6)                                                          # daarna bevroren eindbeeld
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b)
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t_b); GEZ.clear(); GEB.clear(); SCHERM.clear(); d = ImageDraw.Draw(img)
    figs = figuren(n, t_b)
    if n == "winkel":
        twintig(img, t_b)
    if n == "dozen": dozenzee(img, False)
    if n == "tent": tentkamp(img, t_b, False)
    if n == "hond": manden(img); hond(img, t_b)
    if n == "failliet": failliet(img, t_b)
    if n == "laatst": winkeltje(img, t_b, "achter")
    if n == "kerst": tv_muur(img)
    if n == "kerst" and t_b >= T_TVK: cadeau(img, t_b)
    if n == "laatst":                                                                      # kassière achter de toonbank, dan de toonbank ervoor
        koppen = teken(img, figs[:1], t_b, nu); winkeltje(img, t_b, "voor"); koppen.update(teken(img, figs[1:], t_b, nu))
    else: koppen = teken(img, figs, t_b, nu)
    if n == "dozen": dozenzee(img, True)
    if n == "tent":
        tentkamp(img, t_b, True); f = figs[0]
        if f[4] != "wijs": hx, hy = rhand("dad", f[1], f[2], f[3], 55); koffie(img, hx, hy, f[3] * ps.C["dad"]["groot"], t_b)
    if n == "kerst" and t_b < T_TVK: cadeau(img, t_b)
    ps.W, ps.H = W, H
    for naam, (hx_, top_) in koppen.items():
        tekst, kl = NAAM[naam]
        if tekst: ps.label(img, tekst, hx_, top_ - 45, kl, 0.55)
    img = camera(img, t)
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    for naam, (hx_, top_) in koppen.items():
        tekst, kl = NAAM[naam]
        if tekst: bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, ((hx_ - bw_ / 2 - cx0) * zm_, (top_ - 70 - cy0) * zm_, (hx_ + bw_ / 2 - cx0) * zm_, (top_ - 20 - cy0) * zm_)))
    if TEKST_AAN:
        d = ImageDraw.Draw(img)
        plaatskaart(img, t_b, sc)
        if n == "winkel" and nu == I_HOOK and t_b >= T_90: kop(img, "-90%", W / 2, 400, 200, (235, 45, 45), ps.pop((t_b - T_90) / 0.35))
        if n == "winkel" and nu == I_HOOK and t_b >= T_NOOIT: kop(img, "SALE ENDS: NEVER", W / 2, 580, 70, KL["geel"], ps.pop((t_b - T_NOOIT) / 0.3))
        if n == "winkel" and nu == I_TWINTIG and t_b >= T_9: prijskaart(d, W / 2, 400, "TV $9", ps.pop((t_b - T_9) / 0.3))
        if n == "winkel" and nu == I_TWINTIG and t_b >= T_20: kop(img, "x20", W / 2, 560, 110, (255, 255, 255), ps.pop((t_b - T_20) / 0.3))
        if n == "hond" and t_b >= T_BED: kop(img, "47 BEDS", W / 2, 400, 110, (255, 255, 255), ps.pop((t_b - T_BED) / 0.3))
        if n == "feit" and t_b >= T_POLITIE: kop(img, "PHILADELPHIA POLICE", W / 2, 400, 64, (255, 255, 255), ps.pop((t_b - T_POLITIE) / 0.3))
        if n == "kerst" and t_b >= T_ELFDE: kop(img, "TV #11", W / 2, 1300, 100, KL["geel"], ps.pop((t_b - T_ELFDE) / 0.3))
        if n == "failliet" and t_b >= T_BANK: kop(img, "CLOSED", W / 2, 400, 130, (255, 90, 80), ps.pop((t_b - T_BANK) / 0.3))
        if n == "laatst" and T_1000 <= t_b < T_CYBER: kop(img, "$1,000", W / 2, 1240, 140, (235, 45, 45), ps.pop((t_b - T_1000) / 0.35))
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1]) for k_, v in GEZ.items()}, gebaren=dict(GEB), crop=CROP[0])
    return img

# ---------- geluid: ECHTE opnames (CC0, ../geluiden), alleen wat je ziet ----------
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
    piep = _fade(_drukste(_laad("scanner"), 0.15))
    for q in range(0, 20, 2): zet_(T_20 + q * 0.02, "scanner", piep, 0.3, "tvdoos")                    # piepjes: de dozen komen erbij
    for q in np.arange(T_SISIN + 0.2, T_SISIN + 1.1, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.3, "sis")
    zet_(T_TVK - 0.05, "papier", _fade(_drukste(_laad("papier"), 0.4)), 0.4, "tv")
    for q in np.arange(T_DADIN + 0.2, T_DADIN + 1.2, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.35, "dad")
    zet_(T_CYBER, "kassa", _fade(_laad("kassa")), 0.45, "tv-scherm")
    uit /= max(1, np.abs(uit).max() / 0.9)
    sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
        frame(t + 0.15); gezien = {x[0] for x in WACHT.dit_frame} | set(GEZ)
        if zie not in gezien: fout.append(f"{t:.1f} s: geluid '{n}' maar '{zie}' is niet in beeld")
    return fout

if __name__ == "__main__":
    if "--tekst" in sys.argv:                               # snelle controle zonder video (6 beelden per seconde)
        for i in range(int(EIND * 6)): frame(i / 6)
        print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); print("LAYOUT:", sorted(LAYOUT) or "alles past"); sys.exit()
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 10, 480 * 2)); [pl.paste(im, (270 * (i % 10), 480 * (i // 10))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); sys.exit()
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-blackfriday.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-blackfriday.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    print("KLAAR short-blackfriday.mp4", round(EIND, 1), "s")
