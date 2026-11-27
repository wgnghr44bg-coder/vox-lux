"""GTA-short bij de lange video "What If GTA 6 Was Real Life?" (27 nov 2026), staand 1080x1920. Regels Studio-analyse: vraag in seconde 1, ± 40 s, laatste zin loopt terug naar de eerste.
Zelfde opzet en controles als Black Friday: naamlabels, plaatskaarten, scènewachter (ondergrond, maat), tekstwachter (genoemd =
gezien, spreker, gevoel, RIJDEN, DOEN), LAYOUT, geluidcheck, TEKSTCONTROLE.jpg.
Gebruik: <omnivoice-venv>/python maak_short.py [--tekst | --plaat]  -> short-gta.mp4"""
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
ps.C["buur"] = dict(broek=(70, 90, 60), shirt=(235, 140, 60), haar=(150, 150, 155), kapsel="grijs", groot=1.12)      # Gary
ps.C["agent"] = dict(broek=(30, 35, 60), shirt=(40, 50, 95), haar=(70, 50, 40), kapsel="kort", pet=(30, 35, 70), groot=1.12)
def zi(tekst): return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
I_HOOK, I_WAAROM, I_KAUW, I_DADZ = zi("What if"), zi("Why do I"), zi("Dad drops"), zi("It was an")
I_MELK, I_MOMZ, I_GARY, I_BUUR, I_SLOT = zi("Mom puts"), zi("I just"), zi("And your neighbor"), zi("Nice weather"), zi("And that's only")
T_HEALTH = kw(I_HOOK, "health", -0.1); T_DROP = kw(I_KAUW, "drops", -0.1); T_DING = kw(I_KAUW, "Ding", -0.05)
T_POLITIE = kw(I_KAUW, "police", -0.4); T_PUTS = kw(I_MELK, "puts", -0.1); T_FRIDGE = kw(I_MELK, "fridge", 0.2)
T_MISSIE = kw(I_MELK, "Mission", -0.05); T_400 = kw(I_GARY, "Four", -0.1); T_DAG30 = kw(I_SLOT, "thirty", -0.1)
def Zs(i): return Z[i][0] - 0.1
SC = [dict(t=0, naam="straat"), dict(t=Zs(I_MELK), naam="keuken"), dict(t=Zs(I_GARY), naam="gary"), dict(t=Zs(I_SLOT), naam="slot")]
BGN = {"straat": "straat", "keuken": "keuken", "gary": "straat", "slot": "straat"}
def scene(t): return SC[max(i for i in range(len(SC)) if SC[i]["t"] <= t)]
PLAATS = {}
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25), default=None)
SCHRIK = ("Why do I", "It was an", "I just bought")
BLIJ = ("Nice weather",)
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]
    if any(tekst.startswith(f_) for f_ in SCHRIK): return "schrik"
    if any(tekst.startswith(f_) for f_ in BLIJ): return "blij"
    return None
ACTIE = {I_WAAROM: "hoofdhanden", I_DADZ: "armen-open", I_MOMZ: "armen-open"}
LIJF.update({"MOM": "mom", "BUUR": "buur"}); NAAM.update({"mom": ("MOM", (200, 160, 255)), "buur": ("GARY", (255, 170, 90))})

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
        for gn, (fx, fy, fr) in GEZICHTEN:
            ox = max(x - w / 2, min(fx, x + w / 2)); oy = max(y - h / 2, min(fy, y + h / 2))
            if (ox - fx) ** 2 + (oy - fy) ** 2 < fr ** 2: LAYOUT.add(f"kop '{s}' valt over het gezicht van {gn}")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def _toon(ws):                                            # 27 nov (eigenaar: "maak ervan GTA6, niet het Romeins cijfer"): GTA Six -> GTA 6
    uit = []
    for k, w in enumerate(ws):
        s = w[1]
        if k > 0 and ws[k - 1][1].strip(".,!?").upper() == "GTA":
            kern = s.strip(".,!?"); s = s.replace(kern, {"six": "6", "five": "5"}.get(kern.lower(), kern))
        uit.append([w[0], s, w[2], w[3]])
    return uit
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = _toon([w for w in SW if w[0] == i])
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

