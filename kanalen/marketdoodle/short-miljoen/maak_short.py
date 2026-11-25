"""Short 'What If Everyone Got $1 Million?' (25 nov 2026) — voorproefje van de lange video (video-miljoen), staand 1080x1920.
Eigenaar: "de video is goed, graag opslaan voor nieuwe shorts" -> zelfde recept en controles als de lange video
(WHATIF-AFSPRAKEN.md, GOEDGEKEURD SJABLOON): alles wat gezegd wordt in beeld, niets zweeft (scènewachter), gezicht past bij de zin,
naamlabel boven wie praat, geen muziek, eigen geluiden. Het einde verklapt dag 30 niet: lange video eronder als Gerelateerde video.
Gebruik: <omnivoice-venv>/python maak_short.py [--plaat]  -> short-miljoen.mp4"""
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
EIND = Z[-1][1] + 1.3
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
if AUD.ndim > 1: AUD = AUD.mean(axis=1)
def kw(zin, woord, na=0.0):                              # tijd van een woord in zin 'zin' (script-woorden)
    for i, w, t0, t1 in SW:
        if i == zin and _norm(w).startswith(_norm(woord)): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0] + na
LIJF = {"YOU": "you", "DAD": "dad", "MOM": "mom", "SIS": "sis"}
NAAM = {"YOU": "YOU", "DAD": "DAD", "MOM": "MOM", "SIS": "SISTER"}
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
        im = im.resize((int(im.width * hoogte / im.height), hoogte), Image.LANCZOS)
        SPR[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if spiegel else im
    return SPR[k]
WACHT = Scenewachter(HIER.parent / "achtergronden.json")
def zet(img, n, hoogte, x, voet, op=None, voor=False):
    s = sprite(n, hoogte)
    dx, dy = WACHT.plaats(n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, voor=voor)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]

# ---------- tijden (woordtijden uit Whisper) ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_BANK, I_DAD, I_SIS, I_PAARD = zi("It's 6"), zi("Everybody got"), zi("I'm a millionaire"), zi("Day one")
I_MELK, I_MOM, I_PRIJS, I_DONKER, I_BROOD, I_SLOT = zi("Day seven"), zi("Fifty dollars?"), zi("Everyone is rich"), zi("Day fourteen"), zi("By day thirty"), zi("Wait.")
T_BANK = kw(I_BANK, "bank", -0.2); T_GISTER = kw(I_BANK, "Yesterday", -0.1)
T_SIS_IN, T_PAARD, T_EET, T_MAT = kw(I_PAARD, "sister", -0.1), kw(I_PAARD, "horse", -0.15), kw(I_PAARD, "eats", -0.1), kw(I_PAARD, "doormat", -0.1)
T_MOM_IN = kw(I_MELK, "Mom", -0.2); T_50 = kw(I_MELK, "fifty", -0.1)
T_100 = kw(I_PRIJS, "raised", -0.05); T_200 = kw(I_PRIJS, "two", -0.1)
T_UIT = kw(I_DONKER, "go", -0.05); T_KAARS = T_UIT + 0.9
T_BROOD = kw(I_BROOD, "bread", -0.15); T_MEER = kw(I_BROOD, "worth", -0.1); T_GELD = kw(I_BROOD, "million", -0.2)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="kamer", bg="kamer"), dict(t=Zs(I_DAD), naam="keuken", bg="keuken"), dict(t=Zs(I_PAARD), naam="tuin", bg="tuin"),
      dict(t=Zs(I_MELK), naam="winkel", bg="winkel"), dict(t=Zs(I_DONKER), naam="nacht", bg="keuken")]
KOP = {"tuin": "DAY 1", "winkel": "DAY 7", "nacht": "DAY 14"}

# ---------- gezicht en gebaar passen bij de zin ----------
SCHRIK = ("Mom! Dad!", "It's 6", "Check your phones", "Fifty dollars", "fifty dollars", "For milk", "raised the prices", "two hundred", "The lights go out",
          "worth more", "Wait", "eats the doormat")
