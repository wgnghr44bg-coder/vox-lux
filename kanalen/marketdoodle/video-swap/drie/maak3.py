"""What If You Swapped Lives With Your Dad for a Week? — ± 2,5 min, liggend 1920x1080 (eigenaar 23 nov).
Simpel zoals de Short. Alleen jij en papa ruilen; iedereen houdt zijn EIGEN stem, de mond beweegt bij het LIJF.
Naamkaartje boven het lijf: YOU (in papa's lijf), DAD (in jouw lijf). Meer mensen in beeld waar het klopt.
Geen effect bij scènewissel, geen muziek. Gebruik: python maak3.py [--plaat]  -> swap-3min.mp4"""
import json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)

W, H, FPS, SS = 1920, 1080, 30, ps.SS
ps.C.update({                                           # extra mensen (andere kleuren dan de familie)
 "kid1": dict(broek=(60, 60, 80), shirt=(220, 80, 70), haar=(150, 90, 50), kapsel="kort", groot=0.9),
 "kid2": dict(broek=(70, 90, 70), shirt=(80, 190, 170), haar=(40, 30, 25), kapsel="paard", groot=0.88),
 "kid3": dict(broek=(60, 70, 60), shirt=(240, 150, 60), haar=(40, 30, 25), kapsel="krul", groot=0.9),
 "col1": dict(broek=(60, 60, 70), shirt=(70, 160, 170), haar=(200, 160, 90), kapsel="paard", bril=True, groot=1.08),
 "col2": dict(broek=(70, 70, 80), shirt=(230, 140, 70), haar=(60, 50, 45), kapsel="kort", groot=1.12),
 "kassa": dict(broek=(60, 70, 60), shirt=(110, 170, 80), haar=(90, 60, 40), kapsel="staartjes", pet=(110, 170, 80), groot=1.05),
})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.5
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
LIJF = {"YOU": "dad", "DAD": "you", "MOM": "mom", "SIS": "sis", "BOSS": "boss", "TEACH": "teach"}
def luid(t, lijf):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == lijf for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
KAART = {"dad": ("YOU", (70, 130, 220)), "you": ("DAD", (90, 180, 110))}
NAAM = {"YOU": "YOU", "DAD": "DAD", "MOM": "MOM", "SIS": "SISTER", "TEACH": "TEACHER", "BOSS": "BOSS"}
BGNAAM = {"kantine": "schoolplein", "nacht": "keuken-nacht"}
CAST = {"slaapkamer-ouders": ["dad"], "badkamer": ["dad"], "kamer-jij": ["you"], "titel": ["dad", "you"], "kantoor": ["col1", "dad", "col2"],
        "klas": ["kid1", "you", "kid2", "teach"], "kantine": ["kid1", "you", "kid2", "kid3"], "winkel": ["dad", "kassa"], "feit": ["dad"],
        "nacht": ["dad", "you", "sis"]}
PLEK = {1: ([960], 2.0), 2: ([700, 1220], 1.85), 3: ([560, 960, 1360], 1.6), 4: ([520, 820, 1120, 1420], 1.45), 5: ([420, 680, 940, 1200, 1500], 1.4)}
XVAST = {("feit", "dad"): 520, ("badkamer", "dad"): 1420}
DAGEN = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
TEKST = [("Two hundred and forty", "240", "240 EMAILS · ALL URGENT", "rood"), ("Four out of ten", "4", "4 / 10", "rood"), ("I got an eight", "8", "8 / 10", "groen"),
         ("Rent. The car", "rent", "RENT · CAR · FOOD · LIGHTS · PHONE", "wit"), ("already gone", "gone", "ALMOST GONE", "rood"),
         ("About two hundred thirty-three", "$233", "$233,000", "geel"), ("still in Dad's body", "still", "STILL SWAPPED", "rood"),
         ("swap stays forever", "forever", "FOREVER?", "rood"), ("number keeps going up", "number", "$87.40", "rood")]
BRON = "Source: USDA, Expenditures on Children by Families, 2015 ($233,610, birth to age 17)"
VERBAASD = ("no idea", "urgent", "gone", "Wait", "still in", "finds out", "doorbell", "Oh no", "looking back", "screams", "huge")
BOOS = ("harder than my job", "talk like a dad", "Stop", "Where is the milk", "You don't have a dog")

blokken = []
for i, z in enumerate(Z):
    dag = any(z[2].startswith(d.capitalize()) for d in DAGEN)
    if not blokken or blokken[-1][0] != z[3] or dag: blokken.append([z[3], i, i])
    else: blokken[-1][2] = i
