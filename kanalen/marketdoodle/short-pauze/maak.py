"""Short 'What If You Could Pause Time?' (23 nov) — zoals de eerste Short: staand 1080x1920, poppetjes uit code,
eigen stem verteller, personages eigen stem, ondertitels geel woord, geen muziek, geen effect bij scènewissel.
Bevroren = iedereen behalve jij staat stil (niet knipperen, mond dicht) + licht blauwe waas; 'PAUSED' bovenin.
Gebruik: python maak.py [--plaat]  -> short-pauze.mp4"""
import json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)

W, H, FPS, SS = 1080, 1920, 30, ps.SS
ps.C.update({"kid1": dict(broek=(60, 60, 80), shirt=(220, 80, 70), haar=(150, 90, 50), kapsel="kort", groot=0.92),
             "kid2": dict(broek=(70, 90, 70), shirt=(80, 190, 170), haar=(40, 30, 25), kapsel="paard", groot=0.9)})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.3
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def luid(t):                                             # alleen jij praat (YOU)
    if not any(Z[i][0] <= t <= Z[i][1] and Z[i][4] == "YOU" for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
PAUZE = kw(1, "press", 0.2)                              # vanaf hier staat de wereld stil
def Zs(i): return Z[i][0] - 0.1
BGDIR = HIER.parent / "proef-pop-short" / "afbeeldingen"
BG = {}
def bg(n):
    if n not in BG:
        p = HIER / "afbeeldingen" / f"{n}.png"
        BG[n] = Image.open(p if p.exists() else BGDIR / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
Y = 1460
# scènes: bevroren poppetjes (n, x, s, kijk, gebaar, mondopen) + jij (x, s) + kopteksten + extra
SC = [
 dict(t=0, bg="gang", vast=[], jij=dict(x=540, s=2.2, loop=(kw(0, "hallway", -1.0), kw(0, "hallway", 0.6), 200, 540)), kop=[(0, "8:59", 540, 260, 130, "wit")]),
 dict(t=Zs(2), bg="klas", vast=[("teach", 900, 1.55, -0.8, "wijslinks", True), ("kid1", 170, 1.5, 0.6, "zwaai", False), ("kid2", 390, 1.5, 0.6, None, True)],
      jij=dict(x=640, s=1.6), bal=(290, 930), kop=[]),
 dict(t=Zs(4), bg="nacht", vast=[], jij=dict(x=540, s=2.3), kop=[(kw(4, "what"), "WHAT IF YOU COULD", 540, 330, 82, "wit"), (kw(4, "pause"), "PAUSE TIME?", 540, 450, 110, "geel")]),
 dict(t=Zs(5), bg="klas", vast=[("teach", 900, 1.55, -0.8, "wijslinks", True), ("kid1", 170, 1.5, 0.6, "zwaai", False), ("kid2", 390, 1.5, 0.6, None, True)],
      jij=dict(x=640, s=1.6), bal=(290, 930),
      kop=[(kw(5, "every"), "1 MINUTE PAUSED", 540, 250, 72, "wit"), (kw(5, "older"), "= 1 MINUTE OLDER", 540, 345, 72, "rood")], kopweg=Zs(6),
      kop2=[(kw(6, "copy"), "COPY ANSWERS", 540, 250, 70, "wit"), (kw(6, "hair"), "FIX YOUR HAIR", 540, 345, 70, "wit"), (kw(6, "cookie"), "EAT THE COOKIE", 540, 440, 70, "geel")]),
 dict(t=Zs(7), bg="keuken", vast=[("mom", 760, 1.9, -0.6, "wijs", True), ("sis", 950, 1.7, -0.6, None, False)], jij=dict(x=330, s=1.9),
      teller=[(kw(7, "10"), "PAUSED: 10 MIN"), (kw(7, "hour"), "PAUSED: 1 HOUR")]),
 dict(t=Zs(8), bg="ruimte", vast=[], jij=None, kop=[(kw(8, "38", -0.1), "+38 MICROSECONDS", 540, 1180, 84, "geel"), (kw(8, "every"), "EVERY DAY", 540, 1290, 72, "wit")],
      bron="Source: GPS.gov, relativity corrections for GPS satellite clocks"),
 dict(t=Zs(10), bg="badkamer", vast=[], jij=dict(x=830, s=1.85), spiegel=(276, 266, 788, 658), grijs=kw(10, "gray", -0.2),
      teller=[(kw(12, "almost"), "PAUSED TOTAL: ~1 YEAR")]),
 dict(t=Zs(13), bg="gang", vast=[("kid1", 250, 1.8, 0.4, "zwaai", True), ("kid2", 830, 1.8, -0.4, None, False)], jij=dict(x=540, s=2.0),
      kop=[(kw(14, "nothing"), "NOT WORKING", 540, 330, 96, "rood"), (kw(14, "clock"), "TICK... TICK...", 540, 450, 80, "wit")]),
]
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
def kop(img, s, x, y, m, kl, sch): ps.kop(img, s, x, y, m, kl, sch)
def ondertitel(img, t):
    zi = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi: return
    i = zi[-1]; ws = [w for w in WO if w[0] == i]
    if not ws: return
    f = font(FS, 58); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 4 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1].upper() + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 1620
    if Z[i][4] == "YOU":
        fn = font(FB, 30); nb = d.textlength("YOU", font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 52, W / 2 + nb / 2 + 14, y - 12), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 50), "YOU", font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)
