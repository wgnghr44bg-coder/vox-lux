"""Logo + banner Market Doodle in de What If-stijl (eigenaar 23 nov: oude logo/banner passen niet meer).
Zelfde poppetjes als de Short (pop_short.poppetje). Twee varianten: licht (warm) en donker (nacht).
Schrijft branding/logo-licht.png, logo-donker.png (800x800), banner-licht.png, banner-donker.png (2560x1440)."""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pop_short as ps

OUT = Path("branding"); OUT.mkdir(exist_ok=True)
FB = "C:/Windows/Fonts/seguibl.ttf"
GROEN, GEEL = (60, 230, 120), (255, 214, 64)
THEMA = {"licht": dict(bg1=(255, 240, 220), bg2=(250, 222, 190), tekst=(45, 38, 40), sub=(214, 120, 40), ster=None),
         "donker": dict(bg1=(28, 36, 78), bg2=(14, 18, 44), tekst=(255, 255, 255), sub=GEEL, ster=(255, 240, 180))}

def achtergrond(w, h, th):
    im = Image.new("RGB", (w, h)); d = ImageDraw.Draw(im)
    for y in range(h):
        f = y / h; d.line([(0, y), (w, y)], fill=tuple(int(a + (b - a) * f) for a, b in zip(th["bg1"], th["bg2"])))
    if th["ster"]:
        r = random.Random(3)
        for _ in range(int(w * h / 9000)):
            x, y, s = r.random() * w, r.random() * h, r.choice((1.5, 2, 3))
            d.ellipse([x - s, y - s, x + s, y + s], fill=th["ster"])
    return im

def label(im, s, x, y, maat, kl=GROEN):
    f = ImageFont.truetype(FB, maat); b = ImageDraw.Draw(im).textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    laag = Image.new("RGBA", im.size, (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    box = (x - w / 2 - maat * 0.45, y - h / 2 - maat * 0.32, x + w / 2 + maat * 0.45, y + h / 2 + maat * 0.36)
    d.rounded_rectangle(box, int(maat * 0.42), fill=kl + (120,)); g = laag.filter(ImageFilter.GaussianBlur(maat * 0.3)); d2 = ImageDraw.Draw(g)
    d2.rounded_rectangle(box, int(maat * 0.42), fill=(15, 25, 20, 240), outline=kl + (255,), width=max(3, maat // 12))
    d2.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=kl + (255,)); im.paste(g, (0, 0), g)

def poppen(im, lijst):
    """lijst: (naam, x, voet_y, schaal, kijk, verbaasd) -> tekent met supersampling; geeft hoofdtoppen"""
    W, H = im.size; S = ps.SS
    laag = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); toppen = {}
    old = ps.W, ps.H
    for n, x, y, s, kijk, verb in lijst:
        toppen[n] = ps.poppetje(d, n, x, y, s, 0.0, kijk=kijk, verbaasd=verb)
    laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)
    return toppen

def doodles(im, plekken, kleur):
    """simpele getekende icoontjes voor allerlei what-if onderwerpen: planeet, bliksem, klok, hart, ster, raket"""
    S = 2; W, H = im.size; laag = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); L = (45, 38, 40)
    def P(x, y): return (x * S, y * S)
    for soort, x, y, r in plekken:
        lw = int(max(3, r / 9) * S)
        if soort == "planeet":
            d.ellipse([P(x - r * 1.6, y - r * 0.45), P(x + r * 1.6, y + r * 0.45)], outline=L, width=lw)
            d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=(240, 140, 90), outline=L, width=lw)
            d.arc([P(x - r * 1.6, y - r * 0.45), P(x + r * 1.6, y + r * 0.45)], 0, 180, fill=L, width=lw)
        elif soort == "bliksem":
            pts = [(x - r * 0.2, y - r), (x + r * 0.5, y - r), (x + r * 0.1, y - r * 0.1), (x + r * 0.6, y - r * 0.1), (x - r * 0.4, y + r), (x - r * 0.05, y + r * 0.1), (x - r * 0.5, y + r * 0.1)]
            d.polygon([P(*q) for q in pts], fill=(255, 214, 64), outline=L, width=lw)
        elif soort == "klok":
            d.ellipse([P(x - r, y - r), P(x + r, y + r)], fill=(255, 255, 255), outline=L, width=lw)
            d.line([P(x, y), P(x, y - r * 0.65)], fill=L, width=lw); d.line([P(x, y), P(x + r * 0.45, y + r * 0.2)], fill=L, width=lw)
        elif soort == "hart":
            d.ellipse([P(x - r, y - r * 0.7), P(x, y + r * 0.3)], fill=(240, 80, 100)); d.ellipse([P(x, y - r * 0.7), P(x + r, y + r * 0.3)], fill=(240, 80, 100))
            d.polygon([P(x - r * 0.97, y - r * 0.05), P(x + r * 0.97, y - r * 0.05), P(x, y + r)], fill=(240, 80, 100))
        elif soort == "ster":
            pts = [(x + r * (1 if i % 2 == 0 else 0.45) * math.sin(i * math.pi / 5), y - r * (1 if i % 2 == 0 else 0.45) * math.cos(i * math.pi / 5)) for i in range(10)]
            d.polygon([P(*q) for q in pts], fill=(255, 214, 64), outline=L, width=lw)
        elif soort == "brein":
            d.ellipse([P(x - r, y - r * 0.8), P(x + r, y + r * 0.8)], fill=(255, 170, 190), outline=L, width=lw)
            d.line([P(x, y - r * 0.8), P(x, y + r * 0.8)], fill=L, width=lw)
            for k in (-1, 1): d.arc([P(x + k * r * 0.5 - r * 0.3, y - r * 0.4), P(x + k * r * 0.5 + r * 0.3, y + r * 0.2)], 180, 360, fill=L, width=lw)
        elif soort == "vraag":
            f = ImageFont.truetype(FB, int(r * 2 * S)); b = d.textbbox((0, 0), "?", font=f)
            d.text((x * S - (b[2] - b[0]) / 2, y * S - (b[3] - b[1]) / 2 - b[1]), "?", font=f, fill=kleur, stroke_width=int(r / 8 * S), stroke_fill=L)
    laag = laag.resize((W, H), Image.LANCZOS); im.paste(laag, (0, 0), laag)

