"""What If-proef (eigenaar 22 nov: "what if heel breed", stijl zoals de what-if kanalen die nu winnen):
platte cartoonbeelden, elke zin een nieuw beeld (± 3 s), kleine bewegingen (beeld 'ploft' binnen, rustige drift),
grote tekst die op het kernwoord binnenploft, tellers die oplopen. Bouwt beeld.mp4 (1280x720, 30 fps) uit
afbeeldingen/ + zinnen.json + woorden.json."""
import json, math, re, subprocess
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1280, 720, 30
Z = json.load(open("zinnen.json", encoding="utf-8"))
WO = json.load(open("woorden.json", encoding="utf-8"))
EIND = Z[-1][1] + 1.6
F = "C:/Windows/Fonts/seguibl.ttf"   # Segoe UI Black

def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def pop(x):                                         # 0 -> iets te groot -> 1 (ploffen)
    x = max(0.0, min(1.0, x)); return 1 + 0.18 * math.sin(math.pi * x) * (1 - x) if x < 1 else 1.0

BEELD = [Image.open(f"afbeeldingen/s{i}.png").convert("RGB").resize((W, H)) for i in range(10)]
START = [0.0] + [Z[i][0] - 0.15 for i in range(1, 10)]

# teksten: (start, tekst, x, y, maat, kleur, rand)  (x,y = midden)
WIT, ROOD, GEEL, GROEN = (255, 255, 255), (235, 64, 52), (255, 214, 64), (80, 200, 120)
T = [
    (kw(0, "sleep"), "NEVER SLEEP AGAIN?", 640, 110, 78, WIT),
    (kw(1, "tiredness"), "NO TIREDNESS", 300, 90, 56, WIT),
    (kw(1, "alarm"), "NO ALARM", 300, 170, 56, WIT),
    (kw(1, "ever"), "EVER.", 300, 260, 74, GEEL),
    (kw(4, "show"), "SHOWS", 260, 120, 54, WIT),
    (kw(4, "book"), "BOOKS", 260, 200, 54, WIT),
    (kw(4, "game"), "GAMES", 260, 280, 54, WIT),
    (kw(5, "night"), "NIGHT 3", 190, 90, 70, GEEL),
    (kw(5, "asleep"), "EVERYONE: ASLEEP", 900, 640, 48, WIT),
    (kw(6, "bigger"), "BIGGER PROBLEM", 640, 640, 70, ROOD),
    (kw(9, "week"), "AFTER 1 WEEK?", 640, 110, 90, ROOD),
]
# tellers: (start, duur, van, tot, sjabloon, x, y, maat, kleur)
TEL = [
    (kw(2, "eight"), 1.0, 0, 8, "+{} HOURS / DAY", 380, 600, 72, GEEL),
    (kw(3, "25"), 1.4, 0, 25, "{} YEARS", 640, 600, 96, GEEL),
    (kw(8, "trash"), 1.6, 0, 100, "BRAIN TRASH: {}%", 640, 90, 64, ROOD),
]
# schakelaar (zoals een instellingenmenu): (start, aan?, scene)
SCH = [(kw(7, "cleans"), True), (kw(8, "without"), False)]

fonts = {}
def font(m):
    if m not in fonts: fonts[m] = ImageFont.truetype(F, m)
    return fonts[m]

def tekst(img, s, x, y, maat, kleur, schaal=1.0):
    m = max(8, int(maat * schaal)); f = font(m)
    d = ImageDraw.Draw(img); b = d.textbbox((0, 0), s, font=f, stroke_width=max(3, m // 9))
    w, h = b[2] - b[0], b[3] - b[1]
    d.text((x - w / 2, y - h / 2 + 4), s, font=f, fill=(0, 0, 0), stroke_width=max(3, m // 9), stroke_fill=(0, 0, 0))   # schaduw
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kleur, stroke_width=max(3, m // 12), stroke_fill=(20, 20, 30))

def schakel(img, t0, aan, t):
    x, y, br, ho = 640, 610, 560, 96
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((x - br / 2, y - ho / 2, x + br / 2, y + ho / 2), 24, fill=(25, 30, 50), outline=(120, 200, 255), width=4)
    f = font(40); d.text((x - br / 2 + 30, y - 26), "BRAIN CLEANING", font=f, fill=WIT)
    k = ease((t - t0 - 0.3) / 0.35)
    links = (1 - k) if aan else k                  # aan: knop schuift naar rechts (groen)
    pos = 1 - links
    kl = tuple(int(a + (b - a) * pos) for a, b in zip(ROOD, GROEN))
    sx = x + br / 2 - 150
    d.rounded_rectangle((sx, y - 28, sx + 110, y + 28), 28, fill=kl)
    cx = sx + 28 + pos * 54
    d.ellipse((cx - 22, y - 22, cx + 22, y + 22), fill=WIT)

def frame(t):
    k = max(i for i in range(10) if START[i] <= t)
    t0 = START[k]; t1 = START[k + 1] if k + 1 < 10 else EIND
    p = (t - t0)
    s = pop(p / 0.35) * (1 + 0.03 * (t - t0) / max(1, t1 - t0))    # ploffen bij binnenkomen + rustige drift
    s = max(s, 1.0)
    img = BEELD[k]
    if s != 1.0:
        w2, h2 = int(W * s), int(H * s)
        img = img.resize((w2, h2), Image.BICUBIC).crop(((w2 - W) // 2, (h2 - H) // 2, (w2 - W) // 2 + W, (h2 - H) // 2 + H))
    else: img = img.copy()
    for st, s_, x, y, m, kl in T:
        if t0 - 0.01 <= st <= t1 and t >= st: tekst(img, s_, x, y, m, kl, pop((t - st) / 0.3))
    for st, du, a, b, sj, x, y, m, kl in TEL:
        if t0 - 0.01 <= st <= t1 and t >= st:
            v = round(a + (b - a) * ease((t - st) / du)); tekst(img, sj.format(v), x, y, m, kl, pop((t - st) / 0.3))
    for st, aan in SCH:
        if t0 - 0.01 <= st <= t1 and t >= st - 0.3: schakel(img, st, aan, t)
    if t > EIND - 0.5: img = Image.blend(img, Image.new("RGB", (W, H)), min(1, (t - (EIND - 0.5)) / 0.5))
    return img

p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-pix_fmt", "yuv420p", "beeld.mp4"], stdin=subprocess.PIPE)
n = int(EIND * FPS)
for i in range(n): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait()
print("KLAAR beeld.mp4", round(EIND, 1), "s")
