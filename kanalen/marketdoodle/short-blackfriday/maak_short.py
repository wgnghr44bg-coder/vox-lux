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
ps.C["oma"] = dict(broek=(110, 90, 120), shirt=(205, 120, 165), haar=(205, 205, 210), kapsel="grijs", bril=True, groot=0.95)
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
EIND = Z[-1][1] + 1.3
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
I_SALE, I_DADL, I_W1, I_W2 = zi("Imagine"), zi("A TV for"), zi("Week one"), zi("Week two")
I_D3, I_D7, I_SIS, I_MOM, I_SLOT, I_LAST = zi("Week three"), zi("Month two"), zi("Mom, can"), zi("Nobody makes"), zi("One year"), zi("Best deal")
T_FOREVER = kw(I_SALE, "forever", -0.1); T_90 = kw(I_SALE, "ninety", -0.1); T_NOOIT = kw(I_SALE, "never", -0.1)
T_STOEL = kw(I_W2, "gaming", -0.1); T_2 = kw(I_W2, "two", -0.1) if False else None
T_NEGEN = kw(I_W2, "nine", -0.1); T_VRIEND = kw(I_W2, "don't", -0.1)
T_9 = kw(I_DADL, "nine", -0.1); T_TIEN = kw(I_DADL, "ten", -0.1); T_KASSA = kw(I_W1, "everyone", -0.05)
T_OMA = kw(I_D3, "grandma", -0.2); T_ROOSTER = kw(I_D3, "toaster", -0.1); T_WINT = kw(I_D3, "wins", -0.05)
T_LEEG = kw(I_D7, "empty", -0.1); T_FABRIEK = kw(I_D7, "factories", -0.1)
T_BROOD = kw(I_SLOT, "cold", -0.15); T_47B = kw(I_SLOT, "forty", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="begin", bg="woonkamer"), dict(t=Zs(I_DADL), naam="winkel", bg="winkel"), dict(t=Zs(I_W2), naam="stoelen", bg="kamer"),
      dict(t=Zs(I_D3), naam="oma", bg="winkel"), dict(t=Zs(I_D7), naam="leeg", bg="leeg"), dict(t=Zs(I_SIS), naam="keuken", bg="keuken"),
      dict(t=Zs(I_SLOT), naam="tvs", bg="woonkamer")]
KOP = {"winkel": "WEEK 1", "stoelen": "WEEK 2", "oma": "WEEK 3", "leeg": "MONTH 2", "tvs": "1 YEAR LATER"}
# "two dollars": eerste 'two' in de zin na 'chair'
T_2 = next(t0 for i, w, t0, t1 in SW if i == I_W2 and _norm(w) == "two" and t0 > T_STOEL) - 0.1

# ---------- gezicht en gebaar passen bij de zin ----------
SCHRIK = ("fights a grandma", "Every shelf", "Then the factories", "Nobody makes")
BLIJ = ("Imagine", "A TV for", "Everyone buys", "Week two", "Best deal")
VERDRIET = ("have nine friends", "grandma wins", "Stores lose", "can we buy", "One year")
ACTIE = {"A TV for": "juich", "Best deal": "duim", "Nobody makes": "schouders"}
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
    d = ImageDraw.Draw(img); n = min(10, 1 + int((t - T_TIEN) / 0.12))
    WACHT.plaats("stapel tv-dozen", (DOOS_X, DOOS_VOET - 4 * DH, DOOS_X + 3 * DW, DOOS_VOET), op="vloer")
    for c, r in DOZEN[:n]: tvdoos(d, DOOS_X + c * DW, DOOS_VOET - (r + 1) * DH, DW - 6, DH - 4)
