"""Proef eigen piraat 'Captain Discount' (26 nov 2026, eigenaar vroeg om een bekend personage zoals Jack Sparrow).
Bewust GEEN Jack Sparrow (Disney): eigen piratenkapitein in de pop_short-stijl. -> piraat-proef.jpg"""
import os, sys
from pathlib import Path
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)

ps.C["piraat"] = dict(broek=(95, 70, 50), shirt=(240, 232, 210), haar=(45, 32, 25), kapsel="kort", groot=1.12)
INK = (40, 35, 40)
W, H, SS = 1080, 1350, ps.SS
img = Image.open(HIER.parent / "short-blackfriday" / "afbeeldingen" / "winkel.png").convert("RGB").resize((1080, 1920)).crop((0, 300, 1080, 1650))

def piraat(img, x, y, s, gebaar=None, mond=0.6):
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    hx, top = ps.poppetje(d, "piraat", x, y, s, 0.3, kijk=0.3, mond=mond, gebaar=gebaar)
    laag = laag.resize((W, H), Image.LANCZOS)
    S = s * ps.C["piraat"]["groot"]; R = 60 * S; cy = top + R
    img.paste(laag, (0, 0), laag)
    d = ImageDraw.Draw(img)
    # lange donkere haarslierten met kraaltjes langs beide kanten van het hoofd, over de schouders
    for k, dx in enumerate((-1.18, -1.0, 1.0, 1.18)):
        sx = hx + dx * R; lang = (1.45 if k % 2 else 1.2) * R
        d.rounded_rectangle((sx - 0.09 * R, cy - 0.15 * R, sx + 0.09 * R, cy + lang), int(0.09 * R), fill=(45, 32, 25), outline=INK, width=3)
        by = cy + lang - 0.25 * R; d.ellipse((sx - 0.12 * R, by - 0.12 * R, sx + 0.12 * R, by + 0.12 * R), fill=(230, 180, 60), outline=INK, width=2)
    # rode bandana met witte stippen + slipjes links
    d.chord((hx - 1.03 * R, cy - 1.04 * R, hx + 1.03 * R, cy + 0.35 * R), 180, 360, fill=(200, 40, 45), outline=INK, width=4)
    for q in range(4): d.ellipse((hx - 0.62 * R + q * 0.4 * R, cy - 0.5 * R, hx - 0.52 * R + q * 0.4 * R, cy - 0.4 * R), fill=(255, 235, 235))
    d.polygon([(hx - 0.98 * R, cy - 0.3 * R), (hx - 1.4 * R, cy - 0.05 * R), (hx - 1.25 * R, cy + 0.12 * R), (hx - 0.93 * R, cy - 0.12 * R)], fill=(200, 40, 45), outline=INK)
    # driekantige hoed die óp het hoofd zit (rand rust op de bandana)
    d.polygon([(hx - 1.35 * R, cy - 0.95 * R), (hx, cy - 0.68 * R), (hx + 1.35 * R, cy - 0.95 * R), (hx + 0.85 * R, cy - 1.55 * R), (hx, cy - 1.45 * R), (hx - 0.85 * R, cy - 1.55 * R)],
              fill=(80, 55, 40), outline=INK)
    d.line([(hx - 1.3 * R, cy - 0.95 * R), (hx, cy - 0.72 * R), (hx + 1.3 * R, cy - 0.95 * R)], fill=(210, 170, 80), width=7)
    # zwarte snor met omhoog gekrulde puntjes, net boven de mond, sikje eronder, gouden tand
    for kant in (-1, 1):
        d.polygon([(hx, cy + 0.36 * R), (hx + kant * 0.3 * R, cy + 0.34 * R), (hx + kant * 0.42 * R, cy + 0.24 * R), (hx + kant * 0.4 * R, cy + 0.42 * R), (hx + kant * 0.05 * R, cy + 0.45 * R)], fill=(35, 25, 20), outline=INK)
    d.polygon([(hx - 0.13 * R, cy + 0.78 * R), (hx + 0.13 * R, cy + 0.78 * R), (hx, cy + 1.12 * R)], fill=(35, 25, 20), outline=INK)
    d.rectangle((hx + 0.03 * R, cy + 0.44 * R, hx + 0.15 * R, cy + 0.54 * R), fill=(240, 200, 60), outline=INK, width=2)
    # rode sjerp om het middel + kompas in de hand
    heup = y - 78 * S - 14 * S
    d.rectangle((x - 50 * S, heup - 18 * S, x + 50 * S, heup + 4 * S), fill=(200, 40, 45), outline=INK, width=4)
    d.polygon([(x + 30 * S, heup + 4 * S), (x + 52 * S, heup + 50 * S), (x + 34 * S, heup + 52 * S)], fill=(200, 40, 45), outline=INK)
    return hx, cy

piraat(img, 540, 1250, 2.6)
f = ps.font(ps.FB, 74); d = ImageDraw.Draw(img)
d.text((540, 90), "CAPTAIN DISCOUNT", font=f, fill=(255, 215, 60), anchor="mm", stroke_width=7, stroke_fill=(20, 20, 30))
img.save(HIER / "piraat-proef.jpg", quality=92); print("piraat-proef.jpg")
