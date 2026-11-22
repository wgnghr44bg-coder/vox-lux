"""Market Doodle Short 1 (staand 1080x1920) bij video 1: "You paid $79.99 for GTA 6. Who got your money?" (22 nov 2026). Cijfers + bronnen: bronnen.md
  python maak.py -> scene.json"""
import json, re
Z = json.load(open("zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
W = json.load(open("woorden.json", encoding="utf-8"))
def kw(zin, woord, na=0.15):
    for i, w, t0, t1 in W:
        if i == zin and re.sub(r"[^\w$%.\-]", "", w.lower()).startswith(woord.lower()): return round(t0 + na, 2)
    print("LET OP: woord niet gevonden:", zin, woord); return s[zin] + 0.2
A = "afbeeldingen/"; L = "logos/"
BL, RO, GR, IN = [25, 55, 120], [214, 32, 39], [46, 150, 84], [30, 30, 30]
it = []
GRENS = [0, 1, 4, 6]
borden = [0.0] + [s[i] - 0.3 for i in GRENS[1:]]
def b(k, naam, x, y, br, h, t0, dur=1.2):
    it.append({"bord": k, "beeld": A + naam + ".png", "x": x, "y": y, "breed": br, "hoog": h, "midden": True, "start": t0 - 0.3, "doel": t0, "teken": min(dur, 1.3), "kleur": 0.5})
def tx(k, t, x, y, maat, kl, t0, dur=0.6): it.append({"bord": k, "tekst": t, "x": x, "y": y, "maat": maat, "kleur": kl, "start": t0 - 0.15, "doel": t0, "teken": min(dur, 0.7)})
def kop(k, titel): it.append({"bord": k, "kop": titel, "rechts": "Not financial advice", "start": borden[k]})
def lg(k, naam, x, y, h, t0): it.append({"bord": k, "logo": L + naam + ".png", "x": x, "y": y, "hoog": h, "start": t0 - 0.2, "doel": t0})
def streep(k, x0, y, x1, t0, kl=IN): it.append({"bord": k, "streep": [x0, y, x1], "kleur": kl, "dik": 4, "start": t0, "teken": 0.6})
def pijl(k, x0, y0, x1, y1, t0, kl=IN): it.append({"bord": k, "pijl": [x0, y0, x1, y1], "kleur": kl, "dik": 6, "start": t0, "teken": 0.5})
def over(k, bedrag, t0): tx(k, f"left: {bedrag}", 820, 600, 46, GR, t0)


def bron(k, t, t0): tx(k, t, 60, 1800, 34, IN, t0, 0.4)
kop(0, "Who got your money?")
b(0, "p_wolk", 60, 170, 960, 520, kw(0, "who", -0.4))
b(0, "p_denkkoop", 290, 640, 500, 800, kw(0, "paid", -0.2))
tx(0, "$79.99", 140, 1470, 170, GR, kw(0, "$79"), 0.6)
tx(0, "paid!", 160, 1680, 80, IN, kw(0, "$79", 0.7))
kop(1, "Who gets what?")
b(1, "r_winkelier", 50, 170, 320, 500, kw(1, "store", -0.4))
tx(1, "the store", 420, 260, 70, IN, kw(1, "store", -0.1))
tx(1, "~ $24", 420, 350, 150, RO, kw(1, "$24", -0.2), 0.6)
b(1, "r_pak", 50, 700, 320, 500, kw(2, "sony", -0.4))
tx(1, "Sony", 420, 790, 70, IN, kw(2, "sony", -0.1))
tx(1, "~ $12", 420, 880, 150, RO, kw(2, "12", -0.2), 0.6)
b(1, "r_helm", 50, 1230, 320, 480, kw(3, "disc", -0.4))
tx(1, "disc, box, truck", 420, 1320, 60, IN, kw(3, "box", -0.2))
tx(1, "~ $4", 420, 1400, 150, RO, kw(3, "$4", -0.2), 0.6)
bron(1, "~ = estimate (analyst Serkan Toto)", kw(1, "keeps"))
kop(2, "And Rockstar?")
b(2, "p_geld", 290, 170, 500, 800, kw(4, "take", -0.4))
lg(2, "taketwo", 80, 1020, 110, kw(4, "owner", -0.2))
tx(2, "Take-Two: ~$40", 80, 1170, 110, GR, kw(4, "40", -0.2), 0.6)
tx(2, "but first, pay back", 80, 1360, 66, IN, kw(5, "pay", -0.3))
tx(2, "~$1-2 billion", 80, 1450, 130, RO, kw(5, "$2", -0.4), 0.6)
tx(2, "(estimate: what the game cost)", 90, 1630, 44, IN, kw(5, "cost", -0.2))
kop(3, "The twist")
b(3, "p_idee", 290, 170, 500, 540, kw(6, "twist", -0.4))
tx(3, "buy it digital:", 100, 790, 86, BL, kw(6, "digitally", -0.3))
tx(3, "Take-Two ~$56", 100, 910, 100, GR, kw(6, "56", -0.3), 0.6)
tx(3, "full breakdown", 100, 1150, 80, RO, kw(7, "breakdown", -0.4))
tx(3, "on the channel", 100, 1250, 80, RO, kw(7, "channel", -0.4))
b(3, "p_yt", 330, 1360, 420, 480, kw(7, "full", -0.2))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it, "W": 1080, "H": 1920},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