STAPELS = [(95, 8), (273, 8), (451, 8), (629, 7), (807, 8), (985, 8)]          # 47 tv's: 6 stapels met ruimte ertussen (x, hoogte)
TV_RIJ = [(x, laag) for x, n in STAPELS for laag in range(n)]
TV_VOET, TV_H = 1250, 100
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
def brood(img, hx, hy, S):                               # sneetje koud brood in de hand (korst + kruim, geen letters)
    d = ImageDraw.Draw(img); w = 15 * S; x0, y0 = hx - w, hy - 1.7 * w
    WACHT.plaats("brood in de hand", (x0, y0 - 0.5 * w, x0 + 2 * w, y0 + 2 * w), op="aan:hand")
    for kl, k in (((165, 105, 50), 0), ((242, 222, 170), 0.18 * w)):
        d.ellipse((x0 + k, y0 - 0.5 * w + k, x0 + w + 2, y0 + 0.6 * w), fill=kl); d.ellipse((x0 + w - 2, y0 - 0.5 * w + k, x0 + 2 * w - k, y0 + 0.6 * w), fill=kl)
        d.rectangle((x0 + k, y0 + k, x0 + 2 * w - k, y0 + 2 * w - k), fill=kl)
    for q in range(5):
        cx_, cy_ = x0 + w * (0.5 + 0.25 * q), y0 + w * (0.6 + 0.25 * (q % 3)); d.ellipse((cx_ - 2, cy_ - 2, cx_ + 2, cy_ + 2), fill=(215, 190, 135))
def rooster(img, t, oma_hand, mom_hand):                 # broodrooster tussen de handen; na "wins" bij oma
    if t < T_ROOSTER: return
    if t < T_WINT: f = 0.5 + 0.08 * math.sin(t * 22)    # trekken: heen en weer
    else: f = max(0.0, 0.5 - (t - T_WINT) / 0.25 * 0.5)
    hx = oma_hand[0] + (mom_hand[0] - oma_hand[0]) * f; hy = oma_hand[1] + (mom_hand[1] - oma_hand[1]) * f
    zet(img, "broodrooster", 120, hx, hy + 45, op="aan:hand", naam="broodrooster", punt=(hx, hy))

# ---------- frame ----------
FAM = [dict(n="mom", x=530, y=1560, s=1.6), dict(n="you", x=710, y=1560, s=1.6), dict(n="sis", x=880, y=1560, s=1.6), dict(n="dad", x=175, y=1560, s=1.6)]
POPS = {"begin": FAM, "stoelen": [dict(n="you", x=470, y=1430, s=1.6)],
        "winkel": [dict(n="dad", x=760, y=1570, s=1.55)],
        "oma": [dict(n="oma", x=330, y=1570, s=1.55, loop=(T_OMA - 0.2, T_OMA + 0.9, -150, 330)), dict(n="mom", x=760, y=1570, s=1.55)],
        "leeg": [dict(n="mom", x=870, y=1570, s=1.55), dict(n="dad", x=200, y=1570, s=1.55)],
        "keuken": [dict(n="sis", x=330, s=1.8), dict(n="mom", x=760, s=1.8)],
        "tvs": FAM}
