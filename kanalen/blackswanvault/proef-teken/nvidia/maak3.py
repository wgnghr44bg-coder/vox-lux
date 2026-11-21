"""Nvidia-proef v2 (eigenaar 22 nov): elk beeld op zijn KERNWOORD (woorden.json via woordtijden.py), per zin een passend beeld,
korte handgeschreven reacties, tekenende hand, opbouw als The Dividend Experiment / The Swedish Investor."""
import json, re
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
W = json.load(open("woorden.json", encoding="utf-8"))
def kw(zin, woord, na=0.15):
    """starttijd van het kernwoord in zin <zin> (+ na), anders begin van de zin"""
    for i, w, t0, t1 in W:
        if i == zin and re.sub(r"[^\w$%.]", "", w.lower()).startswith(woord.lower()): return round(t0 + na, 2)
    print("LET OP: woord niet gevonden:", zin, woord); return s[zin] + 0.2
A = "afbeeldingen/"; P = "../../../personage/afbeeldingen/"; LG = "logos/nvidia.png"; NV = "../../../blackswan-nl/video1/data/nvda.json"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
it = []; borden = [0.0, s[4] - 0.3, s[8] - 0.3, s[12] - 0.3]
def b(k, naam, x, y, br, h, t0, dur=3.0):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0, "teken": max(dur, 2.6), "kleur": 1.2})
def tx(k, t, x, y, maat, kl, t0, dur=1.3): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0, "teken": max(dur, 1.1)})
def kop(k, t0, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": t0})
def F(k, pose, t0, tot=None, snel=False):
    d = {"bord": k, "beeld": P + pose + ".png", "x": 30, "y": 300, "breed": 230, "hoog": 400, "midden": True, "start": t0,
         "teken": 0.25 if snel else 2.2, "kleur": 0.25 if snel else 0.8}
    if tot: d["tot"] = tot
    it.append(d)
def logo(k, x, y, h, t0): it.append({"bord": k, "logo": LG, "x": x, "y": y, "hoog": h, "start": t0})
# 1: de daling
kop(0, 0.0, "Nvidia fell 14% in one day"); F(0, "f2", 0.2, kw(3, "here"))
logo(0, 320, 90, 46, kw(0, "nvidia"))
tx(0, "-14%", 330, 150, 96, RO, kw(0, "14"))
it.append({"bord": 0, "dagen": NV, "logo": LG, "logohoog": 22, "onder": "closing price, change per day", "n": 7,
           "x": 660, "y": 75, "breed": 580, "hoog": 470, "start": kw(1, "seventh", -0.2), "per": 0.22})
b(0, "n_stoel", 330, 330, 270, 230, kw(2, "built", 0.0), 1.4)
tx(0, "the founder walked away", 300, 600, 40, BL, kw(2, "walked", 0.6), 1.0)
F(0, "f3", kw(3, "here"), snel=True)
# 2: Jensen
kop(1, borden[1], "The man who built Nvidia"); F(1, "f3", borden[1] + 0.2)
it.append({"bord": 1, "foto": "jensen.jpg", "x": 300, "y": 85, "breed": 300, "hoog": 380, "start": kw(4, "jensen", 0.0), "teken": 1.8, "kleur": 0.9,
           "naam": "Jensen Huang", "bron": "Photo: Anders Eidesvik, CC BY 4.0"})
b(1, "n_diner", 650, 90, 320, 220, kw(4, "denny", -0.6))
tx(1, "1993", 700, 240, 48, BL, kw(4, "1993"))
tx(1, "33 years", 1010, 80, 50, BL, kw(5, "33"))
b(1, "n_jas", 1000, 170, 220, 250, kw(6, "leather", -0.2), 1.4)
tx(1, "Nov 12: stepped down", 650, 520, 46, RO, kw(7, "stepped"), 0.9)
# 3: zaken gaan goed
kop(2, borden[2], "Business has never been better"); F(2, "f1", borden[2] + 0.2, kw(8, "strange"))
F(2, "f4", kw(8, "strange"), kw(9, "reported"), snel=True); F(2, "f1", kw(9, "reported"), snel=True)
b(2, "n_chips", 300, 150, 330, 300, kw(9, "reported", -0.2), 1.6)
tx(2, "$115.8B", 690, 150, 84, GR, kw(9, "$115"))
tx(2, "in one quarter", 700, 255, 40, GR, kw(9, "quarter", 0.0))
tx(2, "+103% in a year", 700, 330, 52, GR, kw(10, "double", -0.1))
b(2, "n_datacenter", 700, 460, 480, 220, kw(11, "big", -0.1), 1.6)
# 4: de verkoop
kop(3, borden[3], "Then came the selling"); F(3, "f5", borden[3] + 0.2, kw(15, "end"))
b(3, "n_krant", 300, 80, 340, 240, kw(12, "reuters", -0.1), 1.4)
tx(3, "SEC probe (Reuters)", 320, 335, 40, RO, kw(12, "sec"))
b(3, "n_verkoop", 720, 80, 460, 260, kw(13, "investors", -0.1), 1.5)
tx(3, "7 days, 7 drops", 790, 360, 48, RO, kw(14, "7", 0.0))
F(3, "f4", kw(15, "end"), snel=True)
tx(3, "the end of the AI boom?", 320, 470, 50, BL, kw(15, "end", 0.0), 1.0)
tx(3, "or a chance to buy?", 420, 560, 50, GR, kw(15, "chance", 0.0), 0.9)
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0.06, "items": it,
           "hand": "../../../personage/hand/hand.png", "handjson": "../../../personage/hand/hand.json", "handmaat": 0.42},
          open("scene3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
