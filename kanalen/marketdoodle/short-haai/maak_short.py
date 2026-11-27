"""What If You Built A Shark That Can Walk? — Short, staand 1080x1920 (27 nov 2026). Hype: "What If You Built A Snake That
Can Fly" (52k views/uur). Regels Studio-analyse: vraag in seconde 1, ± 40 s, laatste zin loopt terug naar de eerste.
Zelfde opzet en controles als Black Friday: naamlabels, plaatskaarten, scènewachter (ondergrond, maat), tekstwachter (genoemd =
gezien, spreker, gevoel, RIJDEN, DOEN), LAYOUT, geluidcheck, TEKSTCONTROLE.jpg.
Gebruik: <omnivoice-venv>/python maak_short.py [--tekst | --plaat]  -> short-haai.mp4"""
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
        im = los(Image.open(HIER / "afbeeldingen" / f"{n}.png"))
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

# ---------- tijden ----------
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_HOOK, I_STAP, I_OPRIT, I_SCHOOL, I_SIS = zi("What if"), zi("Okay, buddy"), zi("It takes one"), zi("Day one"), zi("Best bodyguard")
I_KEUKEN, I_DAD, I_STRAND, I_BANG, I_BAD, I_SLOT = zi("Day two"), zi("That was"), zi("Day three"), zi("Wait."), zi("So now"), zi("And that's why")
T_BEN, T_ARM, T_BREIN = kw(I_HOOK, "Big", -0.1), kw(I_HOOK, "Tiny", -0.1), kw(I_HOOK, "Zero", -0.1)
T_STAPJE = kw(I_OPRIT, "step", -0.1); T_DEUR = kw(I_OPRIT, "through", -0.1)
T_NOBODY = kw(I_SCHOOL, "Nobody", -0.1)
T_NAAR = kw(I_KEUKEN, "walks", -0.1); T_EET = kw(I_KEUKEN, "eats", -0.1)
T_ZEE = kw(I_STRAND, "walks", -0.1); T_TERUG = kw(I_STRAND, "back", -0.4)
T_LAMP = kw(I_BAD, "night", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="garage"), dict(t=Zs(I_OPRIT), naam="oprit"), dict(t=Zs(I_SCHOOL), naam="straat"), dict(t=Zs(I_KEUKEN), naam="keuken"),
      dict(t=Zs(I_STRAND), naam="strand"), dict(t=Zs(I_BAD), naam="badkamer")]
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
PLAATS = {"straat": ("DAY 1", "THE SCHOOL RUN"), "keuken": ("DAY 2", "THE KITCHEN"), "strand": ("DAY 3", "THE BEACH"), "badkamer": ("NIGHT", "THE BATHROOM")}
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)
SCHRIK = ("That was a brand", "Wait. Are you")
BLIJ = ("Best bodyguard", "Okay, buddy")
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]
    if any(tekst.startswith(f_) for f_ in SCHRIK): return "schrik"
    if any(tekst.startswith(f_) for f_ in BLIJ): return "blij"
    return None
ACTIE = {I_STAP: "wijslinks", I_SIS: "juich", I_DAD: "hoofdhanden", I_BANG: "armen-open"}

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
    if sc["naam"] not in PLAATS: return
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

