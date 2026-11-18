from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
F = "C:/Windows/Fonts/"
GOUD, WIT = (214, 172, 98), (232, 228, 218)
def banner(src, uit):
    W, H = 2560, 1440
    im = Image.open(src).convert("RGB").resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.8)
    # donkere band achter de tekst in het veilige midden (1546 x 423)
    band = Image.new("L", (W, H), 0); d = ImageDraw.Draw(band)
    d.rectangle((300, 580, W - 300, 860), fill=190); band = band.filter(ImageFilter.GaussianBlur(90))
    im = Image.composite(Image.new("RGB", (W, H), (6, 9, 14)), im, band)
    d = ImageDraw.Draw(im)
    t = "N O I R T R A C E S"
    f = ImageFont.truetype(F + "BOD_B.TTF", 150)
    d.text((W / 2 + 5, 690 + 5), t, font=f, fill=(0, 0, 0), anchor="mm")
    d.text((W / 2, 690), t, font=f, fill=WIT, anchor="mm")
    f2 = ImageFont.truetype(F + "BOD_I.TTF", 58)
    sub = "Dark History  &  True Crime for Sleep"
    hw = d.textlength(sub, font=f2) / 2
    d.line((W / 2 - hw - 200, 795, W / 2 - hw - 40, 795), fill=GOUD, width=3); d.line((W / 2 + hw + 40, 795, W / 2 + hw + 200, 795), fill=GOUD, width=3)
    d.text((W / 2 + 3, 790 + 3), sub, font=f2, fill=(0, 0, 0), anchor="mm")
    d.text((W / 2, 790), sub, font=f2, fill=GOUD, anchor="mm")
    im.save(uit, quality=92)
def logo(src, uit, cx, cy, size, nt=True):
    im = Image.open(src).convert("RGB")
    im = im.crop((cx - size // 2, cy - size // 2, cx + size // 2, cy + size // 2)).resize((800, 800), Image.LANCZOS)
    d = ImageDraw.Draw(im)
    f = ImageFont.truetype(F + "BOD_B.TTF", 190)
    # kleine NT onderaan, binnen de cirkel
    if nt: d.text((400 + 4, 600 + 4), "NT", font=f, fill=(0, 0, 0), anchor="mm")
    if nt: d.text((400, 600), "NT", font=f, fill=WIT, anchor="mm")
    im.save(uit, quality=95)
    m = Image.new("L", (800, 800), 0); ImageDraw.Draw(m).ellipse((0, 0, 800, 800), fill=255)
    rond = Image.new("RGB", (800, 800), (255, 255, 255)); rond.paste(im, (0, 0), m)
    return rond
banner("afbeeldingen/b1.png", "banner-1.jpg")
banner("afbeeldingen/b3.png", "banner-3.jpg")
r1 = logo("afbeeldingen/l1.png", "logo-1.jpg", 680, 360, 720)
r3 = logo("afbeeldingen/l3.png", "logo-3.jpg", 700, 340, 640, nt=False)
# voorbeeldvel: banners zoals op YouTube (alleen het veilige midden op telefoon) + ronde logo's
vel = Image.new("RGB", (2000, 1250), (255, 255, 255))
for k, b in enumerate(["banner-1.jpg", "banner-3.jpg"]):
    vel.paste(Image.open(b).resize((1280, 720)), (0, k * 0 + 0) if k == 0 else (0, 0)) if False else None
b1, b3 = Image.open("banner-1.jpg"), Image.open("banner-3.jpg")
vel.paste(b1.crop((0, 508, 2560, 932)).resize((1500, 248)), (20, 20))
vel.paste(b3.crop((0, 508, 2560, 932)).resize((1500, 248)), (20, 300))
vel.paste(r1.resize((300, 300)), (20, 600)); vel.paste(r3.resize((300, 300)), (360, 600))
vel.paste(r1.resize((88, 88)), (720, 600)); vel.paste(r3.resize((88, 88)), (830, 600))
vel.save("voorbeeld.jpg", quality=90)
