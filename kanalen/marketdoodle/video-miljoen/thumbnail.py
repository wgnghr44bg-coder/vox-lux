"""Thumbnail "DAY 1 vs DAY 30" (eigenaar 24 nov: maar 1 thumbnail). Links: blij, roze sportwagen, juichen. Rechts: donkere
keuken, kaarslicht, kippen op tafel, papa met dikke wang. Zelfde poppetjes en achtergronden als de video.
  python thumbnail.py  -> thumbnail.jpg (1280x720)"""
import math
from PIL import Image, ImageDraw, ImageFilter
import maak_miljoen as m

W, H, SS, ps = m.W, m.H, m.SS, m.ps
img = Image.new("RGB", (W, H))

# ---- links: DAY 1 ----
L = m.bg("straat").crop((260, 0, 1220, 1080)); img.paste(L, (0, 0))
m.zet(img, "sportwagen", 120, 150, 760, tint=0.15); m.zet(img, "sportwagen", 120, 520, 760, tint=0.6)
m.zet(img, "sportwagen", 300, 420, 1060)
for k in range(12):                                       # geld dat naar beneden dwarrelt (achter de poppetjes)
    x = 40 + (k * 151) % 820; y = 250 + (k * 97) % 330; a = (k * 37) % 50 - 25
    br = Image.new("RGBA", (110, 56), (0, 0, 0, 0)); bd = ImageDraw.Draw(br)
    bd.rectangle((2, 2, 107, 53), fill=(150, 210, 140), outline=(40, 90, 40), width=4); bd.text((36, 8), "$", font=m.font(m.FB, 34), fill=(40, 90, 40))
    br = br.rotate(a, expand=True, resample=Image.BICUBIC); img.paste(br, (x, y), br)
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
ps.poppetje(d, "dad", 470, 1050, 1.75, 0.3, kijk=0.3, mond=0.9, gebaar="juich")
ps.poppetje(d, "mom", 720, 1060, 1.65, 0.7, kijk=-0.3, mond=0.9, gebaar="juich")
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)

# ---- rechts: DAY 30 ----
R = m.bg("keuken-nacht").crop((300, 0, 1260, 1080)); img.paste(R, (960, 0))
donker = Image.new("RGB", (960, 1080), (12, 14, 34)); img.paste(Image.blend(img.crop((960, 0, 1920, 1080)), donker, 0.55), (960, 0))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
hd = ps.poppetje(d, "dad", 1190, 1080, 2.15, 0.3, kijk=0.4, mond=0.0, boos=True)
ps.poppetje(d, "mom", 1700, 1090, 2.0, 0.6, kijk=-0.5, mond=0.0, boos=True)
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
S = 2.15 * ps.C["dad"].get("groot", 1); m.wang(img, hd[0], hd[1], S, 0.0)
dd = ImageDraw.Draw(img)
dd.rectangle((990, 880, 1920, 925), fill=(150, 105, 65), outline=m.INK, width=6)          # keukentafel voor ze
dd.rectangle((1005, 925, 1920, 1080), fill=(125, 85, 52), outline=m.INK, width=5)
m.kaars(img, 0.4, 1470, 880)
gloed = Image.new("L", (W, H), 0); ImageDraw.Draw(gloed).ellipse((1270, 600, 1670, 1000), fill=110)
gloed = gloed.filter(ImageFilter.GaussianBlur(70)); geel = Image.new("RGB", (W, H), (255, 190, 90))
img.paste(geel, (0, 0), gloed.point(lambda v: v // 2))
m.zet(img, "kip", 170, 1110, 885); m.zet(img, "kip", 150, 1560, 885, spiegel=True)

# ---- scheiding + tekst ----
dd = ImageDraw.Draw(img)
dd.polygon([(930, 0), (990, 0), (990, 1080), (930, 1080)], fill=(255, 255, 255)); dd.line((960, 0, 960, 1080), fill=m.INK, width=6)
m.kop(img, "DAY 1", 300, 120, 170, (90, 230, 110), 1)
m.kop(img, "DAY 30", 1460, 120, 170, (240, 70, 60), 1)
img.resize((1280, 720), Image.LANCZOS).save(m.HIER / "thumbnail.jpg", quality=92)
print("thumbnail.jpg")
