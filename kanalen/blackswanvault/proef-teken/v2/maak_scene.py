"""BlackswanVault proef v2: wit bord, per zin een eigen tekening (links/rechts), bordjes met de kern. Cijfers uit video9/bronnen.md."""
import json
Z = json.load(open("../zinnen.json", encoding="utf-8")); s = [z[0] for z in Z]; e = [z[1] for z in Z]
A = "afbeeldingen/"; LG = "../logos/spacex.png"
it = []
def tot(k): return s[k] - 0.15 if k < len(s) else 1e9
def tek(naam, kant, k, eind, bordje=None, kl=None, y=70, h=430):
    x = 30 if kant == "L" else 655
    dur = max(1.4, min(2.6, (e[k] - s[k]) * 0.55))
    it.append({"beeld": A + naam + ".png", "x": x, "y": y, "breed": 595, "hoog": h, "midden": True, "start": s[k] + 0.1, "teken": dur, "kleur": 0.8, "tot": eind})
    if bordje:
        b = {"bordje": bordje, "x": x + 40, "y": y + h + 40, "maat": 46 if len(bordje) < 18 else 36, "start": s[k] + 0.1 + dur + 0.5, "tot": eind}
        if kl: b[kl] = True
        it.append(b)
# paren: (zin links, zin rechts) -> zelfde doek; doek leeg bij de volgende linkse zin
paren = [((0, "r00", "$127.79", "rood"), (1, "r01b", "IPO price: $135", None)),
         ((2, "r02", "The hype stock of 2026", None), (3, "r03", "One date in December", "rood")),
         ((4, "r01", "IPO: June 12", None), (5, "r05", "Record: $86 billion", "groen")),
         ((16, "r16", "The AI worry", None), (17, "r17", "~$40B in bonds + loans", None)),
         ((18, "r18", "5-year Nvidia chip lease", None), (19, "r19", "Chips into space?", None)),
         ((20, "r20", "Hard to get back", "rood"), (21, None, None, None)),
         ((22, "r22", "Insiders own shares", None), (23, "r23", "~6 months: no selling", None)),
         ((24, "r24", "= the lock-up", None), (25, "r03", "Ends: Dec 8", "rood")),
         ((26, "r26", "Frozen shares can be sold", None), (27, "r27", "Price can drop", "rood")),
         ((28, "r28", "Musk + insiders: June 2027", None), (29, "r29", "Nobody knows", None)),
         ((30, "r30", "Some will hold", "groen"), (31, "r31", "Dec 8: the date to watch", "rood"))]
volgende_links = [p[0][0] for p in paren] + [6, 11, 12]
def einde(k):
    na = sorted(x for x in volgende_links if x > k)
    return tot(na[0]) if na else 1e9
for (l, r) in paren:
    eind = einde(l[0])
    tek(l[1], "L", l[0], eind, l[2], l[3])
    if r[1]: tek(r[1], "R", r[0], eind, r[2], r[3])
it.append({"logo": LG, "x": 40, "y": 18, "hoog": 34, "start": s[0], "tot": tot(2)})
it.append({"tekst": "Now, the date:", "x": 700, "y": 200, "maat": 58, "kleur": [25, 55, 120], "start": s[21], "teken": 0.6, "tot": tot(22)})
it.append({"bordje": "December 8", "x": 720, "y": 320, "maat": 80, "rood": True, "start": s[21] + 0.6, "tot": tot(22)})
# koersgrafiek zin 6-10
it.append({"data": "../../video9/data/spcx.json".replace("../../","../../"), "logo": LG, "logohoog": 26, "onder": "closing price, US dollars", "taal": "en", "valuta": "$",
           "x": 40, "y": 40, "breed": 830, "hoog": 640, "start": s[6], "teken": e[9] - s[6] - 0.3, "tot": tot(11)})
it.append({"bordje": "First day: ~$161", "x": 905, "y": 150, "maat": 38, "start": s[6] + 2.0, "tot": tot(11)})
it.append({"bordje": "-40% from top", "x": 905, "y": 330, "maat": 42, "rood": True, "start": s[10] + 1.6, "tot": tot(11)})
# zin 11: waar verdient SpaceX geld
tek("r11", "L", 11, tot(12), None)
it[-1].update({"x": 260, "breed": 760, "hoog": 520})
it.append({"tekst": "Where does SpaceX make money?", "x": 330, "y": 600, "maat": 44, "kleur": [25, 55, 120], "start": s[11] + 1.0, "teken": 1.2, "tot": tot(12)})
# zin 12-15: staven links, tekening per zin rechts
it.append({"balken": [["Starlink", 11.4, "$11.4B"], ["Rockets", 4.1, "$4.1B"], ["AI", 3.2, "$3.2B"]], "logo": LG, "logohoog": 26, "onder": "revenue 2025",
           "x": 40, "y": 60, "breed": 600, "hoog": 600, "start": s[12], "starts": [s[12] + 3.0, s[14] + 1.0, s[15] + 1.0], "tot": tot(16)})
for k, naam, b, kl in ((12, "r12", "Starlink: $11.4B", None), (13, "r13", "Profit: $4.4B", "groen"), (14, "r14", "Rockets: a loss", "rood"), (15, "r15", "AI: lost ~$3.2B", "rood")):
    tek(naam, "R", k, tot(k + 1) if k < 15 else tot(16), b, kl)
json.dump({"duur": round(e[-1] + 2.0, 2), "items": it}, open("scene.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("items", len(it), "duur", round(e[-1] + 2, 1))
