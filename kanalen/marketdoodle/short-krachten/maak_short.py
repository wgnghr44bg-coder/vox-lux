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
HOEK = {"zwaai": (None, 150), "wijs": (None, 100), "vast": (None, 70), "juich": (-160, 160), "duim": (None, 125), "hoofdhanden": (-172, 172),
        "wijslinks": (-100, None), "armen-open": (-75, 75), "schrik": (-128, 128), "haar": (None, 165), "denk": (None, -116)}
LAGEN = {}
def _handen(naam, x, y, s, geb):
    """handpunten van een gebaar (voor de figuurwachter: moeten in beeld zijn)"""
    if geb is None or geb == "rennen": return []
    if isinstance(geb, tuple): hk = (geb[1], geb[2]); g_ = "hoek"
    else: hk = HOEK.get(geb, (None, None)); g_ = geb
    S = s * ps.C[naam].get("groot", 1.0); sch = y - 175 * S; uit = []
    for kant, h in ((-1, hk[0]), (1, hk[1])):
        if h is None: continue
        uit.append((x + kant * 44 * S + math.sin(math.radians(h)) * 82 * S, sch + math.cos(math.radians(h)) * 82 * S, g_))
    return uit
def teken(img, figs, t, nu, registreer=True):              # figs: (naam, x, y, s, gebaar, kijk, loop)
    koppen = {}
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    for naam, x, y, s, geb, kijk, loop in figs:
        if sp == naam and nu in ACTIE: geb = ACTIE[nu]
        emo = emotie(t, nu) if (sp is None or naam == sp) else None
        laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)   # 28 nov: eigen laag per poppetje (figuurwachter)
        hx, hy = ps.poppetje(d, naam, x, y, s, t, loop=loop, kijk=kijk, mond=luid(t, naam), knipper=(t + hash(naam) % 7 * 0.4) % 3.4 < 0.13,
                             verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=geb if loop is None else "rennen")
        laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); LAGEN[naam] = laag
        koppen[naam] = (hx, hy); S = s * ps.C[naam].get("groot", 1)
        GEZ[naam] = (*hoofd(naam, x, y, s), S); GEB[naam] = "rennen" if loop is not None else geb
        WACHT.persoon(naam, y, 306 * S)
        kx, ky = hoofd(naam, x, y, s); lijf = (x - 48 * S, y - 197 * S, x + 48 * S, y - 92 * S)
        FW_INFO[naam] = ((kx, ky, 60 * S), lijf, _handen(naam, x, y, s, GEB[naam]))
        if registreer: FW.figuur(naam, laag, *FW_INFO[naam])
    return koppen
from figuurwachter import Figuurwachter
FW = Figuurwachter(); FW_INFO = {}

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
ACTIE = {I_MOM: "juich", I_SIS: "wijs", I_YOU: "zwaai"}     # papa: armen per moment (papa_armen)
NAAM["mom"] = ("MOM", (200, 160, 255))

# ---------- handen (zelfde maten als pop_short.poppetje: schouder x±44s, sch = y-175s, arm 82s, hoek 0 = omlaag) ----------
def hand(naam, x, y, s, hoek, kant):
    S = s * ps.C[naam].get("groot", 1.0); sch = y - 175 * S
    return x + kant * 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S
STAAT = set()                                              # wat er NU gebeurt (voor de momentwachter)
T_SIT = kw(I_MAMA, "sit", -0.15)

