"""What If-Short met poppetjes uit code (eigenaar 23 nov: "Ja als short"). Staand 1080x1920.
Verhaal + stem + woordtijden uit ../proef-whatif2 (What if you could see how much everyone earns?).
Poppetjes: losse delen (hoofd, haar, ogen, mond, lijf, armen, benen), dus altijd hetzelfde; lopen, knipperen, kijken,
praten op het geluid, gebaren (zwaaien, wijzen, schouders, stampen). Achtergronden = ComfyUI (leeg). Geen muziek."""
import json, math, re, subprocess
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1080, 1920, 30, 2
SRC = "../proef-whatif2/"
Z = json.load(open(SRC + "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(SRC + "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isdigit(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.3
AUD, SR = sf.read(SRC + "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def luid(t, zinnen):
    if not any(Z[i][0] <= t <= Z[i][1] for i in zinnen): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def pop(x): x = max(0.0, min(1.0, x)); return 1 + 0.2 * math.sin(math.pi * x) * (1 - x) if x < 1 else 1.0

LIJN, HUID, WANG, MONDK = (45, 38, 40), (255, 222, 196), (255, 170, 160), (120, 40, 50)
def P(x, y): return (x * SS, y * SS)
def ledemaat(d, x0, y0, hoek, lengte, dik, kleur, eind=None):
    x1 = x0 + math.sin(math.radians(hoek)) * lengte; y1 = y0 + math.cos(math.radians(hoek)) * lengte
    d.line([P(x0, y0), P(x1, y1)], fill=LIJN, width=int((dik + 6) * SS)); d.line([P(x0, y0), P(x1, y1)], fill=kleur, width=int(dik * SS))
    for r, k in (((dik + 6) / 2, LIJN), (dik / 2, kleur)): d.ellipse([P(x0 - r, y0 - r), P(x0 + r, y0 + r)], fill=k)
    if eind:
        r, k = eind
        d.ellipse([P(x1 - r - 3, y1 - r - 3), P(x1 + r + 3, y1 + r + 3)], fill=LIJN); d.ellipse([P(x1 - r, y1 - r), P(x1 + r, y1 + r)], fill=k)

# personages
C = {
 "you":    dict(broek=(55, 60, 85), shirt=(70, 130, 220), haar=(60, 45, 40), kapsel="kort", hoodie=True),
 "dad":    dict(broek=(90, 80, 70), shirt=(90, 180, 110), haar=(120, 80, 50), kapsel="kort", bril=True, groot=1.15),
 "mom":    dict(broek=(80, 60, 90), shirt=(160, 120, 220), haar=(110, 70, 45), kapsel="paard", groot=1.08),
 "sis":    dict(broek=(240, 200, 70), shirt=(250, 215, 80), haar=(70, 45, 35), kapsel="staartjes", jurk=True, groot=0.8),
 "driver": dict(broek=(60, 70, 90), shirt=(130, 140, 155), haar=(80, 60, 45), kapsel="kort", pet=(50, 80, 160), groot=1.12),
 "rich":   dict(broek=(60, 60, 65), shirt=(140, 140, 145), haar=(50, 40, 35), kapsel="kort", hoodie=True, koptelefoon=True, groot=1.05),
 "teach":  dict(broek=(90, 70, 70), shirt=(215, 90, 80), haar=(170, 170, 175), kapsel="grijs", bril=True, groot=1.08),
 "boss":   dict(broek=(40, 45, 60), shirt=(45, 50, 70), haar=(40, 35, 30), kapsel="kort", das=(200, 40, 50), groot=1.22),
 "fdad":   dict(broek=(70, 75, 95), shirt=(150, 100, 60), haar=(90, 60, 40), kapsel="kort", baard=True, groot=1.15),
 "friend": dict(broek=(60, 70, 60), shirt=(240, 150, 60), haar=(40, 30, 25), kapsel="krul", groot=0.95),
}
SPREKER = {"DAD": "dad", "SIS": "sis", "TEACH": "teach"}

BEWEGEN = False                                                            # 27 nov (eigenaar: "kun je ook iets maken voor de bewegingen"): renderer zet ps.BEWEGEN = True
_VEER = {}                                                                 # per poppetje: (t, links, rechts, v_links, v_rechts)
def _veer(sleutel, t, links, rechts):
    """Armen veren soepel naar de nieuwe houding (lichte overshoot) i.p.v. in één beeldje te springen."""
    oud = _VEER.get(sleutel)
    if oud is None or not (0 < t - oud[0] < 0.25):                         # eerste beeld of een sprong in de tijd: meteen goed
        _VEER[sleutel] = (t, links, rechts, 0.0, 0.0); return links, rechts
    dt = t - oud[0]; uit = []; k, c = 170.0, 17.0                          # veer (iets onder kritisch gedempt -> kleine overshoot)
    for pos, v, doel in ((oud[1], oud[3], links), (oud[2], oud[4], rechts)):
        for _ in range(4):                                                 # in kleine stapjes, stabiel
            h = dt / 4; acc = k * (doel - pos) - c * v; v += acc * h; pos += v * h
        uit.append((pos, v))
    _VEER[sleutel] = (t, uit[0][0], uit[1][0], uit[0][1], uit[1][1]); return uit[0][0], uit[1][0]
LIPSYNC = None                                                             # 27 nov (eigenaar: "zet dit er maar vast in"): renderer zet ps.LIPSYNC = Lipsync(woorden)
def poppetje(d, naam, x, y, s, t, loop=None, kijk=0.0, mond=0.0, knipper=False, verbaasd=False, gebaar=None, boos=False, viseem=None, sleutel=None, bewegen=None):
    kl = C[naam]; s *= kl.get("groot", 1.0)
    bob = abs(math.sin(loop * math.pi)) * 6 * s if loop is not None else math.sin(t * 2.2 + x) * 1.5 * s
    if gebaar == "stamp": bob = abs(math.sin(t * 14)) * 10 * s
    if gebaar == "schouders": bob -= 6 * s
    been, lijf, hoofd = 78 * s, 105 * s, 60 * s
    d.ellipse([P(x - 62 * s, y - 8 * s), P(x + 62 * s, y + 12 * s)], fill=(60, 40, 30, 60))   # schaduw op de vloer
    heup = y - been - 14 * s + bob * 0.3
    zw = math.sin(loop * math.pi) * 26 if loop is not None else 0
    for kant, h in ((-1, zw), (1, -zw)):
        ledemaat(d, x + kant * 18 * s, heup, h, been, 26 * s, kl["broek"] if not kl.get("jurk") else HUID, (13 * s, LIJN))
    top = heup - lijf - bob; sch = top + 22 * s
    if kl.get("jurk"):
        d.polygon([P(x - 40 * s, top), P(x + 40 * s, top), P(x + 68 * s, heup + 20 * s), P(x - 68 * s, heup + 20 * s)], fill=kl["shirt"], outline=LIJN, width=int(4 * s * SS))
    else:
        d.rounded_rectangle([P(x - 48 * s, top), P(x + 48 * s, heup + 12 * s)], int(26 * s * SS), fill=kl["shirt"], outline=LIJN, width=int(4 * s * SS))
    if kl.get("hoodie"):
        for k in (-1, 1): d.line([P(x + k * 10 * s, top + 8 * s), P(x + k * 12 * s, top + 40 * s)], fill=LIJN, width=int(3 * s * SS))
    if kl.get("jack"):                                                   # 26 nov: leren jack (Jensen Huang): T-shirt in een V, kraag, rits, glans
        d.polygon([P(x - 20 * s, top + 2 * s), P(x + 20 * s, top + 2 * s), P(x + 4 * s, heup + 10 * s), P(x - 4 * s, heup + 10 * s)], fill=kl.get("tee", (20, 20, 22)), outline=LIJN, width=int(3 * s * SS))
        for k in (-1, 1):
            d.polygon([P(x + k * 20 * s, top + 1 * s), P(x + k * 44 * s, top + 4 * s), P(x + k * 30 * s, top + 34 * s), P(x + k * 10 * s, top + 26 * s)], fill=kl["shirt"], outline=(110, 110, 120), width=int(3 * s * SS))
            d.line([P(x + k * 6 * s, top + 34 * s), P(x + k * 5 * s, heup + 8 * s)], fill=(150, 150, 160), width=int(3 * s * SS))
        d.line([P(x - 36 * s, top + 40 * s), P(x - 30 * s, top + 80 * s)], fill=(95, 95, 105), width=int(5 * s * SS))
    if kl.get("polo"):                                                   # 26 nov: polo (kraagje + knoopjes)
        for k in (-1, 1): d.polygon([P(x, top + 4 * s), P(x + k * 26 * s, top), P(x + k * 22 * s, top + 16 * s)], fill=kl["shirt"], outline=LIJN, width=int(3 * s * SS))
        d.line([P(x, top + 4 * s), P(x, top + 34 * s)], fill=LIJN, width=int(3 * s * SS))
        for k in (14, 26): d.ellipse([P(x - 2.5 * s, top + k * s), P(x + 2.5 * s, top + (k + 5) * s)], fill=(235, 235, 240))
    if kl.get("das"):
        d.polygon([P(x - 8 * s, top + 4 * s), P(x + 8 * s, top + 4 * s), P(x + 11 * s, top + 70 * s), P(x, top + 82 * s), P(x - 11 * s, top + 70 * s)], fill=kl["das"], outline=LIJN, width=int(2 * s * SS))
        d.polygon([P(x - 30 * s, top + 2 * s), P(x - 8 * s, top + 4 * s), P(x - 14 * s, top + 34 * s)], fill=(240, 240, 240), outline=LIJN, width=int(2 * s * SS))
        d.polygon([P(x + 30 * s, top + 2 * s), P(x + 8 * s, top + 4 * s), P(x + 14 * s, top + 34 * s)], fill=(240, 240, 240), outline=LIJN, width=int(2 * s * SS))
    links, rechts = -16 - zw * 0.8, 16 + zw * 0.8                     # armhoeken (0 = omlaag)
    if isinstance(gebaar, tuple): links, rechts = gebaar[1], gebaar[2]            # 26 nov: vrije armhoeken ("hoek", links, rechts) voor echte handelingen
    elif gebaar == "zwaai": rechts = 150 + 22 * math.sin(t * 11)
    elif gebaar == "wijs": rechts = 100
    elif gebaar == "vast": rechts = 70                                    # 23 nov: iets vasthouden voor je (knop, toets, koekje)
    elif gebaar == "telefoon": rechts = -32                               # 24 nov: telefoon voor de eigen borst (niet bij de buurman)
    elif gebaar == "haar": rechts = 165                                   # 23 nov: hand bij het hoofd (haar kammen)
    elif gebaar == "wijslinks": links = -100
    elif gebaar == "schouders": links, rechts = -58, 58
    elif gebaar == "stamp": links, rechts = -35 - 10 * math.sin(t * 14), 35 + 10 * math.sin(t * 14)
    # 24 nov (eigenaar: "andere bewegingen dan alleen zwaaien"):
    elif gebaar == "juich": links, rechts = -160 - 12 * math.sin(t * 9), 160 + 12 * math.sin(t * 9)          # beide armen omhoog
    elif gebaar == "schrik": links, rechts = -128 + 6 * math.sin(t * 30), 128 - 6 * math.sin(t * 30)         # handen omhoog naast het hoofd, trillen
    elif gebaar == "denk": rechts = -116                                                                      # hand aan de kin
    elif gebaar == "facepalm": rechts = -152                                                                  # hand voor het gezicht
    elif gebaar == "hoofdhanden": links, rechts = -172, 172                                                   # 26 nov: beide handen op het hoofd ("oh nee!", spijt/schrik)
    elif gebaar == "heupen": links, rechts = -28, 28                                                          # handen in de zij
    elif gebaar == "klap": links, rechts = 38 + 14 * math.sin(t * 16), -38 - 14 * math.sin(t * 16)            # in de handen klappen
    elif gebaar == "duim": rechts = 125                                                                       # duim omhoog (arm schuin omhoog)
    elif gebaar == "praat": links, rechts = -25 - 14 * math.sin(t * 5), 30 + 18 * math.sin(t * 6.5)           # handen bewegen mee met praten
    elif gebaar == "armen-open": links, rechts = -75, 75                                                      # 'wat?!' / uitleggen
    elif gebaar == "rennen": links, rechts = -16 - zw * 1.6, 16 + zw * 1.6                                    # armen zwaaien hard (met loop=)
    elif gebaar in ("knik", "nee"): pass                                                                      # alleen het hoofd beweegt
    beweeg = BEWEGEN if bewegen is None else bewegen
    if beweeg:                                                                                # 27 nov: levendiger bewegen
        if gebaar is None and loop is None: links += 3 * math.sin(t * 1.3 + x * 0.01); rechts -= 3 * math.sin(t * 1.3 + x * 0.01 + 0.6)   # ademen
        if gebaar != "heupen": links, rechts = _veer(sleutel or naam, t, links, rechts)
    na_hoofd = gebaar in ("denk", "facepalm", "hoofdhanden")                               # 24 nov: hand vóór het gezicht -> na het hoofd tekenen
    for kant, h in ((-1, links), (1, rechts)):
        if gebaar == "heupen":                                             # 24 nov: ellebogen naar buiten, handen op de heupen
            ex, ey = x + kant * 44 * s + kant * 34 * s, sch + 38 * s; hx2, hy2 = x + kant * 46 * s, sch + 78 * s
            for (a0, b0, a1, b1) in ((x + kant * 44 * s, sch, ex, ey), (ex, ey, hx2, hy2)):
                d.line([P(a0, b0), P(a1, b1)], fill=LIJN, width=int(28 * s * SS)); d.line([P(a0, b0), P(a1, b1)], fill=kl["shirt"], width=int(22 * s * SS))
            for (cx, cy) in ((x + kant * 44 * s, sch), (ex, ey)): d.ellipse([P(cx - 11 * s, cy - 11 * s), P(cx + 11 * s, cy + 11 * s)], fill=kl["shirt"])
            d.ellipse([P(hx2 - 15 * s, hy2 - 15 * s), P(hx2 + 15 * s, hy2 + 15 * s)], fill=LIJN); d.ellipse([P(hx2 - 12 * s, hy2 - 12 * s), P(hx2 + 12 * s, hy2 + 12 * s)], fill=HUID)
            continue
        if (kant == 1 or gebaar == "hoofdhanden") and na_hoofd: continue
        if kant == 1 and kl.get("robot"):                                  # 24 nov: robotarm (cyborg-Short), metaal met gewrichten + blauw lampje
            x0r, y0r = x + 44 * s, sch; lg = 82 * s
            ex, ey = x0r + math.sin(math.radians(h)) * lg * 0.5, y0r + math.cos(math.radians(h)) * lg * 0.5
            ledemaat(d, x0r, y0r, h, lg, 24 * s, (165, 175, 190), (14 * s, (120, 130, 148)))
            d.ellipse([P(ex - 11 * s, ey - 11 * s), P(ex + 11 * s, ey + 11 * s)], fill=(95, 105, 120), outline=LIJN, width=int(3 * s * SS))
            d.ellipse([P(ex - 5 * s, ey - 5 * s), P(ex + 5 * s, ey + 5 * s)], fill=(80, 200, 255))
            continue
        ledemaat(d, x + kant * 44 * s, sch, h, 82 * s, 22 * s, kl["shirt"], (12 * s, HUID))
    hx, hy = x, top - hoofd * 0.82
    if beweeg:
        if mond > 0.1 and gebaar not in ("knik", "nee"):                   # wie praat, knikt en beweegt het hoofd een beetje mee
            hy += math.sin(t * 6.5) * 3.0 * s * min(1.0, mond + 0.3); hx += math.sin(t * 3.1 + 1) * 2.0 * s
        if loop is not None: hx += (1 if kijk >= 0 else -1) * 5 * s       # lopen: iets naar voren leunen
    if gebaar == "knik": hy += abs(math.sin(t * 7)) * 6 * s                                                   # 24 nov: ja knikken
    kap = kl["kapsel"]; hk = kl["haar"]; lw = int(4 * s * SS)
    if kap == "paard": d.ellipse([P(hx + hoofd * 0.55, hy - 10 * s), P(hx + hoofd * 1.15, hy + 75 * s)], fill=hk, outline=LIJN, width=lw)
    if kap == "staartjes":
        for k in (-1, 1): d.ellipse([P(hx + k * hoofd * 1.05 - 22 * s, hy - 15 * s), P(hx + k * hoofd * 1.05 + 22 * s, hy + 40 * s)], fill=hk, outline=LIJN, width=lw)
    if kap == "grijs": d.rounded_rectangle([P(hx - hoofd - 10 * s, hy - hoofd - 8 * s), P(hx + hoofd + 10 * s, hy + 25 * s)], int(40 * s * SS), fill=hk, outline=LIJN, width=lw)
    d.ellipse([P(hx - hoofd - 4 * s, hy - hoofd - 4 * s), P(hx + hoofd + 4 * s, hy + hoofd + 4 * s)], fill=LIJN)
    d.ellipse([P(hx - hoofd, hy - hoofd), P(hx + hoofd, hy + hoofd)], fill=HUID)
    if kap == "achterover":                                              # 26 nov: dik haar achterover gekamd (Jensen nu): golf boven het voorhoofd, grijze slapen
        d.chord([P(hx - hoofd - 4 * s, hy - hoofd - 12 * s), P(hx + hoofd + 4 * s, hy + hoofd * 0.15)], 180, 360, fill=hk, outline=LIJN, width=lw)
        for k in (-1, 1): d.rounded_rectangle([P(hx + k * hoofd * 0.93 - 7 * s, hy - hoofd * 0.6), P(hx + k * hoofd * 0.93 + 7 * s, hy - hoofd * 0.05)], int(6 * s * SS), fill=hk, outline=LIJN, width=int(3 * s * SS))
        d.chord([P(hx - hoofd * 1.0, hy - hoofd - 26 * s), P(hx + hoofd * 0.95, hy - hoofd * 0.25)], 160, 380, fill=hk, outline=LIJN, width=lw)
        for k in range(-2, 3): d.arc([P(hx + k * 16 * s - 34 * s, hy - hoofd - 20 * s), P(hx + k * 16 * s + 34 * s, hy - hoofd * 0.35)], 205, 290, fill=tuple(max(0, c - 55) for c in hk), width=int(3 * s * SS))
    if kap == "scheiding":                                               # 26 nov: kort haar met scheiding opzij (Jensen 1993)
        d.chord([P(hx - hoofd - 3 * s, hy - hoofd - 8 * s), P(hx + hoofd + 3 * s, hy + hoofd * 0.6)], 180, 360, fill=hk, outline=LIJN, width=lw)
        d.polygon([P(hx - 18 * s, hy - hoofd - 6 * s), P(hx + hoofd * 0.95, hy - hoofd * 0.55), P(hx + hoofd * 0.9, hy - hoofd * 0.25), P(hx - 10 * s, hy - hoofd * 0.62)], fill=hk, outline=LIJN)
        d.line([P(hx - 18 * s, hy - hoofd - 4 * s), P(hx - 22 * s, hy - hoofd * 0.55)], fill=tuple(min(255, c + 60) for c in hk), width=int(3 * s * SS))
    if kap in ("kort", "paard", "staartjes", "grijs"):
        d.chord([P(hx - hoofd - 3 * s, hy - hoofd - 6 * s), P(hx + hoofd + 3 * s, hy + hoofd * 0.6)], 180, 360, fill=hk, outline=LIJN, width=lw)
    if kap == "kort": d.ellipse([P(hx + 5 * s, hy - hoofd - 16 * s), P(hx + 30 * s, hy - hoofd + 4 * s)], fill=hk, outline=LIJN, width=int(3 * s * SS))
    if kap == "krul":
        for k in range(-3, 4): d.ellipse([P(hx + k * 18 * s - 20 * s, hy - hoofd - 18 * s + abs(k) * 6 * s), P(hx + k * 18 * s + 20 * s, hy - hoofd + 22 * s + abs(k) * 6 * s)], fill=hk, outline=LIJN, width=int(3 * s * SS))
    if kl.get("pet"):
        d.chord([P(hx - hoofd - 4 * s, hy - hoofd - 10 * s), P(hx + hoofd + 4 * s, hy + hoofd * 0.4)], 180, 360, fill=kl["pet"], outline=LIJN, width=lw)
        d.rounded_rectangle([P(hx - 10 * s, hy - 22 * s), P(hx + hoofd + 40 * s, hy - 8 * s)], int(6 * s * SS), fill=kl["pet"], outline=LIJN, width=lw)
    if kl.get("koptelefoon"):
        d.arc([P(hx - hoofd - 10 * s, hy - hoofd - 14 * s), P(hx + hoofd + 10 * s, hy + hoofd)], 180, 360, fill=(70, 70, 75), width=int(10 * s * SS))
        for k in (-1, 1): d.rounded_rectangle([P(hx + k * hoofd - 16 * s, hy - 22 * s), P(hx + k * hoofd + 16 * s, hy + 24 * s)], int(12 * s * SS), fill=(80, 80, 85), outline=LIJN, width=lw)
    ox = kijk * 12 * s; oy = 6 * s
    if gebaar == "nee": ox += math.sin(t * 10) * 10 * s; hx += math.sin(t * 10) * 3 * s                     # 24 nov: nee schudden
    for k in (-1, 1):
        ex, ey = hx + k * 22 * s + ox, hy + oy
        if knipper: d.line([P(ex - 8 * s, ey), P(ex + 8 * s, ey)], fill=LIJN, width=lw)
        else:
            r = (10 if verbaasd else 7.5) * s
            d.ellipse([P(ex - r, ey - r), P(ex + r, ey + r)], fill=LIJN)
            d.ellipse([P(ex - r * 0.2, ey - r * 0.7), P(ex + r * 0.35, ey - r * 0.15)], fill=(255, 255, 255))
        if boos: d.line([P(ex - k * 12 * s, ey - 20 * s), P(ex + k * 8 * s, ey - 12 * s)], fill=LIJN, width=lw)
        d.ellipse([P(ex + k * 6 * s - 9 * s, ey + 13 * s), P(ex + k * 6 * s + 9 * s, ey + 21 * s)], fill=WANG)
    if kl.get("bril"):
        for k in (-1, 1):
            ex, ey = hx + k * 22 * s + ox, hy + oy
            if kl["bril"] == "recht": d.rounded_rectangle([P(ex - 18 * s, ey - 11 * s), P(ex + 18 * s, ey + 11 * s)], int(4 * s * SS), outline=LIJN, width=int(3 * s * SS))   # dun rechthoekig (Jensen nu)
            elif kl["bril"] == "groot": d.rounded_rectangle([P(ex - 20 * s, ey - 18 * s), P(ex + 20 * s, ey + 18 * s)], int(9 * s * SS), outline=LIJN, width=lw)          # groot jaren-90 montuur
            else: d.ellipse([P(ex - 17 * s, ey - 15 * s), P(ex + 17 * s, ey + 15 * s)], outline=LIJN, width=lw)
        d.line([P(hx - 5 * s + ox, hy + oy - 2 * s), P(hx + 5 * s + ox, hy + oy - 2 * s)], fill=LIJN, width=lw)
    mx, my = hx + ox * 0.6, hy + 32 * s
    if kl.get("baard"): d.chord([P(hx - hoofd + 2 * s, hy - hoofd * 0.2), P(hx + hoofd - 2 * s, hy + hoofd + 14 * s)], 0, 180, fill=kl["haar"], outline=LIJN, width=lw)
    if viseem is None and LIPSYNC is not None and mond > 0.05: viseem = LIPSYNC.viseem(t)   # wie praat krijgt vanzelf lip sync
    if viseem is not None:                                                 # 27 nov: lip sync, mondvorm per klank (tools/lipsync.py)
        ow = int(3 * s * SS); g = 0.75 + 0.5 * min(1.0, mond)
        if viseem == "M": d.line([P(mx - 14 * s, my), P(mx + 14 * s, my)], fill=LIJN, width=int(5 * s * SS))
        elif viseem == "F":
            d.rounded_rectangle([P(mx - 12 * s, my - 4 * s), P(mx + 12 * s, my + 4 * s)], int(3 * s * SS), fill=MONDK, outline=LIJN, width=ow)
            d.rectangle([P(mx - 8 * s, my - 4 * s), P(mx + 8 * s, my)], fill=(250, 250, 250))
        else:
            bw, bh = {"A": (14, 23), "E": (18, 10), "O": (11, 16), "U": (7, 9), "L": (13, 13)}[viseem]; bh *= g        # iets groter: ook op een telefoon zichtbaar
            d.ellipse([P(mx - bw * s, my - bh / 2 * s), P(mx + bw * s, my + bh / 2 * s)], fill=MONDK, outline=LIJN, width=ow)
            if viseem in ("A", "E"): d.chord([P(mx - bw * 0.8 * s, my - bh / 2 * s + 2 * s), P(mx + bw * 0.8 * s, my - bh / 2 * s + 9 * s)], 0, 180, fill=(250, 250, 250))
            if viseem in ("A", "L"): d.chord([P(mx - bw * 0.6 * s, my + bh / 2 * s - 8 * s), P(mx + bw * 0.6 * s, my + bh / 2 * s - 1 * s)], 180, 360, fill=(230, 110, 120))
    elif mond > 0.08:
        mh = (5 + 14 * mond) * s
        d.ellipse([P(mx - 11 * s, my - mh / 2), P(mx + 11 * s, my + mh / 2)], fill=MONDK, outline=LIJN, width=int(3 * s * SS))
    elif verbaasd: d.ellipse([P(mx - 6 * s, my - 6 * s), P(mx + 6 * s, my + 6 * s)], fill=MONDK, outline=LIJN, width=int(3 * s * SS))
    elif boos: d.arc([P(mx - 12 * s, my + 2 * s), P(mx + 12 * s, my + 16 * s)], 200, 340, fill=LIJN, width=lw)
    else: d.arc([P(mx - 12 * s, my - 8 * s), P(mx + 12 * s, my + 6 * s)], 20, 160, fill=LIJN, width=lw)
    if na_hoofd:                                                           # 24 nov: rechterarm vóór het gezicht (denken / facepalm)
        ledemaat(d, x + 44 * s, sch, rechts, 82 * s, 22 * s, kl["shirt"] if not kl.get("robot") else (165, 175, 190), (12 * s, HUID if not kl.get("robot") else (120, 130, 148)))
        if gebaar == "hoofdhanden": ledemaat(d, x - 44 * s, sch, links, 82 * s, 22 * s, kl["shirt"], (12 * s, HUID))
    if gebaar == "duim":                                                   # 24 nov: duim omhoog op de hand
        ux = x + 44 * s + math.sin(math.radians(rechts)) * 82 * s; uy = sch + math.cos(math.radians(rechts)) * 82 * s
        d.ellipse([P(ux - 15 * s, uy - 15 * s), P(ux + 15 * s, uy + 15 * s)], fill=LIJN); d.ellipse([P(ux - 12 * s, uy - 12 * s), P(ux + 12 * s, uy + 12 * s)], fill=HUID)   # vuist
        d.rounded_rectangle([P(ux - 16 * s, uy - 30 * s), P(ux - 3 * s, uy - 4 * s)], int(7 * s * SS), fill=HUID, outline=LIJN, width=int(3 * s * SS))   # brede duim aan de zijkant
    return hx, hy - hoofd - (14 * s if kl.get("koptelefoon") or kap == "krul" else 0)

# ---------- scènes ----------
# per scène: achtergrond, poppetjes, labels, kopteksten. Poppetje: dict(n, x, s, [loop=(t0,t1,x0,x1)], kijk, gebaar=[(t0,t1,naam)], verbaasd=t)
def Zs(i, d=-0.12): return Z[i][0] + d
Y = 1460
SC = [
 dict(t=0, bg="keuken", pop=[dict(n="dad", x=720, s=1.9, kijk=lambda t: -0.8 if t > kw(1, "dad") + 0.6 else 0.3, gebaar=[(kw(3, "morning"), Z[3][1], "zwaai")]),
                              dict(n="you", x=300, s=1.9, loop=(kw(0, "walk", -0.2), kw(0, "kitchen", 0.5), -200, 300), kijk=lambda t: 1.0 if t > kw(1, "dad") else 0.4, verbaasd=kw(1, "glowing") + 0.3)],
      lab=[("dad", kw(1, "glowing"), kw(2, "$64"), 64000, "groen", False)]),
 dict(t=Zs(4), bg="keuken", pop=[dict(n="dad", x=540, s=1.75, kijk=lambda t: 1.0, gebaar=[(Z[5][0], Z[6][1], "schouders")]),
                                 dict(n="you", x=215, s=1.75, kijk=lambda t: 1.0, verbaasd=0),
                                 dict(n="mom", x=850, s=1.75, loop=(Zs(4, 0.1), kw(4, "in", 0.4), 1250, 850), kijk=lambda t: -0.8)],
      lab=[("dad", 0, 0, 64000, "groen", False), ("mom", kw(4, "91", -0.3), kw(4, "91", -0.1), 91000, "groen", False)]),
 dict(t=Zs(7), bg="keuken", pop=[dict(n="you", x=260, s=1.9, kijk=lambda t: 1.0),
                                 dict(n="sis", x=680, s=1.9, kijk=lambda t: -1.0, boos=Z[8][0] - 0.2, gebaar=[(Z[8][0], Z[8][1] + 0.3, "wijslinks"), (Z[8][1] - 0.6, Z[8][1] + 0.3, "stamp")])],
      lab=[("sis", kw(7, "$260", -0.3), kw(7, "$260", -0.1), 260, "groen", False)]),
 dict(t=Zs(9), bg="nacht", pop=[dict(n="you", x=540, s=2.3, kijk=lambda t: 0.0, verbaasd=0)],
      kop=[(kw(9, "what"), "WHAT IF YOU COULD SEE", 540, 330, 74, "wit"), (kw(9, "much"), "HOW MUCH", 540, 430, 96, "geel"), (kw(9, "much", 0.3), "EVERYONE EARNS?", 540, 535, 80, "geel")],
      zweef=True),
 dict(t=Zs(10), bg="klas", pop=[dict(n="you", x=760, s=1.9, kijk=lambda t: -1.0, gebaar=[(kw(10, "rules"), Z[10][1], "wijslinks")])],
      kop=[(kw(10, "rules"), "RULE 1:", 330, 330, 70, "wit"), (kw(10, "number"), "PAY PER YEAR", 330, 420, 64, "wit")]),
 dict(t=Zs(11), bg="badkamer", spiegel=(276, 266, 788, 658), verbaasd=kw(11, "mirror"),
      pop=[dict(n="you", x=840, s=1.85, kijk=lambda t: -1.0 if t < kw(11, "mirror") else -0.3, verbaasd=kw(11, "mirror"))],
      lab=[("you", kw(11, "except"), 0, "NO NUMBER", "grijs", False)], kop=[(kw(11, "except"), "RULE 2: NOT ON YOU", 540, 150, 68, "geel")]),
 dict(t=Zs(12), bg="bus", pop=[dict(n="you", x=540, s=2.1, loop=(Zs(12, 0.1), Z[12][1], 380, 540), kijk=lambda t: math.sin(t * 2.5))]),
 dict(t=Zs(13), bg="busvoor", pop=[dict(n="driver", x=420, s=1.9, kijk=lambda t: 0.8, gebaar=[(kw(13, "driver"), kw(13, "driver", 1.2), "zwaai")])],
      lab=[("driver", kw(13, "48", -0.3), kw(13, "48", -0.1), 48000, "groen", False)]),
 dict(t=Zs(14), bg="bus", pop=[dict(n="rich", x=640, s=1.9, kijk=lambda t: 0.0), dict(n="you", x=230, s=1.6, kijk=lambda t: 1.0, verbaasd=kw(14, "2"))],
      lab=[("rich", kw(14, "2", -0.6), kw(14, "2", -0.4), 2300000, "goud", False)]),
 dict(t=Zs(15), bg="fjord", pop=[], kop=[(kw(15, "norway"), "NORWAY", 540, 330, 120, "wit")]),
 dict(t=Zs(16), bg="bureau", pop=[], kop=[(kw(16, "public"), "PUBLIC", 540, 330, 120, "rood"), (kw(16, "anyone"), "ANYONE CAN LOOK", 540, 1250, 64, "wit")]),
 dict(t=Zs(17), bg="klas", pop=[dict(n="teach", x=760, s=1.9, kijk=lambda t: -0.8, gebaar=[(Z[17][0], Z[17][1], "wijslinks")])],
      lab=[("teach", kw(17, "52", -0.3), kw(17, "52", -0.1), 52000, "groen", False)]),
 dict(t=Zs(18), bg="gang", pop=[dict(n="boss", x=0, s=1.9, loop=(Zs(18, 0.0), Z[18][1] + 0.3, 200, 760), kijk=lambda t: 1.0)],
      lab=[("boss", kw(18, "140", -0.3), kw(18, "140", -0.1), 140000, "groen", False)]),
 dict(t=Zs(19), bg="klas", pop=[dict(n="teach", x=760, s=1.9, kijk=lambda t: -1.0, boos=kw(20, "eyes", -0.2), gebaar=[(Z[20][0], Z[20][1] + 0.2, "wijslinks")]),
                                dict(n="you", x=260, s=1.75, kijk=lambda t: 1.0)],
      lab=[("teach", 0, 0, 52000, "groen", False)], kop=[(kw(19, "both"), "$52,000  vs  $140,000", 540, 260, 64, "groen")]),
 dict(t=Zs(21), bg="schoolplein", pop=[dict(n="fdad", x=800, s=1.9, kijk=lambda t: -0.8, gebaar=[(kw(21, "picks"), Z[21][1] + 0.6, "zwaai")]),
                                      dict(n="friend", x=0, s=1.7, loop=(kw(21, "best"), Z[21][1], 280, 600), kijk=lambda t: 1.0),
                                      dict(n="you", x=170, s=1.7, kijk=lambda t: 1.0)]),
 dict(t=Zs(22), bg="schoolplein", pop=[dict(n="fdad", x=540, s=2.6, y=1620, kijk=lambda t: 0.0)],
      lab=[("fdad", kw(22, "zero", -0.3), 0, "$0", "rood", True)]),
]
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(f"afbeeldingen/{n}.png").convert("RGB").resize((W, H))
    return BG[n]

FB, FS = "C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/segoeuib.ttf"
fonts = {}
def font(p, m):
    if (p, m) not in fonts: fonts[p, m] = ImageFont.truetype(p, m)
    return fonts[p, m]
KL = {"groen": (60, 230, 120), "goud": (255, 205, 60), "rood": (240, 70, 60), "grijs": (180, 180, 190), "wit": (255, 255, 255), "geel": (255, 214, 64)}
def label(img, s, x, y, kl, sch, alpha=1.0):
    f = font(FB, int(60 * sch)); b = ImageDraw.Draw(img).textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    box = (x - w / 2 - 28, y - h / 2 - 20, x + w / 2 + 28, y + h / 2 + 22)
    d.rounded_rectangle(box, 26, fill=kl + (int(110 * alpha),)); g = laag.filter(ImageFilter.GaussianBlur(16)); d2 = ImageDraw.Draw(g)
    d2.rounded_rectangle(box, 26, fill=(15, 25, 20, int(235 * alpha)), outline=kl + (int(255 * alpha),), width=5)
    d2.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=kl + (int(255 * alpha),)); img.paste(g, (0, 0), g)
def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
NAAM = {"DAD": "DAD", "SIS": "SISTER", "TEACH": "TEACHER"}
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = font(FS, 58); d = ImageDraw.Draw(img)
    stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1620
    if Z[i][4] in NAAM:
        fn = font(FB, 30); n = NAAM[Z[i][4]]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 52, W / 2 + nb / 2 + 14, y - 12), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 50), n, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; t0 = sc["t"]
    img = bg(sc["bg"]).copy()
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    koppen = {}
    for p in sc["pop"]:
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]; f = ease((t - a) / max(0.1, b - a)) if t > a else 0; x = x0 + (x1 - x0) * f
            if a < t < b: loop = (t - a) * 2.2
        geb = next((g for a, b, g in p.get("gebaar", []) if a <= t <= b), None)
        sp = [i for i, z in enumerate(Z) if SPREKER.get(z[4]) == p["n"]]
        koppen[p["n"]] = poppetje(d, p["n"], x, p.get("y", Y), p["s"], t, loop=loop, kijk=p["kijk"](t), mond=luid(t, sp),
                                  knipper=(t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13, verbaasd=("verbaasd" in p and t >= p["verbaasd"]),
                                  gebaar=geb, boos=("boos" in p and t >= p["boos"]))
    laag = laag.resize((W, H), Image.LANCZOS)
    # 23 nov (eigenaar): geen effect bij scènewissel, gewoon knippen
    if sc.get("spiegel"):                                        # spiegelbeeld van de jongen (zonder getal erboven)
        x0, y0, x1, y1 = sc["spiegel"]
        sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); poppetje(ImageDraw.Draw(sl), "you", (x0 + x1) / 2, 860, 1.5, t, kijk=0.8,
                                                                          knipper=(t % 3.4) < 0.13, verbaasd=t >= sc.get("verbaasd", 1e9))
        sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1))
        glas = img.crop((x0, y0, x1, y1)).convert("RGBA"); glas.alpha_composite(sl)
        img.paste(Image.blend(glas.convert("RGB"), img.crop((x0, y0, x1, y1)), 0.25), (x0, y0))
    img.paste(laag, (0, 0), laag)
    if sc.get("zweef"):                                          # titelbeeld: zwevende ?-getallen om de jongen
        for j, (zx, zy) in enumerate([(200, 760), (880, 720), (160, 1060), (920, 1010), (540, 640)]):
            if t > t0 + 0.25 * j: label(img, "$???", zx, zy + 12 * math.sin(t * 2 + j), KL["groen"], pop((t - t0 - 0.25 * j) / 0.3), 0.85)
    for n, st, telstart, v, kl, kn in sc.get("lab", []):
        st = st or t0
        if t < st or n not in koppen: continue
        hx, hy = koppen[n]
        if isinstance(v, str): s = v
        else:
            ts = telstart or st
            s = (f"${round(v * ease((t - ts) / 0.8), 0 if v < 1000 else (-2 if v < 1e6 else -4)):,.0f}" if t > ts else "$???") if telstart else f"${v:,.0f}"
        a = 1.0 if not kn else (0.3 + 0.7 * (math.sin((t - st) * 9) > 0))
        label(img, s, hx, hy - 70, KL[kl], pop((t - st) / 0.3), a)
    for st, s, x, y, m, kl in sc.get("kop", []):
        if t >= st: kop(img, s, x, y, m, KL[kl], pop((t - st) / 0.3))
    ondertitel(img, t)
    return img

if __name__ == "__main__":
    import sys
    if "--plaat" in sys.argv:                                    # controle: één beeld per zin
        ims = [frame(min(EIND - 0.6, z[0] + 0.75 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 8, 480 * 3)); [pl.paste(im, (270 * (i % 8), 480 * (i // 8))) for i, im in enumerate(ims)]
        pl.save("plaat-short.jpg", quality=85); print("plaat-short.jpg"); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", SRC + "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "whatif-short.mp4"], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("KLAAR whatif-short.mp4", round(EIND, 1), "s")
