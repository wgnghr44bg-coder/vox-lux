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
def foto(k, pad, x, y, br, h, t0, bron, naam=None, dur=1.4):
    it.append({"bord": k, "foto": pad, "x": x, "y": y, "breed": br, "hoog": h, "start": t0, "teken": dur, "kleur": 0.7, "naam": naam, "bron": bron})
# 1: de daling (eigenaar 22 nov: "er mag wel iets meer gebeuren, meer afbeeldingen")
kop(0, 0.0, "Nvidia fell 14% in one day")
logo(0, 40, 80, 46, 0.3)
b(0, "n_vrijdag", 330, 70, 240, 180, kw(0, "friday", -0.2), 1.6)
tx(0, "-14%", 40, 140, 96, RO, kw(0, "14"))
it.append({"bord": 0, "dagen": NV, "logo": LG, "logohoog": 22, "onder": "closing price, change per day", "n": 7,
           "x": 640, "y": 75, "breed": 600, "hoog": 440, "start": kw(1, "seventh", -0.2), "per": 0.22})
foto(0, "hq.jpg", 50, 320, 270, 180, kw(2, "days", -0.4), "Photo: Daniel J. Prostak, CC BY-SA 4.0", None, 1.0)
b(0, "n_stoel", 370, 320, 230, 190, kw(2, "built", -0.3), 1.2)
tx(0, "the founder walked away", 60, 600, 40, BL, kw(2, "walked", 0.0), 1.0)
# 2: Jensen
kop(1, borden[1], "The man who built Nvidia")
foto(1, "jensen.jpg", 40, 85, 270, 350, kw(4, "jensen", -0.3), "Photo: Anders Eidesvik, CC BY 4.0", "Jensen Huang", 1.3)
tx(1, "1993", 400, 285, 46, BL, kw(4, "1993", 0.0), 0.8)
b(1, "n_diner", 360, 80, 300, 190, kw(4, "denny", -0.4), 1.6)
tx(1, "33 years", 720, 80, 50, BL, kw(5, "33"))
b(1, "n_jas", 720, 150, 200, 220, kw(6, "black", -0.3), 1.6)
foto(1, "dgx.jpg", 960, 95, 270, 170, kw(6, "chips", -0.2), "Photo: Daniel Lu, CC BY-SA 4.0", None, 1.2)
tx(1, "the chips behind AI", 720, 390, 36, GR, kw(6, "boom", 0.0), 0.9)
tx(1, "Nov 12: stepped down", 380, 520, 50, RO, kw(7, "november", 0.0), 1.1)
# 3: zaken gaan goed
kop(2, borden[2], "Business has never been better")
b(2, "n_chips", 40, 75, 300, 280, kw(8, "strange", 0.0), 2.2)
b(2, "n_rapport", 370, 80, 260, 220, kw(9, "reported", -0.2), 1.6)
tx(2, "$115.8B", 670, 80, 80, GR, kw(9, "$115"))
tx(2, "in one quarter", 680, 180, 38, GR, kw(9, "quarter", 0.0))
tx(2, "+103% in a year", 680, 240, 50, GR, kw(10, "double", -0.1))
b(2, "n_datacenter", 40, 420, 440, 230, kw(11, "big", -0.1), 1.8)
tx(2, "big tech keeps buying", 520, 560, 44, BL, kw(11, "buying", 0.0), 1.0)
# 4: de verkoop
kop(3, borden[3], "Then came the selling")
b(3, "n_boekhouding", 40, 75, 300, 210, kw(12, "reuters", -0.1), 1.6)
tx(3, "SEC probe (Reuters)", 40, 300, 40, RO, kw(12, "accounting", 0.0))
b(3, "n_verkoop", 380, 75, 420, 240, kw(13, "investors", -0.1), 1.5)
b(3, "n_7dagen", 840, 110, 400, 110, kw(14, "7", -0.1), 1.2)
tx(3, "7 days, 7 drops", 870, 240, 44, RO, kw(14, "drops", 0.0))
b(3, "n_bubbel", 40, 400, 240, 220, kw(15, "end", -0.2), 1.4)
tx(3, "the end of the AI boom?", 300, 440, 46, BL, kw(15, "ai", 0.0), 1.0)
b(3, "n_koopje", 960, 380, 260, 240, kw(15, "chance", -0.2), 1.4)
tx(3, "or a chance to buy?", 400, 560, 46, GR, kw(15, "buy", 0.0), 0.8)
# eigenaar 22 nov: "haal onze vaste character er ook maar uit" -> F weg, geen verschuiving (al zonder F ontworpen) (geen leeg vak links)
it = [i for i in it if "personage" not in i.get("beeld", "")]
for i in it:
    if "x" in i and "kop" not in i: pass
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0.06, "items": it},   # eigenaar 22 nov: zonder hand
          open("scene4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
