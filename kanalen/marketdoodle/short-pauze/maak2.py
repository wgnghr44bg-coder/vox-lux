"""Short 'What If You Could Pause Time?' (23 nov) — zoals de eerste Short: staand 1080x1920, poppetjes uit code,
eigen stem verteller, personages eigen stem, ondertitels geel woord, geen muziek, geen effect bij scènewissel.
Bevroren = iedereen behalve jij staat stil (niet knipperen, mond dicht) + licht blauwe waas; 'PAUSED' bovenin.
Gebruik: python maak2.py [--plaat]  -> short-pauze-v2.mp4
v2 (23 nov, eigenaar: "poppetje kijkt alleen links-rechts, ik zie die knop nergens, meer laten zien zoals een film"):
knop in beeld + indrukken, jij loopt naar dingen toe, juf met bevroren tekstballon, antwoorden/koekje/toets/kam als voorwerpen."""
import json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)

W, H, FPS, SS = 1080, 1920, 30, ps.SS
ps.C.update({"kid1": dict(broek=(60, 60, 80), shirt=(220, 80, 70), haar=(150, 90, 50), kapsel="kort", groot=0.92),
             "kid2": dict(broek=(70, 90, 70), shirt=(80, 190, 170), haar=(40, 30, 25), kapsel="paard", groot=0.9)})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.3
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def luid(t):                                             # alleen jij praat (YOU)
    if not any(Z[i][0] <= t <= Z[i][1] and Z[i][4] == "YOU" for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
PAUZE = kw(1, "press", 0.2)                              # vanaf hier staat de wereld stil
def Zs(i): return Z[i][0] - 0.1
BGDIR = HIER.parent / "proef-pop-short" / "afbeeldingen"
BG = {}
def bg(n):
    if n not in BG:
        p = HIER / "afbeeldingen" / f"{n}.png"
        BG[n] = Image.open(p if p.exists() else BGDIR / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
Y = 1460
# scènes: bevroren poppetjes (n, x, s, kijk, gebaar, mondopen) + jij (x, s) + kopteksten + extra
KLAS = [("teach", 900, 1.55, -0.8, "wijslinks", True), ("kid1", 330, 1.45, 0.8, "zwaai", False), ("kid2", 500, 1.45, -0.8, None, True)]
KLASSTOP = kw(2, "stops", 0.05)                          # in de klas staat alles stil op het woord "stops"
TSTART = Zs(2) - 2.6                                     # de juf was al aan het praten (tekst loopt door tot KLASSTOP)
SC = [
 dict(t=0, bg="gang", vast=[], jij=dict(x=540, s=2.2, loop=(kw(0, "hallway", -1.0), kw(0, "hallway", 0.6), 200, 540), kijk=0.0,
      gebaar=[(kw(1, "button", -0.4), 1e9, "vast")]), kop=[(0, "8:59", 540, 260, 130, "wit")],
      knop=(kw(1, "button", -0.3), kw(1, "press", 0.0), 1e9, False)),                        # eigenaar: knop in de gang, waar het verhaal zegt
 dict(t=Zs(2), bg="klas", vast=KLAS, live=True, jij=None),                                    # juf praat, bal vliegt, op "stops" bevriest alles
 dict(t=Zs(3), bg="gang", vast=[("kid1", 250, 1.8, 0.4, "zwaai", True), ("kid2", 960, 1.8, -0.4, None, False)], jij=dict(x=540, s=2.0, kijk=0.0)),
 dict(t=Zs(4), bg="nacht", vast=[], jij=dict(x=540, s=2.3), kop=[(kw(4, "what"), "WHAT IF YOU COULD", 540, 330, 82, "wit"), (kw(4, "pause"), "PAUSE TIME?", 540, 450, 110, "geel")]),
 dict(t=Zs(5), bg="klas", vast=KLAS, live=True,
      jij=dict(x=110, s=1.6, pad=[(kw(6, "copy", -0.9), 110), (kw(6, "copy", 0.2), 700), (kw(6, "cookie", -1.0), 700), (kw(6, "cookie", 0.0), 170)],
               kijkpad=[(0, 0.9), (kw(6, "cookie", -1.0), -0.9), (kw(6, "cookie", 0.05), 0.9)],
               gebaar=[(kw(6, "copy", 0.2), kw(6, "hair", -0.3), "vast"), (kw(6, "hair", -0.2), kw(6, "cookie", -1.0), "haar"), (kw(6, "cookie", 0.05), 1e9, "vast")]),
      dingen=[(kw(6, "copy", 0.2), kw(6, "hair", -0.3), "toets", 70), (kw(6, "hair", -0.2), kw(6, "cookie", -1.0), "kam", 165), (kw(6, "cookie", 0.05), 1e9, "koekje", 70)]),
 dict(t=Zs(7), bg="klas", vast=[("teach", 900, 1.55, -0.8, "wijslinks", False), ("kid1", 600, 1.45, -0.6, None, False), ("kid2", 760, 1.45, 0.6, None, False)], bord="TEST TODAY",   # eigenaar 23 nov: toets is op school, niet thuis
      jij=dict(x=200, s=1.6, kijk=0.6, gebaar=[(kw(7, "study", -0.4), 1e9, "vast")]),
      dingen=[(kw(7, "study", -0.4), 1e9, "boek", 70)], klik=[kw(7, "10", -0.4), kw(7, "hour", -0.4)]),
 dict(t=Zs(8), bg="ruimte", vast=[], jij=None, kop=[], bron="Source: GPS.gov, relativity corrections for GPS satellite clocks", bront=kw(8, "38", -0.1)),
 dict(t=Zs(10), bg="badkamer", vast=[], jij=dict(x=830, s=1.85), spiegel=(276, 266, 788, 658), grijs=kw(10, "gray", -0.2)),
 dict(t=Zs(13), bg="gang", vast=[("kid1", 250, 1.8, 0.4, "zwaai", True), ("kid2", 960, 1.8, -0.4, None, False)], jij=dict(x=540, s=2.0, kijk=0.0, gebaar=[(kw(13, "press", -0.6), 1e9, "vast")]),
      knop=(kw(13, "press", -0.7), kw(13, "button", 0.0), 1e9, True)),
]
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
def kop(img, s, x, y, m, kl, sch): ps.kop(img, s, x, y, m, kl, sch)
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = font(FS, 58); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1].upper() + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1620
    if Z[i][4] == "YOU":
        fn = font(FB, 30); nb = d.textlength("YOU", font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 52, W / 2 + nb / 2 + 14, y - 12), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 50), "YOU", font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)
