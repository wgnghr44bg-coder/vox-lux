"""Thumbnail markt-video in de vaste stijl (Nvidia/Anthropic/GTA): links zwart verloop met 2 regels (wit + rood),
logo linksboven, rechts het beeld met de echte Nasdaq-lijn (1 sep -> 19 nov).
Gebruik: python thumb_markt2.py <achtergrond> <regel1> <regel2> <uit.jpg>"""
import sys, json, datetime as dt
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
W, H = 1280, 720
GEEN_LIJN = "--geen-lijn" in sys.argv   # 20 nov: zonder koerslijn (onderwerp zonder koers)
if GEEN_LIJN: sys.argv.remove("--geen-lijn")
achter, r1, r2, uit = sys.argv[1:5]; r3 = sys.argv[5] if len(sys.argv) > 5 else ""
bg = Image.open(f"echt/{achter}.jpg").convert("RGB")
sc = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * sc), int(bg.height * sc)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(1.5))).enhance(0.7)
grad = Image.new("L", (W, 1)); [grad.putpixel((x, 0), int(245 * max(0, min(1, (700 - x) / 380)))) for x in range(W)]
bg = Image.composite(Image.new("RGB", (W, H), (10, 10, 12)), bg, grad.resize((W, H)))
if GEEN_LIJN:
    doek = bg
else:
    r = json.load(open("data/nasdaq.json"))["chart"]["result"][0]
    ts, c = r["timestamp"], r["indicators"]["quote"][0]["close"]
    pts = [v for t, v in zip(ts, c) if v and dt.datetime.fromtimestamp(t, dt.timezone.utc).date() >= dt.date(2026, 9, 1)]
    lo, hi = min(pts), max(pts)
    x0, x1, y0, y1 = 600, W - 50, 150, 600
    xy = [(x0 + (x1 - x0) * i / (len(pts) - 1), y0 + (y1 - y0) * (hi - v) / (hi - lo)) for i, v in enumerate(pts)]
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
    dl.line(xy, fill=(230, 30, 40, 255), width=12, joint="curve")
    ex, ey = xy[-1]; dl.ellipse([ex - 15, ey - 15, ex + 15, ey + 15], fill=(230, 30, 40, 255))
    sch = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sch).line(xy, fill=(0, 0, 0, 200), width=26, joint="curve")
    doek = Image.alpha_composite(bg.convert("RGBA"), sch.filter(ImageFilter.GaussianBlur(8)))
    doek = Image.alpha_composite(doek, laag.filter(ImageFilter.GaussianBlur(9)))
    doek = Image.alpha_composite(doek, laag).convert("RGB")
d = ImageDraw.Draw(doek); F = "C:/Windows/Fonts/impact.ttf"
def pas(s, maxw, start):
    n = start
    while ImageFont.truetype(F, n).getlength(s) > maxw and n > 40: n -= 4
    return ImageFont.truetype(F, n)
f1 = pas(r1, 520, 100); f2 = pas(r2, 540, 170)
top = 150 if r3 else 225
d.text((58, top), r1, font=f1, fill=(245, 245, 245))
d.text((52, top + 120), r2, font=f2, fill=(228, 30, 38))
if r3: d.text((58, top + 330), r3, font=pas(r3, 520, 120), fill=(245, 245, 245))
logo = Image.open("../video1/logo.png").convert("RGB").resize((80, 80)); m = Image.new("L", (80, 80), 0); ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
doek.paste(logo, (40, 36), m)
doek.save(uit, quality=92); print(uit)
