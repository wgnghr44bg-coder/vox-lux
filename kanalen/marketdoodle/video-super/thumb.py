"""Thumbnail 'What If Everyone Got Superpowers Overnight?' — vaste stijl (WHATIF-AFSPRAKEN): fel oranje stralen,
1-2 poppetjes met sterke emotie, groot woord op donkere balk met gele rand. Zus zweeft, jij geschrokken."""
import math, os, sys
from pathlib import Path
from PIL import Image, ImageDraw
HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)
W, H = 1280, 720
im = Image.new("RGB", (W, H)); d = ImageDraw.Draw(im)
for y in range(H):
    f = y / H; d.line([(0, y), (W, y)], fill=(int(255 - 20 * f), int(170 - 60 * f), int(60 - 30 * f)))
mid = (640, 430); st = Image.new("RGBA", (W, H), (0, 0, 0, 0)); ds = ImageDraw.Draw(st)
for i in range(18):
    a = i * math.pi / 9
    ds.polygon([mid, (mid[0] + 1600 * math.cos(a), mid[1] + 1600 * math.sin(a)), (mid[0] + 1600 * math.cos(a + 0.14), mid[1] + 1600 * math.sin(a + 0.14))], fill=(255, 235, 150, 70))
im.paste(st, (0, 0), st)
S = ps.SS
laag = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); ps.poppetje(ImageDraw.Draw(laag), "you", 390, 1010, 2.3, 0.0, kijk=1.0, verbaasd=True)
zus = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); ps.poppetje(ImageDraw.Draw(zus), "sis", 920, 600, 1.65, 0.0, kijk=-1.0, gebaar="zwaai")
a_ = zus.split()[3].point(lambda v: 0 if v <= 70 else v); zus.putalpha(a_)                   # geen schaduw onder haar voeten: ze zweeft
laag = laag.resize((W, H), Image.LANCZOS); zus = zus.resize((W, H), Image.LANCZOS)
d = ImageDraw.Draw(im); d.ellipse((830, 680, 1010, 708), fill=(200, 110, 40))                    # schaduw ver onder haar op de grond
for k in range(3): d.line((870 + k * 25, 625 + k * 10, 870 + k * 25, 665 + k * 10), fill=(255, 255, 255), width=6)   # zweef-streepjes
im.paste(laag, (0, 0), laag); im.paste(zus, (0, 0), zus)
for sx, sy, r in ((760, 260, 22), (1110, 330, 18), (1080, 520, 14)):
    p = [(sx + math.cos(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45), sy + math.sin(math.radians(-90 + i * 36)) * (r if i % 2 == 0 else r * 0.45)) for i in range(10)]
    d.polygon(p, fill=(255, 255, 255), outline=(45, 38, 40))
f = ps.font(ps.FB, 112); d = ImageDraw.Draw(im); t = "SUPERPOWERS?!"
b = d.textbbox((0, 0), t, font=f, stroke_width=6); w, h = b[2] - b[0], b[3] - b[1]; x, y = 640 - w / 2, 92 - h / 2 - b[1]
d.rounded_rectangle((640 - w / 2 - 34, 92 - h / 2 - 22, 640 + w / 2 + 34, 92 + h / 2 + 26), 28, fill=(25, 20, 30), outline=(255, 230, 70), width=6)
d.text((x, y), t, font=f, fill=(255, 230, 70), stroke_width=6, stroke_fill=(20, 15, 20))
im.save(HIER / "thumb.jpg", quality=92); print("thumb.jpg")