def pauzeknop(img, rood=False):                          # 'PAUSED' bovenin met pauze-teken
    d = ImageDraw.Draw(img); kl = (240, 70, 60) if rood else (255, 255, 255)
    d.rounded_rectangle((330, 60, 750, 160), 30, fill=(20, 25, 45), outline=kl, width=5)
    d.rectangle((370, 85, 390, 135), fill=kl); d.rectangle((405, 85, 425, 135), fill=kl)
    d.text((450, 78), "PAUSED", font=font(FB, 58), fill=kl)

def hand(x, s, hoek=70):                                 # positie van de rechterhand bij een armhoek (zie pop_short.poppetje)
    heup = Y - 78 * s - 14 * s; sch = heup - 105 * s + 22 * s
    return x + 44 * s + 82 * s * math.sin(math.radians(hoek)), sch + 82 * s * math.cos(math.radians(hoek))
def knop(img, t, inn, druk, uit, kapot, cx=800, cy=900, R0=120):
    """grote rode knop in beeld (hand), indrukken = knop zakt in + ring; kapot = indrukken maar er gebeurt niets"""
    if not (inn <= t < uit): return
    d = ImageDraw.Draw(img); s = ps.pop((t - inn) / 0.35); R = R0 * s
    d.rounded_rectangle((cx - R * 1.25, cy - R * 0.2, cx + R * 1.25, cy + R * 0.9), int(30 * s), fill=(70, 75, 90), outline=(45, 38, 40), width=8)
    ing = 0.0
    if t >= druk: ing = max(0.0, 1 - (t - druk) / 0.35) if not kapot else min(1.0, (t - druk) / 0.15) * (1 if (t - druk) < 1.2 else 0.0)
    hoog = R * (0.55 - 0.4 * ing); kl = (230, 60, 55) if not (kapot and t >= druk + 0.8) else (150, 150, 155)
    d.ellipse((cx - R, cy - hoog - R * 0.45, cx + R, cy - hoog + R * 0.45), fill=kl, outline=(45, 38, 40), width=8)
    d.rectangle((cx - R, cy - hoog, cx + R, cy), fill=kl); d.line((cx - R, cy - hoog, cx - R, cy), fill=(45, 38, 40), width=8); d.line((cx + R, cy - hoog, cx + R, cy), fill=(45, 38, 40), width=8)
    d.ellipse((cx - R, cy - R * 0.45, cx + R, cy + R * 0.45), outline=(45, 38, 40), width=8)
    if t >= druk and not kapot and t < druk + 0.7:
        a = (t - druk) / 0.7; rr = 60 + 900 * a
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255), width=max(2, int(18 * (1 - a))))
    if kapot and t >= druk + 0.8: kop(img, "?!", cx, cy - R * 2.6, 90, KL["rood"], 1.0)