# ---------- keuken: papa bij de koelkast, pot open, deur eraf ----------
KOEL = (835, 420, 1060, 955)                               # koelkast in de keuken-achtergrond (achtergronden.json v-keuken)
PAPA = (690, 1000)
def papa_s(): return schaal("keuken", "dad", PAPA[1])
def papa_armen(t, n):
    """(links, rechts) armhoek van papa per moment"""
    if n == "slot" or t < T_OPEN: return 13, -13                                       # pot met twee handen vast
    if t < T_OPEN + 0.25: u = (t - T_OPEN) / 0.25; return 13, -13 - 55 * u           # rechterhand naar het deksel
    if t < T_RIP - 0.35: return 13, -68 + 55 * min(1, (t - T_OPEN - 0.25) / 0.3)
    if t < T_RIP + 0.25: u = min(1, (t - (T_RIP - 0.35)) / 0.3); return 13 - 20 * u, -13 + 88 * u   # rechterhand naar de koelkastdeur
    u = min(1, (t - T_RIP - 0.25) / 0.35); return -7 - 153 * u, 75 + 85 * u          # deur omhoog boven het hoofd
def koelkast(img, t, n):
    open_ = n == "keuken" and t >= T_RIP + 0.05
    if not open_: WACHT.plaats("koelkast", KOEL, op="beeld"); return
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = KOEL
    d.rectangle((x0 + 12, y0 + 12, x1 - 12, y1 - 12), fill=(235, 245, 248), outline=INK, width=5)
    for k_ in range(3): d.line((x0 + 20, y0 + 150 + k_ * 130, x1 - 20, y0 + 150 + k_ * 130), fill=(170, 200, 210), width=8)
    for k_, (kx, kl) in enumerate(((x0 + 50, (240, 200, 60)), (x0 + 120, (220, 80, 70)), (x0 + 170, (120, 190, 110)))):
        d.rounded_rectangle((kx, y0 + 80 + 130 * k_, kx + 40, y0 + 145 + 130 * k_), 8, fill=kl, outline=INK, width=3)
    WACHT.plaats("koelkast", KOEL, op="beeld")