def pauzeknop(img, rood=False):                          # 'PAUSED' bovenin met pauze-teken
    d = ImageDraw.Draw(img); kl = (240, 70, 60) if rood else (255, 255, 255)
    d.rounded_rectangle((330, 60, 750, 160), 30, fill=(20, 25, 45), outline=kl, width=5)
    d.rectangle((370, 85, 390, 135), fill=kl); d.rectangle((405, 85, 425, 135), fill=kl)
    d.text((450, 78), "PAUSED", font=font(FB, 58), fill=kl)

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]
    img = bg(sc["bg"]).copy()
    bevroren = t >= PAUZE and sc["bg"] != "ruimte"
    if sc.get("spiegel"):                                 # jouw spiegelbeeld (met grijze haar)
        x0, y0, x1, y1 = sc["spiegel"]
        sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); ds = ImageDraw.Draw(sl)
        top = ps.poppetje(ds, "you", (x0 + x1) / 2, 860, 1.5, t, kijk=0.8, verbaasd=t >= sc["grijs"], mond=luid(t))
        if t >= sc["grijs"]: ds.line([(top[0] * SS - 10 * SS, (top[1] + 6) * SS), (top[0] * SS + 25 * SS, (top[1] + 28) * SS)], fill=(220, 220, 225), width=8 * SS)
        sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1))
        glas = img.crop((x0, y0, x1, y1)).convert("RGBA"); glas.alpha_composite(sl)
        img.paste(Image.blend(glas.convert("RGB"), img.crop((x0, y0, x1, y1)), 0.25), (x0, y0))
    vast = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dv = ImageDraw.Draw(vast)
    for n, x, s, kijk, geb, open_ in sc["vast"]:
        ps.poppetje(dv, n, x, Y, s, 0.0 if bevroren else t, kijk=kijk, mond=0.5 if open_ else 0.0, knipper=False, gebaar=geb)
    if sc.get("bal"):
        bx, by = sc["bal"]; dv.ellipse([((bx - 34) * SS, (by - 34) * SS), ((bx + 34) * SS, (by + 34) * SS)], fill=(230, 80, 60), outline=(45, 38, 40), width=5 * SS)
    vast = vast.resize((W, H), Image.LANCZOS); img.paste(vast, (0, 0), vast)
    if bevroren: img = Image.blend(img, Image.new("RGB", (W, H), (120, 160, 255)), 0.14)      # stilstaande wereld: lichte blauwe waas
    if sc.get("jij"):
        j = sc["jij"]; x = j["x"]; loop = None
        if "loop" in j:
            a, b, x0, x1 = j["loop"]; f = ps.ease((t - a) / max(0.1, b - a)) if t > a else 0; x = x0 + (x1 - x0) * f
            if a < t < b: loop = (t - a) * 2.4
        laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
        top = ps.poppetje(dl, "you", x, Y, j["s"], t, loop=loop, kijk=math.sin(t * 1.3) * 0.7, mond=luid(t),
                          knipper=(t % 3.4) < 0.13, verbaasd=sc["bg"] in ("badkamer",) or (sc["bg"] == "gang" and k > 0) or sc["bg"] == "nacht")
        if sc.get("grijs") and t >= sc["grijs"]:
            dl.line([(top[0] * SS - 10 * SS, (top[1] + 6) * SS), (top[0] * SS + 30 * SS, (top[1] + 34) * SS)], fill=(220, 220, 225), width=9 * SS)
        laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    if bevroren: pauzeknop(img, rood=(k == len(SC) - 1 and t >= kw(14, "nothing")))
    weg = sc.get("kopweg", 1e9)
    for st, s, x, y, m, kl in sc.get("kop", []):
        if st <= t < weg: kop(img, s, x, y + (120 if bevroren and y < 300 else 0), m, KL[kl], ps.pop((t - st) / 0.3))
    for st, s, x, y, m, kl in sc.get("kop2", []):
        if t >= st: kop(img, s, x, y + 120, m, KL[kl], ps.pop((t - st) / 0.3))
    tel = [s for st, s in sc.get("teller", []) if t >= st]
    if tel: kop(img, tel[-1], 540, 215 if sc.get("spiegel") else 330, 56 if sc.get("spiegel") else 72, KL["geel"], 1.0)
    if sc.get("bron") and t >= sc["kop"][0][0]: ImageDraw.Draw(img).text((40, 1860), sc["bron"], font=font(FS, 26), fill=(200, 200, 220))
    ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 8, 480 * 2)); [pl.paste(im, (270 * (i % 8), 480 * (i // 8))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-filter_complex", "[1:a]apad,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "short-pauze.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("KLAAR short-pauze.mp4", round(EIND, 1), "s")
