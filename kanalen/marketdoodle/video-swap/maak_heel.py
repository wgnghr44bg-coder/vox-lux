"""Hele lange video 'Swapped lives' (eigenaar 23 nov: "Ja is prima" na de proef). 1920x1080, ± 9 min.
Begin (zin 0-16) = scènes uit maak.py (goedgekeurde proef). Daarna automatisch per scène uit script.txt:
wie er staat (CAST), wie praat (mond + kijkt), gebaren bij ?/!, dagnaam bovenin, losse teksten/bedragen (TEKST).
Gebruik: python maak_heel.py [--plaat] [--van SEC --tot SEC]  -> swap-lang.mp4"""
import math, re, subprocess, sys
from PIL import Image, ImageDraw
import maak as m
ps, Z, WO, kw, luid = m.ps, m.Z, m.WO, m.kw, m.luid
W, H, FPS, SS = m.W, m.H, m.FPS, m.SS
EIND = Z[-1][1] + 1.5
FAM4 = ["dad", "you", "mom", "sis"]
CAST = {"bus": ["dad"], "kantoor": ["dad"], "klas": ["you", "teach"], "avond": ["dad", "you"], "bank": ["dad"], "post": ["dad"],
        "kleuterklas": ["sis"], "winkel": ["dad", "mom"], "gym": ["you", "teach"], "feit": ["dad"], "keuken": FAM4,
        "schoolplein": ["you"], "ouderavond": ["dad", "teach"], "nacht": FAM4, "park": FAM4}
BGNAAM = {"bank": "woonkamer", "post": "keuken", "nacht": "keuken-nacht"}
PLEK = {1: ([960], 2.0), 2: ([700, 1220], 1.85), 3: ([560, 960, 1360], 1.6), 4: ([560, 840, 1110, 1370], 1.4), 5: ([400, 650, 900, 1150, 1480], 1.4)}
XVAST = {("bus", "dad"): 1480, ("feit", "dad"): 520}
DAGEN = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
# losse teksten: (stukje uit de zin, kernwoord, tekst, kleur)
TEKST = [("two hundred and forty unread", "240", "240 UNREAD EMAILS", "rood"), ("says urgent", "urgent", "URGENT  URGENT  URGENT", "rood"),
         ("four out of ten", "4", "4 / 10", "rood"), ("Seventeen hundred", "$1", "RENT: $1,700", "rood"),
         ("The car payment", "car", "CAR · LIGHTS · INTERNET · PHONE · INSURANCE · FOOD", "wit"), ("already gone", "gone", "ALMOST GONE", "rood"),
         ("About two hundred thirty-three", "$233", "$233,000", "geel"), ("A pony?!", "pony", "A PONY?!", "rood"), ("Payday", "payday", "PAYDAY", "groen"),
         ("You cancel the pony", "cancel", "PONY: CANCELLED", "groen"), ("second pony", "second", "PONY #2", "rood"),
         ("6:59", "6", "6:59", "wit"), ("still in Dad's body", "still", "STILL SWAPPED", "rood"), ("becomes permanent.", "permanent", "PERMANENT?", "rood"),
         ("Food, clothes, a bedroom", "food", "FOOD · CLOTHES · ROOM · SCHOOL · DOCTOR", "wit")]
BRON = "Source: USDA, Expenditures on Children by Families, 2015 ($233,610, birth to age 17)"
VERBAASD = ("no idea", "urgent", "gone", "Wait", "pony", "permanent", "still in", "find out", "worst face", "Two hundred thirty-three")
BOOS = ("disgusting", "Really?", "Nine?", "A pony?!", "Permanent?", "talk like a dad", "my own childhood")

# ---- scènes bouwen ----
blokken = []
for i, z in enumerate(Z):
    nieuwe_dag = any(z[2].startswith(dg.capitalize()) for dg in DAGEN)   # nieuwe dag = nieuw blok (dagnaam + teksten opnieuw)
    if not blokken or blokken[-1][0] != z[3] or i == 17 or nieuwe_dag: blokken.append([z[3], i, i])
    else: blokken[-1][2] = i
