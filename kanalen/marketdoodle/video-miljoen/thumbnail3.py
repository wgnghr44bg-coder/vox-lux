"""Thumbnail v3 $1 Million in de vaste Market Doodle-thumbnailstijl (eigenaar 26 nov 2026: "zelfde style ... dan heb ik wat meer
gemeen qua design voor elke thumbnail"; idee van de eigenaar behouden: "$1,000,000" -> "WORTHLESS?").
Stijl (zie WHATIF-AFSPRAKEN.md, Thumbnail): twee scènes links/rechts, witte lijn ertussen, achtergrond iets vaag, poppetjes groot,
max. 2 schuine banners, weinig spullen.  -> thumbnail3.jpg"""
from PIL import Image, ImageDraw, ImageFilter
import maak_miljoen as m

W, H, SS, ps = m.W, m.H, m.SS, m.ps                     # 1920x1080, aan het eind naar 1280x720
img = Image.new("RGB", (W, H))
# links: dag 1, straat met sportwagen
img.paste(m.bg("straat").crop((200, 0, 1160, 1080)).filter(ImageFilter.GaussianBlur(5)), (0, 0))
m.zet(img, "sportwagen", 300, 300, 1060)
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
hl = ps.poppetje(d, "dad", 600, 1560, 3.0, 0.3, kijk=0.0, mond=1.0, gebaar="juich")
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
dd = ImageDraw.Draw(img)
for x, y, a in ((150, 420, -18), (420, 330, 15), (110, 700, 10), (860, 310, -12)):        # een paar briefjes in de lucht
    br = Image.new("RGBA", (170, 86), (0, 0, 0, 0)); bd = ImageDraw.Draw(br)
    bd.rectangle((3, 3, 166, 82), fill=(150, 210, 140), outline=(40, 90, 40), width=6); bd.text((62, 8), "$", font=m.font(m.FB, 56), fill=(40, 90, 40))
    br = br.rotate(a, expand=True, resample=Image.BICUBIC); img.paste(br, (x - br.width // 2, y - br.height // 2), br)
# rechts: dag 30, donkere keuken, traan
rechts = m.bg("keuken-nacht").crop((250, 0, 1210, 1080)).filter(ImageFilter.GaussianBlur(5))
img.paste(Image.blend(rechts, Image.new("RGB", (960, 1080), (12, 14, 34)), 0.45), (960, 0))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
hd = ps.poppetje(d, "dad", 1440, 1560, 3.0, 0.3, kijk=0.0, mond=0.4, verbaasd=True, boos=True)
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
S = 3.0 * ps.C["dad"].get("groot", 1); R = 60 * S; cx, cy = hd[0], hd[1] + R
dd = ImageDraw.Draw(img)
dd.ellipse((cx - R * 0.42 - 20, cy + R * 0.42, cx - R * 0.42 + 20, cy + R * 0.42 + 56), fill=(90, 170, 255), outline=(40, 90, 160), width=4)   # traan
im = img.resize((1280, 720), Image.LANCZOS)
d = ImageDraw.Draw(im); d.line([(640, 0), (640, 720)], fill=(255, 255, 255), width=8)

def banner(tekst, cx, cy, kl, hoek, mx):                  # zelfde banner als video-swap/drie/thumb4.py
    ft = ps.font(ps.FB, mx); b = ImageDraw.Draw(im).textbbox((0, 0), tekst, font=ft, stroke_width=8); w, h = b[2] - b[0], b[3] - b[1]
    ba = Image.new("RGBA", (w + 90, h + 70), (0, 0, 0, 0)); db = ImageDraw.Draw(ba)
    db.polygon([(10, 12), (w + 84, 0), (w + 76, h + 66), (0, h + 58)], fill=kl, outline=(25, 20, 30))
    db.text((45 - b[0], 35 - b[1] - 4), tekst, font=ft, fill="white", stroke_width=8, stroke_fill=(25, 20, 30))
    ba = ba.rotate(hoek, expand=True, resample=Image.BICUBIC)
    sch = Image.new("RGBA", ba.size, (0, 0, 0, 0)); sch.paste((0, 0, 0, 140), (0, 0), ba); sch = sch.filter(ImageFilter.GaussianBlur(6))
    im.paste(sch, (int(cx - ba.width / 2 + 8), int(cy - ba.height / 2 + 10)), sch)
    im.paste(ba, (int(cx - ba.width / 2), int(cy - ba.height / 2)), ba)
banner("$1,000,000", 320, 85, (40, 160, 70), 3, 76)
banner("WORTHLESS?", 960, 85, (225, 35, 35), -3, 76)
im.save(m.HIER / "thumbnail3.jpg", quality=92)
print("thumbnail3.jpg")