BLIJ = ("one million dollars", "I'm a millionaire", "Everybody got it", "buys a horse")
VERDRIET = ("By day thirty", "The whole city", "on a yacht", "not even the worst part")
ACTIE = {"Mom! Dad!": "telefoon", "Everybody got it": "praat", "I'm a millionaire": "juich", "Fifty dollars?": "armen-open",
         "Wait.": "schrik"}
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
    if x is None: x = 50 + w / 2                          # links uitgelijnd
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = [w for w in SW if w[0] == i]
    f = font(FS, 58); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1].upper() + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1500                    # boven de titel/knoppen van YouTube Shorts
    if br > W - 40: LAYOUT.add(f"ondertitel te breed: {' '.join(w[1] for w in stuk)}")
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)
def telefoon(img, t):                                    # grote telefoon met bank-app (beeld-grafiek boven het hoofd)
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 300, 90, 780, 680
    tril = math.sin(t * 60) * 6 if t < Z[0][1] else 0; x0 += tril; x1 += tril
    sch = ps.pop(t / 0.3)
    WACHT.plaats("bank-app", (x0, y0, x1, y1), op="beeld")
    d.rounded_rectangle((x0, y0, x1, y1), 48, fill=(25, 25, 32), outline=(10, 10, 14), width=6)
    d.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), 34, fill=(245, 247, 250))
    d.rounded_rectangle(((x0 + x1) / 2 - 50, y0 + 30, (x0 + x1) / 2 + 50, y0 + 52), 11, fill=(25, 25, 32))
    d.rectangle((x0 + 18, y0 + 90, x1 - 18, y0 + 190), fill=(40, 110, 220))
    d.text((x0 + 50, y0 + 115), "MY BANK", font=font(FB, 44), fill=(255, 255, 255))
    d.text((x0 + 50, y0 + 240), "Balance", font=font(FS, 38), fill=(120, 120, 130))
    m = int(50 * (ps.pop((t - T_BANK) / 0.35) if t >= T_BANK else sch))
    d.text((x0 + 50, y0 + 300), "$1,000,000.00", font=font(FB, m), fill=(30, 170, 80))
    if d.textlength("$1,000,000.00", font=font(FB, 50)) > x1 - x0 - 90: LAYOUT.add("saldo past niet op het telefoonscherm")   # tekst binnen het kader
    if t >= T_GISTER:                                    # "Yesterday you had twelve"
        yy = y0 + 470; d.line((x0 + 50, yy - 20, x1 - 50, yy - 20), fill=(220, 220, 228), width=3)
        d.text((x0 + 50, yy), "Yesterday", font=font(FS, 34), fill=(60, 60, 70))
        v = "$12.00"; d.text((x1 - 60 - d.textlength(v, font=font(FB, 34)), yy), v, font=font(FB, 34), fill=(120, 120, 130))
    if t < Z[0][1] and int(t * 4) % 2 == 0: d.text((x0 + 60, y1 - 120), "BZZZ", font=font(FB, 56), fill=(220, 60, 60))
def hand(n, x, y, s, hoek=-32):                          # rechterhand bij gebaar 'telefoon' (zelfde maten als poppetje)
    S = s * ps.C[n].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S, S
def telefoontje(img, hx, hy, S, t):
    d = ImageDraw.Draw(img); d.rounded_rectangle((hx - 13 * S, hy - 36 * S, hx + 13 * S, hy + 6 * S), int(5 * S), fill=(30, 30, 36), outline=(10, 10, 12), width=2)
    d.rounded_rectangle((hx - 10 * S, hy - 32 * S, hx + 10 * S, hy + 2 * S), int(3 * S), fill=(150, 220, 255) if int(t * 3) % 2 else (120, 235, 160))
