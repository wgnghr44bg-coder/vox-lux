"""Short 'What If You Built a Real Cyborg?' (24 nov, eigenaar; vervangt Pause Time). Staand 1080x1920, poppetjes uit code,
eigen stem verteller + eigen stemmen, ondertitels geel woord, geen muziek, geen effect bij scènewissel, echte geluiden (CC0).
Lessen (WHATIF-AFSPRAKEN.md): eerste 5 s midden in de chaos, alles klopt als een film, spullen echt in de hand,
geen grote tekst bovenin die hetzelfde zegt als de ondertitel. Gebruik: python maak.py [--plaat] -> short-cyborg.mp4"""
import json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parent / "proef-pop-short"))
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); import pop_short as ps; os.chdir(_c)
W, H, FPS, SS = 1080, 1920, 30, ps.SS
ps.C["cyborg"] = dict(ps.C["you"], robot=True)
ps.C.update({"kid1": dict(broek=(60, 60, 80), shirt=(220, 80, 70), haar=(150, 90, 50), kapsel="kort", groot=0.92),
             "kid2": dict(broek=(70, 90, 70), shirt=(80, 190, 170), haar=(40, 30, 25), kapsel="paard", groot=0.9)})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
EIND = Z[-1][1] + 1.2
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
def kw(zin, woord, na=0.0):
    for i, w, t0, t1 in WO:
        if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); return Z[zin][0]
def luid(t, spreker):
    if not any(Z[i][0] <= t <= Z[i][1] and Z[i][4] == spreker for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
def Zs(i): return Z[i][0] - 0.1
BG = {}
def bg(n):
    if n not in BG:
        p = HIER / "afbeeldingen" / f"{n}.png"
        BG[n] = Image.open(p if p.exists() else HIER.parent / "proef-pop-short" / "afbeeldingen" / f"{n}.png").convert("RGB").resize((W, H))
    return BG[n]
Y = 1460
def hand(x, s, hoek, naam="cyborg", y=None):          # waar de rechterhand is (zelfde maten als pop_short.poppetje)
    s *= ps.C[naam].get("groot", 1.0); y = Y if y is None else y
    return x + 44 * s + 82 * s * math.sin(math.radians(hoek)), y - 175 * s + 82 * s * math.cos(math.radians(hoek))
T_PLUG, T_MOVED = kw(3, "plugged"), kw(3, "moved")
T_GIVE, T_HARD = kw(5, "give"), kw(5, "hard")
T_WAVE, T_LAPTOP = kw(8, "waves", -0.3), kw(10, "laptop")
SC = [dict(t=0, naam="koelkast"), dict(t=Zs(2), naam="werk"), dict(t=Zs(4), naam="vraag"), dict(t=Zs(5), naam="klas"),
      dict(t=Zs(7), naam="feit"), dict(t=Zs(8), naam="nacht")]
FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
NAAM = {"MOM": "MOM", "YOU": "YOU"}
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
    if Z[i][4] in NAAM:
        fn = font(FB, 30); n = NAAM[Z[i][4]]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 52, W / 2 + nb / 2 + 14, y - 12), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 50), n, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1].upper(), font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1].upper() + " ", font=f)
def koelkast(d, cx, onder, s=1.0):                        # getekende koelkast (in de robothand)
    w, h = 190 * s, 330 * s; x0, y0 = cx - w / 2, onder - h
    d.rounded_rectangle([(x0 * SS, y0 * SS), ((x0 + w) * SS, onder * SS)], int(22 * SS), fill=(168, 220, 200), outline=(45, 38, 40), width=5 * SS)
    d.line([(x0 * SS, (y0 + h * 0.38) * SS), ((x0 + w) * SS, (y0 + h * 0.38) * SS)], fill=(45, 38, 40), width=4 * SS)
    for yy in (y0 + h * 0.2, y0 + h * 0.6): d.rounded_rectangle([((x0 + 18 * s) * SS, (yy - 30 * s) * SS), ((x0 + 30 * s) * SS, (yy + 30 * s) * SS)], 6 * SS, fill=(90, 120, 110))
def rugzakken(d, cx, onder, n=10):                        # stapel rugzakken aan de arm
    kleuren = [(230, 80, 70), (70, 130, 220), (250, 200, 60), (90, 180, 110), (160, 120, 220)]
    for k in range(n):
        x = cx + (k % 2) * 40 - 20 + math.sin(k) * 10; y = onder - k * 52
        d.rounded_rectangle([((x - 55) * SS, (y - 50) * SS), ((x + 55) * SS, y * SS)], 16 * SS, fill=kleuren[k % 5], outline=(45, 38, 40), width=4 * SS)
