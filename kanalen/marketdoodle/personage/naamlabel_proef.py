"""Proef naambalkje onder een echt persoon (26 nov 2026). Denny's 1993, zittend, gewone 2D-stijl."""
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
from jensen_proef import JENSEN_1993
ps.C["jensen93"] = JENSEN_1993
ps.C["chris"] = dict(broek=(80, 70, 60), shirt=(150, 190, 230), haar=(80, 55, 35), kapsel="kort", baard=True, groot=1.12)
ps.C["curtis"] = dict(broek=(60, 70, 90), shirt=(80, 130, 80), haar=(120, 80, 45), kapsel="krul", baard=True, bril=True, groot=1.1)
W, H, SS, INK = 1080, 1920, ps.SS, (40, 35, 40)
img = Image.open(HIER.parent / "short-nvidia" / "afbeeldingen" / "denny.png").convert("RGB").resize((W, H)); d = ImageDraw.Draw(img)
TY = 1450
d.rounded_rectangle((60, TY - 520, 1020, TY + 20), 30, fill=(205, 60, 60), outline=INK, width=5)
laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
for n, x in (("chris", 560), ("curtis", 820), ("jensen93", 300)):
    ps.poppetje(dl, n, x, TY + 170, 1.9, 0.3, kijk=0.3 if n == "jensen93" else -0.3, mond=0.5 if n == "jensen93" else 0.0, gebaar=("hoek", -16, 55))
laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); d = ImageDraw.Draw(img)
d.rectangle((40, TY, 1040, TY + 40), fill=(235, 230, 220), outline=INK, width=5); d.rounded_rectangle((30, TY + 58, 1050, H + 40), 26, fill=(205, 60, 60), outline=INK, width=5)
d.polygon([(380, TY - 6), (510, TY - 10), (530, TY + 24), (390, TY + 28)], fill=(252, 252, 248), outline=INK)
# kleine naamlabels boven de hoofden, in de oude stijl (ps.label, zoals vroeger DAD / MOM / SIS)
ps.W, ps.H = W, H
for naam, x, kl in (("JENSEN", 300, (118, 185, 0)), ("CHRIS", 560, (120, 200, 255)), ("CURTIS", 820, (255, 190, 80))):
    ps.label(img, naam, x, 905, kl, 0.62)
d = ImageDraw.Draw(img)
d.text((540, 1780), "HEY KID.", font=ps.font(ps.FS, 58), fill=(255, 215, 60), anchor="mm", stroke_width=6, stroke_fill=(0, 0, 0))
img.resize((540, 960)).save(HIER / "naamlabel-proef.jpg", quality=90); print("ok")
