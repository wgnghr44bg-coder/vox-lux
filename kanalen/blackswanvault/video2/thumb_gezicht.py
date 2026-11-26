"""26 nov: Anthropic-thumbnail met gezicht (Studio: CTR 1,8% met alleen het logo; grote kanalen winnen met een gezicht).
Dario Amodei (echt/dario-d.jpg, CC BY 2.0 TechCrunch) groot rechts, oranje gloed, zelfde 2 regels als de oude thumbnail."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from rembg import remove
W, H = 1280, 720
doek = Image.new("RGB", (W, H), (10, 10, 12)); d = ImageDraw.Draw(doek)
for x in range(W):
    g = max(0, (x - 480) / 800); d.line([(x, 0), (x, H)], fill=(int(10 + 170 * g), int(10 + 70 * g), int(12 + 30 * g)))
doek = doek.filter(ImageFilter.GaussianBlur(50))
im = remove(Image.open("echt/dario-d.jpg").convert("RGB"))
a = im.split()[3].point(lambda v: 255 if v > 140 else 0).filter(ImageFilter.MinFilter(11)).filter(ImageFilter.MaxFilter(11))  # restjes TechCrunch-letters weg
im.putalpha(Image.composite(im.split()[3], Image.new("L", im.size, 0), a)); im = im.crop(im.getbbox())
h = 700; im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS)
rand = im.split()[3].filter(ImageFilter.MaxFilter(9)); wit = Image.new("RGBA", im.size, (255, 255, 255, 255)); wit.putalpha(rand)
x = max(640, W - im.width + 120); y = H - h + 40
doek.paste(wit, (x, y), wit); doek.paste(im, (x, y), im)
doek = ImageEnhance.Contrast(doek).enhance(1.08); d = ImageDraw.Draw(doek)
F = "C:/Windows/Fonts/impact.ttf"
def regel(s, y, kleur, size, breed=560):
    f = ImageFont.truetype(F, size)
    while d.textlength(s, font=f) > breed: size -= 6; f = ImageFont.truetype(F, size)
    d.text((50, y), s, font=f, fill=kleur, stroke_width=6, stroke_fill=(0, 0, 0))
regel("$81 BILLION", 190, (235, 30, 40), 190, 600); regel("END OF HUMANITY?", 420, (255, 255, 255), 130, 600)
lg = Image.open("logo.png").convert("RGBA"); lg.thumbnail((80, 80))
rond = Image.new("L", lg.size, 0); ImageDraw.Draw(rond).ellipse([0, 0, lg.width - 1, lg.height - 1], fill=255)
doek.paste(lg, (40, 36), Image.composite(lg.split()[3], rond, rond))
doek.save("thumbnail-gezicht.jpg", quality=92)
doek.resize((320, 180), Image.LANCZOS).save("thumbnail-gezicht-klein.png"); print("ok")
