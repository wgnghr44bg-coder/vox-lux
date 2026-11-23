"""Thumbnail What If (eigenaar 23 nov): zoals de kleine what-if kanalen die winnen: fel, één groot woord/getal,
poppetje met sterke emotie. Zelfde poppetjes als de video (pop_short.poppetje). Schrijft thumb.jpg (1280x720)."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pop_short as ps
from branding import label, tekst

W, H = 1280, 720
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
for y in range(H):                                    # fel oranje-geel verloop
    f = y / H; d.line([(0, y), (W, y)], fill=(int(255 - 20 * f), int(170 - 60 * f), int(60 - 30 * f)))
mid = (900, 330); stralen = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(stralen)
for i in range(18):                                   # stralen achter de rijke jongen
    a = i * math.pi / 9
    ds.polygon([mid, (mid[0] + 1600 * math.cos(a), mid[1] + 1600 * math.sin(a)), (mid[0] + 1600 * math.cos(a + 0.14), mid[1] + 1600 * math.sin(a + 0.14))], fill=(255, 235, 150, 70))
im.paste(stralen, (0, 0), stralen)
S = ps.SS; laag = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
rijk = ps.poppetje(dl, "rich", 900, 860, 1.75, 0.0, kijk=-0.4)
jij = ps.poppetje(dl, "you", 300, 1010, 2.45, 0.0, kijk=1.0, verbaasd=True)
laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)
label(im, "$2,300,000", rijk[0], rijk[1] - 60, 64, (255, 205, 60))
tekst(im, "HE EARNS", 330, 90, 86, (255, 255, 255), rand=(30, 25, 30))
tekst(im, "WHAT?!", 330, 190, 100, (255, 230, 70), rand=(30, 25, 30))
im.save("thumb.jpg", quality=92); print("thumb.jpg")
