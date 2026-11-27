"""What If GTA 6 Was Real Life? — lange video, liggend 1920x1080 (27 nov 2026), zelfde poppetjes/stijl als $1 Million.
Game-regels in het echte leven: gele pijl, health bar, geldteller, sterren, minimap, missies, respawn bij het ziekenhuis.
Eigen poppetjes en tekeningen, geen GTA-beelden/logo's. GEEN muziek, alleen geluiden van wat je ziet.
Controles: scènewachter, tekstwachter (genoemd = gezien, spreker in beeld, gevoel), LAYOUT, GELUIDCHECK, TEKSTCONTROLE.jpg.
Gebruik: python maak_gta.py [--tekst | --plaat | --proef SEC]  -> gta-echt.mp4 (of gta-proef.mp4)"""
import difflib, json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageChops, ImageEnhance
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools"))
from scenewachter import Scenewachter
from tekstwachter import Tekstwachter, blad

W, H, FPS, SS = 1920, 1080, 30, ps.SS
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
INK = (40, 35, 40)
ps.C.update({                                            # bijfiguren (andere kleuren dan de familie)
 "kassa":   dict(broek=(60, 70, 60), shirt=(110, 170, 80), haar=(90, 60, 40), kapsel="staartjes", groot=1.05),
 "buur":    dict(broek=(70, 90, 60), shirt=(235, 140, 60), haar=(150, 150, 155), kapsel="grijs", groot=1.12),     # Gary
 "zuster":  dict(broek=(120, 190, 210), shirt=(120, 190, 210), haar=(60, 40, 30), kapsel="paard", groot=1.05),
 "ober":    dict(broek=(30, 30, 35), shirt=(245, 245, 245), haar=(40, 35, 30), kapsel="kort", das=(30, 30, 35), groot=1.1),
 "jogger":  dict(broek=(40, 40, 50), shirt=(230, 60, 60), haar=(200, 160, 80), kapsel="kort", groot=1.08),
 "collega": dict(broek=(60, 60, 70), shirt=(150, 160, 175), haar=(70, 50, 40), kapsel="krul", groot=1.05),
})
ps.C["ober2"] = dict(ps.C["ober"], haar=(110, 70, 40)); ps.C["ober3"] = dict(ps.C["ober"], haar=(60, 60, 60), kapsel="krul")
ps.C["jogger2"] = dict(ps.C["jogger"], shirt=(60, 160, 220), haar=(60, 40, 30), kapsel="paard")
ps.C["jogger3"] = dict(ps.C["jogger"], shirt=(250, 200, 60), haar=(40, 30, 25))
ps.C["collega2"] = dict(ps.C["collega"], shirt=(200, 120, 160), kapsel="paard")

# ---------- tijden ----------
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
EIND = Z[-1][1] + 2.5
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
if AUD.ndim > 1: AUD = AUD.mean(axis=1)
LAYOUT = set()
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in SW:
        if i == zin and _norm(w).startswith(_norm(woord)): return t0 + na
    print("LET OP: niet gevonden", zin, woord); LAYOUT.add(f"woord '{woord}' niet gevonden in zin {zin}"); return Z[zin][0] + na
def zi(tekst, n=0): return [i for i, z in enumerate(Z) if z[2].startswith(tekst)][n]
LIJF = {"YOU": "you", "DAD": "dad", "MOM": "mom", "SIS": "sis", "BOSS": "boss", "TEACH": "teach", "KASSA": "kassa",
        "BUUR": "buur", "ZUSTER": "zuster", "OBER": "ober"}
def luid(t, lijf):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == lijf for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
def nu_i(t): return max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)

# ---------- losse voorwerpen ----------
def los(im, tol=30):
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox())
def herkleur(im, tint):                                   # alle kleurige pixels krijgen deze tint (auto spuiten)
    a = im.getchannel("A"); hsv = np.array(im.convert("RGB").convert("HSV")).astype(int)
    m = hsv[..., 1] > 40; hsv[..., 0] = np.where(m, int(tint * 255), hsv[..., 0]); hsv[..., 1] = np.where(m, np.maximum(hsv[..., 1], 150), hsv[..., 1])
    out = Image.fromarray(hsv.astype(np.uint8), "HSV").convert("RGBA"); out.putalpha(a); return out
SPR = {}
def sprite(n, hoogte, spiegel=False, tint=None):
    k = (n, int(hoogte), spiegel, tint)
    if k not in SPR:
        im = los(Image.open(HIER / "afbeeldingen" / f"{n}.png"))
        if tint is not None: im = herkleur(im, tint)
        im = im.resize((max(1, int(im.width * hoogte / im.height)), max(1, int(hoogte))), Image.LANCZOS)
        SPR[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if spiegel else im
    return SPR[k]
WACHT = Scenewachter(HIER.parent / "achtergronden.json")
def zet(img, n, hoogte, x, voet, op=None, punt=None, voor=False, naam=None, **kw_):
    s = sprite(n, hoogte, **kw_)
    dx, dy = WACHT.plaats(naam or n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, punt=punt, voor=voor)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)
BG = {}
def bg(n):
    if n not in BG:
        for m in (HIER, HIER.parent / "video-swap", HIER.parent / "video-miljoen"):
            p = m / "afbeeldingen" / f"{n}.png"
            if p.exists(): break
        BG[n] = Image.open(p).convert("RGB").resize((W, H))
        if n == "straat":                                # AI-vlek (half weggepoetst raam) op het linkerhuis, zoals in miljoen
            d_ = ImageDraw.Draw(BG[n]); d_.rectangle((588, 470, 740, 552), fill=(245, 230, 205))
            d_.rectangle((612, 478, 716, 546), fill=(255, 255, 255)); d_.rectangle((618, 484, 710, 540), fill=(150, 205, 240))
            d_.line((664, 484, 664, 540), fill=(255, 255, 255), width=6); d_.line((618, 512, 710, 512), fill=(255, 255, 255), width=6)
    return BG[n]

# ---------- blokken (scènes) ----------
START = {"Mom! Dad! There's": "open", "You run back inside": "keuken1", "Day one.": "dag1", "Day two.": "winkel", "Day three.": "val",
         "One second later": "zh1", "Day five.": "garage", "Day seven.": "cheat", "It rains rubber": "eenden", "Nobody laughs": "cheat2",
         "Day nine.": "kantoor1", "A giant timer": "timer", "Huge red letters": "kantoor2", "Day ten.": "klas", "Day twelve.": "feit",
         "Day fourteen.": "strand", "Dad is back outside": "zh2", "Day sixteen.": "teddy", "Day eighteen.": "rest", "Day nineteen.": "fiets",
         "Day twenty-one.": "chaos", "Day twenty-four.": "save1", "Super Suck Three Thousand! It sucks": "radio2", "Then you find it": "save2",
         "Day twenty-six.": "team", "Day thirty.": "wakker", "You run downstairs": "eind"}
DAG = {"dag1": 1, "winkel": 2, "val": 3, "zh1": 3, "garage": 5, "cheat": 7, "eenden": 7, "cheat2": 7, "kantoor1": 9, "timer": 9, "kantoor2": 9,
       "klas": 10, "feit": 12, "strand": 14, "zh2": 14, "teddy": 16, "rest": 18, "fiets": 19, "chaos": 21, "save1": 24, "radio2": 24, "save2": 24,
       "team": 26, "wakker": 30, "eind": 30}
BLOK = []
for i, z in enumerate(Z):
    k = next((v for s_, v in START.items() if z[2].startswith(s_)), None)
    if k: BLOK.append(dict(key=k, bg=z[3], a=i, b=i))
    else:
        BLOK[-1]["b"] = i
        if z[3] != BLOK[-1]["bg"]: LAYOUT.add(f"zin {i} is scène {z[3]} maar valt in blok {BLOK[-1]['key']}")
for k, B in enumerate(BLOK): B["t"] = 0.0 if k == 0 else Z[B["a"]][0] - 0.1
for k in range(len(BLOK) - 1): BLOK[k]["eind"] = BLOK[k + 1]["t"]
BLOK[-1]["eind"] = EIND
KB = {B["key"]: B for B in BLOK}

# ---------- figuren ----------
def F(n, x, s=1.6, y=960, **k): return dict(n=n, x=x, s=s, y=y, **k)
def pad_x(p, t):
    """pad = [(t, x), ...] -> (x, loopt?, richting)."""
    if t <= p[0][0]: return p[0][1], False, 0
    for (ta, xa), (tb, xb) in zip(p, p[1:]):
        if ta <= t < tb:
            f = ps.ease((t - ta) / max(0.05, tb - ta)) if abs(xb - xa) < 900 else (t - ta) / max(0.05, tb - ta)
            return xa + (xb - xa) * f, xa != xb, (1 if xb > xa else -1) if xa != xb else 0
    return p[-1][1], False, 0
def rhand(n, x, y, s, hoek):                              # rechterhand bij armhoek (0 = omlaag, 70 = vasthouden, -32 = telefoon)
    S = s * ps.C[n].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S, S
SCHRIK = ("That's terrifying", "Why do I have", "What? It was", "Pick it up", "How do I turn", "Wait. I didn't", "One billion dollars?",
          "Not now, Gary", "This isn't fun", "Oh no", "What's zombie", "Not you again", "I'm an accountant", "It's milk")
VERDRIET = ("This is going to be a long", "He looks very tired", "I hate that this", "Sorry, sir", "I delivered a pizza", "Dad has to start over")
BLIJ = ("They don't recognize", "I'm a genius", "I could get used", "proud of a pizza", "It's over", "Teamwork", "I'm finding all",
        "Okay, you laugh", "Exactly", "Guys! When I", "Beautiful", "Nice weather", "Respawn fee", "Hi again", "I have more codes")
def emotie(t, nu):
    if nu is None: return None
    tekst = Z[nu][2]
    for soort, lijst in (("schrik", SCHRIK), ("verdriet", VERDRIET), ("blij", BLIJ)):
        if any(tekst.startswith(f_) or f_ in tekst for f_ in lijst): return soort
    return None
