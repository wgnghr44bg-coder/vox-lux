"""Short 'What If Black Friday Never Ended?' (26 nov 2026), losse Short, staand 1080x1920.
Zelfde recept en controles als de goedgekeurde $1 Million-Short (short-miljoen/maak_short.py, WHATIF-AFSPRAKEN.md):
alles wat gezegd wordt in beeld, niets zweeft (scènewachter), gezicht past bij de zin, geen armgebaar bij gewoon praten,
geen tekens/naamlabels bij personages, echte CC0-geluiden (alleen wat je ziet), stilte met één krekel, stem 180 wpm.
Gebruik: <omnivoice-venv>/python maak_short.py [--plaat]  -> short-blackfriday.mp4"""
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
LIJF = {"YOU": "you", "DAD": "dad", "MOM": "mom", "SIS": "sis"}
def luid(t, lijf):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == lijf for i in range(len(Z))): return 0.0
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
def zet(img, n, hoogte, x, voet, op=None, voor=False, naam=None, punt=None):
    s = sprite(n, hoogte)
    dx, dy = WACHT.plaats(naam or n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, voor=voor, punt=punt)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]

# ---------- tijden ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
# v2 (eigenaar 26 nov: "script niet zo heel goed", weer een telefoon aan het begin): gekke eindtoestand eerst (47 tv's), dan terug
# v3 (eigenaar 26 nov: begin met "imagine Black Friday forever", meer scenario's, krekel hoeft niet elke keer)
# v4 (eigenaar 26 nov: "script niet zo leuk", stilte/naar elkaar kijken alleen als het past): elke scène een eigen grap,
# einde = papa valt flauw bij een normale prijs. Geen stilte, geen krekel.
# v5 (eigenaar 26 nov: "net zo leuk als de eerste 2 shorts", geen mama-tegen-oma): meer reacties, echt feitje (politie Philadelphia),
# week 3 papa in een tent, week 4 de hond met 47 manden, einde = wending (Cyber Monday. Forever.) i.p.v. flauwvallen.
I_SALE, I_DADL, I_DOZ, I_SISL = zi("Imagine"), zi("A TV for"), zi("Week two"), zi("I live")
I_TENT, I_HOND, I_FEIT = zi("Week three"), zi("Week four"), zi("Fun fact")
I_KERST, I_D7, I_LAATST, I_LAST, I_KASSA = zi("Christmas"), zi("Month six"), zi("Then Dad"), zi("Thirty dollars"), zi("The cashier")
T_FOREVER = kw(I_SALE, "forever", -0.1); T_90 = kw(I_SALE, "ninety", -0.1); T_NOOIT = kw(I_SALE, "never", -0.1)
T_9 = kw(I_DADL, "nine", -0.1); T_TIEN = kw(I_DADL, "ten", -0.1)
T_SISUP = Z[I_SISL][0] - 0.4
T_TENT = kw(I_TENT, "tent", -0.1); T_BED = kw(I_HOND, "forty", -0.1); T_POLITIE = kw(I_FEIT, "police", -0.1)
T_OPEN = kw(I_KERST, "open", -0.1); T_TVK = kw(I_KERST, "tv", -0.1); T_ELF = kw(I_KERST, "eleven", -0.1)
T_LEEG = kw(I_D7, "stores", -0.1); T_DICHT = kw(I_D7, "close", -0.1)
T_DADIN = Z[I_LAATST][0]; T_PRIJS = kw(I_LAATST, "full", -0.1); T_30 = kw(I_LAATST, "thirty", -0.1)
T_CYBER = kw(I_KASSA, "cyber", -0.1); T_FOREVER2 = kw(I_KASSA, "forever", -0.1)
TENT_VOET = 1395                                            # voet van de tent op de stoep (buiten-nacht.png)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="begin", bg="woonkamer"), dict(t=Zs(I_DADL), naam="winkel", bg="winkel"), dict(t=Zs(I_DOZ), naam="dozen", bg="woonkamer"),
      dict(t=Zs(I_TENT), naam="tent", bg="buiten-nacht"), dict(t=Zs(I_HOND), naam="hond", bg="woonkamer"), dict(t=Zs(I_FEIT), naam="feit", bg="straat-oud"),
      dict(t=Zs(I_KERST), naam="kerst", bg="woonkamer"), dict(t=Zs(I_D7), naam="leeg", bg="leeg"), dict(t=Zs(I_LAATST), naam="laatst", bg="leeg")]