PAARD_X, PAARD_VOET, PAARD_H = 470, 930, 390       # paard achterin bij de achterdeur, kijkt naar links (naar de deurmat op de stoep)
def paard(img, t):
    if t < T_PAARD: return
    sch = ps.pop((t - T_PAARD) / 0.35); hh = int(PAARD_H * sch)
    pd = sprite("paard", hh, spiegel=True); hap = T_EET <= t < T_MAT + 1.2 and int((t - T_EET) * 5) % 2 == 0
    if hap: pd = pd.rotate(6, resample=Image.BICUBIC, expand=True, center=(pd.width, pd.height))     # hoofd omlaag = happen
    WACHT.plaats("paard", (PAARD_X - pd.width / 2, PAARD_VOET - pd.height, PAARD_X + pd.width / 2, PAARD_VOET), op="gras")
    w0 = sprite("paard", hh, spiegel=True).width
    img.paste(pd, (int(PAARD_X + w0 / 2 - pd.width), int(PAARD_VOET - pd.height)), pd)
def bek():                                               # bek van het paard (gespiegeld: kijkt naar links), verhouding uit de lange video
    s = PAARD_H / 470; return PAARD_X - 285 * s, PAARD_VOET - 335 * s
MATKL = ((176, 126, 64), (90, 60, 30), (140, 95, 45))
def mat_stoep(img):                                      # deurmat plat op de stoep voor de achterdeur, met WELCOME
    BR, RD, DK = MATKL; d = ImageDraw.Draw(img)
    d.polygon([(50, 704), (212, 704), (226, 734), (36, 734)], fill=BR, outline=RD)
    for k in range(40): px = 50 + (k * 37) % 160; py = 708 + (k * 13) % 22; d.line((px, py, px + 3, py + 2), fill=DK, width=1)
    d.text((131, 719), "WELCOME", font=font(FB, 20), fill=(80, 50, 25), anchor="mm")
    WACHT.plaats("deurmat op de stoep", (36, 704, 226, 734), op="stoep")
def mat(img):                                            # aangevreten kokosmat hangt uit de bek (zelfde kleur als op de stoep)
    bx, by = bek(); d = ImageDraw.Draw(img); BR, RD, DK = MATKL
    x0, x1, y0 = bx - 70, bx + 40, by
    rand = [(x1 + 2, y0 + 50), (x1 - 10, y0 + 60), (x1 - 2, y0 + 70), (bx - 10, y0 + 66), (x0 + 4, y0 + 72), (x0 - 2, y0 + 46)]
    d.polygon([(x0, y0 + 6), (x1, y0)] + rand, fill=BR, outline=RD)
    for k in range(36): px = x0 + 6 + (k * 37) % (x1 - x0 - 12); py = y0 + 10 + (k * 53) % 52; d.line((px, py, px + 3, py + 2), fill=DK, width=2)
    d.text((x0 + 8, y0 + 22), "WELC", font=font(FB, 20), fill=(80, 50, 25))
    WACHT.plaats("deurmat", (x0 - 2, y0, x1 + 2, y0 + 72), op="bek", punt=(bx, by + 4))
TAG_X, TAG_Y = 482, 1192                                 # aan de plankrand onder het tweede melkpak (onderste plank)
def prijs(img, t):
    st = [(T_50, "$50"), (T_100, "$100"), (T_200, "$200")]; nu = [(t0, p) for t0, p in st if t >= t0]
    if not nu: return
    t0, p = nu[-1]; sch = ps.pop((t - t0) / 0.3); d = ImageDraw.Draw(img)
    f = font(FB, int(60 * sch)); b = d.textbbox((0, 0), p, font=f); tw, th = b[2] - b[0], b[3] - b[1]
    bx, by = TAG_X - (tw + 36) / 2, TAG_Y
    WACHT.plaats("prijskaartje", (bx, by, bx + tw + 36, by + th + 30), op="aan:plankrand")
    d.rounded_rectangle((bx, by, bx + tw + 36, by + th + 30), 12, fill=(255, 225, 60), outline=INK, width=5)
    d.text((bx + 18 - b[0], by + 15 - b[1]), p, font=f, fill=(200, 30, 30))
