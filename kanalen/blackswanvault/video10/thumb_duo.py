"""Thumbnail met 2 mensen (zoals de grote kanalen bij het Huang-verhaal): hoofdpersoon groot rechts-midden, tweede persoon rechts,
links 2 korte regels. Alleen vrije foto's (echt/bronnen.tsv). Gebruik: python thumb_duo.py <hoofd.jpg> <tweede.jpg> <rood> <wit> <uit.jpg>"""
import sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from rembg import remove
W, H = 1280, 720
a, b, r1, r2, uit = sys.argv[1:6]
def knip(p, h):
    im = remove(Image.open(p).convert("RGB")); bb = im.getbbox(); im = im.crop(bb)
    return im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
doek = Image.new("RGB", (W, H), (10, 12, 14)); d = ImageDraw.Draw(doek)
for x in range(W):                                        # groene gloed rechts (Nvidia-kleur), links donker
    g = max(0, (x - 520) / 760); d.line([(x, 0), (x, H)], fill=(int(10 + 20 * g), int(12 + 120 * g), int(14 + 20 * g)))
doek = doek.filter(ImageFilter.GaussianBlur(40))
t = Image.open(b).convert("RGB"); t = t.crop((0, 0, t.width, int(t.width * 1.2))).resize((270, 324), Image.LANCZOS)
ImageDraw.Draw(doek).rectangle([492, 72, 492 + 270 + 16, 72 + 324 + 16], fill=(255, 255, 255)); doek.paste(t, (500, 80))
h = knip(a, 660)
rand = h.split()[3].filter(ImageFilter.MaxFilter(9)); wit = Image.new("RGBA", h.size, (255, 255, 255, 255)); wit.putalpha(rand)
x = max(700, W - h.width + 150); doek.paste(wit, (x, H - h.height + 10), wit); doek.paste(h, (x, H - h.height + 10), h)
doek = ImageEnhance.Contrast(doek).enhance(1.08); d = ImageDraw.Draw(doek)
F = "C:/Windows/Fonts/impact.ttf"
def regel(s, y, kleur, size):
    f = ImageFont.truetype(F, size)
    while d.textlength(s, font=f) > 470: size -= 6; f = ImageFont.truetype(F, size)
    d.text((50, y), s, font=f, fill=kleur, stroke_width=6, stroke_fill=(0, 0, 0))
regel(r1, 190, (235, 30, 40), 190); regel(r2, 400, (255, 255, 255), 130)
lg = Image.open("logo.png").convert("RGBA"); lg.thumbnail((80, 80)); doek.paste(lg, (40, 36), lg)
doek.save(uit, quality=92); print(uit)
