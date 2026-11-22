"""What If-proef 2 (22 nov): opbouw zoals de grote what-if kanalen (Mirage, The If Lab, What if U click):
scène met 'you' + familie, beeld per zin (± 2-3 s), groen gloeiend getal boven hoofden, ondertitels onderin met
naamlabel bij wie praat en het gesproken woord geel. Geen muziek (eigenaar 22 nov). Bouwt whatif2-proef.mp4."""
import json, math, re, subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 720, 30
Z = json.load(open("zinnen.json", encoding="utf-8"))           # [start, eind, tekst, scene, spreker]
WO = json.load(open("woorden.json", encoding="utf-8"))          # [zin, woord, t0, t1]
_wo = []                                                         # Whisper splitst getallen ("2 .3", "140 ,000"): weer aan elkaar
for w in WO:
    if _wo and _wo[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isdigit(): _wo[-1] = [w[0], _wo[-1][1] + w[1], _wo[-1][2], w[3]]
    else: _wo.append(list(w))
WO = _wo
EIND = Z[-1][1] + 1.4
FB, FS = "C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/segoeuib.ttf"
fonts = {}
def font(p, m):
    if (p, m) not in fonts: fonts[p, m] = ImageFont.truetype(p, m)
    return fonts[p, m]

def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def pop(x): x = max(0.0, min(1.0, x)); return 1 + 0.2 * math.sin(math.pi * x) * (1 - x) if x < 1 else 1.0

# scènes: eerste zin per scene bepaalt de start
SC = []
for z in Z:
    if not SC or SC[-1][1] != z[3]: SC.append([max(0.0, z[0] - 0.12) if SC else 0.0, z[3]])
BEELD = {s: Image.open(f"afbeeldingen/{s}.png").convert("RGB").resize((W, H)) for _, s in SC}

GROEN, GEEL, ROOD, WIT = (60, 230, 120), (255, 214, 64), (240, 70, 60), (255, 255, 255)
# getallen boven hoofden: (scene, start, bedrag, x, y, kleur, knipper)
LAB = [
    ("k3", kw(2, "$64", -0.1), 64000, 820, 45, GROEN, False),
    ("k4", 0, 64000, 300, 40, GROEN, False),
    ("k5", kw(4, "91", -0.1), 91000, 810, 60, GROEN, False),
    ("k6", 0, 64000, 260, 290, GROEN, False),
    ("k6", 0, 91000, 800, 45, GROEN, False),
    ("k7", kw(7, "$5", -0.1), "$5 / WEEK", 760, 80, GROEN, False),
    ("k8", 0, "$5 / WEEK", 500, 60, GROEN, False),
    ("b2", kw(13, "48", -0.1), 48000, 810, 170, GROEN, False),
    ("b3", kw(14, "2", -0.1), 2300000, 680, 60, GEEL, False),
    ("s1", kw(17, "52", -0.1), 52000, 910, 70, GROEN, False),
    ("s2", kw(18, "140", -0.1), 140000, 760, 85, GROEN, False),
    ("s3", 0, "$52,000  vs  $140,000", 640, 60, GROEN, False),
    ("e2", kw(22, "zero", -0.1), 0, 940, 120, ROOD, True),
]
# losse kopteksten: (scene, start, tekst, x, y, maat, kleur)
KOP = [
    ("t1", kw(9, "what"), "WHAT IF YOU COULD SEE", 640, 470, 62, WIT),
    ("t1", kw(9, "much"), "HOW MUCH EVERYONE EARNS?", 640, 550, 62, GEEL),
    ("r1", kw(10, "rules"), "RULE 1: PAY PER YEAR", 420, 260, 54, WIT),
    ("r2", kw(11, "except"), "RULE 2: NOT ON YOU", 640, 70, 58, GEEL),
    ("f1", kw(15, "norway"), "NORWAY", 640, 80, 84, WIT),
    ("f2", kw(16, "public"), "PUBLIC", 980, 120, 84, ROOD),
]

def bedrag(v): return v if isinstance(v, str) else f"${v:,.0f}"

def label(img, s, x, y, kleur, sch, alpha=1.0):
    f = font(FB, int(46 * sch)); d0 = ImageDraw.Draw(img)
    b = d0.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    box = (x - w / 2 - 22, y - h / 2 - 16, x + w / 2 + 22, y + h / 2 + 18)
    d.rounded_rectangle(box, 22, fill=kleur + (int(110 * alpha),))
    gloed = laag.filter(ImageFilter.GaussianBlur(14))
    d2 = ImageDraw.Draw(gloed)
    d2.rounded_rectangle(box, 22, fill=(15, 25, 20, int(235 * alpha)), outline=kleur + (int(255 * alpha),), width=4)
    d2.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=kleur + (int(255 * alpha),))
    img.paste(gloed, (0, 0), gloed)

def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(3, int(m * sch) // 12)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    d.text((x - w / 2, y - h / 2 + 4), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))

NAAM = {"DAD": "DAD", "SIS": "SISTER", "TEACH": "TEACHER"}
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = font(FS, 42); d = ImageDraw.Draw(img)
    # in stukken van max ± 7 woorden; toon het stuk waarin het huidige woord valt
    stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 7 or w[1][-1:] in ".?!": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.15), stukken[-1])
    tekst = [w[1] for w in stuk]
    breed = sum(d.textlength(x + " ", font=f) for x in tekst)
    x = W / 2 - breed / 2; y = 650
    sp = Z[i][4]
    if sp in NAAM:
        fn = font(FB, 22); n = NAAM[sp]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 10, y - 40, W / 2 + nb / 2 + 10, y - 10), 8, fill=(120, 80, 220))
        d.text((W / 2 - nb / 2, y - 38), n, font=fn, fill=WIT)
    for w in stuk:
        kl = GEEL if w[2] <= t <= w[3] + 0.05 else WIT
        d.text((x, y), w[1], font=f, fill=kl, stroke_width=4, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i][0] <= t)
    t0, s = SC[k]; t1 = SC[k + 1][0] if k + 1 < len(SC) else EIND
    sch = max(1.0, pop((t - t0) / 0.3)) * (1 + 0.025 * (t - t0) / max(1, t1 - t0))
    img = BEELD[s]
    w2, h2 = int(W * sch), int(H * sch)
    img = img.resize((w2, h2), Image.BICUBIC).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H)) if sch > 1.0001 else img.copy()
    for sc, st, v, x, y, kl, kn in LAB:
        if sc != s: continue
        st = st or t0
        if t < st: continue
        tel = v
        if not isinstance(v, str) and v > 0: tel = round(v * ease((t - st) / 0.7), -2 if v < 1e6 else -4)
        a = 1.0 if not kn else (0.35 + 0.65 * (math.sin((t - st) * 9) > 0))
        label(img, bedrag(tel), x, y, kl, pop((t - st) / 0.3), a)
    for sc, st, tx, x, y, m, kl in KOP:
        if sc == s and t >= st: kop(img, tx, x, y, m, kl, pop((t - st) / 0.3))
    ondertitel(img, t)
    if t > EIND - 0.5: img = Image.blend(img, Image.new("RGB", (W, H)), min(1, (t - (EIND - 0.5)) / 0.5))
    return img

p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                      "-c:v", "libx264", "-crf", "19", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                      "whatif2-proef.mp4"], stdin=subprocess.PIPE)
for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
print("KLAAR whatif2-proef.mp4", round(EIND, 1), "s")