SPR = {}
def zet_sprite(img, naam, cx, onder, schaal):            # plaatje met onderkant-midden op (cx, onder); geeft de bovenkant terug
    if (naam, schaal) not in SPR:
        s = Image.open(HIER / "afbeeldingen" / f"{naam}.png").convert("RGBA"); SPR[naam, schaal] = s.resize((int(s.width * schaal), int(s.height * schaal)), Image.LANCZOS)
    s = SPR[naam, schaal]; img.paste(s, (int(cx - s.width / 2), int(onder - s.height)), s); return onder - s.height
def popup(img, t):                                        # bericht op de laptop, groot in beeld
    a = min(1, (t - kw(10, "upgrade", -0.2)) / 0.3)
    if a <= 0: return
    laag = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.rounded_rectangle((150, 520, 930, 900), 34, fill=(20, 28, 48, int(240 * a)), outline=(80, 200, 255, int(255 * a)), width=6)
    d.text((540, 600), "UPGRADE AVAILABLE", font=font(FB, 62), fill=(80, 200, 255, int(255 * a)), anchor="mm")
    if t >= kw(10, "install", -0.1):
        d.text((540, 700), "Install the other arm?", font=font(FS, 50), fill=(255, 255, 255, int(255 * a)), anchor="mm")
        for x0, tx, kl in ((260, "YES", (60, 200, 110)), (580, "NO", (110, 110, 125))):
            d.rounded_rectangle((x0, 770, x0 + 240, 850), 20, fill=kl + (int(255 * a),)); d.text((x0 + 120, 810), tx, font=font(FB, 46), fill=(255, 255, 255, int(255 * a)), anchor="mm")
    img.paste(laag, (0, 0), laag)

