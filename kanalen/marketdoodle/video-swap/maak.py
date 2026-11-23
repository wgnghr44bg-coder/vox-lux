"""Lange What If-video 'Swapped lives' — liggend 1920x1080 (eigenaar 23 nov: eerst een proef).
Poppetjes uit ../proef-pop-short/pop_short.py (zelfde personages als de Short). Geen effect bij scènewissel, geen muziek.
Het LIJF wordt getekend; een klein naamkaartje boven het hoofd laat zien wie er IN zit (YOU / DAD / MOM / SISTER).
Gebruik: python maak.py [--plaat]  -> proef.mp4 (of plaat.jpg: één beeld per zin)"""
import json, math, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, str(Path(__file__).parent.parent / "proef-pop-short"))
import os; _cwd = os.getcwd(); os.chdir(Path(__file__).parent.parent / "proef-pop-short")
import pop_short as ps                                 # laadt zijn eigen bestanden relatief; daarna terug
os.chdir(_cwd)

W, H, FPS, SS = 1920, 1080, 30, ps.SS
Z = json.load(open("zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open("woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.0
AUD, SR = sf.read("stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def luid(t, zinnen):
    if not any(Z[i][0] <= t <= Z[i][1] for i in zinnen): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
ease, pop = ps.ease, ps.pop

# lijf -> wie zit erin (naamkaartje) ; spreker (ziel) -> welk lijf praat
ZIEL = {"dad": ("YOU", (70, 130, 220)), "you": ("DAD", (90, 180, 110)), "mom": ("SISTER", (235, 190, 40)), "sis": ("MOM", (160, 120, 220))}
LIJF = {"YOU": "dad", "DAD": "you", "MOM": "sis", "SIS": "mom", "TEACH": "teach", "BOSS": "boss"}
Y = 960
def Zs(i): return Z[i][0] - 0.1
SC = [
 dict(t=0, bg="slaapkamer-ouders", pop=[dict(n="dad", x=1250, s=2.2, kijk=lambda t: math.sin(t * 1.7) * 0.8 if t > kw(1, "open") else 0,
       dicht=lambda t: t < kw(1, "open"), verbaasd=kw(1, "ceiling"))]),
 dict(t=Zs(2), bg="badkamer", spiegel=(812, 96, 1150, 398), pop=[dict(n="dad", x=1380, s=2.2, kijk=lambda t: -1.0, verbaasd=kw(2, "dad"))]),
 dict(t=Zs(4), bg="kamer-jij", pop=[dict(n="you", x=760, s=2.3, kijk=lambda t: 0.3, verbaasd=Z[4][0], gebaar=[(Z[5][0], Z[5][1], "schouders")])],
      kaart=[("you", kw(4, "dad"))]),
 dict(t=Zs(6), bg="keuken", pop=[dict(n="mom", x=1150, s=2.1, kijk=lambda t: -0.6, boos=kw(6, "worst")),
                                 dict(n="sis", x=760, s=2.1, kijk=lambda t: 0.8, gebaar=[(Z[8][0], Z[8][1], "wijs")])],
      kaart=[("mom", Z[7][0]), ("sis", Z[8][0])]),
 dict(t=Zs(9), bg="keuken", pop=[dict(n="dad", x=560, s=1.4, kijk=lambda t: 0.6), dict(n="you", x=840, s=1.4, kijk=lambda t: -0.6),
                                 dict(n="mom", x=1110, s=1.4, kijk=lambda t: 0.5), dict(n="sis", x=1370, s=1.4, kijk=lambda t: -0.5)],
      kaart=[("dad", kw(9, "got")), ("you", kw(9, "dad", 0.2)), ("mom", kw(9, "mom")), ("sis", kw(9, "switched"))]),
 dict(t=Zs(10), bg="titel", pop=[dict(n="dad", x=560, s=1.9, kijk=lambda t: 0.4), dict(n="you", x=1360, s=1.9, kijk=lambda t: -0.4)],
      kop=[(kw(10, "what"), "WHAT IF YOU SWAPPED LIVES", 960, 170, 104, "wit"), (kw(10, "parents"), "WITH YOUR PARENTS?", 960, 300, 110, "geel")]),
 dict(t=Zs(11), bg="keuken", pop=[dict(n="dad", x=560, s=1.4, kijk=lambda t: 0.6), dict(n="you", x=840, s=1.4, kijk=lambda t: -0.6, boos=kw(14, "permanent"),
                                      gebaar=[(Z[14][0], Z[14][1], "stamp")]),
                                 dict(n="mom", x=1110, s=1.4, kijk=lambda t: 0.5), dict(n="sis", x=1370, s=1.4, kijk=lambda t: -0.5)],
      kaart=[("dad", 0), ("you", 0), ("mom", 0), ("sis", 0)],
      kop=[(kw(11, "seven"), "7 DAYS", 960, 110, 110, "geel"), (kw(12, "job"), "THEIR JOB  ·  THEIR SCHOOL  ·  THEIR BILLS", 960, 215, 60, "wit"),
           (kw(13, "nobody"), "NOBODY CAN KNOW", 960, 310, 80, "rood")],
      kopweg=Zs(14)),
]
NAAM = {"YOU": "YOU", "DAD": "DAD", "MOM": "MOM", "SIS": "SISTER", "TEACH": "TEACHER", "BOSS": "BOSS"}
FB, FS = ps.FB, ps.FS
def font(p, m): return ps.font(p, m)
KL = ps.KL

def kaartje(img, s, x, y, kl, sch):
    f = font(FB, int(34 * sch)); d = ImageDraw.Draw(img); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
    d.rounded_rectangle((x - w / 2 - 16, y - h / 2 - 10, x + w / 2 + 16, y + h / 2 + 12), 14, fill=kl, outline=(40, 35, 40), width=3)
    d.text((x - w / 2, y - h / 2 - b[1]), s, font=f, fill=(255, 255, 255))
def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = font(FS, 56); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 6 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 985
    sp = Z[i][4]
    if sp in NAAM and sp != "N":
        fn = font(FB, 30); n = NAAM[sp]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 50, W / 2 + nb / 2 + 14, y - 10), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 48), n, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)

BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(f"afbeeldingen/{n}.png").convert("RGB").resize((W, H))
    return BG[n]

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; t0 = sc["t"]
    img = bg(sc["bg"]).copy()
    if sc.get("spiegel"):                                          # papa's gezicht in de spiegel
        x0, y0, x1, y1 = sc["spiegel"]
        sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        ps.poppetje(ImageDraw.Draw(sl), "dad", (x0 + x1) / 2, y1 + 380, 1.6, t, kijk=0.8, verbaasd=t >= kw(2, "dad"),
                    mond=luid(t, [i for i, z in enumerate(Z) if z[4] == "YOU"]))
        sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1))
        glas = img.crop((x0, y0, x1, y1)).convert("RGBA"); glas.alpha_composite(sl)
        img.paste(Image.blend(glas.convert("RGB"), img.crop((x0, y0, x1, y1)), 0.25), (x0, y0))
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    for p in sc["pop"]:
        geb = next((g for a, b, g in p.get("gebaar", []) if a <= t <= b), None)
        sp = [i for i, z in enumerate(Z) if LIJF.get(z[4]) == p["n"]]
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13 or ("dicht" in p and p["dicht"](t))
        koppen[p["n"]] = ps.poppetje(d, p["n"], p["x"], p.get("y", Y), p["s"], t, kijk=p["kijk"](t), mond=luid(t, sp), knipper=knip,
                                     verbaasd=("verbaasd" in p and t >= p["verbaasd"]), gebaar=geb, boos=("boos" in p and t >= p["boos"]))
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for n, st in sc.get("kaart", []):
        st = st or t0
        if t >= st and n in koppen: kaartje(img, ZIEL[n][0], koppen[n][0], koppen[n][1] - 45, ZIEL[n][1], pop((t - st) / 0.3))
    for st, s, x, y, m, kl in sc.get("kop", []):
        if st <= t < sc.get("kopweg", 1e9): kop(img, s, x, y, m, KL[kl], pop((t - st) / 0.3))
    ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((480, 270)) for z in Z]
        n = len(ims); pl = Image.new("RGB", (480 * 4, 270 * ((n + 3) // 4)))
        for i, im in enumerate(ims): pl.paste(im, (480 * (i % 4), 270 * (i // 4)))
        pl.save("plaat.jpg", quality=85); print("plaat.jpg"); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", "proef.mp4"], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("KLAAR proef.mp4", round(EIND, 1), "s")