# ---------- de haai: plaatje + getekende grote benen met sneakers en piepkleine armpjes ----------
HAAI_L = 2.0                                               # meter (neus tot staart)
def haai(img, x, voet, bgn, t, loop=None, rechts=True, schud=0.0, op="vloer", benen=True):
    """x = midden, voet = waar de schoenen staan. Geeft het kader terug."""
    m = pxm(bgn, voet); L = HAAI_L * m; s_ = sprite("haai", L, spiegel=not rechts); hs = s_.height
    been = 0.85 * m if benen else 0; bob = abs(math.sin(loop * math.pi)) * 0.04 * m if loop is not None else 0
    jx = math.sin(t * 60) * schud * 8
    top = voet - been - 0.74 * hs - bob; x0 = x - L / 2 + jx
    box = (x0, top, x0 + L, voet); WACHT.plaats("haai", box, op=op)
    d = ImageDraw.Draw(img); dik = max(6, int(0.17 * m)); grijs = (120, 130, 145)
    if benen:
        for k_, fx in enumerate((0.40, 0.58)):
            hx = x0 + L * (fx if rechts else 1 - fx); hy = top + 0.70 * hs
            zw = math.sin((loop or 0) * math.pi + k_ * math.pi) * 0.35 if loop is not None else 0
            vx, vy = hx + math.sin(zw) * been, hy + math.cos(zw) * been - bob * 0
            d.line((hx, hy, vx, vy), fill=INK, width=dik + 8); d.line((hx, hy, vx, vy), fill=grijs, width=dik)
            sw_ = 0.30 * m * (1 if rechts else -1)                                     # rode sneaker
            d.rounded_rectangle((min(vx - 0.08 * m, vx + sw_), vy - 0.11 * m, max(vx - 0.08 * m, vx + sw_), vy + 0.02 * m), int(0.05 * m),
                                fill=(220, 50, 50), outline=INK, width=4)
            d.line((min(vx - 0.08 * m, vx + sw_), vy - 0.01 * m, max(vx - 0.08 * m, vx + sw_), vy - 0.01 * m), fill=(255, 255, 255), width=max(3, int(0.03 * m)))
    img.paste(s_, (int(x0), int(top)), s_)
    d = ImageDraw.Draw(img)
    for k_ in range(2):                                    # piepkleine armpjes onder de kop
        ax = x0 + L * ((0.74 if rechts else 0.26) + k_ * 0.03 * (1 if rechts else -1)); ay = top + 0.66 * hs
        ex = ax + (0.10 * m) * (1 if rechts else -1); ey = ay + 0.08 * m + math.sin(t * 8 + k_) * 0.02 * m
        d.line((ax, ay, ex, ey), fill=INK, width=max(4, int(0.05 * m)) + 4); d.line((ax, ay, ex, ey), fill=grijs, width=max(3, int(0.05 * m)))
        d.ellipse((ex - 0.025 * m, ey - 0.025 * m, ex + 0.025 * m, ey + 0.025 * m), fill=grijs, outline=INK, width=2)
    GEB["haai"] = "rennen" if loop is not None else None
    return box

# ---------- scènes ----------
def figuren(n, t):
    nu = nu_i(t)
    if n == "garage":
        y = 1300; return [("you", 930, y, schaal("garage", "you", y), None, -0.9, None)]
    if n == "straat":
        y = 1470; a = ps.ease(min(1, (t - SC[2]["t"]) / 3.0)); x = 120 + 90 * a; loop = (t - SC[2]["t"]) * 2.2 if a < 1 else None
        return [("sis", x, y, schaal("straat", "sis", y, 0.8), None, 0.9, loop)]
    if n == "keuken":
        y = 1480; return [("dad", 170, y, schaal("keuken", "dad", y), None, 0.9, None)] if t >= Z[I_KEUKEN][0] + 1.0 else []
    if n == "strand":
        y = 1640; return [("you", 190, y, schaal("strand", "you", y), None, 0.9, None)]
    return []
