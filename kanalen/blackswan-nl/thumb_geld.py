"""Geldverhaal-thumbnail (eigenaar 21 nov: "moet echt anders, lijkt teveel op Swan").
Eigen stijl: beeld over de hele thumbnail, zwarte tekst in gouden balken, getal wit in een rood blok, Segoe UI Black, logo rechtsboven.
Gebruik: python thumb_geld.py <beeld> "<BOVEN>" "<GETAL>" "<ONDER>" uit.jpg   (env: ZOOM, MIDX 0-1, MIDY 0-1, DONKER 0-1)"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
W, H = 1280, 720
GOUD, ZWART, ROOD, WIT = (246, 190, 40), (12, 12, 14), (214, 32, 39), (255, 255, 255)
FB = "C:/Windows/Fonts/seguibl.ttf" if os.path.exists("C:/Windows/Fonts/seguibl.ttf") else "C:/Windows/Fonts/segoeuib.ttf"
beeld, boven, getal, onder, uit = sys.argv[1:6]
im = Image.open(beeld).convert("RGB")
s = max(W / im.width, H / im.height) * float(os.environ.get("ZOOM", "1.0"))
im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
mx, my = float(os.environ.get("MIDX", "0.5")), float(os.environ.get("MIDY", "0.5"))
x0 = int(min(max(mx * im.width - W / 2, 0), im.width - W)); y0 = int(min(max(my * im.height - H / 2, 0), im.height - H))
im = im.crop((x0, y0, x0 + W, y0 + H))
im = ImageEnhance.Brightness(im).enhance(float(os.environ.get("DONKER", "0.85")))
im = ImageEnhance.Contrast(im).enhance(1.12); im = ImageEnhance.Color(im).enhance(1.15)
d = ImageDraw.Draw(im)

def balk(tekst, x, y, maat, kleur_bg, kleur_tekst, schaduw=True):
    f = ImageFont.truetype(FB, maat); bb = d.textbbox((0, 0), tekst, font=f)
    w, h = bb[2] - bb[0], bb[3] - bb[1]; px, py = int(maat * 0.28), int(maat * 0.18)
    r = (x, y, x + w + 2 * px, y + h + 2 * py)
    if schaduw:
        sch = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sch).rounded_rectangle((r[0] + 8, r[1] + 10, r[2] + 8, r[3] + 10), 14, fill=(0, 0, 0, 150))
        im.paste(sch.filter(ImageFilter.GaussianBlur(6)), (0, 0), sch.filter(ImageFilter.GaussianBlur(6)))
    d.rounded_rectangle(r, 14, fill=kleur_bg)
    d.text((x + px - bb[0], y + py - bb[1]), tekst, font=f, fill=kleur_tekst)
    return r

r1 = balk(boven, 48, 52, 86, GOUD, ZWART) if boven else (48, 52, 48, 30)   # lege BOVEN = geen bovenbalk (bv. als het logo al in beeld staat)
r2 = balk(getal, 48, r1[3] + 22, 150 if boven else 190, ROOD, WIT)
balk(onder, 48, H - 160, 82, GOUD, ZWART)
lg = Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "branding", "logo-definitief.png")).convert("RGB").resize((96, 96))
m = Image.new("L", (96, 96), 0); ImageDraw.Draw(m).ellipse([0, 0, 95, 95], fill=255); im.paste(lg, (W - 96 - 32, 28), m)
im.save(uit, quality=93); print(uit)
