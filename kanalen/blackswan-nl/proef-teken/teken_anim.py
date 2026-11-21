"""Whiteboard-animatie (eigenaar 21 nov: "word op beeld getekend gelijk met het verhaal").
Een tekening (zwarte lijnen op wit) wordt eerst lijn voor lijn 'getekend' (pen-volgorde), daarna loopt de kleur erin.
Meerdere tekeningen komen op hetzelfde witte doek, elk op een eigen moment (straks: begin van de zin uit zinnen.json).

  python teken_anim.py scene.json uit.mp4
scene.json: {"duur": 12, "items": [{"beeld": "a.png", "x": 60, "y": 80, "breed": 520, "start": 0.3, "teken": 3.0, "kleur": 1.0},
                                   {"bordje": "€4400", "x": 320, "y": 560, "start": 4.2}, ...]}"""
import json, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1280, 720, 30
TEGEL = 10


def wit_maken(im):
    """achtergrond (licht, weinig kleur) -> puur wit"""
    a = np.asarray(im.convert("RGB")).astype(np.int16).copy()
    a[:6], a[-6:], a[:, :6], a[:, -6:] = 255, 255, 255, 255              # randje van het AI-beeld weg
    licht = (a.min(axis=2) > 225) & ((a.max(axis=2) - a.min(axis=2)) < 25)
    a[licht] = 255
    return a.astype(np.uint8)