def haai_scene(img, n, t):
    if n == "garage": return haai(img, 330, 1290, "garage", t, rechts=True)
    if n == "oprit":
        if t < T_DEUR: return None
        a = ps.ease(min(1, (t - T_DEUR) / 1.8)); v = 1290 + (1560 - 1290) * a
        return haai(img, 540, v, "oprit", t, loop=(t - T_DEUR) * 2.0 if a < 1 else None, rechts=True, op="oprit")
    if n == "straat":
        a = ps.ease(min(1, (t - SC[2]["t"]) / 3.0)); x = 640 + 90 * a
        return haai(img, x, 1250, "straat", t, loop=(t - SC[2]["t"]) * 2.0 if a < 1 else None, op="stoep")
    if n == "keuken":
        a = ps.ease(min(1, max(0, t - T_NAAR) / 1.6)); x = 470 + (700 - 470) * a
        loop = (t - T_NAAR) * 2.0 if 0 < a < 1 else None
        return haai(img, x, 1100, "keuken" if t < T_EET else "keuken-leeg", t, loop=loop, schud=1.0 if T_EET <= t < T_EET + 1.2 else 0)
    if n == "strand":
        if t < T_ZEE: v, x, loop = 1500, 640, None
        elif t < T_TERUG: a = ps.ease(min(1, (t - T_ZEE) / 1.6)); v, x, loop = 1500 + (1110 - 1500) * a, 640 + 60 * a, (t - T_ZEE) * 2.0 if a < 1 else None
        else: a = ps.ease(min(1, (t - T_TERUG) / 0.8)); v, x, loop = 1110 + (1560 - 1110) * a, 700 - 60 * a, (t - T_TERUG) * 3.0 if a < 1 else None
        bang = Z[I_BANG][0] - 0.3 <= t
        op = "zee" if v < 1140 else "zand"
        box = haai(img, x, v, "strand", t, loop=loop, rechts=t < T_TERUG + 0.1 or True, schud=1.0 if bang else 0, op=op)
        if v < 1150:                                       # benen in het water: zee eroverheen
            y0 = int(v - 0.55 * pxm("strand", v)); img.paste(bg("strand").crop((int(box[0]) - 10, y0, int(box[2]) + 10, int(v) + 6)), (int(box[0]) - 10, y0))
        return box
    if n == "badkamer": return None
def bad(img, t):                                           # haai ligt in bad, benen omhoog, ogen dicht, nachtlampje
    d = ImageDraw.Draw(img); L = 980; s_ = sprite("haai", L); x0 = 50; top = 610
    WACHT.plaats("haai", (x0, top, x0 + L, 830), op="bad")
    m = 300; grijs = (120, 130, 145)
    for k_, fx in enumerate((0.42, 0.56)):                 # benen steken omhoog uit het bad
        hx = x0 + L * fx; hy = top + 0.55 * s_.height; vx, vy = hx + (k_ * 2 - 1) * 40, hy - 330
        d.line((hx, hy, vx, vy), fill=INK, width=60); d.line((hx, hy, vx, vy), fill=grijs, width=50)
        d.rounded_rectangle((vx - 30, vy - 90, vx + 40, vy + 10), 18, fill=(220, 50, 50), outline=INK, width=4)
    img.paste(s_, (x0, top), s_)
    ex, ey = x0 + L * 0.835, top + s_.height * 0.36                                          # oog dicht (ooglid)
    d.ellipse((ex - 26, ey - 22, ex + 26, ey + 22), fill=(130, 140, 155)); d.arc((ex - 22, ey - 10, ex + 22, ey + 18), 10, 170, fill=INK, width=5)
    img.paste(bg("badkamer").crop((130, 860, 990, 1160)), (130, 860))                        # voorkant van het bad ervoor
    for k_ in range(3):                                    # zzz (het verhaal zegt dat hij slaapt)
        zx, zy = 820 + k_ * 50, 520 - k_ * 70 - (t * 25) % 30
        d.text((zx, zy), "z", font=font(FB, 54 + k_ * 14), fill=(255, 255, 255), stroke_width=4, stroke_fill=INK)
    if t >= T_LAMP:                                        # nachtlampje in het stopcontact, gloeit
        lx, ly = 860, 1330; WACHT.plaats("nachtlampje", (lx - 40, ly - 60, lx + 40, ly + 10), op="vloer")
        gl = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); a = np.zeros((420, 420), np.float32); yy, xx = np.mgrid[0:420, 0:420]
        a = (np.clip(1 - np.sqrt((xx - 210) ** 2 + (yy - 210) ** 2) / 210, 0, 1) ** 2 * 200).astype(np.uint8)
        gl = Image.merge("RGBA", [Image.new("L", (420, 420), c) for c in (255, 220, 120)] + [Image.fromarray(a)]); img.paste(gl, (lx - 210, ly - 230), gl)
        d = ImageDraw.Draw(img); d.ellipse((lx - 36, ly - 60, lx + 36, ly + 8), fill=(255, 236, 150), outline=INK, width=4)
        d.rectangle((lx - 20, ly, lx + 20, ly + 10), fill=(230, 230, 235), outline=INK, width=3)
