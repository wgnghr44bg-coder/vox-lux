"""Thumbnail in de stijl van video 1 (eigenaar koos "$1 TRILLION GONE."): links donker verloop met grote letters (Impact),
rechts een echte foto; letters nooit over het onderwerp; logo linksboven. Gebruik:
python thumb.py <foto.jpg> <uit.jpg> "<regel1>" "<regel2>" [focus_x 0-1] [kleur2 rood|wit|roze] [spiegel]"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps
W, H = 1280, 720
foto, uit, r1, r2 = sys.argv[1:5]
fx = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
k2 = {"rood": (226, 35, 45), "wit": (245, 245, 245), "roze": (236, 72, 153), "groen": (70, 200, 120)}[sys.argv[6] if len(sys.argv) > 6 else "rood"]
im = Image.open(foto).convert("RGB")
if len(sys.argv) > 7 and sys.argv[7] == "ja": im = ImageOps.mirror(im); fx = 1 - fx
fy = float(sys.argv[8]) if len(sys.argv) > 8 else 0.4
zoom = float(sys.argv[9]) if len(sys.argv) > 9 else 1.0
RW = int(W * 0.66)                                         # foto rechts, letters links op het donkere deel
sc = max(RW / im.width, H / im.height) * zoom; im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
cx = min(max(fx * im.width - RW / 2, 0), im.width - RW); cy = min(max(fy * im.height - H / 2, 0), im.height - H)
foto_r = im.crop((int(cx), int(cy), int(cx) + RW, int(cy) + H))
doek = Image.new("RGB", (W, H), (12, 12, 14)); doek.paste(foto_r, (W - RW, 0))
grad = Image.new("L", (W, 1)); [grad.putpixel((x, 0), int(255 * max(0, min(1, ((W - RW) + 260 - x) / 260)))) for x in range(W)]
doek = Image.composite(Image.new("RGB", (W, H), (12, 12, 14)), doek, grad.resize((W, H)))
d = ImageDraw.Draw(doek); F = "C:/Windows/Fonts/impact.ttf"
def pas(s, maxw, start):
    n = start
    while ImageFont.truetype(F, n).getlength(s) > maxw and n > 40: n -= 4
    return ImageFont.truetype(F, n)
f1 = pas(r1, 520, 110); f2 = pas(r2, 520, 170)
d.text((58, 250), r1, font=f1, fill=(245, 245, 245)); d.text((52, 250 + f1.size + 10), r2, font=f2, fill=k2)
logo = Image.open("video1/logo.png").convert("RGB").resize((80, 80)); m = Image.new("L", (80, 80), 0); ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
doek.paste(logo, (40, 36), m); doek.save(uit, quality=92); print("thumb", uit)
