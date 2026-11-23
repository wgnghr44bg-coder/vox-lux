"""What If Everyone Got Superpowers Overnight? — lange video, liggend 1920x1080 (eigenaar 23 nov 2026).
Regels (WHATIF-AFSPRAKEN.md): alleen tonen wat er op dat moment gezegd wordt, spullen echt in de hand, poppetjes lopen/kijken
naar wat er gebeurt, geen grote tekst die hetzelfde zegt als de ondertitel, geen effect bij scènewissel, geen muziek, alleen stem.
Les uit Studio: meteen chaos in de eerste 5 s (zus zweeft, papa door de muur), regels daarna.
Gebruik: <omnivoice-venv>/python maak.py [--plaat]  -> superpowers.mp4"""
import json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)

W, H, FPS, SS = 1920, 1080, 30, ps.SS
ps.C.update({
 "kid1": dict(broek=(60, 60, 80), shirt=(220, 80, 70), haar=(150, 90, 50), kapsel="kort", groot=0.9),
 "kid2": dict(broek=(70, 90, 70), shirt=(80, 190, 170), haar=(40, 30, 25), kapsel="paard", groot=0.88),
 "kid3": dict(broek=(60, 70, 60), shirt=(240, 150, 60), haar=(40, 30, 25), kapsel="krul", groot=0.9),
})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".,:" and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.5
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def Zs(i): return Z[i][0] - 0.1
LIJF = {"YOU": "you", "DAD": "dad", "MOM": "mom", "SIS": "sis", "TEACH": "teach"}
NAAM = {"YOU": "YOU", "DAD": "DAD", "MOM": "MOM", "SIS": "SISTER", "TEACH": "TEACHER"}
def luid(t, lijf):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == lijf for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
def lin(t, a, b, x0, x1): return x0 + (x1 - x0) * ps.ease((t - a) / max(0.05, b - a)) if t > a else x0