ACTIE = {"Mom! Dad! There's": "wijslinks", "Why do I have": "hoofdhanden", "What? It was": "armen-open", "Pick it up": "wijslinks",
         "How do I turn": "armen-open", "Wait. I didn't": "armen-open", "Respawn fee": "zwaai", "Hi again": "zwaai",
         "They don't recognize": "juich", "You're driving a purple": "heupen", "Give me that remote": "wijslinks",
         "I'm an accountant": "armen-open", "Not anymore. Go": "wijslinks", "I have never been": "juich", "Side mission": "wijslinks",
         "Can I skip": "denk", "You can't skip": "heupen", "I hate that": "schouders", "One billion dollars?": "schrik",
         "And now we live": "armen-open", "Mom, that man": "wijslinks", "Don't make eye": "nee", "One of one hundred?": "juich",
         "Not now, Gary": "stamp", "I could get used": "juich", "Can I have some bread": "armen-open", "Sorry, sir": "nee",
         "I delivered a pizza": "armen-open", "What can I get": "armen-open", "It's fine. Nobody": "heupen", "This isn't fun": "schouders",
         "Says the guy": "wijslinks", "If this is a game": "denk", "Not you again": "facepalm", "Guys! When I": "wijs",
         "So if something": "denk", "Exactly. Nobody": "armen-open", "Teamwork": "juich", "It's over": "juich", "What's zombie": "schrik",
         "Oh no": "hoofdhanden", "No stars. No money": "juich", "Does that mean": "juich", "No. Eat your": "wijs", "It says I have": "schrik"}
GEZ = {}; GEB = {}; SCHERM = []; CROP = [(0, 0, W, H)]

def teken_figuren(img, figs, t, nu):
    """Tekent de figuren; geeft {naam: (hoofd_x, hoofd_y, S, x, y, s)}."""
    sp = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    tekst_nu = Z[nu][2] if nu is not None else ""
    xs = {}
    for p in figs:
        if "pad" in p: xs[p["n"]] = pad_x(p["pad"], t)
        else: xs[p["n"]] = (p["x"], False, 0)
    gewoon = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(gewoon); koppen = {}; apart = []
    for p in figs:
        n = p["n"]; x, loopt, richt = xs[n]
        if x < -200 or x > W + 200: continue
        if "zichtbaar" in p and not (p["zichtbaar"][0] <= t < p["zichtbaar"][1]): continue
        loop = (t * 2.2 + hash(n) % 5) if loopt or p.get("rondje") else None
        if sp is not None and sp != n and sp in xs: kijk = 0.9 if xs[sp][0] > x else -0.9
        else: kijk = 0.5 if x < 960 else -0.5
        if loopt: kijk = 0.9 * richt
        if p.get("rondje"): kijk = 0.9 if math.cos(t * p["rondje"] + hash(n) % 3) > 0 else -0.9
        if "kijk" in p: kijk = p["kijk"]
        geb = p.get("geb")
        for t0, t1, g in p.get("gebt", []):
            if t0 <= t < t1: geb = g
        if sp == n and nu is not None:
            g2 = next((g for s_, g in ACTIE.items() if tekst_nu.startswith(s_)), None)
            if g2 and not (geb == "vast" and p.get("houd_vast")): geb = g2
        if loopt and geb not in ("vast", "telefoon"): geb = "rennen"
        emo = emotie(t, nu) if (sp == n or n in ("you", "dad", "mom", "sis")) and nu is not None and (sp == n or Z[nu][4] == "N") else None
        if p.get("emo"): emo = p["emo"]
        verb, boos = emo == "schrik", emo == "verdriet"
        knip = (t + hash(n) % 7 * 0.4) % 3.4 < 0.13
        S = p["s"] * ps.C[n].get("groot", 1.0)
        if p.get("val") is not None or p.get("groen") or p.get("clip"):
            L = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
            hx, hy = ps.poppetje(dl, n, x, p["y"], p["s"], t, loop=loop, kijk=kijk, mond=luid(t, n), knipper=knip, verbaasd=verb, gebaar=geb, boos=boos)
            apart.append((L, p, x)); koppen[n] = (hx, hy, S, x, p["y"], p["s"])
        else:
            hx, hy = ps.poppetje(d, n, x, p["y"], p["s"], t, loop=loop, kijk=kijk, mond=luid(t, n), knipper=knip, verbaasd=verb, gebaar=geb, boos=boos)
            koppen[n] = (hx, hy, S, x, p["y"], p["s"])
        GEB[n] = geb; GEZ[n] = (hx, hy + 60 * S, S)
    gewoon = gewoon.resize((W, H), Image.LANCZOS); img.paste(gewoon, (0, 0), gewoon)
    for L, p, x in apart:
        L = L.resize((W, H), Image.LANCZOS)
        if p.get("groen"):                                    # zombie: alles groenig
            a = L.getchannel("A"); r_, g_, b_ = L.convert("RGB").split()
            L = Image.merge("RGB", (r_.point(lambda v: int(v * 0.55)), g_.point(lambda v: min(255, int(v * 0.95 + 40))), b_.point(lambda v: int(v * 0.5)))).convert("RGBA"); L.putalpha(a)
        if p.get("val") is not None:
            hoek = p["val"](t)
            if hoek: L = L.rotate(-hoek, resample=Image.BICUBIC, center=(x, p["y"]))
            n = p["n"]
            if hoek > 30: GEZ.pop(n, None)                 # ligt: gezicht ligt niet meer op de plek van het hoofd
        if p.get("clip"):
            m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rectangle(p["clip"], fill=255)
            a = ImageChops.multiply(L.getchannel("A"), m); L.putalpha(a)
        img.paste(L, (0, 0), L)
    return koppen

# ---------- tekenwerk ----------
def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30)); SCHERM.append(s)
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = [w for w in SW if w[0] == i]
    if not ws: return
    f = font(FS, 56); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 6 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 985
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)
def gloed(img, cx, cy, r, kl=(255, 230, 90), sterk=0.55):
    L = Image.new("RGBA", (int(r * 2), int(r * 2)), (0, 0, 0, 0)); a = np.zeros((int(r * 2), int(r * 2)), np.float32)
    yy, xx = np.mgrid[0:int(r * 2), 0:int(r * 2)]; dd = np.sqrt((xx - r) ** 2 + (yy - r) ** 2) / r; a = np.clip(1 - dd, 0, 1) ** 2 * 255 * sterk
    L = Image.merge("RGBA", [Image.new("L", L.size, c) for c in kl] + [Image.fromarray(a.astype(np.uint8))]); img.paste(L, (int(cx - r), int(cy - r)), L)
def pijl(img, cx, cy, t, s=1.0, naam="pijl"):            # gele game-pijl die draait en dobbert
    cy += math.sin(t * 3) * 10 * s; f = abs(math.cos(t * 2.2)) * 0.85 + 0.15; w = 70 * s * f; h = 120 * s
    WACHT.plaats(naam, (cx - 70 * s, cy - h / 2, cx + 70 * s, cy + h / 2), op="beeld")
    gloed(img, cx, cy, 120 * s, sterk=0.45); d = ImageDraw.Draw(img)
    pts = [(cx - w * 0.45, cy - h / 2), (cx + w * 0.45, cy - h / 2), (cx + w * 0.45, cy), (cx + w, cy), (cx, cy + h / 2), (cx - w, cy), (cx - w * 0.45, cy)]
    d.polygon(pts, fill=(255, 214, 40), outline=INK); d.line(pts + [pts[0]], fill=INK, width=max(3, int(5 * s)))
    d.polygon([(cx - w * 0.45, cy - h / 2), (cx - w * 0.1, cy - h / 2), (cx - w * 0.1, cy), (cx - w * 0.45, cy)], fill=(255, 238, 130))
def sterren(img, cx, y, n, t, knipper=False, naam="ster"):
    if n <= 0 or (knipper and int(t * 6) % 2): return
    d = ImageDraw.Draw(img); r = 34; x0 = cx - (n - 1) * r * 1.1
    WACHT.plaats(naam, (x0 - r, y - r, x0 + (n - 1) * r * 2.2 + r, y + r), op="beeld")
    for k in range(n):
        x = x0 + k * r * 2.2
        pts = [(x + (r if j % 2 == 0 else r * 0.45) * math.sin(j * math.pi / 5), y - (r if j % 2 == 0 else r * 0.45) * math.cos(j * math.pi / 5)) for j in range(10)]
        d.polygon(pts, fill=(255, 255, 255), outline=INK); d.line(pts + [pts[0]], fill=INK, width=4)
def balkje(img, cx, y, tekst, frac, kl=(70, 210, 90), naam="health"):   # health bar boven het hoofd
    d = ImageDraw.Draw(img); f = font(FB, 38); tw = d.textlength(tekst, font=f); w = 240
    WACHT.plaats(naam, (cx - w / 2, y - 50, cx + w / 2, y + 30), op="beeld"); SCHERM.append(tekst)
    gloed(img, cx, y, 150, kl=(140, 255, 160), sterk=0.3); d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, y - 52), tekst, font=f, fill=(255, 255, 255), stroke_width=5, stroke_fill=INK)
    d.rounded_rectangle((cx - w / 2, y, cx + w / 2, y + 30), 10, fill=(40, 40, 50), outline=INK, width=4)
    d.rounded_rectangle((cx - w / 2 + 5, y + 5, cx - w / 2 + 5 + (w - 10) * frac, y + 25), 7, fill=kl)
def geldteller(img, cx, y, tekst, sch=1.0):
    f = font(FB, int(72 * sch)); d = ImageDraw.Draw(img); tw = d.textlength(tekst, font=f)
    WACHT.plaats("geldteller", (cx - tw / 2, y - 30, cx + tw / 2, y + 30), op="beeld"); SCHERM.append(tekst)
    gloed(img, cx, y, 110, kl=(120, 255, 150), sterk=0.35); d = ImageDraw.Draw(img)
    d.text((cx - tw / 2, y - 30 * sch), tekst, font=f, fill=(90, 235, 120), stroke_width=5, stroke_fill=INK)
