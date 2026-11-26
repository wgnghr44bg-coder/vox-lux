"""Proefscène (26 nov 2026, eigenaar: "personages als echte mensen iets laten doen, laten zitten ... met de camera bewegen zoals het voorbeeld").
Denny's 1993: iedereen zit in een bankje achter een tafel (onderlijf weg), Jensen tekent op een servet, jij eet pannenkoeken,
de serveerster schenkt koffie in; camera zoomt en schuift naar wie praat.  -> proef-scene.mp4"""
import math, subprocess, sys
from PIL import Image, ImageDraw
import maak_short as M
ps, W, H, FPS, INK = M.ps, M.W, M.H, M.FPS, M.INK
Z = M.Z
EIND = Z[3][1] + 0.8                                       # t/m "You've been here four hours."
T_SERV, T_SCHENK = Z[3][0] - 1.2, Z[3][0] - 0.2

def rhand(n, x, y, s, hoek):                               # rechterhand bij armhoek (0 = omlaag, 90 = opzij, <0 = naar het lijf/gezicht)
    S = s * ps.C[n].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S

TAFEL_Y = 1560                                             # bovenkant tafelblad; alles daaronder wordt door de tafel/bank bedekt
def bank_achter(d, x0, x1):                                # rugleuning van het bankje achter de personages
    d.rounded_rectangle((x0, 1100, x1, TAFEL_Y + 20), 30, fill=(205, 60, 60), outline=INK, width=5)
    for k in range(int((x1 - x0) / 90)): d.line((x0 + 45 + k * 90, 1130, x0 + 45 + k * 90, TAFEL_Y), fill=(175, 45, 45), width=4)
def tafel(d, x0, x1):                                      # tafelblad + voorste bankje (verbergt de benen: ze zitten)
    d.rectangle((x0, TAFEL_Y, x1, TAFEL_Y + 40), fill=(235, 230, 220), outline=INK, width=5)
    d.rectangle((x0 + 10, TAFEL_Y + 40, x1 - 10, TAFEL_Y + 58), fill=(180, 180, 185), outline=INK, width=3)
    d.rounded_rectangle((x0 - 10, TAFEL_Y + 58, x1 + 10, TAFEL_Y + 230), 26, fill=(205, 60, 60), outline=INK, width=5)
    for k in range(int((x1 - x0) / 90)): d.line((x0 + 45 + k * 90, TAFEL_Y + 80, x0 + 45 + k * 90, TAFEL_Y + 220), fill=(175, 45, 45), width=4)
def mok(d, x, kl=(250, 250, 250)):
    d.rectangle((x - 22, TAFEL_Y - 44, x + 22, TAFEL_Y + 2), fill=kl, outline=INK, width=4); d.arc((x + 12, TAFEL_Y - 36, x + 40, TAFEL_Y - 10), -90, 90, fill=INK, width=5)
def servet(img, d, t):                                     # servet plat op tafel, chip-schets komt er lijn voor lijn bij
    x0, y0 = 700, TAFEL_Y - 6; d.polygon([(x0 - 70, y0), (x0 + 60, y0 - 4), (x0 + 80, y0 + 30), (x0 - 60, y0 + 34)], fill=(252, 252, 248), outline=INK)
    n = min(6, int(max(0, t - 0.6) / 0.6))
    lijnen = [(-30, 6, 10, 6), (10, 6, 10, 26), (10, 26, -30, 26), (-30, 26, -30, 6), (-40, 12, -30, 12), (10, 20, 20, 20)]
    for a, b, c, e in lijnen[:n]: d.line((x0 + a, y0 + b, x0 + c, y0 + e), fill=(60, 80, 170), width=3)

CAM = [(0.0, 540, 1300, 1.0), (4.0, 560, 1250, 1.12), (Z[1][0], 640, 1200, 1.32), (Z[1][1] - 0.6, 600, 1200, 1.38),
       (Z[2][0], 260, 1250, 1.38), (Z[2][1], 300, 1250, 1.3), (Z[3][0], 480, 1300, 1.25), (EIND, 500, 1320, 1.3)]
def camera(t):                                             # (midden x, midden y, zoom), zacht tussen de sleutelmomenten
    for (t0, x0, y0, z0), (t1, x1, y1, z1) in zip(CAM, CAM[1:]):
        if t0 <= t <= t1:
            f = ps.ease((t - t0) / max(0.01, t1 - t0)); return x0 + (x1 - x0) * f, y0 + (y1 - y0) * f, z0 + (z1 - z0) * f
    return CAM[-1][1:]

