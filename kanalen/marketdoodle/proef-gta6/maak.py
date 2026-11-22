"""Proef v2 "GTA 6: je koopt het in de winkel, wie verdient er nu aan?" (22 nov 2026), whiteboard. Cijfers + bronnen: script.txt.
  python maak.py -> scene.json"""
import json, re
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
W = json.load(open("woorden.json", encoding="utf-8"))
def kw(zin, woord, na=0.15):
    for i, w, t0, t1 in W:
        if i == zin and re.sub(r"[^\w$%.\-]", "", w.lower()).startswith(woord.lower()): return round(t0 + na, 2)
    print("LET OP: woord niet gevonden:", zin, woord); return s[zin] + 0.2
A = "afbeeldingen/"; L = "logos/"
BL, RO, GR, IN = [25, 55, 120], [214, 32, 39], [46, 150, 84], [30, 30, 30]
it = []
GRENS = [0, 3, 5, 7, 9, 12, 14]
borden = [0.0] + [s[i] - 0.3 for i in GRENS[1:]]
def b(k, naam, x, y, br, h, t0, dur=1.2):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.3), "kleur": 0.5})
def tx(k, t, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": min(dur, 0.7)})
def kop(k, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": borden[k]})
def lg(k, naam, x, y, h, t0): it.append({"bord": k, "logo": L + naam + ".png", "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
def streep(k, x0, y, x1, t0, kl=IN): it.append({"bord": k, "streep": [x0, y, x1], "kleur": kl, "dik": 4, "start": t0, "teken": 0.6})
def pijl(k, x0, y0, x1, y1, t0, kl=IN): it.append({"bord": k, "pijl": [x0, y0, x1, y1], "kleur": kl, "dik": 6, "start": t0, "teken": 0.5})
def over(k, bedrag, t0): tx(k, f"left: {bedrag}", 820, 600, 46, GR, t0)
def bron(k, t, t0): tx(k, t, 70, 640, 24, IN, t0, 0.4)
# 0 de winkel in
kop(0, "Launch night")
b(0, "n_nacht", 40, 100, 330, 330, kw(0, "walk", -0.3))
b(0, "n_kassa", 400, 100, 380, 330, kw(1, "counter", -0.4))
tx(0, "GTA VI is out!", 820, 110, 46, BL, kw(0, "grand", -0.1))
lg(0, "rockstar", 1165, 95, 66, kw(0, "auto", 0.1))
tx(0, "$79.99", 820, 180, 120, GR, kw(1, "$79"), 0.6)
tx(0, "hmm...", 840, 340, 60, RO, kw(2, "question", -0.2))
tx(0, "How much is everyone", 90, 470, 62, BL, kw(2, "how", -0.1))
tx(0, "earning on this, right now?", 90, 545, 62, BL, kw(2, "earning", -0.1))
# 1 de winkel
kop(1, "Who earns? #1 the store")
b(1, "n_winkel", 60, 110, 420, 420, kw(3, "store", -0.4))
tx(1, "the shop keeps", 540, 140, 56, IN, kw(4, "shop"))
tx(1, "about 30%", 540, 215, 56, IN, kw(4, "30"))
tx(1, "~ $24", 540, 310, 140, RO, kw(4, "$24", -0.1), 0.6)
bron(1, "estimate: game analyst Serkan Toto", kw(4, "analysts"))
# 2 Sony
kop(2, "#2 Sony")
b(2, "n_ps5", 40, 100, 520, 430, kw(5, "playstation", -0.3))
lg(2, "playstation", 1150, 110, 70, kw(5, "disc", -0.1))
tx(2, "Sony wants a share", 600, 120, 50, BL, kw(5, "sony", -0.1))
tx(2, "license fee", 600, 195, 50, IN, kw(6, "license", -0.1))
tx(2, "for every disc", 600, 260, 50, IN, kw(6, "disc", -0.6))
tx(2, "~ $12", 600, 340, 130, RO, kw(6, "$12", -0.1), 0.6)
bron(2, "estimate: about 15% (Serkan Toto)", kw(6, "15"))
# 3 schijf + Take-Two
kop(3, "#3 the disc, #4 Take-Two")
b(3, "n_disc", 60, 100, 360, 290, kw(7, "disc", -0.3))
tx(3, "~ $4", 460, 140, 100, RO, kw(7, "$4"), 0.6)
tx(3, "disc + box", 470, 275, 40, IN, kw(7, "box", -0.1))
tx(3, "+ the trip to the shop", 470, 325, 40, IN, kw(7, "trip", -0.1))
b(3, "n_studio", 60, 410, 330, 230, kw(8, "take", -0.3))
tx(3, "from your $79.99...", 820, 160, 40, IN, kw(8, "$79", -0.1))
tx(3, "Take-Two (Rockstar) gets", 440, 430, 46, BL, kw(8, "rockstar", -0.2))
lg(3, "taketwo", 1080, 500, 100, kw(8, "two", -0.2))
tx(3, "~ $40", 440, 495, 110, GR, kw(8, "$40", -0.1), 0.6)
# 4 nog geen winst
kop(4, "Not profit yet")
b(4, "n_slot", 60, 110, 360, 400, kw(9, "profit", -0.3))
tx(4, "first: earn back the cost", 470, 120, 46, IN, kw(9, "earn", -0.1))
tx(4, "Rockstar never said...", 470, 190, 46, IN, kw(10, "never", -0.1))
tx(4, "$1 - 2 billion", 470, 255, 100, RO, kw(10, "billion", -0.5), 0.7)
tx(4, "estimates by analysts", 480, 380, 34, IN, kw(10, "estimates"))
tx(4, "at $40 a copy:", 470, 440, 44, IN, kw(11, "$40"))
tx(4, "25 - 50 million copies", 470, 495, 66, BL, kw(11, "25"), 0.6)
tx(4, "just to break even", 480, 585, 40, RO, kw(11, "break", -0.1))
# 5 verkocht + digitaal
kop(5, "So far... and a twist")
b(5, "n_raket", 50, 100, 260, 210, kw(12, "day", -0.3))
tx(5, "day one: ~19 million", 320, 150, 44, GR, kw(12, "19", -0.2), 0.6)
tx(5, "estimate: Sensor Tower", 330, 215, 28, IN, kw(12, "sensor"))
b(5, "n_toren", 90, 340, 180, 260, kw(12, "grand", -0.2))
tx(5, "GTA V: 230+ million", 320, 430, 44, BL, kw(12, "230", -0.2), 0.6)
tx(5, "Take-Two", 330, 495, 28, IN, kw(12, "million", 0.2))
b(5, "n_digitaal", 860, 90, 300, 260, kw(13, "twist", -0.3))
tx(5, "bought digital?", 845, 370, 44, IN, kw(13, "digitally"))
tx(5, "no shop, no disc", 845, 430, 38, IN, kw(13, "shop", -0.2))
tx(5, "Sony: 30%", 845, 485, 40, RO, kw(13, "takes", -0.1))
tx(5, "Take-Two: ~$56", 845, 545, 48, GR, kw(13, "$56", -0.2), 0.6)
# 6 bon
kop(6, "Your receipt")
t0 = kw(14, "receipt", -0.4)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
tx(6, "GTA VI, store copy", 105, 125, 32, IN, t0 + 0.3)
lg(6, "rockstar", 432, 108, 44, t0 + 0.5)
tx(6, "you pay", 105, 185, 30, IN, t0 + 0.7, 0.3); tx(6, "79.99", 380, 185, 30, BL, t0 + 0.7, 0.3)
rij = [("the shop", "-24.00", "shop"), ("Sony license", "-12.00", "sony"), ("disc & box", "-4.00", "disc")]
for n, (lab, bed, w) in enumerate(rij):
    tx(6, lab, 105, 230 + n * 44, 30, IN, kw(15, w, -0.3), 0.3); tx(6, bed, 368, 230 + n * 44, 30, RO, kw(15, w, -0.3), 0.3)
streep(6, 105, 368, 460, kw(15, "disc", 0.3))
tx(6, "Take-Two", 105, 385, 36, GR, kw(15, "40", -0.3), 0.3); tx(6, "39.99", 370, 385, 34, GR, kw(15, "40", -0.3), 0.3)
tx(6, "to earn back first:", 105, 450, 26, IN, kw(15, "40", 0.4), 0.3)
tx(6, "~$1-2 billion", 105, 490, 36, RO, kw(15, "40", 0.7), 0.3)
tx(6, "~ = estimate", 105, 585, 22, RO, kw(15, "40", 1.0), 0.3)
b(6, "n_winst", 640, 110, 360, 360, kw(15, "more", -0.3))
tx(6, "more buyers =", 620, 500, 54, IN, kw(15, "people", -0.2))
tx(6, "more they keep", 620, 565, 54, GR, kw(15, "keep", -0.3))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
