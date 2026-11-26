"""Thumbnail v3 'Swapped lives with your dad' (26 nov 2026: CTR oude thumb 0,97% -> eigenaar: "maak een nieuwe thumbnail").
Stijl van de $1 Million-thumbnail van de eigenaar: links/rechts twee scènes, felle tekst op schuine banners, pijlen.
Links: jij (met das van papa) op papa's werk, 240 e-mails, paniek. Rechts: papa terug in de klas, toets 4/10, boos.
Midden: geel rondje met twee draaipijlen (= ruilen). Geen naamlabels (verwarrend bij lichaamsruil).  -> thumb3.jpg
v3 (eigenaar: "het is teveel op een thumbnail"): alleen 2 poppetjes groot, 1 banner, 4/10 op het bord; vage achtergrond."""
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
d.text((675, 45), "4/10", font=ps.font(ps.FB, 128), fill=(255, 115, 105), stroke_width=3, stroke_fill=(150, 40, 40))   # toets op het bord
ps.C["jijdas"] = dict(ps.C["you"], hoodie=False, das=(200, 40, 50), shirt=(240, 240, 245))
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
ps.poppetje(dl, "jijdas", 295, 1080, 2.75, 0.0, kijk=0.0, mond=1.0, verbaasd=True, gebaar="schrik")
ps.poppetje(dl, "dad", 1065, 1190, 2.6, 0.0, kijk=-0.3, mond=0.3, boos=True)
laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)
d = ImageDraw.Draw(im)
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
im.save(HIER / "thumb3.jpg", quality=92)
print("thumb3.jpg")