def pen_volgorde(lijn):
    """tegels met lijnen in de volgorde waarin een pen ze zou tekenen (steeds de dichtstbijzijnde volgende)"""
    h, w = lijn.shape
    ty, tx = np.nonzero(lijn[: h // TEGEL * TEGEL, : w // TEGEL * TEGEL].reshape(h // TEGEL, TEGEL, w // TEGEL, TEGEL).any(axis=(1, 3)))
    pts = np.stack([ty, tx], 1).astype(np.float32)
    if len(pts) == 0:
        return pts.astype(int)
    over = np.ones(len(pts), bool); orde = []
    i = int(np.argmin(pts[:, 0] * 3 + pts[:, 1]))            # begin bovenaan links
    for _ in range(len(pts)):
        orde.append(i); over[i] = False
        if not over.any(): break
        idx = np.nonzero(over)[0]
        d = np.abs(pts[idx] - pts[i]).sum(1)
        i = idx[int(np.argmin(d))]
    return pts[orde].astype(int)


class Tekening:
    def __init__(self, it):
        im = Image.open(it["beeld"]).convert("RGB")
        ys, xs = np.nonzero(wit_maken(im).min(axis=2) < 245)          # bijsnijden tot de tekening zelf
        im = im.crop((max(0, xs.min() - 6), max(0, ys.min() - 6), xs.max() + 6, ys.max() + 6))
        s = min(it["breed"] / im.width, it.get("hoog", 10000) / im.height)      # past in breed én hoogte
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
        if it.get("midden"): it["x"] = int(it["x"] + (it["breed"] - im.width) / 2)
        self.kleur = wit_maken(im)
        g = self.kleur.mean(axis=2)
        self.lijn = g < 80
        self.bg = self.kleur.min(axis=2) >= 245
        if KRIJT:                                                   # BlackswanVault: krijt op donker bord (21 nov)
            kr = np.array(KRIJT, np.uint8)
            self.kleur = np.where(self.lijn[..., None], kr, (self.kleur * 0.9).astype(np.uint8))
        self.lijnbeeld = np.where(self.lijn[..., None], self.kleur, 255).astype(np.uint8)
        self.orde = pen_volgorde(self.lijn)
        self.x, self.y = it["x"], it["y"]
        self.start, self.teken, self.kduur = it["start"], it.get("teken", 3.0), it.get("kleur", 1.0)
        h, w = self.lijn.shape
        # kleur loopt erin als een zachte veeg van linksboven naar rechtsonder
        yy, xx = np.mgrid[0:h, 0:w]
        self.veeg = ((xx / w) * 0.6 + (yy / h) * 0.4)

    def op(self, doek, t):
        if t < self.start: return
        h, w = self.lijn.shape
        p = min(1.0, (t - self.start) / self.teken)
        vak = doek[self.y:self.y + h, self.x:self.x + w]
        if p < 1.0:
            n = int(len(self.orde) * p)
            m = np.zeros((h // TEGEL + 1, w // TEGEL + 1), bool)
            if n: m[self.orde[:n, 0], self.orde[:n, 1]] = True
            m = np.kron(m, np.ones((TEGEL, TEGEL), bool))[:h, :w] & self.lijn
            vak[m] = self.lijnbeeld[m]
            return
        q = min(1.0, (t - self.start - self.teken) / self.kduur)
        a = np.clip((q * 1.3 - self.veeg) / 0.3, 0, 1)[..., None]
        vak[self.lijn] = self.kleur[self.lijn]
        vul = ~self.bg & ~self.lijn                                 # vlakken: van doek naar kleur
        vak[vul] = (vak[vul] * (1 - a[vul]) + self.kleur[vul] * a[vul]).astype(np.uint8)


class Bordje:
    FONT = "C:/Windows/Fonts/rockb.ttf"

    def __init__(self, it):
        maat = it.get("maat", 84); d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
        while True:                                                 # "maxbreed": kleiner tot het past (bordjes naast elkaar)
            f = ImageFont.truetype(self.FONT, maat)
            b = d.textbbox((0, 0), it["bordje"], font=f); tw, th = b[2] - b[0], b[3] - b[1]
            if not it.get("maxbreed") or tw + 100 <= it["maxbreed"] or maat <= 16: break
            maat -= 2
        pw, ph = 46, 34; w, h = tw + 2 * pw, th + 2 * ph
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 16, fill=(30, 28, 32, 255))
        rood = it.get("rood") or it.get("groen"); bg, fg = (((46, 150, 84, 255) if it.get("groen") else (214, 32, 39, 255)), (255, 255, 255, 255)) if rood else ((238, 228, 208, 255), (22, 22, 48, 255))
        d.rounded_rectangle((9, 9, w - 10, h - 10), 11, fill=bg)
        d.rounded_rectangle((18, 18, w - 19, h - 19), 7, outline=fg if rood else (30, 28, 32, 255), width=4)
        d.text((pw - b[0], ph - b[1]), it["bordje"], font=f, fill=fg)
        self.im, self.x, self.y, self.start = im, it["x"], it["y"], it["start"]

    def op(self, doek, t):
        if t < self.start: return
        k = min(1.0, (t - self.start) / 0.25)
        s = 0.6 + 0.5 * k - 0.1 * max(0, (t - self.start - 0.25) / 0.15 if t - self.start < 0.4 else 1)   # klein 'plop'
        s = max(0.6, min(1.1, s))
        im = self.im.resize((max(1, int(self.im.width * s)), max(1, int(self.im.height * s))), Image.LANCZOS)
        cx, cy = self.x + self.im.width // 2, self.y + self.im.height // 2
        x0, y0 = cx - im.width // 2, cy - im.height // 2
        x0, y0 = min(max(0, x0), W - im.width), min(max(0, y0), H - im.height)   # altijd binnen beeld
        a = np.asarray(im).astype(np.float32) / 255
        vak = doek[y0:y0 + im.height, x0:x0 + im.width]
        al = a[..., 3:4]
        vak[:] = (vak * (1 - al) + a[..., :3] * 255 * al).astype(np.uint8)


INKT, PAPIER = (28, 28, 34), (255, 255, 255)
KRIJT = None
FH = "C:/Windows/Fonts/segoeprb.ttf"          # handschrift-achtig (Segoe Print Bold)


def schrijf(d, xy, tekst, maat, kleur=INKT, anker="la"):
    d.text(xy, tekst, font=ImageFont.truetype(FH, maat), fill=kleur, anchor=anker)


class Lijn:
    """koersgrafiek die getekend wordt: assen, dan de lijn met een pen-punt, dan top en laagste als bordjes (vaste regel)"""
    def __init__(self, it):
        r = json.load(open(it["data"]))["chart"]["result"][0]
        import datetime as dt
        p = [(dt.date.fromtimestamp(a), b) for a, b in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if b]
        self.p, self.x, self.y, self.w, self.h = p, it["x"], it["y"], it["breed"], it["hoog"]
        self.start, self.teken, self.titel = it["start"], it.get("teken", 3.0), it.get("titel", "")
        v = [b for _, b in p]; lo, hi = min(v), max(v); m = (hi - lo) * 0.12
        self.lo, self.hi = lo - m, hi + m
        self.pts = [(self.x + 40 + i / (len(p) - 1) * (self.w - 60), self.y + 130 + (self.hi - b) / (self.hi - self.lo) * (self.h - 160))
                    for i, (_, b) in enumerate(p)]
        self.itop = max(range(len(p)), key=lambda i: p[i][1]); self.ilaag = min(range(len(p)), key=lambda i: p[i][1])

    @staticmethod
    def eur(b):
        return "€" + f"{b:,.0f}".replace(",", ".")

    def op(self, doek, t):
        if t < self.start: return
        im = Image.fromarray(doek); d = ImageDraw.Draw(im)
        q = t - self.start
        a = min(1.0, q / 0.5)                                   # assen
        x0, y1 = self.x + 30, self.y + self.h - 20
        d.line((x0, self.y + 60, x0, self.y + 60 + (y1 - self.y - 60) * a), fill=INKT, width=4)
        d.line((x0, y1, x0 + (self.w - 30) * a, y1), fill=INKT, width=4)
        if self.titel: schrijf(d, (x0, self.y), self.titel, 30)
        p = max(0.0, min(1.0, (q - 0.5) / self.teken))
        n = max(2, int(len(self.pts) * p))
        if p > 0:
            d.line(self.pts[:n], fill=(200, 40, 40), width=6, joint="curve")
            if p < 1:
                cx, cy = self.pts[n - 1]; d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), fill=INKT)
        im_np = np.asarray(im); doek[:] = im_np
        for i, naam, nr in ((self.itop, "TOP", 0), (self.ilaag, "NU" if self.ilaag == len(self.p) - 1 else "LAAGSTE", 1)):
            tt = 0.5 + self.teken * (i + 1) / len(self.pts) + 0.2
            if q >= tt:
                cx, cy = self.pts[i]; dd = ImageDraw.Draw(im := Image.fromarray(doek))
                dd.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(200, 40, 40), outline=INKT, width=3)
                datum = f"{self.p[i][0].day} {['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'][self.p[i][0].month-1]}"
                doek[:] = np.asarray(im)
                b = Bordje({"bordje": f"{naam} {self.eur(self.p[i][1])} ({datum})", "maat": 30, "x": 0, "y": 0, "start": self.start + tt})
                bx = int(min(max(cx - b.im.width / 2, self.x), self.x + self.w - b.im.width))
                by = int(cy - b.im.height - 22) if nr == 0 else int(cy + 22)
                if nr == 1 and by + b.im.height > self.y + self.h: by = int(cy - b.im.height - 22); bx = int(cx - b.im.width - 20)
                b.x, b.y = bx, by; b.op(doek, t)


