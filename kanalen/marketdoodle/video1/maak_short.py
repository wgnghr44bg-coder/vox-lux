"""Short (staand 1080x1920) uit de lange video: gekozen zinnen uit stem.wav knippen (zelfde stem, eigen pauzes),
woordtijden omrekenen en een eigen staand beeldplan maken. Schrijft short/stem.wav, short/zinnen.json, short/woorden.json, short/scene.json.
  python maak_short.py"""
import json, re
from pathlib import Path
import numpy as np
import wav
H = Path(__file__).parent; O = H / "short"; O.mkdir(exist_ok=True)
KIES = [0, 1, 2, 3, 58, 60, 61, 62, 65, 66, 68, 72]          # haak -> dotcom -> verschil
ZL = json.load(open(H / "zinnen.json", encoding="utf-8")); WL = json.load(open(H / "woorden.json", encoding="utf-8"))
a, SR = wav.lees(H / "stem.wav")
t = 0.4; delen = [np.zeros(int(t * SR), np.float32)]; zin, woorden = [], []
for k, i in enumerate(KIES):
    s0, e0, z, sc = ZL[i]
    delen.append(a[int(s0 * SR):int(e0 * SR)]); zin.append([round(t, 3), round(t + e0 - s0, 3), z, sc])
    woorden += [[k, w, round(t + w0 - s0, 2), round(t + w1 - s0, 2)] for j, w, w0, w1 in WL if j == i]
    p = 0.8 if (k + 1 < len(KIES) and KIES[k + 1] == i + 1) else 1.0
    if k + 1 == len(KIES): p = 1.2
    delen.append(np.zeros(int(p * SR), np.float32)); t += e0 - s0 + p
wav.schrijf(O / "stem.wav", np.concatenate(delen), SR)
json.dump(zin, open(O / "zinnen.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(woorden, open(O / "woorden.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
s = [z[0] for z in zin]; e = [z[1] for z in zin]
def kw(k, woord, na=0.15):
    for i, w, t0, t1 in woorden:
        if i == k and re.sub(r"[^\w$%.\-]", "", w.lower()).startswith(woord.lower()): return round(t0 + na, 2)
    print("LET OP: woord niet gevonden:", k, woord, "|", " ".join(w for i, w, *_ in woorden if i == k)); return s[k] + 0.2
A = "afbeeldingen/"; F = "fotos/"; L = "logos/"; D = "data/"
BL, RO, GR = [25, 55, 120], [214, 32, 39], [46, 150, 84]
it = []; borden = [0.0, s[4] - 0.3, s[9] - 0.3]
def b(k, naam, x, y, br, h, t0):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": 1.2, "kleur": 0.5})
def tx(k, txt, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": txt, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": dur})
def lg(k, naam, x, y, h, t0): it.append({"bord": k, "logo": L + naam + ".png", "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
def kop(k, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": borden[k]})
# 0 haak (zinnen 0-3)
kop(0, "The Nasdaq just erased 2026")
lg(0, "nasdaq", 70, 110, 70, kw(0, "nasdaq", -0.1))
tx(0, "-5.3%", 70, 200, 170, RO, kw(0, "fell"), 0.7)
tx(0, "in one day", 90, 420, 64, RO, kw(0, "single"))
tx(0, "this week: -10%", 70, 540, 76, RO, kw(1, "week"))
b(0, "n_virus", 720, 170, 280, 240, kw(2, "covid", -0.1))
tx(0, "worst week since March 2020", 70, 680, 50, BL, kw(2, "march"))
it.append({"bord": 0, "data": D + "ixic_2026.json", "onder": "Nasdaq, closing points", "taal": "en", "valuta": "", "logo": L + "nasdaq.png", "logohoog": 22,
           "x": 60, "y": 860, "breed": 960, "hoog": 620, "start": kw(3, "gain") - 0.3, "doel": kw(3, "gain"), "teken": 2.2})
tx(0, "2026: -2.7%", 70, 1560, 110, RO, kw(3, "gone"), 0.6)
# 1 dotcom (zinnen 58, 60, 61, 62, 65)
kop(1, "Is this 2000 all over again?")
b(1, "n_pc2000", 70, 110, 340, 300, kw(4, "dot", -0.1))
tx(1, "2000 again?", 450, 200, 90, RO, kw(4, "again"))
it.append({"bord": 1, "data": D + "ixic_9915.json", "onder": "Nasdaq 1999-2015, closing points", "taal": "en", "valuta": "", "logo": L + "nasdaq.png", "logohoog": 22,
           "x": 60, "y": 470, "breed": 960, "hoog": 700, "start": kw(5, "march") - 0.3, "doel": kw(5, "march"), "teken": 3.0, "jaren": 5})
tx(1, "-78%", 70, 1230, 200, RO, kw(7, "78"), 0.7)
tx(1, "15 years", 70, 1520, 100, RO, kw(8, "15"))
tx(1, "to get back", 540, 1555, 60, RO, kw(8, "back"))
# 2 het verschil (zinnen 66, 68, 72)
kop(2, "But there is a big difference")
tx(2, "2000: no profits", 70, 120, 70, BL, kw(9, "big"))
lg(2, "nvidia", 70, 330, 80, kw(10, "nvidia", -0.1))
b(2, "n_schat", 60, 460, 560, 460, kw(10, "billion", -0.3))
tx(2, "> $1B", 650, 520, 120, GR, kw(10, "every"))
tx(2, "every day", 660, 690, 64, GR, kw(10, "day"))
tx(2, "the money is real", 70, 1060, 80, GR, kw(11, "real"))
tx(2, "but how much future", 70, 1230, 66, RO, kw(11, "future"))
tx(2, "is in the price?", 70, 1330, 66, RO, kw(11, "price"))
json.dump({"W": 1080, "H": 1920, "duur": round(e[-1] + 1.6, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open(O / "scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items, short", round(e[-1] + 1.6, 1), "s")
