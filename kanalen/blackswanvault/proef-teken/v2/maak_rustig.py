"""Rustige tekenstijl (eigenaar 21 nov: "te rommelig, rustiger, duidelijk wat er gebeurt"): F vast links (alleen houding wisselt),
rechts één groot beeld dat zich opbouwt, weinig tekst (groot, handgeschreven), bord schuift opzij bij een nieuw onderwerp,
grafiek krijgt het hele vak. Proefstuk: eerste ± 31 s van de SpaceX-proef."""
import json
Z = json.load(open("../zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; P = "../../../personage/afbeeldingen/"; LG = "../logos/spacex.png"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
EIND = round(e[-1] + 2.5, 2)
it = []
# F links, alleen de houding wisselt
houding = [(0.2, "f3"), (s[1] + 0.3, "f2"), (s[3], "f4"), (s[4] + 0.2, "f1"), (s[6], "f3"), (s[10], "f2"),
           (s[11], "f4"), (s[13], "f1"), (s[14], "f2"), (s[16], "f5"), (s[19], "f2"), (s[21], "f3"), (s[26], "f2"),
           (s[28], "f4"), (s[29], "f4"), (s[31], "f3")]
for i, (t0, f) in enumerate(houding):
    t1 = houding[i + 1][0] if i + 1 < len(houding) else 1e9
    eerste = i == 0
    it.append({"beeld": P + f + ".png", "x": 20, "y": 130, "breed": 330, "hoog": 560, "midden": True,
               "start": t0, "teken": 1.4 if eerste else 0.01, "kleur": 0.6 if eerste else 0.3, "tot": t1})
borden = [0.0, s[3] - 0.4, s[4] - 0.4, s[6] - 0.4, s[11] - 0.4, s[16] - 0.4, s[19] - 0.4, s[21] - 0.4, s[25] - 0.4, s[29] - 0.4]
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
tekst(3, "-40% from the top", 900, 650, 40, RO, s[10] + 1.0)
# bord 4: waar verdient SpaceX geld (staven over het hele vak)
tekst(4, "Where does SpaceX make money?", 400, 25, 46, BL, s[11] + 0.2, 1.2)
it.append({"bord": 4, "balken": [["Starlink", 11.4, "$11.4B"], ["Rockets", 4.1, "$4.1B"], ["AI", 3.2, "$3.2B"]], "logo": LG, "logohoog": 26,
           "onder": "revenue 2025", "x": 400, "y": 100, "breed": 600, "hoog": 590, "start": s[11] + 1.0, "starts": [s[12] + 3.0, s[14] + 1.0, s[15] + 1.0]})
tekst(4, "profit", 1040, 250, 40, GR, s[13] + 0.5); tekst(4, "$4.4B", 1040, 300, 52, GR, s[13] + 1.0)
tekst(4, "loss", 1040, 430, 40, RO, s[14] + 2.6); tekst(4, "loss", 1040, 520, 40, RO, s[15] + 3.6)
# bord 5: $40 miljard voor chips
beeld(5, "r17", 400, 40, 820, 470, s[16] + 0.2, 2.6)
tekst(5, "$40 billion in debt", 460, 545, 54, RO, s[17] + 1.5)
tekst(5, "for Nvidia chips, 5 years", 640, 625, 42, BL, s[18] + 0.5)
# bord 6: chips de ruimte in?
beeld(6, "r19", 400, 30, 820, 500, s[19] + 0.1, 2.6)
tekst(6, "into space?", 500, 560, 54, BL, s[19] + 3.0)
tekst(6, "hard to get back", 820, 630, 46, RO, s[20] + 1.0)
# bord 7: de lock-up
tekst(7, "December 8", 420, 20, 70, RO, s[21] + 0.2, 0.8)
beeld(7, "r23", 420, 120, 800, 430, s[22] + 0.1, 2.8)
tekst(7, "~6 months: no selling", 440, 590, 46, BL, s[23] + 1.4)
tekst(7, "= the lock-up", 920, 640, 46, RO, s[24] + 0.5)
# bord 8: einde lock-up
tekst(8, "Dec 8: the lock-up ends", 420, 20, 52, RO, s[25] + 0.8)
beeld(8, "q26", 420, 110, 800, 440, s[26] + 0.1, 2.6)
tekst(8, "price can drop", 440, 590, 50, RO, s[27] + 1.5)
tekst(8, "Musk + insiders: June 2027", 700, 650, 38, BL, s[28] + 1.8)
# bord 9: niemand weet het
beeld(9, "r29", 420, 40, 560, 460, s[29] + 0.1, 2.0)
tekst(9, "nobody knows", 1000, 200, 46, BL, s[29] + 1.6)
tekst(9, "some will hold", 1000, 300, 42, GR, s[30] + 1.6)
tekst(9, "Dec 8:", 440, 545, 66, RO, s[31] + 0.2, 0.5); tekst(9, "the date to watch", 680, 560, 52, RO, s[31] + 0.7, 1.0)
json.dump({"duur": EIND, "borden": borden, "schuif": 1.0, "items": it}, open("scene-rustig.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
