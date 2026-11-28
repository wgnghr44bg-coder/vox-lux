"""Figuurwachter (eigenaar 28 nov 2026: "achter de tafel poppetje is helemaal weg ... zet hier ook een controle voor").
Kijkt per beeld of de poppetjes HEEL en ZICHTBAAR zijn zoals bedoeld:
  1. LIJF WEG   van elk poppetje moet het hoofd (>= KOP_MIN) en het lijf (>= LIJF_MIN) echt te zien zijn in het eindbeeld:
                er mag geen achtergrond, tafel of ander plaatje overheen geplakt zijn (zo verdween "you" achter de tafel).
                Vergelijkt de eigen laag van het poppetje met het eindbeeld (vóór camera/teksten), pixel voor pixel.
  2. BUITEN BEELD  bij een gebaar (duim, zwaai, juich, wijs ...) moet de hand binnen het camerabeeld vallen
                (mama's duim bij "Done!" viel erbuiten).
  3. LOS PLAATJE  elk los getekend plaatje (pijl, vlek, vorm) moet een naam hebben in de scènewachter (WACHT.plaats), anders
                weet niemand wat het is (de losse gele pijl). Renderer roept FW.los_plaatje(naam) aan bij zo'n tekening; een
                plaatje zonder uitleg (naam leeg) = fout.
Bewust (half) verborgen (onzichtbaar, achter een tafel geknipt) geef je mee met verborgen=True of registreer je de
geknipte laag zelf.  Schrijft FIGUURWACHTER.md; tools/poort.py eist 0 fouten.
"""
import numpy as np

KOP_MIN, LIJF_MIN, MIN_DUUR = 0.6, 0.35, 0.1

class Figuurwachter:
    def __init__(self):
        self.t = 0.0; self.nu = []; self.fout = {}
    def begin(self, t): self.t = t; self.nu = []
    def figuur(self, naam, laag, kop, lijf, handen=(), verborgen=False):
        """laag = RGBA-beeld (zelfde maat als het eindbeeld) met alleen dit poppetje; kop = (cx, cy, r); lijf = (x0, y0, x1, y1);
        handen = [(x, y, gebaar), ...] voor handen die iets doen"""
        self.nu.append((naam, laag, kop, lijf, list(handen), verborgen))
    def los_plaatje(self, naam):
        if not naam: self._f("los plaatje zonder naam/uitleg in beeld")
    def _f(self, tekst): self.fout.setdefault(tekst, []).append(self.t)
    def einde(self, eindbeeld, crop):
        """eindbeeld = PIL RGB vóór camera en teksten; crop = (x0, y0, x1, y1) van de camera"""
        E = np.asarray(eindbeeld.convert("RGB"), dtype=np.int16)
        for naam, laag, (cx, cy, r), (x0, y0, x1, y1), handen, verborgen in self.nu:
            if not verborgen:
                L = np.asarray(laag, dtype=np.int16); a = L[..., 3] > 200
                same = (np.abs(E - L[..., :3]).sum(axis=2) < 45) & a
                for deel, (bx0, by0, bx1, by1), mn in (("hoofd", (cx - r, cy - r, cx + r, cy + r), KOP_MIN), ("lijf", (x0, y0, x1, y1), LIJF_MIN)):
                    bx0, by0, bx1, by1 = [int(max(0, v)) for v in (bx0, by0, bx1, by1)]
                    n = a[by0:by1, bx0:bx1].sum()
                    if n < 50: continue
                    zicht = same[by0:by1, bx0:bx1].sum() / n
                    if zicht < mn: self._f(f"{naam}: {deel} maar {zicht:.0%} zichtbaar (er ligt iets overheen of het is weggeknipt)")
            for hx, hy, geb in handen:
                if not (crop[0] <= hx <= crop[2] and crop[1] <= hy <= crop[3]): self._f(f"{naam}: hand van gebaar '{geb}' valt buiten beeld")
    def fouten(self):
        uit = []
        for tekst, ts in self.fout.items():
            reeks = [[ts[0], ts[0]]]
            for t in ts[1:]:
                if t - reeks[-1][1] < 0.25: reeks[-1][1] = t
                else: reeks.append([t, t])
            for a, b in reeks:
                if b - a >= MIN_DUUR or len(ts) == 1: uit.append(f"{a:.1f}-{b:.1f} s: {tekst}")
        return uit
    def schrijf(self, pad):
        f = self.fouten()
        open(pad, "w", encoding="utf-8").write("# Figuurwachter\n\n**%d fouten** (poppetjes heel en zichtbaar, gebaren in beeld, geen losse plaatjes zonder uitleg).\n\n" % len(f)
                                               + "".join(f"- {x}\n" for x in f))
        return len(f)
