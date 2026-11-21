"""Proef 6 (eigenaar 21 nov: "onze eigen tekeningen, alleen de opbouw van The Dividend Experiment"): hoofdstukkop linksboven,
stilstaande camera, kleine tekeningen los verspreid, elke 4-6 s één nieuw (lijnen -> kleur), F als verteller per bord, leeg bord per hoofdstuk."""
import json
Z = json.load(open("../zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "../v2/afbeeldingen/"; P = "../../../personage/afbeeldingen/"; LG = "../logos/spacex.png"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
it = []; borden = [0.0, s[4] - 0.3, s[11] - 0.3]
def b(k, naam, x, y, br, h, t0, dur=1.8, map_=A):
    it.append({"bord": k, "beeld": map_ + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0, "teken": dur, "kleur": 0.9})
def tx(k, t, x, y, maat, kl, t0, dur=0.8): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0, "teken": dur})
def kop(k, t0, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": t0})
def F(k, pose, t0, tot=None):
    d = {"bord": k, "beeld": P + pose + ".png", "x": 30, "y": 300, "breed": 230, "hoog": 400, "midden": True, "start": t0, "teken": 1.4, "kleur": 0.6}
    if tot: d["tot"] = tot
    it.append(d)
# hoofdstuk 1
kop(0, 0.0, "SpaceX fell below its IPO price")
F(0, "f3", 0.3)
b(0, "r00", 300, 80, 300, 270, s[0] + 0.6)
it.append({"bord": 0, "logo": LG, "x": 320, "y": 370, "hoog": 32, "start": s[0] + 2.6})
tx(0, "$127.79", 620, 130, 54, RO, s[0] + 3.4)
b(0, "q01", 950, 75, 300, 250, s[1] + 0.2)
tx(0, "below $135", 970, 345, 44, RO, s[1] + 2.4)
b(0, "r02", 320, 450, 380, 250, s[2] + 0.1)
b(0, "q03", 900, 440, 330, 250, s[3] + 0.1)
# hoofdstuk 2
kop(1, borden[1], "The record IPO")
F(1, "f1", borden[1] + 0.2, s[10])
b(1, "r01", 300, 70, 400, 230, s[4] + 0.2)
tx(1, "June 12", 380, 305, 40, BL, s[4] + 2.0)
b(1, "r05", 780, 70, 400, 230, s[5] + 0.1)
tx(1, "$86 billion: a record", 800, 305, 38, GR, s[5] + 2.0)
it.append({"bord": 1, "data": "../../video9/data/spcx.json", "logo": LG, "logohoog": 22, "onder": "closing price", "taal": "en", "valuta": "$",
           "x": 290, "y": 405, "breed": 640, "hoog": 300, "start": s[6] + 0.2, "teken": e[9] - s[6] - 0.5})
F(1, "f2", s[10])
tx(1, "-40%", 990, 470, 72, RO, s[10] + 0.8)
tx(1, "from the top", 960, 560, 38, RO, s[10] + 1.4)
# hoofdstuk 3
kop(2, borden[2], "Where the money comes from")
F(2, "f4", borden[2] + 0.2)
b(2, "r11", 300, 75, 360, 270, s[11] + 0.3)
b(2, "r12", 760, 75, 400, 250, s[12] + 0.1)
tx(2, "Starlink: $11.4B", 800, 340, 40, BL, s[12] + 2.6)
b(2, "r13", 300, 420, 370, 230, s[13] + 0.1)
tx(2, "profit $4.4B", 330, 655, 38, GR, s[13] + 1.8)
b(2, "r14", 780, 420, 360, 230, s[14] + 0.1)
tx(2, "rockets: a loss", 800, 655, 38, RO, s[14] + 2.0)
json.dump({"duur": round(e[14] + 1.6, 2), "borden": borden, "schuif": 0, "items": it}, open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items", round(e[14] + 1.6, 1), "s")
