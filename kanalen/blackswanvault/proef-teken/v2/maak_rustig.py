"""Rustige tekenstijl (eigenaar 21 nov: "te rommelig, rustiger, duidelijk wat er gebeurt"): F vast links (alleen houding wisselt),
rechts één groot beeld dat zich opbouwt, weinig tekst (groot, handgeschreven), bord schuift opzij bij een nieuw onderwerp,
grafiek krijgt het hele vak. Proefstuk: eerste ± 31 s van de SpaceX-proef."""
import json
Z = json.load(open("../zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; P = "../../../personage/afbeeldingen/"; LG = "../logos/spacex.png"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
EIND = 31.5
it = []
# F links, alleen de houding wisselt
houding = [(0.2, "f3"), (s[1] + 0.3, "f2"), (s[3], "f4"), (s[4] + 0.2, "f1"), (s[6], "f3")]
for i, (t0, f) in enumerate(houding):
    t1 = houding[i + 1][0] if i + 1 < len(houding) else 1e9
    eerste = i == 0
    it.append({"beeld": P + f + ".png", "x": 20, "y": 130, "breed": 330, "hoog": 560, "midden": True,
               "start": t0, "teken": 1.4 if eerste else 0.01, "kleur": 0.6 if eerste else 0.3, "tot": t1})
borden = [0.0, s[3] - 0.4, s[4] - 0.4, s[6] - 0.4]
def tekst(b, tx, x, y, maat, kl, t0, dur=0.9): it.append({"bord": b, "tekst": tx, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0, "teken": dur})
def beeld(b, naam, x, y, br, h, t0, dur=2.4): it.append({"bord": b, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0, "teken": dur, "kleur": 1.0})
# bord 0: raket, prijs onder de IPO-lijn
beeld(0, "r00", 360, 40, 470, 640, s[0] + 0.3)
tekst(0, "$127.79", 860, 360, 84, RO, s[0] + 3.0)
it.append({"bord": 0, "streep": [845, 330, 1240], "kleur": BL, "start": s[1] + 0.8, "teken": 1.0})
tekst(0, "IPO price  $135", 860, 250, 48, BL, s[1] + 1.6)
tekst(0, "the hype stock", 860, 500, 40, BL, s[2] + 0.3, 1.0)
tekst(0, "of 2026", 860, 555, 40, BL, s[2] + 1.3, 0.6)
# bord 1: storm boven de beurs
beeld(1, "q03", 420, 40, 760, 520, s[3] - 0.2, 2.2)
tekst(1, "one date in December...", 520, 590, 52, RO, s[3] + 1.2, 1.4)
# bord 2: IPO-dag
beeld(2, "r01", 400, 30, 840, 480, s[4] - 0.2, 2.6)
tekst(2, "June 12: IPO", 440, 545, 52, BL, s[4] + 0.8)
tekst(2, "$86 billion, a record", 760, 620, 50, GR, s[5] + 1.6, 1.2)
# bord 3: grafiek over het hele vak
it.append({"bord": 3, "data": "../../video9/data/spcx.json", "logo": LG, "logohoog": 26, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
           "x": 380, "y": 40, "breed": 860, "hoog": 640, "start": s[6] + 0.2, "teken": e[9] - s[6] - 0.3})
json.dump({"duur": EIND, "borden": borden, "schuif": 1.0, "items": it}, open("scene-rustig.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
