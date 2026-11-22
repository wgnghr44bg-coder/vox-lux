"""Proef "Follow the Dollar: Nvidia" (22 nov 2026): één dollar volgen door het bedrijf, op whiteboard. Cijfers: script.txt (SEC, GAAP).
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
GRENS = [0, 2, 4, 6, 9, 11, 13]
borden = [0.0] + [s[i] - 0.3 for i in GRENS[1:]]
def b(k, naam, x, y, br, h, t0, dur=1.2):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.3), "kleur": 0.5})
def tx(k, t, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": min(dur, 0.7)})
def kop(k, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": borden[k]})
def lg(k, naam, x, y, h, t0): it.append({"bord": k, "logo": L + naam + ".png", "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
def streep(k, x0, y, x1, t0, kl=IN): it.append({"bord": k, "streep": [x0, y, x1], "kleur": kl, "dik": 4, "start": t0, "teken": 0.6})
def pijl(k, x0, y0, x1, y1, t0, kl=IN): it.append({"bord": k, "pijl": [x0, y0, x1, y1], "kleur": kl, "dik": 6, "start": t0, "teken": 0.5})
def over(k, bedrag, t0): tx(k, f"left: {bedrag}", 820, 600, 46, GR, t0)

# 0 de dollar
kop(0, "Follow the dollar: Nvidia")
b(0, "n_geld", 70, 110, 520, 380, kw(0, "$100", -0.1))
tx(0, "$100", 650, 150, 130, GR, kw(0, "$100", 0.1), 0.6)
lg(0, "nvidia", 660, 345, 60, kw(0, "nvidia", -0.1))
pijl(0, 590, 300, 645, 360, kw(0, "pays"))
tx(0, "How much does", 650, 450, 50, BL, kw(1, "follow"))
tx(0, "Nvidia keep?", 650, 515, 50, BL, kw(1, "keep", -0.2))
# 1 omzet
kop(1, "Last quarter")
lg(1, "nvidia", 70, 95, 44, kw(2, "nvidia", -0.1))
tx(1, "$115.8 billion", 70, 160, 92, BL, kw(2, "$115"), 0.7)
tx(1, "revenue, Aug - Oct 2026", 75, 280, 36, IN, kw(2, "billion"))
it.append({"bord": 1, "delen": [93, 7], "x": 120, "y": 360, "straal": 150, "start": kw(3, "$93", -0.2), "teken": 1.6})
tx(1, "$93 of every $100", 470, 420, 54, GR, kw(3, "$93"))
tx(1, "= AI data centers", 470, 495, 54, GR, kw(3, "data", -0.2))
b(1, "n_datacenter", 900, 100, 330, 250, kw(3, "data", -0.3))
# 2 stap 1: chips bouwen
kop(2, "Step 1: building the chips")
b(2, "n_fabriek", 60, 100, 560, 400, kw(4, "chips", -0.2))
tx(2, "factories, materials,", 660, 130, 44, IN, kw(5, "factories"))
tx(2, "partners like", 660, 190, 44, IN, kw(5, "partners"))
lg(2, "tsmc", 950, 190, 50, kw(5, "tsmc", -0.1))
tx(2, "- $25.18", 660, 300, 120, RO, kw(5, "$25"), 0.6)
over(2, "$74.82", kw(5, "$25", 1.0))
# 3 stap 2: onderzoek + kantoren
kop(3, "Step 2: brains and offices")
b(3, "n_lamp", 60, 100, 420, 300, kw(6, "engineers", -0.2))
tx(3, "- $6.43", 520, 150, 96, RO, kw(7, "$6"), 0.6)
tx(3, "research", 530, 260, 44, IN, kw(7, "research", 0.4))
b(3, "n_kantoor", 60, 420, 300, 230, kw(8, "sales", -0.2))
tx(3, "- $1.47", 520, 430, 96, RO, kw(8, "half"), 0.6)
tx(3, "sales & offices", 530, 540, 44, IN, kw(8, "half", 0.4))
over(3, "$66.92", kw(8, "dollars", 0.5))
# 4 stap 3: extraatje + belasting
kop(4, "Step 3: a bonus, then taxes")
b(4, "n_kluis", 60, 100, 340, 260, kw(9, "cash", -0.2))
tx(4, "+ $1.29", 440, 140, 90, GR, kw(9, "$1"), 0.6)
tx(4, "cash & investments", 450, 245, 40, IN, kw(9, "$1", 0.5))
b(4, "n_overheid", 60, 390, 360, 250, kw(10, "government", -0.2))
tx(4, "- $11.85", 440, 420, 90, RO, kw(10, "$12"), 0.6)
tx(4, "taxes", 450, 525, 40, IN, kw(10, "$12", 0.5))
over(4, "$56.36", kw(10, "$12", 1.1))
# 5 wat blijft over
kop(5, "What is left")
b(5, "n_winst", 70, 100, 480, 480, kw(11, "left", -0.4))
tx(5, "$56", 620, 140, 200, GR, kw(12, "$56"), 0.6)
tx(5, "profit from", 640, 400, 56, BL, kw(12, "profit"))
tx(5, "every $100", 640, 470, 56, BL, kw(12, "$100", -0.2))
# 6 de bon
kop(6, "Nvidia's receipt")
t0 = kw(13, "receipt", -0.4)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
lg(6, "nvidia", 160, 110, 40, t0 + 0.3)
tx(6, "per $100 of revenue", 105, 170, 30, IN, t0 + 0.5)
rij = [("chips & factories", "-25.18", RO), ("research", "-6.43", RO), ("sales & offices", "-1.47", RO), ("investments", "+1.29", GR), ("taxes", "-11.85", RO)]
for n, (lab, bed, kl) in enumerate(rij):
    tx(6, lab, 105, 225 + n * 44, 30, IN, t0 + 0.9 + n * 0.3, 0.3); tx(6, bed, 372, 225 + n * 44, 30, kl, t0 + 0.9 + n * 0.3, 0.3)
streep(6, 105, 462, 460, t0 + 2.6)
tx(6, "PROFIT", 105, 480, 44, GR, t0 + 3.0, 0.4); tx(6, "$56.36", 300, 480, 44, GR, t0 + 3.0, 0.4)
tx(6, "NVIDIA Q3 FY2027 (GAAP)", 105, 570, 22, IN, t0 + 3.2, 0.4)
tx(6, "why investors", 600, 150, 54, GR, kw(14, "investors"))
tx(6, "love it", 600, 215, 54, GR, kw(14, "love"))
tx(6, "the big risk:", 600, 340, 54, RO, kw(15, "risk", -0.2))
tx(6, "customers pay less", 600, 410, 46, IN, kw(15, "pay"))
tx(6, "-> $56 shrinks fast", 600, 475, 46, RO, kw(15, "shrink", -0.2))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
