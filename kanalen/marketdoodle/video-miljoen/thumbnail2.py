"""Thumbnail v2 (na kijken bij The Infographics Show / What If, 24 nov): gezichten groot en dichtbij, dagen in witte
vlakken met zwarte letters (zoals hun '3:33 AM | 3:39 AM', 20 mln. views), sterke emotie links/rechts.  -> thumbnail2.jpg"""
from PIL import Image, ImageDraw, ImageFilter
import maak_miljoen as m

W, H, SS, ps = m.W, m.H, m.SS, m.ps
img = Image.new("RGB", (W, H))
# links: DAY 1
img.paste(m.bg("straat").crop((200, 150, 1160, 1230 if False else 1080)).resize((960, 1080)), (0, 0))
m.zet(img, "sportwagen", 330, 330, 1090)
for k in range(10):
    x = 30 + (k * 173) % 860; y = 230 + (k * 113) % 300; a = (k * 37) % 50 - 25
    br = Image.new("RGBA", (130, 66), (0, 0, 0, 0)); bd = ImageDraw.Draw(br)
    bd.rectangle((2, 2, 127, 63), fill=(150, 210, 140), outline=(40, 90, 40), width=5); bd.text((44, 8), "$", font=m.font(m.FB, 42), fill=(40, 90, 40))
    br = br.rotate(a, expand=True, resample=Image.BICUBIC); img.paste(br, (x, y), br)
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
ps.poppetje(d, "dad", 560, 1500, 3.1, 0.3, kijk=0.2, mond=1.0, gebaar="juich")
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
# rechts: DAY 30
img.paste(m.bg("keuken-nacht").crop((250, 60, 1210, 1140)).resize((960, 1080)), (960, 0))
img.paste(Image.blend(img.crop((960, 0, 1920, 1080)), Image.new("RGB", (960, 1080), (12, 14, 34)), 0.55), (960, 0))
gloed = Image.new("L", (W, H), 0); ImageDraw.Draw(gloed).ellipse((1350, 650, 1850, 1150), fill=120)
gloed = gloed.filter(ImageFilter.GaussianBlur(80)); img.paste(Image.new("RGB", (W, H), (255, 190, 90)), (0, 0), gloed.point(lambda v: v // 2))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
hd = ps.poppetje(d, "dad", 1370, 1520, 3.1, 0.3, kijk=0.3, mond=0.5, verbaasd=True, boos=True)
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
S = 3.1 * ps.C["dad"].get("groot", 1); m.wang(img, hd[0], hd[1], S, 0.0)
dd = ImageDraw.Draw(img); R = 60 * S; cx, cy = hd[0], hd[1] + R
dd.ellipse((cx - R * 0.5 - 16, cy + R * 0.05, cx - R * 0.5 + 16, cy + R * 0.05 + 44), fill=(90, 170, 255), outline=(40, 90, 160), width=3)   # traan
m.kaars(img, 0.4, 1640, 1075)
m.zet(img, "kip", 230, 1790, 1085, spiegel=True)
# scheiding + dagen in witte vlakken
dd = ImageDraw.Draw(img); dd.rectangle((950, 0, 970, 1080), fill=(255, 255, 255))
import sys
TEKSTEN = {"A": ("RICH!", "BROKE"), "B": ("$1,000,000", "WORTHLESS"), "C": ("WE'RE RICH", "WE'RE DOOMED")}
basis = img.copy(); uit = []
for k, (links, rechts) in TEKSTEN.items():
    im = basis.copy()
    for tekst, x, kl in ((links, 480, (90, 230, 110)), (rechts, 1440, (240, 70, 60))):
        f = 150
        while ImageDraw.Draw(im).textlength(tekst, font=m.font(m.FB, f)) > 860: f -= 4
        m.kop(im, tekst, x, 130, f, kl, 1)
    im.resize((1280, 720), Image.LANCZOS).save(m.HIER / f"thumbnail-{k}.jpg", quality=92); uit.append(k)
v = Image.new("RGB", (1280, 720 * 3 + 40), "white")
for i, k in enumerate(uit):
    v.paste(Image.open(m.HIER / f"thumbnail-{k}.jpg"), (0, i * 740)); ImageDraw.Draw(v).text((20, i * 740 + 640), k, font=m.font(m.FB, 70), fill=(255, 230, 0), stroke_width=6, stroke_fill=(0, 0, 0))
v.save(m.HIER / "thumbnail-teksten.jpg", quality=88); print("ok")