BGDIR = HIER.parent / "video-swap" / "afbeeldingen"
BG = {}
def bg(n):
    if n not in BG:
        if n == "leeg":                                    # rustige effen ruimte voor het feit
            im = Image.new("RGB", (W, H), (253, 240, 222)); ImageDraw.Draw(im).rectangle((0, 820, W, H), fill=(236, 214, 186)); BG[n] = im
        elif n == "kamer-nacht":
            im = Image.open(BGDIR / "kamer-jij.png").convert("RGB").resize((W, H)); BG[n] = Image.blend(im, Image.new("RGB", (W, H), (20, 25, 60)), 0.55)
        else: BG[n] = Image.open(BGDIR / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
L = (45, 38, 40)

# ---------- voorwerpen ----------
def tafel(d, x, y, w=520):
    d.rectangle((x - w / 2, y, x + w / 2, y + 26), fill=(190, 140, 95), outline=L, width=5)
    for k in (-1, 1): d.rectangle((x + k * (w / 2 - 40) - 12, y + 26, x + k * (w / 2 - 40) + 12, y + 190), fill=(170, 120, 80), outline=L, width=4)
def bord(d, x, y):                                         # ontbijtbord met ei en toast
    d.ellipse((x - 55, y - 16, x + 55, y + 16), fill=(255, 255, 255), outline=L, width=4)
    d.ellipse((x - 24, y - 10, x + 6, y + 8), fill=(255, 255, 250)); d.ellipse((x - 14, y - 6, x - 2, y + 4), fill=(255, 200, 40))
    d.rectangle((x + 10, y - 22, x + 40, y + 4), fill=(220, 170, 100), outline=L, width=3)
def lepel(d, x, y):
    d.ellipse((x - 14, y - 22, x + 14, y + 10), fill=(200, 205, 215), outline=L, width=3); d.line((x, y + 8, x, y + 70), fill=L, width=7); d.line((x, y + 8, x, y + 70), fill=(200, 205, 215), width=3)
def deur(d, x, y):
    d.rectangle((x - 95, y - 330, x + 95, y), fill=(165, 115, 75), outline=L, width=6)
    d.rectangle((x - 70, y - 300, x + 70, y - 190), outline=(130, 90, 60), width=4); d.rectangle((x - 70, y - 160, x + 70, y - 30), outline=(130, 90, 60), width=4)
    d.ellipse((x + 55, y - 175, x + 75, y - 155), fill=(240, 200, 80), outline=L, width=3)
def rugzak(d, x, y, t):
    b = abs(math.sin(t * 7)) * 8
    d.rounded_rectangle((x - 60, y - 150 - b, x + 60, y - b), 24, fill=(230, 80, 80), outline=L, width=5)
    d.rounded_rectangle((x - 40, y - 80 - b, x + 40, y - 30 - b), 10, fill=(200, 60, 60), outline=L, width=4)
    for k in (-1, 1): d.line((x + k * 30, y - b, x + k * 34 + math.sin(t * 7 + k) * 10, y + 50), fill=L, width=8)   # stapjes (onzichtbaar kind)
def vuur(d, x, y, t, r=1.0):
    for k, (kl, s) in enumerate((((255, 120, 30), 1.0), ((255, 200, 40), 0.65), ((255, 250, 180), 0.35))):
        w = 150 * s * r; fl = math.sin(t * 25 + k) * 12
        d.polygon([(x, y - 30 * s), (x + w, y - 55 * s + fl), (x + w * 1.4, y), (x + w, y + 55 * s - fl), (x, y + 30 * s)], fill=kl)
def boom_top(img): pass
def broccoli(d, x, y, s=1.0):
    d.rectangle((x - 12 * s, y, x + 12 * s, y + 60 * s), fill=(140, 190, 90), outline=L, width=3)
    for a, b in ((-28, -10), (0, -30), (28, -10), (-14, -38), (14, -38)):
        d.ellipse((x + a * s - 26 * s, y + b * s - 26 * s, x + a * s + 26 * s, y + b * s + 26 * s), fill=(60, 150, 60), outline=L, width=3)
def tas(d, x, y):
    d.polygon([(x - 50, y - 90), (x + 50, y - 90), (x + 60, y), (x - 60, y)], fill=(225, 195, 150), outline=L)
    d.line((x - 25, y - 90, x - 20, y - 125), fill=L, width=5); d.line((x + 25, y - 90, x + 20, y - 125), fill=L, width=5)
def sleutels(d, x, y):
    d.ellipse((x - 30, y - 30, x + 10, y + 10), outline=(200, 160, 40), width=8); d.line((x + 5, y - 5, x + 60, y + 30), fill=(200, 160, 40), width=10)
    d.line((x + 40, y + 18, x + 48, y + 34), fill=(200, 160, 40), width=8)
def bot(d, x, y):
    for k in (-1, 1):
        d.ellipse((x + k * 50 - 18, y - 30, x + k * 50 + 18, y + 4), fill=(250, 245, 235), outline=L, width=3); d.ellipse((x + k * 50 - 18, y - 4, x + k * 50 + 18, y + 30), fill=(250, 245, 235), outline=L, width=3)
    d.rectangle((x - 50, y - 14, x + 50, y + 14), fill=(250, 245, 235)); d.line((x - 48, y - 14, x + 48, y - 14), fill=L, width=3); d.line((x - 48, y + 14, x + 48, y + 14), fill=L, width=3)
def wolkje(d, x, y, w=230, h=150):                         # gedachtewolk met bolletjes naar beneden
    for a in range(10):
        hh = math.radians(a * 36); d.ellipse((x + math.cos(hh) * w * 0.42 - 45, y + math.sin(hh) * h * 0.38 - 38, x + math.cos(hh) * w * 0.42 + 45, y + math.sin(hh) * h * 0.38 + 38), fill=(255, 255, 255), outline=L, width=4)
    for a in range(10):
        hh = math.radians(a * 36); d.ellipse((x + math.cos(hh) * w * 0.42 - 40, y + math.sin(hh) * h * 0.38 - 33, x + math.cos(hh) * w * 0.42 + 40, y + math.sin(hh) * h * 0.38 + 33), fill=(255, 255, 255))
    d.ellipse((x - w * 0.42, y - h * 0.38, x + w * 0.42, y + h * 0.38), fill=(255, 255, 255))
    for r, dy in ((16, h * 0.62), (10, h * 0.82)): d.ellipse((x - 20 - r, y + dy - r, x - 20 + r, y + dy + r), fill=(255, 255, 255), outline=L, width=4)
def kruis(d, x, y, r=60): d.line((x - r, y - r, x + r, y + r), fill=(220, 40, 40), width=14); d.line((x - r, y + r, x + r, y - r), fill=(220, 40, 40), width=14)
def vraag(d, x, y): d.text((x, y), "?", font=ps.font(ps.FB, 90), fill=(220, 40, 40), anchor="mm")
def hond(d, x, y, t):                                      # simpel hondje (zijkant)
    d.ellipse((x - 90, y - 90, x + 70, y - 10), fill=(200, 150, 100), outline=L, width=5)
    d.ellipse((x + 40, y - 140, x + 130, y - 60), fill=(200, 150, 100), outline=L, width=5)
    d.ellipse((x + 50, y - 125, x + 80, y - 75), fill=(150, 100, 60), outline=L, width=4); d.ellipse((x + 98, y - 112, x + 110, y - 100), fill=L)
    for k in (-60, -20, 20, 50): d.line((x + k, y - 20, x + k, y + 30), fill=L, width=10)
    d.line((x - 85, y - 70, x - 130, y - 110 + math.sin(t * 9) * 15), fill=L, width=8)
def ster(d, x, y, r=40, kl=(255, 210, 50)):
    p = [(x + math.cos(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45), y + math.sin(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45)) for i in range(10)]
    d.polygon(p, fill=kl, outline=L)
def streep(d, x, y, richting=1, n=4):                       # snelheidsstrepen achter iemand
    for k in range(n): d.line((x - richting * (60 + k * 10), y - 90 + k * 50, x - richting * (260 + k * 40), y - 90 + k * 50), fill=(255, 255, 255), width=10)

# ---------- scènes: per zin-bereik ----------
FLOAT = lambda t: math.sin(t * 2.2) * 14
SC = [
 dict(t=0, bg="keuken", n="ochtend"), dict(t=Zs(4), bg="titel", n="titel"), dict(t=Zs(5), bg="keuken", n="regels"),
 dict(t=Zs(10), bg="schoolplein", n="school"), dict(t=Zs(11), bg="klas", n="klas"), dict(t=Zs(14), bg="schoolplein", n="lunch"),
 dict(t=Zs(15), bg="woonkamer", n="deur"), dict(t=Zs(18), bg="park", n="park"), dict(t=Zs(21), bg="leeg", n="feit"),
 dict(t=Zs(24), bg="kamer-nacht", n="nacht"),
]
Y = 960
def pop(d, laag, naam, x, y, s, t, **kw_):
    return ps.poppetje(d, naam, x, y, s, t, **kw_)

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; n = sc["n"]
    img = bg(sc["bg"]).copy()
    nu = next((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), None)
    sp = LIJF.get(Z[nu][4]) if nu is not None else None
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    geest = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dg = ImageDraw.Draw(geest)   # half doorzichtig (papa door muur/deur)
    vlak = ImageDraw.Draw(img)
    def P(naam, x, y=Y, s=1.5, kijk=0.0, **e):
        e.setdefault("knipper", (t + sum(map(ord, naam)) % 5 * 0.5) % 3.6 < 0.12)
        return pop(d, laag, naam, x, y, s, t, kijk=kijk, mond=luid(t, naam), **e)
    if n == "ochtend" or n == "regels":
        tafel(vlak, 900, 760)
        if t >= kw(2, "breakfast", -0.3) or n == "regels":
            for bx in (760, 900, 1040): bord(vlak, bx, 748)
        # zus zweeft boven de tafel (slaapt)
        vlak.ellipse((820, 744, 980, 762), fill=(150, 110, 80))                                   # schaduw op de tafel: ze zweeft echt
        P("sis", 900, 560 + FLOAT(t), 1.3, kijk=0.0, knipper=True) if n == "ochtend" and t < kw(2, "mom", -0.2) else P("sis", 900, 560 + FLOAT(t), 1.3, kijk=0.5)
        if n == "ochtend" and t < kw(2, "mom", -0.2):
            for i, (zx, zy, zm) in enumerate(((960, 250, 40), (1000, 205, 52), (1045, 150, 64))): vlak.text((zx, zy + math.sin(t * 2 + i) * 6), "z", font=ps.font(ps.FB, zm), fill=(90, 110, 200), anchor="mm")
        # papa door de muur
        if n == "ochtend":
            xd = lin(t, kw(0, "dad", -0.2), kw(0, "wall", 0.6), 60, 330)
            pop(dg, geest, "dad", xd, Y, 1.55, t, kijk=1.0, mond=luid(t, "dad"), loop=(t * 2.2 if kw(0, "dad", -0.2) < t < kw(0, "wall", 0.6) else None),
                gebaar="schouders" if Z[1][0] <= t <= Z[1][1] else None)
        else: P("dad", 330, kijk=1.0)
        # mama super snel
        if n == "ochtend" and kw(2, "mom", -0.2) <= t < kw(2, "second", 0.3):
            xm = 1250 + math.sin((t - kw(2, "mom")) * 18) * 260; P("mom", xm, kijk=-1.0); streep(vlak, xm, 820, 1 if math.cos((t - kw(2, "mom")) * 18) > 0 else -1)
        else: P("mom", 1350, kijk=-1.0)
        # jij
        xj = 1650; geb = None; yj = Y; verb = n == "ochtend" or (n == "regels" and Zs(8) <= t)
        if n == "regels" and nu == 7:
            if t < kw(7, "push", -0.2): yj = Y - abs(math.sin((t - Z[7][0]) * 6)) * 70                  # springen
            elif t < kw(7, "stare", -0.2): xj = 1560; geb = "wijs"                                     # tegen de muur duwen
            else: geb = "vast"
        top = P("you", xj, yj, 1.5, kijk=-1.0, verbaasd=verb, gebaar=geb, boos=(nu == 9))
        if n == "regels" and nu == 7 and t >= kw(7, "stare", -0.2):
            hx, hy = xj + 44 * 1.5 + 82 * 1.5 * math.sin(math.radians(70)), (Y - 92 * 1.5 - 83 * 1.5) + 82 * 1.5 * math.cos(math.radians(70))
            lepel(vlak, hx + 8, hy - 70)
        if n == "regels" and nu == 6:                       # bij elke kracht kort een sterretje boven wie het heeft
            for woord, x, y in (("sister", 900, 470), ("dad", 330, 560), ("mom", 1350, 560)):
                if t >= kw(6, woord, -0.1): ster(vlak, x, y)
        if n == "ochtend" and Z[1][0] <= t <= Z[1][1] + 0.4: sleutels(vlak, 470, 560); vraag(vlak, 540, 520)
    elif n == "titel":
        P("you", 960, Y, 2.0, kijk=0.0, verbaasd=True)
        P("sis", 1350, 700 + FLOAT(t), 1.4, kijk=-0.6)
        pop(dg, geest, "dad", 560, Y, 1.7, t, kijk=0.6)
        ps.kop(img, "WHAT IF EVERYONE GOT", 960, 150, 96, ps.KL["wit"], ps.pop((t - kw(4, "what")) / 0.3)) if t >= kw(4, "what") else None
        ps.kop(img, "SUPERPOWERS?", 960, 270, 130, ps.KL["geel"], ps.pop((t - kw(4, "superpowers")) / 0.3)) if t >= kw(4, "superpowers") else None
    elif n == "school":
        for i, (naam, x0) in enumerate((("kid1", 300), ("kid3", 1500))):    # kinderen vliegen naar de klas
            a = kw(10, "fly", -0.4) + i * 0.3; xx = lin(t, a, a + 3, x0, 960 + (i * 2 - 1) * 180); yy = lin(t, a, a + 3, Y, 520) + FLOAT(t + i)
            P(naam, xx, yy, 1.1, kijk=1.0 if x0 < 960 else -1.0)
        if t >= kw(10, "backpack", -0.4): rugzak(vlak, lin(t, kw(10, "backpack", -0.4), kw(10, "backpack", 3.5), 1750, 1200), 990, t)
        P("you", 520, kijk=0.8, verbaasd=True)
    elif n == "klas":
        for naam, x in (("kid1", 560), ("kid2", 820), ("you", 1080)):
            boos = nu == 13 and t >= kw(13, "groans", -0.2)
            P(naam, x, kijk=1.0, boos=boos)
        P("teach", 1500, kijk=-1.0, gebaar="wijslinks" if nu == 12 else None)
        if nu == 11 and t >= kw(11, "minds", -0.3):          # juf leest gedachten: wolkjes met ? boven de kinderen
            for x in (560, 820, 1080): wolkje(vlak, x + 90, 380, 170, 110); vraag(vlak, x + 90, 380)
        if nu == 13 and t >= kw(13, "heads", -0.3):
            for x in (560, 820, 1080): wolkje(vlak, x + 90, 380, 170, 110); vlak.text((x + 90, 380), "UGH", font=ps.font(ps.FB, 44), fill=L, anchor="mm")
        if nu == 13: vlak.text((1180, 300), "POP QUIZ", font=ps.font(ps.FS, 110), fill=(235, 240, 235), anchor="mm")
    elif n == "lunch":
        P("kid3", 1200, kijk=1.0, verbaasd=t >= kw(14, "sneezes", -0.1)); P("kid2", 1650, kijk=-1.0, verbaasd=t >= kw(14, "fire", 0.2)); P("you", 600, kijk=1.0, verbaasd=t >= kw(14, "fire", 0.2))
        if kw(14, "sneezes", -0.1) <= t < kw(14, "sneezes", 1.6): vuur(vlak, 1255, 600, t)
    elif n == "deur":
        deur(vlak, 500, Y + 10)
        if nu == 15 and t >= kw(15, "dad", -0.2):              # papa loopt dwars door de deur
            xd = lin(t, kw(15, "walks", -0.2), kw(15, "door", 0.8), 220, 760)
            pop(dg, geest, "dad", xd, Y, 1.55, t, kijk=1.0, loop=t * 2.2 if xd < 760 else None, mond=luid(t, "dad"))
        elif nu is not None and nu >= 16: pop(dg, geest, "dad", 760, Y, 1.55, t, kijk=1.0, mond=luid(t, "dad"), gebaar="schouders" if nu == 17 else None)
        P("sis", 1350, kijk=-1.0, boos=nu == 16, gebaar="wijslinks" if nu == 16 else None)
    elif n == "park":
        if nu == 18:
            a = kw(18, "runs", -0.2); xm = 1900 - ((t - a) * 900 % 3800) if t > a else 1500
            xm = 1500 if t < a else (abs(((t - a) * 1400) % 3200 - 1600) + 150)
            P("mom", xm, kijk=-1.0); streep(vlak, xm, 820, 1)
            if t >= kw(18, "seconds", -0.2): tas(vlak, xm + 110, 860)
        else: P("mom", 400, kijk=1.0)
        if nu is not None and nu >= 19:                        # zus boven in de boom, bang
            yy = lin(t, kw(19, "flies", -0.2), kw(19, "tree", 0.3), 900, 360) if nu == 19 else 360
            P("sis", 1720, yy + (FLOAT(t) * 0.3 if nu == 19 else 0), 1.0, kijk=-1.0, verbaasd=True)
        P("you", 960, kijk=1.0 if nu is not None and nu >= 19 else -1.0)
    elif n == "feit":
        rij = [("kid1", 480), ("kid2", 800), ("kid3", 1120), ("you", 1440)]
        for naam, x in rij:
            if nu == 23: continue
            P(naam, x, kijk=0.0, boos=(naam == "kid2" and nu == 22 and t >= kw(22, "broccoli", 0)))
        if nu == 22 and t >= kw(22, "one", -0.2): ster(vlak, 800, 500, 50)
        if nu == 22 and t >= kw(22, "broccoli", -0.3): broccoli(vlak, 900, 700, 1.3)
        if nu == 23:
            P("sis", 900, kijk=0.6, boos=True); broccoli(vlak, 1080, 700, 1.4); kruis(vlak, 1080, 680, 70)
    elif n == "nacht":
        P("you", 960, Y, 1.7, kijk=0.0, verbaasd=nu is not None and nu >= 25, knipper=False)
        if nu is not None and 25 <= nu < 28:
            if t >= kw(25, "sister", -0.2): wolkje(vlak, 420, 300); broccoli(vlak, 420, 290, 0.8); kruis(vlak, 420, 290, 55)
            if t >= kw(25, "dad", -0.2): wolkje(vlak, 960, 220); sleutels(vlak, 930, 220); vraag(vlak, 1030, 200)
            if t >= kw(25, "dog", -0.2): wolkje(vlak, 1500, 300); bot(vlak, 1500, 300)
        if nu is not None and 26 <= nu < 28:
            for i in range(6): wolkje(vlak, 200 + i * 300, 560 + (i % 2) * 60, 140, 90)
        if nu == 28 and t >= kw(28, "teacher", -0.2):
            wolkje(vlak, 1450, 380, 420, 300)
            mini = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); ps.poppetje(ImageDraw.Draw(mini), "teach", 1450, 520, 0.9, t, kijk=-1.0, verbaasd=True)
            mini = mini.resize((W, H), Image.LANCZOS); img.paste(mini, (0, 0), mini)
            if t >= kw(28, "find", -0.2): vlak.text((1620, 290), "!", font=ps.font(ps.FB, 110), fill=(220, 40, 40), anchor="mm")
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    geest = geest.resize((W, H), Image.LANCZOS); a = geest.split()[3].point(lambda v: int(v * 0.55)); geest.putalpha(a); img.paste(geest, (0, 0), geest)
    ondertitel(img, t)
    return img

