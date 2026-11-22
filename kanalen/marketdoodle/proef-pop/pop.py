"""Proef 'poppetjes met code' (eigenaar 22 nov: geen AI-video, wel bewegen met ffmpeg/code).
Poppetjes worden met code getekend (hoofd, haar, ogen, mond, lijf, armen, benen als losse delen), dus ze blijven altijd
hetzelfde en kunnen lopen, knipperen, kijken en praten (mond volgt het geluid). Achtergrond = ComfyUI (lege keuken).
Stem en tijden uit ../proef-whatif2 (zinnen 0-3). Bouwt pop-proef.mp4."""
import json, math, re, subprocess
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS, SS = 1280, 720, 30, 2                     # SS = supersampling voor gladde lijnen
SRC = "../proef-whatif2/"
Z = json.load(open(SRC + "zinnen.json", encoding="utf-8"))[:4]
WO = []
for w in json.load(open(SRC + "woorden.json", encoding="utf-8")):   # Whisper splitst getallen ("7 .15"): weer aan elkaar
    if w[0] >= 4: continue
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isdigit(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[3][1] + 0.9
a, SR = sf.read(SRC + "stem.wav", dtype="float32"); a = a[:int(EIND * SR)]
sf.write("stem.wav", a, SR)
def kw(zin, woord):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0
    print("LET OP", zin, woord); return Z[zin][0]
# mond van papa: volume van zijn zin (zin 3) per beeldje
def luid(t):
    if not (Z[3][0] <= t <= Z[3][1]): return 0.0
    s = a[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

BG = Image.open("afbeeldingen/keuken.png").convert("RGB").resize((W, H))
LIJN, HUID, WANG = (45, 38, 40), (255, 222, 196), (255, 170, 160)

def P(x, y): return (x * SS, y * SS)
def ledemaat(d, x0, y0, hoek, lengte, dik, kleur, eind=None):
    """lijn vanaf (x0,y0) onder hoek (graden, 0 = recht naar beneden); geeft eindpunt"""
    x1 = x0 + math.sin(math.radians(hoek)) * lengte; y1 = y0 + math.cos(math.radians(hoek)) * lengte
    d.line([P(x0, y0), P(x1, y1)], fill=LIJN, width=int((dik + 6) * SS))
    d.line([P(x0, y0), P(x1, y1)], fill=kleur, width=int(dik * SS))
    for (x, y), r, k in (((x0, y0), (dik + 6) / 2, LIJN), ((x0, y0), dik / 2, kleur)):
        d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=k)
    if eind:
        r, k = eind
        d.ellipse([P(x1 - r - 3, y1 - r - 3), P(x1 + r + 3, y1 + r + 3)], fill=LIJN)
        d.ellipse([P(x1 - r, y1 - r), P(x1 + r, y1 + r)], fill=k)
    return x1, y1

def poppetje(d, x, y, s, kl, t, loop=0.0, kijk=0.0, mond=0.0, knipper=False, bril=False, haar="kort", verbaasd=False):
    """x,y = tussen de voeten op de vloer; s = schaal; loop = fase (0 = stilstaan); kijk = -1 links .. 1 rechts"""
    bob = abs(math.sin(loop * math.pi)) * 6 * s if loop else math.sin(t * 2.2) * 1.5 * s   # wippen bij lopen / ademen
    been, lijf, hoofd = 78 * s, 105 * s, 60 * s
    heup = y - been - 14 * s + bob * 0.3
    zw = math.sin(loop * math.pi) * 26 if loop else 0
    for kant, h in ((-1, zw), (1, -zw)):                                                      # benen
        ledemaat(d, x + kant * 18 * s, heup, h, been, 26 * s, kl["broek"], (13 * s, LIJN))
    top = heup - lijf - bob
    sch = top + 22 * s
    d.rounded_rectangle([P(x - 48 * s, top), P(x + 48 * s, heup + 12 * s)], int(26 * s * SS), fill=kl["shirt"], outline=LIJN, width=int(4 * s * SS))
    for kant, h in ((-1, -zw * 0.8), (1, zw * 0.8)):                                          # armen naast het lijf
        ledemaat(d, x + kant * 44 * s, sch, kant * 16 + h, 82 * s, 22 * s, kl["shirt"], (12 * s, HUID))
    if kl.get("koordjes"):
        for k in (-1, 1): d.line([P(x + k * 10 * s, top + 8 * s), P(x + k * 12 * s, top + 40 * s)], fill=LIJN, width=int(3 * s * SS))
    hx, hy = x, top - hoofd * 0.82                                                            # hoofd
    d.ellipse([P(hx - hoofd - 4 * s, hy - hoofd - 4 * s), P(hx + hoofd + 4 * s, hy + hoofd + 4 * s)], fill=LIJN)
    d.ellipse([P(hx - hoofd, hy - hoofd), P(hx + hoofd, hy + hoofd)], fill=HUID)
    if haar == "kort":
        d.chord([P(hx - hoofd - 3 * s, hy - hoofd - 6 * s), P(hx + hoofd + 3 * s, hy + hoofd * 0.6)], 180, 360, fill=kl["haar"], outline=LIJN, width=int(4 * s * SS))
        d.ellipse([P(hx + 5 * s, hy - hoofd - 16 * s), P(hx + 30 * s, hy - hoofd + 4 * s)], fill=kl["haar"], outline=LIJN, width=int(3 * s * SS))
    ox = kijk * 12 * s; oy = 6 * s                                                            # ogen
    for k in (-1, 1):
        ex, ey = hx + k * 22 * s + ox, hy + oy
        if knipper: d.line([P(ex - 8 * s, ey), P(ex + 8 * s, ey)], fill=LIJN, width=int(4 * s * SS))
        else:
            r = (10 if verbaasd else 7.5) * s
            d.ellipse([P(ex - r, ey - r), P(ex + r, ey + r)], fill=LIJN)
            d.ellipse([P(ex - r * 0.2, ey - r * 0.7), P(ex + r * 0.35, ey - r * 0.15)], fill=(255, 255, 255))
        d.ellipse([P(ex + k * 6 * s - 9 * s, ey + 13 * s), P(ex + k * 6 * s + 9 * s, ey + 21 * s)], fill=WANG)
    if bril:
        for k in (-1, 1):
            ex, ey = hx + k * 22 * s + ox, hy + oy
            d.ellipse([P(ex - 17 * s, ey - 15 * s), P(ex + 17 * s, ey + 15 * s)], outline=LIJN, width=int(4 * s * SS))
        d.line([P(hx - 5 * s + ox, hy + oy - 2 * s), P(hx + 5 * s + ox, hy + oy - 2 * s)], fill=LIJN, width=int(4 * s * SS))
    mx, my = hx + ox * 0.6, hy + 32 * s                                                      # mond
    if mond > 0.08:
        mh = (5 + 14 * mond) * s
        d.ellipse([P(mx - 11 * s, my - mh / 2), P(mx + 11 * s, my + mh / 2)], fill=(120, 40, 50), outline=LIJN, width=int(3 * s * SS))
    elif verbaasd: d.ellipse([P(mx - 6 * s, my - 6 * s), P(mx + 6 * s, my + 6 * s)], fill=(120, 40, 50), outline=LIJN, width=int(3 * s * SS))
    else: d.arc([P(mx - 12 * s, my - 8 * s), P(mx + 12 * s, my + 6 * s)], 20, 160, fill=LIJN, width=int(4 * s * SS))
    return hx, hy - hoofd

JONGEN = {"broek": (55, 60, 85), "shirt": (70, 130, 220), "haar": (60, 45, 40), "koordjes": True}
PAPA = {"broek": (90, 80, 70), "shirt": (90, 180, 110), "haar": (120, 80, 50)}
FB, FS = "C:/Windows/Fonts/seguibl.ttf", "C:/Windows/Fonts/segoeuib.ttf"
fonts = {}
def font(p, m):
    if (p, m) not in fonts: fonts[p, m] = ImageFont.truetype(p, m)
    return fonts[p, m]
def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def pop(x): x = max(0.0, min(1.0, x)); return 1 + 0.2 * math.sin(math.pi * x) * (1 - x) if x < 1 else 1.0
GROEN, GEEL, WIT = (60, 230, 120), (255, 214, 64), (255, 255, 255)
def label(img, s, x, y, sch):
    f = font(FB, int(46 * sch)); b = ImageDraw.Draw(img).textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    box = (x - w / 2 - 22, y - h / 2 - 16, x + w / 2 + 22, y + h / 2 + 18)
    d.rounded_rectangle(box, 22, fill=GROEN + (110,)); g = laag.filter(ImageFilter.GaussianBlur(14)); d2 = ImageDraw.Draw(g)
    d2.rounded_rectangle(box, 22, fill=(15, 25, 20, 235), outline=GROEN + (255,), width=4)
    d2.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=GROEN + (255,)); img.paste(g, (0, 0), g)
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]; f = font(FS, 42); d = ImageDraw.Draw(img)
    stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 7 or w[1][-1:] in ".?!": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.15), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 650
    if Z[i][4] == "DAD":
        fn = font(FB, 22); nb = d.textlength("DAD", font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 10, y - 40, W / 2 + nb / 2 + 10, y - 10), 8, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 38), "DAD", font=fn, fill=WIT)
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=GEEL if w[2] <= t <= w[3] + 0.05 else WIT, stroke_width=4, stroke_fill=(0, 0, 0)); x += d.textlength(w[1] + " ", font=f)

