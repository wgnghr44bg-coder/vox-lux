"""Momentwachter (eigenaar 28 nov 2026: "wat er gezegd wordt zie je niet op beeld").
De tekstwachter kijkt alleen of iets dat genoemd wordt ergens in die zin in beeld is (de pot was in beeld -> 0 fouten), niet of de
HANDELING gebeurt op het moment dat ze gezegd wordt ("opens a jar", "rips the door off", "sit down", "nobody notices").
Deze wachter kijkt per zinsdeel: rond de woorden (van het eerste woord - VOOR tot het laatste woord + NA seconden) moet de
gevraagde toestand minstens één keer in beeld zijn; met "!" ervoor mag hij er juist NIET zijn (bv. "!sis:wijs" bij "nobody notices").

Gebruik in een renderer:
    from momentwachter import Momentwachter
    MW = Momentwachter(SW, {"opens a jar": ["deksel-los"], "rips the fridge door off": ["deur-los"], "nobody notices": ["!sis:wijs"]})
    ... per frame:  MW.zie(t, toestanden)      # toestanden = set met namen van voorwerpen/handelingen die NU in beeld zijn,
                                               # plus "naam:gebaar" voor de poppetjes (bv. "sis:wijs")
    MW.schrijf(pad) -> aantal fouten (MOMENTWACHTER.md)
"""
import re
VOOR, NA = 0.15, 0.6

def _norm(w): return re.sub(r"[^a-z0-9']", "", w.lower())

class Momentwachter:
    def __init__(self, woorden, regels):
        """woorden = [[zin, woord, t0, t1], ...] (scriptwoorden met tijden); regels = {zinsdeel: [toestand, ...]}"""
        self.ramen = []
        ws = [(z, _norm(w), t0, t1) for z, w, t0, t1 in woorden]
        for deel, eisen in regels.items():
            d = [_norm(x) for x in deel.split()]
            gevonden = False
            for i in range(len(ws) - len(d) + 1):
                if all(ws[i + k][1] == d[k] and ws[i + k][0] == ws[i][0] for k in range(len(d))):
                    self.ramen.append(dict(deel=deel, a=ws[i][2] - VOOR, b=ws[i + len(d) - 1][3] + NA, eisen=eisen, gezien=set(), verboden=set()))
                    gevonden = True
            if not gevonden: self.ramen.append(dict(deel=deel, a=None, b=None, eisen=eisen, gezien=set(), verboden=set()))
    def zie(self, t, toestanden):
        for r in self.ramen:
            if r["a"] is None or not (r["a"] <= t <= r["b"]): continue
            for e in r["eisen"]:
                if e.startswith("!"):
                    if e[1:] in toestanden: r["verboden"].add(e[1:])
                elif e in toestanden: r["gezien"].add(e)
    def fouten(self):
        f = []
        for r in self.ramen:
            if r["a"] is None: f.append(f'zinsdeel "{r["deel"]}" niet gevonden in de woordtijden'); continue
            for e in r["eisen"]:
                if e.startswith("!"):
                    if e[1:] in r["verboden"]: f.append(f'{r["a"] + VOOR:.1f} s "{r["deel"]}": {e[1:]} is in beeld, maar dat spreekt de tekst tegen')
                elif e not in r["gezien"]: f.append(f'{r["a"] + VOOR:.1f} s "{r["deel"]}": je ziet {e} niet gebeuren terwijl het gezegd wordt')
        return f
    def schrijf(self, pad):
        f = self.fouten()
        open(pad, "w", encoding="utf-8").write("# Momentwachter\n\n**%d fouten** (wat gezegd wordt moet je op dat moment zien gebeuren).\n\n" % len(f)
                                               + "".join(f"- {x}\n" for x in f))
        return len(f)
