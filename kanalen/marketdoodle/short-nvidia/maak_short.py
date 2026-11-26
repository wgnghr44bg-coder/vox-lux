"""v4 (26 nov): script van de eigenaar; oude 2D-poppetjes, herkenbare Jensen, kleine naamlabels, zitten, plaatstitels met animatie, camera volgt de spreker.
Short 'What If You Invested $100 in NVIDIA?' (26 nov 2026), staand 1080x1920. Echt verhaal (Denny's 1993, NV1, Sega, beursgang 1999, AI),
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
from tekstwachter import Tekstwachter, blad

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

# ---------- personages v3 (eigenaar 26 nov: "hou het op de oude style 2D", Jensen herkenbaar, kleine naamlabels, zitten, camera) ----------
sys.path.insert(0, str(HIER.parent / "personage")); from jensen_proef import JENSEN_1993, JENSEN_NU
ps.C["jensen"] = JENSEN_1993; ps.C["jensennu"] = JENSEN_NU
ps.C["chris"] = dict(broek=(80, 70, 60), shirt=(150, 190, 230), haar=(80, 55, 35), kapsel="kort", baard=True, groot=1.12)
ps.C["curtis"] = dict(broek=(60, 70, 90), shirt=(80, 130, 80), haar=(120, 80, 45), kapsel="krul", baard=True, bril=True, groot=1.1)
ps.C["serveerster"] = dict(broek=(200, 90, 110), shirt=(120, 180, 230), haar=(225, 190, 95), kapsel="paard", jurk=True, groot=1.0)
ps.C["sega"] = dict(broek=(40, 40, 48), shirt=(70, 72, 82), haar=(135, 135, 140), kapsel="grijs", bril=True, das=(150, 30, 40), groot=1.05)
ps.C["onderzoeker"] = dict(broek=(50, 55, 70), shirt=(60, 120, 80), haar=(30, 25, 25), kapsel="paard", hoodie=True, groot=0.98)
ps.C["collega"] = dict(broek=(55, 55, 65), shirt=(110, 110, 120), haar=(45, 35, 30), kapsel="krul", koptelefoon=True, groot=1.05)
ps.C["jij99"] = dict(ps.C["you"], shirt=(130, 130, 140), hoodie=True)
ps.C["jijoud"] = dict(ps.C["you"], haar=(140, 130, 125), hoodie=False, shirt=(45, 65, 110), groot=1.12)
LIJF = {"YOU": "you", "YOU2": "jijoud", "JENSEN": "jensen", "JENSEN2": "jensennu", "SERVEERSTER": "serveerster",
        "CURTIS": "curtis", "SEGA": "sega", "ONDERZOEKER": "onderzoeker"}
NAAM = {"you": ("YOU", (255, 215, 60)), "jij99": ("YOU", (255, 215, 60)), "jijoud": ("YOU", (255, 215, 60)),
        "jensen": ("JENSEN", (118, 185, 0)), "jensennu": ("JENSEN", (118, 185, 0)), "chris": ("CHRIS", (120, 200, 255)),
        "curtis": ("CURTIS", (255, 190, 80)), "serveerster": ("WAITRESS", (255, 140, 170)), "sega": ("SEGA BOSS", (255, 110, 110)),
        "onderzoeker": ("RESEARCHER", (120, 220, 200)), "collega": ("ENGINEER", (200, 170, 255))}
def luid(t, naam):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == naam for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

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
LAYOUT = set(); TEKST_AAN = True; SCHERM = []; GEB = {}; CROP = [None]; LABELS = []
def kop(img, s, x, y, m, kl, sch):
    SCHERM.append(s)
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if x is None: x = 50 + w / 2
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    if sch >= 1:                                            # 26 nov: kop mag niet over een naamlabel vallen
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

# ---------- indeling per scène: (poppetje, x, voet, schaal, gebaar, zit) ----------
TAFEL_Y = 1560
ZY = TAFEL_Y + 140                                         # voet van iemand die zit (onderlijf achter de tafel)
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)
def hoofd(naam, x, y, s, *_):                              # midden van het hoofd (camera, scènewachter)
    S = s * ps.C[naam].get("groot", 1.0); return x, y - 246 * S
def rhand(naam, x, y, s, hoek):                            # rechterhand bij armhoek (0 = omlaag, 90 = opzij)
    S = s * ps.C[naam].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S
def teken(img, figs, t, nu):                               # poppetjes op één laag; geeft hoofdposities terug
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    spx = next((f[1] for f in figs if f[0] == sp), None)
    for f_ in figs:
        naam, x, y, s, geb, zit = f_[:6]
        kijk = (0.9 if spx > x else -0.9) if spx is not None and naam != sp else (0.5 if x < 540 else -0.5)
        if len(f_) > 6: kijk = f_[6]                       # vaste kijkrichting (bv. van de pc weg kijken)
        emo = emotie(t, nu) if (sp is None or naam == sp) else None
        loop = t * 2.2 if geb == "rennen" else None
        koppen[naam] = ps.poppetje(d, naam, x, y, s, t, loop=loop, kijk=kijk, mond=luid(t, naam), knipper=(t + hash(naam) % 7 * 0.4) % 3.4 < 0.13,
                                   verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=None if geb == "rennen" else geb)
        GEZ[naam] = (*hoofd(naam, x, y, s), s * ps.C[naam].get("groot", 1)); GEB[naam] = geb
        WACHT.persoon(naam, y, 306 * s * ps.C[naam].get("groot", 1), zit=zit)                 # maatwachter: klopt de grootte met de kamer?
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); return koppen
def plaatskaart(img, t, sc):                               # 26 nov (eigenaar: "label Denny's 1993 met motion graphics"): titel schuift in en weer uit
    dt = t - sc["t"]; r1, r2 = PLAATS[sc["naam"]]
    if dt > 2.8:
        kop(img, JAAR[sc["naam"]], None, 150, 70, KL["geel"], 1.0); return
    f1, f2 = font(FB, 74), font(FS, 44); d0 = ImageDraw.Draw(img); SCHERM.extend([r1, r2])
    w = max(d0.textlength(r1, font=f1), d0.textlength(r2, font=f2)) + 110
    if w > W - 60: LAYOUT.add(f"plaatskaart '{r1}' te breed")
    inn = ps.ease(dt / 0.4); uit = ps.ease(max(0.0, dt - 2.4) / 0.4); x0 = 40 - (w + 60) * (1 - inn) - (w + 60) * uit; y0 = 110
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.rounded_rectangle((x0 + 8, y0 + 10, x0 + w + 8, y0 + 190), 22, fill=(0, 0, 0, 110))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + 180), 22, fill=(18, 20, 26, 235))
    d.rectangle((x0, y0 + 14, x0 + 14, y0 + 166), fill=(118, 185, 0, 255))
    lijn = min(1.0, max(0.0, (dt - 0.25) / 0.5)); d.rectangle((x0 + 44, y0 + 104, x0 + 44 + (w - 90) * lijn, y0 + 108), fill=(118, 185, 0, 255))
    d.text((x0 + 44, y0 + 18), r1, font=f1, fill=(255, 255, 255, 255))
    n_ = int(len(r2) * min(1.0, max(0.0, (dt - 0.45) / 0.6)))                      # typemachine
    d.text((x0 + 46, y0 + 118), r2[:n_], font=f2, fill=(170, 230, 90, 255))
    img.paste(laag, (0, 0), laag)

# ---------- meubels en spullen ----------
def bank_achter(d, x0, x1):
    d.rounded_rectangle((x0, TAFEL_Y - 520, x1, TAFEL_Y + 20), 30, fill=(205, 60, 60), outline=INK, width=5)
    for k in range(int((x1 - x0) / 90)): d.line((x0 + 45 + k * 90, TAFEL_Y - 490, x0 + 45 + k * 90, TAFEL_Y), fill=(175, 45, 45), width=4)
def tafel(d, x0, x1, blad=(235, 230, 220), voor=(205, 60, 60), naam="tafel"):   # tafelblad + voorkant (bankje of bureau): bovenlijf erachter
    WACHT.vlak(naam, [x0, x1, TAFEL_Y - 10, TAFEL_Y + 16], staat_op="beeldrand", voet=(x0, x1, H + 40))
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


# ---------- v4 (26 nov 2026): script van de eigenaar "What If You Invested $100 in NVIDIA in 1999?" ----------
ps.C["jijpyjama"] = dict(ps.C["you"], haar=(140, 130, 125), hoodie=False, shirt=(150, 185, 235), groot=1.12)     # 2026: pyjama, grijze slapen
ps.C["gamer1"] = dict(broek=(50, 60, 90), shirt=(230, 90, 60), haar=(240, 200, 80), kapsel="krul", groot=0.95)
ps.C["gamer2"] = dict(broek=(40, 40, 45), shirt=(60, 170, 90), haar=(30, 25, 25), kapsel="kort", pet=(200, 40, 40), groot=1.0)
LIJF.update({"YOU": "jij99", "YOU2": "jijpyjama"})
NAAM.update({"jijpyjama": ("YOU", (255, 215, 60)), "gamer1": ("", (0, 0, 0)), "gamer2": ("", (0, 0, 0))})
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_HOOK, I_RIJK, I_OFFER, I_GELD, I_PLAN, I_FINE, I_DEAL = zi("What if"), zi("Wait"), zi("Hey!"), zi("Does it"), zi("That's the plan"), zi("Fine."), zi("Deal")
I_JAREN, I_ALIVE, I_GAME, I_BABY, I_AI, I_ONDZ = zi("Years pass"), zi("Is this"), zi("Then PC"), zi("Look at"), zi("Then artificial"), zi("We need")
I_FORT, I_ISLAND, I_CONGR, I_RETIRE, I_VRAAG, I_SOLD, I_WHY, I_PS2, I_SLOT = (zi("Your little"), zi("I'm buying"), zi("Congratulations"),
    zi("I'm retiring"), zi("Just one"), zi("Well..."), zi("Why"), zi("I needed"), zi("I built"))
T_KOOP = 1e9; T_BILJET = kw(I_FINE, "fine", -0.1); T_HONDERD = kw(I_OFFER, "hundred", -0.1); T_620 = kw(I_FORT, "small", -0.1); T_DEUR = Z[I_CONGR][0] - 1.4; T_2002 = kw(I_SOLD, "2002", -0.1); T_CHIPS = kw(I_AI, "everyone", -0.2)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="woon", bg="woon2026"), dict(t=Zs(I_OFFER), naam="diner", bg="denny"), dict(t=Zs(I_JAREN), naam="kamer", bg="beurs"),
      dict(t=Zs(I_GAME), naam="gaming", bg="gaming"), dict(t=Zs(I_AI), naam="ai", bg="ai"), dict(t=Zs(I_FORT), naam="woon2", bg="woon2026")]
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
SCHRIK = ("Wait", "I'm buying", "Why", "I built", "Well...")
BLIJ = ("Hey!", "That's the plan", "Deal", "Look at", "We need", "Congratulations", "I'm retiring", "Fine.", "Then PC", "Then artificial")
VERDRIET = ("Is this", "I needed")
PLAATS = {"woon": ("YOUR LIVING ROOM", "2026"), "diner": ("A DINER", "SAN JOSE · 1999"), "kamer": ("YOUR BEDROOM", "2000 – 2005"),
          "gaming": ("GAME CONVENTION", "2000s"), "ai": ("AI DATA CENTER", "2023"), "woon2": ("YOUR LIVING ROOM", "2026")}
JAAR = {"woon": "2026", "diner": "1999", "kamer": "2002", "gaming": "2000s", "ai": "2023", "woon2": "2026"}
SALON_Y = 1180                                              # bovenkant salontafel vóór de bank (woon2026.png: zitting ± y 1050, rugleuning ± 840)

# maten volgens de maatwachter (achtergronden.json "maat"): ± 85-95% van de echte maat op die plek
def figuren(n, t):
    nu = nu_i(t)
    if n == "woon":
        return [("jijpyjama", 320, SALON_Y + 210, 2.1, "hoofdhanden" if nu == I_RIJK else ("hoek", -16, 40), True)]       # zit óp de bank
    if n == "diner":
        jg = ("hoek", -100, -16) if nu in (I_OFFER, I_PLAN) else ("duim" if nu == I_DEAL else None)
        yg = ("hoek", -16, 70) if nu == I_FINE else ("denk" if nu == I_GELD else None)
        return [("jij99", 300, ZY, 2.4, yg, True), ("jensen", 780, ZY, 2.3, jg, True)]
    if n == "kamer":
        if nu == I_ALIVE: return [("jij99", 800, 1330, 2.8, "denk", False, -0.9)]                                    # kijkt eindelijk naar de pc
        return [("jij99", 800, 1330, 2.8, "telefoon", False, 0.9)]                       # 'barely gets your attention': rug naar de pc, speelt op een spelcomputertje
    if n == "gaming":
        return [("gamer1", 190, 1650, 1.75, "juich" if nu == I_BABY else None, False), ("gamer2", 860, 1690, 1.8, "wijs", False),
                ("jij99", 400, 1780, 1.85, ("hoek", -16, 145) if nu == I_BABY else None, False, 0.0)]
    if n == "ai":
        chip = t >= T_CHIPS
        return [("collega", 300, 1750, 3.15, ("hoek", -16, 40) if chip else None, False), ("onderzoeker", 790, 1750, 3.4, "juich" if nu == I_ONDZ else None, False)]
    if n == "woon2":
        g = {I_ISLAND: "juich", I_RETIRE: "juich", I_SOLD: "schouders", I_PS2: "schouders"}.get(nu, ("hoek", -16, 40))
        f = [("jijpyjama", 320, SALON_Y + 210, 2.1, g, True)]
        if t >= T_DEUR:                                     # Jensen komt door de voordeur binnen (op de juiste maat bij de deur, groter vooraan)
            a = ps.ease((t - T_DEUR) / 1.3); x = 870 + (905 - 870) * a; y = 1110 + (1400 - 1110) * a; s = 1.48 + (2.43 - 1.48) * a
            jg = "rennen" if a < 1 else {I_CONGR: "duim", I_WHY: "armen-open", I_SLOT: "facepalm"}.get(nu)
            f.append(("jensennu", x, y, s, jg, False))
        return f
    return []
_LOGO = {}
def logo(hoogte, wit=False):                               # echte NVIDIA-logo (Wikimedia Commons, File:NVIDIA_logo.svg); wit = witte letters voor donkere schermen
    k = (hoogte, wit)
    if k not in _LOGO:
        im = Image.open(HIER / "afbeeldingen" / "nvidia-logo.png").convert("RGBA")
        if wit:
            px = np.array(im); donker = (px[..., 0] < 90) & (px[..., 1] < 90) & (px[..., 2] < 90); px[donker, :3] = 255; im = Image.fromarray(px)
        _LOGO[k] = im.resize((int(im.width * hoogte / im.height), hoogte), Image.LANCZOS)
    return _LOGO[k]
def plak_logo(img, x, y, hoogte, wit=False):               # x, y = linksboven
    l = logo(hoogte, wit); img.paste(l, (int(x), int(y)), l); WACHT.plaats("logo", (x, y, x + l.width, y + hoogte), op="beeld"); return l.width
def deur(d, t):                                             # voordeur (woon2026.png, rechts): gaat open als Jensen binnenkomt
    if t < T_DEUR: return
    d.rectangle((752, 432, 988, 1100), fill=(70, 60, 55)); d.polygon([(752, 432), (800, 450), (800, 1080), (752, 1100)], fill=(245, 245, 240), outline=INK)
def salontafel(d):                                         # lage salontafel: verbergt je benen, jij zit erachter op de bank
    WACHT.vlak("tafel", [120, 940, SALON_Y - 10, SALON_Y + 16], staat_op="vloer", voet=(160, 902, SALON_Y + 150))
    d.rounded_rectangle((120, SALON_Y, 940, SALON_Y + 34), 10, fill=(170, 120, 80), outline=INK, width=5)
    d.rectangle((140, SALON_Y + 34, 920, SALON_Y + 110), fill=(135, 95, 62), outline=INK, width=5)
    for x_ in (160, 880): d.rectangle((x_, SALON_Y + 110, x_ + 22, SALON_Y + 150), fill=(110, 75, 50), outline=INK, width=4)
def laptop(img, x, t, n, ty):                              # opengeklapte laptop op tafel; scherm naar de kijker met de koers + echt logo
    d = ImageDraw.Draw(img); w, h = 240, 155; x0, y0 = x - w / 2, ty - h - 14
    WACHT.plaats("laptop", (x0, y0, x0 + w, ty), op="tafel", voor=True)
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 12, fill=(55, 58, 66), outline=INK, width=5)
    sx0, sy0, sx1, sy1 = x0 + 14, y0 + 14, x0 + w - 14, y0 + h - 14; d.rectangle((sx0, sy0, sx1, sy1), fill=(12, 20, 35))
    d.polygon([(x0 - 20, ty - 14), (x0 + w + 20, ty - 14), (x0 + w + 6, ty + 2), (x0 - 6, ty + 2)], fill=(150, 152, 160), outline=INK)
    plak_logo(img, sx0 + 8, sy0 + 6, 20, wit=True); d = ImageDraw.Draw(img)
    pts = [(sx0 + 12 + k * (sx1 - sx0 - 24) / 11, sy1 - 10 - (sy1 - sy0 - 44) * (k / 11) ** 3) for k in range(12)]
    d.line(pts, fill=(120, 255, 140), width=5)
def kom(img, x, ty):                                        # kom ontbijtgranen op tafel
    zet(img, "ontbijtkom", 110, x, ty + 4, op="tafel", naam="ontbijtkom")
def krant(img, t):                                           # 26 nov (tekstwachter): krant op tafel bij "NVIDIA is going public" (beursgang jan 1999, $12 per aandeel)
    d = ImageDraw.Draw(img); x0, x1, y1 = 690, 860, TAFEL_Y + 2; y0 = y1 - 120
    WACHT.plaats("krant", (x0, y0, x1, y1), op="tafel")
    d.polygon([(x0, y1), (x1, y1), (x1 - 6, y0), (x0 + 6, y0)], fill=(245, 242, 230), outline=INK)
    d.text(((x0 + x1) / 2, y0 + 16), "GOES PUBLIC", font=font(FB, 22), fill=INK, anchor="mm")
    plak_logo(img, x0 + 30, y0 + 32, 26); d = ImageDraw.Draw(img)
    d.text(((x0 + x1) / 2, y0 + 80), "IPO · $12 A SHARE", font=font(FS, 16), fill=(90, 90, 90), anchor="mm")
    for k_ in range(2): d.line((x0 + 18, y0 + 96 + k_ * 9, x1 - 18, y0 + 96 + k_ * 9), fill=(170, 170, 170), width=3)
def biljet(d, t):                                           # $100-biljet schuift over de tafel naar Jensen
    if t < T_HONDERD: return                                 # 26 nov (tekstwachter): ligt al op tafel bij "a hundred bucks", schuift bij "Fine."
    a = ps.ease(max(0, t - T_BILJET) / 0.8); x = 420 + (640 - 420) * a; y = TAFEL_Y - 4
    WACHT.plaats("biljet", (x - 60, y - 14, x + 60, y + 4), op="tafel")
    d.polygon([(x - 60, y - 10), (x + 56, y - 14), (x + 60, y + 4), (x - 56, y + 6)], fill=(150, 205, 140), outline=(40, 90, 40))
    d.text((x, y - 4), "$100", font=font(FB, 20), fill=(30, 80, 30), anchor="mm")
def oudscherm(img, t):                                     # koers op het CRT-scherm van de pc op het bureau (beurs.png: scherm x 256-400, y 662-798)
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 258, 664, 400, 798
    WACHT.plaats("computer", (200, 620, 600, 895), op="bureau")
    d.rectangle((x0, y0, x1, y1), fill=(10, 25, 60)); plak_logo(img, x0 + 8, y0 + 8, 16, wit=True); d = ImageDraw.Draw(img)
    pts = [(x0 + 10 + k * (x1 - x0 - 20) / 7, y1 - 40 - (6 if k % 2 else 0) - (8 if k > 4 else 0)) for k in range(8)]   # koers kabbelt: bijna niks
    d.line(pts, fill=(120, 255, 140), width=3)
def kalender(d, t):                                         # scheurkalender aan de muur: de jaren vliegen voorbij
    x0, y0 = 740, 330; WACHT.plaats("kalender", (x0, y0, x0 + 180, y0 + 200), op="muur")
    jaar = 2000 + min(5, int(max(0, t - Z[I_JAREN][0]) / 0.5))
    d.rounded_rectangle((x0, y0, x0 + 180, y0 + 200), 10, fill=(255, 255, 255), outline=INK, width=5); d.rectangle((x0, y0, x0 + 180, y0 + 50), fill=(220, 60, 60))
    d.text((x0 + 90, y0 + 125), str(jaar), font=font(FB, 54), fill=INK, anchor="mm")
SCHERM_HAL = (206, 428, 842, 800)                           # binnenkant van het grote scherm in gaming.png (opgemeten met raster)
def kaartpodium(img, t):                                    # 26 nov (eigenaar: "zet de kaart op het tv-scherm of de beamer"): presentatie op het grote scherm
    T0 = kw(I_GAME, "NVIDIA", -0.1)
    if t < T0: return
    x0, y0, x1, y1 = SCHERM_HAL; w, h = x1 - x0, y1 - y0
    pres = Image.new("RGB", (w, h), (14, 16, 20)); d = ImageDraw.Draw(pres)
    for k_ in range(0, h, 6): d.line((0, k_, w, k_), fill=(14 + k_ // 30, 18 + k_ // 12, 20 + k_ // 30))                  # donker met groene gloed onderaan
    for k_ in range(3): d.line((0, h - 40 - k_ * 14, w, h - 70 - k_ * 14), fill=(118, 185, 0), width=3)
    kaart = sprite("videokaart", int(h * 0.62)); dans = math.sin(t * 2.2) * 4
    pres.paste(kaart, (int(w / 2 - kaart.width / 2), int(h * 0.30 + dans)), kaart)
    lg = logo(52, True); pres.paste(lg, (int(w / 2 - lg.width / 2), 24), lg)
    a = min(1.0, (t - T0) / 0.35)                                                                                          # overvloeien van game naar presentatie
    onder = img.crop((x0, y0, x1, y1)); img.paste(Image.blend(onder, pres, a), (x0, y0))
    WACHT.plaats("videokaart", (x0 + w / 2 - kaart.width / 2, y0 + h * 0.30, x0 + w / 2 + kaart.width / 2, y0 + h * 0.30 + kaart.height), op="beeld")
    WACHT.plaats("logo", (x0 + w / 2 - lg.width / 2, y0 + 24, x0 + w / 2 + lg.width / 2, y0 + 76), op="beeld")

def in_hand(img, naam, figs, t, wat):                          # voorwerp in de rechterhand van een poppetje (26 nov: beeld moet bij de tekst passen)
    f = next((f for f in figs if f[0] == naam), None)
    if f is None or not isinstance(f[4], (str, tuple)): return
    hoek = {"vast": 70, "telefoon": -32}.get(f[4], f[4][2] if isinstance(f[4], tuple) else None)
    if hoek is None: return
    hx, hy = rhand(naam, f[1], f[2], f[3], hoek); S = f[3] * ps.C[naam].get("groot", 1.0); d = ImageDraw.Draw(img)
    if wat == "gpu":
        k = sprite("videokaart", int(70 * S)); img.paste(k, (int(hx - k.width / 2), int(hy - k.height * 0.7)), k)
        lh = max(10, int(11 * S)); lw = logo(lh, True).width                         # NVIDIA-logo op de kaart (tekstwachter: "NVIDIA chips")
        d.rounded_rectangle((hx - lw / 2 - 6, hy - k.height * 0.7 - lh - 14, hx + lw / 2 + 6, hy - k.height * 0.7 - 2), 6, fill=(20, 20, 24))
        plak_logo(img, hx - lw / 2, hy - k.height * 0.7 - lh - 8, lh, wit=True); d = ImageDraw.Draw(img)
        WACHT.plaats("videokaart-hand", (hx - k.width / 2, hy - k.height * 0.7, hx + k.width / 2, hy + k.height * 0.3), op="hand:" + naam, punt=(hx, hy), voor=True)
    elif wat == "ps2":                                            # zwarte spelcomputer (eigen tekening, geen logo) met controller
        w, h = 150 * S, 32 * S; x0, y0 = hx - w * 0.5, hy - h - 2 * S
        d.polygon([(x0, y0 + h), (x0 + w, y0 + h), (x0 + w, y0), (x0, y0)], fill=(22, 22, 26), outline=INK)
        for k_ in range(1, 5): d.line((x0 + 8 * S, y0 + k_ * h / 5, x0 + w * 0.6, y0 + k_ * h / 5), fill=(55, 55, 65), width=max(2, int(2 * S)))
        d.rectangle((x0 + w * 0.68, y0 + h * 0.3, x0 + w * 0.92, y0 + h * 0.55), fill=(40, 40, 48)); d.ellipse((x0 + w * 0.94, y0 + h * 0.35, x0 + w * 0.94 + 5 * S, y0 + h * 0.35 + 5 * S), fill=(70, 140, 255))
        cx_, cy_ = x0 - 40 * S, y0 + h * 0.4                    # controller in de andere... aan een snoer ernaast
        d.line((x0, y0 + h * 0.6, cx_ + 20 * S, cy_), fill=INK, width=max(2, int(2 * S)))
        d.rounded_rectangle((cx_ - 30 * S, cy_ - 12 * S, cx_ + 30 * S, cy_ + 16 * S), int(10 * S), fill=(30, 30, 36), outline=INK, width=max(2, int(2 * S)))
        for k_, kl_ in enumerate(((90, 200, 120), (230, 80, 80), (80, 140, 240), (230, 120, 200))): d.ellipse((cx_ + 8 * S + (k_ % 2) * 9 * S, cy_ - 6 * S + (k_ // 2) * 9 * S, cx_ + 14 * S + (k_ % 2) * 9 * S, cy_ + (k_ // 2) * 9 * S), fill=kl_)
        WACHT.plaats("ps2-hand", (x0 - 80 * S, y0, x0 + w, y0 + h), op="hand:" + naam, punt=(hx, hy), voor=True)
    elif wat == "handheld":                                       # klein spelcomputertje (begin jaren 2000) voor de borst
        w, h = 34 * S, 48 * S; x0, y0 = hx - w / 2, hy - h * 0.8
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), int(6 * S), fill=(110, 90, 170), outline=INK, width=max(3, int(2 * S)))
        d.rectangle((x0 + 5 * S, y0 + 5 * S, x0 + w - 5 * S, y0 + h * 0.45), fill=(150, 200, 120))
        WACHT.plaats("handheld", (x0, y0, x0 + w, y0 + h), op="hand:" + naam, punt=(hx, hy), voor=True)
def ps2(img, t, n):                                            # 26 nov: de PlayStation 2 (gekocht in 2002) staat nog op de salontafel; licht op bij "I needed a PlayStation 2!"
    d = ImageDraw.Draw(img); x0, x1, y1 = 232, 412, SALON_Y + 2; y0 = y1 - 40
    WACHT.plaats("ps2", (x0, y0, x1, y1), op="tafel", voor=True)
    if n == "woon2" and nu_i(t) == I_PS2:
        r = 1 + 0.04 * math.sin(t * 8)
        for k_ in range(5): d.rounded_rectangle((x0 - 14 * r - k_ * 6, y0 - 14 * r - k_ * 6, x1 + 14 * r + k_ * 6, y1 + 6 + k_ * 3), 18, outline=(120, 170, 255), width=3)
    d.rectangle((x0, y0, x1, y1), fill=(24, 24, 28), outline=INK, width=4)                      # zwarte, platte spelcomputer (eigen tekening, geen logo)
    for k_ in range(1, 5): d.line((x0 + 10, y0 + k_ * 8, x0 + 110, y0 + k_ * 8), fill=(60, 60, 70), width=2)
    d.rectangle((x0 + 120, y0 + 12, x1 - 14, y0 + 22), fill=(45, 45, 52)); d.ellipse((x1 - 12, y0 + 28, x1 - 5, y0 + 35), fill=(70, 140, 255))
def gloed(img, t):                                              # kaart op het podium licht op als jij ernaar wijst
    if nu_i(t) != I_BABY: return
    d = ImageDraw.Draw(img); r = 120 + 12 * math.sin(t * 8)
    for k_ in range(5): d.rectangle((206 - 6 - k_ * 5 - r / 30, 428 - 6 - k_ * 5 - r / 30, 842 + 6 + k_ * 5 + r / 30, 800 + 6 + k_ * 5 + r / 30), outline=(150, 230, 40), width=3)   # scherm licht op

# ---------- camera ----------
SCENE_MID = {"woon": (540, 1080), "diner": (540, 1250), "kamer": (560, 1150), "gaming": (540, 1200), "ai": (540, 1250), "woon2": (560, 1080)}
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = nu_i(t)
    cx, cy = SCENE_MID[n]; zm = 1.0 + min(0.15, (t - sc["t"]) * 0.03)
    if n == "woon" and t < 1.6: cx, cy, zm = 560, SALON_Y - 100, 2.4                 # extreme close-up op de koers, dan snel uitzoomen
    if nu is not None and Z[nu][4] in LIJF:
        naam = LIJF[Z[nu][4]]
        for f in figuren(n, t):
            if f[0] == naam: hx, hy = hoofd(*f); cx, cy, zm = hx, hy + 260, 1.32
    if n == "gaming" and nu == I_BABY: cx, cy, zm = 540, 1150, 1.05                 # jij én de kaart waar je naar wijst
    if n == "woon2" and nu == I_PS2: cx, cy, zm = 380, SALON_Y - 180, 1.45        # jij én de PS2 op tafel
    if n == "woon2" and nu == I_FORT: cx, cy, zm = 520, SALON_Y - 200, 1.5          # de koers schiet omhoog
    if n == "woon2" and T_DEUR <= t < Z[I_CONGR][0]: cx, cy, zm = 760, 1080, 1.15   # deur gaat open
    if n == "woon2" and t > Z[I_SLOT][1]: cx, cy, zm = 320, 1000, 1.8                # bevroren eindbeeld op jouw gezicht
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz * (1.0 if i == 0 else 0.92)
        a = 0.06 if not (n == "woon" and 1.6 <= t < 2.4) else 0.2                       # snelle zoom-out na het begin
        cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter (26 nov): wat genoemd wordt, moet in beeld zijn
ZIE = {"hundred dollars": ["tekst:$100", "biljet"], "hundred bucks": ["biljet", "tekst:$100"], "nvidia": ["logo"], "graphics cards": ["videokaart"],
       "chips": ["videokaart-hand", "videokaart"], "artificial intelligence": ["tekst:AI"], "playstation": ["ps2", "ps2-hand"],
       "fortune": ["tekst:$"], "2002": ["tekst:2002"], "pc gaming": ["gamer1", "gamer2"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)
GEZ = {}
from PIL import ImageOps
def flashback(t):                                           # 26 nov (eigenaar: "zelfde achtergrond in 1999 als in 2026"): bij "back in 1999?" een oud sepia-beeld van de diner
    tb = t; T0 = kw(I_HOOK, "back", -0.1)
    img = bg("denny").copy(); WACHT.begin("v-denny", tb); GEZ.clear(); GEB.clear(); SCHERM.clear(); d = ImageDraw.Draw(img)
    bank_achter(d, 0, 1080)
    koppen = teken(img, [("jij99", 300, ZY, 2.4, None, True), ("jensen", 780, ZY, 2.3, None, True)], tb, None); d = ImageDraw.Draw(img)
    tafel(d, 0, 1080); mok(d, 220); mok(d, 900); zet(img, "pannenkoek", 100, 470, TAFEL_Y + 4, op="tafel", naam="pannenkoeken"); krant(img, tb)
    ps.W, ps.H = W, H
    for naam, (hx_, top_) in koppen.items():
        tekst, kl = NAAM[naam]
        if tekst: ps.label(img, tekst, hx_, top_ - 45, kl, 0.55)
    zm = 1.12 + 0.05 * (tb - T0); bw, bh = W / zm, H / zm; x0 = (W - bw) / 2; y0 = min(H - bh, max(0, 1250 - bh / 2)); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    img = img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)
    img = ImageOps.colorize(img.convert("L"), (45, 30, 15), (255, 238, 200))                      # oude foto
    d = ImageDraw.Draw(img); d.rectangle((0, 0, W - 1, H - 1), outline=(250, 245, 230), width=26)
    LABELS.clear()
    if TEKST_AAN:
        kop(img, "1999", None, 150, 70, KL["geel"], 1.0)
        kop(img, "$100 IN 1999", W / 2, 300, 105, KL["geel"], ps.pop((tb - kw(I_HOOK, "1999", -0.1)) / 0.3) if tb >= kw(I_HOOK, "1999", -0.1) else 0)
        ondertitel(img, t)
    if tb - T0 < 0.15: img = Image.blend(img, Image.new("RGB", (W, H), (255, 255, 255)), 1 - (tb - T0) / 0.15)   # flits
    WACHT.einde(gezichten={k_: (v[0], v[1], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1]) for k_, v in GEZ.items()}, gebaren=dict(GEB), crop=CROP[0])
    return img
def frame(t):
    t_beeld = min(t, Z[-1][1] + 0.6)                                                  # daarna bevroren eindbeeld
    if kw(I_HOOK, "back", -0.1) <= t_beeld < Z[I_RIJK][0] - 0.15: return flashback(t)
    sc = scene(t_beeld); n = sc["naam"]; nu = nu_i(t_beeld)
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t_beeld); GEZ.clear(); GEB.clear(); SCHERM.clear(); d = ImageDraw.Draw(img)
    if n == "woon2": deur(d, t_beeld)
    figs = figuren(n, t_beeld); zit = [f for f in figs if f[5]]; staan = [f for f in figs if not f[5]]
    if n == "diner": bank_achter(d, 0, 1080)
    if n == "gaming": kaartpodium(img, t_beeld)
    if n == "kamer": oudscherm(img, t_beeld); kalender(ImageDraw.Draw(img), t_beeld)
    koppen = teken(img, zit, t_beeld, nu); d = ImageDraw.Draw(img)
    if n in ("woon", "woon2"): salontafel(d); laptop(img, 545, t_beeld, n, SALON_Y); kom(img, 125, SALON_Y); ps2(img, t_beeld, n)
    if n == "diner":
        tafel(d, 0, 1080); mok(d, 220); mok(d, 900); zet(img, "pannenkoek", 100, 470, TAFEL_Y + 4, op="tafel", naam="pannenkoeken"); krant(img, t_beeld); biljet(ImageDraw.Draw(img), t_beeld)
    if staan: koppen.update(teken(img, staan, t_beeld, nu))
    if n == "gaming": gloed(img, t_beeld)
    if n == "ai": in_hand(img, "collega", figs, t_beeld, "gpu"); in_hand(img, "onderzoeker", figs, t_beeld, "gpu")
    if n == "kamer" and nu != I_ALIVE: in_hand(img, "jij99", figs, t_beeld, "handheld")
    ps.W, ps.H = W, H
    for naam, (hx_, top_) in koppen.items():
        tekst, kl = NAAM[naam]
        if tekst: ps.label(img, tekst, hx_, top_ - 45, kl, 0.55)
    img = camera(img, t)
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    for naam, (hx_, top_) in koppen.items():               # naamlabels in beeldcoördinaten (na de camera)
        tekst, kl = NAAM[naam]
        if tekst: bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, ((hx_ - bw_ / 2 - cx0) * zm_, (top_ - 70 - cy0) * zm_, (hx_ + bw_ / 2 - cx0) * zm_, (top_ - 20 - cy0) * zm_)))
    if TEKST_AAN:
        if n == "woon":                                     # 26 nov (eigenaar): tijdens "What if ... in 1999?" geen '2026' in beeld; label pas bij "Wait..."
            T_W = Z[I_RIJK][0] - 0.1
            if t_beeld >= T_W: plaatskaart(img, t_beeld, dict(sc, t=T_W))
            else:
                T_H, T_J = kw(I_HOOK, "hundred", -0.1), kw(I_HOOK, "1999", -0.1)
                if t_beeld >= T_H: kop(img, "$100", W / 2, 235, 120, (90, 220, 110), ps.pop((t_beeld - T_H) / 0.3))
        else: plaatskaart(img, t_beeld, sc)
        if n == "woon2" and T_620 <= t_beeld < Z[I_CONGR][1] + 0.2: kop(img, "$620,000", W / 2, 235, 120, (90, 220, 110), ps.pop((t_beeld - T_620) / 0.35))
        if n == "woon2" and t_beeld >= T_2002 and nu in (I_SOLD, I_WHY, I_PS2): kop(img, "SOLD IN 2002", W / 2, 235, 100, (255, 90, 80), ps.pop((t_beeld - T_2002) / 0.3))
        if n == "ai" and nu == I_AI and t_beeld >= Z[I_AI][0] + 0.8: kop(img, "AI", W / 2, 235, 130, (118, 185, 0), ps.pop((t_beeld - Z[I_AI][0] - 0.8) / 0.3))
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1]) for k_, v in GEZ.items()}, gebaren=dict(GEB), crop=CROP[0])
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
    zet_(T_BILJET + 0.1, "papier", _fade(_drukste(_laad("papier"), 0.4)), 0.4, "biljet")                         # biljet over tafel
    for q in np.arange(T_DEUR + 0.2, T_DEUR + 1.3, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.35, "jensennu")
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
    if "--tekst" in sys.argv:                               # snelle tekstcontrole zonder video (6 beelden per seconde)
        for i in range(int(EIND * 6)): frame(i / 6)
        print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); print("LAYOUT:", sorted(LAYOUT) or "alles past"); sys.exit()
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 11, 480 * 2)); [pl.paste(im, (270 * (i % 11), 480 * (i // 11))) for i, im in enumerate(ims)]
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
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-nvidia.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    print("KLAAR short-nvidia.mp4", round(EIND, 1), "s")
