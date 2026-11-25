"""Meetraster over een achtergrond (1920x1080) leggen, zodat Claude de vlakken (vloer, aanrecht, tafel, stoep, muur) en
meubels kan opmeten voor de scènewachter (tools/scenewachter.py, achtergronden.json).

  python tools/meet_achtergrond.py <achtergrond.png> [<uit.jpg>]

Rode streepjes om de 100 px (x) en 50 px (y), met getallen in 1920x1080-coördinaten. Uitvoer op 1280x720.
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def raster(pad, uit=None):
    im = Image.open(pad).convert("RGB").resize((1920, 1080)); d = ImageDraw.Draw(im)
    f = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 22)
    for x in range(0, 1920, 100):
        d.line((x, 0, x, 1080), fill=(255, 0, 0), width=1); d.text((x + 3, 4), str(x), fill=(255, 0, 0), font=f)
    for y in range(0, 1080, 50):
        d.line((0, y, 1920, y), fill=(255, 0, 0) if y % 100 == 0 else (255, 150, 150), width=1)
        d.text((4, y + 2), str(y), fill=(255, 0, 0), font=f)
    uit = Path(uit or Path(pad).with_suffix(".raster.jpg")); im.resize((1280, 720)).save(uit, quality=85); return uit

if __name__ == "__main__":
    print(raster(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None))