def deur_gat(img, t):                                      # gat in de garagedeur + planken op de oprit
    d = ImageDraw.Draw(img); cx, cy = 535, 1090; f = min(1, (t - T_DEUR) / 0.25)
    pts = [(cx + math.cos(a) * r * f, cy + math.sin(a) * r * 0.8 * f) for a, r in zip(np.linspace(0, 2 * math.pi, 15, endpoint=False), (230, 190, 245, 175, 220, 160, 240, 180, 225, 170, 235, 185, 215, 175, 240))]
    WACHT.plaats("garagedeur", (cx - 245, cy - 200, cx + 245, cy + 200), op="beeld")
    d.polygon(pts, fill=(45, 40, 45), outline=INK); d.line(pts + [pts[0]], fill=(250, 250, 250), width=6)
    zet_plank(img, t)
def zet_plank(img, t):
    s_ = sprite("garagedeur", 330); v = 1400
    WACHT.plaats("garagedeur", (240 - s_.width / 2, v - s_.height, 240 + s_.width / 2, v), op="oprit"); img.paste(s_, (int(240 - s_.width / 2), int(v - s_.height)), s_)
def koelkast(img, t):
    if t < T_EET: WACHT.plaats("koelkast", (835, 420, 1060, 955), op="beeld")
def kruimels(img, t):
    if not (T_EET <= t < T_EET + 2.5): return
    d = ImageDraw.Draw(img); u = t - T_EET
    for k_ in range(10):
        x = 900 + (k_ * 37) % 140 - 70 + u * (k_ - 5) * 30; y = 640 + u * 300 + (k_ * 23) % 60
        if y < 1100: d.rectangle((x, y, x + 18, y + 14), fill=(160, 215, 200) if k_ % 2 else (235, 235, 240), outline=INK)

# ---------- camera ----------
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = nu_i(t)
    cx, cy, zm = 540, 1150, 1.0 + min(0.12, (t - sc["t"]) * 0.03)
    if n == "garage":
        cx, cy, zm = 540, 1050, 1.0 + t * 0.03
        if T_BEN <= t < T_ARM: cx, cy, zm = 440, 1200, 1.7           # grote benen
        elif T_ARM <= t < T_BREIN: cx, cy, zm = 600, 1050, 2.2       # piepkleine armpjes
        elif T_BREIN <= t < Z[I_STAP][0]: cx, cy, zm = 680, 930, 2.0  # het hoofd (zero brain)
        elif nu == I_STAP: cx, cy, zm = 650, 1050, 1.15
    if n == "oprit": cx, cy, zm = 540, 1150, 1.0 + min(0.15, max(0, t - T_DEUR) * 0.08)
    if n == "straat": cx, cy, zm = 520, 1150, 1.05
    if n == "keuken": cx, cy, zm = (560, 1000, 1.05) if t < T_EET else (470, 1050, 1.2)
    if n == "strand": cx, cy, zm = 560, 1250, 1.0 if nu != I_BANG else 1.2
    if n == "badkamer": cx, cy, zm = 540, 900, 1.0 + min(0.2, (t - sc["t"]) * 0.04)
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz
        a = 0.08 if n != "garage" else 0.14
        cx += (dx - cx) * a; cy += (dy - cy) * a; zm += (dz - zm) * a
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter: wat genoemd wordt, moet in beeld zijn
ZIE = {"shark": ["haai"], "big legs": ["haai"], "garage door": ["garagedeur"], "your sister": ["sis"], "walks to the fridge": ["koelkast", "haai"],
       "eats the whole fridge": ["koelkast"], "brand new fridge": ["tekst:FRIDGE: GONE"], "the sea": ["haai"], "scared of water": ["haai"],
       "bathtub": ["haai"], "night light": ["nachtlampje"], "nobody bullies": ["tekst:BULLIES: 0"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)

def frame(t):
    t_b = min(t, Z[-1][1] + 0.4)
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b)
    bgn = "keuken-leeg" if n == "keuken" and t_b >= T_EET else n
    img = bg(bgn).copy(); WACHT.begin("v-" + bgn, t_b); GEZ.clear(); GEB.clear(); SCHERM.clear()
    if n == "oprit" and t_b >= T_DEUR: deur_gat(img, t_b)
    if n == "oprit" and T_STAPJE <= t_b < T_DEUR:                                          # bonk: de deur trilt
        sh = int(math.sin(t_b * 70) * 6); deel = bg("oprit").crop((240, 900, 830, 1260)); img.paste(deel, (240 + sh, 900))
    if n == "keuken": koelkast(img, t_b)
    figs = figuren(n, t_b)
    if n == "badkamer":
        img = Image.blend(img, Image.new("RGB", (W, H), (20, 25, 60)), 0.35); bad(img, t_b); koppen = {}
    elif n == "strand":
        box = haai_scene(img, n, t_b); koppen = teken(img, figs, t_b, nu)
    else:
        koppen = teken(img, figs, t_b, nu); haai_scene(img, n, t_b)
    if n == "keuken": kruimels(img, t_b)
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
        if n == "straat" and t_b >= T_NOBODY: kop(img, "BULLIES: 0", W / 2, 420, 110, KL["groen"], ps.pop((t_b - T_NOBODY) / 0.3))
        if n == "keuken" and nu == I_DAD: kop(img, "FRIDGE: GONE", W / 2 + 120, 1250, 100, (235, 60, 60), ps.pop((t_b - Z[I_DAD][0]) / 0.3))
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1] + 60 * v[2], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1] + 60 * v[2]) for k_, v in GEZ.items()},
           gebaren=dict(GEB), crop=CROP[0])
    return img

