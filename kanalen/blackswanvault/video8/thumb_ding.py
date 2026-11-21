"""Thumbnail met het onderwerp zelf (eigenaar 21 nov: "de persoon die ermee te maken heeft of het ding laten zien").
Het beeld vult de rechterkant (onderwerp rond x=880), links donker met de tekst. Alleen eigen AI-beelden of beelden met licentie (echt/bronnen.tsv).
Gebruik: python thumb_ding.py <beeld> <midden 0-1: waar het onderwerp in het beeld staat> <regel1 rood> <regel2 wit> <uit.jpg>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
W, H, DOEL = 1280, 720, 880
beeld, mid, r1, r2, uit = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]
im = Image.open(beeld).convert("RGB"); sc = max(H / im.height, W / im.width) * float(os.environ.get("ZOOM", "1.0"))
im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
im = ImageEnhance.Contrast(ImageEnhance.Color(im).enhance(1.15)).enhance(1.08)
x = int(DOEL - mid * im.width); x = min(x, W - 200); x = max(x, W - im.width); y = (H - im.height) // 2
doek = Image.new("RGB", (W, H), (12, 12, 16)); doek.paste(im, (x, y))
links = max(0, x)                                        # waar het beeld begint; daar zacht laten overlopen in donker
grad = Image.new("L", (W, 1))
for i in range(W):
    a = max(min(1, (600 - i) / 320), min(1, (links + 300 - i) / 300) if links > 0 else 0)
    grad.putpixel((i, 0), int(255 * max(0, a)))
doek = Image.composite(Image.new("RGB", (W, H), (12, 12, 16)), doek, grad.resize((W, H)))
d = ImageDraw.Draw(doek); F = "C:/Windows/Fonts/impact.ttf"
def pas(s, maxw, start):
    n = start
    while ImageFont.truetype(F, n).getlength(s) > maxw and n > 40: n -= 4
    return ImageFont.truetype(F, n)
f1 = pas(r1, 560, 230); f2 = pas(r2, 560, 150)
d.text((57, 155), r1, font=f1, fill=(0, 0, 0)); d.text((52, 150), r1, font=f1, fill=(232, 30, 40), stroke_width=5, stroke_fill=(0, 0, 0))
d.text((63, 405), r2, font=f2, fill=(0, 0, 0)); d.text((58, 400), r2, font=f2, fill=(250, 250, 250), stroke_width=4, stroke_fill=(0, 0, 0))
logo = Image.open("logo.png").convert("RGB").resize((80, 80)); m = Image.new("L", (80, 80), 0); ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
doek.paste(logo, (40, 36), m); doek.save(uit, quality=92); print(uit)
