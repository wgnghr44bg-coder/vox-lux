"""BlackswanVault proef tekenstijl: scene.json uit zinnen.json (elk onderdeel start bij zijn zin). Donker bord."""
import json
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; LG = "logos/spacex.png"
def tot(k): return s[k] - 0.15
def tek(naam, x, y, b, st, t_=1.6, k=0.6, eind=None):
    d = {"beeld": A + naam + ".png", "x": x, "y": y, "breed": b, "start": st, "teken": t_, "kleur": k}
    if eind: d["tot"] = eind
    return d
it = [
 # a
 {"logo": LG, "x": 60, "y": 40, "hoog": 40, "start": s[0], "tot": tot(4)},
 tek("s1", 70, 130, 380, s[0] + 0.2, 1.8, 0.6, tot(4)),
 {"bordje": "$127.79", "x": 560, "y": 170, "maat": 90, "rood": True, "start": s[0] + 3.0, "tot": tot(4)},
 {"bordje": "IPO price: $135", "x": 560, "y": 360, "maat": 56, "start": s[1] + 2.0, "tot": tot(4)},
 {"tekst": "The most hyped stock of the year...", "x": 560, "y": 520, "maat": 36, "start": s[2], "teken": 1.2, "tot": tot(4)},
 {"tekst": "...and one date in December", "x": 560, "y": 590, "maat": 36, "start": s[3], "teken": 1.2, "tot": tot(4)},
 # b
 {"data": "../video9/data/spcx.json", "logo": LG, "logohoog": 26, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
  "x": 40, "y": 40, "breed": 820, "hoog": 640, "start": s[4], "teken": e[9] - s[4] - 0.5, "tot": tot(11)},
 {"bordje": "Record IPO: $86B", "x": 900, "y": 150, "maat": 40, "start": s[5] + 1.8, "tot": tot(11)},
 {"bordje": "-40% from top", "x": 900, "y": 330, "maat": 44, "rood": True, "start": s[10] + 1.6, "tot": tot(11)},
 # c
 {"balken": [["Starlink", 11.4, "$11.4B"], ["Rockets", 4.1, "$4.1B"], ["AI", 3.2, "$3.2B"]], "logo": LG, "logohoog": 26, "onder": "revenue 2025",
  "x": 40, "y": 60, "breed": 700, "hoog": 600, "start": s[11] + 0.5, "starts": [s[12] + 3.0, s[14] + 1.0, s[15] + 1.0], "tot": tot(16)},
 tek("s7", 830, 80, 400, s[12] + 0.5, 1.6, 0.6, tot(16)),
 {"bordje": "Profit: $4.4B", "x": 840, "y": 420, "maat": 44, "groen": True, "start": s[13] + 1.0, "tot": tot(16)},
 {"bordje": "Rockets: loss", "x": 840, "y": 520, "maat": 40, "rood": True, "start": s[14] + 2.8, "tot": tot(16)},
 {"bordje": "AI: about -$3.2B", "x": 840, "y": 610, "maat": 40, "rood": True, "start": s[15] + 3.5, "tot": tot(16)},
 # d1
 {"tekst": "$40 billion for AI chips", "x": 60, "y": 40, "maat": 46, "start": s[16] + 0.5, "teken": 1.2, "tot": tot(19)},
 tek("s8", 60, 200, 420, s[17], 1.8, 0.6, tot(19)),
 {"pijl": [520, 400, 640, 400], "start": s[18], "tot": tot(19)},
 tek("s9", 680, 240, 320, s[18] + 0.4, 1.2, 0.5, tot(19)),
 {"bordje": "5-year lease of Nvidia chips", "x": 600, "y": 590, "maat": 34, "start": s[18] + 1.4, "tot": tot(19)},
 # d2
 tek("s11", 40, 150, 430, s[19], 1.6, 0.6, tot(21)),
 tek("s9", 560, 330, 200, s[19] + 1.5, 0.8, 0.4, tot(21)),
 {"pijl": [780, 400, 870, 300], "start": s[19] + 2.6, "tot": tot(21)},
 tek("s7", 880, 90, 360, s[19] + 3.0, 1.4, 0.5, tot(21)),
 {"tekst": "Into space?", "x": 900, "y": 470, "maat": 44, "start": s[19] + 3.8, "teken": 0.8, "tot": tot(21)},
 {"bordje": "Hard to get back", "x": 560, "y": 590, "maat": 40, "rood": True, "start": s[20] + 0.8, "tot": tot(21)},
 # e
 {"tekst": "The lock-up", "x": 60, "y": 40, "maat": 56, "start": s[21], "teken": 0.8, "tot": tot(25)},
 tek("s2", 40, 170, 560, s[22] + 0.2, 2.0, 0.6, tot(25)),
 tek("s3", 700, 170, 480, s[23] + 0.2, 1.8, 0.6, tot(25)),
 {"bordje": "No selling for ~6 months", "x": 680, "y": 590, "maat": 36, "start": s[23] + 2.4, "tot": tot(25)},
 # f
 tek("s6", 60, 140, 330, s[25] + 0.2, 1.4, 0.5, tot(29)),
 {"bordje": "Dec 8", "x": 110, "y": 520, "maat": 70, "rood": True, "start": s[25] + 2.6, "tot": tot(29)},
 tek("s4", 480, 120, 480, s[26] + 0.2, 1.8, 0.6, tot(29)),
 {"bordje": "Price can drop", "x": 520, "y": 520, "maat": 46, "rood": True, "start": s[27] + 2.0, "tot": tot(29)},
 {"bordje": "Musk + insiders: June 2027", "x": 440, "y": 620, "maat": 34, "start": s[28] + 2.0, "tot": tot(29)},
 # g
 {"tekst": "Hold or sell?", "x": 60, "y": 40, "maat": 56, "start": s[29], "teken": 0.8},
 tek("s5", 380, 150, 520, s[29] + 0.3, 1.6, 0.6),
 {"bordje": "Dec 8: the date to watch", "x": 330, "y": 560, "maat": 48, "start": s[31] + 0.3},
]
json.dump({"duur": round(e[-1] + 2.0, 2), "bord": [26, 32, 30], "items": it}, open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("duur", e[-1] + 2.0)