# ---------- poppetjes ----------
def hoofd(naam, x, y, s, *_):
    S = s * ps.C[naam].get("groot", 1.0); return x, y - 246 * S
def rhand(naam, x, y, s, hoek):
    S = s * ps.C[naam].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S
def teken(img, figs, t, nu):                                # figs: (naam, x, y, s, gebaar, kijk, loop)
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    for naam, x, y, s, geb, kijk, loop in figs:
        if sp == naam and nu in ACTIE and geb != "vast": geb = ACTIE[nu]
        emo = emotie(t, nu) if (sp is None or naam == sp) else None
        hx, hy = ps.poppetje(d, naam, x, y, s, t, loop=loop, kijk=kijk, mond=luid(t, naam), knipper=(t + hash(naam) % 7 * 0.4) % 3.4 < 0.13,
                             verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=geb if loop is None or geb == "vast" else "rennen")
        koppen[naam] = (hx, hy); S = s * ps.C[naam].get("groot", 1)
        GEZ[naam] = (*hoofd(naam, x, y, s), S); GEB[naam] = "rennen" if loop is not None else geb
        WACHT.persoon(naam, y, 306 * S)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); return koppen

# ---------- game-dingen ----------
def gloed(img, cx, cy, r, kl=(255, 230, 90), sterk=0.55):
    yy, xx = np.mgrid[0:int(r * 2), 0:int(r * 2)]; a = (np.clip(1 - np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r, 0, 1) ** 2 * 255 * sterk).astype(np.uint8)
    L = Image.merge("RGBA", [Image.new("L", (int(r * 2), int(r * 2)), c) for c in kl] + [Image.fromarray(a)]); img.paste(L, (int(cx - r), int(cy - r)), L)
def balkje(img, cx, y, tekst, frac):
    d = ImageDraw.Draw(img); f = font(FB, 44); tw = d.textlength(tekst, font=f); w = 300
    WACHT.plaats("health", (cx - w / 2, y - 56, cx + w / 2, y + 36), op="beeld"); SCHERM.append(tekst)
    gloed(img, cx, y, 190, kl=(140, 255, 160), sterk=0.3); d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, y - 60), tekst, font=f, fill=(255, 255, 255), stroke_width=5, stroke_fill=INK)
    d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + 36), 12, fill=(40, 40, 50), outline=INK, width=5)
    d.rounded_rectangle((cx - w / 2 + 6, y + 6, cx - w / 2 + 6 + (w - 12) * frac, y + 30), 8, fill=(70, 210, 90))
def sterren(img, cx, y, n, t):
    if n <= 0: return
    d = ImageDraw.Draw(img); r = 44; x0 = cx - (n - 1) * r * 1.1
    WACHT.plaats("ster", (x0 - r, y - r, x0 + (n - 1) * r * 2.2 + r, y + r), op="beeld")
    for k in range(n):
        x = x0 + k * r * 2.2
        pts = [(x + (r if j % 2 == 0 else r * 0.45) * math.sin(j * math.pi / 5), y - (r if j % 2 == 0 else r * 0.45) * math.cos(j * math.pi / 5)) for j in range(10)]
        d.polygon(pts, fill=(255, 255, 255), outline=INK); d.line(pts + [pts[0]], fill=INK, width=5)
def minimap(img, t):
    cx, cy, r = 940, 150, 95; WACHT.plaats("minimap", (cx - r, cy - r, cx + r, cy + r), op="beeld")
    L = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=(70, 120, 90, 225))
    for k in range(-3, 4):
        d.line((0, r + k * 45 + 10, 2 * r, r + k * 45 - 10), fill=(225, 225, 210, 235), width=9); d.line((r + k * 55, 0, r + k * 55 + 14, 2 * r), fill=(225, 225, 210, 235), width=7)
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255); L.putalpha(ImageChops.multiply(L.getchannel("A"), m))
    img.paste(L, (cx - r, cy - r), L); d = ImageDraw.Draw(img); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(20, 20, 25), width=7)
    a = t * 0.6; d.polygon([(cx + 22 * math.sin(a), cy - 22 * math.cos(a)), (cx + 14 * math.sin(a + 2.4), cy - 14 * math.cos(a + 2.4)), (cx, cy), (cx + 14 * math.sin(a - 2.4), cy - 14 * math.cos(a - 2.4))], fill=(255, 255, 255), outline=INK)
