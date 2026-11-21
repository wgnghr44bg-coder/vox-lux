"""Banner Geldverhaal: alleen donkere achtergrond + gouden beurslijn (geen gebouw). Eigenaar 21 nov: "of doe een donker achtergrond"."""
from PIL import Image, ImageDraw, ImageFilter
import maak
W, H = 2560, 1440
im = Image.new("RGB", (W, H), (8, 9, 14)); d = ImageDraw.Draw(im)
for y in range(H):  # zachte verloop: midden iets lichter
    t = 1 - abs(y - H / 2) / (H / 2)
    d.line([(0, y), (W, y)], fill=(int(8 + 10 * t), int(10 + 12 * t), int(16 + 22 * t)))
raster = Image.new("RGBA", (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(raster)
for x in range(0, W, 160): g.line([(x, 0), (x, H)], fill=(255, 255, 255, 10), width=2)
for y in range(0, H, 160): g.line([(0, y), (W, y)], fill=(255, 255, 255, 10), width=2)
im = im.convert("RGBA"); im.alpha_composite(raster)
lijn = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lijn)
pts = [(120, 1180), (330, 1090), (430, 1120), (640, 960), (820, 1040), (1020, 900), (1150, 930), (1360, 790), (1520, 850),
       (1780, 680), (1920, 590), (2050, 640), (2170, 540), (2340, 390)]
d.line(pts, fill=(222, 170, 60, 255), width=12, joint="curve")
for p in pts[1:-1]: d.ellipse((p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14), fill=(235, 200, 120, 255))
x, y = pts[-1]; d.polygon([(x + 60, y - 55), (x - 40, y - 10), (x + 15, y + 40)], fill=(222, 170, 60, 255))
im.alpha_composite(lijn.filter(ImageFilter.GaussianBlur(22))); im.alpha_composite(lijn)
im.convert("RGB").save("ai/afbeeldingen/banner-donker.png")
maak.banner("ai/afbeeldingen/banner-donker.png", Image.open("logo-munt.png"), "banner-donker.jpg")
