"""Nvidia-proef (1 min): opbouw zoals The Dividend Experiment (hoofdstukkop, stilstaande camera, losse tekeningen, F als verteller)
+ echte foto van Jensen Huang die getekend binnenkomt + echt Nvidia-logo + echte dagkoersen. Feiten: zie script.txt."""
import json
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; P = "../../../personage/afbeeldingen/"; LG = "logos/nvidia.png"; NV = "../../../blackswan-nl/video1/data/nvda.json"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
it = []; borden = [0.0, s[4] - 0.3, s[8] - 0.3, s[12] - 0.3]
def b(k, naam, x, y, br, h, t0, dur=1.8):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0, "teken": dur, "kleur": 0.9})
def tx(k, t, x, y, maat, kl, t0, dur=0.8): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0, "teken": dur})
def kop(k, t0, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": t0})
def F(k, pose, t0, tot=None, snel=False):
    d = {"bord": k, "beeld": P + pose + ".png", "x": 30, "y": 300, "breed": 230, "hoog": 400, "midden": True, "start": t0,
         "teken": 0.25 if snel else 1.4, "kleur": 0.25 if snel else 0.6}
    if tot: d["tot"] = tot
    it.append(d)
def logo(k, x, y, h, t0): it.append({"bord": k, "logo": LG, "x": x, "y": y, "hoog": h, "start": t0})
# 1
kop(0, 0.0, "Nvidia fell 14% in one day"); F(0, "f2", 0.3)
logo(0, 320, 90, 46, s[0] + 0.4)
tx(0, "-14%", 330, 160, 96, RO, s[0] + 1.6)
it.append({"bord": 0, "dagen": NV, "logo": LG, "logohoog": 22, "onder": "closing price, change per day", "n": 7,
           "x": 640, "y": 75, "breed": 600, "hoog": 470, "start": s[1] - 0.2, "per": 0.25})
tx(0, "7th drop in a row", 300, 300, 38, RO, s[1] + 1.2)
tx(0, "...and the founder walked away", 320, 600, 42, BL, s[2] + 1.0, 1.4)
# 2
kop(1, borden[1], "The man who built Nvidia"); F(1, "f3", borden[1] + 0.2)
it.append({"bord": 1, "foto": "jensen.jpg", "x": 310, "y": 85, "breed": 330, "hoog": 400, "start": s[4] + 0.2, "teken": 2.0, "kleur": 1.0,
           "naam": "Jensen Huang", "bron": "Photo: Anders Eidesvik, CC BY 4.0"})
b(1, "n_diner", 760, 80, 400, 250, s[4] + 2.6)
tx(1, "1993: a Denny's booth", 780, 340, 38, BL, s[4] + 4.2)
tx(1, "33 years", 800, 410, 62, BL, s[5] + 0.4)
tx(1, "Nov 12: stepped down", 740, 540, 44, RO, s[7] + 0.4)
# 3
kop(2, borden[2], "Business has never been better"); F(2, "f1", borden[2] + 0.2)
b(2, "n_chips", 300, 80, 400, 330, s[8] + 0.2, 2.0)
logo(2, 760, 90, 40, s[9] + 0.2)
tx(2, "$115.8B", 760, 150, 84, GR, s[9] + 2.8); tx(2, "in one quarter", 770, 260, 42, GR, s[9] + 3.8)
tx(2, "+103%", 770, 330, 70, GR, s[10] + 0.4); tx(2, "vs. a year ago", 780, 425, 36, GR, s[10] + 1.0)
tx(2, "big tech keeps buying", 320, 480, 44, BL, s[11] + 0.8, 1.2)
# 4
kop(3, borden[3], "Then came the selling"); F(3, "f5", borden[3] + 0.2, s[15])
b(3, "n_krant", 300, 80, 360, 260, s[12] + 0.2)
tx(3, "SEC probe (Reuters)", 320, 360, 40, RO, s[12] + 2.6)
b(3, "n_verkoop", 720, 80, 460, 270, s[13] + 0.1)
tx(3, "7 days, 7 drops", 790, 370, 50, RO, s[14] + 0.3)
F(3, "f4", s[15], snel=True)
tx(3, "the end of the AI boom?", 320, 470, 50, BL, s[15] + 0.3, 1.0)
tx(3, "or a chance to buy?", 420, 560, 50, GR, s[15] + 1.6, 0.9)
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "items": it}, open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items", round(e[-1] + 2, 1), "s")