TAFEL = (15, 1065, 1230)                                 # keukentafel: x0, x1, bovenkant (dichte voorkant tot onder de voeten)
def tafel(img):
    x0, x1, y = TAFEL; d = ImageDraw.Draw(img)
    WACHT.plaats("keukentafel", (x0, y, x1, 1540), op="vloer"); WACHT.vlak("keukentafel", [x0, x1, y - 4, y + 30])
    d.rectangle((x0, y, x1, y + 34), fill=(190, 140, 90), outline=INK, width=5)
    d.rectangle((x0 + 20, y + 34, x1 - 20, 1540), fill=(170, 120, 75), outline=INK, width=4)
    for x in range(x0 + 60, x1 - 40, 150): d.line((x, y + 44, x, 1530), fill=(150, 104, 64), width=3)
def kaars(img, t, x, y):
    WACHT.plaats("kaars", (x - 12, y - 105, x + 12, y), op="keukentafel", voor=True)
    d = ImageDraw.Draw(img); d.rectangle((x - 12, y - 70, x + 12, y), fill=(250, 245, 230), outline=INK, width=3)
    fl = 1 + 0.15 * math.sin(t * 13); d.ellipse((x - 11 * fl, y - 105 * fl, x + 11 * fl, y - 70), fill=(255, 200, 60), outline=(240, 120, 30), width=3)
def gloed(img, x, y, r0=520, kracht=0.55):
    g = Image.new("L", img.size, 0); dg = ImageDraw.Draw(g)
    for r in range(r0, 0, -30): dg.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), fill=int(150 * (1 - r / r0)))
    licht = Image.new("RGB", img.size, (255, 190, 90)); return Image.composite(licht, img, g.point(lambda v: int(v * kracht)))
def geld(img, t, x, y):                                  # stapel bankbiljetten op tafel ("your million")
    d = ImageDraw.Draw(img); WACHT.plaats("stapel geld", (x - 94, y - 116, x + 98, y), op="keukentafel", voor=True)
    for k in range(6):                                   # bundeltjes biljetten met een papieren bandje en $
        yy = y - k * 12; xx = x + (k % 2) * 8 - 4
        d.rectangle((xx - 90, yy - 12, xx + 90, yy), fill=(120, 185, 110), outline=(40, 80, 40), width=2)
    xx, yy = x, y - 72
    d.rectangle((xx - 90, yy - 44, xx + 90, yy), fill=(135, 200, 125), outline=(40, 80, 40), width=3)
    d.ellipse((xx - 26, yy - 38, xx + 26, yy - 6), fill=(110, 170, 100), outline=(40, 80, 40), width=2)
    d.text((xx, yy - 22), "$", font=font(FB, 30), fill=(30, 70, 30), anchor="mm")
    d.rectangle((xx - 52, yy - 44, xx - 36, y), fill=(245, 240, 225), outline=(40, 80, 40), width=1)

# ---------- frame ----------
POPS = {"kamer": [dict(n="you", x=540, s=2.0)],
        "keuken": [dict(n="dad", x=250, s=1.8), dict(n="mom", x=560, s=1.8), dict(n="sis", x=850, s=1.8)],
        "tuin": [dict(n="sis", x=820, s=1.8, loop=(T_SIS_IN - 0.9, T_SIS_IN + 0.2, 1250, 820))],
        "winkel": [dict(n="mom", x=915, y=1570, s=1.55, loop=(T_MOM_IN, T_MOM_IN + 1.3, 1250, 915))],      # rechts naast de kast, wijst naar links
        "nacht": [dict(n="you", x=200, s=1.7), dict(n="mom", x=430, s=1.7), dict(n="dad", x=660, s=1.7), dict(n="sis", x=890, s=1.7)]}