KOP = {"winkel": "WEEK 1", "dozen": "WEEK 2", "tent": "WEEK 3", "hond": "WEEK 4", "feit": "FUN FACT", "kerst": "CHRISTMAS", "leeg": "MONTH 6"}

# ---------- gezicht en gebaar passen bij de zin ----------
SCHRIK = ("can't see", "It's a TV", "Full price", "Thirty dollars", "Cyber Monday")
BLIJ = ("Imagine", "A TV for", "I live here", "The deals", "You open", "Then Dad finds", "The cashier")
VERDRIET = ("He still", "They hated", "already have", "Wow", "The stores sold")
ACTIE = {"A TV for": "juich", "The deals": "juich", "Thirty dollars": "schrik"}
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
def telefoon(img, t):                                    # grote telefoon met winkel-app (beeld-grafiek boven het hoofd)
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 300, 80, 780, 720
    tril = math.sin(t * 60) * 6 if t < Z[0][0] + 0.8 else 0; x0 += tril; x1 += tril
    WACHT.plaats("winkel-app", (x0, y0, x1, y1), op="beeld")
    d.rounded_rectangle((x0, y0, x1, y1), 48, fill=(25, 25, 32), outline=(10, 10, 14), width=6)
    d.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), 34, fill=(245, 247, 250))
    d.rounded_rectangle(((x0 + x1) / 2 - 50, y0 + 30, (x0 + x1) / 2 + 50, y0 + 52), 11, fill=(25, 25, 32))
    d.rectangle((x0 + 18, y0 + 90, x1 - 18, y0 + 190), fill=(20, 20, 24))
    tk = "BLACK FRIDAY"; f = font(FB, 46)
    if d.textlength(tk, font=f) > x1 - x0 - 70: LAYOUT.add("BLACK FRIDAY past niet op het telefoonscherm")
    d.text(((x0 + x1) / 2, y0 + 140), tk, font=f, fill=(255, 255, 255), anchor="mm")
    sch = ps.pop((t - T_90) / 0.35) if t >= T_90 else 0
    if sch > 0:
        f = font(FB, int(150 * sch)); d.text(((x0 + x1) / 2, y0 + 320), "-90%", font=f, fill=(220, 40, 40), anchor="mm", stroke_width=4, stroke_fill=(120, 20, 20))
        if d.textlength("-90%", font=font(FB, 150)) > x1 - x0 - 60: LAYOUT.add("-90% past niet op het telefoonscherm")
        d.text(((x0 + x1) / 2, y0 + 430), "EVERYTHING", font=font(FB, 40), fill=(60, 60, 70), anchor="mm")
    if t >= T_NOOIT:                                     # "The sale never ends": onderaan "Sale ends: NEVER"
        yy = y0 + 520; d.line((x0 + 50, yy - 20, x1 - 50, yy - 20), fill=(220, 220, 228), width=3)
        d.text((x0 + 50, yy), "Sale ends", font=font(FS, 36), fill=(60, 60, 70))
        v = "NEVER"; f2 = font(FB, int(40 * ps.pop((t - T_NOOIT) / 0.3)))
        d.text((x1 - 60 - d.textlength(v, font=f2), yy - 2), v, font=f2, fill=(220, 40, 40))
        if y0 + 580 > y1 - 18: LAYOUT.add("Sale ends-regel past niet")
    if t < Z[0][0] + 0.8 and int(t * 4) % 2 == 0: d.text((x0 + 60, y1 - 110), "BZZZ", font=font(FB, 56), fill=(220, 60, 60))
def hand(n, x, y, s, hoek):                              # rechterhand bij een armhoek (zelfde maten als poppetje); hoek<0 = linkerhand
    S = s * ps.C[n].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S; kant = 1 if hoek >= 0 else -1
    return x + kant * 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S, S
