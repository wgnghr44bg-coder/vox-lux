"""Proef 2 "Netflix: wat houden ze over aan jouw abonnement?" (22 nov 2026), whiteboard, echte bedragen. Cijfers: script.txt.
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
GRENS = [0, 2, 3, 5, 7, 9, 12]
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
# 0 intro
kop(0, "Netflix: what do they keep?")
b(0, "n_tv", 60, 110, 520, 430, kw(0, "pay", -0.2))
lg(0, "netflix", 650, 130, 60, kw(0, "netflix", -0.1))
tx(0, "You pay every month.", 650, 230, 50, IN, kw(0, "month", -0.3))
tx(0, "How much is", 650, 330, 66, BL, kw(0, "how"))
tx(0, "pure profit?", 650, 410, 66, GR, kw(0, "profit", -0.3))
tx(0, "-> the real numbers", 655, 530, 44, IN, kw(1, "real", -0.2))
# 1 omzet
kop(1, "Last quarter")
lg(1, "netflix", 70, 110, 50, kw(2, "netflix", -0.1))
tx(1, "$12.9 billion", 70, 190, 100, BL, kw(2, "$12"), 0.7)
tx(1, "came in, Jul - Sep 2026", 75, 320, 40, IN, kw(2, "billion"))
b(1, "n_geld", 700, 160, 480, 340, kw(2, "took", -0.3))
# 2 inhoud
kop(2, "The biggest bill")
b(2, "n_film", 60, 100, 540, 400, kw(3, "watch", -0.4))
tx(2, "shows, movies,", 660, 130, 46, IN, kw(4, "shows"))
tx(2, "getting them to you", 660, 190, 46, IN, kw(4, "getting"))
tx(2, "- $6.1 billion", 660, 290, 90, RO, kw(4, "$6"), 0.6)
over(2, "$6.8 billion", kw(4, "billion", 0.4))
# 3 app, reclame, kantoren
kop(3, "App, ads, offices")
b(3, "n_app", 60, 100, 330, 250, kw(5, "engineers", -0.2))
tx(3, "- $1.0 billion", 420, 140, 70, RO, kw(5, "$1"), 0.6)
tx(3, "engineers & app", 430, 225, 38, IN, kw(5, "app", -0.2))
b(3, "n_kantoor", 60, 370, 260, 230, kw(6, "ads", -0.2))
tx(3, "- $840 million", 420, 365, 64, RO, kw(6, "840"), 0.6)
tx(3, "ads & marketing", 430, 440, 36, IN, kw(6, "marketing", -0.2))
tx(3, "- $470 million", 420, 500, 56, RO, kw(6, "470"), 0.6)
tx(3, "offices & managers", 430, 565, 34, IN, kw(6, "470", 0.4))
over(3, "$4.5 billion", kw(6, "470", 0.8))
# 4 rente + belasting
kop(4, "Debt, then taxes")
b(4, "n_bank", 60, 100, 340, 260, kw(7, "debt", -0.3))
tx(4, "- $140 million", 440, 140, 80, RO, kw(7, "$140"), 0.6)
tx(4, "interest (net)", 450, 240, 40, IN, kw(7, "$140", 0.5))
b(4, "n_overheid", 60, 390, 360, 250, kw(8, "government", -0.2))
tx(4, "- $650 million", 440, 420, 80, RO, kw(8, "650"), 0.6)
tx(4, "taxes", 450, 520, 40, IN, kw(8, "650", 0.5))
over(4, "$3.7 billion", kw(8, "650", 0.8))
# 5 winst
kop(5, "What Netflix kept")
b(5, "n_winst", 60, 100, 460, 460, kw(9, "keep", -0.4))
tx(5, "$3.7 billion", 560, 130, 110, GR, kw(10, "$3"), 0.7)
tx(5, "profit in 3 months", 570, 270, 50, BL, kw(10, "months", -0.3))
tx(5, "= about $40 million", 560, 400, 64, GR, kw(11, "$40", -0.1))
tx(5, "every single day", 570, 480, 50, BL, kw(11, "day", -0.3))
# 6 jouw bon
kop(6, "Your receipt")
t0 = kw(12, "subscription", -0.3)
b(6, "n_bon", 70, 80, 440, 600, t0 - 0.2, 0.8)
lg(6, "netflix", 170, 110, 36, t0 + 0.3)
tx(6, "Standard plan, 1 month", 105, 165, 28, IN, t0 + 0.5)
tx(6, "you pay", 105, 205, 30, IN, kw(12, "$19")); tx(6, "$19.99", 372, 205, 30, BL, kw(12, "$19"))
rij = [("shows & movies", "-9.44"), ("engineers & app", "-1.60"), ("ads & marketing", "-1.30"), ("offices", "-0.72"), ("interest", "-0.22"), ("taxes", "-1.01")]
r0 = kw(13, "average", -0.1)
for n, (lab, bed) in enumerate(rij):
    tx(6, lab, 105, 250 + n * 40, 28, IN, r0 + n * 0.3, 0.3); tx(6, bed, 380, 250 + n * 40, 28, RO, r0 + n * 0.3, 0.3)
streep(6, 105, 498, 460, r0 + 1.9)
tx(6, "PROFIT", 105, 512, 44, GR, kw(14, "$5", -0.1), 0.4); tx(6, "$5.70", 320, 512, 44, GR, kw(14, "$5", -0.1), 0.4)
tx(6, "Netflix Q3 2026 averages,", 105, 580, 20, IN, kw(14, "profit"), 0.4)
tx(6, "GAAP, rounded; US price", 105, 608, 20, IN, kw(14, "profit", 0.3), 0.4)
tx(6, "$19.99 a month", 600, 140, 64, BL, kw(12, "$19"))
tx(6, "~$9.40", 600, 260, 64, IN, kw(13, "940"), 0.5); tx(6, "what you watch", 880, 275, 42, IN, kw(13, "watch", -0.2))
tx(6, "~$5.70", 600, 370, 64, GR, kw(14, "$5"), 0.5); tx(6, "pure profit", 880, 385, 42, GR, kw(14, "profit", -0.2))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