TELEFOON = {"kamer": ("you",), "keuken": ("dad", "mom", "sis")}
ZOOM_AAN = True; TEKST_AAN = True                       # uit voor de herkenwachter
GEZ = {}
def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; n = sc["naam"]
    img = bg(sc["bg"]).copy(); WACHT.begin("v-" + sc["bg"], t)
    nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    spreker = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    if n == "tuin":
        if t < T_EET + 0.6: mat_stoep(img)              # ligt bij de deur tot het paard hem pakt
        paard(img, t)
    if n == "winkel": prijs(img, t)
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}; vast = []; GEZ.clear()
    pops = POPS[n]; sp = next((p for p in pops if p["n"] == spreker), None)
    for p in pops:
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]
            if t < a and x0 < -100: continue
            f = ps.ease((t - a) / max(0.1, b - a)); x = x0 + (x1 - x0) * f
            if a <= t < b: loop = (t - a) * 2.2
        if sp is not None and p is not sp: kijk = 0.9 if sp["x"] > x else -0.9
        else: kijk = 0.5 if x < 540 else -0.5
        if n == "tuin" and t >= T_PAARD: kijk = -0.9                    # zus kijkt naar haar paard (links van haar)
        if n == "winkel" and t >= T_50: kijk = -0.9                     # mama kijkt naar het prijskaartje (links van haar)
        geb = "telefoon" if p["n"] in TELEFOON.get(n, ()) else None
        if n == "tuin" and T_PAARD <= t < T_MAT: geb = "wijslinks"
        if n == "winkel" and T_50 <= t < Z[I_MOM][0]: geb = "wijslinks"
        if sp is p and nu is not None:
            geb = next((g for s_, g in ACTIE.items() if tekst_nu.startswith(s_)), geb or ("praat" if t - Z[nu][0] < 2.0 else None))
            if p["n"] in TELEFOON.get(n, ()) and geb == "praat": geb = "telefoon"
        if loop is not None: geb = "rennen"
        emo = emotie(t, nu)
        verb, boos_ = emo == "schrik", emo == "verdriet"
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13
        koppen[p["n"]] = ps.poppetje(d, p["n"], x, p.get("y", 1460), p["s"], t, loop=loop, kijk=kijk, mond=luid(t, p["n"]), knipper=knip,
                                     verbaasd=verb, gebaar=geb, boos=boos_)
        GEZ[p["n"]] = (*koppen[p["n"]], p["s"] * ps.C[p["n"]].get("groot", 1))
        if geb == "telefoon": vast.append(hand(p["n"], x, p.get("y", 1460), p["s"]))
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for hx, hy, S in vast: WACHT.plaats("telefoon in de hand", (hx - 14 * S, hy - 38 * S, hx + 14 * S, hy + 8 * S), op="aan:hand"); telefoontje(img, hx, hy, S, t)
    if n == "tuin" and t >= T_EET + 0.6: mat(img)
    if n == "nacht":
        tafel(img)
        if t >= T_BROOD:
            sch = 1.0 if t < T_MEER else 1 + 0.12 * min(1, (t - T_MEER) / 0.4)
            zet(img, "brood", int(95 * sch * ps.pop((t - T_BROOD) / 0.3)), 380, TAFEL[2] + 4, op="keukentafel", voor=True)
        if t >= T_GELD: geld(img, t, 740, TAFEL[2] + 4)
        if t >= T_UIT:
            f = min(1, (t - T_UIT) / 0.15); img = Image.blend(img, Image.new("RGB", img.size, (10, 12, 30)), 0.58 * f)
        if t >= T_KAARS: img = gloed(img, 560, TAFEL[2] - 150, 700, 0.7); kaars(img, t, 560, TAFEL[2] + 4)
        if t >= T_BROOD: img = gloed(img, 380, TAFEL[2] - 40, 160, 0.35)
    if n == "kamer" and TEKST_AAN: telefoon(img, t)
    if TEKST_AAN:
        if nu is not None and Z[nu][4] in NAAM and spreker in koppen:      # naamlabel boven het hoofd van wie praat
            hx_, hy_ = koppen[spreker]; dd = ImageDraw.Draw(img); fn = font(FB, 30); n_ = NAAM[Z[nu][4]]; nb = dd.textlength(n_, font=fn); yy = hy_ - 30
            if n == "kamer": R_ = 60 * GEZ[spreker][2]; hx_ = hx_ + R_ + nb / 2 + 26; yy = hy_ + R_ * 0.55     # boven het hoofd staat de telefoon
            dd.rounded_rectangle((hx_ - nb / 2 - 14, yy - 42, hx_ + nb / 2 + 14, yy - 2), 10, fill=(120, 80, 220)); dd.text((hx_ - nb / 2, yy - 40), n_, font=fn, fill=(255, 255, 255))
            dd.polygon([(hx_ - 10, yy - 3), (hx_ + 10, yy - 3), (hx_, yy + 10)], fill=(120, 80, 220))
        if n in KOP: kop(img, "DAY 30" if n == "nacht" and t >= Zs(I_BROOD) else KOP[n], None, 150, 84, KL["geel"], ps.pop((t - sc["t"]) / 0.3))
        ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1], 60 * v[2]) for k_, v in GEZ.items()})
    return img