def telefoontje(img, hx, hy, S, t):
    d = ImageDraw.Draw(img); d.rounded_rectangle((hx - 13 * S, hy - 36 * S, hx + 13 * S, hy + 6 * S), int(5 * S), fill=(30, 30, 36), outline=(10, 10, 12), width=2)
    d.rounded_rectangle((hx - 10 * S, hy - 32 * S, hx + 10 * S, hy + 2 * S), int(3 * S), fill=(40, 40, 46))
    d.text((hx, hy - 15 * S), "%", font=font(FB, int(14 * S)), fill=(230, 60, 60), anchor="mm")
def tvdoos(d, x, y, w, h):                               # kartonnen doos met een plaatje van een tv erop (geen letters)
    d.rectangle((x, y, x + w, y + h), fill=(200, 160, 105), outline=INK, width=4)
    d.line((x + w / 2, y, x + w / 2, y + 14), fill=(160, 120, 75), width=6)
    d.rectangle((x + w * 0.22, y + h * 0.25, x + w * 0.78, y + h * 0.68), fill=(30, 30, 38), outline=INK, width=3)
    d.rectangle((x + w * 0.45, y + h * 0.68, x + w * 0.55, y + h * 0.78), fill=(30, 30, 38))
DOZEN = [(c, r) for c, n in enumerate((4, 3, 3)) for r in range(n)]          # 10 dozen: kolommen van 4, 3 en 3
DOOS_X, DOOS_VOET, DW, DH = 70, 1600, 135, 95
def dozen(img, t):
    if t < T_TIEN: return
    d = ImageDraw.Draw(img); n = min(10, 1 + int((t - T_TIEN) / 0.05))
    WACHT.plaats("stapel tv-dozen", (DOOS_X, DOOS_VOET - 4 * DH, DOOS_X + 3 * DW, DOOS_VOET), op="vloer")
    for c, r in DOZEN[:n]: tvdoos(d, DOOS_X + c * DW, DOOS_VOET - (r + 1) * DH, DW - 6, DH - 4)
STAPELS = [(860, 6), (1005, 5)]                         # kerst: 11 tv's (de 10 van papa + 1) rechts in de kamer
TV_RIJ = [(x, laag) for x, n in STAPELS for laag in range(n)]
TV_VOET, TV_H = 1250, 86
def doos(d, x, voet, w, h):                              # gewone kartonnen doos (plakband, geen letters), x = midden
    x0, y0 = x - w / 2, voet - h
    d.rectangle((x0, y0, x0 + w, voet), fill=(200, 160, 105), outline=INK, width=4)
    d.rectangle((x - w * 0.09, y0, x + w * 0.09, y0 + h * 0.35), fill=(225, 200, 150), outline=(160, 120, 75), width=2)
    d.line((x0 + 6, y0 + h * 0.18, x0 + w - 6, y0 + h * 0.18), fill=(170, 130, 85), width=3)
DOZEN_ACHTER = [(x, 1270, 190, 150) for x in (100, 290, 480, 670, 860, 1030)] + [(x, 1430, 210, 170) for x in (60, 260, 470, 980)]
DOZEN_VOOR = [(x, 1760, 230, 200) for x in (560, 790, 1010)] + [(x, 1960, 250, 230) for x in (80, 330, 580, 830, 1060)]
SISDOOS = (300, 1700, 300, 330)                          # de doos waar zus in woont (voor alles, x, voet, b, h)
def dozenzee(img, voor):
    d = ImageDraw.Draw(img)
    for x, v, w, h in (DOZEN_VOOR + [SISDOOS] if voor else DOZEN_ACHTER):
        WACHT.plaats("doos", (x - w / 2, v - h, x + w / 2, min(v, H - 4)), op="vloer")        # onderste rij loopt onder de rand door
        doos(d, x, v, w, h)