def cirkel(img, cx, cy, t):
    gloed(img, cx, cy - 30, 230, sterk=0.5); d = ImageDraw.Draw(img); p = 1 + 0.06 * math.sin(t * 5)
    WACHT.plaats("cirkel", (cx - 170, cy - 45, cx + 170, cy + 45), op="vloer")
    d.ellipse((cx - 170 * p, cy - 45 * p, cx + 170 * p, cy + 45 * p), fill=(255, 220, 60), outline=(200, 150, 20), width=6)
    d.ellipse((cx - 125 * p, cy - 30 * p, cx + 125 * p, cy + 30 * p), fill=(255, 240, 140))
AUTOINFO = {"politieauto": dict(regio=(395, 252, 870, 360), glas=(0.08, 0.45, 0.45), raam=(735, 312, 95), voor=1)}
KHOOFD = {}
def _khoofd(n):
    if n not in KHOOFD:
        d_ = ImageDraw.Draw(Image.new("RGBA", (W * SS, H * SS))); hx, hy = ps.poppetje(d_, n, 500, 1000, 1.0, 0.0); KHOOFD[n] = (1000 - hy) / ps.C[n].get("groot", 1.0)
    return KHOOFD[n]
AUTO = {}
def _vul_gaten(a0):
    """Witte delen binnen de auto (deur van de politieauto, zelfde wit als de achtergrond) dicht houden: de omtrek even dikker
    maken zodat kleine kiertjes dicht zijn, de achtergrond van buitenaf vullen, en alles wat daar niet bij hoort is auto."""
    from PIL import ImageFilter
    dik = a0.filter(ImageFilter.MaxFilter(15)); w, h = dik.size
    for p_ in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)):
        if dik.getpixel(p_) == 0: ImageDraw.floodfill(dik, p_, 128)
    buiten = dik.point(lambda v: 255 if v == 128 else 0).filter(ImageFilter.MaxFilter(15))
    return ImageChops.lighter(a0, ImageChops.invert(buiten))