def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = ps.font(ps.FS, 56); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 6 or w[1][-1:] in ".?!,:": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 985
    if Z[i][4] in NAAM:
        fn = ps.font(ps.FB, 30); nm = NAAM[Z[i][4]]; nb = d.textlength(nm, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 50, W / 2 + nb / 2 + 14, y - 10), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 48), nm, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=ps.KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)
    if 21 <= i <= 23 and t >= Z[22][0]:
        d.text((40, 1040), "Source: research by Linda Bartoshuk (Yale) on supertasters, about 25% of people", font=ps.font(ps.FS, 26), fill=(90, 70, 60))

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.75 * (z[1] - z[0]))).resize((480, 270)) for z in Z]
        for v in range(0, len(ims), 16):
            pl = Image.new("RGB", (480 * 4, 270 * 4))
            for i, im in enumerate(ims[v:v + 16]): pl.paste(im, (480 * (i % 4), 270 * (i // 4)))
            pl.save(HIER / f"plaat-{v // 16}.jpg", quality=80)
        print("platen", (len(ims) + 15) // 16); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "superpowers.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 20) == 0: print(f"{i / FPS:.0f} / {EIND:.0f} s", flush=True)
    p.stdin.close(); p.wait(); print("KLAAR superpowers.mp4", round(EIND, 1), "s")
