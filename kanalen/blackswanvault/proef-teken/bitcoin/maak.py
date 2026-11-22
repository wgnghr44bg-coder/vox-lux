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
it = []; borden = [0.0, s[5] - 0.3, s[8] - 0.3, s[13] - 0.3, s[16] - 0.3, s[18] - 0.3]
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
# BEELDPLAN Bitcoin-proef (per stukje tekst één beeld)
def lg(k, pad, x, y, h, t0): it.append({"bord": k, "logo": pad, "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
BTC = "btc.json"; BL_ = "logos/bitcoin.png"
# 0: de daling
kop(0, 0.0, "Bitcoin fell below $60,000")
lg(0, BL_, 65, 80, 90, kw(0, "bitcoin", -0.1))
tx(0, "$58,450", 175, 95, 70, RO, kw(0, "$60", 0.0))
tx(0, "lowest since July", 70, 200, 40, RO, kw(1, "lowest", 0.0))
it.append({"bord": 0, "data": BTC, "logo": BL_, "logohoog": 26, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
           "x": 560, "y": 75, "breed": 660, "hoog": 430, "start": kw(2, "october", -0.3), "doel": kw(2, "october"), "teken": 2.6})
tx(0, "-53%", 70, 270, 110, RO, kw(3, "half", -0.2), 0.6)
tx(0, "who is selling?", 70, 560, 56, BL, kw(4, "selling", -0.2))
# 1: fondsen
kop(1, borden[1], "1. Bitcoin funds")
b(1, "n_fonds", 65, 80, 320, 290, kw(5, "funds", -0.2))
lg(1, "logos/blackrock.png", 440, 95, 38, kw(6, "blackrock", -0.1))
tx(1, "-$3.5B in November", 440, 160, 52, RO, kw(6, "$3", 0.0))
tx(1, "Nov 19: -$541M", 440, 260, 48, RO, kw(7, "19", 0.0))
tx(1, "biggest daily outflow ever", 440, 335, 38, BL, kw(7, "biggest", 0.0))
# 2: bedrijven
kop(2, borden[2], "2. Companies that hold bitcoin")
b(2, "n_bedrijf", 65, 80, 250, 260, kw(8, "companies", -0.2))
tx(2, "Strategy: ~850,000 BTC", 360, 85, 44, BL, kw(9, "strategy", 0.0))
tx(2, "paid ~$75,000 per coin", 360, 150, 40, BL, kw(10, "$75", 0.0))
tx(2, "Friday: $58,450", 360, 210, 40, RO, kw(11, "today", 0.0))
b(2, "n_verlies", 360, 280, 280, 240, kw(11, "loss", -0.3))
b(2, "n_rente", 720, 290, 300, 210, kw(12, "sold", -0.3))
tx(2, "sold to pay interest (CNBC)", 600, 540, 36, RO, kw(12, "pay", 0.0))
# 3: handelaren met geleend geld
kop(3, borden[3], "3. Traders who borrowed money")
b(3, "n_kaarten", 65, 80, 300, 270, kw(13, "traders", -0.2))
tx(3, "~$700M wiped out in 1 day", 400, 100, 48, RO, kw(14, "700", 0.0))
b(3, "n_handelaars", 400, 220, 450, 280, kw(14, "crypto", -0.2))
tx(3, "140,000+ traders", 890, 330, 34, RO, kw(15, "140", 0.0))
# 4: AI trekt het geld weg
kop(4, borden[4], "4. Investors chasing AI")
b(4, "n_magneet", 65, 80, 460, 340, kw(16, "chasing", -0.3))
tx(4, "“AI is sucking out every", 560, 120, 36, BL, kw(17, "sucking", -0.4), 0.8)
tx(4, "marginal dollar away from crypto”", 560, 170, 36, BL, kw(17, "marginal", 0.0), 0.8)
tx(4, "Jean-Marie Mognetti, CoinShares", 580, 250, 32, GR, kw(17, "mognetti", 0.0))
# 5: wat nu
kop(5, borden[5], "What comes next")
b(5, "n_7dagen", 65, 90, 420, 110, kw(18, "seventh", -0.3))
tx(5, "heading for a 7th weekly loss", 65, 230, 42, RO, kw(18, "weekly", 0.0))
b(5, "n_evenwicht", 620, 80, 420, 260, kw(19, "footing", -0.4))
tx(5, "a footing under $60,000?", 640, 370, 40, BL, kw(19, "$60", 0.0))
b(5, "n_vraag", 65, 380, 140, 200, kw(20, "bottom", -0.3))
tx(5, "the bottom, or just the start?", 230, 460, 52, RO, kw(20, "start", -0.3))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items")
