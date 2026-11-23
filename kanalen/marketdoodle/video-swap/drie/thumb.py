"""Thumbnail 'Swapped lives with your dad' — stijl van proef-pop-short/thumb.py (fel oranje stralen, emotie, groot woord)."""
import math, os, sys
from pathlib import Path
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent.parent / "proef-pop-short")
import pop_short as ps
from branding import tekst
os.chdir(_c)
import maak3 as m3

W, H = 1280, 720
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
for y in range(H):
    f = y / H; d.line([(0, y), (W, y)], fill=(int(255 - 20 * f), int(170 - 60 * f), int(60 - 30 * f)))
mid = (640, 420); st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
for i in range(18):
    a = i * math.pi / 9
    ds.polygon([mid, (mid[0] + 1600 * math.cos(a), mid[1] + 1600 * math.sin(a)), (mid[0] + 1600 * math.cos(a + 0.14), mid[1] + 1600 * math.sin(a + 0.14))], fill=(255, 235, 150, 70))
im.paste(st, (0, 0), st)
S = ps.SS; laag = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
papa = ps.poppetje(dl, "dad", 330, 1000, 2.05, 0.0, kijk=1.0, verbaasd=True)            # jij, in papa's lijf
jij = ps.poppetje(dl, "you", 960, 1010, 2.25, 0.0, kijk=-1.0, boos=True)                # papa, in jouw lijf
laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)
for (x, y), (s, kl) in ((papa, ("YOU", (70, 130, 220))), (jij, ("DAD", (90, 180, 110)))):
    f = ps.font(ps.FB, 44); dd = ImageDraw.Draw(im); b = dd.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    dd.rounded_rectangle((x - w / 2 - 20, y - 70 - h / 2 - 12, x + w / 2 + 20, y - 70 + h / 2 + 14), 16, fill=kl, outline=(40, 35, 40), width=4)
    dd.text((x - w / 2, y - 70 - h / 2 - b[1]), s, font=f, fill=(255, 255, 255))
tekst(im, "I'M MY DAD?!", 640, 95, 110, (255, 230, 70), rand=(30, 25, 30))
im.save(HIER / "thumb.jpg", quality=92); print("thumb.jpg")
