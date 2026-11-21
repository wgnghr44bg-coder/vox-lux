"""Banner met het echte DNB-gebouw (Wikimedia, CC BY-SA 4.0, Erremm) in avondsfeer + gouden beurslijn. Vergelijken met banner B (AI)."""
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps
import maak
W, H = 2560, 1440
im = Image.open("echt/dnbwest.jpg").convert("RGB")
s = max(W / im.width, H / im.height) * 1.05; im = im.resize((int(im.width * s), int(im.height * s)), Image.LANCZOS)
im = im.crop(((im.width - W) // 2, (im.height - H) // 2 + 60, (im.width - W) // 2 + W, (im.height - H) // 2 + 60 + H))
# avondsfeer: minder kleur, donker, blauwe toon
im = ImageEnhance.Color(im).enhance(0.35); im = ImageEnhance.Brightness(im).enhance(0.42)
blauw = Image.new("RGB", (W, H), (10, 16, 38)); im = Image.blend(im, blauw, 0.35)
# gouden stijgende lijn met gloed
lijn = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lijn)
pts = [(160, 1210), (330, 1130), (420, 1150), (620, 1000), (800, 1080), (1000, 930), (1120, 960), (1330, 820), (1500, 880),
       (1760, 700), (1900, 600), (2030, 650), (2150, 560), (2320, 420)]
d.line(pts, fill=(222, 170, 60, 255), width=12, joint="curve")
for p in pts[1:-1]: d.ellipse((p[0] - 14, p[1] - 14, p[0] + 14, p[1] + 14), fill=(235, 200, 120, 255))
x, y = pts[-1]; d.polygon([(x + 60, y - 55), (x - 40, y - 10), (x + 15, y + 40)], fill=(222, 170, 60, 255))
gloed = lijn.filter(ImageFilter.GaussianBlur(18)); im = im.convert("RGBA"); im.alpha_composite(gloed); im.alpha_composite(lijn)
im.convert("RGB").save("ai/afbeeldingen/banner-dnb.png")
maak.banner("ai/afbeeldingen/banner-dnb.png", Image.open("logo-munt.png"), "banner-dnb.jpg")
