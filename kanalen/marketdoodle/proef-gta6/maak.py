"""Proef "GTA 6: wat houdt Take-Two over aan jouw exemplaar?" (22 nov 2026), whiteboard. Cijfers + bronnen: script.txt.
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
# 0 intro
kop(0, "GTA 6: what do they keep?")
b(0, "n_game", 60, 110, 520, 420, kw(0, "pay", -0.2))
tx(0, "$79.99", 640, 130, 130, GR, kw(0, "$79"), 0.6)
tx(0, "Grand Theft Auto VI, Standard", 650, 320, 36, IN, kw(0, "grand"))
tx(0, "How much do", 650, 420, 60, BL, kw(1, "how"))
tx(0, "they keep?", 650, 495, 60, BL, kw(1, "keep", -0.2))
# 1 winkel van Sony
kop(1, "Step 1: the store")
b(1, "n_console", 60, 100, 500, 440, kw(2, "playstation", -0.3))
tx(1, "PlayStation Store", 620, 130, 54, BL, kw(2, "sony", -0.2))
tx(1, "takes 30%", 620, 200, 54, IN, kw(2, "30"))
tx(1, "- $24.00", 620, 300, 120, RO, kw(3, "$24"), 0.6)
tx(1, "before anyone else", 630, 440, 46, IN, kw(3, "anyone"))
# 2 Take-Two
kop(2, "Step 2: Take-Two")
b(2, "n_studio", 60, 110, 520, 380, kw(4, "take", -0.2))
tx(2, "Take-Two", 640, 120, 64, BL, kw(4, "take"))
tx(2, "(owns Rockstar Games)", 645, 200, 38, IN, kw(4, "rockstar", -0.2))
tx(2, "gets ~$56", 640, 280, 100, GR, kw(4, "$56"), 0.6)
tx(2, "but first: earn back", 645, 430, 46, RO, kw(5, "earn", -0.2))
tx(2, "what it cost to make", 645, 490, 46, RO, kw(5, "cost", -0.1))
# 3 kosten
kop(3, "What did it cost?")
b(3, "n_slot", 60, 110, 360, 400, kw(6, "never", -0.3))
tx(3, "Rockstar never said", 470, 120, 50, IN, kw(6, "said", -0.2))
tx(3, "$1 - 2 billion", 470, 200, 100, RO, kw(6, "billion", -0.5), 0.7)
tx(3, "estimates by analysts", 480, 320, 36, IN, kw(6, "estimates"))
tx(3, "break even at $56 a copy:", 470, 410, 44, IN, kw(7, "$56"))
tx(3, "18 - 36 million copies", 470, 480, 66, BL, kw(7, "18"), 0.6)
tx(3, "just to break even", 480, 575, 40, RO, kw(7, "even", 0.2))
# 4 verkoop
kop(4, "How many sold?")
b(4, "n_raket", 60, 100, 380, 300, kw(8, "day", -0.2))
tx(4, "day one: ~19 million", 470, 150, 64, GR, kw(8, "19", -0.2), 0.6)
tx(4, "estimate: Sensor Tower", 480, 240, 32, IN, kw(8, "sensor"))
b(4, "n_toren", 60, 400, 220, 260, kw(9, "grand", -0.2))
tx(4, "GTA V: 230+ million", 470, 450, 64, BL, kw(9, "230", -0.2), 0.6)
tx(4, "Take-Two", 480, 540, 32, IN, kw(9, "million"))
# 5 het geheim
kop(5, "The secret")
b(5, "n_teller", 60, 110, 440, 330, kw(10, "secret", -0.2))
tx(5, "after break-even:", 560, 130, 50, IN, kw(10, "once"))
tx(5, "most of each copy", 560, 200, 60, GR, kw(10, "every", -0.2))
tx(5, "= profit", 560, 275, 60, GR, kw(10, "profit", -0.2))
tx(5, "quarter before launch:", 560, 420, 44, IN, kw(11, "quarter", -0.2))
tx(5, "- $54 million", 560, 480, 80, RO, kw(11, "$54"), 0.6)
bron(5, "official: Take-Two Q2 FY2027 (Jul - Sep 2026), GAAP net loss", kw(11, "lost", -0.2))
# 6 bon
kop(6, "Your copy's receipt")
t0 = kw(12, "receipt", -0.4)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
tx(6, "GTA VI Standard", 105, 125, 34, IN, t0 + 0.3)
tx(6, "you pay", 105, 190, 30, IN, t0 + 0.6, 0.3); tx(6, "79.99", 380, 190, 30, BL, t0 + 0.6, 0.3)
tx(6, "Sony store 30%", 105, 236, 30, IN, kw(13, "$24", -0.2), 0.3); tx(6, "-24.00", 368, 236, 30, RO, kw(13, "$24", -0.2), 0.3)
streep(6, 105, 292, 460, kw(13, "$24", 0.3))
tx(6, "Take-Two", 105, 312, 34, GR, kw(13, "$56", -0.2), 0.3); tx(6, "55.99", 380, 312, 32, GR, kw(13, "$56", -0.2), 0.3)
tx(6, "to earn back first:", 105, 370, 28, IN, kw(13, "$56", 0.7), 0.3)
tx(6, "~$1-2 billion", 105, 410, 40, RO, kw(13, "$56", 1.0), 0.3)
tx(6, "= 18-36 million copies", 105, 470, 28, IN, kw(13, "$56", 1.3), 0.3)
tx(6, "~ = estimate", 105, 585, 22, RO, kw(13, "$56", 1.6), 0.3)
b(6, "n_winst", 640, 110, 360, 360, kw(13, "buy", -0.3))
tx(6, "more buyers =", 620, 500, 54, IN, kw(13, "buy"))
tx(6, "more they keep", 620, 565, 54, GR, kw(13, "keep", -0.3))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
