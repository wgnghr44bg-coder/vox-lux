"""Thumbnail v4 'Swapped lives with your dad' (26 nov 2026: CTR oude thumb 0,97% -> eigenaar: "maak een nieuwe thumbnail").
Stijl van de $1 Million-thumbnail van de eigenaar: links/rechts twee scènes, felle tekst op schuine banners, pijlen.
Links: jij (met das van papa) op papa's werk, 240 e-mails, paniek. Rechts: papa terug in de klas, toets 4/10, boos.
Midden: geel rondje met twee draaipijlen (= ruilen). Geen naamlabels (verwarrend bij lichaamsruil).  -> thumb4.jpg
v3 (eigenaar: "het is teveel op een thumbnail"); v4 ("lastig om te zien wie wie is"): jongen KLEIN achter een groot
kantoorbureau met stapels papier, papa GROOT achter een piepklein schoolbankje: alleen 2 poppetjes groot, 1 banner, 4/10 op het bord; vage achtergrond."""
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
# links: kantoor, rechts: klas - iets vaag, zodat de poppetjes eruit springen
im.paste(Image.open(AF / "kantoor.png").convert("RGB").crop((0, 120, 760, 720)).resize((640, 720)).filter(ImageFilter.GaussianBlur(4)), (0, 0))
im.paste(Image.open(AF / "klas.png").convert("RGB").crop((260, 0, 1180, 720)).resize((640, 720)), (640, 0))
d = ImageDraw.Draw(im)
f = lambda m: ps.font(ps.FB, m)
d.text((668, 50), "4/10", font=ps.font(ps.FB, 112), fill=(255, 115, 105), stroke_width=3, stroke_fill=(150, 40, 40))   # toets op het bord
ps.C["jijdas"] = dict(ps.C["you"], hoodie=False, das=(200, 40, 50), shirt=(240, 240, 245))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
ps.poppetje(dl, "jijdas", 330, 735, 1.75, 0.0, kijk=0.0, mond=1.0, verbaasd=True, gebaar="schrik")   # klein: kind
hd = ps.poppetje(dl, "dad", 1045, 960, 2.2, 0.0, kijk=-0.3, mond=0.3, boos=True)                       # groot: volwassene
laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)
d = ImageDraw.Draw(im)
# groot kantoorbureau voor de jongen, met stapels papier
for x0, n in ((70, 11), (470, 14)):
    for k in range(n):
        y = 548 - k * 14; d.rectangle((x0 + (k % 3) * 3, y, x0 + 120 + (k % 3) * 3, y + 12), fill=(250, 250, 250), outline=(150, 150, 160), width=2)
d.rectangle((20, 560, 640, 584), fill=(150, 155, 165), outline=(70, 72, 80), width=4)
d.rectangle((40, 584, 620, 720), fill=(110, 115, 125), outline=(70, 72, 80), width=4)
for k in range(2): d.rectangle((70, 600 + k * 62, 250, 650 + k * 62), outline=(70, 72, 80), width=3); d.rectangle((140, 621 + k * 62, 180, 629 + k * 62), fill=(70, 72, 80))
# piepklein schoolbankje voor papa (komt maar tot zijn heup)
d.rectangle((900, 600, 1190, 628), fill=(205, 150, 90), outline=(110, 70, 40), width=4)
for lx in (920, 1160): d.rectangle((lx, 628, lx + 14, 720), fill=(120, 120, 130))
d.rectangle((940, 578, 1030, 600), fill=(250, 250, 250), outline=(150, 150, 160), width=2)        # toetsblad op het bankje
# kinderpetje met propeller op papa (zoals andere kanalen: kleding van het kind = "hij is nu het kind")
hx, hy = hd[0] / SS if hd[0] > W else hd[0], (hd[1] / SS if hd[1] > H else hd[1]) + 48
d.chord((hx - 168, hy - 105, hx + 168, hy + 150), 180, 360, fill=(230, 60, 60), outline=(25, 20, 30), width=5)
for k, kl in enumerate(((255, 210, 40), (60, 140, 230), (60, 180, 90))):
    d.pieslice((hx - 168, hy - 105, hx + 168, hy + 150), 180 + k * 60 + 10, 180 + k * 60 + 50, fill=kl)
d.chord((hx - 168, hy - 105, hx + 168, hy + 150), 180, 360, outline=(25, 20, 30), width=5)
d.rounded_rectangle((hx + 40, hy + 40, hx + 175, hy + 62), 10, fill=(230, 60, 60), outline=(25, 20, 30), width=4)   # klep
d.rectangle((hx - 4, hy - 118, hx + 4, hy - 80), fill=(25, 20, 30))
d.polygon([(hx, hy - 121), (hx - 70, hy - 138), (hx - 70, hy - 108)], fill=(255, 210, 40), outline=(25, 20, 30))
d.polygon([(hx, hy - 121), (hx + 70, hy - 138), (hx + 70, hy - 108)], fill=(60, 140, 230), outline=(25, 20, 30))
d.ellipse((hx - 9, hy - 130, hx + 9, hy - 112), fill=(230, 60, 60), outline=(25, 20, 30), width=3)
d.line([(640, 0), (640, 720)], fill=(255, 255, 255), width=8)
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
banner("DAD'S JOB?!", 330, 85, (225, 35, 35), 3, 84)
im.save(HIER / "thumb4.jpg", quality=92)
print("thumb4.jpg")
