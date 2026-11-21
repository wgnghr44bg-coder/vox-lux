"""Thumbnail-stijl v2 (20 nov, na vergelijking grote kanalen): 2 korte regels (samen ± 4 woorden), gezicht van voren met emotie
rechts (uitgeknipt), lichtere/fellere achtergrond, logo linksboven.
Gebruik: python thumb_v2.py <achtergrond.jpg> <gezicht.jpg|png> <regel1 rood> <regel2 wit> <uit.jpg>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from rembg import remove
W, H = 1280, 720
achter, gez, r1, r2, uit = sys.argv[1:6]
def vul(im):
    sc = max(W / im.width, H / im.height); im = im.resize((int(im.width * sc), int(im.height * sc)), Image.LANCZOS)
    return im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H))
bg = vul(Image.open(achter).convert("RGB")).filter(ImageFilter.GaussianBlur(6))
bg = ImageEnhance.Color(ImageEnhance.Brightness(bg).enhance(0.8)).enhance(1.3)
grad = Image.new("L", (W, 1)); [grad.putpixel((x, 0), int(235 * max(0, min(1, (640 - x) / 380)))) for x in range(W)]
bg = Image.composite(Image.new("RGB", (W, H), (12, 12, 16)), bg, grad.resize((W, H)))
cut = remove(Image.open(gez).convert("RGB")); rechtsaf = cut.getbbox()[2] >= cut.width - 2; cut = cut.crop(cut.getbbox())
# 21 nov (eigenaar: "mensen zijn voor de helft afgesneden"): nooit opzij afknippen. De persoon past in de rechterhelft
# (vanaf x=VAN); alleen als de foto zelf al rechts afloopt, mag hij rechts uit beeld lopen.
VAN = 560
sc = min(H / cut.height, (W - VAN) / cut.width)   # nooit links over de tekst
cut = cut.resize((int(cut.width * sc), int(cut.height * sc)), Image.LANCZOS)
if cut.height < 0.85 * H: print("LET OP: persoon wordt klein (", cut.height, "px hoog); kies een smallere foto")
cut = ImageEnhance.Contrast(cut).enhance(1.08)
x = W - cut.width if rechtsaf else VAN + (W - VAN - cut.width) // 2; y = H - cut.height
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); a = cut.split()[3]
rand = Image.new("RGBA", cut.size, (255, 255, 255, 0)); rand.putalpha(a.point(lambda v: 200 if v > 10 else 0))
glow.paste(rand, (x, y), rand); glow = glow.filter(ImageFilter.GaussianBlur(10))
doek = Image.alpha_composite(bg.convert("RGBA"), glow); doek.paste(cut, (x, y), cut); doek = doek.convert("RGB")
d = ImageDraw.Draw(doek); F = "C:/Windows/Fonts/impact.ttf"
def pas(s, maxw, start):
    n = start
    while ImageFont.truetype(F, n).getlength(s) > maxw and n > 40: n -= 4
    return ImageFont.truetype(F, n)
f1 = pas(r1, VAN - 70, 230); f2 = pas(r2, VAN - 70, 150)
for dx, dy in [(5, 5)]: d.text((52 + dx, 150 + dy), r1, font=f1, fill=(0, 0, 0)); d.text((58 + dx, 400 + dy), r2, font=f2, fill=(0, 0, 0))
d.text((52, 150), r1, font=f1, fill=(232, 30, 40)); d.text((58, 400), r2, font=f2, fill=(250, 250, 250))
logo = Image.open("logo.png").convert("RGB").resize((80, 80)); m = Image.new("L", (80, 80), 0); ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
doek.paste(logo, (40, 36), m); doek.save(uit, quality=92); print(uit)