class Taart:
    """taartdiagram: omtrek wordt getekend, daarna kleuren de stukken één voor één in (zonder getallen = niets verzonnen)"""
    KLEUREN = [(76, 175, 80), (255, 152, 0), (120, 120, 120), (33, 150, 243), (244, 67, 54)]

    def __init__(self, it):
        self.x, self.y, self.r, self.delen = it["x"], it["y"], it["straal"], it["delen"]
        self.start, self.teken = it["start"], it.get("teken", 2.0)

    def op(self, doek, t):
        if t < self.start: return
        q = t - self.start; im = Image.fromarray(doek); d = ImageDraw.Draw(im)
        cx, cy, r = self.x + self.r, self.y + self.r, self.r
        box = (cx - r, cy - r, cx + r, cy + r)
        tot = sum(self.delen); hoek = -90
        fase = min(1.0, q / (self.teken * 0.4)); kl = max(0.0, (q - self.teken * 0.4) / (self.teken * 0.6))
        for k, dl in enumerate(self.delen):
            h = dl / tot * 360
            if kl * len(self.delen) > k:
                d.pieslice((box[0] + 12, box[1] + 10, box[2] + 12, box[3] + 10), hoek, hoek + h, fill=tuple(int(c * .6) for c in self.KLEUREN[k % 5]))
                d.pieslice(box, hoek, hoek + h, fill=self.KLEUREN[k % 5], outline=INKT, width=5)
            hoek += h
        d.arc(box, -90, -90 + 360 * fase, fill=INKT, width=5)
        doek[:] = np.asarray(im)