def frame(t):
    img = M.bg("denny").copy(); d = ImageDraw.Draw(img)
    bank_achter(d, 480, 1080); bank_achter(d, 0, 330)
    nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)
    laag = Image.new("RGBA", (W * M.SS, H * M.SS), (0, 0, 0, 0)); dl = ImageDraw.Draw(laag)
    S = 1.6
    # Jensen tekent (arm schuin naar het servet, kleine krasbewegingen); bij zijn zin draait hij zich naar jou
    jen_arm = 55 + 8 * math.sin(t * 14) if nu == 0 else 95
    zit = [("you", 170, -0.0 if nu != 2 else 0.6, ("hoek", -16, 40 + 12 * math.sin(t * 5))),          # eet: prikt in de pannenkoeken
           ("jensen", 640, -0.8 if nu in (1, 2) else 0.0, ("hoek", -16, jen_arm)),
           ("chris", 830, -0.4, None), ("curtis", 1010, -0.5, ("hoek", -16, 40))]
    for n, x, kijk, geb in zit:
        emo = M.emotie(t, nu); y = TAFEL_Y + 140
        M.ps.poppetje(dl, n, x, y, S, t, kijk=kijk, mond=M.luid(t, n), knipper=(t + hash(n) % 7 * 0.4) % 3.4 < 0.13,
                      verbaasd=emo == "schrik", boos=emo == "verdriet", gebaar=geb)
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); d = ImageDraw.Draw(img)
    tafel(d, 0, 330); tafel(d, 480, 1080)
    servet(img, d, t); mok(d, 860); mok(d, 1010); mok(d, 560, (240, 240, 235))
    M.zet(img, "pannenkoek", 100, 270, TAFEL_Y + 4, naam="pannenkoeken")
    # vork in de hand van jou
    hx, hy = rhand("you", 170, TAFEL_Y + 140, S, 40 + 12 * math.sin(t * 5))
    d.line((hx, hy, hx + 30, hy + 30), fill=(150, 150, 160), width=6)
    if t >= T_SERV:                                        # serveerster in het gangpad, vóór de tafels; schenkt koffie in de mok
        l2 = Image.new("RGBA", (W * M.SS, H * M.SS), (0, 0, 0, 0)); d2 = ImageDraw.Draw(l2)
        f = ps.ease((t - T_SERV) / 1.0); xs = -150 + (405 - -150) * f; loop = (t - T_SERV) * 2.2 if f < 1 else None
        geb = "rennen" if loop is not None else ("hoek", -16, 105)
        M.ps.poppetje(d2, "serveerster", xs, 1900, 1.5, t, loop=loop, kijk=0.9, mond=M.luid(t, "serveerster"), gebaar=geb)
        l2 = l2.resize((W, H), Image.LANCZOS); img.paste(l2, (0, 0), l2); d = ImageDraw.Draw(img)
        if loop is None:
            kx, ky = rhand("serveerster", 405, 1900, 1.5, 105)
            schenk = T_SCHENK <= t < T_SCHENK + 1.6
            kan = M.sprite("koffiekan", 130).rotate(-40 if schenk else 0, expand=True, resample=Image.BICUBIC)
            px, py = int(kx - kan.width * 0.3), int(ky - kan.height * 0.75); img.paste(kan, (px, py), kan)
            if schenk: d.line((px + kan.width * 0.92, py + kan.height * 0.35, 560, TAFEL_Y - 44), fill=(110, 65, 35), width=7)
    # camera
    cx, cy, zm = camera(t); bw, bh = W / zm, H / zm
    x0 = min(max(0, cx - bw / 2), W - bw); y0 = min(max(0, cy - bh / 2), H - bh)
    img = img.crop((int(x0), int(y0), int(x0 + bw), int(y0 + bh))).resize((W, H), Image.LANCZOS)
    M.kop(img, "1993", None, 150, 84, ps.KL["geel"], ps.pop(t / 0.3)); M.ondertitel(img, t)
    return img

if __name__ == "__main__":
    if "--beeld" in sys.argv:
        for tt in (2.0, 7.0, 11.0, Z[3][0] + 0.5): frame(tt).resize((540, 960)).save(f"proef-{tt:.0f}.jpg", quality=85)
        sys.exit()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(M.HIER / "stem.wav"), "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "160k", "-t", f"{EIND:.2f}", str(M.HIER / "proef-scene.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
    p.stdin.close(); p.wait(); print("proef-scene.mp4", round(EIND, 1), "s")