ZIN = "So the answer is twelve, because we multiply"
def ballon(img, t):
    n = max(1, int((min(t, KLASSTOP) - TSTART) * 8.5)); tekst = ZIN[:n] + ("-" if t >= KLASSTOP else "")
    d = ImageDraw.Draw(img); f = font(FB, 40); b = max(d.textlength(tekst, font=f), 120)
    x0, y0 = 1040 - b - 40, 830
    d.rounded_rectangle((x0, y0, 1050, y0 + 90), 30, fill=(255, 255, 255), outline=(45, 38, 40), width=6)
    d.polygon([(960, y0 + 88), (1000, y0 + 88), (990, y0 + 140)], fill=(255, 255, 255)); d.line([(960, y0 + 90), (990, y0 + 140), (1000, y0 + 90)], fill=(45, 38, 40), width=6)
    d.text((x0 + 20, y0 + 22), tekst, font=f, fill=(45, 38, 40))
def ding(img, soort, x, y, t0, t, klein=True):
    d = ImageDraw.Draw(img); s = ps.pop((t - t0) / 0.3) * (0.62 if klein else 0.8); L = (45, 38, 40)
    if soort in ("toets", "toets2"):
        w, h = 150 * s, 190 * s; d.rectangle((x - w / 2, y - h / 2, x + w / 2, y + h / 2), fill=(255, 255, 250), outline=L, width=6)
        for k in range(4): d.line((x - w / 2 + 18, y - h / 2 + 30 + k * 36, x + w / 4, y - h / 2 + 30 + k * 36), fill=(150, 150, 160), width=5)
        d.text((x + w / 2 - 70 * s, y + h / 2 - 80 * s), "A+", font=font(FB, int(60 * s)), fill=(220, 50, 50))
    elif soort == "boek":                                 # open schoolboek
        w, h = 170 * s, 120 * s
        d.polygon([(x - w, y - h / 2), (x, y - h / 2 + 12 * s), (x, y + h / 2 + 12 * s), (x - w, y + h / 2)], fill=(250, 250, 245), outline=L)
        d.polygon([(x + w, y - h / 2), (x, y - h / 2 + 12 * s), (x, y + h / 2 + 12 * s), (x + w, y + h / 2)], fill=(250, 250, 245), outline=L)
        d.line((x, y - h / 2 + 12 * s, x, y + h / 2 + 12 * s), fill=L, width=4)
        for k in range(4):
            yy = y - h / 2 + 30 * s + k * 22 * s
            d.line((x - w + 18 * s, yy, x - 18 * s, yy + 4 * s), fill=(150, 150, 160), width=4); d.line((x + 18 * s, yy + 4 * s, x + w - 18 * s, yy), fill=(150, 150, 160), width=4)
        d.rectangle((x - w - 6 * s, y + h / 2 - 2 * s, x + w + 6 * s, y + h / 2 + 18 * s), fill=(70, 130, 220), outline=L)
    elif soort == "kam":
        d.rounded_rectangle((x - 90 * s, y - 18 * s, x + 90 * s, y + 18 * s), 8, fill=(120, 80, 220), outline=L, width=5)
        for k in range(12): d.line((x - 80 * s + k * 14 * s, y + 18 * s, x - 80 * s + k * 14 * s, y + 55 * s), fill=(120, 80, 220), width=int(6 * s))
    elif soort == "koekje":
        hap = t > t0 + 0.7
        d.ellipse((x - 60 * s, y - 60 * s, x + 60 * s, y + 60 * s), fill=(205, 150, 80), outline=L, width=6)
        for a, b in ((-25, -15), (15, -25), (-5, 20), (28, 15)): d.ellipse((x + a * s - 8, y + b * s - 8, x + a * s + 8, y + b * s + 8), fill=(80, 50, 30))
        if hap: d.ellipse((x + 25 * s, y - 75 * s, x + 95 * s, y - 5 * s), fill=(0, 0, 0, 0)) if False else None
        if hap:
            bgk = img.getpixel((int(min(1079, x + 120)), int(y)))
            d.ellipse((x + 22 * s, y - 72 * s, x + 92 * s, y - 2 * s), fill=bgk)