T_LOOP0, T_LOOP1 = kw(0, "walk") - 0.2, kw(0, "kitchen") + 0.5      # jongen loopt binnen
T_KIJK = kw(1, "dad")                                                # kijkt naar papa
T_LAB, T_TEL = kw(1, "glowing"), kw(2, "$64")
X0, X1, XP = -150, 420, 880
def frame(t):
    img = BG.copy()
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    knip = lambda off: (t + off) % 3.3 < 0.13
    # papa: staat bij het aanrecht, kijkt eerst naar links (koffie), praat in zin 3
    hp = poppetje(d, XP, 700, 1.5, PAPA, t, kijk=-0.6 if t > T_KIJK + 0.8 else 0.2, mond=luid(t), knipper=knip(1.1), bril=True)
    # jongen
    f = ease((t - T_LOOP0) / (T_LOOP1 - T_LOOP0)) if t > T_LOOP0 else 0
    loopt = T_LOOP0 < t < T_LOOP1
    x = X0 + (X1 - X0) * f
    poppetje(d, x, 708, 1.3, JONGEN, t, loop=(t - T_LOOP0) * 2.2 if loopt else 0, kijk=1.0 if t > T_KIJK else 0.4,
             knipper=knip(0.0) and t < T_LAB, verbaasd=t > T_LAB + 0.3)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    if t >= T_LAB:
        v = 0 if t < T_TEL else round(64000 * ease((t - T_TEL) / 0.8), -2)
        label(img, f"${v:,.0f}", XP, hp[1] - 60, pop((t - T_LAB) / 0.3))
    ondertitel(img, t)
    if t > EIND - 0.4: img = Image.blend(img, Image.new("RGB", (W, H)), min(1, (t - (EIND - 0.4)) / 0.4))
    return img

p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                      "-c:v", "libx264", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "pop-proef.mp4"], stdin=subprocess.PIPE)
for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("KLAAR pop-proef.mp4", round(EIND, 1), "s")
