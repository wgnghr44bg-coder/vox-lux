"""Proef "Wat verdient Nvidia aan jouw videokaart? (schattingen met bron)" (22 nov 2026), whiteboard. Cijfers: script.txt.
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
GRENS = [0, 2, 4, 6, 8, 10, 12]
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
# 0 jouw kaart
kop(0, "Your graphics card")
b(0, "n_kaart", 60, 110, 560, 400, kw(0, "graphics", -0.2))
lg(0, "nvidia", 660, 120, 50, kw(0, "nvidia", -0.1))
tx(0, "RTX 5090", 660, 185, 60, IN, kw(0, "rtx"))
tx(0, "$1,999", 660, 255, 120, GR, kw(0, "$1999"), 0.6)
tx(0, "Who gets", 660, 420, 56, BL, kw(1, "who"))
tx(0, "your money?", 660, 485, 56, BL, kw(1, "money", -0.2))
tx(0, "-> follow every $100", 665, 570, 44, GR, kw(1, "follow"))
# 1 waarschuwing
kop(1, "First, a warning")
b(1, "n_slot", 70, 110, 380, 400, kw(2, "nvidia", -0.2))
tx(1, "Nvidia does not say", 500, 150, 54, IN, kw(2, "say", -0.2))
tx(1, "what it makes per card", 500, 215, 54, IN, kw(2, "makes"))
tx(1, "= ESTIMATES", 500, 330, 90, RO, kw(3, "estimates", -0.2), 0.6)
tx(1, "source shown with every number", 505, 460, 40, BL, kw(3, "show"))
# 2 de chip
kop(2, "Step 1: the chip")
b(2, "n_fabriek", 60, 100, 520, 380, kw(4, "chip", -0.2))
lg(2, "tsmc", 640, 120, 50, kw(4, "tsmc", -0.1))
tx(2, "Taiwan", 900, 125, 44, IN, kw(4, "taiwan"))
tx(2, "~$290 to make", 640, 210, 76, IN, kw(5, "$290"), 0.6)
tx(2, "= about $15", 640, 330, 96, RO, kw(5, "$15"), 0.6)
tx(2, "of your $100", 650, 445, 50, IN, kw(5, "hundred", -0.2))
bron(2, "estimate: Tom's Hardware (GB202 chip)", kw(5, "estimates"))
# 3 kaartenbouwers
kop(3, "Step 2: the card makers")
b(3, "n_doos", 60, 100, 500, 330, kw(6, "build", -0.2))
tx(3, "ASUS, MSI, ...", 600, 130, 60, BL, kw(6, "asus"))
b(3, "n_onderdelen", 600, 210, 300, 200, kw(6, "memory", -0.3))
tx(3, "they keep", 600, 440, 50, IN, kw(7, "keep"))
tx(3, "~ $5", 870, 420, 100, RO, kw(7, "$5"), 0.6)
tx(3, "of your $100", 610, 530, 46, IN, kw(7, "hundred", -0.2))
bron(3, "estimate: Jon Peddie Research (2022)", kw(7, "research", -0.3))
# 4 de rest
kop(4, "The other ~$80")
tx(4, "memory & parts", 80, 130, 50, IN, kw(8, "memory"))
tx(4, "shipping", 80, 195, 50, IN, kw(8, "shipping"))
b(4, "n_winkel", 540, 140, 170, 170, kw(8, "shop", -0.3))
tx(4, "the shop", 80, 260, 50, IN, kw(8, "shop"))
tx(4, "Nvidia's chip price", 80, 325, 50, GR, kw(8, "price", -0.3))
b(4, "n_slot", 720, 110, 360, 380, kw(9, "secret", -0.4))
tx(4, "split = secret", 80, 470, 80, RO, kw(9, "secret"), 0.6)
# 5 officieel getal
kop(5, "One official number")
lg(5, "nvidia", 80, 110, 50, kw(10, "nvidia", -0.1))
tx(5, "whole company", 350, 115, 44, IN, kw(10, "company", -0.2))
tx(5, "$74.80", 80, 190, 170, GR, kw(10, "$75"), 0.7)
tx(5, "kept from every $100", 90, 400, 50, IN, kw(10, "hundred", -0.2))
tx(5, "after the cost of making", 90, 465, 44, IN, kw(10, "cost"))
b(5, "n_chips", 760, 160, 400, 300, kw(11, "ai", -0.2))
tx(5, "mostly AI data centers", 760, 480, 44, BL, kw(11, "data", -0.2))
bron(5, "official: NVIDIA Q3 FY2027, GAAP gross margin 74.8%", kw(10, "products", -0.2))
# 6 de bon
kop(6, "Your card's receipt")
t0 = kw(12, "receipt", -0.4)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
tx(6, "RTX 5090, per $100", 105, 125, 32, IN, t0 + 0.3)
rij = [("chip (TSMC)", "~15", RO), ("card maker", "~5", RO), ("memory, parts,", "", IN), ("shop, Nvidia", "~80", RO)]
for n, (lab, bed, kl) in enumerate(rij):
    tx(6, lab, 105, 200 + n * 46, 30, IN, t0 + 0.7 + n * 0.3, 0.3)
    if bed: tx(6, bed, 390, 200 + n * 46, 30, kl, t0 + 0.7 + n * 0.3, 0.3)
streep(6, 105, 400, 460, t0 + 2.0)
tx(6, "NVIDIA keeps", 105, 420, 36, GR, t0 + 2.3, 0.4)
tx(6, "$74.80", 105, 470, 60, GR, t0 + 2.5, 0.4)
tx(6, "whole company, official", 105, 545, 24, IN, t0 + 2.7, 0.4)
tx(6, "~ = estimate", 105, 590, 24, RO, t0 + 2.8, 0.4)
b(6, "n_ontwerp", 620, 110, 380, 300, kw(13, "designing", -0.4))
tx(6, "making it: cheap", 620, 440, 50, IN, kw(13, "cheap", -0.2))
tx(6, "designing it: $$$", 620, 510, 50, GR, kw(13, "designing"))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