# ---------- geluid: echte opnames (CC0, ../geluiden) + zelfgemaakte plons; alleen wat je ziet ----------
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
    rng = np.random.default_rng(3); uit = np.zeros(int((EIND + 1) * GSR), np.float32); GELUIDEN.clear()
    def zet_(t, n, x, g, zie):
        i = int(t * GSR); j = min(len(uit), i + len(x))
        if j > i >= 0: uit[i:j] += x[:j - i] * g; GELUIDEN.append((t, n, zie))
    plof = _fade(_laad("plof")); klap = _fade(_laad("deur-dicht")); hap = _fade(_drukste(_laad("hap"), 0.5)); slok = _fade(_drukste(_laad("slok"), 0.6))
    x = np.arange(int(0.9 * GSR)) / GSR; plons = np.convolve(rng.normal(0, 1, len(x)), np.ones(30) / 30, "same") * np.exp(-x * 5) * 1.6
    klik = _fade(_laad("klik"))
    for q in (T_STAPJE + 0.05, T_STAPJE + 0.45): zet_(q, "bonk", plof, 0.8, "garagedeur" if q > T_DEUR else "haai-binnen")
    zet_(T_DEUR, "krak", klap, 1.0, "garagedeur")
    for q in np.arange(T_DEUR + 0.2, T_DEUR + 1.8, 0.45): zet_(q, "stap", plof, 0.35, "haai")
    for q in np.arange(SC[2]["t"] + 0.2, SC[2]["t"] + 3.0, 0.45): zet_(q, "stap", plof, 0.3, "haai")
    for q in np.arange(T_NAAR + 0.1, T_NAAR + 1.6, 0.45): zet_(q, "stap", plof, 0.3, "haai")
    for q in (T_EET, T_EET + 0.4, T_EET + 0.8): zet_(q, "hap", hap, 0.8, "haai")
    zet_(T_EET + 1.3, "slok", slok, 0.7, "haai")
    zet_(T_ZEE + 1.2, "plons", plons, 0.6, "haai"); zet_(T_TERUG + 0.1, "plons", plons, 0.5, "haai")
    zet_(T_LAMP, "klik", klik, 0.6, "nachtlampje")
    uit /= max(1, np.abs(uit).max() / 0.9); sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
        if zie == "haai-binnen": continue                    # bonk achter de dichte garagedeur (de deur trilt mee)
        frame(t + 0.15); gezien = {x[0] for x in WACHT.dit_frame} | set(GEZ)
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
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-haai.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-haai.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-haai.mp4"), "-vf", "scale=720:1280", "-c:v", "libx264", "-b:v", "1100k",
                    "-c:a", "aac", "-b:a", "128k", str(HIER / "short-haai-720.mp4")])
    print("KLAAR short-haai.mp4", round(EIND, 1), "s")