SC = []
for naam, a, b in blokken:
    tekst = " ".join(Z[i][2] for i in range(a, b + 1)); sprekers = {Z[i][4] for i in range(a, b + 1)}
    if naam == "keuken":
        cast = ["dad", "you", "mom", "sis"] if ("rules" in tekst or "7 a.m. The week" in tekst) else (["dad", "mom"] if "MOM" in sprekers else ["dad"])
    else: cast = list(CAST.get(naam, ["dad"]))
    if "BOSS" in sprekers and "boss" not in cast: cast.append("boss")
    if naam == "keuken" and "doorbell" in tekst: cast.append("boss")
    xs, s = PLEK[len(cast)]
    pop = []
    for n, x in zip(cast, xs):
        d = dict(n=n, x=XVAST.get((naam, n), x), s=s)
        if n == "boss" and naam == "keuken":
            i0 = next(i for i in range(a, b + 1) if "doorbell" in Z[i][2]); d["loop"] = (kw(i0, "boss", -1.2), kw(i0, "boss", 0.2), 2150, x)
        pop.append(d)
    kop, slot = [], 0
    for i in range(a, b + 1):
        for dg in DAGEN:
            if Z[i][2].startswith(dg.capitalize()): kop.append((Z[i][0], dg, 60 + len(dg) * 20, 70, 60, "geel"))
        for stuk, woord, tx, kl in TEKST:
            if stuk in Z[i][2]:
                big = tx == "$233,000"
                kop.append((kw(i, woord, -0.1), tx, 1150 if big else 960, 330 if big else 200 + 110 * slot, 150 if big else (64 if len(tx) > 22 else 90), kl)); slot += 1
    if naam == "titel":
        i0 = a; kop += [(kw(i0, "what"), "WHAT IF YOU SWAPPED LIVES", 960, 120, 104, "wit"), (kw(i0, "dad"), "WITH YOUR DAD?", 960, 245, 120, "geel")]
    SC.append(dict(t=0.0 if not SC else Z[a][0] - 0.1, naam=naam, bg=BGNAAM.get(naam, naam), pop=pop, kop=kop, a=a, b=b))

FB, FS, KL = ps.FB, ps.FS, ps.KL
font = ps.font
BG = {}
def bg(n):
    if n not in BG: BG[n] = Image.open(HIER.parent / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
def kaartje(img, s, x, y, kl):
    f = font(FB, 34); d = ImageDraw.Draw(img); b = d.textbbox((0, 0), s, font=f); w, h = b[2] - b[0], b[3] - b[1]
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
    if Z[i][4] in NAAM:
        fn = font(FB, 30); n = NAAM[Z[i][4]]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 50, W / 2 + nb / 2 + 14, y - 10), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 48), n, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)
WAKKER = kw(0, "wake")

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]
    img = bg(sc["bg"]).copy()
    nu = next((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    spreker = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    sp = next((p for p in sc["pop"] if p["n"] == spreker), None)
    if sc["naam"] == "badkamer":                               # papa's gezicht in de spiegel
        x0, y0, x1, y1 = 812, 96, 1150, 398
        sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
        ps.poppetje(ImageDraw.Draw(sl), "dad", (x0 + x1) / 2, y1 + 380, 1.6, t, kijk=0.8, verbaasd=True, mond=luid(t, "dad"))
        sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1))
        glas = img.crop((x0, y0, x1, y1)).convert("RGBA"); glas.alpha_composite(sl)
        img.paste(Image.blend(glas.convert("RGB"), img.crop((x0, y0, x1, y1)), 0.25), (x0, y0))
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    for p in sc["pop"]:
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]
            if t < a: continue
            f = ps.ease((t - a) / max(0.1, b - a)); x = x0 + (x1 - x0) * f
            if t < b: loop = (t - a) * 2.2
        if sp is not None and p is not sp: kijk = 0.9 if sp["x"] > x else -0.9
        else: kijk = 0.5 if x < 960 else -0.5
        if sc["naam"] == "badkamer": kijk = -1.0
        geb = None
        if sp is p and nu is not None and t - Z[nu][0] < 1.4:
            z = Z[nu][2]
            if "!" in z: geb = "wijs" if x < 960 else "wijslinks"
            elif "?" in z: geb = "schouders"
        familie = p["n"] in ("dad", "you", "mom", "sis")
        boos = sp is p and any(w in tekst_nu for w in BOOS)
        verb = familie and any(w in tekst_nu for w in VERBAASD) and not boos
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13 or (sc["naam"] == "slaapkamer-ouders" and t < WAKKER)
        koppen[p["n"]] = ps.poppetje(d, p["n"], x, 960, p["s"], t, loop=loop, kijk=kijk, mond=luid(t, p["n"]), knipper=knip, verbaasd=verb, gebaar=geb, boos=boos)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for n, (s, kl) in KAART.items():
        if n in koppen and not (sc["naam"] == "kamer-jij" and t < kw(3, "dad")): kaartje(img, s, koppen[n][0], koppen[n][1] - 45, kl)
    for st, s, x, y, m, kl in sc["kop"]:
        if t >= st: kop(img, s, x, y, m, KL[kl], ps.pop((t - st) / 0.3))
    if sc["naam"] == "feit" and any(s == "$233,000" and t >= st for st, s, *_ in sc["kop"]):
        ImageDraw.Draw(img).text((40, 1035), BRON, font=font(FS, 28), fill=(60, 50, 50))
    ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((400, 225)) for z in Z]
        for v in range(0, len(ims), 24):
            pl = Image.new("RGB", (400 * 6, 225 * 4))
            for i, im in enumerate(ims[v:v + 24]): pl.paste(im, (400 * (i % 6), 225 * (i // 6)))
            pl.save(HIER / f"plaat-{v // 24}.jpg", quality=80)
        print("platen", (len(ims) + 23) // 24); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "swap-3min.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 20) == 0: print(f"{i / FPS:.0f} / {EIND:.0f} s", flush=True)
    p.stdin.close(); p.wait(); print("KLAAR swap-3min.mp4", round(EIND, 1), "s")
