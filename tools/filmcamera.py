"""Filmcamera (eigenaar 27 nov 2026: "kan het iets meer levendiger of iets meer film met de camera?").
Maakt van de zinnen een shotlijst zoals een tv-serie en rendert de uitsnede:
  - begin van een scène: WIJD shot (waar zijn we), ± 1,5 s
  - personage praat: CLOSE-UP op de spreker (shot / tegenshot, harde knip tussen sprekers)
  - verteller: MEDIUM shot met iedereen in beeld, langzame push-in
  - uitroep (!): korte PUNCH-IN extra op het laatste woord
  - handheld: heel lichte, rustige trilling (geen schok)
  - scherptediepte: bij een close-up wordt de achtergrond wazig (renderer tekent achtergrond en poppetjes apart)
Gebruik:
    cam = FilmCamera(W, H, zinnen, woorden, posities={"DAD": (x, hoofd_y), ...}, scenes=[(t0, t1), ...])
    box, waas = cam.uitsnede(t)          # (x0, y0, x1, y1) in beeldcoördinaten, en hoeveel de achtergrond wazig moet (0..1)
    beeld = cam.toepassen(img, t)        # uitsnede + schalen
"""
import math
from PIL import Image

def _ease(x): x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

class FilmCamera:
    def __init__(self, W, H, zinnen, woorden, posities, scenes=None, wijd=1.0, medium=1.25, close=1.7, punch=1.15, handheld=3.0):
        self.W, self.H, self.Z, self.WO, self.pos = W, H, zinnen, woorden, posities
        self.scenes = scenes or [(0.0, zinnen[-1][1] + 2)]
        self.k = dict(wijd=wijd, medium=medium, close=close, punch=punch); self.hh = handheld
        self.shots = self._plan()

    def _plan(self):
        shots = []
        for s0, s1 in self.scenes:
            zz = [z for z in self.Z if s0 <= z[0] < s1]
            t = s0; shots.append(dict(t0=s0, t1=min(s0 + 1.5, zz[0][0] + 0.6 if zz else s1), soort="wijd"))
            for i, z in enumerate(zz):
                a = max(shots[-1]["t1"], z[0] - 0.15); b = zz[i + 1][0] - 0.15 if i + 1 < len(zz) else s1
                if b <= a: continue
                sp = z[4]
                shots.append(dict(t0=a, t1=b, soort="close" if sp in self.pos else "medium", wie=sp, zin=z))
        return shots

    def _shot(self, t):
        for sh in self.shots:
            if sh["t0"] <= t < sh["t1"]: return sh
        return self.shots[-1]

    def uitsnede(self, t):
        sh = self._shot(t); W, H = self.W, self.H; u = (t - sh["t0"]) / max(0.1, sh["t1"] - sh["t0"])
        if sh["soort"] == "wijd": cx, cy, zm = W / 2, H / 2, self.k["wijd"] + 0.04 * _ease(u)
        elif sh["soort"] == "medium":
            xs = [p[0] for p in self.pos.values()]; ys = [p[1] for p in self.pos.values()]
            cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2 + H * 0.12; zm = self.k["medium"] + 0.06 * _ease(u)
        else:
            hx, hy = self.pos[sh["wie"]]; cx, cy = hx, hy + H * 0.08; zm = self.k["close"] + 0.05 * _ease(u)          # hoofd met ruimte erboven
            z = sh["zin"]
            if z[2].rstrip().endswith("!"):                                            # uitroep: punch-in op het laatste woord
                ww = [w for w in self.WO if abs(w[2] - z[0]) < (z[1] - z[0]) + 0.1 and z[0] - 0.05 <= w[2] <= z[1]]
                if ww and t >= ww[-1][2] - 0.05: zm *= 1 + (self.k["punch"] - 1) * _ease((t - ww[-1][2] + 0.05) / 0.18)
        # handheld: rustige, langzame trilling
        cx += self.hh * (math.sin(t * 1.7) + 0.5 * math.sin(t * 3.9 + 1)); cy += self.hh * 0.7 * (math.sin(t * 2.3 + 2) + 0.5 * math.sin(t * 4.7))
        bw, bh = W / zm, H / zm; x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh)
        waas = 0.0 if sh["soort"] != "close" else min(1.0, (zm - 1.3) / 0.6)
        return (x0, y0, x0 + bw, y0 + bh), waas

    def toepassen(self, img, t):
        (x0, y0, x1, y1), _ = self.uitsnede(t)
        return img.crop((int(x0), int(y0), int(x1), int(y1))).resize((self.W, self.H), Image.LANCZOS)
