"""Bordje met bedrag in tekenstijl (crème bordje, dikke rand, schreeflettertype), zoals het voorbeeld van de eigenaar."""
import sys
from PIL import Image, ImageDraw, ImageFont
FONT = "C:/Windows/Fonts/rockb.ttf"
def bordje(im, tekst, cx, cy, maat=110):
    d = ImageDraw.Draw(im); f = ImageFont.truetype(FONT, maat)
    b = d.textbbox((0, 0), tekst, font=f); w, h = b[2]-b[0], b[3]-b[1]
    pw, ph = int(maat*.55), int(maat*.42); x0, y0 = cx-w//2-pw, cy-h//2-ph; x1, y1 = cx+w//2+pw, cy+h//2+ph
    d.rounded_rectangle((x0, y0, x1, y1), 18, fill=(30, 28, 32))
    d.rounded_rectangle((x0+10, y0+10, x1-10, y1-10), 12, fill=(238, 228, 208))
    d.rounded_rectangle((x0+20, y0+20, x1-20, y1-20), 8, outline=(30, 28, 32), width=4)
    d.text((cx-w//2-b[0], cy-h//2-b[1]), tekst, font=f, fill=(22, 22, 48))
if __name__ == "__main__":
    i, t, uit = sys.argv[1], sys.argv[2], sys.argv[3]; cx, cy = float(sys.argv[4]), float(sys.argv[5])
    im = Image.open(i).convert("RGB"); bordje(im, t, int(cx*im.width), int(cy*im.height)); im.save(uit, quality=92)
