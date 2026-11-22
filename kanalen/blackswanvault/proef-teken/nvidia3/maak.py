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
it = []; borden = [0.0, s[4] - 0.3, s[9] - 0.3, s[14] - 0.3, s[20] - 0.3, s[24] - 0.3, s[27] - 0.3]
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
# BEELDPLAN langere proef (per stukje tekst één beeld; anders het woord zelf schrijven)
SP = "../../../blackswan-nl/video1/data/sp500.json"
def lg(k, pad, x, y, h, t0): it.append({"bord": k, "logo": pad, "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
# a: de daling
kop(0, 0.0, "Nvidia fell 14% in one day")
tx(0, "Friday", 65, 72, 48, BL, kw(0, "friday", -0.1))
logo(0, 65, 140, 56, kw(0, "nvidia", -0.1))
tx(0, "-14%", 65, 205, 96, RO, kw(0, "fell", 0.0), 0.7)
it.append({"bord": 0, "pijl": [370, 170, 470, 300], "kleur": RO, "dik": 14, "start": kw(0, "14", 0.0), "teken": 0.6})
tx(0, "in 1 day", 85, 320, 42, RO, kw(0, "single", 0.0))
it.append({"bord": 0, "dagen": NV, "logo": LG, "logohoog": 22, "onder": "closing price, change per day", "n": 7,
           "x": 640, "y": 75, "breed": 570, "hoog": 420, "start": kw(1, "seventh", -0.2), "per": 0.22})
foto(0, "hq.jpg", 65, 420, 250, 140, kw(2, "man", -0.2), "Photo: Daniel J. Prostak, CC BY-SA 4.0", None, 1.0)
b(0, "n_stoel", 360, 410, 220, 180, kw(2, "walked", -0.3))
tx(0, "the founder walked away", 650, 530, 40, BL, kw(2, "away", 0.0))
tx(0, "what is going on?", 650, 600, 46, RO, kw(3, "going", 0.0))
# b: de man die Nvidia bouwde
kop(1, borden[1], "The man who built Nvidia")
foto(1, "jensen.jpg", 65, 85, 250, 320, kw(4, "jensen", -0.3), "Photo: Anders Eidesvik, CC BY 4.0", "Jensen Huang", 1.1)
foto(1, "dennys.jpg", 380, 85, 270, 160, kw(4, "booth", -0.3), "Photo: Alexis Doine, CC0", None, 1.0)
tx(1, "1993", 390, 300, 50, BL, kw(4, "1993", 0.0))
tx(1, "+ Chris Malachowsky", 390, 370, 34, BL, kw(5, "chris", 0.0))
tx(1, "+ Curtis Priem", 390, 415, 34, BL, kw(5, "curtis", 0.0))
tx(1, "33 years", 720, 72, 44, BL, kw(6, "33"))
foto(1, "gtc.jpg", 720, 165, 250, 145, kw(7, "black", -0.3), "Photo: NVIDIA Taiwan, CC BY 2.0", None, 1.0)
foto(1, "chip_crop.jpg", 1010, 165, 190, 145, kw(7, "chips", -0.3), "Photo: Fritzchens Fritz, CC0", None, 0.9)
b(1, "n_kroon", 745, 410, 190, 180, kw(8, "valuable", -0.3))
tx(1, "#1 in the world", 950, 450, 34, GR, kw(8, "world", 0.0))
tx(1, "(until October)", 960, 500, 30, GR, kw(8, "world", 0.5))
# c: het vertrek
kop(2, borden[2], "Weeks of reports and investigations")
b(2, "n_dossiers", 65, 80, 260, 210, kw(9, "reports", -0.3))
tx(2, "Nov 12: stepped down", 345, 90, 36, RO, kw(10, "november", 0.0))
tx(2, "interim CEO: Colette Kress", 345, 155, 30, BL, kw(11, "colette", 0.0))
foto(2, "capitol.jpg", 350, 240, 280, 170, kw(12, "testify", -0.3), "Photo: Noclip, public domain", "testify before Congress", 1.0)
it.append({"bord": 2, "data": NV, "logo": LG, "logohoog": 22, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
           "x": 790, "y": 75, "breed": 440, "hoog": 400, "start": kw(13, "first", -0.3), "doel": kw(13, "first"), "teken": 3.0})
tx(2, "-29% since the first report", 720, 540, 40, RO, kw(13, "30", 0.0))
# d: zaken gaan goed
kop(3, borden[3], "Business has never been better")
tx(3, "?", 65, 70, 140, RO, kw(14, "strange", -0.1), 0.5)
b(3, "n_chips", 160, 75, 260, 260, kw(14, "business", -0.1))
tx(3, "$115.8B", 450, 80, 70, GR, kw(15, "$115"))
tx(3, "in one quarter", 455, 170, 34, GR, kw(15, "quarter", 0.0))
tx(3, "+103% in a year", 455, 220, 34, GR, kw(16, "double", -0.1))
it.append({"bord": 3, "balken": [["Q3", 115.8, "$115.8B"], ["Data ctr", 107.6, "$107.6B"], ["Next Q*", 130, "~$130B"]], "logo": LG, "logohoog": 22,
           "onder": "revenue, *expected", "x": 760, "y": 75, "breed": 480, "hoog": 430, "start": kw(17, "data", -0.4), "doel": kw(17, "data"),
           "starts": [kw(17, "data", -0.2), kw(17, "107", 0.0), kw(18, "130", 0.0)]})
b(3, "n_datacenter", 65, 420, 420, 220, kw(19, "big", -0.1))
tx(3, "big tech keeps buying", 500, 560, 40, BL, kw(19, "buying", 0.0))
# e: de verkoop
kop(4, borden[4], "Then came the selling")
tx(4, "Reuters:", 65, 72, 40, BL, kw(20, "reuters", -0.1))
b(4, "sec_wit", 65, 125, 150, 150, kw(20, "sec", -0.2))
b(4, "n_boekhouding", 230, 105, 230, 170, kw(20, "accounting", -0.2))
tx(4, "SEC probe", 80, 300, 44, RO, kw(20, "problems", 0.0))
lg(4, "logos/broadcom.png", 520, 90, 36, kw(21, "broadcom", -0.1))
tx(4, "-12%", 540, 140, 64, RO, kw(21, "12", 0.0))
lg(4, "logos/google.png", 800, 85, 50, kw(21, "google", -0.1))
tx(4, "buying fewer chips?", 790, 160, 34, BL, kw(21, "fewer", 0.0))
tx(4, "Nasdaq 100: -5.6%", 80, 400, 46, RO, kw(22, "nasdaq", 0.0))
it.append({"bord": 4, "data": SP, "onder": "S&P 500, closing price", "taal": "en", "valuta": "",
           "x": 560, "y": 270, "breed": 660, "hoog": 400, "start": kw(23, "s", -0.3), "doel": kw(23, "s"), "teken": 2.6})
tx(4, "-11.6% from the top", 80, 480, 40, RO, kw(23, "below", 0.0))
# f: te veel geld?
kop(5, borden[5], "Too much money?")
lg(5, "logos/anthropic.png", 65, 95, 34, kw(24, "anthropic", -0.1))
tx(5, "raised $81B (Nov 19)", 65, 150, 44, GR, kw(24, "$81", 0.0))
tx(5, "a simple question:", 65, 280, 44, BL, kw(25, "simple", 0.0))
b(5, "n_geldjacht", 560, 90, 620, 360, kw(26, "money", -0.4))
tx(5, "too much money, one AI dream?", 120, 560, 50, RO, kw(26, "dream", -0.2), 1.0)
# g: wat nu
kop(6, borden[6], "What comes next")
b(6, "n_bubbel", 65, 80, 220, 200, kw(27, "end", -0.2))
tx(6, "end of the AI boom?", 300, 110, 44, BL, kw(27, "ai", 0.0))
b(6, "n_koopje", 980, 80, 230, 210, kw(27, "chance", -0.2))
tx(6, "or a chance to buy?", 300, 190, 44, GR, kw(27, "buy", 0.0))
b(6, "n_nieuwechip", 65, 340, 230, 210, kw(28, "vera", -0.3))
tx(6, "Vera Rubin: \"explosive start\"", 300, 380, 38, GR, kw(28, "explosive", 0.0))
b(6, "n_nerveus", 900, 330, 300, 250, kw(29, "nervous", -0.4))
b(6, "n_7dagen", 300, 470, 300, 80, kw(30, "seven", -0.2))
tx(6, "7 days of selling", 300, 580, 46, RO, kw(30, "selling", 0.0))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0.045, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
