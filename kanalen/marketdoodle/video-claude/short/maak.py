"""Market Doodle Short 2 (staand 1080x1920) bij video 2: "How much does Anthropic make from my Claude subscription?" (22 nov 2026). Cijfers + bronnen: bronnen.md
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
GRENS = [0, 1, 3, 5]
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
kop(0, "My Claude subscription")
b(0, "n_chat", 140, 170, 800, 420, kw(0, "claude", -0.3))
tx(0, "$20 / month", 140, 640, 140, GR, kw(0, "$20", -0.2), 0.6)
b(0, "p_wolk2", 60, 850, 960, 520, kw(0, "how", -0.4))
b(0, "p_denk", 330, 1330, 420, 560, kw(0, "subscription", -0.6))
kop(1, "Where does my $20 go?")
b(1, "r_helm", 40, 170, 340, 520, kw(1, "computers", -0.4))
tx(1, "computers", 420, 270, 70, IN, kw(1, "computers", -0.1))
tx(1, "~$11.63", 400, 360, 125, RO, kw(1, "$11", -0.2), 0.6)
b(1, "r_lab", 40, 760, 320, 500, kw(2, "people", -0.4))
tx(1, "people", 420, 850, 70, IN, kw(2, "people", -0.1))
tx(1, "~$2.02", 420, 940, 150, RO, kw(2, "$2", -0.2), 0.6)
b(1, "n_puzzel", 40, 1330, 340, 240, kw(2, "sales", -0.4))
tx(1, "sales & partners", 420, 1330, 64, IN, kw(2, "sales", -0.1))
tx(1, "~$2.78", 420, 1420, 150, RO, kw(2, "partners", 0.1), 0.6)
kop(2, "And the rest?")
b(2, "n_hart", 60, 170, 420, 320, kw(3, "charity", -0.4))
tx(2, "charity (shares)", 520, 220, 60, IN, kw(3, "charity", -0.1))
tx(2, "~$2.36", 520, 300, 130, RO, kw(3, "$2", -0.2), 0.6)
b(2, "n_kosten2", 60, 560, 420, 300, kw(3, "everything", -0.4))
tx(2, "everything else", 520, 600, 60, IN, kw(3, "everything", -0.1))
tx(2, "~$1.87", 520, 680, 130, RO, kw(3, "$1", -0.2), 0.6)
tx(2, "Anthropic: -$0.67", 60, 1000, 92, RO, kw(4, "loses", -0.2), 0.6)
tx(2, "per $20", 90, 1140, 70, IN, kw(4, "$20", -0.3))
tx(2, "+ interest: back above 0", 80, 1300, 76, GR, kw(4, "interest", -0.2), 0.6)
bron(2, "~ = Q3 2026 company averages (Anthropic prospectus)", kw(3, "charity"))
kop(3, "But on paper...")
tx(3, "-$23 billion", 50, 220, 140, RO, kw(5, "$23", -0.3), 0.7)
tx(3, "in one quarter?!", 90, 420, 90, IN, kw(5, "quarter", -0.3))
b(3, "p_schrik", 290, 600, 500, 760, kw(5, "why", -0.4))
tx(3, "full breakdown", 120, 1450, 90, RO, kw(5, "breakdown", -0.4))
tx(3, "on the channel", 120, 1560, 90, RO, kw(5, "channel", -0.4))
json.dump({"duur": round(e[-1] + 2.0, 2), "borden": borden, "schuif": 0, "zoom": 0, "items": it, "W": 1080, "H": 1920},
          open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print(len(it), "items,", len(borden), "borden")
