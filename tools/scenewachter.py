"""Scènewachter (eigenaar 24 nov 2026: "wat kunnen we maken zodat dit voortaan automatisch wordt gezien en aangepast als het
niet klopt, ik moet nu elke keer zelf kijken" – na zwevende auto's, een router voor de koelkast, een bord in de lucht en een
tv die door de bank stond).

Elk voorwerp dat de renderer tekent, meldt zich met zijn kader en waar het OP staat. De wachter:
  1. ANKER: de onderkant moet in de band van dat vlak liggen (achtergronden.json: stoep, aanrecht, tafel, vloer ...).
     Zo niet -> zet het voorwerp er zelf op (geeft dx, dy terug) en schrijft "aangepast" in het rapport.
  2. MUUR: iets wat hangt (tv, klok) moet helemaal binnen een muurstuk vallen en mag geen meubel raken.
  3. BOTSING: valt de onderkant binnen de voetafdruk van een meubel (bank, koelkast, kast), dan staat het er dóórheen ->
     schuift het opzij naar de dichtstbijzijnde vrije plek op hetzelfde vlak; lukt dat niet -> FOUT.
  4. GEZICHT: iets wat vóór de poppetjes getekend wordt, mag geen gezicht bedekken (behalve wat die persoon vasthoudt).
  5. GEEN ANKER opgegeven -> FOUT ("waar staat dit op?").
op-waarden: een vlaknaam uit achtergronden.json | "muur" | "hand:<naam>" / "bek" / "aan:<iets>" (vastgehouden, met
punt=(x, y): het voorwerp moet dat punt raken) | "beeld" (grafiek bovenop het beeld: telefoonscherm, biljet, kop) .

Gebruik in een renderer:
    W = Scenewachter(Path(".../achtergronden.json"))
    W.begin(bg_naam, t)
    dx, dy = W.plaats("router", (x0, y0, x1, y1), op="aanrecht")          # vóór het tekenen; schuif mee
    W.plaats("bord", box, op="tafel-rechts", voor=True)                    # voor=True: getekend vóór de poppetjes
    W.einde(gezichten={"dad": (cx, cy, r), ...})
    W.rapport()  -> lijst met meldingen (leeg = goed). Na de render: W.schrijf(Path("SCENEWACHTER.md")).
"""
import json
from pathlib import Path

