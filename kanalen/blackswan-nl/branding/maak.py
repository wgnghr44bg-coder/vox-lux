"""Het Geldverhaal: logo (800x800) en banner (2560x1440, veilige zone 1546x423 midden). Eigen ontwerp, geen internetbeelden."""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, sys
GOUD, WIT, ZWART = (222, 170, 60), (245, 245, 245), (8, 8, 10)
FB = "C:/Windows/Fonts/segoeuib.ttf"

def logo(stijl, S=1600):
    im = Image.new("RGB", (S, S), ZWART); d = ImageDraw.Draw(im)
    c = S // 2
    if stijl == "munt":
        r = int(S * 0.36)
        d.ellipse((c - r, c - r, c + r, c + r), outline=GOUD, width=int(S * 0.035))
        f = ImageFont.truetype(FB, int(S * 0.46))
        w = f.getlength("G"); bb = f.getbbox("G")
        d.text((c - w / 2, c - (bb[1] + bb[3]) / 2), "G", font=f, fill=WIT)
        # stijgende lijn met pijl door de G
        pts = [(c - r * 0.62, c + r * 0.38), (c - r * 0.2, c + r * 0.05), (c + r * 0.08, c + r * 0.2), (c + r * 0.6, c - r * 0.42)]
        d.line(pts, fill=GOUD, width=int(S * 0.04), joint="curve")
        x, y = pts[-1]; a = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]); L = S * 0.09
        d.polygon([(x + math.cos(a) * L * 0.6, y + math.sin(a) * L * 0.6),
                   (x + math.cos(a + 2.4) * L, y + math.sin(a + 2.4) * L), (x + math.cos(a - 2.4) * L, y + math.sin(a - 2.4) * L)], fill=GOUD)
    else:  # boek: open boek, de bladzijden vormen een stijgende lijn
        w, h = S * 0.62, S * 0.36; x0, y0 = c - w / 2, c - h / 2 + S * 0.05
        lw = int(S * 0.035)
        for kant in (-1, 1):
            punten = [(c, y0 + h), (c + kant * w / 2, y0 + h - S * 0.05), (c + kant * w / 2, y0 - S * 0.02), (c, y0 + S * 0.05)]
            d.line(punten + [punten[0]], fill=WIT, width=lw, joint="curve")
        pts = [(c - w * 0.42, y0 + h * 0.62), (c - w * 0.15, y0 + h * 0.35), (c + w * 0.05, y0 + h * 0.48), (c + w * 0.42, y0 - h * 0.32)]
        d.line(pts, fill=GOUD, width=int(S * 0.04), joint="curve")
        x, y = pts[-1]; a = math.atan2(pts[-1][1] - pts[-2][1], pts[-1][0] - pts[-2][0]); L = S * 0.09
        d.polygon([(x + math.cos(a) * L * 0.6, y + math.sin(a) * L * 0.6),
                   (x + math.cos(a + 2.4) * L, y + math.sin(a + 2.4) * L), (x + math.cos(a - 2.4) * L, y + math.sin(a - 2.4) * L)], fill=GOUD)
    return im.resize((800, 800), Image.LANCZOS)

def banner(achter, lg, uit):
    W, H = 2560, 1440
    bg = Image.open(achter).convert("RGB"); s = max(W / bg.width, H / bg.height)
    bg = bg.resize((int(bg.width * s) + 1, int(bg.height * s) + 1), Image.LANCZOS)
    bg = bg.crop(((bg.width - W) // 2, (bg.height - H) // 2, (bg.width - W) // 2 + W, (bg.height - H) // 2 + H))
    donker = Image.new("RGB", (W, H), ZWART); bg = Image.blend(bg, donker, 0.25)
    # donkere zachte band achter de tekst (veilige zone midden), zodat de tekst altijd leesbaar is
    m = Image.new("L", (W, H), 0); ImageDraw.Draw(m).rounded_rectangle((W/2-900, H/2-260, W/2+900, H/2+200), 120, fill=235)
    m = m.filter(ImageFilter.GaussianBlur(90)); bg.paste(donker, (0, 0), m)
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(FB, 150); f2 = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 54)
    t1a, t1b = "Het ", "Geldverhaal"; t2 = "Geld, bedrijven en beleggen. Helder uitgelegd."
    lgk = lg.resize((230, 230), Image.LANCZOS)
    bw = 230 + 40 + f1.getlength(t1a + t1b); x = (W - bw) / 2; y = H / 2 - 150
    rond = Image.new("L", lgk.size, 0); ImageDraw.Draw(rond).ellipse((4, 4, 226, 226), fill=255)
    bg.paste(lgk, (int(x), int(y) - 10), rond)
    tx = x + 270
    d.text((tx, y), t1a, font=f1, fill=WIT); d.text((tx + f1.getlength(t1a), y), t1b, font=f1, fill=GOUD)
    d.text(((W - f2.getlength(t2)) / 2, y + 250), t2, font=f2, fill=(220, 220, 220))
    bg.save(uit, quality=92)

if __name__ == "__main__":
    for st in ("munt", "boek"):
        logo(st).save(f"logo-{st}.png")
    for b in "abc":
        banner(f"ai/afbeeldingen/banner-{b}.png", Image.open("logo-munt.png"), f"banner-{b}.jpg")
