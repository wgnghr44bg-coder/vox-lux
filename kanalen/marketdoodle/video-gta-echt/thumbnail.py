"""Thumbnail What If GTA 6 Was Real Life? in de vaste Market Doodle-stijl (zie WHATIF-AFSPRAKEN.md, Thumbnail): twee scènes
links/rechts, witte lijn, achtergrond iets vaag, poppetjes groot, max. 2 schuine banners, weinig spullen.
Links: papa laat een kauwgompapiertje vallen ("GUM WRAPPER"). Rechts: zelfde straat, papa geschrokken, 5 sterren, politieauto ("5 STARS?!").
-> thumbnail.jpg (1280x720) + thumbnail-klein.jpg (246x138, telefoon-controle)"""
from PIL import Image, ImageDraw, ImageFilter
import maak_gta as m

W, H, SS, ps = m.W, m.H, m.SS, m.ps
img = Image.new("RGB", (W, H))
img.paste(m.bg("straat").crop((100, 0, 1060, 1080)).filter(ImageFilter.GaussianBlur(5)), (0, 0))
rechts = m.bg("straat").crop((860, 0, 1820, 1080)).filter(ImageFilter.GaussianBlur(5))
img.paste(rechts, (960, 0))
# rechts: politieauto achter papa (met agent achter het stuur)
m.WACHT.begin("straat", 0)
m.auto(img, "politieauto", 300, 1500, 1020, spiegel=True, bestuurder="agent", t=0.3)
m.sirene(img, 1500, 720, 0.0)
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
hl = ps.poppetje(d, "dad", 430, 1180, 2.1, 0.3, kijk=0.4, mond=0.2, gebaar=("hoek", -16, 25))
hr = ps.poppetje(d, "dad", 1250, 1180, 2.1, 0.3, kijk=0.0, mond=1.0, verbaasd=True, gebaar="hoofdhanden")
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
dd = ImageDraw.Draw(img)
S = 2.35 * ps.C["dad"].get("groot", 1); hx, hy, _ = m.rhand("dad", 430, 1180, 2.1, 25)
pap = Image.new("RGBA", (170, 100), (0, 0, 0, 0)); pd = ImageDraw.Draw(pap)                      # kauwgompapiertje valt uit de hand
pd.rectangle((4, 4, 166, 96), fill=(215, 220, 230), outline=(40, 35, 40), width=7); pd.line((20, 50, 150, 50), fill=(170, 175, 190), width=6); pap = pap.rotate(-20, expand=True, resample=Image.BICUBIC)
img.paste(pap, (int(hx + 10), int(hy - 20)), pap)
for k in range(3): dd.line((hx + 40 + k * 26, hy - 50, hx + 52 + k * 26, hy - 20), fill=(255, 255, 255), width=6)   # valstreepjes
for k in range(5):                                                                            # 5 grote sterren
    import math as _m; x = hr[0] + (k - 2) * 118; y = hr[1] - 80; r = 56
    pts = [(x + (r if j % 2 == 0 else r * 0.45) * _m.sin(j * _m.pi / 5), y - (r if j % 2 == 0 else r * 0.45) * _m.cos(j * _m.pi / 5)) for j in range(10)]
    dd.polygon(pts, fill=(255, 255, 255), outline=(40, 35, 40)); dd.line(pts + [pts[0]], fill=(40, 35, 40), width=7)
im = img.resize((1280, 720), Image.LANCZOS)
d = ImageDraw.Draw(im); d.line([(640, 0), (640, 720)], fill=(255, 255, 255), width=8)
def banner(tekst, cx, cy, kl, hoek, mx):
    ft = ps.font(ps.FB, mx); b = ImageDraw.Draw(im).textbbox((0, 0), tekst, font=ft, stroke_width=8); w, h = b[2] - b[0], b[3] - b[1]
    ba = Image.new("RGBA", (w + 90, h + 70), (0, 0, 0, 0)); db = ImageDraw.Draw(ba)
    db.polygon([(10, 12), (w + 84, 0), (w + 76, h + 66), (0, h + 58)], fill=kl, outline=(25, 20, 30))
    db.text((45 - b[0], 35 - b[1] - 4), tekst, font=ft, fill="white", stroke_width=8, stroke_fill=(25, 20, 30))
    ba = ba.rotate(hoek, expand=True, resample=Image.BICUBIC)
    sch = Image.new("RGBA", ba.size, (0, 0, 0, 0)); sch.paste((0, 0, 0, 140), (0, 0), ba); sch = sch.filter(ImageFilter.GaussianBlur(6))
    im.paste(sch, (int(cx - ba.width / 2 + 8), int(cy - ba.height / 2 + 10)), sch)
    im.paste(ba, (int(cx - ba.width / 2), int(cy - ba.height / 2)), ba)
banner("GUM WRAPPER", 320, 80, (40, 160, 70), 3, 70)
banner("5 STARS?!", 960, 80, (225, 35, 35), -3, 80)
im.save(m.HIER / "thumbnail.jpg", quality=92); im.resize((246, 138), Image.LANCZOS).save(m.HIER / "thumbnail-klein.jpg", quality=92)
print("thumbnail.jpg")
