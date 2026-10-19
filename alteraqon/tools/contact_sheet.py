"""Overzichtsplaat van de beelden in een videomap (om op de iPhone te bekijken).

Gebruik:  python alteraqon/tools/contact_sheet.py <map> <uit.jpg> [kolommen=3]
Leest <map>/afbeeldingen/*.png|jpg in de volgorde van prompts.txt en zet de naam (bijv. L01) linksboven op elk beeld.
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

folder, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 3
names = [l.split("|", 1)[0] for l in open(os.path.join(folder, "prompts.txt"), encoding="utf-8") if "|" in l and not l.startswith("#")]
imgs = []
for n in names:
    for ext in (".png", ".jpg"):
        p = os.path.join(folder, "afbeeldingen", n + ext)
        if os.path.exists(p): imgs.append((n, Image.open(p).convert("RGB"))); break
if not imgs: sys.exit("Geen beelden gevonden.")
W = 480; H = round(W * imgs[0][1].height / imgs[0][1].width); GAP = 8
rows = -(-len(imgs) // cols)
sheet = Image.new("RGB", (cols * W + (cols + 1) * GAP, rows * H + (rows + 1) * GAP), (16, 16, 16))
try: font = ImageFont.truetype("arial.ttf", 44)
except OSError: font = ImageFont.load_default()
for k, (n, im) in enumerate(imgs):
    x, y = GAP + (k % cols) * (W + GAP), GAP + (k // cols) * (H + GAP)
    sheet.paste(im.resize((W, H)), (x, y))
    d = ImageDraw.Draw(sheet); d.rectangle((x, y, x + 110, y + 60), fill=(0, 0, 0)); d.text((x + 12, y + 6), n, fill=(255, 255, 255), font=font)
sheet.save(out, quality=88)
print(f"{len(imgs)} beelden -> {out}")