class Tekst:
    """kop in handschrift die letter voor letter verschijnt"""
    def __init__(self, it):
        self.it = it

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        n = int(len(it["tekst"]) * min(1.0, (t - it["start"]) / it.get("teken", 1.0)))
        im = Image.fromarray(doek); schrijf(ImageDraw.Draw(im), (it["x"], it["y"]), it["tekst"][:n], it.get("maat", 44), tuple(it.get("kleur", INKT)))
        doek[:] = np.asarray(im)


class Balken:
    """staven die omhoog groeien, elk op een eigen moment; label eronder, bedrag erboven"""
    KLEUREN = [(33, 150, 243), (76, 175, 80), (255, 152, 0), (244, 67, 54)]

    def __init__(self, it):
        self.it = it

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        im = Image.fromarray(doek); d = ImageDraw.Draw(im)
        x, y, w, h = it["x"], it["y"], it["breed"], it["hoog"]
        a = min(1.0, (t - it["start"]) / 0.4)
        d.line((x, y + h, x + w * a, y + h), fill=INKT, width=5)
        mx = max(b[1] for b in it["balken"]); n = len(it["balken"]); bw = w / (n * 1.6)
        for k, (naam, v, label) in enumerate(it["balken"]):
            st = it.get("starts", [it["start"] + 0.4 + k * 0.8] * n)[k]
            if t < st: continue
            g = min(1.0, (t - st) / 0.8); g = 1 - (1 - g) ** 3
            bh = (h - 70) * v / mx * g; bx = x + bw * 0.4 + k * bw * 1.6
            d.rectangle((bx + 8, y + h - bh + 8, bx + bw + 8, y + h), fill=(200, 200, 200))
            d.rectangle((bx, y + h - bh, bx + bw, y + h), fill=self.KLEUREN[k % 4], outline=INKT, width=4)
            schrijf(d, (bx + bw / 2, y + h + 12), naam, 30, anker="ma")
            if g >= 1: schrijf(d, (bx + bw / 2, y + h - bh - 12), label, 34, anker="md")
        doek[:] = np.asarray(im)


class Pijl:
    """pijl die zichzelf tekent"""
    def __init__(self, it):
        self.it = it

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        x0, y0, x1, y1 = it["pijl"]; p = min(1.0, (t - it["start"]) / it.get("teken", 0.6))
        xe, ye = x0 + (x1 - x0) * p, y0 + (y1 - y0) * p
        im = Image.fromarray(doek); d = ImageDraw.Draw(im)
        d.line((x0, y0, xe, ye), fill=INKT, width=6)
        if p >= 1:
            v = np.array([x1 - x0, y1 - y0], float); v /= np.linalg.norm(v) + 1e-9; n = np.array([-v[1], v[0]])
            pk = np.array([x1, y1]); a = pk - v * 26 + n * 16; b = pk - v * 26 - n * 16
            d.polygon([tuple(pk), tuple(a), tuple(b)], fill=INKT)
        doek[:] = np.asarray(im)