def kerstboom(img):                                      # eenvoudige kerstboom met ster en ballen (zelf getekend)
    d = ImageDraw.Draw(img); x, v = 150, 1300
    WACHT.plaats("kerstboom", (x - 130, v - 470, x + 130, v), op="vloer")
    d.rectangle((x - 22, v - 60, x + 22, v), fill=(120, 80, 45), outline=INK, width=4)
    for bw, bot, top in ((130, 50, 260), (105, 160, 360), (80, 270, 470)):        # drie lagen: breedte, onderkant, top
        d.polygon([(x - bw, v - bot), (x + bw, v - bot), (x, v - top)], fill=(45, 140, 70), outline=INK)
    d.polygon([(x, v - 500), (x + 18, v - 470), (x - 18, v - 470)], fill=(255, 215, 60), outline=INK); d.ellipse((x - 20, v - 492, x + 20, v - 452), fill=(255, 215, 60), outline=INK, width=3)
    for bx, by, kl in ((-60, 110, (220, 50, 50)), (50, 130, (60, 120, 220)), (-30, 210, (255, 200, 40)), (35, 250, (220, 50, 50)), (0, 330, (60, 120, 220))):
        d.ellipse((x + bx - 13, v - by - 13, x + bx + 13, v - by + 13), fill=kl, outline=INK, width=2)
KADO = (540, 1720, 230, 190)
def cadeau(img, t):                                      # ingepakt cadeau; bij "It's a TV" zit er een tv in (papier eraf)
    d = ImageDraw.Draw(img); x, v, w, h = KADO
    if t < T_TVK:
        WACHT.plaats("cadeau", (x - w / 2, v - h, x + w / 2, v), op="vloer")
        d.rectangle((x - w / 2, v - h, x + w / 2, v), fill=(215, 45, 55), outline=INK, width=4)
        d.rectangle((x - 18, v - h, x + 18, v), fill=(255, 210, 60)); d.rectangle((x - w / 2, v - h / 2 - 16, x + w / 2, v - h / 2 + 16), fill=(255, 210, 60))
        d.ellipse((x - 70, v - h - 45, x - 4, v - h + 8), fill=(255, 210, 60), outline=INK, width=3); d.ellipse((x + 4, v - h - 45, x + 70, v - h + 8), fill=(255, 210, 60), outline=INK, width=3)
    else:
        zet(img, "tv", 170, x, v, op="vloer", naam="tv")
        for k, (dx, dy, a) in enumerate(((-170, -10, 20), (150, -25, -30), (-120, 30, -10), (175, 25, 15))):   # stukken papier op de vloer
            px, py = x + dx, v + dy; d.polygon([(px - 30, py), (px + 25, py - 18), (px + 32, py + 12), (px - 20, py + 22)], fill=(215, 45, 55), outline=INK)
PLANK_Y = 1058                                           # plank in de lege winkel (gemeten op leeg.png, 1080x1920)
def laatste_rooster(img, t):                             # één broodrooster op de plank, prijskaartje $30 bij "Full price"
    WACHT.vlak("plank", [190, 880, PLANK_Y - 10, PLANK_Y + 16])
    zet(img, "broodrooster", 120, 540, PLANK_Y, op="plank", naam="broodrooster")
    if t >= T_PRIJS:
        d = ImageDraw.Draw(img); sch = ps.pop((t - T_PRIJS) / 0.3); bx = 660                 # prijsbordje staat op de plank naast de rooster
        WACHT.plaats("prijskaartje", (bx - 58, PLANK_Y - 74, bx + 58, PLANK_Y), op="plank")
        d.rectangle((bx - 4, PLANK_Y - 14, bx + 4, PLANK_Y), fill=INK)
        d.rounded_rectangle((bx - 58 * sch, PLANK_Y - 14 - 60 * sch, bx + 58 * sch, PLANK_Y - 14), 10, fill=(255, 255, 255), outline=INK, width=4)
        if sch > 0.3: d.text((bx, PLANK_Y - 14 - 30 * sch), "$30", font=font(FB, int(44 * sch)), fill=(220, 40, 40), anchor="mm")
def tvs(img, t):
    onder = {}                                           # elke tv staat op de vloer of bovenop de tv eronder (eigen vlak per tv)
    for k, (x, laag) in enumerate(TV_RIJ):
        voet = TV_VOET - laag * (TV_H - 8)
        if laag == 0: op = "vloer"
        else: op = min((v for v in onder if onder[v][1] == laag - 1), key=lambda v: abs(onder[v][0] - x))
        zet(img, "tv", TV_H, x, voet, op=op, naam="tv")
        hw = sprite("tv", TV_H).width / 2
        WACHT.vlak(f"tv{k}", [x - hw, x + hw, voet - TV_H - 6, voet - TV_H + 16]); onder[f"tv{k}"] = (x, laag)