# ---------- geluid (zelf gemaakt, alleen wat je ziet) ----------
def geluid():
    rng = np.random.default_rng(5); uit = np.zeros(int((EIND + 1) * SR), np.float32)
    def tt(d): return np.arange(int(d * SR)) / SR
    def leg(x, t, v):
        i = int(t * SR); m = min(len(x), len(uit) - i)
        if m > 0 and i >= 0: uit[i:i + m] += v * x[:m].astype(np.float32)
    x = tt(0.45); bzz = np.sign(np.sin(2 * np.pi * 150 * x)) * 0.3 * (np.sin(2 * np.pi * 8 * x) > 0)
    x = tt(1.2); kaching = sum(np.sin(2 * np.pi * f * (x - o)) * (x > o) * np.exp(-np.maximum(0, x - o) * 5) for f, o in [(1319, 0), (1760, 0.08), (2637, 0.16)]) * 0.4 + rng.normal(0, 1, len(x)) * np.exp(-x * 40) * 0.3
    x = tt(0.3); papier = np.convolve(rng.normal(0, 1, len(x)), np.ones(6) / 6, "same") * np.exp(-x * 12) * 0.6
    x = tt(0.18); stap = np.sin(2 * np.pi * 110 * x) * np.exp(-x * 30) * 0.5
    x = tt(0.06); klik = rng.normal(0, 1, len(x)) * np.exp(-x * 90) + np.sin(2 * np.pi * 1200 * x) * np.exp(-x * 80)
    x = tt(0.8); uitgaan = np.sin(2 * np.pi * np.cumsum(220 - 180 * x / 0.8) / SR) * np.exp(-x * 3) * 0.6
    x = tt(0.25); plof = np.sin(2 * np.pi * (90 - 60 * x) * x) * np.exp(-x * 18)
    for j in range(3): leg(bzz, 0.05 + j * 0.6, 0.5)
    leg(kaching, T_BANK + 0.25, 0.6)
    for q in np.arange(T_SIS_IN - 0.9, T_SIS_IN + 0.2, 0.22): leg(stap, q, 0.5)
    leg(plof, T_PAARD, 0.8)
    for q in (0.15, 0.45, 0.75, 1.05): leg(papier, T_EET + q, 0.9)
    for q in np.arange(T_MOM_IN, T_MOM_IN + 1.3, 0.22): leg(stap, q, 0.5)
    for t0 in (T_50, T_100, T_200): leg(kaching, t0, 0.45)
    leg(uitgaan, T_UIT - 0.1, 0.8); leg(klik, T_KAARS, 0.5)
    uit /= max(1, np.abs(uit).max() / 0.9)
    sf.write(HIER / "sfx.wav", uit, SR)

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 6, 480 * 2)); [pl.paste(im, (270 * (i % 6), 480 * (i // 6))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); sys.exit()
    geluid()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-miljoen.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); print("KLAAR short-miljoen.mp4", round(EIND, 1), "s")
