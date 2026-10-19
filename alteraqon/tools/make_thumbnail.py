"""Alteraqon: YouTube-thumbnail 1280x720 voor lange video's.

Gebruik:  python alteraqon/tools/make_thumbnail.py alteraqon/<map>
Leest <map>/thumbnail.json, bijv.:
  {"image": "T01", "small": "WHAT IF THE SKY…", "lines": ["IT'S", "COUNTING", "DOWN"], "accent": "red"}
- image: afbeeldingen/<image>.png (ComfyUI, 16:9, het spannendste beeld; rechts het onderwerp, links rustige ruimte voor tekst)
- small: kleine gouden regel bovenaan; lines: 2-3 korte woorden/regels in grote letters (max ±10 tekens per regel);
  de laatste regel krijgt de accentkleur (red/gold/blue).
Schrijft <map>/thumbnail.jpg. De tekst wordt zelf getekend, dus altijd scherp en leesbaar (YouTube zet de duur rechtsonder).
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

vid = sys.argv[1]
cfg = json.load(open(os.path.join(vid, "thumbnail.json"), encoding="utf-8"))
W, H = 1280, 720
GOLD = (242, 200, 128)
ACC = {"red": (255, 70, 55), "gold": GOLD, "blue": (90, 190, 255)}[cfg.get("accent", "red")]
F = next((d for d in ("/usr/share/fonts/opentype/inter/", os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Fonts\\"),
                      r"C:\Windows\Fonts\\") if os.path.exists(os.path.join(d, "InterDisplay-Black.otf"))), "")
src = os.path.join(vid, "afbeeldingen", cfg["image"] + ".png")
if not os.path.exists(src): src = src[:-4] + ".jpg"
img = Image.open(src).convert("RGB")
s = max(W / img.width, H / img.height)
img = img.resize((round(img.width * s), round(img.height * s)), Image.LANCZOS)
img = img.crop(((img.width - W) // 2, (img.height - H) // 2, (img.width - W) // 2 + W, (img.height - H) // 2 + H))
img = ImageEnhance.Contrast(img).enhance(1.2); img = ImageEnhance.Color(img).enhance(1.15)
shade = Image.linear_gradient("L").rotate(90, expand=True).resize((W, H))
shade = shade.point(lambda v: int(225 * max(0.0, (v / 255 - 0.42) / 0.58) ** 1.2))
img = Image.composite(Image.new("RGB", (W, H), (4, 6, 12)), img, shade)

def glow(base, xy, t, font, fill, radius=14, strength=0.9, stroke=4):
    g = Image.new("L", base.size, 0)
    ImageDraw.Draw(g).text(xy, t, font=font, fill=255, stroke_width=stroke + 6, stroke_fill=255)
    g = g.filter(ImageFilter.GaussianBlur(radius)).point(lambda v: min(255, int(v * strength)))
    base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0), g)
    ImageDraw.Draw(base).text(xy, t, font=font, fill=fill, stroke_width=stroke, stroke_fill=(10, 10, 14))

lines = cfg["lines"]
size = 150 if len(lines) <= 3 and max(len(l) for l in lines) <= 9 else 118
big = ImageFont.truetype(F + "InterDisplay-Black.otf", size)
small = ImageFont.truetype(F + "Inter-ExtraBold.otf", 50)
x = 52
if cfg.get("small"):
    glow(img, (x + 4, 96), cfg["small"], small, GOLD, 12, 0.9, 2)
    ImageDraw.Draw(img).rectangle((x + 6, 166, x + 150, 174), fill=GOLD)
y = 196
for i, l in enumerate(lines):
    glow(img, (x, y), l, big, ACC if i == len(lines) - 1 else (255, 255, 255))
    y += int(size * 1.03)
out = os.path.join(vid, "thumbnail.jpg")
img.save(out, quality=90)
print(out, img.size)