STOELEN = [(770, 1450), (110, 1450), (280, 1450), (970, 1450), (120, 1800), (330, 1800), (540, 1800), (750, 1800), (960, 1800), (630, 1450)]
def stoelen(img, t):                                     # 1 gamestoel bij "gaming chair", 9 erbij bij "nine more"
    if t < T_STOEL: return
    n = 1 if t < T_NEGEN else min(10, 2 + int((t - T_NEGEN) / 0.12))
    for x, v in sorted(STOELEN[:n], key=lambda q: q[1]): zet(img, "gamestoel", 320, x, v, op="vloer", naam="gamestoel")
def tent(img):                                           # tentje van papa op de stoep voor de winkel
    zet(img, "tent", 360, 330, TENT_VOET, op="stoep", naam="tent")
MANDEN = []                                              # 47 hondenmanden: rijen op de vloer, achter klein, voor groot (gat in het midden voor de hond)
for y_, h_, xs in ((1060, 70, range(240, 800, 92)), (1175, 85, range(240, 800, 92)), (1300, 100, range(60, 1040, 108)),   # achter: tussen bank en tv-kast
                   (1440, 115, range(70, 1040, 120)), (1600, 130, [80, 240, 860, 1010]), (1780, 145, [90, 260, 830, 1000]),
                   (1915, 150, [80, 260, 440, 620, 800, 980])):
    MANDEN += [(x_, y_, h_) for x_ in xs]
assert len(MANDEN) == 47, len(MANDEN)                    # "forty-seven beds": er staan er echt 47
def manden(img):
    for x_, y_, h_ in MANDEN: zet(img, "hondenmand", h_, x_, y_, op="vloer", naam="hondenmand")
def hond(img):                                           # de hond slaapt gewoon op de vloer, vooraan in het midden, naast al die manden
    zet(img, "hond", 360, 470, 1790, op="vloer", naam="hond")
def brood(img, hx, hy, S):                               # sneetje koud brood in de hand (korst + kruim, geen letters)
    d = ImageDraw.Draw(img); w = 15 * S; x0, y0 = hx - w, hy - 1.7 * w
    WACHT.plaats("brood in de hand", (x0, y0 - 0.5 * w, x0 + 2 * w, y0 + 2 * w), op="aan:hand")
    for kl, k in (((165, 105, 50), 0), ((242, 222, 170), 0.18 * w)):
        d.ellipse((x0 + k, y0 - 0.5 * w + k, x0 + w + 2, y0 + 0.6 * w), fill=kl); d.ellipse((x0 + w - 2, y0 - 0.5 * w + k, x0 + 2 * w - k, y0 + 0.6 * w), fill=kl)
        d.rectangle((x0 + k, y0 + k, x0 + 2 * w - k, y0 + 2 * w - k), fill=kl)
    for q in range(5):
        cx_, cy_ = x0 + w * (0.5 + 0.25 * q), y0 + w * (0.6 + 0.25 * (q % 3)); d.ellipse((cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2), fill=(215, 190, 135))

# ---------- frame ----------
FAM = [dict(n="mom", x=530, y=1560, s=1.6), dict(n="you", x=710, y=1560, s=1.6), dict(n="sis", x=880, y=1560, s=1.6), dict(n="dad", x=175, y=1560, s=1.6)]
POPS = {"begin": FAM, "dozen": [dict(n="you", x=760, y=1600, s=1.6), dict(n="sis", x=300, y=1780, s=1.6)],
        "winkel": [dict(n="dad", x=760, y=1570, s=1.55)],
        "tent": [dict(n="dad", x=740, y=TENT_VOET + 10, s=1.55)],
        "hond": [dict(n="you", x=690, y=1580, s=1.6)],
        "feit": [dict(n="agent", x=640, y=1850, s=1.7)],
        "kerst": [dict(n="mom", x=330, y=1560, s=1.6), dict(n="you", x=600, y=1560, s=1.6)],
        "leeg": [dict(n="mom", x=870, y=1570, s=1.55), dict(n="dad", x=200, y=1570, s=1.55)],
        "laatst": [dict(n="kassa", x=170, y=1600, s=1.5), dict(n="dad", x=800, y=1570, s=1.55, loop=(T_DADIN - 0.1, T_DADIN + 0.9, 1250, 800))]}