ZOOM_AAN = True; TEKST_AAN = True
GEZ = {}
def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; n = sc["naam"]
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t)
    nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    spreker = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    if n == "winkel": dozen(img, t)
    if n == "tvs": tvs(img, t)
    if n == "stoelen": stoelen(img, t)
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
        if n == "oma": kijk = 0.9 if p["n"] == "oma" else -0.9                               # ze kijken elkaar aan
        if n == "leeg": kijk = -0.9 if p["n"] == "mom" else 0.9                              # kijken naar de lege kast
        if n == "tvs" and Z[I_SLOT][1] + 0.2 <= t < Z[I_LAST][0]:                           # stilte: langzaam opzij kijken naar elkaar
            u_ = (t - Z[I_SLOT][1] - 0.2) / max(0.5, Z[I_LAST][0] - Z[I_SLOT][1] - 0.2)
            kijk = (1 if hash(p["n"]) % 2 else -1) * 0.9 * math.sin(math.pi * min(1, u_))
        geb = "telefoon" if n == "tvs" and t >= T_BROOD and not (p["n"] == "dad" and t >= Z[I_LAST][0] - 0.1) else None   # sneetje brood vasthouden
        if n == "oma" and t >= T_ROOSTER and loop is None:
            geb = "wijs" if p["n"] == "oma" else "wijslinks"                               # allebei een arm naar de broodrooster
            if p["n"] == "mom" and t >= T_WINT + 0.25: geb = "schouders"
        if sp is p and nu is not None:
            geb = next((g for s_, g in ACTIE.items() if tekst_nu.startswith(s_)), geb)
        if geb == "praat": LAYOUT.add(f"armgebaar 'praat' bij gewoon praten ({p['n']}, {t:.1f} s): weghalen")
        if loop is not None: geb = "rennen"
        emo = emotie(t, nu)
        if n == "oma" and p["n"] == "oma" and t >= T_WINT: emo = "blij"
        verb, boos_ = emo == "schrik", emo == "verdriet"
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13
        y = p.get("y", 1460)
        koppen[p["n"]] = ps.poppetje(d, p["n"], x, y, p["s"], t, loop=loop, kijk=kijk, mond=luid(t, p["n"]), knipper=knip,
                                     verbaasd=verb, gebaar=geb, boos=boos_)
        GEZ[p["n"]] = (*koppen[p["n"]], p["s"] * ps.C[p["n"]].get("groot", 1))
        if geb == "telefoon": S_ = p["s"] * ps.C[p["n"]].get("groot", 1.0); vast.append((x + 6 * S_, y - 125 * S_, S_))   # hand voor de buik (gemeten)
        if geb == "wijs": handen[p["n"]] = hand(p["n"], x, y, p["s"], 100)
        if geb == "wijslinks": handen[p["n"]] = hand(p["n"], x, y, p["s"], -100)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for hx, hy, S in vast: brood(img, hx, hy, S)
    if n == "oma" and "oma" in handen:
        mh = handen.get("mom") or hand("mom", 760, 1570, 1.55, -100)
        rooster(img, t, handen["oma"], mh)
    if TEKST_AAN:
        if n in KOP: kop(img, KOP[n], None, 150, 84, KL["geel"], ps.pop((t - sc["t"]) / 0.3))
        if n == "leeg" and t >= T_FABRIEK: kop(img, "FACTORIES: CLOSED", W / 2, 300, 72, (255, 90, 80), ps.pop((t - T_FABRIEK) / 0.3))
        if n == "tvs" and t >= T_47B: kop(img, "47 TVs", None, 255, 80, (255, 255, 255), ps.pop((t - T_47B) / 0.3))
        if n == "begin" and t < T_90:
            kop(img, "BLACK FRIDAY", W / 2, 260, 110, (255, 255, 255), ps.pop(t / 0.3))
            if t >= T_FOREVER: kop(img, "FOREVER", W / 2, 400, 120, KL["geel"], ps.pop((t - T_FOREVER) / 0.3))
        if n == "begin" and t >= T_90: kop(img, "-90%", W / 2, 330, 230, (235, 45, 45), ps.pop((t - T_90) / 0.35))
        if n == "begin" and t >= T_NOOIT: kop(img, "SALE ENDS: NEVER", W / 2, 560, 76, KL["geel"], ps.pop((t - T_NOOIT) / 0.3))
        if n == "stoelen" and T_2 <= t < T_NEGEN: kop(img, "CHAIR: $2", W / 2, 330, 120, (255, 255, 255), ps.pop((t - T_2) / 0.3))
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
    for q in range(10): zet_(T_TIEN + q * 0.12, "scanner", piep, 0.3, "stapel tv-dozen")             # tien piepjes: tien tv's
    zet_(T_KASSA, "kassa", _fade(_laad("kassa")), 0.4, "stapel tv-dozen")                             # "Everyone buys everything"
    for q in np.arange(T_OMA - 0.2, T_OMA + 0.9, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.35, "oma")
    zet_(T_WINT, "ting", _fade(_laad("ting")), 0.5, "broodrooster")                                  # broodrooster-ping: oma wint
    zet_(T_LEEG, "papier-ritsel", _fade(_drukste(_laad("papier-ritsel"), 0.8)), 0.3, "mom")
    plof = _fade(_drukste(_laad("plof"), 0.25))
    zet_(T_STOEL + 0.05, "plof", plof, 0.35, "gamestoel")
    for q in range(9): zet_(T_NEGEN + q * 0.12, "plof", plof, 0.22, "gamestoel")                     # negen stoelen erbij
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
        pl = Image.new("RGB", (270 * 6, 480 * 2)); [pl.paste(im, (270 * (i % 6), 480 * (i // 6))) for i, im in enumerate(ims)]
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
