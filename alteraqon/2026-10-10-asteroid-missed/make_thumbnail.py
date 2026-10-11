"""Thumbnail 1280x720 voor de lange asteroid-video (Alteraqon-stijl: koel, hoog contrast, goud accent).

Gebruik (vanuit deze map): python3 make_thumbnail.py   -> thumbnail.jpg
Basis: afbeeldingen/T01.jpg (asteroïde scheert langs de aarde, T. rex op de voorgrond).
Tekst links (YouTube zet de duur rechtsonder): klein "WHAT IF" in goud, daarboven/onder groot "IT MISSED".
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
GOLD = (242, 200, 128)
F = "/usr/share/fonts/opentype/inter/"
img = Image.open("afbeeldingen/T01.jpg").convert("RGB")
s = max(W / img.width, H / img.height)
img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
img = img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width - W) // 2 + W, (img.height - H) // 2 + H))
img = ImageEnhance.Contrast(img).enhance(1.18)
img = ImageEnhance.Color(img).enhance(1.15)

# links donkerder voor de tekst
shade = Image.new("L", (W, H))
px = shade.load()
for x in range(W):
    v = int(215 * max(0.0, 1 - x / (W * 0.58)) ** 1.3)
    for y in range(H):
        px[x, y] = v
img = Image.composite(Image.new("RGB", (W, H), (4, 8, 16)), img, shade)

def text(base, xy, t, font, fill, stroke=0):
    glow = Image.new("L", base.size, 0)
    ImageDraw.Draw(glow).text(xy, t, font=font, fill=255, stroke_width=stroke + 10, stroke_fill=255)
    base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0), glow.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.8)))
    ImageDraw.Draw(base).text(xy, t, font=font, fill=fill, stroke_width=stroke, stroke_fill=(10, 10, 14))

d = ImageDraw.Draw(img)
small = ImageFont.truetype(F + "Inter-ExtraBold.otf", 58)
big = ImageFont.truetype(F + "InterDisplay-Black.otf", 190)
x = 56
text(img, (x + 6, 92), "WHAT IF…", small, GOLD, 2)
d.rectangle((x + 8, 170, x + 150, 178), fill=GOLD)
text(img, (x, 196), "IT", big, (255, 255, 255), 4)
text(img, (x, 396), "MISSED?", big, (255, 255, 255), 4)
img.save("thumbnail.jpg", quality=90)
print("thumbnail.jpg", img.size)