def auto_sprite(n, h, spiegel):
    k = (n, int(h), spiegel)
    if k not in AUTO:
        bron = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB"); w0, h0 = bron.size; m0 = bron.copy()
        for p_ in ((0, 0), (w0 - 1, 0), (0, h0 - 1), (w0 - 1, h0 - 1)): ImageDraw.floodfill(m0, p_, (255, 0, 255), thresh=30)
        a0 = Image.eval(ImageChops.difference(m0, Image.new("RGB", m0.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
        a0 = _vul_gaten(a0)                                # 27 nov: witte deur politieauto niet doorzichtig
        bx0, by0, bx1, by1 = a0.getbbox(); im = bron.convert("RGBA"); im.putalpha(a0); im = im.crop((bx0, by0, bx1, by1)); info = AUTOINFO[n]
        hsv = np.array(bron.convert("HSV")).astype(float) / 255; x0, y0, x1, y1 = info["regio"]; smin, smax, vmin = info["glas"]
        m = np.zeros(hsv.shape[:2], bool); sub = hsv[y0:y1, x0:x1]; m[y0:y1, x0:x1] = (sub[..., 1] >= smin) & (sub[..., 1] <= smax) & (sub[..., 2] >= vmin)
        m = m[by0:by1, bx0:bx1]; a = np.array(im.getchannel("A")); a[m & (a > 0)] = 105; im.putalpha(Image.fromarray(a))
        sc = h / im.height; im = im.resize((max(1, int(im.width * sc)), int(h)), Image.LANCZOS)
        if spiegel: im = im.transpose(Image.FLIP_LEFT_RIGHT)
        cx, cy, hh = info["raam"]; rx, ry = (cx - bx0) * sc, (cy - by0) * sc
        AUTO[k] = (im, (im.width - rx if spiegel else rx, ry, hh * sc, info["voor"] * (-1 if spiegel else 1)))
    return AUTO[k]
def auto(img, n, h, x, voet, op, spiegel, bestuurder, t):
    s_, (rx, ry, hh, richting) = auto_sprite(n, h, spiegel)
    dx, dy = WACHT.plaats(n, (x - s_.width / 2, voet - s_.height, x + s_.width / 2, voet), op=op)
    left, top = x + dx - s_.width / 2, voet + dy - s_.height
    wx, wy = left + rx, top + ry; S = 0.5 * hh / 60; s = S / ps.C[bestuurder].get("groot", 1.0); y = wy - 60 * S + _khoofd(bestuurder) * S
    L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    ps.poppetje(d, bestuurder, wx, y, s, t, kijk=0.9 * richting, knipper=(t % 3.4) < 0.13)
    L = L.resize((W, H), Image.LANCZOS); mk = Image.new("L", (W, H), 0); ImageDraw.Draw(mk).rectangle((left, wy - hh * 0.62, left + s_.width, top + s_.height), fill=255)
    L.putalpha(ImageChops.multiply(L.getchannel("A"), mk)); img.paste(L, (0, 0), L); GEZ[bestuurder] = (wx, wy - 60 * S, S)
    img.paste(s_, (int(left), int(top)), s_)
    aan = int(t * 6) % 2; gloed(img, left + s_.width * 0.48, top + s_.height * 0.08, 70, kl=(255, 60, 60) if aan else (60, 120, 255), sterk=0.7)
def zet(img, n, breed, x, voet, op, naam=None, punt=None, voor=False):
    s_ = sprite(n, breed); dx, dy = WACHT.plaats(naam or n, (x - s_.width / 2, voet - s_.height, x + s_.width / 2, voet), op=op, punt=punt, voor=voor)
    img.paste(s_, (int(x + dx - s_.width / 2), int(voet + dy - s_.height)), s_)

# ---------- scènes ----------
Y = 1320
def figuren(n, t):
    s = lambda naam, y=Y, f=0.92: schaal(BGN[n], naam, y, f)
    if n == "straat":
        f = [("you", 780, Y, s("you"), None, -0.6, None)]
        if t >= Z[I_KAUW][0] - 0.6:
            geb = ("hoek", -16, 20) if T_DROP - 0.2 <= t < T_DROP + 0.5 else None
            f.append(("dad", 300, Y, s("dad"), geb, 0.6, None))
        return f
    if n == "keuken":
        a = ps.ease(min(1, max(0, t - T_PUTS) / 1.3)); x = 260 + (640 - 260) * a; loop = (t - T_PUTS) * 2.2 if 0 < a < 1 else None
        return [("mom", x, Y, s("mom"), "vast" if t < T_FRIDGE else None, 0.9 if t < T_FRIDGE + 0.5 else -0.6, loop)]
    if n == "gary": return [("buur", 560, Y, s("buur"), "zwaai" if Z[I_BUUR][0] <= t < Z[I_BUUR][1] else None, 0.0, None)]
    if n == "slot": return [("buur", 200, Y, s("buur"), None, 0.6, None), ("you", 540, Y, s("you"), None, 0.0, None), ("dad", 880, Y, s("dad"), None, -0.6, None)]
    return []

# ---------- camera ----------
def _doel(t):
    sc = scene(t); n = sc["naam"]; nu = nu_i(t)
    cx, cy, zm = 540, 1100, 1.0 + min(0.1, (t - sc["t"]) * 0.03)
    if n == "straat":
        if t < Z[I_KAUW][0]: cx, cy, zm = 760, 1000, 1.25
        else: cx, cy, zm = 540, 1050, 1.0
    if n == "keuken": cx, cy, zm = 600, 960, 1.05
    if n == "gary": cx, cy, zm = 560, 1000, 1.15
    return cx, cy, zm
CAMTRACK = []
def _maak_track():
    cx, cy, zm = _doel(0); vorige = None
    for i in range(int((EIND + 1) * FPS)):
        t = i / FPS; dx, dy, dz = _doel(t); n = scene(t)["naam"]
        if n != vorige: cx, cy, zm = dx, dy, dz
        cx += (dx - cx) * 0.08; cy += (dy - cy) * 0.08; zm += (dz - zm) * 0.08
        CAMTRACK.append((cx, cy, zm)); vorige = n
_maak_track()
def camera(img, t):
    cx, cy, zm = CAMTRACK[min(len(CAMTRACK) - 1, int(t * FPS))]; bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh); CROP[0] = (x0, y0, x0 + bw, y0 + bh)
    return img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)

ZIE = {"real life": ["minimap"], "health bar": ["health"], "gum wrapper": ["kauwgompapiertje"], "one star": ["ster"],
       "police car": ["in:agent@politieauto"], "milk": ["melk"], "fridge": ["koelkast"], "mission complete": ["tekst:MISSION COMPLETE"], "gary": ["buur"],
       "four hundred": ["tekst:x400"], "day thirty": ["tekst:DAY 30"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)

def frame(t):
    t_b = min(t, Z[-1][1] + 0.4)
    sc = scene(t_b); n = sc["naam"]; nu = nu_i(t_b); bgn = BGN[n]
    img = bg(bgn).copy(); WACHT.begin("v-" + bgn, t_b); GEZ.clear(); GEB.clear(); SCHERM.clear()
    if n == "straat" and t_b >= T_POLITIE:
        a = ps.ease(min(1, (t_b - T_POLITIE) / 1.4)); x = 1500 + (800 - 1500) * a
        auto(img, "politieauto", 300, x, 1080, "stoep", True, "agent", t_b)
    if n == "keuken":
        if T_MISSIE - 1.0 <= t_b < T_MISSIE + 2.5: cirkel(img, 640, 1330, t_b)
        WACHT.plaats("koelkast", (835, 420, 1060, 955), op="beeld")
        if t_b >= T_FRIDGE - 0.3:                                                     # koelkast open, melk staat erin
            d = ImageDraw.Draw(img); d.rectangle((850, 440, 1050, 940), fill=(245, 250, 255), outline=INK, width=6)
            for yy in (600, 760): d.line((858, yy, 1042, yy), fill=(190, 205, 220), width=6)
            gloed(img, 950, 560, 120, kl=(255, 255, 230), sterk=0.4)
            zet(img, "melk", 70, 950, 596, op="aan:koelkast")
    if n == "straat" and t_b < T_DROP: pass
    figs = figuren(n, t_b); koppen = teken(img, figs, t_b, nu)
    if n == "straat" and t_b >= T_DROP and "dad" in koppen:                         # kauwgompapiertje valt uit papa's hand op de stoep
        f_ = [f for f in figs if f[0] == "dad"][0]; hx, hy = rhand("dad", f_[1], f_[2], f_[3], 20); u = min(1, (t_b - T_DROP) / 0.5)
        x_, y_ = hx, hy + (Y - 8 - hy) * u * u; d = ImageDraw.Draw(img)
        WACHT.plaats("kauwgompapiertje", (x_ - 26, y_ - 16, x_ + 26, y_), op="stoep" if u >= 1 else "aan:lucht")
        d.rectangle((x_ - 26, y_ - 16, x_ + 26, y_), fill=(210, 215, 225), outline=INK, width=3)
    if n == "keuken" and t_b < T_FRIDGE:                                              # melk in mama's hand
        f_ = figs[0]; hx, hy = rhand("mom", f_[1], f_[2], f_[3], 70)
        zet(img, "melk", 90, hx, hy + 50, op="hand:mom", punt=(hx, hy), voor=True)
    if n == "straat" and t_b >= T_HEALTH and "you" in GEZ: balkje(img, GEZ["you"][0], GEZ["you"][1] - 40 * GEZ["you"][2] - 60, "HEALTH 100%", 1.0)
    if n == "straat" and t_b >= T_DING and "dad" in GEZ: sterren(img, GEZ["dad"][0], GEZ["dad"][1] - 40 * GEZ["dad"][2] - 60, 1, t_b)
    img = camera(img, t)
    LABELS.clear(); cx0, cy0, cx1, cy1 = CROP[0]; zm_ = W / (cx1 - cx0)
    GEZICHTEN[:] = [(k_, ((v[0] - cx0) * zm_, (v[1] + 60 * v[2] - cy0) * zm_, 66 * v[2] * zm_)) for k_, v in GEZ.items() if k_ != "agent"]
    if TEKST_AAN:
        minimap(img, t)
        for naam, (hx_, top_) in koppen.items():
            tekst, kl = NAAM[naam]; X = (hx_ - cx0) * zm_; Yl = (top_ - cy0) * zm_
            if naam == "you" and n == "straat" and t_b >= T_HEALTH: continue          # health bar staat al boven je hoofd
            if naam == "dad" and n == "straat" and t_b >= T_DING: continue            # ster staat boven papa
            if naam == "mom" and n == "keuken" and t_b >= T_MISSIE: continue          # MISSION COMPLETE staat boven mama
            ps.W, ps.H = W, H; ps.label(img, tekst, X, Yl - 45, kl, 0.55)
            bw_ = 14 * len(tekst) + 40; LABELS.append((tekst, (X - bw_ / 2, Yl - 70, X + bw_ / 2, Yl - 20)))
        if n == "keuken" and t_b >= T_MISSIE: kop(img, "MISSION COMPLETE", W / 2, 280, 84, KL["goud"], ps.pop((t_b - T_MISSIE) / 0.3))
        if n == "keuken" and t_b >= T_MISSIE + 0.6: kop(img, "+50 RESPECT", W / 2, 380, 70, KL["groen"], ps.pop((t_b - T_MISSIE - 0.6) / 0.3))
        if n == "gary" and t_b >= T_400: kop(img, "x400", 880, 560, 120, KL["geel"], ps.pop((t_b - T_400) / 0.3))
        if n == "slot": kop(img, "DAY 1", W / 2, 300, 90, KL["groen"], 1.0)
        if n == "slot" and t_b >= T_DAG30: kop(img, "DAY 30: ???", W / 2, 420, 110, (235, 60, 60), ps.pop((t_b - T_DAG30) / 0.3))
        if t <= Z[-1][1] + 0.3: ondertitel(img, t)
    WACHT.einde(gezichten={k_: (v[0], v[1] + 60 * v[2], 60 * v[2]) for k_, v in GEZ.items()})
    TW.zie(t, nu_i(t), voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1] + 60 * v[2]) for k_, v in GEZ.items()},
           gebaren=dict(GEB), crop=CROP[0])
    return img