def minimap(img, t):                                       # rond kaartje rechtsboven "in de lucht"
    cx, cy, r = 1790, 140, 100; WACHT.plaats("minimap", (cx - r, cy - r, cx + r, cy + r), op="beeld")
    L = Image.new("RGBA", (2 * r, 2 * r), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=(70, 120, 90, 225))
    for k in range(-3, 4):
        d.line((0, r + k * 45 + 10, 2 * r, r + k * 45 - 10), fill=(225, 225, 210, 235), width=9)
        d.line((r + k * 55, 0, r + k * 55 + 14, 2 * r), fill=(225, 225, 210, 235), width=7)
    d.rectangle((r + 30, r - 70, r + 75, r - 30), fill=(120, 170, 230, 230))
    m = Image.new("L", (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse((0, 0, 2 * r - 1, 2 * r - 1), fill=255); L.putalpha(ImageChops.multiply(L.getchannel("A"), m))
    img.paste(L, (cx - r, cy - r), L); d = ImageDraw.Draw(img)
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(20, 20, 25), width=7)
    a = t * 0.6; pts = [(cx + 22 * math.sin(a), cy - 22 * math.cos(a)), (cx + 14 * math.sin(a + 2.4), cy - 14 * math.cos(a + 2.4)), (cx, cy), (cx + 14 * math.sin(a - 2.4), cy - 14 * math.cos(a - 2.4))]
    d.polygon(pts, fill=(255, 255, 255), outline=INK)
def ballon(img, x, y, tekst, sch=1.0, naam="ballon"):
    d = ImageDraw.Draw(img); f = font(FB, int(42 * sch)); w = d.textlength(tekst, font=f)
    WACHT.plaats(naam, (x - w / 2 - 26, y - 44 * sch, x + w / 2 + 26, y + 34 * sch), op="beeld"); SCHERM.append(tekst)
    d.rounded_rectangle((x - w / 2 - 26, y - 44 * sch, x + w / 2 + 26, y + 34 * sch), 26, fill=(255, 255, 255), outline=INK, width=5)
    d.polygon([(x - 30, y + 30 * sch), (x - 70, y + 80 * sch), (x + 5, y + 32 * sch)], fill=(255, 255, 255), outline=INK)
    d.text((x - w / 2, y - 30 * sch), tekst, font=f, fill=INK)
def cirkel(img, cx, cy, t):                                # gele missiecirkel op de vloer
    gloed(img, cx, cy - 30, 190, sterk=0.5); d = ImageDraw.Draw(img); p = 1 + 0.06 * math.sin(t * 5)
    WACHT.plaats("cirkel", (cx - 150, cy - 40, cx + 150, cy + 40), op="vloer")
    d.ellipse((cx - 150 * p, cy - 40 * p, cx + 150 * p, cy + 40 * p), fill=(255, 220, 60), outline=(200, 150, 20), width=6)
    d.ellipse((cx - 110 * p, cy - 26 * p, cx + 110 * p, cy + 26 * p), fill=(255, 240, 140))
def timer(img, cx, cy, sec, rood=False, sch=1.0, naam="timer"):
    s = f"{int(sec) // 60}:{int(sec) % 60:02d}"; f = font(FB, int(120 * sch)); d = ImageDraw.Draw(img); tw = d.textlength(s, font=f)
    WACHT.plaats(naam, (cx - tw / 2 - 30, cy - 80 * sch, cx + tw / 2 + 30, cy + 80 * sch), op="beeld"); SCHERM.append(s)
    d.rounded_rectangle((cx - tw / 2 - 30, cy - 80 * sch, cx + tw / 2 + 30, cy + 80 * sch), 30, fill=(30, 30, 40), outline=(255, 255, 255), width=6)
    d.text((cx - tw / 2, cy - 72 * sch), s, font=f, fill=(240, 70, 60) if rood else (255, 214, 64))
def kaart(img, t, t0):                                     # RESPAWN CARD (spaarkaart)
    if t < t0: return
    sch = ps.pop((t - t0) / 0.35); w, h = 640 * sch, 300 * sch; cx, cy = 1400, 400; d = ImageDraw.Draw(img)
    WACHT.plaats("spaarkaart", (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), op="beeld"); SCHERM.append("RESPAWN CARD")
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), int(30 * sch), fill=(250, 250, 255), outline=INK, width=6)
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 80 * sch), int(30 * sch), fill=(220, 60, 70))
    f = font(FB, int(48 * sch)); tw = d.textlength("RESPAWN CARD", font=f); d.text((cx - tw / 2, cy - h / 2 + 12 * sch), "RESPAWN CARD", font=f, fill=(255, 255, 255))
    for k in range(11):
        x = cx - w / 2 + 50 * sch + (k % 6) * 108 * sch; y = cy - 20 * sch + (k // 6) * 90 * sch
        vol = k < 3
        if k == 10: d.text((x - 32 * sch, y - 20 * sch), "FREE", font=font(FB, int(32 * sch)), fill=(30, 160, 80)); continue
        d.ellipse((x - 30 * sch, y - 30 * sch, x + 30 * sch, y + 30 * sch), fill=(220, 60, 70) if vol else (235, 235, 240), outline=INK, width=3)
def tv(img, box, aan, t, regels=(), naam="tv"):
    x0, y0, x1, y1 = box; d = ImageDraw.Draw(img)
    d.rounded_rectangle((x0, y0, x1, y1), 14, fill=(25, 25, 30), outline=INK, width=6)
    sx0, sy0, sx1, sy1 = x0 + 14, y0 + 14, x1 - 14, y1 - 14
    d.rectangle((sx0, sy0, sx1, sy1), fill=(20, 30, 50) if aan else (45, 50, 58))
    if aan:
        yy = sy0 + 10
        for s, kl, m in regels:
            f = font(FB, m); tw = d.textlength(s, font=f)
            while tw > sx1 - sx0 - 16 and m > 10: m -= 2; f = font(FB, m); tw = d.textlength(s, font=f)
            d.text(((sx0 + sx1) / 2 - tw / 2, yy), s, font=f, fill=kl); yy += m + 10
            if s.startswith("UPDATE"):
                frac = min(1, (t % 6) / 4); d.rectangle((sx0 + 16, yy, sx1 - 16, yy + 16), outline=(255, 255, 255), width=2)
                d.rectangle((sx0 + 18, yy + 2, sx0 + 18 + (sx1 - sx0 - 36) * frac, yy + 14), fill=(90, 220, 110)); yy += 28
def floppy(img, cx, cy, t):
    cy += math.sin(t * 2.5) * 10; gloed(img, cx, cy, 190, kl=(120, 200, 255), sterk=0.6); d = ImageDraw.Draw(img); s = 130
    WACHT.plaats("floppy", (cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), op="beeld")
    d.rounded_rectangle((cx - s / 2, cy - s / 2, cx + s / 2, cy + s / 2), 8, fill=(50, 90, 200), outline=INK, width=4)
    d.rectangle((cx - s * 0.28, cy - s / 2, cx + s * 0.28, cy - s * 0.12), fill=(200, 205, 215), outline=INK, width=3)
    d.rectangle((cx + s * 0.08, cy - s * 0.44, cx + s * 0.2, cy - s * 0.18), fill=(50, 90, 200))
    d.rectangle((cx - s * 0.34, cy + s * 0.06, cx + s * 0.34, cy + s * 0.46), fill=(250, 250, 250), outline=INK, width=3)
def notitieblok(img, hx, hy, eig):
    WACHT.plaats("notitieblok", (hx - 26, hy - 60, hx + 26, hy + 6), op="hand:" + eig, punt=(hx, hy), voor=True)
    d = ImageDraw.Draw(img); d.rectangle((hx - 26, hy - 60, hx + 26, hy + 6), fill=(255, 250, 220), outline=INK, width=3)
    for k in range(4): d.line((hx - 18, hy - 46 + k * 12, hx + 18, hy - 46 + k * 12), fill=(150, 150, 170), width=2)
    d.line((hx + 22, hy - 70, hx + 40, hy - 10), fill=(30, 60, 160), width=6)
def stopwatch(img, hx, hy, eig, sec):
    WACHT.plaats("timer", (hx - 34, hy - 70, hx + 34, hy + 4), op="hand:" + eig, punt=(hx, hy), voor=True)
    d = ImageDraw.Draw(img); d.rectangle((hx - 6, hy - 76, hx + 6, hy - 64), fill=(120, 120, 130), outline=INK)
    d.ellipse((hx - 34, hy - 66, hx + 34, hy + 2), fill=(250, 250, 250), outline=INK, width=4)
    a = sec / 60 * 2 * math.pi; d.line((hx, hy - 32, hx + 24 * math.sin(a), hy - 32 - 24 * math.cos(a)), fill=(220, 50, 50), width=4)
def toets(img, x0, y0, klaar):                             # wiskundetoets op het schoolbureau
    WACHT.plaats("toets", (x0, y0 - 6, x0 + 150, y0), op="schoolbureau", voor=True)
    d = ImageDraw.Draw(img); d.polygon([(x0, y0), (x0 + 150, y0), (x0 + 130, y0 - 16), (x0 + 18, y0 - 16)], fill=(255, 255, 255), outline=INK)
    if klaar: d.text((x0 + 52, y0 - 17), "100", font=font(FB, 16), fill=(220, 40, 40))
def tafel(img, x0, x1):                                    # schoolbureau vóór je: zo lijkt het of je zit
    d = ImageDraw.Draw(img)
    d.rectangle((x0, 818, x1, 846), fill=(200, 150, 95), outline=(60, 45, 35), width=4)
    for x in (x0 + 30, x1 - 44): d.rectangle((x, 846, x + 14, 990), fill=(120, 120, 130), outline=(50, 50, 60), width=2)
    d.rectangle((x0 + 15, 846, x1 - 15, 1000), fill=(185, 135, 85), outline=(60, 45, 35), width=3)
    WACHT.vlak("schoolbureau", [x0, x1, 812, 846], staat_op="vloer", voet=(x0, x1, 1000))
def keukentafel(img, x0, x1):
    d = ImageDraw.Draw(img); d.rectangle((x0, 820, x1, 850), fill=(190, 140, 90), outline=INK, width=5)
    d.rectangle((x0 + 20, 850, x1 - 20, 1010), fill=(170, 120, 75), outline=INK, width=4)
    for x in range(x0 + 40, x1 - 40, 160): d.line((x, 860, x, 1000), fill=(150, 104, 64), width=3)
    WACHT.vlak("keukentafel", [x0, x1, 815, 850], staat_op="vloer", voet=(x0, x1, 1010))
def kom(img, cx, y):                                       # kom cornflakes op tafel
    WACHT.plaats("kom", (cx - 60, y - 50, cx + 60, y), op="keukentafel", voor=True)
    d = ImageDraw.Draw(img); d.chord((cx - 60, y - 70, cx + 60, y + 10), 0, 180, fill=(250, 250, 255), outline=INK, width=4)
    for k in range(7): d.ellipse((cx - 45 + k * 13, y - 36 - (k % 2) * 6, cx - 33 + k * 13, y - 26 - (k % 2) * 6), fill=(235, 180, 70), outline=(150, 100, 40))
def druppels(img, cx, top, bot, t):                       # nat: druppels lopen eraf
    d = ImageDraw.Draw(img)
    for k in range(9):
        x = cx - 70 + (k * 37) % 140; y = top + ((t * 260 + k * 53) % (bot - top))
        d.ellipse((x - 6, y - 10, x + 6, y + 6), fill=(110, 180, 245), outline=(50, 100, 170), width=2)
def plons(img, cx, cy, f):
    d = ImageDraw.Draw(img)
    for k in range(14):
        a = math.pi * (0.1 + 0.8 * k / 13); r = 40 + 160 * f
        x, y = cx + math.cos(a) * r, cy - math.sin(a) * r * 1.3 + 140 * f * f
        d.ellipse((x - 12, y - 12, x + 12, y + 12), fill=(200, 235, 255), outline=(70, 140, 210), width=3)
def water(img, hx, hy, t):                                 # tuinslang-straal van de hand naar het gras
    d = ImageDraw.Draw(img)
    for k in range(16):
        f = ((k / 16) + t * 1.4) % 1; x = hx + f * 230; y = hy - 170 * math.sin(math.pi * f) + 60 * f
        d.ellipse((x - 7, y - 7, x + 7, y + 7), fill=(130, 200, 250), outline=(60, 120, 200), width=2)
def biljetjes(img, hx, hy, eig):
    WACHT.plaats("geld", (hx - 40, hy - 50, hx + 40, hy + 4), op="hand:" + eig, punt=(hx, hy), voor=True)
    d = ImageDraw.Draw(img)
    for k in range(3): d.rectangle((hx - 40 + k * 6, hy - 46 + k * 6, hx + 30 + k * 6, hy - 10 + k * 6), fill=(120, 200, 120), outline=(40, 100, 50), width=3)
def grijs(img, f):
    if f <= 0: return img
    return ImageEnhance.Brightness(ImageEnhance.Color(img).enhance(1 - 0.92 * min(1, f))).enhance(1 - 0.18 * min(1, f))
def sirene(img, cx, top, t):
    d = ImageDraw.Draw(img); aan = int(t * 6) % 2
    gloed(img, cx - 25, top + 8, 60, kl=(255, 60, 60) if aan else (60, 120, 255), sterk=0.7)
def held(img, item, h, n, k, t, hoek=70, naam=None):      # voorwerp in de rechterhand (alleen als die hand echt vasthoudt)
    if GEB.get(n) != "vast": return None, None
    hx, hy, S = rhand(n, k[3], k[4], k[5], hoek)
    zet(img, item, h, hx, hy + h * 0.35, op="hand:" + n, punt=(hx, hy), voor=True, naam=naam)
    return hx, hy

# ---------- per blok: figuren en momenten ----------
def V(t0, dur, a, b, extra=None):                          # val-hoek: 0 -> b graden in dur seconden vanaf t0
    return lambda t: 0 if t < t0 else min(1, (t - t0) / dur) * b
for B in BLOK:
    k, a = B["key"], B["a"]; B["figs"], B["kop"] = [], []
    dag = DAG.get(k)
    if dag is not None and Z[a][2].startswith("Day"): B["kop"].append((Z[a][0], f"DAY {dag}", 185, 90, 70, "geel"))
    elif dag is not None: B["kop"].append((-1, f"DAY {dag}", 185, 90, 70, "geel"))
    if k == "open":
        B["figs"] = [F("you", 1250, geb="wijslinks", s=1.7)]
        B["kop"].append((kw(1, "7"), "7:00 AM", 960, 170, 80, "wit"))
        B["health"] = kw(2, "above", -0.1)
    elif k == "keuken1":
        B["figs"] = [F("you", 480, pad=[(Z[a][0], -150), (Z[a][0] + 1.1, 480)]), F("dad", 820, geb="vast", houd_vast=True),
                     F("mom", 1120, geb="telefoon", houd_vast=True), F("sis", 1400)]
        B["geld"] = kw(4, "money", -0.1); B["tafel"] = (650, 1620)
        B["kop"].append((kw(6, "video"), "THE WHOLE WORLD = A VIDEO GAME", 960, 160, 70, "wit"))
        B["kop"].append((kw(9, "Day"), "DAY 1: FUN", 960, 160, 76, "groen")); B["kop"].append((kw(9, "two"), "DAY 2: WEIRD", 960, 250, 76, "geel"))
        B["kop"].append((kw(9, "thirty"), "DAY 30: ...", 960, 340, 76, "rood"))
    elif k == "dag1":
        tg = kw(15, "drops"); tp = kw(19, "picks")
        B["figs"] = [F("buur", 330, geb="vast", houd_vast=True), F("you", 1080, gebt=[(kw(12, "hi", -0.2), kw(12, "hi", 1.2), "zwaai")]),
                     F("dad", 1300, pad=[(Z[21][0], 1300), (Z[21][0] + 1.6, 900)], gebt=[(tg - 0.3, tg + 0.3, ("hoek", -16, 20)), (tp - 0.2, tp + 0.8, ("hoek", -16, 10))]),
                     F("mom", 1580)]
        B["kauw"] = (tg, tp + 0.5)
        B["ster"] = [(kw(15, "Ding"), 1), (kw(17, "Two"), 2), (kw(19, "blink"), -2), (kw(19, "disappear"), 0)]
        B["politie"] = (kw(17, "police", -0.3), kw(19, "drives", -0.1))
        B["auto"] = Z[21][0]; B["radio"] = (kw(21, "radio", -0.1), Z[24][1] + 0.3)
        B["kop"].append((kw(14, "four"), "x400", 560, 330, 110, "geel", Z[15][0]))
        B["kop"].append((kw(24, "every"), "EVERY CAR. SAME RADIO. FOREVER.", 960, 170, 64, "wit"))
    elif k == "winkel":
        ts = kw(26, "steps")
        B["figs"] = [F("mom", 520, pad=[(ts - 0.2, 520), (ts + 1.0, 960)], gebt=[(ts + 1.2, 99999, "vast")], houd_vast=True),
                     F("kassa", 1560, gebt=[(Z[29][0], Z[29][1] + 0.3, "vast")])]
        B["cirkel"] = (kw(25, "glowing", -0.2), ts + 2.4); B["melk"] = ts + 1.2
        B["kop"] += [(kw(26, "mission"), "MISSION COMPLETE", 960, 170, 110, "goud"), (kw(28, "fifty"), "+50 RESPECT", 960, 300, 80, "groen"),
                     (kw(28, "mayor"), "MOM > THE MAYOR", 960, 300, 80, "groen")]
    elif k == "val":
        tt = kw(31, "trip")
        B["figs"] = [F("you", 900, pad=[(Z[a][0], 380), (tt, 900)], val=V(tt + 0.1, 0.45, 0, 80))]
        B["slang"] = True; B["grijs"] = kw(31, "gray", -0.2)
    elif k in ("zh1", "zh2"):
        wie = "you" if k == "zh1" else "dad"
        B["figs"] = [F(wie, 760), F("zuster", 1000, s=1.45, y=830)]
        B["kop"].append((kw(a, "Minus"), "-$100", 540, 300, 110, "rood"))
        if k == "zh1":
            B["kop"] += [(kw(35, "next"), "RESPAWN #2", 960, 170, 70, "wit"), (kw(35, "after"), "RESPAWN #3", 960, 170, 70, "wit")]
            B["kaart"] = kw(36, "loyalty", -0.1)
        else: B["nat"] = True
    elif k == "garage":
        tin, tdicht, topen = kw(38, "drives"), kw(38, "closes"), kw(39, "opens")
        B["car"] = dict(pad=[(Z[a][0], 380), (tin - 0.6, 560), (tin + 0.9, 985), (topen + 0.3, 985), (topen + 1.6, 1050)],
                        tint=[(topen, 0.78), (kw(42, "orange"), 0.07), (kw(42, "green"), 0.33), (kw(42, "gold"), 0.13)],
                        dicht=(tin + 0.9, topen), ster=(Z[a][0], tdicht))
        B["politie"] = (Z[a][0], kw(39, "police", -0.2))
        B["figs"] = [F("dad", 1460, zichtbaar=(Z[40][0] - 0.4, 99999)), F("mom", 1690, zichtbaar=(Z[41][0] - 0.6, 99999))]
        B["kop"].append((kw(37, "three"), "+3 MPH", 960, 170, 90, "rood"))
    elif k in ("cheat", "cheat2"):
        B["figs"] = [F("you", 640, emo="blij" if k == "cheat2" else None), F("sis", 1000, geb="vast", houd_vast=True), F("mom", 1420)]
        if k == "cheat":
            i0 = zi("Left, left")
            B["kop"] += [(kw(i0, "Left"), "LEFT", 960, 170, 70, "wit"), (kw(i0, "left", 0.35), "LEFT LEFT", 960, 170, 70, "wit"),
                         (kw(i0, "right"), "LEFT LEFT RIGHT", 960, 170, 70, "wit"), (kw(i0, "jump"), "LEFT LEFT RIGHT JUMP SPIN", 960, 170, 70, "wit"),
                         (kw(45, "presses"), "CHEAT ACTIVATED", 960, 170, 90, "goud")]
            B["eendjes"] = kw(45, "raining", -0.2)
        else:
            B["eendjes"] = -99; B["afpak"] = kw(50, "remote", -0.2)
            for p in B["figs"]:
                if p["n"] == "mom": p["gebt"] = [(B["afpak"], 99999, "vast")]; p["houd_vast"] = True
                if p["n"] == "sis": p["gebt"] = [(B["afpak"], 99999, None)]
    elif k == "eenden":
        B["figs"] = [F("buur", 330, emo="blij"), F("you", 1000), F("dad", 1300)]; B["regen"] = Z[a][0] - 0.1
    elif k == "kantoor1":
        B["figs"] = [F("collega", 420, rondje=1.6), F("collega2", 1560, rondje=1.3), F("dad", 760, pad=[(kw(55, "Go", 0.6), 760), (kw(55, "Go", 1.6), -200)], gebt=[(kw(55, "Go", 0.2), 99999, "vast")], houd_vast=True),
                     F("boss", 1150, geb="vast", houd_vast=True, gebt=[(kw(55, "Go", 0.2), 99999, None)])]
        B["pijl_boss"] = kw(52, "arrow", -0.1); B["pizza_naar_dad"] = kw(55, "Go", 0.2)
        B["kop"].append((kw(53, "ninety"), "DELIVER THE PIZZA: 1:30", 960, 170, 76, "wit"))
    elif k == "timer":
        ttr = kw(56, "trips")
        B["figs"] = [F("dad", 1100, pad=[(Z[a][0], -150), (ttr, 1100)], geb="vast", val=V(ttr, 0.4, 0, 75))]
        B["klok"] = (kw(56, "timer", -0.1), kw(56, "Eighty"), kw(56, "zero")); B["vlieg"] = kw(56, "trips", 0.1)
    elif k == "kantoor2":
        B["figs"] = [F("dad", 860, geb="vast", houd_vast=True, gebt=[(Z[a][0], Z[59][0] - 0.2, None)]), F("boss", 1260)]
        B["kop"] += [(kw(57, "mission"), "MISSION FAILED", 960, 170, 110, "rood"), (kw(58, "seventeen"), "TRY 17", 960, 170, 110, "wit"),
                     (kw(58, "eighteenth"), "TRY 18", 960, 170, 110, "wit"), (kw(58, "one"), "0:01 LEFT · MISSION COMPLETE", 960, 170, 80, "goud")]
        B["pizza_dad"] = Z[59][0] - 0.2
    elif k == "klas":
        B["figs"] = [F("teach", 1400), F("you", 700, y=1010)]
        B["pijl_teach"] = kw(60, "arrow", -0.1); B["toets"] = kw(61, "math", -0.1); B["honderd"] = kw(65, "hundred", -0.1)
        B["kop"] += [(kw(61, "Side"), "SIDE MISSION: MATH TEST", 960, 170, 76, "geel"), (kw(61, "two"), "REWARD: +200 RESPECT", 960, 270, 64, "groen"),
                     (kw(64, "Mission"), "MISSION FAILED", 960, 170, 100, "rood"), (kw(64, "eleven"), "TRY 11", 960, 270, 90, "wit"),
                     (kw(65, "hundred"), "100%", 960, 170, 130, "groen"), (kw(65, "Plus"), "+200 RESPECT", 960, 270, 80, "groen")]
    elif k == "feit":
        B["figs"] = [F("you", 700), F("dad", 1250, geb="telefoon", houd_vast=True)]
        B["kop"] += [(kw(68, "2013"), "GTA V · 2013", 960, 150, 84, "geel"), (kw(68, "billion"), "$1,000,000,000", 960, 265, 110, "groen"),
                     (kw(68, "three"), "IN 3 DAYS", 960, 380, 84, "wit")]
        B["bron"] = kw(68, "2013")
    elif k == "strand":
        tj = kw(76, "rents", -0.1)
        B["figs"] = [F("jogger", 0, s=1.15, y=870, rondje=0), F("jogger2", 0, s=1.15, y=870, rondje=0), F("jogger3", 0, s=1.15, y=870, rondje=0),
                     F("dad", 1200, s=1.4, y=1040, zichtbaar=(-1, tj)), F("mom", 1380, s=1.4, y=1040), F("sis", 1560, s=1.4, y=1040), F("you", 1740, s=1.4, y=1040)]
        B["jet"] = (tj, kw(76, "crashes", -0.1)); B["grijs"] = kw(76, "gray", -0.2)
        B["kop"].append((kw(74, "six"), "6 HOURS", 420, 330, 90, "geel"))
    elif k == "teddy":
        B["figs"] = [F("sis", 1200, pad=[(kw(81, "garden"), 1200), (kw(81, "roof"), 900), (kw(81, "shed"), 560), (kw(81, "Gary's", 0.4), 640)]),
                     F("buur", 1620, pad=[(Z[82][0] - 1.2, 2200), (Z[82][0] - 0.1, 1620)], emo="blij")]
        B["teddy"] = True
        B["kop"] += [(kw(79, "hidden"), "HIDDEN TEDDY: 1/100", 960, 170, 84, "geel"), (kw(81, "garden"), "GARDEN", 960, 290, 70, "wit"),
                     (kw(81, "roof"), "ROOF", 960, 290, 70, "wit"), (kw(81, "shed"), "SHED", 960, 290, 70, "wit"), (kw(81, "dog"), "GARY'S DOG HOUSE", 960, 290, 70, "wit")]
    elif k == "rest":
        tw_ = kw(85, "Waiters", -0.3)
        B["figs"] = [F("mom", 720), F("dad", 1000),
                     F("ober", 1290, pad=[(tw_, 2150), (tw_ + 1.4, 1290)], geb="vast", houd_vast=True, gebt=[(Z[88][0], Z[88][1], "nee")]),
                     F("ober2", 1500, pad=[(tw_ + 0.2, 2150), (tw_ + 1.6, 1500)], geb="vast", houd_vast=True),
                     F("ober3", 1710, pad=[(tw_ + 0.4, 2150), (tw_ + 1.8, 1710)], geb="vast", houd_vast=True)]
        B["kop"] += [(kw(84, "free"), "FREE FOOD", 960, 170, 100, "groen"), (kw(88, "respect"), "RESPECT: TOO LOW", 960, 170, 90, "rood")]
    elif k == "fiets":
        B["figs"] = [F("dad", 900, geb="vast", houd_vast=True, gebt=[(Z[92][0], 99999, None)])]
        B["kop"] += [(kw(91, "Three"), "$312", 960, 130, 100, "groen"), (kw(91, "four"), "-4 HOSPITAL VISITS", 960, 225, 64, "rood"),
                     (kw(91, "seven"), "-7 PAINT JOBS", 960, 300, 64, "rood"), (kw(91, "eleven"), "$11 LEFT", 960, 130, 100, "groen")]
        B["fiets"] = kw(93, "bicycle", -0.1); B["ster"] = [(kw(95, "Ding"), 1)]; B["biljet"] = (Z[a][0], Z[92][0])
    elif k == "chaos":
        B["figs"] = [F("you", 820), F("dad", 1120)]; B["chaos"] = True
        B["kop"].append((kw(97, "more"), "MORE POLICE THAN CARS", 960, 170, 84, "rood"))
    elif k == "save1":
        B["figs"] = [F("you", 640), F("mom", 960, gebt=[(Z[a][0], Z[101][1], "denk")]), F("sis", 1280), F("dad", 1540)]
        B["kop"] += [(kw(101, "save"), "SAVE BUTTON?", 960, 170, 90, "geel"), (kw(102, "couch"), "COUCH: NOTHING", 960, 170, 70, "wit"),
                     (kw(102, "fridge"), "FRIDGE: NOTHING", 960, 260, 70, "wit"), (kw(102, "car"), "DAD'S CAR: ...", 960, 350, 70, "wit")]
    elif k == "radio2":
        B["figs"] = [F("dad", 1380)]; B["auto"] = -99; B["radio"] = (Z[a][0] - 0.1, Z[a][1] + 0.3); B["goud"] = True
    elif k == "save2":
        B["figs"] = [F("you", 700), F("sis", 430)]; B["floppy"] = kw(105, "floppy", -0.4)
        B["kop"].append((kw(106, "saves"), "GAME SAVED", 960, 170, 100, "goud"))
    elif k == "team":
        B["figs"] = [F("buur", 330, geb="vast", houd_vast=True), F("sis", 720, geb="vast", houd_vast=True), F("mom", 1050, geb="wijs"),
                     F("dad", 1380), F("you", 1650)]
        B["kop"] += [(kw(111, "twelve"), "0:12", 960, 170, 110, "goud"), (kw(111, "Mission"), "MISSION COMPLETE", 960, 170, 110, "goud"),
                     (kw(111, "Plus"), "+1000 RESPECT · EVERYONE", 960, 290, 70, "groen")]
        B["stilauto"] = True
    elif k == "wakker":
        B["figs"] = [F("you", 1000)]
        B["weg"] = dict(pijl=kw(114, "arrow", 0.5), health=kw(114, "health", 0.6), map=kw(114, "map", 0.5))
    elif k == "eind":
        B["figs"] = [F("you", 480, pad=[(Z[a][0], -150), (Z[a][0] + 1.1, 480)]), F("dad", 820, geb="vast", houd_vast=True, gebt=[(Z[122][0] - 0.1, 99999, "hoofdhanden")]), F("mom", 1120), F("sis", 1400),
                     F("buur", 890, s=1.0, y=640, groen=True, clip=(700, 195, 1080, 430), zichtbaar=(kw(120, "Gary", -0.2), 99999), kijk=0.0)]
        B["tafel"] = (650, 1620); B["tvaan"] = kw(118, "TV", -0.1); B["zombie"] = kw(118, "zombie", -0.1)
        B["kop"].append((kw(118, "zombie"), "UPDATE: ZOMBIE MODE", 960, 150, 84, "rood"))

# tekstwachter: wat genoemd wordt, moet in beeld zijn
ZIE = {"yellow arrow": ["pijl", "pijl-boss", "pijl-juf"], "health": ["health"], "coffee": ["koffiemok"], "money counter floating": ["geldteller"],
       "three hundred and twelve dollars": ["geldteller", "tekst:$312"], "cereal": ["kom"], "gary is watering": ["buur", "tuinslang"],
       "gum wrapper": ["kauwgompapiertje"], "white star": ["ster"], "two stars": ["ster"], "one star": ["ster"], "police car": ["politieauto"],
       "radio turns on": ["radio"], "milk": ["melk"], "glowing yellow circle": ["cirkel"], "mission complete": ["tekst:MISSION COMPLETE", "tekst:0:01 LEFT · MISSION COMPLETE"],
       "fifty respect": ["tekst:+50 RESPECT"], "autograph": ["notitieblok"], "garden hose": ["tuinslang"], "minus one hundred": ["tekst:-$100"],
       "you now have a loyalty card": ["spaarkaart"], "purple car": ["auto"], "remote": ["afstandsbediening"], "rubber ducks": ["badeend"],
       "this pizza": ["pizzadoos"], "pizza flies": ["pizzadoos"], "proud of a pizza": ["pizzadoos"], "carries the pizzas": ["pizzadoos"],
       "giant timer": ["timer"], "holds the timer": ["timer"], "mission failed": ["tekst:MISSION FAILED"], "math test": ["toets"],
       "one billion dollars": ["tekst:$1,000,000,000"], "on his phone": ["telefoon"], "jet ski": ["jetski"], "glowing teddy": ["teddy"],
       "dog house": ["hondenhok"], "bring her bread": ["broodmand"], "bicycle": ["fiets"], "more police cars": ["politieauto"],
       "floppy disk": ["floppy"], "tv turns on": ["tv"], "zombie mode": ["tekst:UPDATE: ZOMBIE MODE"], "very green": ["buur"],
       "six hours": ["tekst:6 HOURS"], "eleven dollars": ["tekst:$11 LEFT"]}
TW = Tekstwachter(Z, ZIE, lijf=LIJF)

def joggers_x(n, t):
    o = {"jogger": 0.0, "jogger2": 0.7, "jogger3": 1.4}[n]; u = ((t / 7 + o / 7) % 1); f = 1 - abs(2 * u - 1)
    return 150 + f * 500, (1 if u < 0.5 else -1)
POLITIE_X = (2300, 1500)

# ---------- frame ----------
GELUIDEN = []; ZOOM_AAN = True; TEKST_AAN = True
def frame(t):
    B = next(b for b in reversed(BLOK) if b["t"] <= t); k = B["key"]; nu = nu_i(t)
    img = bg(B["bg"]).copy(); WACHT.begin(B["bg"], t); GEZ.clear(); GEB.clear(); SCHERM.clear(); d = ImageDraw.Draw(img)
    figs = [dict(p) for p in B["figs"]]
    # --- achter de poppetjes ---
    if k == "open": pijl(img, 527, 215, t, 1.25)
    if k in ("dag1", "radio2") and B.get("auto") is not None and t >= B["auto"]:
        zet(img, "gezinsauto", 210, 620, 905, op="weg", naam="auto", tint=0.13 if B.get("goud") else None)
    if k == "dag1":
        zet(img, "tuinslang", 70, 470, 990, op="weg")
        p0, p1 = B["politie"]
        if p0 <= t < p1 + 2.2:
            x = POLITIE_X[0] + (POLITIE_X[1] - POLITIE_X[0]) * ps.ease((t - p0) / 1.4) if t < p1 else POLITIE_X[1] - (POLITIE_X[1] + 500) * ((t - p1) / 2.2)
            zet(img, "politieauto", 190, x, 900, op="weg", spiegel=t >= p1); sirene(img, x, 900 - 190, t)
    if k == "garage":
        c = B["car"]; x, loopt, _ = pad_x(c["pad"], t); tint = None
        for tt_, tn in c["tint"]:
            if t >= tt_: tint = tn
        dicht = c["dicht"][0] <= t < c["dicht"][1]
        if not dicht: zet(img, "gezinsauto", 230, x, 1000, op="weg", naam="auto", tint=tint)
        if c["ster"][0] <= t < c["ster"][1] and not dicht: sterren(img, x, 700, 2, t)
        p0, p1 = B["politie"]
        if t < p1: px = x - 520 if not dicht else 600; zet(img, "politieauto", 200, px, 1010, op="weg"); sirene(img, px, 810, t)
        elif t < p1 + 2.5: px = -400 + (2400) * ((t - p1) / 2.5); zet(img, "politieauto", 200, px, 1040, op="weg"); sirene(img, px, 840, t)
    if k == "winkel":
        c0, c1 = B["cirkel"]
        if c0 <= t < c1: cirkel(img, 960, 950, t)
        if t < B["melk"]: zet(img, "melk", 110, 960, 720, op="plank-4")
    if k == "val": zet(img, "tuinslang", 80, 950, 985, op="gras")
    if k == "teddy":
        zet(img, "hondenhok", 230, 430, 905, op="gras")
        gloed(img, 1700, 540, 150, sterk=0.6); zet(img, "teddy", 125, 1700, 600, op="gras")
    if k == "strand":
        for n_ in ("jogger", "jogger2", "jogger3"):
            jx, rr = joggers_x(n_, t)
            for p in figs:
                if p["n"] == n_: p["x"] = jx; p["kijk"] = 0.9 * rr; p["rondje"] = 0.0001
        tj, tc = B["jet"]
        if t >= tj:
            f = min(1, (t - tj) / max(0.1, tc - tj)); jx = 760 + (1185 - 760) * f if t < tc else 1185
            zet(img, "jetski", 105, jx, 705, op="zee")
            figs = [p for p in figs if p["n"] != "dad"]
            if t < tc + 0.3: figs.append(F("dad", jx - 10, s=0.62, y=668))
            if tc <= t < tc + 1.0: plons(img, 1200, 690, (t - tc) / 1.0)
    if k == "chaos":
        for j, (y_, v_, o_) in enumerate(((840, 520, 0), (885, -640, 900), (1060, 700, 300))):
            x = (o_ + v_ * t) % 2600 - 300
            if j == 2: continue
            zet(img, "politieauto", 150 + j * 25, x, y_, op="weg", spiegel=v_ < 0); sirene(img, x, y_ - 150 - j * 25, t + j)
        zet(img, "politieauto", 190, 1650, 905, op="weg"); sirene(img, 1650, 715, t)
    if k == "team" and B.get("stilauto"): zet(img, "politieauto", 190, 1760, 880, op="weg")
    if k == "cheat" or k == "cheat2":
        if t >= B["eendjes"]:
            for j in range(6):
                y = 140 + ((t * 300 + j * 77) % 380); x = 1560 + (j * 41) % 180
                WACHT.plaats("badeend", (x - 20, y - 20, x + 20, y + 20), op="aan:regen"); img.paste(sprite("badeend", 38), (int(x - 20), int(y - 19)), sprite("badeend", 38))
            ImageDraw.Draw(img).rectangle((1530, 110, 1760, 125), fill=(196, 160, 120))
    if k == "eenden":
        r0 = B["regen"]; n_op = int(min(40, (t - r0) * 10))
        for j in range(n_op):
            x = 80 + (j * 211) % 1780; y = 790 + (j * 97) % 250
            zet(img, "badeend", 46, x, y, op="weg", spiegel=j % 2 == 1)
        for j in range(18):
            x = (j * 113 + 40) % 1900; y = -40 + ((t * 420 + j * 61) % 900)
            WACHT.plaats("badeend", (x - 24, y - 24, x + 24, y + 24), op="aan:regen"); s_ = sprite("badeend", 46, spiegel=j % 2 == 1); img.paste(s_, (int(x - 23), int(y - 23)), s_)
    if k in ("keuken1", "eind"):
        tvaan = B.get("tvaan", 1e9); WACHT.plaats("tv", (230, 470, 450, 600), op="aanrecht-links")
        regels = [("UPDATE DOWNLOADING...", (255, 255, 255), 24)] + ([("ZOMBIE MODE", (90, 230, 100), 34)] if t >= B.get("zombie", 1e9) else [])
        tv(img, (230, 470, 450, 600), t >= tvaan, t, regels)
    if k == "kantoor1" or k == "kantoor2": pass
    # --- poppetjes ---
    if B.get("tafel"):
        koppen = teken_figuren(img, [p for p in figs if p["n"] == "you" or p.get("clip")], t, nu)
        keukentafel(img, *B["tafel"]); koppen.update(teken_figuren(img, [p for p in figs if not (p["n"] == "you" or p.get("clip"))], t, nu))
        kom(img, 1400, 826)
    elif k == "klas":
        koppen = teken_figuren(img, figs, t, nu); tafel(img, 540, 880)
        if t >= B["toets"]: toets(img, 640, 818, t >= B["honderd"])
    else: koppen = teken_figuren(img, figs, t, nu)
    # --- vóór de poppetjes / boven de hoofden ---
    def kp(n): return koppen.get(n)
    if k == "open" and t >= B["health"] and kp("you"): balkje(img, kp("you")[0], kp("you")[1] - 60, "HEALTH 100%", 1.0)
    if k in ("keuken1", "eind") and kp("dad"):
        held(img, "koffiemok", 70, "dad", kp("dad"), t)
        if k == "keuken1" and B["geld"] <= t < Z[9][0]: geldteller(img, kp("dad")[0], kp("dad")[1] - 50, "$312", ps.pop((t - B["geld"]) / 0.3))
    if k == "keuken1" and kp("mom"):
        hx, hy, S = rhand("mom", kp("mom")[3], kp("mom")[4], kp("mom")[5], -32)
        WACHT.plaats("telefoon", (hx - 14 * S, hy - 38 * S, hx + 14 * S, hy + 8 * S), op="hand:mom", punt=(hx, hy)); telefoontje(img, hx, hy, S, t)
    if k == "dag1":
        if kp("buur"): hx, hy, _ = rhand("buur", kp("buur")[3], kp("buur")[4], kp("buur")[5], 70); water(img, hx - 10, hy - 6, t)
        tg, tp = B["kauw"]
        if tg <= t < tp and kp("dad"):
            hx0, hy0, _ = rhand("dad", kp("dad")[3], kp("dad")[4], kp("dad")[5], 20); f = min(1, (t - tg) / 0.5)
            x_, y_ = hx0, hy0 + (975 - hy0) * f * f
            WACHT.plaats("kauwgompapiertje", (x_ - 16, y_ - 10, x_ + 16, y_), op="weg" if f >= 1 else "aan:lucht")
            ImageDraw.Draw(img).rectangle((x_ - 16, y_ - 10, x_ + 16, y_), fill=(210, 215, 225), outline=INK, width=2)
        n_s, kn = 0, False
        for tt_, n_ in B["ster"]:
            if t >= tt_: n_s, kn = abs(n_), n_ < 0
        if kp("dad"): sterren(img, kp("dad")[0], kp("dad")[1] - 55, n_s, t, kn)
    if k in ("dag1", "radio2") and B.get("radio"):
        r0, r1 = B["radio"]
        if r0 <= t < r1:
            ballon(img, 620, 520, "SUPER SUCK 3000!", ps.pop((t - r0) / 0.3), naam="radio")
            zet(img, "stofzuiger", 110, 620, 466, op="beeld", naam="stofzuiger")
    if k == "radio2": zet(img, "gezinsauto", 210, 620, 905, op="weg", naam="auto", tint=0.13)
    if k == "winkel":
        if t >= B["melk"] and kp("mom"): held(img, "melk", 90, "mom", kp("mom"), t)
        if Z[29][0] <= t < Z[29][1] + 0.3 and kp("kassa"):
            hx, hy, _ = rhand("kassa", kp("kassa")[3], kp("kassa")[4], kp("kassa")[5], 70); notitieblok(img, hx, hy, "kassa")
    if k == "garage":
        pass
    if k in ("cheat", "cheat2"):
        af = B.get("afpak", 1e9); wie = "mom" if t >= af else "sis"
        if kp(wie):
            hk = 70; hx, hy, _ = rhand(wie, kp(wie)[3], kp(wie)[4], kp(wie)[5], hk)
            zet(img, "afstandsbediening", 75, hx, hy + 22, op="hand:" + wie, punt=(hx, hy), voor=True)
    if k == "kantoor1":
        if t >= B["pijl_boss"] and kp("boss"): pijl(img, kp("boss")[0], kp("boss")[1] - 110, t, 0.8, naam="pijl-boss")
        wie = "dad" if t >= B["pizza_naar_dad"] else "boss"
        if kp(wie):
            if wie == "dad": figs_dad = True
            held(img, "pizzadoos", 95, wie, kp(wie), t)
    if k == "timer":
        k0, k1, k2 = B["klok"]
        if t >= k0:
            sec = 90 if t < k1 else max(0, 89 - (t - k1) / max(0.1, k2 - k1) * 89)
            timer(img, 960, 190, sec, rood=sec <= 0)
        tv_ = B["vlieg"]
        if kp("dad"):
            if t < tv_: held(img, "pizzadoos", 95, "dad", kp("dad"), t)
            else:
                f = min(1, (t - tv_) / 0.9); x0_ = 1180; x = x0_ + 520 * f; y = 820 - 380 * math.sin(math.pi * f) + (990 - 820) * f
                WACHT.plaats("pizzadoos", (x - 50, y - 60, x + 50, y), op="weg" if f >= 1 else "aan:lucht")
                s_ = sprite("pizzadoos", 60).rotate(-f * 400, expand=True); img.paste(s_, (int(x - s_.width / 2), int(y - s_.height)), s_)
    if k == "kantoor2" and t >= B["pizza_dad"] and kp("dad"): held(img, "pizzadoos", 95, "dad", kp("dad"), t)
    if k == "klas" and t >= B["pijl_teach"] and kp("teach"): pijl(img, kp("teach")[0], kp("teach")[1] - 110, t, 0.8, naam="pijl-juf")
    if k == "feit" and kp("dad"):
        hx, hy, S = rhand("dad", kp("dad")[3], kp("dad")[4], kp("dad")[5], -32)
        WACHT.plaats("telefoon", (hx - 14 * S, hy - 38 * S, hx + 14 * S, hy + 8 * S), op="hand:dad", punt=(hx, hy)); telefoontje(img, hx, hy, S, t)
    if k in ("zh1", "zh2") and B.get("nat") and kp("dad"): druppels(img, kp("dad")[3], kp("dad")[1], kp("dad")[4], t)
    if k == "rest":
        for n_ in ("ober", "ober2", "ober3"):
            if kp(n_): held(img, "broodmand", 70, n_, kp(n_), t, naam="broodmand")
    if k == "fiets":
        b0, b1 = B["biljet"]
        if b0 <= t < b1 and kp("dad"):
            hx, hy, _ = rhand("dad", kp("dad")[3], kp("dad")[4], kp("dad")[5], 70); biljetjes(img, hx, hy, "dad")
        if t >= B["fiets"]: zet(img, "fiets", int(230 * ps.pop((t - B["fiets"]) / 0.35)), 1350, 990, op="weg")
        if t >= B["ster"][0][0] and kp("dad"): sterren(img, kp("dad")[0], kp("dad")[1] - 55, 1, t)
    if k == "chaos":
        for n_, ns in (("you", 3), ("dad", 5)):
            if kp(n_): sterren(img, kp(n_)[0], kp(n_)[1] - 55, ns, t)
    if k == "save2" and t >= B["floppy"]: floppy(img, 1160, 360, t)
    if k == "team":
        if kp("buur"):
            hx, hy, _ = rhand("buur", kp("buur")[3], kp("buur")[4], kp("buur")[5], 70)
            for j in range(3): zet(img, "pizzadoos", 70, hx, hy + 20 - j * 26, op="hand:buur" if j == 0 else "aan:pizzadoos", punt=(hx, hy) if j == 0 else None, voor=True)
        if kp("sis"):
            hx, hy, _ = rhand("sis", kp("sis")[3], kp("sis")[4], kp("sis")[5], 70); stopwatch(img, hx, hy, "sis", t * 5)
    if k == "wakker":
        wg = B["weg"]
        if t < wg["health"] and kp("you"): balkje(img, kp("you")[0], kp("you")[1] - 60, "HEALTH 100%", 1.0)
        if t < wg["pijl"]: pijl(img, 1160, 330, t, 0.8)
    if k == "eind" and kp("buur") and t >= kw(120, "Gary", -0.2): pass
    # grijs (respawn)
    if B.get("grijs") is not None and t >= B["grijs"]: img = grijs(img, (t - B["grijs"]) / 0.6)
    WACHT.einde({n_: v for n_, v in GEZ.items()})
    # rustige push-in per scène
    f = 1 + 0.06 * ps.ease((t - B["t"]) / max(1.0, B["eind"] - B["t"]))
    cw, ch = W / f, H / f; cx0, cy0 = (W - cw) / 2, (H - ch) * 0.45; CROP[0] = (cx0, cy0, cx0 + cw, cy0 + ch)
    if f > 1.001 and ZOOM_AAN: img = img.crop((int(cx0), int(cy0), int(cx0 + cw), int(cy0 + ch))).resize((W, H), Image.BICUBIC)
    # HUD en koppen na de zoom
    if TEKST_AAN:
        kaartweg = KB["wakker"]["weg"]["map"]
        if t < kaartweg and k != "eind": minimap(img, t)
        if B.get("kaart") is not None: kaart(img, t, B["kaart"])
        if B.get("bron") is not None and t >= B["bron"]:
            d2 = ImageDraw.Draw(img); s_ = "Source: Take-Two Interactive, 2013"; d2.text((40, 905), s_, font=font(FS, 30), fill=(255, 255, 255), stroke_width=4, stroke_fill=(0, 0, 0)); SCHERM.append(s_)
        for st, s, x, y, m, kl, *eind_ in B["kop"]:
            later = [st2 for st2, s2, x2, y2, *_ in B["kop"] if (x2, y2) == (x, y) and st2 > st]
            if eind_ and t >= eind_[0]: continue
            if t >= st and not (later and t >= min(later)): kop(img, s, x, y, m, KL[kl], ps.pop((t - st) / 0.3) if st >= 0 else 1.0)
        ondertitel(img, t)
    TW.zie(t, nu, voorwerpen=WACHT.dit_frame, teksten=list(SCHERM), koppen={k_: (v[0], v[1]) for k_, v in GEZ.items()}, gebaren=dict(GEB), crop=CROP[0])
    return img
def telefoontje(img, hx, hy, S, t):
    d = ImageDraw.Draw(img); d.rounded_rectangle((hx - 13 * S, hy - 36 * S, hx + 13 * S, hy + 6 * S), int(5 * S), fill=(30, 30, 36), outline=(10, 10, 12), width=2)
    d.rounded_rectangle((hx - 10 * S, hy - 32 * S, hx + 10 * S, hy + 2 * S), int(3 * S), fill=(150, 220, 255) if int(t * 3) % 2 else (120, 235, 160))

# ---------- geluid: echte opnames waar we ze hebben, de rest zelf gemaakt; alleen wat je ziet ----------
GSR = 48000
def _laad(n):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HIER.parent / "geluiden" / f"{n}.mp3"), "-ac", "1", "-ar", str(GSR), "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
def _drukste(x, dur):
    n = min(len(x) - 1, int(dur * GSR)); e = np.convolve(x ** 2, np.ones(GSR // 10), "same")
    best = max(range(0, max(1, len(x) - n), GSR // 20), key=lambda i: e[i:i + n].sum()); return x[best:best + n]
def _fade(x, f=0.04):
    k = min(len(x) // 3, int(f * GSR)); x = x.copy(); x[:k] *= np.linspace(0, 1, k); x[-k:] *= np.linspace(1, 0, k); return x
def _tt(d): return np.arange(int(d * GSR)) / GSR
def geluid():
    rng = np.random.default_rng(7); uit = np.zeros(int((EIND + 1) * GSR), np.float32); GELUIDEN.clear()
    def zet_(t, n, x, g, zie):
        i = int(t * GSR); j = min(len(uit), i + len(x))
        if i < 0 or j <= i: return
        uit[i:j] += x[:j - i] * g; GELUIDEN.append((t, n, zie))
    x = _tt(0.35); ding = sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 7) for f in (1568, 2350)) * 0.4
    x = _tt(2.0); sir = np.sin(2 * np.pi * np.cumsum(np.where((x * 2) % 1 < 0.5, 700, 950)) / GSR) * 0.35 * np.minimum(1, x * 4)
    x = _tt(1.4); fan = sum(np.sign(np.sin(2 * np.pi * f * (x - o))) * (x > o) * np.exp(-np.maximum(0, x - o) * 2.2) * 0.12 for f, o in ((523, 0), (659, 0.15), (784, 0.3), (1047, 0.45)))
    x = _tt(0.22); kwek = np.sin(2 * np.pi * np.cumsum(900 + 1400 * x / 0.22) / GSR) * np.exp(-x * 9) * 0.5
    x = _tt(0.9); plons_ = np.convolve(rng.normal(0, 1, len(x)), np.ones(30) / 30, "same") * np.exp(-x * 5) * 1.6
    x = _tt(1.2); sis_ = rng.normal(0, 1, len(x)) * 0.25 * np.minimum(1, x * 8) * np.exp(-np.maximum(0, x - 0.9) * 10)
    x = _tt(0.8); faal = sum(np.sign(np.sin(2 * np.pi * f * (x - o))) * (x > o) * np.exp(-np.maximum(0, x - o) * 3) * 0.12 for f, o in ((392, 0), (330, 0.2), (262, 0.4)))
    x = _tt(1.0); bel = sum(np.sin(2 * np.pi * f * x) * np.exp(-x * 4) for f in (2637, 3520)) * 0.3
    stap = _fade(_drukste(_laad("stappen"), 0.25)); klik = _fade(_laad("klik")); kassa = _fade(_laad("kassa")); ploff = _fade(_laad("plof"))
    papier = _fade(_drukste(_laad("papier"), 0.4)); deur = _fade(_laad("deur-dicht")); stempel = _fade(_laad("stempel")); auto = _fade(_drukste(_laad("auto"), 1.4))
    for B in BLOK:
        k = B["key"]
        for p in B["figs"]:
            if "pad" in p:
                for (ta, xa), (tb, xb) in zip(p["pad"], p["pad"][1:]):
                    if xa != xb:
                        for q in np.arange(ta + 0.1, tb, 0.3): zet_(q, "stappen", stap, 0.3, p["n"])
        for st, s, *_ in B["kop"]:
            if st < 0: continue
            if "MISSION COMPLETE" in s or s == "GAME SAVED" or s == "CHEAT ACTIVATED": zet_(st, "fanfare", fan, 0.5, "tekst:" + s)
            elif "MISSION FAILED" in s: zet_(st, "faal", faal, 0.5, "tekst:" + s)
            elif "RESPECT" in s and s.startswith("+"): zet_(st, "ding", ding, 0.45, "tekst:" + s)
            elif s in ("-$100",): zet_(st, "kassa", kassa, 0.4, "tekst:" + s)
        if k == "dag1":
            for tt_, n_ in B["ster"]:
                if n_ > 0: zet_(tt_, "ding", ding, 0.6, "ster")
            zet_(B["politie"][0] + 0.1, "sirene", sir, 0.5, "politieauto"); zet_(B["politie"][1], "auto", auto, 0.5, "politieauto")
            zet_(B["kauw"][0] + 0.35, "papier", papier, 0.4, "kauwgompapiertje"); zet_(B["radio"][0], "klik", klik, 0.6, "radio")
        if k == "winkel": zet_(B["cirkel"][0], "ding", ding, 0.4, "cirkel")
        if k == "val": zet_(kw(31, "fall", -0.1), "plof", ploff, 0.6, "tuinslang")
        if k == "garage":
            c = B["car"]; zet_(Z[B["a"]][0] + 0.2, "sirene", sir, 0.35, "politieauto"); zet_(c["dicht"][0], "deur", deur, 0.5, "verfgarage-deur")
            zet_(c["dicht"][0] + 0.8, "spuitbus", sis_, 0.5, "verfgarage-deur")
            for tt_, _ in c["tint"][1:]: zet_(tt_, "spuitbus", sis_[: int(0.5 * GSR)], 0.4, "auto")
        if k == "cheat":
            for st, s, *_ in B["kop"]:
                if s.startswith("LEFT"): zet_(st, "klik", klik, 0.5, "afstandsbediening")
            for q in np.arange(B["eendjes"] + 0.3, B["eind"], 0.5): zet_(q, "piep", kwek, 0.25, "badeend")
        if k == "eenden":
            for q in np.arange(B["t"] + 0.2, B["eind"], 0.3): zet_(q, "piep", kwek, 0.25 + 0.1 * ((q * 7) % 1), "badeend")
        if k == "timer": zet_(B["klok"][2], "faal", faal, 0.4, "timer"); zet_(kw(56, "trips"), "plof", ploff, 0.6, "pizzadoos"); zet_(B["vlieg"] + 0.9, "plof", ploff, 0.4, "pizzadoos")
        if k == "strand": zet_(B["jet"][0] + 0.2, "auto", auto, 0.35, "jetski"); zet_(B["jet"][1], "plons", plons_, 0.8, "jetski")
        if k == "zh1": zet_(B["kaart"], "papier", papier, 0.5, "spaarkaart")
        if k == "teddy": zet_(kw(79, "hidden"), "ding", ding, 0.5, "teddy")
        if k == "fiets": zet_(B["fiets"], "bel", bel, 0.5, "fiets"); zet_(B["ster"][0][0], "ding", ding, 0.6, "ster")
        if k == "chaos": zet_(B["t"] + 0.2, "sirene", sir, 0.4, "politieauto"); zet_(B["t"] + 3.0, "sirene", sir, 0.35, "politieauto")
        if k == "radio2": zet_(B["radio"][0], "klik", klik, 0.6, "radio")
        if k == "save2": zet_(B["floppy"], "ding", ding, 0.5, "floppy")
        if k == "eind": zet_(B["tvaan"], "klik", klik, 0.6, "tv")
    uit /= max(1, np.abs(uit).max() / 0.9); sf.write(HIER / "sfx.wav", uit, GSR)
def geluidcheck():
    fout = []
    for t, n, zie in GELUIDEN:
        frame(t + 0.15); gezien = {x[0] for x in WACHT.dit_frame} | set(GEZ) | {"tekst:" + s for s in SCHERM}
        if zie == "verfgarage-deur": continue                     # de deur zit in de achtergrond zelf
        if zie not in gezien: fout.append(f"{t:.1f} s: geluid '{n}' maar '{zie}' is niet in beeld")
    return fout

if __name__ == "__main__":
    if "--tekst" in sys.argv:
        for i in range(int(EIND * 4)): frame(i / 4)
        print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten"); print("LAYOUT:", sorted(LAYOUT) or "alles past"); sys.exit()
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((400, 225)) for z in Z]
        for v in range(0, len(ims), 24):
            pl = Image.new("RGB", (400 * 6, 225 * 4))
            for i, im in enumerate(ims[v:v + 24]): pl.paste(im, (400 * (i % 6), 225 * (i // 6)))
            pl.save(HIER / f"plaat-{v // 24}.jpg", quality=80)
        print("platen", (len(ims) + 23) // 24); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); sys.exit()
    tot = EIND; naam = "gta-echt.mp4"
    if "--proef" in sys.argv: tot = min(EIND, float(sys.argv[sys.argv.index("--proef") + 1])); naam = "gta-proef.mp4"
    geluid(); gf = geluidcheck(); print("GELUIDCHECK:", gf or "elk geluid hoort bij iets in beeld")
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{tot:.2f}", str(HIER / naam)], stdin=subprocess.PIPE)
    for i in range(int(tot * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 20) == 0: print(f"{i / FPS:.0f} / {tot:.0f} s", flush=True)
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)")
    print("TEKSTWACHTER:", TW.schrijf(HIER / "TEKSTWACHTER.md"), "fouten (zie TEKSTWACHTER.md)")
    zz = [z for z in Z if z[1] <= tot]
    blad(HIER / naam, zz, HIER / "TEKSTCONTROLE.jpg", breed=400, hoog=225); print("TEKSTCONTROLE.jpg: per zin begin/midden/eind (zelf nakijken)")
    print("KLAAR", naam, round(tot, 1), "s")