ZOOM_AAN = True; TEKST_AAN = True
GEZ = {}
def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; n = sc["naam"]
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t)
    nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    spreker = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    if n == "winkel": dozen(img, t)
    if n == "dozen": dozenzee(img, False)
    if n == "kerst": kerstboom(img); tvs(img, t)
    if n == "laatst": laatste_rooster(img, t)
    if n == "tent": tent(img)
    if n == "hond": manden(img); hond(img)
    flauw = False
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}; vast = []; handen = {}; GEZ.clear()
    pops = POPS[n]; sp = next((p for p in pops if p["n"] == spreker), None)
    for p in pops:
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]
            if t < a: continue
            f = ps.ease((t - a) / max(0.1, b - a)); x = x0 + (x1 - x0) * f
            if a <= t < b: loop = (t - a) * 2.2
        if sp is not None and p is not sp: kijk = 0.9 if sp["x"] > x else -0.9
        else: kijk = 0.5 if x < 540 else -0.5
        if n == "winkel" and t >= T_TIEN: kijk = -0.9                                        # papa kijkt trots naar zijn dozen
        if n == "hond": kijk = -0.9                                                          # jij kijkt naar de hond
        if n == "leeg": kijk = -0.9 if p["n"] == "mom" else 0.9                              # kijken naar de lege kast
        if n == "laatst": kijk = 0.9 if p["n"] == "kassa" else -0.9                         # papa kijkt naar rooster en kassa, kassa naar papa
        if n == "kerst": kijk = 0.6 if p["n"] == "mom" else -0.2                             # kijken naar het cadeau
        if n == "dozen" and p["n"] == "sis":                                                # zus komt uit haar doos omhoog
            if t < T_SISUP: continue
            y_op = p["y"] - 250 * ps.ease(min(1, (t - T_SISUP) / 0.3)); kijk = 0.6
        if n == "dozen" and p["n"] == "you": kijk = -0.9 if t >= T_SISUP else 0.0
        geb = None
        if n == "feit" and t >= T_POLITIE: geb = "stamp"                                    # agent baalt van de drukte
        if sp is p and nu is not None:
            geb = next((g for s_, g in ACTIE.items() if tekst_nu.startswith(s_)), geb)
        if geb == "praat": LAYOUT.add(f"armgebaar 'praat' bij gewoon praten ({p['n']}, {t:.1f} s): weghalen")
        if loop is not None: geb = "rennen"
        emo = emotie(t, nu)
        if n == "laatst" and nu == I_KASSA: emo = "schrik" if p["n"] == "dad" else "blij"       # kassa glimlacht, papa schrikt
        verb, boos_ = emo == "schrik", emo == "verdriet"
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13
        y = p.get("y", 1460)
        if n == "dozen" and p["n"] == "sis": y = y_op
        dl = d
        if flauw and p["n"] == "dad":                                                       # papa valt flauw: eigen laag, draait om zijn voeten
            l2 = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(l2); verb, boos_, geb = True, False, None
        koppen[p["n"]] = ps.poppetje(dl, p["n"], x, y, p["s"], t, loop=loop, kijk=kijk, mond=0.0 if dl is not d else luid(t, p["n"]), knipper=knip,
                                     verbaasd=verb, gebaar=geb, boos=boos_)
        GEZ[p["n"]] = (*koppen[p["n"]], p["s"] * ps.C[p["n"]].get("groot", 1))
        if dl is not d:
            a = 88 * ps.ease(min(1, (t - T_VAL) / 0.35)); ra = math.radians(a)
            l2 = l2.resize((W, H), Image.LANCZOS).rotate(a, center=(x, y), resample=Image.BICUBIC); vast.append(l2)
            hx_, hy_ = koppen[p["n"]][0] - x, koppen[p["n"]][1] - y
            GEZ[p["n"]] = (x + hx_ * math.cos(ra) + hy_ * math.sin(ra), y - hx_ * math.sin(ra) + hy_ * math.cos(ra), GEZ[p["n"]][2])
        if geb == "wijs": handen[p["n"]] = hand(p["n"], x, y, p["s"], 100)
        if geb == "wijslinks": handen[p["n"]] = hand(p["n"], x, y, p["s"], -100)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for l2 in vast: img.paste(l2, (0, 0), l2)
    if n == "dozen": dozenzee(img, True)
    if n == "kerst": cadeau(img, t)
    if TEKST_AAN:
        if n in KOP: kop(img, KOP[n], None, 150, 84, KL["geel"], ps.pop((t - sc["t"]) / 0.3))
        if n == "leeg" and t >= T_DICHT: kop(img, "STORES: CLOSED", W / 2, 300, 80, (255, 90, 80), ps.pop((t - T_DICHT) / 0.3))
        if n == "kerst" and t >= T_ELF: kop(img, "TV #12", W / 2, 330, 120, (255, 255, 255), ps.pop((t - T_ELF) / 0.3))
        if n == "laatst" and T_30 <= t < T_CYBER: kop(img, "$30", W / 2, 330, 200, (235, 45, 45), ps.pop((t - T_30) / 0.35))
        if n == "laatst" and t >= T_CYBER:
            kop(img, "CYBER MONDAY", W / 2, 300, 110, (80, 200, 255), ps.pop((t - T_CYBER) / 0.3))
            if t >= T_FOREVER2: kop(img, "FOREVER", W / 2, 440, 120, KL["geel"], ps.pop((t - T_FOREVER2) / 0.3))
        if n == "hond" and t >= T_BED: kop(img, "47 BEDS", W / 2, 330, 120, (255, 255, 255), ps.pop((t - T_BED) / 0.3))
        if n == "feit" and t >= T_POLITIE: kop(img, "PHILADELPHIA, 1960s", W / 2, 300, 70, (255, 255, 255), ps.pop((t - T_POLITIE) / 0.3))
        if n == "begin" and t < T_90:
            kop(img, "BLACK FRIDAY", W / 2, 260, 110, (255, 255, 255), ps.pop(t / 0.3))
            if t >= T_FOREVER: kop(img, "FOREVER", W / 2, 400, 120, KL["geel"], ps.pop((t - T_FOREVER) / 0.3))
        if n == "begin" and t >= T_90: kop(img, "-90%", W / 2, 330, 230, (235, 45, 45), ps.pop((t - T_90) / 0.35))
        if n == "begin" and t >= T_NOOIT: kop(img, "SALE ENDS: NEVER", W / 2, 560, 76, KL["geel"], ps.pop((t - T_NOOIT) / 0.3))
        if n == "winkel" and T_9 <= t < T_TIEN + 0.6: kop(img, "TV: $9", W / 2, 330, 120, (255, 255, 255), ps.pop((t - T_9) / 0.3))
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
    piep = _fade(_drukste(_laad("scanner"), 0.15))
    for q in range(10): zet_(T_TIEN + q * 0.05, "scanner", piep, 0.3, "stapel tv-dozen")             # tien piepjes: tien tv's
    zet_(T_SISUP, "papier-ritsel", _fade(_drukste(_laad("papier-ritsel"), 0.5)), 0.35, "sis")            # zus komt uit haar doos
    zet_(T_TVK - 0.25, "papier", _fade(_drukste(_laad("papier"), 0.4)), 0.4, "cadeau")                  # cadeaupapier eraf
    zet_(T_LEEG, "papier-ritsel", _fade(_drukste(_laad("papier-ritsel"), 0.8)), 0.3, "mom")
    for q in np.arange(T_DADIN - 0.1, T_DADIN + 0.9, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.35, "dad")
    zet_(T_CYBER, "kassa", _fade(_laad("kassa")), 0.45, "kassa")                                         # kassa: de volgende uitverkoop begint
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
                          "-t", f"{EIND:.2f}", str(HIER / "short-blackfriday.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); print("KLAAR short-blackfriday.mp4", round(EIND, 1), "s")