def interp(pad, t):
    if t <= pad[0][0]: return pad[0][1], False
    for (a, xa), (b, xb) in zip(pad, pad[1:]):
        if a <= t <= b: return xa + (xb - xa) * ps.ease((t - a) / max(0.05, b - a)), xa != xb
    return pad[-1][1], False

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]
    img = bg(sc["bg"]).copy()
    bevroren = t >= PAUZE and sc["bg"] != "ruimte" and not (sc.get("live") and t < KLASSTOP)
    if sc.get("spiegel"):                                 # jouw spiegelbeeld (met grijze haar)
        x0, y0, x1, y1 = sc["spiegel"]
        sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); ds = ImageDraw.Draw(sl)
        top = ps.poppetje(ds, "you", (x0 + x1) / 2, 860, 1.5, t, kijk=0.8, verbaasd=t >= sc["grijs"], mond=luid(t))
        if t >= sc["grijs"]: ds.line([(top[0] * SS - 10 * SS, (top[1] + 6) * SS), (top[0] * SS + 25 * SS, (top[1] + 28) * SS)], fill=(220, 220, 225), width=8 * SS)
        sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1))
        glas = img.crop((x0, y0, x1, y1)).convert("RGBA"); glas.alpha_composite(sl)
        img.paste(Image.blend(glas.convert("RGB"), img.crop((x0, y0, x1, y1)), 0.25), (x0, y0))
    if sc.get("bord"):
        db = ImageDraw.Draw(img); fb = font(ps.FS, 96); bb = db.textlength(sc["bord"], font=fb)
        db.text((540 - bb / 2, 330), sc["bord"], font=fb, fill=(235, 240, 235))
    vast = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dv = ImageDraw.Draw(vast)
    for n, x, s, kijk, geb, open_ in sc["vast"]:
        tt = min(t, KLASSTOP) if sc.get("live") else (0.0 if bevroren else t)
        mond = (abs(math.sin(tt * 9)) if n == "teach" else 0.0) if sc.get("live") else (0.5 if open_ else 0.0)
        ps.poppetje(dv, n, x, Y, s, tt, kijk=kijk, mond=mond, knipper=(not bevroren and (t % 3.1) < 0.12), gebaar=geb)
    if sc.get("live"):                                     # bal vliegt heen en weer tussen de kinderen, stopt bij PAUZE
        u = ((min(t, KLASSTOP) - TSTART) / 1.4) % 2; u = u if u <= 1 else 2 - u
        bx, by = 340 + 140 * u, 1010 - 200 * math.sin(math.pi * u); dv.ellipse([((bx - 34) * SS, (by - 34) * SS), ((bx + 34) * SS, (by + 34) * SS)], fill=(230, 80, 60), outline=(45, 38, 40), width=5 * SS)
    vast = vast.resize((W, H), Image.LANCZOS); img.paste(vast, (0, 0), vast)
    if bevroren: img = Image.blend(img, Image.new("RGB", (W, H), (120, 160, 255)), 0.14)      # stilstaande wereld: lichte blauwe waas
    if sc.get("jij"):
        j = sc["jij"]; x = j["x"]; loop = None
        if "pad" in j:
            x, beweegt = interp(j["pad"], t)
            if beweegt: loop = t * 2.4
        if "loop" in j:
            a, b, x0, x1 = j["loop"]; f = ps.ease((t - a) / max(0.1, b - a)) if t > a else 0; x = x0 + (x1 - x0) * f
            if a < t < b: loop = (t - a) * 2.4
        laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
        kijk = j.get("kijk", math.sin(t * 1.3) * 0.7)
        if "kijkpad" in j: kijk = [k for st, k in j["kijkpad"] if t >= st][-1]
        geb = next((g for a, b, g in j.get("gebaar", []) if a <= t < b), None)
        top = ps.poppetje(dl, "you", x, Y, j["s"], t, loop=loop, kijk=kijk, mond=luid(t), gebaar=geb,
                          knipper=(t % 3.4) < 0.13, verbaasd=sc["bg"] in ("badkamer",) or (sc["bg"] == "gang" and k > 0) or sc["bg"] == "nacht")
        if sc.get("grijs") and t >= sc["grijs"]:
            dl.line([(top[0] * SS - 10 * SS, (top[1] + 6) * SS), (top[0] * SS + 30 * SS, (top[1] + 34) * SS)], fill=(220, 220, 225), width=9 * SS)
        laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    if sc.get("live"): ballon(img, t)
    for a, b, soort, _ in sc.get("dingen", []):
        if a <= t < b:
            jx = interp(sc["jij"]["pad"], t)[0] if "pad" in sc.get("jij", {}) else sc["jij"]["x"]
            hx, hy = hand(jx, sc["jij"]["s"], _)
            ding(img, soort, hx + (10 if soort != "kam" else -5) - (60 if soort == "boek" else 0), hy - (10 if soort != "kam" else 40), a, t, klein=soort != "boek")
    for kt in sc.get("klik", []):
        if kt <= t < kt + 0.6:
            a = (t - kt) / 0.6; rr = 80 + 500 * a; hx, hy = hand(sc["jij"]["x"], sc["jij"]["s"]); ImageDraw.Draw(img).ellipse((hx - rr, hy - rr, hx + rr, hy + rr), outline=(255, 255, 255), width=max(2, int(14 * (1 - a))))
    if k == len(SC) - 1 and t >= kw(14, "clock", -0.1):
        dk = ImageDraw.Draw(img); cx, cy, R = 540, 560, 120 * ps.pop((t - kw(14, "clock", -0.1)) / 0.3)
        dk.ellipse((cx - R - 10, cy - R - 10, cx + R + 10, cy + R + 10), fill=(45, 38, 40)); dk.ellipse((cx - R, cy - R, cx + R, cy + R), fill=(255, 255, 250))
        for u in range(12):
            a_ = math.radians(u * 30); dk.line((cx + math.sin(a_) * R * 0.8, cy - math.cos(a_) * R * 0.8, cx + math.sin(a_) * R * 0.92, cy - math.cos(a_) * R * 0.92), fill=(45, 38, 40), width=6)
        sec = int((t - kw(14, "clock")) * 2) if t > kw(14, "clock") else 0; a_ = math.radians(sec * 6)
        dk.line((cx, cy, cx + math.sin(math.radians(60)) * R * 0.5, cy - math.cos(math.radians(60)) * R * 0.5), fill=(45, 38, 40), width=10)
        dk.line((cx, cy, cx + math.sin(a_) * R * 0.85, cy - math.cos(a_) * R * 0.85), fill=(220, 50, 50), width=6); dk.ellipse((cx - 12, cy - 12, cx + 12, cy + 12), fill=(45, 38, 40))
    if sc.get("knop"):
        hx, hy = hand(sc["jij"]["x"], sc["jij"]["s"]); knop(img, t, *sc["knop"], cx=hx + 12, cy=hy - 6, R0=42)
    if bevroren: pauzeknop(img, rood=(k == len(SC) - 1 and t >= kw(14, "nothing")))
    weg = sc.get("kopweg", 1e9)
    for st, s, x, y, m, kl in sc.get("kop", []):
        if st <= t < weg: kop(img, s, x, y + (120 if bevroren and y < 300 else 0), m, KL[kl], ps.pop((t - st) / 0.3))
    for st, s, x, y, m, kl in sc.get("kop2", []):
        if t >= st: kop(img, s, x, y + 120, m, KL[kl], ps.pop((t - st) / 0.3))
    tel = [s for st, s in sc.get("teller", []) if t >= st]
    if tel: kop(img, tel[-1], 540, 215 if sc.get("spiegel") else 330, 56 if sc.get("spiegel") else 72, KL["geel"], 1.0)
    if sc.get("bron") and t >= sc["bront"]: ImageDraw.Draw(img).text((40, 1860), sc["bron"], font=font(FS, 26), fill=(200, 200, 220))
    ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 8, 480 * 2)); [pl.paste(im, (270 * (i % 8), 480 * (i // 8))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat2.jpg", quality=85); print("plaat.jpg"); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "short-pauze-v2.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("KLAAR short-pauze-v2.mp4", round(EIND, 1), "s")