class Dagen:
    """dagkoersen als staafjes vanaf een nullijn (rood = omlaag), één voor één; uit echte slotkoersen (data + laatste n dagen)"""
    def __init__(self, it):
        import datetime as dt
        r = json.load(open(it["dagen"]))["chart"]["result"][0]
        p = [(dt.date.fromtimestamp(a), b) for a, b in zip(r["timestamp"], r["indicators"]["quote"][0]["close"]) if b]
        n = it.get("n", 7)
        self.d = [(p[i][0], (p[i][1] / p[i - 1][1] - 1) * 100) for i in range(len(p) - n, len(p))]
        self.it = it

    def op(self, doek, t):
        it = self.it
        if t < it["start"]: return
        im = Image.fromarray(doek); d = ImageDraw.Draw(im)
        x, y, w, h = it["x"], it["y"], it["breed"], it["hoog"]
        y0 = y + 40; a = min(1.0, (t - it["start"]) / 0.4)
        d.line((x, y0, x + w * a, y0), fill=INKT, width=5)
        mx = max(abs(v) for _, v in self.d); n = len(self.d); bw = w / (n * 1.5)
        per = it.get("per", 0.35)
        for k, (dag, v) in enumerate(self.d):
            st = it["start"] + 0.4 + k * per
            if t < st: continue
            g = min(1.0, (t - st) / 0.35); g = 1 - (1 - g) ** 3
            bh = (h - 130) * abs(v) / mx * g; bx = x + bw * 0.3 + k * bw * 1.5
            kl = (214, 32, 39) if v < 0 else (76, 175, 80)
            d.rectangle((bx, y0, bx + bw, y0 + bh), fill=kl, outline=INKT, width=3)
            maand = ['jan','feb','mrt','apr','mei','jun','jul','aug','sep','okt','nov','dec'][dag.month - 1]
            schrijf(d, (bx + bw / 2, y0 - 8), f"{dag.day} {maand}", 22, anker="md")
            if g >= 1: schrijf(d, (bx + bw / 2, y0 + bh + 8), f"{v:+.1f}%".replace(".", ",").replace("-", "−"), 24, anker="ma")
        doek[:] = np.asarray(im)


def maak(i):
    import mooi                                                   # 21 nov: mooiere grafieken + logo's
    for k, c in (("bordje", Bordje), ("data", mooi.Lijn), ("delen", Taart), ("tekst", Tekst), ("balken", mooi.Balken),
                 ("pijl", Pijl), ("dagen", mooi.Dagen), ("logo", mooi.Logo)):
        if k in i: return c(i)
    return Tekening(i)


def main():
    sc = json.load(open(sys.argv[1], encoding="utf-8")); uit = sys.argv[2]
    global KRIJT, INKT, PAPIER
    if sc.get("bord"):                                              # donker bord: krijtkleur voor lijnen en tekst
        PAPIER = tuple(sc["bord"]); KRIJT = INKT = (236, 236, 228)
        import mooi; mooi.thema_donker()
    items = [(maak(i), i.get("tot", 1e9)) for i in sc["items"]]   # "tot": tijd waarop het doek weer leeg gaat
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", uit],
                         stdin=subprocess.PIPE)
    for f in range(int(sc["duur"] * FPS)):
        t = f / FPS
        doek = np.empty((H, W, 3), np.uint8); doek[:] = PAPIER
        for it, tot in items:
            if t < tot: it.op(doek, t)
        p.stdin.write(doek.tobytes())
    p.stdin.close(); p.wait(); print("KLAAR", uit)


if __name__ == "__main__":
    main()