def deur(img, cx, cy, hoek):
    w_, h_ = KOEL[2] - KOEL[0], KOEL[3] - KOEL[1]
    laag = Image.new("RGBA", (w_ + 20, h_ + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.rounded_rectangle((5, 5, w_, h_), 22, fill=(170, 220, 210), outline=INK, width=6)
    d.line((30, int(h_ * 0.42), w_ - 25, int(h_ * 0.42)), fill=INK, width=5)
    d.rounded_rectangle((22, int(h_ * 0.15), 38, int(h_ * 0.35)), 6, fill=(120, 130, 145), outline=INK, width=3)
    if hoek: laag = laag.rotate(hoek, expand=True, resample=Image.BICUBIC)
    img.paste(laag, (int(cx - laag.width / 2), int(cy - laag.height / 2)), laag)
    WACHT.plaats("koelkastdeur", (cx - laag.width / 2, cy - laag.height / 2, cx + laag.width / 2, cy + laag.height / 2), op="beeld")
def keuken_actie(img, t, n):
    x, y = PAPA; s = papa_s(); S = s * 1.15; L, R = papa_armen(t, n)
    hl, hr = hand("dad", x, y, s, L, -1), hand("dad", x, y, s, R, 1)
    jx, jy = (hl[0] + hr[0]) / 2, (hl[1] + hr[1]) / 2                                  # pot tussen de handen
    pot_los = n == "keuken" and t >= T_RIP - 0.35
    if pot_los: jx, jy = x - 95 * S, y - 22 * S                                         # papa zet de pot neer (op de vloer)
    s_ = sprite("augurkpot", 52 * S); deksel_af = n == "keuken" and t >= T_OPEN + 0.3
    pot_ = s_.crop((0, int(s_.height * 0.17), s_.width, s_.height)) if deksel_af else s_
    if not pot_los and n == "keuken" and T_OPEN + 0.25 <= t < T_OPEN + 0.5: jx += math.sin(t * 90) * 4       # trillen bij het openen
    img.paste(pot_, (int(jx - pot_.width / 2), int(jy + s_.height / 2 - pot_.height)), pot_)
    WACHT.plaats("augurkenpot", (jx - s_.width / 2, jy - s_.height / 2, jx + s_.width / 2, jy + s_.height / 2), op="beeld")
    d = ImageDraw.Draw(img)
    if deksel_af:
        d.ellipse((jx - s_.width * 0.36, jy - s_.height / 2 + s_.height * 0.15, jx + s_.width * 0.36, jy - s_.height / 2 + s_.height * 0.24), fill=(70, 110, 60), outline=INK, width=3)
        u = t - T_OPEN - 0.3
        if u < 1.6:                                        # deksel vliegt eraf + POP!
            lx, ly = jx + 160 * u, jy - s_.height / 2 - 420 * u + 380 * u * u
            d.ellipse((lx - 0.4 * s_.width, ly - 14, lx + 0.4 * s_.width, ly + 14), fill=(190, 195, 205), outline=INK, width=4); STAAT.add("deksel-los")
            if u < 0.5:
                kop(img, "POP!", jx + 70, jy - s_.height - 30, 70, (255, 255, 255), ps.pop(u / 0.15))
                for k_ in range(8):
                    a = k_ / 8 * 6.283; d.line((jx + math.cos(a) * 60, jy - s_.height / 2 + math.sin(a) * 40, jx + math.cos(a) * 110, jy - s_.height / 2 + math.sin(a) * 75), fill=(255, 255, 255), width=6)
    if n == "keuken" and t >= T_RIP + 0.05:                # deur los: eerst uit de koelkast getrokken, dan boven het hoofd
        u = min(1, (t - T_RIP - 0.05) / 0.2); v = min(1, max(0, (t - T_RIP - 0.25) / 0.35))
        kx0 = (KOEL[0] + KOEL[2]) / 2 - 70 * u; ky0 = (KOEL[1] + KOEL[3]) / 2
        # 28 nov (figuurwachter: deur lag over papa's hoofd): deur BOVEN het hoofd (onderkant net boven de kruin), eerst omhoog
        # en dan pas opzij (zo schuift hij niet over zijn gezicht), en papa's armen reiken tot aan de deur
        onder = y - 318 * S; bx, by = x, onder - (KOEL[2] - KOEL[0]) / 2
        v1, v2 = min(1, 2 * v), max(0, 2 * v - 1)
        dx_, dy_ = kx0 + (bx - kx0) * v2, ky0 + (by - ky0) * v1
        if v >= 0.5:
            for kant in (-1, 1):                           # lange armen van schouder tot de onderkant van de deur
                sx, sy = x + kant * 44 * S, y - 175 * S; ex, ey = dx_ + kant * 95 * S, onder + 4
                d.line((sx, sy, ex, ey), fill=INK, width=int(28 * S)); d.line((sx, sy, ex, ey), fill=(90, 180, 110), width=int(22 * S))
                d.ellipse((ex - 13 * S, ey - 13 * S, ex + 13 * S, ey + 13 * S), fill=INK); d.ellipse((ex - 10 * S, ey - 10 * S, ex + 10 * S, ey + 10 * S), fill=ps.HUID)
        deur(img, dx_, dy_, 90 * v + 8 * u * (1 - v)); STAAT.add("deur-los")
        if v >= 1: STAAT.add("deur-boven")
        if u < 1:                                          # krak
            for k_ in range(7):
                a = k_ / 7 * 6.283; cx, cy = KOEL[0] + 10, (KOEL[1] + KOEL[3]) / 2
                d.line((cx + math.cos(a) * 40, cy + math.sin(a) * 60, cx + math.cos(a) * 120, cy + math.sin(a) * 170), fill=(255, 240, 150), width=8)
    return L, R

# ---------- eetkamer: mama zoeft, jij gaat zitten, eten en huiswerk ----------
TAFEL_Y = 790
TAFEL_TOP = 766                                            # achterrand van het tafelblad (gemeten in eetkamer.png): wie erachter zit, verdwijnt hier
TAFEL = (180, 765, 880, 1160)                              # stuk achtergrond met tafel (vóór jou geplakt = jij zit achter de tafel)
def mama_x(t):
    if T_SPEED <= t < T_DINER + 0.3: return 520 + 310 * math.sin((t - T_SPEED) * 13)
    return 800                                             # ruimte rechts voor haar duim omhoog ("Done!")
def jij_eet(t):
    """x, y van jou in de eetkamer (loopt binnen, gaat zitten achter de tafel)"""
    if t < T_DINER: return None
    a = ps.ease(min(1, (t - T_DINER) / 0.9)); x = -80 + (330 + 80) * a
    # gaat zitten = klimt op de stoel: zijn buik komt op tafelhoogte, borst en buik boven het tafelblad (eigenaar 28 nov:
    # "zit nog steeds niet goed aan tafel" -> eerst zag je alleen zijn schouders, alsof hij achter de tafel stond)
    y = 1105 - 105 * ps.ease(min(1, max(0, t - T_SIT) / 0.3))
    return x, y, (t - T_DINER) * 2.2 if a < 1 else None
def eten(img, t):
    if t >= T_DINER + 0.3:
        s_ = sprite("diner", 360); img.paste(s_, (int(560 - s_.width / 2), int(TAFEL_Y + 25 - s_.height)), s_)
        WACHT.plaats("diner", (560 - s_.width / 2, TAFEL_Y + 25 - s_.height, 560 + s_.width / 2, TAFEL_Y + 25), op="beeld")
    if t >= T_HUISWERK + 0.2:
        d = ImageDraw.Draw(img); x0, y0 = 240, TAFEL_Y - 14                  # plat op het tafelblad, vóór je (niet voor je gezicht)
        d.polygon(((x0 + 20, y0), (x0 + 230, y0), (x0 + 250, y0 + 62), (x0, y0 + 62)), fill=(252, 250, 240), outline=INK)
        for k_ in range(4): d.line((x0 + 30, y0 + 10 + k_ * 13, x0 + 170, y0 + 10 + k_ * 13), fill=(150, 160, 190), width=4)
        if t >= T_FOUT:
            for k_ in range(4):
                cx, cy = x0 + 205, y0 + 11 + k_ * 13
                d.line((cx - 8, cy - 6, cx + 8, cy + 6), fill=(220, 40, 40), width=5); d.line((cx - 8, cy + 6, cx + 8, cy - 6), fill=(220, 40, 40), width=5)
            STAAT.add("fout")
        WACHT.plaats("huiswerk", (x0, y0, x0 + 250, y0 + 62), op="beeld")

# ---------- woonkamer ----------
def gedachte(img, x, y, t):
    d = ImageDraw.Draw(img)
    for k_, r in enumerate((14, 22)): d.ellipse((x - 40 - k_ * 35 - r, y + 150 - k_ * 50 - r, x - 40 - k_ * 35 + r, y + 150 - k_ * 50 + r), fill=(255, 255, 255), outline=INK, width=4)
    d.ellipse((x - 150, y - 150, x + 150, y + 60), fill=(255, 255, 255), outline=INK, width=6)
    s_ = sprite("koekje", 150); img.paste(s_, (int(x - s_.width / 2), int(y - 45 - s_.height / 2)), s_)
    WACHT.plaats("koekje", (x - 75, y - 120, x + 75, y + 30), op="beeld"); STAAT.add("gedachte")
def gloed(img, x, y, t):
    d = ImageDraw.Draw(img)
    for k_ in range(3):
        r = 110 + ((t * 120 + k_ * 50) % 150); d.ellipse((x - r, y - r * 0.8, x + r, y + r * 0.8), outline=(190, 120, 255), width=6)
    STAAT.add("gloed")
def onzichtbaar(t): return scene(t)["naam"] == "woonkamer" and t >= T_ONZ

# ---------- camera ----------
def _doel(t):
    sc = scene(t); n = sc["naam"]
    cx, cy, zm = 540, 1000, 1.0
    if n in ("keuken", "slot"): cx, cy, zm = 780, 760, 1.42 + (min(0.08, t * 0.02) if n == "keuken" else 0)
    if n == "eetkamer": cx, cy, zm = 560, 900, 1.05
    if n == "woonkamer": cx, cy, zm = (540, 1100, 1.0) if t < T_ONZ else (700, 1150, 1.25)
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz
        cx += (dx - cx) * 0.12; cy += (dy - cy) * 0.12; zm += (dz - zm) * 0.12
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

# tekstwachter: wat genoemd wordt, moet in beeld zijn; momentwachter: wat gezegd wordt moet je op dat moment zien gebeuren
ZIE = {"super strength": ["tekst:SUPER STRENGTH"], "jar of pickles": ["augurkenpot"], "fridge door": ["koelkastdeur"], "fridge doors": ["koelkastdeur"],
       "mom has": ["mom"], "super speed": ["tekst:SUPER SPEED"], "dinner": ["diner"], "homework": ["huiswerk"], "all wrong": ["huiswerk"],
       "your sister": ["sis"], "read minds": ["tekst:MIND READER"], "last cookie": ["koekje"], "invisible": ["tekst:INVISIBLE"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)
from momentwachter import Momentwachter
MW = Momentwachter(SW, {"opens a jar": ["deksel-los"], "rips the fridge door off": ["deur-los"], "who makes these fridge doors so weak": ["deur-boven"],
                        "super speed": ["zoef"], "dinner is ready": ["diner"], "sit down": ["zitten"], "your homework": ["huiswerk"], "all wrong": ["fout"],
                        "done": ["mom:juich"], "read minds": ["gloed"], "especially yours": ["gedachte"], "you ate the last cookie": ["sis:wijs"],
                        "you are invisible": ["doorzichtig"], "nobody even notices": ["!sis:wijs"], "you are gone": ["doorzichtig"], "sit down": ["zitten", "stoel"], "hello anybody": ["you:zwaai"]})
EIND_VRAAG = "WHICH POWER WOULD YOU PICK? 👇"
EINDTEKSTEN = set()

def frame(t):
    t_b = min(t, Z[-1][1] + 0.4)
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b); bgn = sc["bg"]
    img = bg(bgn).copy(); WACHT.begin("v-" + bgn, t_b); GEZ.clear(); GEB.clear(); SCHERM.clear(); STAAT.clear(); FW.begin(t); FW_INFO.clear()
    koppen = {}
    if n in ("keuken", "slot"):
        koelkast(img, t_b, n)
        L, R = papa_armen(t_b, n)
        koppen.update(teken(img, [("dad", PAPA[0], PAPA[1], papa_s(), ("hoek", L, R), 0.9 if t_b >= T_RIP - 0.5 and n == "keuken" else 0.0, None)], t_b, nu))
        keuken_actie(img, t_b, n)
    if n == "eetkamer":
        jj = jij_eet(t_b)
        if jj:
            # 28 nov (eigenaar: "achter de tafel poppetje is helemaal weg"): niet meer een stuk achtergrond over je heen plakken
            # (dat wiste je lijf uit), maar alleen je onderlijf wegknippen achter het tafelblad: je zit aan tafel, bovenlijf zichtbaar
            if t_b >= T_SIT:                               # stoel achter je (rugleuning steekt boven je schouders uit): je zit echt
                d_ = ImageDraw.Draw(img); sx_ = jj[0]; Sj = schaal("eetkamer", "you", 1105); ry0 = jj[1] - 197 * Sj - 45   # rugleuning breder en hoger dan je schouders
                d_.rounded_rectangle((sx_ - 165, ry0, sx_ + 165, TAFEL_TOP + 5), 20, fill=(150, 95, 55), outline=INK, width=6)
                d_.rounded_rectangle((sx_ - 135, ry0 + 22, sx_ + 135, ry0 + 70), 12, fill=(178, 118, 72), outline=INK, width=4)
                WACHT.plaats("stoel", (sx_ - 165, ry0, sx_ + 165, TAFEL_TOP + 5), op="beeld"); STAAT.add("stoel")
            laag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            koppen.update(teken(laag, [("you", jj[0], jj[1], schaal("eetkamer", "you", 1105), None, 0.6, jj[2])], t_b, nu, registreer=False))
            heel = laag.copy()
            a_ = laag.getchannel("A"); ImageDraw.Draw(a_).rectangle((0, TAFEL_TOP, TAFEL[2], H), fill=0); laag.putalpha(a_)
            img.paste(laag, (0, 0), laag); FW.figuur("you", laag, *FW_INFO["you"])          # de geknipte laag is wat zichtbaar hoort te zijn
            # zitcontrole (eigenaar 28 nov: "zit nog steeds niet goed aan tafel"): de BOVENSTE HELFT van je lijf (borst) moet
            # boven het tafelblad te zien zijn, anders lijkt het een los hoofd achter de tafel
            (kc, lj, hd) = FW_INFO["you"]; FW.figuur("you (zittend: borst boven tafel)", heel, kc, (lj[0], lj[1], lj[2], lj[1] + (lj[3] - lj[1]) * 0.5), hd)
            if t_b >= T_SIT + 0.15: STAAT.add("zitten")
        eten(img, t_b)
        mx = mama_x(t_b); ms = schaal("eetkamer", "mom", 1230)
        if T_SPEED <= t_b < T_DINER + 0.3:                 # wazige kopieën van mama (supersnelheid)
            for k_, a_ in ((3, 0.2), (2, 0.35), (1, 0.55)):
                laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); teken(laag, [("mom", mama_x(t_b - 0.03 * k_), 1230, ms, None, 0.0, None)], t_b, nu, registreer=False)
                laag.putalpha(laag.getchannel("A").point(lambda v, a_=a_: int(v * a_))); img.paste(laag, (0, 0), laag)
            STAAT.add("zoef")
        koppen.update(teken(img, [("mom", mx, 1230, ms, None, -0.6, None)], t_b, nu))
    if n == "woonkamer":
        geb_s = "wijs" if Z[I_SIS][0] - 0.1 <= t_b < Z[I_SIS][1] + 0.3 else None
        kijk_s = -0.9 if t_b >= T_ONZ else 0.6                                             # na "invisible": de zus kijkt de andere kant op
        koppen.update(teken(img, [("sis", 300, 1560, schaal("woonkamer", "sis", 1560, 1.0), geb_s, kijk_s, None)], t_b, nu))
        you = ("you", 780, 1560, schaal("woonkamer", "you", 1560), None, -0.5, None)
        if onzichtbaar(t_b):
            laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); kk = teken(laag, [you], t_b, nu, registreer=False)
            FW.figuur("you", laag, *FW_INFO["you"][:2], handen=FW_INFO["you"][2], verborgen=True)   # bewust doorzichtig; hand wel in beeld
            laag.putalpha(laag.getchannel("A").point(lambda v: int(v * 0.28))); img.paste(laag, (0, 0), laag); koppen.update(kk); STAAT.add("doorzichtig")
        else: koppen.update(teken(img, [you], t_b, nu))
        if "sis" in GEZ and T_LEZEN <= t_b < T_ONZ: gloed(img, GEZ["sis"][0], GEZ["sis"][1], t_b)
        if "you" in GEZ and T_JOUW <= t_b < T_ONZ: gedachte(img, GEZ["you"][0] + 40, GEZ["you"][1] - 330 * GEZ["you"][2], t_b)
    voor_camera = img
    img = camera(img, t); FW.einde(voor_camera, CROP[0])
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    GEZICHTEN[:] = [(k_, ((v[0] - cx0) * zm_, (v[1] + 60 * v[2] - cy0) * zm_, 66 * v[2] * zm_)) for k_, v in GEZ.items()]
    if TEKST_AAN:
        for naam, (hx_, top_) in koppen.items():
            if naam == "you" and onzichtbaar(t_b): continue
            tekst, kl = NAAM[naam]; X = (hx_ - cx0) * zm_; Y = (top_ - cy0) * zm_
            ps.W, ps.H = W, H; ps.label(img, tekst, X, Y - 45, kl, 0.55)
            bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, (X - bw_ / 2, Y - 70, X + bw_ / 2, Y - 20)))
        if n == "keuken" and T_KRACHT <= t_b < T_OPEN: kop(img, "SUPER STRENGTH", W / 2, 1300, 96, KL["geel"], ps.pop((t_b - T_KRACHT) / 0.25))
        if n == "eetkamer" and T_SPEED <= t_b: kop(img, "SUPER SPEED", W / 2, 1300, 96, KL["geel"], ps.pop((t_b - T_SPEED) / 0.25))
        if n == "woonkamer" and T_LEZEN <= t_b < T_ONZ: kop(img, "MIND READER", W / 2, 300, 96, KL["geel"], ps.pop((t_b - T_LEZEN) / 0.25))
        if n == "woonkamer" and T_ONZ <= t_b: kop(img, "INVISIBLE", W / 2, 300, 96, KL["geel"], ps.pop((t_b - T_ONZ) / 0.25))
        if t_b >= EIND - 3.2:
            # 28 nov: de losse gele pijl was onduidelijk -> gewoon zeggen waar het antwoord moet: in de reacties
            p_ = ps.pop((t_b - (EIND - 3.2)) / 0.3); kop(img, "WHICH POWER", W / 2, 1150, 78, (255, 255, 255), p_); kop(img, "WOULD YOU PICK?", W / 2, 1250, 78, (255, 255, 255), p_)
            kop(img, "TELL ME IN THE COMMENTS", W / 2, 1345, 48, KL["geel"], p_); EINDTEKSTEN.add(EIND_VRAAG)
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1] + 60 * v[2], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1] + 60 * v[2]) for k_, v in GEZ.items()},
           gebaren=dict(GEB), crop=CROP[0])
    MW.zie(t, STAAT | {x[0] for x in WACHT.dit_frame} | {f"{k_}:{g_}" for k_, g_ in GEB.items() if isinstance(g_, str)})
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
    zet_(T_OPEN + 0.3, "plop", plof, 0.7, "augurkenpot")
    zet_(T_RIP + 0.1, "krak", klap, 1.0, "koelkastdeur")
    zet_(T_SPEED + 0.1, "suis", suis, 0.6, "mom"); zet_(T_SIT + 0.15, "stoel", plof, 0.3, "you"); zet_(T_DINER + 0.3, "ting", ting, 0.6, "diner"); zet_(T_HUISWERK + 0.2, "papier", papier, 0.6, "huiswerk")
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
        print("MOMENTWACHTER:", MW.schrijf(HIER / "MOMENTWACHTER.md"), "fouten (zie MOMENTWACHTER.md)")
        print("FIGUURWACHTER:", FW.schrijf(HIER / "FIGUURWACHTER.md"), "fouten (zie FIGUURWACHTER.md)")
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
    print("MOMENTWACHTER:", MW.schrijf(HIER / "MOMENTWACHTER.md"), "fouten (zie MOMENTWACHTER.md)")
    print("FIGUURWACHTER:", FW.schrijf(HIER / "FIGUURWACHTER.md"), "fouten (zie FIGUURWACHTER.md)")
    blad(HIER / "short-krachten.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HIER / "short-krachten.mp4"), "-vf", "scale=720:1280", "-c:v", "libx264", "-b:v", "1100k",
                    "-c:a", "aac", "-b:a", "128k", str(HIER / "short-krachten-720.mp4")])
    print("KLAAR short-krachten.mp4", round(EIND, 1), "s")