# ---------- geluid: echte opnames (CC0, ../geluiden) + zelfgemaakt; alleen wat je ziet ----------
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
    uit = np.zeros(int((EIND + 1) * GSR), np.float32); GELUIDEN.clear()
    def zet_(t, n, x, g, zie):
        i = int(t * GSR); j = min(len(uit), i + len(x))
        if j > i >= 0: uit[i:j] += x[:j - i] * g; GELUIDEN.append((t, n, zie))
    x = np.arange(int(0.35 * GSR)) / GSR; ding = sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 7) for f in (1568, 2350)) * 0.4
    x = np.arange(int(2.0 * GSR)) / GSR; sir = np.sin(2 * np.pi * np.cumsum(np.where((x * 2) % 1 < 0.5, 700, 950)) / GSR) * 0.35 * np.minimum(1, x * 4)
    x = np.arange(int(1.4 * GSR)) / GSR; fan = sum(np.sign(np.sin(2 * np.pi * f * (x - o))) * (x > o) * np.exp(-np.maximum(0, x - o) * 2.2) * 0.12 for f, o in ((523, 0), (659, 0.15), (784, 0.3), (1047, 0.45)))
    zet_(T_DROP + 0.45, "papier", _fade(_drukste(_laad("papier"), 0.4)), 0.4, "kauwgompapiertje")
    zet_(T_DING, "ding", ding, 0.6, "ster"); zet_(T_POLITIE + 0.2, "sirene", sir, 0.45, "politieauto")
    zet_(T_MISSIE, "fanfare", fan, 0.5, "cirkel")
    zet_(T_FRIDGE - 0.1, "deur", _fade(_laad("klik")), 0.6, "koelkast")
    for q in np.arange(T_PUTS + 0.1, T_PUTS + 1.3, 0.3): zet_(q, "stappen", _fade(_drukste(_laad("stappen"), 0.25)), 0.3, "mom")
    uit /= max(1, np.abs(uit).max() / 0.9); sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
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
        pl = Image.new("RGB", (270 * 5, 480 * 2)); [pl.paste(im, (270 * (i % 5), 480 * (i // 5))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); sys.exit()
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "short-gta.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    blad(HIER / "short-gta.mp4", Z, HIER / "TEKSTCONTROLE.jpg"); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    print("KLAAR short-gta.mp4", round(EIND, 1), "s")