def tekst(im, s, x, y, maat, kl, rand=None):
    f = ImageFont.truetype(FB, maat); d = ImageDraw.Draw(im); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    if rand: d.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=kl, stroke_width=maat // 12, stroke_fill=rand)
    else: d.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=kl)

for naam, th in [("licht", THEMA["licht"])]:   # 23 nov: eigenaar koos licht
    # logo: jongen (hoofd + schouders) met gloeiend ? erboven, rond uitgesneden door YouTube
    lg = achtergrond(800, 800, th)
    top = poppen(lg, [("you", 400, 1290, 3.6, 0.0, True)])   # 23 nov: verbaasd, ronde mond (eigenaar)
    pass   # 23 nov: logo zonder plaatjes (eigenaar)
    lg.save(OUT / f"logo-{naam}.png")
    # banner 2560x1440; alles belangrijk binnen het midden (1546x423 = veilig op elk scherm)
    bn = achtergrond(2560, 1440, th)
    cx, cy = 1280, 720
    # 23 nov (eigenaar): familiefoto, iedereen dicht bij elkaar, geen plaatjes; tekst links ervan
    poppen(bn, [("dad", 1560, 890, 0.9, -0.2, False), ("mom", 1880, 890, 0.9, -0.3, False),
                ("you", 1665, 900, 0.86, 0.1, False), ("sis", 1785, 905, 0.82, 0.0, False)])
    tekst(bn, "MARKET DOODLE", 1000, cy - 35, 96, th["tekst"])
    tekst(bn, "What if...?", 1000, cy + 62, 62, th["sub"])
    bn.save(OUT / f"banner-{naam}.png")
    # voorbeeld zoals YouTube hem op een pc laat zien (midden 2560x423)
    bn.crop((0, cy - 212, 2560, cy + 211)).resize((1280, 212)).save(OUT / f"banner-{naam}-pc.jpg")
    # rond logo-voorbeeld
    m = Image.new("L", (800, 800), 0); ImageDraw.Draw(m).ellipse([0, 0, 800, 800], fill=255)
    rond = Image.new("RGB", (800, 800), (255, 255, 255)); rond.paste(lg, (0, 0), m); rond.resize((240, 240)).save(OUT / f"logo-{naam}-rond.jpg")
print("KLAAR")