SC = [s for s in m.SC]                                   # proef-scènes (zin 0-16)
for naam, a, b in blokken:
    if a < 17: continue
    cast = list(CAST.get(naam, ["dad"]))
    if any(Z[i][4] == "BOSS" for i in range(a, b + 1)) and "boss" not in cast: cast.append("boss")
    if naam == "ouderavond" and any(Z[i][4] == "DAD" for i in range(a, b + 1)): cast.append("you")
    xs, s = PLEK[len(cast)]
    pop = []
    for n, x in zip(cast, xs):
        d = dict(n=n, x=XVAST.get((naam, n), x), s=s * (1.0 if n not in ("teach", "boss") else 0.95))
        if n == "boss" and naam == "keuken":                 # baas loopt binnen bij zijn eerste zin
            i0 = next(i for i in range(a, b + 1) if Z[i][4] == "BOSS"); d["loop"] = (Z[i0][0] - 1.6, Z[i0][0] - 0.2, 2150, x)
        if n == "you" and naam == "ouderavond":              # papa (in jouw lijf) staat pas in de gang bij zijn zin
            d["vanaf"] = next(Z[i][0] - 2.5 for i in range(a, b + 1) if Z[i][4] == "DAD")
        pop.append(d)
    kop = []
    eerste = Z[a][2]
    for k, dag in enumerate(DAGEN):
        if any(Z[i][2].startswith(dag.capitalize()) for i in range(a, b + 1)):
            j = next(i for i in range(a, b + 1) if Z[i][2].startswith(dag.capitalize())); kop.append((Z[j][0], dag, 60 + len(dag) * 20, 70, 60, "geel"))
    slot = 0
    for i in range(a, b + 1):
        for stuk, woord, tx, kl in TEKST:
            if stuk in Z[i][2]:
                kop.append((kw(i, woord, -0.1), tx, 1150 if tx == "$233,000" else 960, 200 + 110 * slot if tx != "$233,000" else 330, 64 if len(tx) > 24 else (150 if tx == "$233,000" else 84), kl)); slot += 1
    SC.append(dict(t=Z[a][0] - 0.1, bg=BGNAAM.get(naam, naam), pop=pop, kaart=[(n, 0) for n in cast if n in m.ZIEL], kop=kop, auto=(a, b), feit=(naam == "feit")))

def spreker_x(t, sc):
    for i, z in enumerate(Z):
        if z[0] - 0.05 <= t <= z[1] + 0.2 and z[4] != "N":
            lijf = m.LIJF.get(z[4]); p = next((p for p in sc["pop"] if p["n"] == lijf), None)
            if p: return lijf, p, i
    return None, None, None

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]
    if "auto" not in sc: return m.frame(t)                # proef-deel: precies zoals goedgekeurd
    img = m.bg(sc["bg"]).copy()
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}
    lijf, sp, zi = spreker_x(t, sc)
    nu = next((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    for p in sc["pop"]:
        if t < p.get("vanaf", -1): continue
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]; f = ps.ease((t - a) / max(0.1, b - a)) if t > a else 0; x = x0 + (x1 - x0) * f
            if a < t < b: loop = (t - a) * 2.2
        if sp is not None and p is not sp: kijk = 0.9 if sp["x"] > x else -0.9
        elif sp is p: kijk = 0.7 if x < 960 else -0.7
        else: kijk = 0.3 if x < 960 else -0.3
        geb = None
        if sp is p and zi is not None and t - Z[zi][0] < 1.4:
            z = Z[zi][2]
            if z.startswith(("Morning", "Good morning")): geb = "zwaai"
            elif "!" in z: geb = "wijs" if x < 960 else "wijslinks"
            elif "?" in z: geb = "schouders"
        mond = luid(t, [i for i, z in enumerate(Z) if m.LIJF.get(z[4]) == p["n"]])
        verb = any(w in tekst_nu for w in VERBAASD) and p["n"] in ("dad", "you", "mom", "sis")
        boos = sp is p and any(w in tekst_nu for w in BOOS)
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13
        koppen[p["n"]] = ps.poppetje(d, p["n"], x, m.Y, p["s"], t, loop=loop, kijk=kijk, mond=mond, knipper=knip, verbaasd=verb and not boos, gebaar=geb, boos=boos)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for n, st in sc.get("kaart", []):
        if n in koppen: m.kaartje(img, m.ZIEL[n][0], koppen[n][0], koppen[n][1] - 45, m.ZIEL[n][1], 1.0)
    for st, s, x, y, mt, kl in sc["kop"]:
        if t >= st: m.kop(img, s, x, y, mt, m.KL[kl], ps.pop((t - st) / 0.3))
    if sc.get("feit") and any(s == "$233,000" and t >= st for st, s, *_ in sc["kop"]):
        f = m.font(m.FS, 28); ImageDraw.Draw(img).text((40, 1035), BRON, font=f, fill=(60, 50, 50))
    m.ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--plaat" in sys.argv:                            # één beeld per zin, in vellen van 24
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((400, 225)) for z in Z]
        for v in range(0, len(ims), 24):
            pl = Image.new("RGB", (400 * 6, 225 * 4))
            for i, im in enumerate(ims[v:v + 24]): pl.paste(im, (400 * (i % 6), 225 * (i // 6)))
            pl.save(f"plaat-{v // 24}.jpg", quality=80)
        print("platen", (len(ims) + 23) // 24); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", "stem.wav", "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest",
                          "swap-lang.mp4"], stdin=subprocess.PIPE)
    n = int(EIND * FPS)
    for i in range(n):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 30) == 0: print(f"{i / FPS / 60:.1f} / {EIND / 60:.1f} min", flush=True)
    p.stdin.close(); p.wait(); print("KLAAR swap-lang.mp4", round(EIND, 1), "s")
