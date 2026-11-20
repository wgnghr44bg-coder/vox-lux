"""Anthropic thumbnail B (eigenaar 20 nov): "$81 BILLION" + "ANTHROPIC IPO", Dario uitgeknipt voor de Nasdaq MarketSite.
Gebruik: python thumb_ipo.py <achtergrond> <dario-foto> <uit.jpg>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from rembg import remove
W, H = 1280, 720
achter, foto, uit = sys.argv[1:4]
bg = Image.open(f"echt/{achter}.jpg").convert("RGB")
sc = max(W / bg.width, H / bg.height); bg = bg.resize((int(bg.width * sc), int(bg.height * sc)), Image.LANCZOS)
bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
bg = ImageEnhance.Brightness(bg.filter(ImageFilter.GaussianBlur(2))).enhance(0.75)
# links donker verloop voor de letters
grad = Image.new("L", (W, 1)); [grad.putpixel((x, 0), int(245 * max(0, min(1, (760 - x) / 420)))) for x in range(W)]
bg = Image.composite(Image.new("RGB", (W, H), (10, 10, 12)), bg, grad.resize((W, H)))
p = Image.open(f"echt/{foto}.jpg").convert("RGB")
cut = remove(p)                                            # RGBA, achtergrond weg
bb = cut.getbbox(); cut = cut.crop(bb)
h = int(H * 1.05); cut = cut.resize((int(cut.width * h / cut.height), h), Image.LANCZOS)
x = W - cut.width + int(cut.width * 0.08); y = H - cut.height + int(H * 0.12)
glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); sh = Image.new("RGBA", cut.size, (0, 0, 0, 160)); sh.putalpha(cut.split()[3].point(lambda v: int(v * 0.6)))
glow.paste(sh, (x - 14, y + 6), sh); glow = glow.filter(ImageFilter.GaussianBlur(14))
doek = bg.convert("RGBA"); doek = Image.alpha_composite(doek, glow); doek.paste(cut, (x, y), cut); doek = doek.convert("RGB")
d = ImageDraw.Draw(doek); F = "C:/Windows/Fonts/impact.ttf"
def pas(s, maxw, start):
    n = start
    while ImageFont.truetype(F, n).getlength(s) > maxw and n > 40: n -= 4
    return ImageFont.truetype(F, n)
r1, r2, r3 = "ANTHROPIC", "IPO", "$81 BILLION"
f1 = pas(r1, 500, 96); f3 = pas(r3, 560, 150)
d.text((58, 205), r1 + " " + r2, font=pas(r1 + " " + r2, 560, 100), fill=(245, 245, 245))
d.text((52, 330), r3, font=f3, fill=(70, 200, 120))
logo = Image.open("../video1/logo.png").convert("RGB").resize((80, 80)); m = Image.new("L", (80, 80), 0); ImageDraw.Draw(m).ellipse([0, 0, 79, 79], fill=255)
doek.paste(logo, (40, 36), m)
doek.save(uit, quality=92); print("thumb", uit, "dario x", x, "breed", cut.width)