class Scenewachter:
    def __init__(self, achtergronden, marge=6):
        self.A = json.loads(Path(achtergronden).read_text(encoding="utf-8")); self.marge = marge
        self.meld = {}                                    # (soort, voorwerp, bg, detail) -> eerste tijd
        self.bg = None; self.t = 0.0; self.voor = []; self.extra = {}; self.gezien = {}

    # ---------- per frame ----------
    def begin(self, bg, t):
        self.bg = bg; self.t = t; self.voor = []; self.extra = {}
        if bg not in self.A: self._m("FOUT", "achtergrond", f"'{bg}' staat niet in achtergronden.json (eerst opmeten)")

    def vlak(self, naam, band):
        """Vlak van een zelfgetekend meubel (bv. keukentafel) voor de rest van dit frame: [x0, x1, y_achter, y_voor]."""
        self.extra[naam] = band

    def _m(self, soort, naam, tekst):
        k = (soort, naam, self.bg, tekst)
        if k not in self.meld: self.meld[k] = self.t

    def plaats(self, naam, box, op=None, punt=None, voor=False):
        """Geeft (dx, dy) terug waarmee het voorwerp verschoven moet worden zodat het klopt (0, 0 = klopt al)."""
        x0, y0, x1, y1 = box; dx = dy = 0.0
        if voor: self.voor.append((naam, box, op))
        if op != "beeld": self.gezien.setdefault((naam, self.bg), []).append((self.t, tuple(box)))   # voor de herkenwachter (grafieken niet)
        A = self.A.get(self.bg)
        if A is None or op == "beeld": return 0.0, 0.0
        if op is None:
            self._m("FOUT", naam, "geen ondergrond opgegeven: waar staat dit op?"); return 0.0, 0.0
        if op.startswith(("hand:", "bek", "aan:")):
            if punt is not None:
                px, py = punt; m = 25
                if not (x0 - m <= px <= x1 + m and y0 - m <= py <= y1 + m):
                    self._m("FOUT", naam, f"wordt vastgehouden ({op}) maar raakt dat punt niet")
            return 0.0, 0.0
        if op == "muur":
            vrij = [r for r in A["muur"] if r[0] - self.marge <= x0 and x1 <= r[2] + self.marge and r[1] - self.marge <= y0 and y1 <= r[3] + self.marge]
            if not vrij: self._m("FOUT", naam, "hangt niet helemaal op een vrij stuk muur")
            for mn, (a0, b0, a1, b1) in A["meubels"].items():
                if x0 < a1 and x1 > a0 and y0 < b1 and y1 > b0: self._m("FOUT", naam, f"hangt over/achter meubel '{mn}'")
            return 0.0, 0.0
        vlakken = {**A["vlakken"], **self.extra}
        if op not in vlakken:
            self._m("FOUT", naam, f"vlak '{op}' bestaat niet in deze achtergrond"); return 0.0, 0.0
        vx0, vx1, ya, yv = vlakken[op][:4]; eigen = vlakken[op][4] if len(vlakken[op]) > 4 else op
        # 1. anker: onderkant in de band
        if y1 < ya - self.marge: dy = ya + 2 - y1
        elif y1 > yv + self.marge: dy = yv - 2 - y1
        if x1 <= 0 or x0 >= 1920: pass                     # (nog) buiten beeld, bv. auto die gaat inrijden: niet schuiven
        elif x1 < vx0: dx = vx0 - x1 + 10                 # helemaal naast het vlak; deels erop (bv. inrijden) is goed
        elif x0 > vx1: dx = vx1 - x0 - 10
        if dx or dy: self._m("AANGEPAST", naam, f"stond niet op '{op}' -> verschoven ({dx:+.0f}, {dy:+.0f})")
        # 3. botsing met meubels (onderkant binnen de voetafdruk, niet het meubel waar het op staat)
        bx0, bx1, by = x0 + dx, x1 + dx, y1 + dy
        if op in self.extra: return dx, dy                   # staat op een zelfgetekend meubel dat vóór de achtergrond staat
        for mn, (a0, b0, a1, b1) in A["meubels"].items():
            if mn in (op, eigen): continue
            if b0 < by < b1 and bx0 + (bx1 - bx0) * 0.15 < a1 and bx1 - (bx1 - bx0) * 0.15 > a0:
                links, rechts = a0 - bx1 - 4, a1 - bx0 + 4         # schuif naar de dichtstbijzijnde kant
                sch = links if abs(links) < abs(rechts) else rechts
                if vx0 <= (bx0 + bx1) / 2 + sch <= vx1:
                    dx += sch; bx0 += sch; bx1 += sch; self._m("AANGEPAST", naam, f"stond door '{mn}' -> opzij geschoven ({sch:+.0f})")
                else: self._m("FOUT", naam, f"staat door meubel '{mn}' en kan niet opzij")
        return dx, dy

    def einde(self, gezichten=None):
        for naam, (x0, y0, x1, y1), op in self.voor:
            if op == "beeld": continue
            for pn, (cx, cy, r) in (gezichten or {}).items():
                if op and op.endswith(":" + pn): continue
                ox = max(x0, min(cx, x1)); oy = max(y0, min(cy, y1))
                if (ox - cx) ** 2 + (oy - cy) ** 2 < (r * 0.8) ** 2: self._m("FOUT", naam, f"bedekt het gezicht van {pn}")

    # ---------- rapport ----------
    def rapport(self, soort=None):
        return [(t, s, n, bg, tekst) for (s, n, bg, tekst), t in sorted(self.meld.items(), key=lambda kv: kv[1]) if soort in (None, s)]

    def schrijf(self, pad, titel="Scènewachter"):
        r = self.rapport(); fout = [x for x in r if x[1] == "FOUT"]
        regels = [f"# {titel}", "", f"**{len(fout)} fouten**, {len(r) - len(fout)} zelf aangepast.", ""]
        for t, s, n, bg, tekst in r: regels.append(f"- {int(t // 60)}:{t % 60:04.1f} **{s}** {n} ({bg}): {tekst}")
        Path(pad).write_text("\n".join(regels) + "\n", encoding="utf-8"); return len(fout)
