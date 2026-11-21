"""Bouwt scene.json uit zinnen.json: elk onderdeel start bij het begin van zijn zin."""
import json
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"
def tot(k): return s[k] - 0.15
it = [
 # a: duizend euro
 {"tekst": "€1.000 in ASML?", "x": 60, "y": 30, "maat": 52, "start": s[0], "teken": 1.0, "tot": tot(1)},
 {"beeld": A+"a1.png", "x": 120, "y": 150, "breed": 520, "start": s[0] + 0.2, "teken": 1.8, "kleur": 0.6, "tot": tot(1)},
 {"bordje": "€1.000", "x": 760, "y": 300, "maat": 96, "start": s[0] + 1.8, "tot": tot(1)},
 # b: koers
 {"data": "../../video1/data/asml.json", "titel": "ASML (Amsterdam), slotkoers", "x": 40, "y": 60, "breed": 780, "hoog": 620,
  "start": s[1], "teken": e[2] - s[1] - 0.8, "tot": tot(5)},
 {"bordje": "± €680 over", "x": 850, "y": 210, "maat": 46, "start": s[3] + 1.6, "tot": tot(5)},
 {"bordje": "-9,3% op 1 dag", "x": 850, "y": 380, "maat": 40, "rood": True, "start": s[4] + 1.0, "tot": tot(5)},
 # c: goede cijfers
 {"tekst": "Hoe kan dat?", "x": 60, "y": 30, "maat": 52, "start": s[5], "teken": 0.8, "tot": tot(8)},
 {"beeld": A+"c1.png", "x": 40, "y": 160, "breed": 480, "start": s[5] + 0.2, "teken": 1.6, "kleur": 0.6, "tot": tot(8)},
 {"tekst": "ASML, derde kwartaal", "x": 640, "y": 110, "maat": 32, "start": s[6], "teken": 0.6, "tot": tot(8)},
 {"balken": [["Omzet", 11.7, "€11,7 mld"], ["Winst", 5.0, "€5,0 mld"]], "x": 620, "y": 170, "breed": 560, "hoog": 440,
  "start": s[6], "starts": [s[6] + 1.6, s[7] + 0.4], "tot": tot(8)},
 # d: keten
 {"tekst": "Niet door ASML zelf", "x": 60, "y": 30, "maat": 52, "start": s[8], "teken": 1.0, "tot": tot(11)},
 {"beeld": A+"d1.png", "x": 30, "y": 250, "breed": 380, "start": s[9], "teken": 1.4, "kleur": 0.5, "tot": tot(11)},
 {"pijl": [425, 400, 505, 400], "start": s[9] + 1.9, "tot": tot(11)},
 {"beeld": A+"d2.png", "x": 520, "y": 300, "breed": 250, "start": s[9] + 2.2, "teken": 1.0, "kleur": 0.4, "tot": tot(11)},
 {"pijl": [785, 400, 865, 400], "start": s[10], "tot": tot(11)},
 {"beeld": A+"d3.png", "x": 900, "y": 200, "breed": 260, "start": s[10] + 0.3, "teken": 1.3, "kleur": 0.5, "tot": tot(11)},
 {"tekst": "machine  →  chip  →  AI", "x": 300, "y": 610, "maat": 40, "start": s[10] + 0.5, "teken": 1.0, "tot": tot(11)},
 # e: Nvidia
 {"bordje": "Nvidia -14%", "x": 40, "y": 160, "maat": 62, "rood": True, "start": s[11] + 1.6, "tot": tot(13)},
 {"tekst": "Nvidia, slotkoers per dag", "x": 560, "y": 60, "maat": 32, "start": s[11], "teken": 0.6, "tot": tot(13)},
 {"dagen": "../../video1/data/nvda.json", "n": 7, "x": 520, "y": 130, "breed": 730, "hoog": 560, "start": s[11] + 0.1, "per": 0.4, "tot": tot(13)},
 {"bordje": "7e daling op rij", "x": 40, "y": 360, "maat": 50, "start": s[12] + 0.4, "tot": tot(13)},
 # f: vooruit
 {"tekst": "Koopkans, of pas het begin?", "x": 60, "y": 30, "maat": 52, "start": s[13], "teken": 1.2},
 {"beeld": "../afbeeldingen/t5.png", "x": 40, "y": 150, "breed": 560, "start": s[13] + 0.3, "teken": 1.8, "kleur": 0.6},
 {"beeld": A+"f1.png", "x": 760, "y": 150, "breed": 380, "start": s[14], "teken": 1.4, "kleur": 0.5},
 {"bordje": "27 januari", "x": 790, "y": 560, "maat": 56, "start": s[14] + 1.6},
]
json.dump({"duur": round(e[-1] + 1.8, 2), "items": it}, open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("duur", e[-1] + 1.8)
