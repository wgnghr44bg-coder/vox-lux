"""Thumbnail 1280x720 voor de lange sky-countdown-video (Alteraqon-stijl: donker, hoog contrast, rood/goud accent).

Gebruik (vanuit deze map): python3 make_thumbnail.py   -> thumbnail.jpg
Basis: afbeeldingen/T01.jpg (donkere stad, rode gloed in de lucht, silhouetten op een dak).
Rechts boven in de lucht een gloeiende countdown (zelf getekend, dus altijd leesbaar),
links groot "IT'S COUNTING DOWN" (YouTube zet de duur rechtsonder).
"""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
GOLD = (242, 200, 128)
F = "/usr/share/fonts/opentype/inter/"
img = Image.open("afbeeldingen/T01.jpg").convert("RGB")
s = max(W / img.width, H / img.height)
img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
img = img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width - W) // 2 + W, (img.height - H) // 2 + H))
img = ImageEnhance.Contrast(img).enhance(1.2)
img = ImageEnhance.Color(img).enhance(1.15)

# links donkerder voor de tekst
shade = Image.linear_gradient("L").rotate(90, expand=True).resize((W, H))      # 255 links -> 0 rechts
shade = shade.point(lambda v: int(225 * max(0.0, (v / 255 - 0.42) / 0.58) ** 1.2))
img = Image.composite(Image.new("RGB", (W, H), (4, 6, 12)), img, shade)

def glow_text(base, xy, t, font, fill, glow, radius, strength, stroke=0, anchor="la"):
    g = Image.new("L", base.size, 0)
    ImageDraw.Draw(g).text(xy, t, font=font, fill=255, stroke_width=stroke + 6, stroke_fill=255, anchor=anchor)
    g = g.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * strength)))
    base.paste(Image.new("RGB", base.size, glow), (0, 0), g)
    ImageDraw.Draw(base).text(xy, t, font=font, fill=fill, stroke_width=stroke, stroke_fill=(10, 10, 14), anchor=anchor)

# gloeiende countdown in de lucht (rechts boven, niet onder de duur-badge)
num = ImageFont.truetype(F + "InterDisplay-SemiBold.otf", 104)
glow_text(img, (905, 150), "00:00:07", num, (255, 226, 214), (255, 40, 30), 22, 2.2, anchor="mm")
glow_text(img, (905, 150), "00:00:07", num, (255, 236, 228), (255, 70, 50), 6, 1.0, anchor="mm")

d = ImageDraw.Draw(img)
small = ImageFont.truetype(F + "Inter-ExtraBold.otf", 50)
big = ImageFont.truetype(F + "InterDisplay-Black.otf", 150)
x = 52
glow_text(img, (x + 4, 96), "WHAT IF THE SKY…", small, GOLD, (0, 0, 0), 12, 0.9, 2)
d.rectangle((x + 6, 166, x + 150, 174), fill=GOLD)
glow_text(img, (x, 196), "IT'S", big, (255, 255, 255), (0, 0, 0), 14, 0.9, 4)
glow_text(img, (x, 350), "COUNTING", big, (255, 255, 255), (0, 0, 0), 14, 0.9, 4)
glow_text(img, (x, 504), "DOWN", big, (255, 70, 55), (0, 0, 0), 14, 0.9, 4)
img.save("thumbnail.jpg", quality=90)
print("thumbnail.jpg", img.size)