def frame(t):
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); n = SC[k]["naam"]
    knip = lambda o: (t + o) % 3.4 < 0.13
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    if n == "koelkast":
        img = bg("keuken-leeg").copy()                     # koelkast is weg uit de hoek: hij zit in jouw hand
        Y2 = 1585                                             # dichter bij de camera: koelkast hangt duidelijk vóór de keuken
        ps.poppetje(d, "mom", 900, Y2, 1.9, t, kijk=-1.0, mond=luid(t, "MOM"), verbaasd=t < Z[1][0], boos=t >= Z[1][0],
                    gebaar="schrik" if t < Z[1][0] else ("wijslinks" if t < Z[1][0] + 0.9 else "heupen"), knipper=False)   # 24 nov: meer gebaren
        x = 300; hx, hy = hand(x, 2.1, 100, y=Y2)               # arm opzij gestrekt, koelkast op de handpalm (als een ober)
        zet_sprite(img, "sprite-koelkast", hx + 10 + math.sin(t * 9) * 3, hy + 6, 0.75)
        ps.poppetje(d, "cyborg", x, Y2, 2.1, t, kijk=0.6, verbaasd=True, gebaar="wijs", knipper=knip(0))
    elif n == "werk":
        img = bg("werkkamer").copy(); geplugd = t >= T_PLUG
        naam = "cyborg" if geplugd else "you"
        geb = "denk" if not geplugd else ("zwaai" if T_MOVED <= t <= T_MOVED + 1.2 else ("juich" if t > T_MOVED + 1.2 else "vast"))
        ps.poppetje(d, naam, 620, Y, 1.9, t, kijk=0.6 if geplugd else -0.6, verbaasd=t >= T_MOVED, gebaar=geb, knipper=knip(0.4))
        if not geplugd:                                    # de arm ligt nog op de vloer (nog niet aangesloten)
            d.rounded_rectangle([(700 * SS, 1440 * SS), (900 * SS, 1470 * SS)], 14 * SS, fill=(165, 175, 190), outline=(45, 38, 40), width=4 * SS)
            d.ellipse([(890 * SS, 1436 * SS), (930 * SS, 1474 * SS)], fill=(120, 130, 148), outline=(45, 38, 40), width=3 * SS)
    elif n == "vraag":
        img = bg("nacht").copy(); ps.poppetje(d, "cyborg", 540, Y, 2.3, t, kijk=0.0, gebaar="denk", knipper=knip(0.2))
    elif n == "klas":
        img = bg("klas").copy(); x = 560
        if t < Zs(6):                                      # high five: de klasgenoot schuift achteruit
            terug = ps.ease((t - T_HARD) / 0.5) if t > T_HARD else 0
            ps.poppetje(d, "kid1", 860 + 140 * terug, Y, 1.6, t, kijk=-0.9, gebaar="wijslinks" if t < T_HARD else "schrik", verbaasd=t > T_HARD)
            ps.poppetje(d, "cyborg", x, Y, 1.75, t, kijk=0.9, gebaar="wijs" if t >= T_GIVE else None, verbaasd=t > T_HARD, knipper=knip(0.1))
        else:
            ps.poppetje(d, "kid2", 230, Y, 1.55, t, kijk=0.9, gebaar="juich", verbaasd=True)
            ps.poppetje(d, "kid1", 880, Y, 1.6, t, kijk=-0.9, gebaar="klap", verbaasd=True)
            hx, hy = hand(x, 1.75, 165); onder = hy + 2
            for k2 in range(10):                              # 10 echte rugzakken op de hand gestapeld
                kl = ("rood", "blauw", "geel", "groen", "paars")[k2 % 5]
                onder = zet_sprite(img, f"sprite-rugzak-{kl}", hx + (k2 % 2) * 14 - 7 + math.sin(t * 3 + k2 * 0.5) * k2 * 1.5, onder + 24, 0.17)
            ps.poppetje(d, "cyborg", x, Y, 1.75, t, kijk=0.0, gebaar="haar", knipper=knip(0.1))
    elif n == "feit":
        img = bg("lab").copy()
    else:
        img = bg("kamer-nacht").copy(); zwaait = t >= T_WAVE
        ps.poppetje(d, "cyborg", 760, Y, 1.9, t, kijk=-0.4 if t < T_LAPTOP else -0.9, verbaasd=zwaait, mond=luid(t, "YOU"),
                    gebaar="zwaai" if zwaait and t < Z[9][0] else ("praat" if t < T_LAPTOP else "schrik"), knipper=knip(0.3) and not zwaait)
        if t >= T_LAPTOP:                                  # laptop gaat aan: scherm licht op
            d.rectangle([(414 * SS, 612 * SS), (628 * SS, 742 * SS)], fill=(80, 200, 255))
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    if n == "feit" and t >= kw(7, "some"):
        ImageDraw.Draw(img).text((40, 1860), "Source: BrainGate study, Nature (2012): robot arm moved by brain sensors", font=font(FS, 26), fill=(70, 70, 90))
    if n == "nacht": popup(img, t)
    ondertitel(img, t)
    return img

def geluid():                                             # echte CC0-geluiden (../geluiden), zacht onder de stem
    G = HIER.parent / "geluiden"; S2 = 48000; N = int((EIND + 0.5) * S2); uit = np.zeros(N, np.float32)
    def laad(nm):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(G / f"{nm}.mp3"), "-ac", "1", "-ar", str(S2), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).copy(); return x / (np.abs(x).max() + 1e-6)
    def zet(t, x, gain, duur=None):
        x = x[: int(duur * S2)] if duur else x; i = int(t * S2); j = min(N, i + len(x))
        if 0 <= i < N: uit[i:j] += x[: j - i] * gain
    zet(T_PLUG, laad("klik"), 0.6, 0.5)                    # stekker in de schouder
    zet(T_HARD, laad("boek"), 0.5, 0.8)                    # te harde high five
    zet(Zs(5), laad("klas"), 0.12, Zs(7) - Zs(5))          # geroezemoes in de klas
    zet(T_LAPTOP, laad("klik"), 0.5, 0.5)                  # laptop gaat aan
    sf.write(HIER / "sfx.wav", uit, S2)

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((270, 480)) for z in Z]
        pl = Image.new("RGB", (270 * 6, 480 * 2)); [pl.paste(im, (270 * (i % 6), 480 * (i // 6))) for i, im in enumerate(ims)]
        pl.save(HIER / "plaat.jpg", quality=85); print("plaat.jpg"); sys.exit()
    geluid()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"),
                          "-filter_complex", "[1:a]apad[v];[v][2:a]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]", "-map", "0:v", "-map", "[a]",
                          "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "short-cyborg.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("KLAAR short-cyborg.mp4", round(EIND, 1), "s")
