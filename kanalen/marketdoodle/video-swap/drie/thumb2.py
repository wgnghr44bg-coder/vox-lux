"""Thumbnail v2 'Swapped lives with your dad' (26 nov 2026: CTR oude thumb 0,97% -> eigenaar: "maak een nieuwe thumbnail").
Stijl van de $1 Million-thumbnail van de eigenaar: links/rechts twee scènes, felle tekst op schuine banners, pijlen.
Links: jij (met das van papa) op papa's werk, 240 e-mails, paniek. Rechts: papa terug in de klas, toets 4/10, boos.
Midden: geel rondje met twee draaipijlen (= ruilen). Geen naamlabels (verwarrend bij lichaamsruil).  -> thumb2.jpg"""
import math, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent.parent / "proef-pop-short")
import pop_short as ps
os.chdir(_c)

W, H, SS = 1280, 720, ps.SS
AF = HIER.parent / "afbeeldingen"
im = Image.new("RGB", (W, H))
# links: kantoor (linker bureau met scherm), rechts: klas (schoolbord)
im.paste(Image.open(AF / "kantoor.png").convert("RGB").crop((0, 120, 760, 720)).resize((760, 600)).resize((640, 720)), (0, 0))
im.paste(Image.open(AF / "klas.png").convert("RGB").crop((260, 0, 1180, 720)).resize((640, 720)), (640, 0))
d = ImageDraw.Draw(im)
f = lambda m: ps.font(ps.FB, m)

# scherm met 240 ongelezen e-mails (op het bureau links)
d.rectangle((500, 365, 545, 400), fill=(45, 50, 62))                       # voet van het scherm
d.rectangle((380, 398, 640, 418), fill=(150, 155, 165), outline=(70, 72, 80), width=3)   # bureaublad (zoals de bureaus in het kantoor)
d.rectangle((395, 418, 640, 720), fill=(105, 110, 120), outline=(70, 72, 80), width=3)
for k in range(3): d.rectangle((410, 440 + k * 85, 520, 510 + k * 85), outline=(70, 72, 80), width=3); d.rectangle((450, 470 + k * 85, 480, 478 + k * 85), fill=(70, 72, 80))
d.rounded_rectangle((420, 215, 625, 365), 14, fill=(45, 50, 62), outline=(25, 25, 30), width=6)
d.rectangle((434, 229, 611, 351), fill=(235, 240, 248))
for k in range(5):
    d.rectangle((442, 238 + k * 22, 603, 252 + k * 22), fill=(255, 255, 255), outline=(200, 205, 215))
    d.rectangle((446, 241 + k * 22, 456, 249 + k * 22), fill=(220, 50, 50))

d.ellipse((515, 160, 620, 265), fill=(225, 35, 35), outline=(255, 255, 255), width=6)
b = d.textbbox((0, 0), "240", font=f(46)); d.text((567 - (b[2] + b[0]) / 2, 212 - (b[3] + b[1]) / 2), "240", font=f(46), fill="white")

# toets 4/10 op het schoolbord (rechts), in krijt
kr = (245, 245, 235)
d.text((680, 95), "TEST", font=ps.font(ps.FS, 54), fill=kr)
d.text((680, 160), "4/10", font=ps.font(ps.FB, 104), fill=(255, 120, 110))
d.ellipse((660, 150, 915, 300), outline=(255, 120, 110), width=7)

# poppetjes, groot en dichtbij
ps.C["jijdas"] = dict(ps.C["you"], hoodie=False, das=(200, 40, 50), shirt=(240, 240, 245))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
ps.poppetje(dl, "jijdas", 250, 1010, 2.5, 0.0, kijk=-0.6, mond=1.0, verbaasd=True, gebaar="schrik")
ps.poppetje(dl, "dad", 1085, 1050, 2.3, 0.0, kijk=0.5, mond=0.3, boos=True, gebaar="heupen")
laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)

# zweetdruppel bij jou
d = ImageDraw.Draw(im)
d.polygon([(395, 300), (380, 340), (410, 340)], fill=(120, 200, 255)); d.ellipse((379, 325, 411, 357), fill=(120, 200, 255))

# scheiding: bliksem-lijn
d.line([(648, 0), (628, 300), (660, 330), (632, 720)], fill=(255, 230, 70), width=14)
d.line([(648, 0), (628, 300), (660, 330), (632, 720)], fill=(255, 255, 255), width=5)

# midden: ruil-rondje
cx, cy, r = 640, 560, 78
d.ellipse((cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6), fill=(25, 20, 30)); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 220, 50))
for a0, a1 in ((200, 330), (20, 150)):
    d.arc((cx - 48, cy - 48, cx + 48, cy + 48), a0, a1, fill=(25, 20, 30), width=14)
    ae = math.radians(a1); px, py = cx + 48 * math.cos(ae), cy + 48 * math.sin(ae); tx, ty = -math.sin(ae), math.cos(ae)
    nx, ny = math.cos(ae), math.sin(ae)
    d.polygon([(px + tx * 26, py + ty * 26), (px + nx * 22, py + ny * 22), (px - nx * 22, py - ny * 22)], fill=(25, 20, 30))

# banners (schuin, zoals WORTHLESS?)
def banner(tekst, cx, cy, kl, hoek, m):
    ft = f(m); b = ImageDraw.Draw(im).textbbox((0, 0), tekst, font=ft, stroke_width=8); w, h = b[2] - b[0], b[3] - b[1]
    ba = Image.new("RGBA", (w + 90, h + 70), (0, 0, 0, 0)); db = ImageDraw.Draw(ba)
    db.polygon([(10, 12), (w + 84, 0), (w + 76, h + 66), (0, h + 58)], fill=kl, outline=(25, 20, 30))
    db.text((45 - b[0], 35 - b[1] - 4), tekst, font=ft, fill="white", stroke_width=8, stroke_fill=(25, 20, 30))
    ba = ba.rotate(hoek, expand=True, resample=Image.BICUBIC)
    sch = Image.new("RGBA", ba.size, (0, 0, 0, 0)); sch.paste((0, 0, 0, 140), (0, 0), ba); sch = sch.filter(ImageFilter.GaussianBlur(6))
    im.paste(sch, (int(cx - ba.width / 2 + 8), int(cy - ba.height / 2 + 10)), sch)
    im.paste(ba, (int(cx - ba.width / 2), int(cy - ba.height / 2)), ba)
banner("DAD'S JOB", 330, 90, (225, 35, 35), 3, 78)
banner("SCHOOL?!", 990, 640, (40, 110, 220), -3, 78)
im.save(HIER / "thumb2.jpg", quality=92)
im.resize((320, 180), Image.LANCZOS).save(HIER / "thumb2-klein.jpg", quality=90)
print("thumb2.jpg")
