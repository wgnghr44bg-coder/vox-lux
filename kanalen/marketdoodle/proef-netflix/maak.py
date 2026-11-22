"""Proef "Follow the Dollar: Netflix (Q3 2026, SEC, GAAP)" (22 nov 2026), whiteboard. Cijfers: script.txt.
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
GRENS = [0, 2, 3, 4, 6, 8, 10]
borden = [0.0] + [s[i] - 0.3 for i in GRENS[1:]]
def b(k, naam, x, y, br, h, t0, dur=1.2):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.3), "kleur": 0.5})
def tx(k, t, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": min(dur, 0.7)})
def kop(k, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": borden[k]})
def lg(k, naam, x, y, h, t0): it.append({"bord": k, "logo": L + naam + ".png", "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
def streep(k, x0, y, x1, t0, kl=IN): it.append({"bord": k, "streep": [x0, y, x1], "kleur": kl, "dik": 4, "start": t0, "teken": 0.6})
def pijl(k, x0, y0, x1, y1, t0, kl=IN): it.append({"bord": k, "pijl": [x0, y0, x1, y1], "kleur": kl, "dik": 6, "start": t0, "teken": 0.5})
def over(k, bedrag, t0): tx(k, f"left: {bedrag}", 820, 600, 46, GR, t0)
def over(k, bedrag, t0): tx(k, f"left: {bedrag}", 820, 600, 46, GR, t0)
# 0 de dollar
kop(0, "Follow the dollar: Netflix")
b(0, "n_geld", 70, 110, 520, 380, kw(0, "$100", -0.1))
tx(0, "$100", 650, 150, 130, GR, kw(0, "$100", 0.1), 0.6)
lg(0, "netflix", 660, 340, 60, kw(0, "netflix", -0.1))
tx(0, "How much does", 650, 450, 50, BL, kw(1, "how"))
tx(0, "Netflix keep?", 650, 515, 50, BL, kw(1, "keep", -0.2))
# 1 omzet
kop(1, "Last quarter")
lg(1, "netflix", 70, 110, 50, kw(2, "netflix", -0.1))
tx(1, "$12.9 billion", 70, 190, 100, BL, kw(2, "$12"), 0.7)
tx(1, "revenue, Jul - Sep 2026", 75, 320, 40, IN, kw(2, "billion"))
b(1, "n_tv", 700, 140, 480, 400, kw(2, "quarter", -0.3))
# 2 inhoud
kop(2, "Step 1: what you watch")
b(2, "n_film", 60, 100, 540, 400, kw(3, "content", -0.2))
tx(2, "shows, movies,", 660, 130, 46, IN, kw(3, "shows"))
tx(2, "getting them to you", 660, 190, 46, IN, kw(3, "getting"))
tx(2, "- $47.22", 660, 290, 120, RO, kw(3, "$47"), 0.6)
over(2, "$52.78", kw(3, "$47", 1.0))
# 3 app, reclame, kantoren
kop(3, "Step 2: app, ads, offices")
b(3, "n_app", 60, 100, 330, 250, kw(4, "engineers", -0.2))
tx(3, "- $8.02", 420, 140, 80, RO, kw(4, "$8"), 0.6)
tx(3, "engineers & app", 430, 235, 38, IN, kw(4, "$8", 0.4))
b(3, "n_kantoor", 60, 380, 260, 230, kw(5, "ads", -0.2))
tx(3, "- $6.50", 420, 390, 80, RO, kw(5, "$6"), 0.6)
tx(3, "ads & marketing", 430, 485, 38, IN, kw(5, "$6", 0.5))
tx(3, "- $3.62", 800, 140, 80, RO, kw(5, "$3"), 0.6)
tx(3, "offices & managers", 810, 235, 38, IN, kw(5, "$3", 0.4))
over(3, "$34.63", kw(5, "$3", 0.2))
# 4 rente + belasting
kop(4, "Step 3: debt, then taxes")
b(4, "n_bank", 60, 100, 340, 260, kw(6, "debt", -0.3))
tx(4, "- $1.10", 440, 140, 90, RO, kw(6, "$1"), 0.6)
tx(4, "interest (net)", 450, 245, 40, IN, kw(6, "$1", 0.5))
b(4, "n_overheid", 60, 390, 360, 250, kw(7, "government", -0.2))
tx(4, "- $5.07", 440, 420, 90, RO, kw(7, "$5"), 0.6)
tx(4, "taxes", 450, 525, 40, IN, kw(7, "$5", 0.5))
over(4, "$28.46", kw(7, "$5", 0.2))
# 5 winst
kop(5, "What is left")
b(5, "n_winst", 70, 100, 480, 480, kw(8, "left", -0.4))
tx(5, "$28", 620, 140, 200, GR, kw(9, "$28"), 0.6)
tx(5, "profit from", 640, 400, 56, BL, kw(9, "profit"))
tx(5, "every $100", 640, 470, 56, BL, kw(9, "$100", -0.2))
# 6 bon
kop(6, "Netflix's receipt")
t0 = kw(10, "receipt", -0.4)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
lg(6, "netflix", 170, 110, 36, t0 + 0.3)
tx(6, "per $100 you pay", 105, 165, 30, IN, t0 + 0.5)
rij = [("shows & movies", "-47.22"), ("engineers & app", "-8.02"), ("ads & marketing", "-6.50"), ("offices", "-3.62"), ("interest", "-1.10"), ("taxes", "-5.07")]
for n, (lab, bed) in enumerate(rij):
    tx(6, lab, 105, 215 + n * 42, 30, IN, t0 + 0.8 + n * 0.25, 0.3); tx(6, bed, 372, 215 + n * 42, 30, RO, t0 + 0.8 + n * 0.25, 0.3)
streep(6, 105, 478, 460, t0 + 2.4)
tx(6, "PROFIT", 105, 495, 44, GR, t0 + 2.7, 0.4); tx(6, "$28.46", 300, 495, 44, GR, t0 + 2.7, 0.4)
tx(6, "NETFLIX Q3 2026 GAAP, rounded", 105, 580, 20, IN, t0 + 2.9, 0.4)
tx(6, "almost half:", 600, 150, 54, IN, kw(11, "half", -0.2))
tx(6, "what you watch", 600, 215, 54, BL, kw(11, "watch", -0.3))
tx(6, "more than 1/4:", 600, 340, 54, IN, kw(11, "quarter", -0.3))
tx(6, "pure profit", 600, 405, 54, GR, kw(11, "profit", -0.2))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
