"""BlackswanVault proef v3 (eigenaar 21 nov: "naast elkaar zetten en laten staan, maar niet alles"): per onderwerp een bord
met 2-5 tekeningen die blijven staan; bordje onder elke tekening; grafiek en staven als eigen bord. Cijfers uit video9/bronnen.md."""
import json
import numpy as np
from PIL import Image
def hoogte(naam, b, h):
    """werkelijke hoogte van de tekening na bijsnijden en schalen (zoals teken_anim doet)"""
    a = np.asarray(Image.open(A + naam + ".png").convert("RGB")).astype(int)
    a[:6], a[-6:], a[:, :6], a[:, -6:] = 255, 255, 255, 255
    ys, xs = np.nonzero(a.min(axis=2) < 245); w0, h0 = xs.max() - xs.min() + 12, ys.max() - ys.min() + 12
    return int(h0 * min(b / w0, h / h0))
Z = json.load(open("../zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; LG = "../logos/spacex.png"; BLAUW = [25, 55, 120]
it = []
GROEPEN = [0, 4, 6, 11, 16, 21, 26, 29]                     # zin waarop een nieuw bord begint
def einde(k):
    na = [g for g in GROEPEN if g > k]; return s[na[0]] - 0.15 if na else 1e9
def slot(n, i):
    """vakken op het bord: n tekeningen -> (x, y, breed, hoog)"""
    if n == 2: return (40 + i * 620, 90, 580, 440)
    if n == 3: return (25 + i * 415, 120, 395, 400)
    if n == 4: return (40 + (i % 2) * 620, 20 + (i // 2) * 350, 580, 250)
    if n == 5: return ((25 + i * 415, 15, 395, 250) if i < 3 else (230 + (i - 3) * 415, 370, 395, 250))
def tek(naam, k, n, i, bordje=None, kl=None, extra=0.1):
    x, y, b, h = slot(n, i); dur = max(1.6, min(2.8, (e[k] - s[k]) * 0.6)); eind = einde(k)
    it.append({"beeld": A + naam + ".png", "x": x, "y": y, "breed": b, "hoog": h, "midden": True, "start": s[k] + extra, "teken": dur, "kleur": 0.9, "tot": eind})
    if bordje:
        d = {"bordje": bordje, "x": x + 10, "y": y + hoogte(naam, b, h) + 10, "maat": 34, "maxbreed": b - 10, "start": s[k] + extra + dur + 0.3, "tot": eind}
        if kl: d[kl] = True
        it.append(d)
# bord 1 (zin 0-3): 4 vakken
tek("r00", 0, 4, 0, "$127.79", "rood"); tek("q01", 1, 4, 1, "Below IPO price: $135", "rood")
tek("r02", 2, 4, 2, "The hype stock of 2026"); tek("q03", 3, 4, 3, "One date in December", "rood")
# bord 2 (zin 4-5)
tek("r01", 4, 2, 0, "IPO: June 12"); tek("r05", 5, 2, 1, "Record: $86 billion", "groen")
# bord 3 (zin 6-10): koersgrafiek
it.append({"data": "../../video9/data/spcx.json", "logo": LG, "logohoog": 26, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
           "x": 40, "y": 40, "breed": 830, "hoog": 640, "start": s[6], "teken": e[9] - s[6] - 0.3, "tot": einde(6)})
it.append({"bordje": "First day: ~$161", "x": 905, "y": 150, "maat": 38, "start": s[6] + 2.0, "tot": einde(6)})
it.append({"bordje": "-40% from top", "x": 905, "y": 330, "maat": 42, "rood": True, "start": s[10] + 1.6, "tot": einde(6)})
# bord 4 (zin 11-15): links de staven, rechts 4 kleine tekeningen die blijven staan
it.append({"tekst": "Where does SpaceX make money?", "x": 40, "y": 20, "maat": 40, "kleur": BLAUW, "start": s[11], "teken": 1.2, "tot": einde(11)})
it.append({"beeld": A + "r11.png", "x": 650, "y": 90, "breed": 600, "hoog": 520, "midden": True, "start": s[11] + 0.3, "teken": 2.0, "kleur": 0.8, "tot": s[12] + 0.2})
it.append({"balken": [["Starlink", 11.4, "$11.4B"], ["Rockets", 4.1, "$4.1B"], ["AI", 3.2, "$3.2B"]], "logo": LG, "logohoog": 26, "onder": "revenue 2025",
           "x": 40, "y": 90, "breed": 560, "hoog": 590, "start": s[12], "starts": [s[12] + 3.0, s[14] + 1.0, s[15] + 1.0], "tot": einde(11)})
for i, (k, naam, b, kl) in enumerate(((12, "r12", "Starlink: $11.4B", None), (13, "r13", "Profit: $4.4B", "groen"),
                                      (14, "r14", "Rockets: a loss", "rood"), (15, "r15", "AI: lost ~$3.2B", "rood"))):
    x, y = 650 + (i % 2) * 310, 80 + (i // 2) * 320
    it.append({"beeld": A + naam + ".png", "x": x, "y": y, "breed": 290, "hoog": 210, "midden": True, "start": s[k] + 0.1, "teken": 1.8, "kleur": 0.8, "tot": einde(11)})
    d = {"bordje": b, "x": x + 5, "y": y + hoogte(naam, 290, 210) + 10, "maat": 26, "maxbreed": 285, "start": s[k] + 2.2, "tot": einde(11)}
    if kl: d[kl] = True
    it.append(d)
# bord 5 (zin 16-20): 5 vakken
tek("r16", 16, 5, 0, "The AI worry"); tek("r17", 17, 5, 1, "~$40B in debt"); tek("q18", 18, 5, 2, "Nvidia chips, 5 years")
tek("r19", 19, 5, 3, "Chips into space?"); tek("q20", 20, 5, 4, "Hard to get back", "rood")
# bord 6 (zin 21-25): datum + lock-up
it.append({"tekst": "Now, the date:", "x": 60, "y": 40, "maat": 52, "kleur": BLAUW, "start": s[21], "teken": 0.6, "tot": einde(21)})
it.append({"bordje": "December 8", "x": 520, "y": 28, "maat": 60, "rood": True, "start": s[21] + 0.5, "tot": einde(21)})
for i, (k, naam, b) in enumerate(((22, "r22", "Insiders own shares"), (23, "r23", "~6 months: no selling"), (24, "r24", "= the lock-up"))):
    x, y, bb, h = 25 + i * 415, 170, 395, 380
    it.append({"beeld": A + naam + ".png", "x": x, "y": y, "breed": bb, "hoog": h, "midden": True, "start": s[k] + 0.1, "teken": 2.2, "kleur": 0.9, "tot": einde(21)})
    it.append({"bordje": b, "x": x + 10, "y": y + hoogte(naam, bb, h) + 10, "maat": 32, "maxbreed": bb - 10, "start": s[k] + 2.6, "tot": einde(21)})
it.append({"bordje": "Lock-up ends: Dec 8 (Motley Fool)", "x": 300, "y": 640, "maat": 34, "rood": True, "start": s[25] + 1.0, "tot": einde(21)})
# bord 7 (zin 26-28)
tek("q26", 26, 3, 0, "Frozen shares can be sold"); tek("r27", 27, 3, 1, "Price can drop", "rood"); tek("q28", 28, 3, 2, "Insiders: June 2027")
# bord 8 (zin 29-31)
tek("r29", 29, 3, 0, "Nobody knows"); tek("q30", 30, 3, 1, "Some will hold", "groen"); tek("r31", 31, 3, 2, "Dec 8: the date to watch", "rood")
json.dump({"duur": round(e[-1] + 2.5, 2), "items": it}, open("scene3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("items", len(it))
