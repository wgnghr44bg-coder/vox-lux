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
def b(k, naam, x, y, br, h, t0, dur=1.2):
    it.append({"bord": k, "beeld": (naam + ".png" if naam.startswith("sec") else A + naam + ".png"), "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.3), "kleur": 0.5})
def tx(k, t, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": min(dur, 0.7)})
def kop(k, t0, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": t0})
def F(k, pose, t0, tot=None, snel=False):
    d = {"bord": k, "beeld": P + pose + ".png", "x": 30, "y": 300, "breed": 230, "hoog": 400, "midden": True, "start": t0,
         "teken": 0.25 if snel else 2.2, "kleur": 0.25 if snel else 0.8}
    if tot: d["tot"] = tot
    it.append(d)
def logo(k, x, y, h, t0): it.append({"bord": k, "logo": LG, "x": x, "y": y, "hoog": h, "start": t0})
def foto(k, pad, x, y, br, h, t0, bron, naam=None, dur=1.4):
    it.append({"bord": k, "foto": pad, "x": x, "y": y, "breed": br, "hoog": h, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.1), "kleur": 0.5, "naam": naam, "bron": bron})
# BEELDPLAN (eigenaar 22 nov: "tekst opdelen, timen, en daar een afbeelding tekenen of laten zien"):
# elk stukje tekst -> één beeld dat precies dat laat zien; geen goed beeld -> het woord zelf groot schrijven
# 1: de daling
kop(0, 0.0, "Nvidia fell 14% in one day")
tx(0, "Friday", 65, 72, 48, BL, kw(0, "friday", -0.1), 0.6)                         # "On Friday,"
logo(0, 65, 150, 46, kw(0, "nvidia", -0.1))                                          # "Nvidia stock"
tx(0, "-14%", 65, 205, 96, RO, kw(0, "fell", 0.0), 0.7)                              # "fell fourteen percent"
it.append({"bord": 0, "pijl": [330, 150, 450, 300], "kleur": RO, "dik": 14, "start": kw(0, "14", 0.0), "teken": 0.6})
tx(0, "in 1 day", 60, 320, 42, RO, kw(0, "single", 0.0), 0.6)                        # "in a single day"
it.append({"bord": 0, "dagen": NV, "logo": LG, "logohoog": 22, "onder": "closing price, change per day", "n": 7,
           "x": 640, "y": 75, "breed": 570, "hoog": 440, "start": kw(1, "seventh", -0.2), "per": 0.22})   # "the seventh drop in a row"
foto(0, "hq.jpg", 65, 420, 260, 150, kw(2, "man", -0.2), "Photo: Daniel J. Prostak, CC BY-SA 4.0", None, 1.0)   # "the man who built the company"
b(0, "n_stoel", 360, 410, 230, 190, kw(2, "walked", -0.3), 1.2)                       # "walked away"
tx(0, "the founder walked away", 650, 560, 40, BL, kw(2, "away", 0.0), 0.8)
# 2: Jensen
kop(1, borden[1], "The man who built Nvidia")
foto(1, "jensen.jpg", 65, 85, 270, 350, kw(4, "jensen", -0.3), "Photo: Anders Eidesvik, CC BY 4.0", "Jensen Huang", 1.3)   # "Jensen Huang"
tx(1, "1993", 400, 285, 46, BL, kw(4, "1993", 0.0), 0.8)                              # "started Nvidia in 1993"
b(1, "n_diner", 360, 80, 300, 190, kw(4, "booth", -0.4), 1.6)                          # "in a booth at a Denny's"
tx(1, "33 years", 720, 80, 50, BL, kw(5, "33"))                                       # "for thirty-three years"
b(1, "n_jas", 720, 150, 200, 220, kw(6, "black", -0.3), 1.6)                          # "black leather jacket"
foto(1, "chip_crop.jpg", 960, 95, 230, 190, kw(6, "chips", -0.3), "Photo: Fritzchens Fritz, CC0", None, 1.1)   # "the chips behind the AI boom"
tx(1, "the chips behind AI", 720, 390, 36, GR, kw(6, "boom", 0.0), 0.9)
tx(1, "Nov 12: stepped down", 380, 520, 50, RO, kw(7, "november", 0.0), 1.1)          # "On November 12th, he stepped down"
# 3: zaken gaan goed
kop(2, borden[2], "Business has never been better")
tx(2, "?", 50, 70, 150, RO, kw(8, "strange", -0.1), 0.5)                              # "The strange part"
b(2, "n_chips", 150, 75, 280, 280, kw(8, "business", -0.1), 1.8)                       # "business has never been better"
b(2, "n_rapport", 470, 80, 230, 200, kw(9, "reported", -0.2), 1.4)                     # "Nvidia reported"
tx(2, "$115.8B", 730, 80, 80, GR, kw(9, "$115"))                                      # "$115.8 billion"
tx(2, "in one quarter", 740, 180, 38, GR, kw(9, "quarter", 0.0))                      # "for a single quarter"
tx(2, "+103% in a year", 740, 240, 50, GR, kw(10, "double", -0.1))                    # "more than double a year ago"
b(2, "n_datacenter", 65, 420, 440, 230, kw(11, "big", -0.1), 1.8)                      # "big tech ... AI data centers"
tx(2, "big tech keeps buying", 520, 560, 44, BL, kw(11, "buying", 0.0), 1.0)
# 4: de verkoop
kop(3, borden[3], "Then came the selling")
tx(3, "Reuters:", 65, 72, 40, BL, kw(12, "reuters", -0.1), 0.6)                       # "Then Reuters reported"
b(3, "sec_wit", 65, 125, 160, 160, kw(12, "sec", -0.2), 1.2)                           # "the SEC is looking at"
b(3, "n_boekhouding", 220, 100, 260, 190, kw(12, "accounting", -0.2), 1.3)             # "possible accounting problems"
tx(3, "SEC probe", 60, 300, 44, RO, kw(12, "problems", 0.0), 0.6)
b(3, "n_verkoop", 520, 75, 380, 230, kw(13, "investors", -0.1), 1.4)                   # "investors started selling"
b(3, "n_7dagen", 925, 120, 285, 85, kw(14, "7", -0.1), 1.0)                            # "Seven days, seven drops"
tx(3, "7 days, 7 drops", 925, 225, 38, RO, kw(14, "drops", 0.0))
b(3, "n_bubbel", 65, 400, 240, 220, kw(15, "end", -0.2), 1.3)                          # "the end of the AI boom"
tx(3, "the end of the AI boom?", 300, 440, 46, BL, kw(15, "ai", 0.0), 1.0)
b(3, "n_koopje", 950, 380, 250, 240, kw(15, "chance", -0.2), 1.3)                      # "or a chance to buy?"
tx(3, "or a chance to buy?", 400, 560, 46, GR, kw(15, "buy", 0.0), 0.8)
# eigenaar 22 nov: "haal onze vaste character er ook maar uit" -> F weg, geen verschuiving (al zonder F ontworpen) (geen leeg vak links)
it = [i for i in it if "personage" not in i.get("beeld", "")]
for i in it:
    if "x" in i and "kop" not in i: pass
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0.03, "items": it},   # eigenaar 22 nov: zonder hand
          open("scene5.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
