from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps, ImageEnhance
W, H = 1280, 720
IMP = "C:/Windows/Fonts/impact.ttf"; BOD = "C:/Windows/Fonts/BOD_I.TTF"
CREAM, GOUD, ROOD = (242, 236, 222), (226, 184, 110), (178, 44, 48)
def basis(src, schuif=0, warm=1.0):
    im = Image.open(src).convert("RGB").resize((W, H))
    if schuif:
        n = Image.new("RGB", (W, H)); n.paste(im, (schuif, 0)); n.paste(ImageOps.mirror(im.crop((0, 0, schuif, H))), (0, 0)); im = n
    im = ImageEnhance.Color(im).enhance(warm)
    g = Image.new("L", (W, 1)); [g.putpixel((x, 0), int(225 * max(0, 1 - x / 720) ** 1.2)) for x in range(W)]
    return Image.composite(Image.new("RGB", (W, H), (6, 9, 18)), im, g.resize((W, H)))
def maan(d, x, y, r):
    d.ellipse((x - r, y - r, x + r, y + r), fill=GOUD); d.ellipse((x - r + r * 0.55, y - r - r * 0.15, x + r + r * 0.55, y + r - r * 0.15), fill=(6, 9, 18))
def tekst(d, xy, s, f, kleur):
    for o in (5, 3): d.text((xy[0] + o, xy[1] + o), s, font=f, fill=(0, 0, 0))
    d.text(xy, s, font=f, fill=kleur)
def maak(src, uit, schuif, warm):
    im = basis(src, schuif, warm); d = ImageDraw.Draw(im)
    tekst(d, (60, 140), "JACK THE", ImageFont.truetype(IMP, 140), CREAM)
    tekst(d, (60, 290), "RIPPER", ImageFont.truetype(IMP, 170), ROOD)
    # rustige belofte: maantje + "a calm story for sleep"
    maan(d, 92, 548, 26)
    tekst(d, (136, 522), "true crime for sleep", ImageFont.truetype(BOD, 54), GOUD)
    im.save(uit, quality=92)
maak("branding/afbeeldingen/l1.png", "video1/thumb-A-lantaarn.jpg", 380, 1.1)
maak("branding/afbeeldingen/b1.png", "video1/thumb-B-straat.jpg", 260, 1.0)
maak("../../stories/_ripper-proef/afbeeldingen/007.png", "video1/thumb-C-vrouw.jpg", 360, 1.0)
vel = Image.new("RGB", (1290, 1110), (255, 255, 255))
for k, n in enumerate(["A-lantaarn", "B-straat", "C-vrouw", None]):
    p = f"video1/thumb-{n}.jpg" if n else "video1/thumbnail.jpg"
    vel.paste(Image.open(p).resize((640, 360)), ((k % 2) * 645, (k // 2) * 370))
klein = Image.open("video1/thumb-A-lantaarn.jpg").resize((246, 138))
vel.paste(klein, (0, 750)); vel.paste(Image.open("video1/thumb-B-straat.jpg").resize((246, 138)), (256, 750)); vel.paste(Image.open("video1/thumb-C-vrouw.jpg").resize((246, 138)), (512, 750))
vel.save("video1/thumbs-vergelijk.jpg", quality=90)
