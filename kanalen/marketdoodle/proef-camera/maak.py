"""Proef 10 s 'camera-stijl' (eigenaar 24 nov, naar voorbeeld-Short @RicksClips3000): gedetailleerde stilstaande plaatjes,
± elke seconde een nieuw beeld (gewoon knippen), langzame camerabeweging per beeld (zoom of schuif), ondertitel 1-2 woorden
groot in het midden, eigen stem verteller, geen muziek. Wijzers (7:00) en het briefje worden zelf getekend (AI maakt fouten)."""
import json, math, subprocess
from PIL import Image, ImageDraw, ImageFont
W, H, FPS = 1080, 1920, 30
Z = json.load(open("zinnen.json", encoding="utf-8")); WO = json.load(open("woorden.json", encoding="utf-8"))
EIND = Z[-1][1] + 0.8
def kw(woord, n=1):
    k = 0
    for i, w, t0, t1 in WO:
        if w.lower().strip(".,").startswith(woord):
            k += 1
            if k == n: return t0
    raise SystemExit("niet gevonden " + woord)
def laad(n): return Image.open(f"afbeeldingen/{n}.png").convert("RGB")
# wekker: oude wijzers wegschilderen en zelf 7:00 tekenen
klok = laad("c1"); d = ImageDraw.Draw(klok); cx, cy, r = 495, 890, 235
d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 250, 250))
for hoek, lengte, dik in ((210, 140, 22), (0, 210, 14)):            # uurwijzer naar 7, minutenwijzer naar 12
    a = math.radians(hoek); d.line((cx, cy, cx + lengte * math.sin(a), cy - lengte * math.cos(a)), fill=(35, 35, 40), width=dik)
d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), fill=(225, 190, 70), outline=(35, 35, 40), width=5)
# briefje: handschrift er zelf op zetten
brief = laad("c8"); d = ImageDraw.Draw(brief); f = ImageFont.truetype("C:/Windows/Fonts/segoepr.ttf", 78)
for k, regel in enumerate(["Don't go", "outside.", "  - You"]):
    d.text((230, 330 + k * 130), regel, font=f, fill=(40, 45, 70))
brief = brief.rotate(0)
SHOTS = [(0, klok, "in"), (kw("the"), laad("c2"), "rechts"), (kw("too"), laad("c3"), "in"), (kw("no"), laad("c4b"), "links"),
         (kw("no", 2), laad("c5b"), "in"), (kw("your"), laad("c6"), "rechts"), (kw("and"), laad("c7"), "in"),
         (kw("note"), brief, "in"), (kw("handwriting"), laad("c9"), "in")]
SHOTS = [(t, im.resize((W, int(im.height * W / im.width))).resize((W, H)), m) for t, im, m in SHOTS]
def camera(im, f, m):
    """langzame beweging: 'in' = inzoomen 1.00 -> 1.12, 'links'/'rechts' = schuiven op 1.12"""
    if m == "in": s, dx = 1.0 + 0.12 * f, 0.0
    else: s, dx = 1.12, (f - 0.5) * (1 if m == "rechts" else -1)
    w2, h2 = int(W * s), int(H * s); big = im.resize((w2, h2), Image.BICUBIC)
    x0 = (w2 - W) / 2 + dx * (w2 - W) * 0.9; y0 = (h2 - H) / 2
    return big.crop((int(x0), int(y0), int(x0) + W, int(y0) + H))
FB = ImageFont.truetype("C:/Windows/Fonts/seguibl.ttf", 104)
groepen = []                                                       # ondertitel: telkens 1-2 woorden
for i in range(0, len(WO), 2):
    g = WO[i:i + 2]
    if len(g) == 2 and g[0][1][-1:] in ".,": g = g[:1]
    groepen.append(g)
groepen2, i = [], 0
while i < len(WO):
    g = [WO[i]]
    if WO[i][1][-1:] not in ".,!?" and i + 1 < len(WO) and len(WO[i][1]) + len(WO[i + 1][1]) < 14: g.append(WO[i + 1])
    groepen2.append(g); i += len(g)
def onder(img, t):
    g = next((g for k, g in enumerate(groepen2) if g[0][2] - 0.05 <= t < (groepen2[k + 1][0][2] if k + 1 < len(groepen2) else EIND)), None)
    if not g: return
    s = " ".join(w[1] for w in g).strip(",.").replace("7", "seven")
    s = " ".join(w[1] for w in g).replace(",", "").replace(".", "")
    d = ImageDraw.Draw(img); b = d.textbbox((0, 0), s, font=FB, stroke_width=10)
    d.text((W / 2 - (b[2] - b[0]) / 2, 1180), s, font=FB, fill=(255, 255, 255), stroke_width=10, stroke_fill=(0, 0, 0))
def frame(t):
    k = max(i for i in range(len(SHOTS)) if SHOTS[i][0] <= t)
    t0 = SHOTS[k][0]; t1 = SHOTS[k + 1][0] if k + 1 < len(SHOTS) else EIND
    img = camera(SHOTS[k][1], (t - t0) / max(0.1, t1 - t0), SHOTS[k][2]); onder(img, t); return img
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                      "-i", "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                      "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "proef-camera.mp4"], stdin=subprocess.PIPE)
for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("KLAAR proef-camera.mp4", round(EIND, 1), "s")
