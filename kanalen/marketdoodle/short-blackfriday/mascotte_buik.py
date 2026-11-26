"""Zet de winkelnaam CHEAPZILLA (verzonnen winkel) op de gele buik van de dino-mascotte -> afbeeldingen/mascotte-buik.png"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
H = Path(__file__).parent
im = Image.open(H / "afbeeldingen" / "mascotte.png").convert("RGB"); d = ImageDraw.Draw(im)
sx, sy = im.width / 1088, im.height / 1920                      # buik gemeten op 1088x1920: midden (580, 1160), breed ~440
f = ImageFont.truetype("C:/Windows/Fonts/seguibl.ttf", int(118 * sx))
for k, (w, kl) in enumerate((("CHEAP", (220, 40, 45)), ("ZILLA", (40, 110, 60)))):
    d.text((580 * sx, (1095 + k * 130) * sy), w, font=f, fill=kl, anchor="mm", stroke_width=int(6 * sx), stroke_fill=(255, 255, 255))
im.save(H / "afbeeldingen" / "mascotte-buik.png"); print("mascotte-buik.png")
