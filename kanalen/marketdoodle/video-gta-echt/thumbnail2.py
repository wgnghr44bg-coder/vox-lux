"""Thumbnail v2 (eigenaar 27 nov: "kun je dat niet zo maken als de cover van GTA 6 zelf maar dan onze style").
Opbouw zoals een game-cover: raster van panelen met witte randen in zonsondergang-kleuren, elk paneel een moment uit de video,
één titelpaneel. GEEN logo of artwork van Rockstar (beschermd): eigen poppetjes, eigen letters.  -> thumbnail2.jpg (+ klein)"""
import math
from PIL import Image, ImageDraw, ImageFilter
import maak_gta as m

W, H, SS, ps, INK = m.W, m.H, m.SS, m.ps, m.INK
PW, PH, RAND = 640, 540, 10                                   # paneel op 1920x1080

def zonsondergang(im, sterk=0.42):                             # roze -> oranje over het hele paneel
    g = Image.new("RGB", im.size); d = ImageDraw.Draw(g)
    for y in range(im.height):
        f = y / im.height; d.line((0, y, im.width, y), fill=(int(255), int(110 + 80 * f), int(170 - 100 * f)))
    return Image.blend(im, g, sterk)
def scene(bgn, figs, extra=None, uitsnede=None):
    img = zonsondergang(m.bg(bgn).copy(), 0.38); m.WACHT.begin(bgn, 0)           # alleen de achtergrond kleuren, poppetjes blijven fel
    if extra: extra(img, "achter")
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    for n, x, y, s, geb, kw_ in figs: koppen[n] = ps.poppetje(d, n, x, y, s, 0.3, gebaar=geb, **kw_)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    if extra: extra(img, "voor", koppen)
    x0, y0, x1, y1 = uitsnede; return img.crop((x0, y0, x1, y1)).resize((PW, PH), Image.LANCZOS)

def sterren(img, cx, y, n, r=40):
    d = ImageDraw.Draw(img)
    for k in range(n):
        x = cx + (k - (n - 1) / 2) * r * 2.2
        pts = [(x + (r if j % 2 == 0 else r * 0.45) * math.sin(j * math.pi / 5), y - (r if j % 2 == 0 else r * 0.45) * math.cos(j * math.pi / 5)) for j in range(10)]
        d.polygon(pts, fill=(255, 255, 255), outline=INK); d.line(pts + [pts[0]], fill=INK, width=6)

# 1. papa met 5 sterren en politieauto
def e1(img, stap, koppen=None):
    if stap == "achter": m.auto(img, "politieauto", 330, 1250, 1000, spiegel=True, bestuurder="agent", t=0.3)
    else: sterren(img, koppen["dad"][0], koppen["dad"][1] - 70, 5)
p1 = scene("straat", [("dad", 760, 1080, 2.2, "hoofdhanden", dict(verbaasd=True, mond=1.0))], e1, (300, 0, 1580, 1080))
# 2. jij met health bar en gele pijl
def e2(img, stap, koppen=None):
    if stap == "voor":
        m.balkje(img, koppen["you"][0], koppen["you"][1] - 60, "HEALTH 100%", 1.0); m.pijl(img, 560, 230, 0.4, 1.4)
p2 = scene("straat", [("you", 960, 1080, 2.3, "wijslinks", dict(mond=0.6))], e2, (320, 0, 1600, 1080))
# 3. mama: mission complete met melk
def e3(img, stap, koppen=None):
    if stap == "achter": m.cirkel(img, 960, 1040, 0.2)
    else:
        hx, hy, S = m.rhand("mom", 960, 1040, 2.2, 70); m.zet(img, "melk", 150, hx, hy + 55, op="hand:mom", punt=(hx, hy))
p3 = scene("winkel", [("mom", 960, 1040, 2.2, "vast", dict(mond=0.5))], e3, (320, 0, 1600, 1080))
# 4. Gary tussen de badeendjes
def e4(img, stap, koppen=None):
    if stap == "achter":
        for j in range(26): x = 120 + (j * 211) % 1700; y = 820 + (j * 97) % 240; m.zet(img, "badeend", 60, x, y, op="weg", spiegel=j % 2 == 1)
    else:
        for j in range(10):
            x = 380 + (j * 173) % 1200; y = 80 + (j * 131) % 500
            if 700 < x < 1220 and y > 250: continue                       # geen eendje voor Gary's gezicht
            s_ = m.sprite("badeend", 60); img.paste(s_, (int(x), int(y)), s_)
p4 = scene("straat", [("buur", 960, 1080, 2.2, "zwaai", dict(mond=0.8))], e4, (320, 0, 1600, 1080))
# 5. zombie-Gary in het keukenraam
def e5(img, stap, koppen=None): pass
z = scene("keuken", [], None, (520, 120, 1280, 760))
gary = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dg = ImageDraw.Draw(gary); ps.poppetje(dg, "buur", 960, 1300, 2.6, 0.3, mond=1.0, verbaasd=True)
gary = gary.resize((W, H), Image.LANCZOS); a = gary.getchannel("A"); r_, g_, b_ = gary.convert("RGB").split()
gary = Image.merge("RGB", (r_.point(lambda v: int(v * 0.55)), g_.point(lambda v: min(255, int(v * 0.95 + 40))), b_.point(lambda v: int(v * 0.5)))).convert("RGBA"); gary.putalpha(a)
keuk = zonsondergang(m.bg("keuken").copy(), 0.5); keuk.paste(gary, (0, 0), gary)
p5 = keuk.crop((320, 0, 1600, 1080)).resize((PW, PH), Image.LANCZOS)
# titelpaneel
tp = Image.new("RGB", (PW, PH)); d = ImageDraw.Draw(tp)
for y in range(PH): f = y / PH; d.line((0, y, PW, y), fill=(int(255 - 60 * f), int(90 + 40 * f), int(160 - 60 * f)))
def tekst(s, y, mx, kl):
    f = ps.font(ps.FB, mx); b = d.textbbox((0, 0), s, font=f, stroke_width=10)
    while b[2] - b[0] > PW - 50: mx -= 4; f = ps.font(ps.FB, mx); b = d.textbbox((0, 0), s, font=f, stroke_width=10)
    d.text(((PW - (b[2] - b[0])) / 2 - b[0], y), s, font=f, fill=kl, stroke_width=10, stroke_fill=(25, 20, 30))
tekst("WHAT IF", 40, 120, (255, 255, 255)); tekst("GTA 6", 175, 190, (255, 214, 64)); tekst("WAS REAL?", 390, 110, (255, 255, 255))

doek = Image.new("RGB", (W, H), (255, 255, 255))
for (k, p) in enumerate((p1, tp, p2, p4, p5, p3)):
    c, r = k % 3, k // 3; doek.paste(p, (c * (PW) + RAND // 2 if c else 0, r * PH + (RAND // 2 if r else 0)))
dd = ImageDraw.Draw(doek)
for c in (1, 2): dd.rectangle((c * PW - RAND // 2, 0, c * PW + RAND // 2, H), fill=(255, 255, 255))
dd.rectangle((0, PH - RAND // 2, W, PH + RAND // 2), fill=(255, 255, 255))
im = doek.resize((1280, 720), Image.LANCZOS)
im.save(m.HIER / "thumbnail2.jpg", quality=92); im.resize((246, 138), Image.LANCZOS).save(m.HIER / "thumbnail2-klein.jpg", quality=92)
print("thumbnail2.jpg")
