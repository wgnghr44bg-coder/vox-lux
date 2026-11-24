"""Losse voorwerpen (24 nov, eigenaar: 'meer details, zoals in het echt'): rugzak (AI, witte achtergrond weg) in 5 kleuren,
en de echte koelkast uit de keukenachtergrond (muur weg), zodat de opgetilde koelkast dezelfde is als in de keuken."""
from PIL import Image, ImageDraw, ImageChops
import colorsys
def los(im, tol):                                         # achtergrond vanaf de hoeken wegvullen -> transparant
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox())
rz = los(Image.open("afbeeldingen/rugzak.png"), 30)
for naam, tint in (("rood", 0.0), ("blauw", 0.6), ("geel", 0.13), ("groen", 0.33), ("paars", 0.75)):
    px = rz.load(); im = rz.copy(); q = im.load()
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = px[x, y]
            if a == 0: continue
            h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
            if s > 0.35: h = (h + tint) % 1.0                  # alleen de gekleurde stof, niet het zwart/grijs
            q[x, y] = tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, l, s)) + (a,)
    im.save(f"afbeeldingen/sprite-rugzak-{naam}.png")
kk = Image.open("../proef-pop-short/afbeeldingen/keuken.png").convert("RGB").resize((1080, 1920)).crop((828, 410, 1066, 972))
los(kk, 40).save("afbeeldingen/sprite-koelkast.png")
pl = Image.new("RGBA", (900, 420), (240, 240, 240, 255))
for i, n in enumerate(("rood", "blauw", "geel", "groen", "paars")):
    s = Image.open(f"afbeeldingen/sprite-rugzak-{n}.png"); s.thumbnail((150, 170)); pl.paste(s, (10 + i * 150, 10), s)
k = Image.open("afbeeldingen/sprite-koelkast.png"); k.thumbnail((200, 400)); pl.paste(k, (760, 10), k); pl.convert("RGB").save("sprites-check.jpg")
print("ok")
