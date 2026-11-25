"""What If Everyone on Earth Got $1 Million Tonight? — lang, liggend 1920x1080 (eigenaar 24 nov). Proef = eerste 2 min.
Zelfde poppetjes/stijl als Swapped Lives (pop_short.py), met de lessen van AI Studio: meteen chaos, LATEN ZIEN (telefoon met
saldo, roze sportwagen, boot, paard, gamestoel, briefje op de schooldeur, kroon), rustige push-in per scène (geen effect bij
scènewissel), geluidseffecten. GEEN muziek. Gebruik: python maak_miljoen.py [--plaat]  -> miljoen.mp4"""
import colorsys, json, math, os, re, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import ImageFilter, Image, ImageDraw, ImageChops
HIER = Path(__file__).parent
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)

W, H, FPS, SS = 1920, 1080, 30, ps.SS
ps.C.update({                                            # extra mensen (andere kleuren dan de familie)
 "kassa": dict(broek=(60, 70, 60), shirt=(110, 170, 80), haar=(90, 60, 40), kapsel="staartjes", pet=(110, 170, 80), groot=1.05),
 "oma":   dict(broek=(90, 80, 100), shirt=(190, 110, 140), haar=(215, 215, 220), kapsel="grijs", bril=True, groot=0.98),
 "ster":  dict(broek=(40, 40, 50), shirt=(235, 190, 60), haar=(240, 210, 120), kapsel="paard", groot=1.0),
})
Z = json.load(open(HIER / "zinnen.json", encoding="utf-8"))
WO = []
for w in json.load(open(HIER / "woorden.json", encoding="utf-8")):
    if WO and WO[-1][0] == w[0] and w[1][:1] in ".," and w[1][1:2].isalnum(): WO[-1] = [w[0], WO[-1][1] + w[1], WO[-1][2], w[3]]
    else: WO.append(list(w))
import difflib
def _norm(w): return re.sub(r"[^a-z0-9]", "", w.lower())
def _script_woorden():
    """Per zin de woorden van het script met tijden: Whisper-tijden waar de woorden overeenkomen, anders verdeeld naar lengte."""
    uit = []
    for i, z in enumerate(Z):
        sw = z[2].replace('"', "").split(); ww = [w for w in WO if w[0] == i]
        if not ww: ww = [[i, z[2], z[0], z[1]]]
        t0s, t1s = [None] * len(sw), [None] * len(sw)
        sm = difflib.SequenceMatcher(None, [_norm(w) for w in sw], [_norm(w[1]) for w in ww], autojunk=False)
        for a, b, n in sm.get_matching_blocks():
            for k in range(n): t0s[a + k], t1s[a + k] = ww[b + k][2], ww[b + k][3]
        begin, eind = ww[0][2], ww[-1][3]
        k = 0
        while k < len(sw):                               # gaten opvullen: tussen vorige eind en volgende begin, naar woordlengte
            if t0s[k] is not None: k += 1; continue
            j = k
            while j < len(sw) and t0s[j] is None: j += 1
            a = t1s[k - 1] if k > 0 else begin; b = t0s[j] if j < len(sw) else eind
            if b <= a: b = a + 0.25 * (j - k)
            lens = [max(1, len(_norm(w))) for w in sw[k:j]]; tot = sum(lens); t = a
            for q in range(k, j):
                d = (b - a) * lens[q - k] / tot; t0s[q], t1s[q] = t, t + d; t += d
            k = j
        uit += [[i, w, round(t0s[q], 2), round(t1s[q], 2)] for q, w in enumerate(sw)]
    return uit
SW = _script_woorden()
EIND = Z[-1][1] + 3.0                                  # even laten hangen na "Oh no." (en net boven 8 min)
AUD, SR = sf.read(HIER / "stem.wav", dtype="float32")
if AUD.ndim > 1: AUD = AUD.mean(axis=1)
LAYOUT = set()                                          # layoutcheck (vroeg, zodat kw() erin kan melden)
def kw(zin, woord, na=0.0):                              # 25 nov: eerst de scriptwoorden (goede spelling, Whisper schrijft "un -plugs"/"$1")
    for bron in (SW, WO):
        for i, w, t0, t1 in bron:
            if i == zin and re.sub(r"[^\w$%]", "", w.lower()).startswith(woord.lower()): return t0 + na
    print("LET OP: niet gevonden", zin, woord); LAYOUT.add(f"woord '{woord}' niet gevonden in zin {zin}: tijd klopt niet"); return Z[zin][0] + na
NAAMLABELS = False                                       # eigenaar 25 nov: "alle tekens bij de characters mogen ook weg"
LIJF = {"YOU": "you", "DAD": "dad", "MOM": "mom", "SIS": "sis", "BOSS": "boss", "TEACH": "teach"}
NAAM = {"YOU": "YOU", "DAD": "DAD", "MOM": "MOM", "SIS": "SISTER", "TEACH": "TEACHER", "BOSS": "BOSS"}
def luid(t, lijf):
    if not any(Z[i][0] <= t <= Z[i][1] and LIJF.get(Z[i][4]) == lijf for i in range(len(Z))): return 0.0
    s = AUD[int(t * SR): int((t + 1 / FPS) * SR)]
    return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0

# ---------- losse voorwerpen (ComfyUI, witte achtergrond weg) ----------
def los(im, tol=30):
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox())
SPR = {}
def sprite(n, hoogte, spiegel=False, tint=None):
    k = (n, hoogte, spiegel, tint)
    if k not in SPR:
        bron = Image.open(HIER / "afbeeldingen" / f"{n}.png").convert("RGB")
        if n == "boot":                                  # antennes + koepeltje bovenop leken een mannetje -> weg (achtergrondkleur)
            ImageDraw.Draw(bron).rectangle((415, 55, 565, 226), fill=bron.getpixel((5, 5)))
        im = los(bron)
        if tint is not None:
            px = np.array(im).astype(float) / 255; rgb = px[..., :3]
            hsv = np.array([colorsys.rgb_to_hsv(*c) for c in rgb.reshape(-1, 3)]).reshape(rgb.shape)
            m = hsv[..., 1] > 0.35; hsv[..., 0] = np.where(m, (hsv[..., 0] + tint) % 1, hsv[..., 0])
            rgb = np.array([colorsys.hsv_to_rgb(*c) for c in hsv.reshape(-1, 3)]).reshape(rgb.shape)
            im = Image.fromarray((np.dstack([rgb, px[..., 3:]]) * 255).astype(np.uint8), "RGBA")
        im = im.resize((int(im.width * hoogte / im.height), hoogte), Image.LANCZOS)
        SPR[k] = im.transpose(Image.FLIP_LEFT_RIGHT) if spiegel else im
    return SPR[k]
sys.path.insert(0, str(HIER.parents[2] / "tools"))
from scenewachter import Scenewachter
WACHT = Scenewachter(HIER.parent / "achtergronden.json")      # elk voorwerp: waar staat het op? (anker, muur, botsing, gezicht)
def zet(img, n, hoogte, x, voet, op=None, punt=None, voor=False, **kw_):
    s = sprite(n, hoogte, **kw_)
    dx, dy = WACHT.plaats(n, (x - s.width / 2, voet - s.height, x + s.width / 2, voet), op=op, punt=punt, voor=voor)
    img.paste(s, (int(x + dx - s.width / 2), int(voet + dy - s.height)), s)

# ---------- scènes ----------
def _van_tot(van, tot):                                  # zinnummers van zin die met 'van' begint t/m 'tot'
    i0 = next(i for i, z in enumerate(Z) if z[2].startswith(van)); i1 = next(i for i, z in enumerate(Z) if z[2].startswith(tot))
    return range(i0, i1 + 1)
SCENE = {next(i for i, z in enumerate(Z) if z[2].startswith("You sit alone")): "klas"}
SCENE.update({i: "winkel" for i in _van_tot("And the stores are running", "Yes. The toilet paper")})     # lege schappen
SCENE.update({i: "klas" for i in _van_tot("Day twenty-five", "Then she hands out homework")})       # juf terug in de klas
BGNAAM = {"slaapkamer-jij": "kamer-jij", "school": "schooldeur", "tv": "woonkamer", "nacht": "keuken-nacht"}
blokken = []
for i, z in enumerate(Z):
    sc = SCENE.get(i, z[3]); dag = z[2].startswith("Day ")
    if not blokken or blokken[-1][0] != sc or dag: blokken.append([sc, i, i])
    else: blokken[-1][2] = i
def zi(tekst):                                           # nummer van de zin die met deze tekst begint
    return next(i for i, z in enumerate(Z) if z[2].startswith(tekst))
SC = []
for naam, a, b in blokken:
    sp = {Z[i][4] for i in range(a, b + 1)}; T = " ".join(Z[i][2] for i in range(a, b + 1)); pop = []; kop = []; extra = {}
    if naam == "slaapkamer-jij" and "Check your phones" in T:
        pop = [dict(n="you", x=620, s=1.9, geb="vast")]; extra["telefoon"] = True
    elif naam == "slaapkamer-jij":
        pop = [dict(n="you", x=1180, s=1.8)]; extra["stoel"] = True
        if "every game" in T: extra["games"] = Z[zi("You buy every")][0]
        if "SIS" in sp: i0 = zi("I bought a horse"); pop.append(dict(n="sis", x=560, s=1.8, loop=(Z[i0][0] - 1.0, Z[i0][0] + 0.2, -150, 560)))
    elif naam == "keuken" and "run downstairs" in T:
        i0 = a; pop = [dict(n="dad", x=820, s=1.55, geb="vast"), dict(n="mom", x=1120, s=1.55, geb="vast"), dict(n="sis", x=1400, s=1.55, geb="vast"),
                       dict(n="you", x=480, s=1.55, loop=(Z[i0][0], Z[i0][0] + 1.2, -150, 480))]
        kop.append((kw(zi("It's on the news"), "every"), "EVERY PERSON ON EARTH", 960, 150, 84, "wit"))
        kop.append((kw(zi("It's on the news"), "one"), "$1,000,000 EACH", 960, 265, 104, "groen"))
    elif naam == "keuken" and "internet goes down" in T:
        pop = [dict(n="dad", x=700, s=1.6, geb="vast"), dict(n="sis", x=1250, s=1.6, geb="vast")]
        i0 = zi("Day five"); kop += [(Z[i0][0], "DAY 5", 185, 90, 70, "geel"), (kw(i0, "internet"), "NO INTERNET", 960, 170, 96, "rood")]
        i1 = zi("Dad calls a repair"); extra["bel"] = [(kw(i1, "laughs"), "HA HA HA"), (kw(i1, "hangs", 0.3), "*click*")]
        i2 = zi("Dad calls ten"); kop.append((kw(i2, "10"), "10 CALLS · 10 x NO", 960, 170, 80, "rood"))
        i3 = zi("Dad unplugs"); extra["router"] = (kw(i3, "unplugs"), kw(i3, "plugs"), kw(i3, "again"))
        kop.append((kw(i3, "TV"), "TV: BROKEN", 960, 170, 96, "rood")); extra["kapot"] = kw(i3, "TV", -0.1)
    elif naam == "keuken" and "family meeting" in T:
        pop = [dict(n="dad", x=1000, s=1.55), dict(n="mom", x=1300, s=1.55), dict(n="you", x=1530, s=1.55), dict(n="sis", x=1740, s=1.55)]
        i0 = zi("Day ten"); i1 = zi("The boat was"); i2 = zi("And milk is now")
        kop.append((Z[i0][0], "DAY 10", 185, 90, 70, "geel"))
        extra["sheet"] = [(kw(i0, "has", -0.1), "SPREADSHEET", ""), (kw(i1, "boat"), "Boat", "$200,000"), (kw(i1, "horse"), "Horse", "$50,000"),
                          (kw(i1, "gaming"), "Gaming chair", "???"), (kw(i2, "milk"), "Milk (1 carton)", "$500")]
    elif naam == "keuken" and "toothache" in T:
        pop = [dict(n="dad", x=900, s=1.6), dict(n="mom", x=1300, s=1.6)]
        i0 = zi("Day sixteen"); kop.append((Z[i0][0], "DAY 16", 185, 90, 70, "geel"))
        i1 = zi("Then Grandma shows up"); pop.append(dict(n="oma", x=470, s=1.6, loop=(kw(i1, "grandma", -0.3), kw(i1, "grandma", 1.3), -150, 470)))
        i2 = zi("Grandma ties"); i3 = zi("The door slams"); extra["tand"] = (Z[i0][0], kw(i2, "tooth"), kw(i3, "slams", -0.05))
        sl = kw(i3, "slams", -0.05)
        extra["oma_pad"] = [(kw(i2, "grandma"), 470), (kw(i2, "tooth"), 655), (kw(i2, "other"), 655), (kw(i2, "door"), 458),
                            (sl + 0.7, 458), (sl + 2.6, 1600)]
        extra["oma_hand"] = (kw(i2, "tooth"), kw(i2, "other"))
        i4 = zi("Ten thousand dollars now"); kop.append((kw(i4, "three", -0.1), "$10,000 = 3 APPLES", 960, 170, 90, "rood"))
        i5 = zi("Grandma wants"); kop.append((kw(i5, "loaf", -0.1), "PRICE: 1 LOAF OF BREAD", 960, 170, 84, "geel")); extra["broodje"] = kw(i5, "loaf", -0.1)
    elif naam == "keuken" and "You trade" in T:
        pop = [dict(n="dad", x=700, s=1.6), dict(n="sis", x=1250, s=1.6)]
        i0 = zi("Nobody pays with money")
        kop += [(kw(i0, "bread"), "BREAD = PIPE FIX", 960, 140, 74, "wit"), (kw(i0, "horse"), "HORSE RIDES = EGGS", 960, 235, 74, "wit"),
                (kw(i0, "boat", -0.1), "BOAT = 6 CHICKENS", 960, 330, 80, "geel")]
        extra["kippen"] = kw(i0, "chickens", -0.2)
    elif naam == "keuken" and "Day thirty" in T:
        pop = [dict(n="dad", x=330, s=1.5, y=1000), dict(n="mom", x=600, s=1.5, y=1000), dict(n="you", x=870, s=1.5, y=1000), dict(n="sis", x=1130, s=1.5, y=1000)]
        extra["tafelx"] = (170, 1290)
        i_h = next(i for i, z in enumerate(Z) if "still have the horse" in z[2]); extra["raampaard"] = kw(i_h, "horse", -0.3)
        i_b = next(i for i, z in enumerate(Z) if "People make bread" in z[2]); extra["brood_t"] = kw(i_b, "people", -0.1)
        i0 = zi("Day thirty"); kop += [(Z[i0][0], "DAY 30", 185, 90, 70, "geel"), (kw(i0, "boat"), "BOAT: GONE", 960, 150, 76, "rood"),
                                       (kw(i0, "firewood"), "GAMING CHAIR: FIREWOOD", 960, 245, 76, "rood")]
        extra["keukentafel"] = True; extra["kippen"] = Z[i0][0]; extra["hout"] = Z[i0][0] + 0.5
        i1 = zi("Then, at midnight"); extra["middernacht"] = kw(i1, "midnight", -0.2); i3 = zi("Your phone buzzes one")
        extra["slot"] = (kw(i1, "phone", -0.2), Z[i1 + 1][0], Z[i3][0], kw(i3, "congratulations", -0.1))
    elif naam == "keuken":
        pop = [dict(n="dad", x=820, s=1.55), dict(n="mom", x=1120, s=1.55)]
    elif naam == "straat" and "garbage truck" in T:
        pop = [dict(n="dad", x=1000, s=1.55), dict(n="mom", x=1230, s=1.55), dict(n="you", x=1440, s=1.55)]
        i0 = zi("Day three"); kop.append((Z[i0][0], "DAY 3", 185, 90, 70, "geel")); extra["vuil"] = kw(i0, "garbage", -0.1); extra["vol"] = True
        i1 = zi("Your street now"); kop.append((kw(i1, "mountain"), "7 CARS · 1 BOAT · 1 HORSE · 1 MOUNTAIN OF TRASH", 960, 170, 56, "wit"))
        extra["kijk"] = kw(zi("Everybody looks"), "looks")
        i2 = zi("By the end of the day, the trash"); extra["wasbeer"] = min(kw(i2, "raccoons", -0.1), next((kw(i, "family", -0.2) for i, z in enumerate(Z) if "family of raccoons" in z[2]), 1e9))
        kop.append((kw(i2, "raccoons"), "NEW NEIGHBORS: RACCOONS", 960, 170, 64, "geel"))
    elif naam == "straat" and "out of gas" in T:
        pop = [dict(n="you", x=1350, s=1.55), dict(n="sis", x=1560, s=1.55), dict(n="oma", x=1760, s=1.55)]
        i0 = zi("Day twenty."); kop += [(Z[i0][0], "DAY 20", 185, 90, 70, "geel"), (kw(i0, "gas"), "OUT OF GAS", 400, 760, 64, "rood")]
        i_p = next((i for i, z in enumerate(Z) if "talking to each other" in z[2]), None)
        if i_p is not None: extra["praten"] = kw(i_p, "talking", -0.2)
        extra["vol"] = True
        extra["lopers"] = kw(zi("The whole street is full"), "walks", -0.6)
        i1 = zi("Turns out"); kop += [(kw(i1, "pipes", -0.2), "NEIGHBOR: FIXES PIPES", 960, 150, 66, "wit"), (kw(i1, "bake", -0.2), "GRANDMA: BAKES BREAD", 960, 235, 66, "wit"),
                                    (kw(i1, "power", -0.3), "NUMBER 12: FIXES THE POWER", 960, 320, 66, "wit")]
        i2 = zi("Your sister can ride"); kop.append((kw(i2, "ride", -0.1), "SISTER: RIDES HORSES", 960, 405, 66, "geel")); extra["paard_straat"] = kw(i2, "horse", -0.3)
    elif naam == "straat":
        pop = [dict(n="dad", x=1480, s=1.55), dict(n="mom", x=1730, s=1.55)] if "DAD" in sp else []
        extra["auto"] = kw(zi("Day one"), "pink", -0.6) if "Day one" in T else None
        extra["show"] = "Day one" in T                                     # 'looks like a car show': al auto's op de opritten
        if "across the street" in T: extra["drie"] = kw(zi("The guy across"), "three", -0.2)
        if "boat" in T: extra["boot"] = kw(zi("Dad orders"), "boat", -0.1)
        if "Day one" in T: kop.append((Z[a][0], "DAY 1", 185, 90, 70, "geel"))
        if "across the street" in T: kop.append((kw(zi("The guy across"), "three"), "x3", 1080, 520, 110, "rood"))
    elif naam == "tuin":
        pop = [dict(n="mom", x=380, s=1.7), dict(n="sis", x=640, s=1.7)]; extra["paard"] = True
        i0 = zi("Mister Pancake eats"); extra["eet"] = [kw(i0, "flowers"), kw(i0, "fence"), kw(i0, "doormat")]
    elif naam == "school":
        pop = [dict(n="you", x=1450, s=1.7)]; extra["briefje"] = kw(zi("There's a note"), "note", -0.1)
        kop.append((Z[a][0], "DAY 2", 185, 90, 70, "geel"))
    elif naam == "klas" and "Your teacher comes back" in T:
        pop = [dict(n="teach", x=1300, s=1.6, loop=(Z[a][0] + 0.3, Z[a][0] + 1.8, 2100, 1300)), dict(n="you", x=640, s=1.6, y=1010)]
        i0 = zi("Day twenty-five"); kop.append((Z[i0][0], "DAY 25", 185, 90, 70, "geel")); extra["zon"] = kw(i0, "sunburned", -0.2)
        i4 = zi("Then she hands out"); kop.append((kw(i4, "homework"), "HOMEWORK", 960, 170, 96, "rood")); extra["huiswerk"] = kw(i4, "homework", -0.1)
        i1 = zi("I spent it on"); extra["kokos"] = kw(i1, "coconut", -0.2); kop.append((kw(i1, "coconut"), "$1,000,000 COCONUT", 960, 170, 84, "geel"))
    elif naam == "klas":
        pop = [dict(n="you", x=960, s=1.6, y=1010)]; i0 = zi("You sit alone"); extra["thuis"] = kw(i0, "home", -0.2)
    elif naam == "tv":
        pop = [dict(n="you", x=1470, s=1.6), dict(n="sis", x=1685, s=1.6)]
        i0 = zi("Day four"); kop.append((Z[i0][0], "DAY 4", 185, 90, 70, "geel")); extra["tv"] = kw(i0, "TV", -0.2)
    elif naam == "winkel" and "Mom goes to the store" in T:
        pop = [dict(n="mom", x=620, s=1.7), dict(n="kassa", x=1500, s=1.7)]
        i0 = zi("Day seven"); i1 = zi("By lunch"); i2 = zi("The cashier says"); extra["kassabel"] = kw(i2, "number", -0.2)
        kop.append((Z[i0][0], "DAY 7", 185, 90, 70, "geel"))
        extra["prijs"] = [(kw(i0, "milk", -0.1), "$50"), (kw(i1, "lunch", 0.3), "$100"), (kw(i1, "dinner", 0.3), "$200"), (kw(i1, "price"), "$350")]
        extra["banaan"] = (kw(zi("I'll just take"), "banana", -0.2), kw(i2, "back", 0.4), kw(i2, "number"))
    elif naam == "winkel":
        pop = [dict(n="mom", x=1300, s=1.7)]
        i0 = zi("The shelves get"); kop += [(kw(i0, "snacks"), "SNACKS: SOLD OUT", 700, 160, 66, "rood"), (kw(i0, "bread"), "BREAD: SOLD OUT", 700, 255, 66, "rood"),
                                          (kw(i0, "toilet"), "TOILET PAPER: SOLD OUT", 700, 350, 66, "rood")]
        extra["leeg"] = [kw(i0, "snacks", -0.4), kw(i0, "bread", -0.4), kw(i0, "toilet", -0.4)]
    elif naam == "restaurant":
        pop = [dict(n="dad", x=560, s=1.55), dict(n="mom", x=820, s=1.55), dict(n="you", x=1080, s=1.55), dict(n="sis", x=1320, s=1.55)]
        i0 = zi("Day eight"); kop.append((Z[i0][0], "DAY 8", 185, 90, 70, "geel"))
        i1 = zi("Nobody answers"); i2 = zi("Forty minutes"); extra["minibord"] = kw(zi("Day eight"), "tiny", -0.2)
        extra["muts"] = kw(i1, "puts", -0.1); extra["rook"] = kw(i2, "smoke", -0.2); extra["cereal"] = kw(i2, "cereal", -0.1)
        kop.append((kw(i2, "Forty"), "40 MINUTES LATER", 960, 170, 80, "geel"))
        i3 = zi("On the way out"); kop.append((kw(i3, "tip"), "TIP: $1,000,000", 960, 170, 84, "groen")); extra["fooi"] = kw(i3, "tip", -0.1)
    elif naam == "feit":
        pop = [dict(n="you", x=360, s=1.5)]
        i0 = zi("In Zimbabwe"); i1 = zi("In 2009")
        kop += [(kw(i0, "Zimbabwe"), "ZIMBABWE", 1250, 150, 96, "geel"), (kw(i0, "prices"), "PRICES UP EVERY DAY", 1250, 260, 64, "rood")]
        extra["biljet"] = kw(i1, "printed", -0.1)
    elif naam == "nacht":
        pop = [dict(n="dad", x=560, s=1.5, y=1000), dict(n="mom", x=850, s=1.5, y=1000), dict(n="you", x=1140, s=1.5, y=1000), dict(n="sis", x=1420, s=1.5, y=1000)]
        i0 = zi("Day fourteen"); kop.append((Z[i0][0], "DAY 14", 185, 90, 70, "geel")); extra["donker"] = kw(i0, "lights", 0.2)
        extra["keukentafel"] = True; i2 = zi("So you play a board"); extra["kaars"] = kw(i2, "candlelight", -0.3); extra["spel"] = kw(i2, "board", -0.2)
        i1 = zi("The people who run"); kop += [(kw(i1, "island"), "ISLAND", 560, 200, 70, "wit"), (kw(i1, "yacht"), "YACHT", 960, 200, 70, "wit"), (kw(i1, "Hawaii"), "HAWAII", 1360, 200, 70, "wit")]
        extra["accu"] = kw(zi("I can't charge"), "charge", -0.2)
    elif naam == "kantoor":
        pop = [dict(n="dad", x=700, s=1.7, loop=(Z[a][0], Z[a][0] + 1.6, -150, 700)), dict(n="boss", x=1250, s=1.7)]; extra["kroon"] = "No crown" not in T
        if "Dad sits down at his desk" in T:
            i5 = zi("Dad sits down at his desk"); kop.append((kw(i5, "240", -0.1), "240 EMAILS!", 960, 170, 90, "groen")); extra["inbox"] = kw(i5, "240", -0.1)
        if "Nobody wants to work" in T:
            i0 = zi("And that's the problem")
            kop += [(kw(i0, "bus"), "BUS DRIVER: QUIT", 560, 90, 62, "rood"), (kw(i0, "cook"), "COOK: QUIT", 560, 170, 62, "rood"),
                    (kw(i0, "internet", -0.3), "INTERNET GUY: QUIT", 560, 250, 62, "rood")]
    SC.append(dict(t=0.0 if not SC else Z[a][0] - 0.1, eind=Z[b][1] + 0.4, naam=naam, bg=BGNAAM.get(naam, naam), pop=pop, kop=kop, a=a, b=b, **extra))
for k in range(len(SC) - 1): SC[k]["eind"] = SC[k + 1]["t"]
SC[-1]["eind"] = EIND

SCHRIK = ("fifty dollars", "raised the prices", "raised them again", "This time, only one person", "Round two starts",
          "Congratulations", "For milk", "By lunch", "two hundred", "The price tags change", "smoke alarm", "Pitch black",
          "the TV is broken", "Not the toilet paper", "eats Mom's flowers", "Then the fence", "Then the doormat", "How much is one banana")
BLIJ = ("You're rich", "Day one is amazing", "It was a really good coconut", "Best deal I ever made", "This is the best restaurant",
        "I'm a millionaire", "A millionaire did")
def _start(i, frase):                                    # tijd van het eerste woord van 'frase' in zin i
    w0 = re.sub(r"[^a-z0-9]", "", frase.split()[0].lower())
    for j, w, t0, t1 in SW:
        if j == i and re.sub(r"[^a-z0-9]", "", w.lower()) == w0: return t0
    return Z[i][0]
def emotie(t, nu_i):
    """'schrik' | 'verdriet' | 'blij' | None: de laatst begonnen frase uit de lijsten in de huidige zin."""
    if nu_i is None: return None
    tekst = Z[nu_i][2]; best = (None, -1)
    for soort, lijst in (("schrik", SCHRIK), ("verdriet", VERDRIET), ("blij", BLIJ)):
        for f_ in lijst:
            if f_.lower() in tekst.lower():
                st = _start(nu_i, f_)
                if st - 0.15 <= t and st > best[1]: best = (soort, st)
    return best[0]
VERDRIET = ("A little less happy", "Nobody finds it funny", "I can't charge my phone", "very, very slowly", "The shelves get emptier", "Then the bread", "Yes. The toilet paper",
            "We had a million dollars", "He laughs", "Dad calls ten more",
            "poorer than before", "The boat is gone")          # gezicht past bij de zin: teleurgesteld/verdrietig (wenkbrauwen)
VERBAASD = ("toothache", "balloon", "dentist", "Twenty thousand", "One million dollars?", "blink", "Oh", "screams", "Nobody", "three", "boat", "can't even swim", "horse", "Gone to Hawaii", "crown")
BLIJ = ("millionaire", "Best. Day", "rich")
NACTIE = {"The cashier shrugs": ("kassa", "schouders"), "Then she hands out homework": ("teach", "wijslinks"),
          "Day twenty. The car": None}
# 25 nov (eigenaar: "elke keer dat er iets gezegd wordt zwaaien ze met de armen, dat hoeft toch niet"): gewoon praten = GEEN
# armgebaar. Alleen een gebaar als de zin erom vraagt (juichen, schrikken, 'wat?!', handen in de zij ...).
ACTIE = {"Best. Day. Ever": "juich", "You can't even swim": "heupen", "Who sold a seven": "armen-open",
         "A millionaire did": "juich", "I quit": "zwaai", "But who runs": "schouders", "One million dollars?": "schrik"}

FB, FS, KL, font = ps.FB, ps.FS, ps.KL, ps.font
BG = {}
def bg(n):
    if n not in BG:
        p = HIER / "afbeeldingen" / f"{n}.png"
        if not p.exists(): p = HIER.parent / "video-swap" / "afbeeldingen" / f"{n}.png"
        BG[n] = Image.open(p).convert("RGB").resize((W, H))
        if n == "straat":                                # AI-vlek (half weggepoetst raam) op de bovenverdieping van het linkerhuis
            d_ = ImageDraw.Draw(BG[n]); d_.rectangle((588, 470, 740, 552), fill=(245, 230, 205))
            d_.rectangle((612, 478, 716, 546), fill=(255, 255, 255)); d_.rectangle((618, 484, 710, 540), fill=(150, 205, 240))
            d_.line((664, 484, 664, 540), fill=(255, 255, 255), width=6); d_.line((618, 512, 710, 512), fill=(255, 255, 255), width=6)
    return BG[n]
LAYOUT = globals().get("LAYOUT", set())                # layoutcheck: tekst buiten beeld/kader -> melding bij --plaat en render
def kop(img, s, x, y, m, kl, sch):
    f = font(FB, max(8, int(m * sch))); d = ImageDraw.Draw(img); sw = max(4, int(m * sch) // 11)
    b = d.textbbox((0, 0), s, font=f, stroke_width=sw); w, h = b[2] - b[0], b[3] - b[1]
    if sch >= 1 and (x - w / 2 < 20 or x + w / 2 > W - 20 or y - h / 2 < 10): LAYOUT.add(f"kop '{s}' valt (deels) buiten beeld")
    d.text((x - w / 2, y - h / 2 + 5), s, font=f, fill=(0, 0, 0), stroke_width=sw, stroke_fill=(0, 0, 0))
    d.text((x - w / 2, y - h / 2), s, font=f, fill=kl, stroke_width=sw, stroke_fill=(20, 20, 30))
def ondertitel(img, t):
    zi_ = [i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.25]
    if not zi_: return
    i = zi_[-1]; ws = [w for w in SW if w[0] == i]
    if not ws: return
    f = font(FS, 56); d = ImageDraw.Draw(img); stukken, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= 6 or w[1][-1:] in ".?!,": stukken.append(cur); cur = []
    if cur: stukken.append(cur)
    stuk = next((s for s in stukken if t <= s[-1][3] + 0.1), stukken[-1])
    br = sum(d.textlength(w[1] + " ", font=f) for w in stuk); x = W / 2 - br / 2; y = 985
    if NAAMLABELS and Z[i][4] in NAAM and not NAAM_GETOOND:
        fn = font(FB, 30); n = NAAM[Z[i][4]]; nb = d.textlength(n, font=fn)
        d.rounded_rectangle((W / 2 - nb / 2 - 14, y - 50, W / 2 + nb / 2 + 14, y - 10), 10, fill=(120, 80, 220)); d.text((W / 2 - nb / 2, y - 48), n, font=fn, fill=(255, 255, 255))
    for w in stuk:
        d.text((x, y), w[1], font=f, fill=KL["geel"] if w[2] <= t <= w[3] + 0.05 else (255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
        x += d.textlength(w[1] + " ", font=f)

T_SALDO = kw(zi("One million dollars. In"), "million", -0.3)
def telefoon(img, t):                                   # grote telefoon met bank-app: saldo springt van $12.00 naar $1,000,000.00
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 1100, 110, 1600, 900
    tril = math.sin(t * 60) * 6 if t < T_SALDO else 0
    x0 += tril; x1 += tril
    d.rounded_rectangle((x0, y0, x1, y1), 48, fill=(25, 25, 32), outline=(10, 10, 14), width=6)
    d.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), 34, fill=(245, 247, 250))
    d.rounded_rectangle(((x0 + x1) / 2 - 50, y0 + 30, (x0 + x1) / 2 + 50, y0 + 52), 11, fill=(25, 25, 32))
    d.rectangle((x0 + 18, y0 + 90, x1 - 18, y0 + 190), fill=(40, 110, 220))
    d.text((x0 + 50, y0 + 115), "MY BANK", font=font(FB, 44), fill=(255, 255, 255))
    d.text((x0 + 50, y0 + 240), "Balance", font=font(FS, 38), fill=(120, 120, 130))
    if t < Z[0][1] + 0.2: s, kl, m = "$1,000,000.00", (30, 170, 80), 54       # openingsroep: je ziet waarom hij roept
    elif t < T_SALDO: s, kl, m = "$12.00", (40, 40, 50), 84
    else: s, kl, m = "$1,000,000.00", (30, 170, 80), int(54 * ps.pop((t - T_SALDO) / 0.35))
    d.text((x0 + 50, y0 + 300), s, font=font(FB, m), fill=kl)
    for k, (r, v) in enumerate((("Fries coupon", "1x"), ("Deposit", "+$999,988.00" if t >= T_SALDO else ""))):
        yy = y0 + 470 + k * 110; d.line((x0 + 50, yy - 20, x1 - 50, yy - 20), fill=(220, 220, 228), width=3)
        d.text((x0 + 50, yy), r, font=font(FS, 30), fill=(60, 60, 70)); d.text((x1 - 60 - d.textlength(v, font=font(FB, 30)), yy), v, font=font(FB, 30), fill=(30, 170, 80))
    if t < T_SALDO and int(t * 4) % 2 == 0:
        d.text((x0 + 60, y1 - 120), "BZZZ", font=font(FB, 56), fill=(220, 60, 60))

def briefje(img, t, t0):
    if t < t0: return
    sch = ps.pop((t - t0) / 0.3); w, h = int(360 * sch), int(250 * sch); cx, cy = 960, 470
    d = ImageDraw.Draw(img); d.rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=(255, 250, 215), outline=(60, 50, 40), width=4)
    d.ellipse((cx - 10, cy - h / 2 - 6, cx + 10, cy - h / 2 + 14), fill=(220, 60, 60))
    for k, r in enumerate(("GONE TO HAWAII.", "FOREVER.")):
        fz = int(44 * sch)
        while fz > 8 and d.textlength(r, font=font(FB, fz)) > w - 40: fz -= 2
        f = font(FB, max(8, fz)); tw = d.textlength(r, font=f); d.text((cx - tw / 2, cy - 60 * sch + k * 70 * sch), r, font=f, fill=(40, 40, 60))

def kroon(img, x, y, s):
    d = ImageDraw.Draw(img); w = 70 * s; h = 50 * s; yb = y + 6 * s
    pts = [(x - w / 2, yb), (x - w / 2, yb - h), (x - w / 4, yb - h * 0.55), (x, yb - h), (x + w / 4, yb - h * 0.55), (x + w / 2, yb - h), (x + w / 2, yb)]
    d.polygon(pts, fill=(255, 205, 60), outline=(40, 35, 40)); d.line(pts + [pts[0]], fill=(40, 35, 40), width=int(4 * s))
    for px in (x - w / 2, x, x + w / 2): d.ellipse((px - 7 * s, yb - h - 7 * s, px + 7 * s, yb - h + 7 * s), fill=(230, 60, 80), outline=(40, 35, 40), width=2)

def hand(n, x, y, s, hoek=70):                          # rechterhand bij gebaar 'vast' (70) of 'telefoon' (-32), zelfde maten als poppetje
    S = s * ps.C[n].get("groot", 1.0); heup = y - 78 * S - 14 * S; sch = heup - 105 * S + 22 * S
    return x + 44 * S + math.sin(math.radians(hoek)) * 82 * S, sch + math.cos(math.radians(hoek)) * 82 * S, S
def telefoontje(img, hx, hy, S, t):
    d = ImageDraw.Draw(img); d.rounded_rectangle((hx - 13 * S, hy - 36 * S, hx + 13 * S, hy + 6 * S), int(5 * S), fill=(30, 30, 36), outline=(10, 10, 12), width=2)
    d.rounded_rectangle((hx - 10 * S, hy - 32 * S, hx + 10 * S, hy + 2 * S), int(3 * S), fill=(150, 220, 255) if int(t * 3) % 2 else (120, 235, 160))
def games(img, t, t0):                                  # stapel game-doosjes die snel groeit, met een controller bovenop
    d = ImageDraw.Draw(img); n = int(min(14, max(0, (t - t0) * 9))); KLR = [(220, 60, 60), (60, 120, 220), (60, 180, 90), (240, 180, 40), (150, 80, 200), (30, 30, 40)]
    y1 = 980
    for k in range(n):
        x0 = 1450 + (k % 2) * 8 - (k % 3) * 6; y1 = 980 - k * 34
        d.rounded_rectangle((x0, y1 - 32, x0 + 190, y1), 5, fill=KLR[k % len(KLR)], outline=(30, 30, 36), width=3)
        d.rectangle((x0 + 12, y1 - 26, x0 + 74, y1 - 6), fill=(250, 250, 250))
        d.rounded_rectangle((x0 + 22, y1 - 22, x0 + 64, y1 - 10), 6, fill=(45, 45, 52))           # mini-controller op het doosje
        d.ellipse((x0 + 54, y1 - 19, x0 + 59, y1 - 14), fill=(230, 60, 60)); d.rectangle((x0 + 27, y1 - 17, x0 + 35, y1 - 15), fill=(220, 220, 225))
    if n:                                                # gamecontroller
        cx, cy = 1545, 980 - (n - 1) * 34 - 32 - 34
        for gx in (-52, 52): d.ellipse((cx + gx - 30, cy - 18, cx + gx + 30, cy + 40), fill=(45, 45, 52), outline=INK, width=3)
        d.rounded_rectangle((cx - 70, cy - 24, cx + 70, cy + 24), 22, fill=(45, 45, 52), outline=INK, width=3)
        d.rectangle((cx - 52, cy - 4, cx - 28, cy + 4), fill=(220, 220, 225)); d.rectangle((cx - 44, cy - 12, cx - 36, cy + 12), fill=(220, 220, 225))
        for (bx, by, kl) in ((38, -8, (230, 60, 60)), (50, 4, (60, 180, 90)), (26, 4, (60, 120, 220)), (38, 16, (240, 190, 40))):
            d.ellipse((cx + bx - 6, cy + by - 6, cx + bx + 6, cy + by + 6), fill=kl)
def tafel(img, x0=760, x1=1160):                        # schooltafel vóór het poppetje: zo lijkt het of je zit
    d = ImageDraw.Draw(img)
    d.rectangle((x0, 818, x1, 846), fill=(200, 150, 95), outline=(60, 45, 35), width=4)
    for x in (x0 + 30, x1 - 44): d.rectangle((x, 846, x + 14, 990), fill=(120, 120, 130), outline=(50, 50, 60), width=2)
    d.rectangle((x0 + 15, 846, x1 - 15, 1000), fill=(185, 135, 85), outline=(60, 45, 35), width=3)     # dichte voorkant: je zit erachter
    WACHT.vlak("schoolbureau", [x0, x1, 812, 846])
def mat(img, half):                                      # deurmat met "WELCOME"; half = aangevreten, hangt uit de bek
    d = ImageDraw.Draw(img); BR, RD = (165, 110, 60), (70, 45, 30)
    if not half:                                          # plat op het gras voor het paard
        d.polygon([(1320, 945), (1570, 945), (1600, 990), (1290, 990)], fill=BR, outline=RD)
        d.polygon([(1332, 951), (1558, 951), (1584, 984), (1306, 984)], outline=(110, 70, 40))
        f_ = font(FB, 28); tw = d.textlength("WELCOME", font=f_); d.text((1445 - tw / 2, 951), "WELCOME", font=f_, fill=(90, 55, 30))
        return
    x0, y0 = 1330, 650                                    # hangt breed uit de bek (bek op x 1385, y 625-677), hap uit de rechterkant
    rand = [(x0 + 170, y0 + 22), (x0 + 152, y0 + 36), (x0 + 168, y0 + 50), (x0 + 150, y0 + 64), (x0 + 166, y0 + 78)]
    d.polygon([(x0, y0), (x0 + 170, y0)] + rand + [(x0 + 166, y0 + 90), (x0, y0 + 90)], fill=BR, outline=RD)
    d.rectangle((x0 + 8, y0 + 8, x0 + 148, y0 + 82), outline=(110, 70, 40), width=2)
    d.text((x0 + 14, y0 + 28), "WELCO", font=font(FB, 34), fill=(90, 55, 30))
# ---------- tekeningen voor de rest van het verhaal (laten zien wat er gezegd wordt) ----------
INK = (40, 35, 40)
def ballon(img, x, y, tekst, sch=1.0):                  # tekstballon (telefoon/roep)
    d = ImageDraw.Draw(img); f = font(FB, int(46 * sch)); w = d.textlength(tekst, font=f)
    d.rounded_rectangle((x - w / 2 - 26, y - 44 * sch, x + w / 2 + 26, y + 34 * sch), 26, fill=(255, 255, 255), outline=INK, width=5)
    d.polygon([(x - 30, y + 30 * sch), (x - 70, y + 80 * sch), (x + 5, y + 32 * sch)], fill=(255, 255, 255), outline=INK)
    d.text((x - w / 2, y - 30 * sch), tekst, font=f, fill=INK)
def router(img, t, tijden):
    a, b, c = tijden; aan = not (a <= t < b or t >= c)
    d = ImageDraw.Draw(img); x0, y0 = 1065, 522            # staat op het aanrecht (blad op y 572)
    d.rectangle((1150, 455, 1196, 495), fill=(245, 245, 245), outline=INK, width=3)           # stopcontact
    for ox in (1163, 1183): d.ellipse((ox - 4, 471, ox + 4, 479), fill=INK)
    stekker = (1173, 475) if aan else (1215, 560)          # uitgetrokken: stekker hangt over de rand
    d.line((x0 + 140, y0 + 20, x0 + 150, y0 - 10, stekker[0], stekker[1] + 14), fill=INK, width=5)
    d.rectangle((stekker[0] - 10, stekker[1], stekker[0] + 10, stekker[1] + 22), fill=(60, 60, 70))
    d.rounded_rectangle((x0, y0, x0 + 140, y0 + 50), 10, fill=(235, 235, 240), outline=INK, width=4)
    for k in (22, 118): d.line((x0 + k, y0, x0 + k - 8, y0 - 55), fill=INK, width=5)
    for k in range(4): d.ellipse((x0 + 24 + k * 26, y0 + 20, x0 + 36 + k * 26, y0 + 32), fill=(60, 220, 100) if aan and int(t * 4 + k) % 3 else (90, 90, 100))
    kapot = t >= SC_NU.get("kapot", 1e9)                   # kleine tv op het linker aanrecht
    d.rectangle((410, 598, 470, 612), fill=(60, 60, 70))
    d.rounded_rectangle((330, 470, 550, 600), 10, fill=(25, 25, 32))
    d.rectangle((342, 482, 538, 588), fill=(20, 20, 24) if kapot else (120, 170, 220))
    if kapot:
        for pts in (((440, 482), (420, 520), (455, 545), (430, 588)), ((420, 520), (360, 540)), ((455, 545), (520, 560))):
            d.line(pts, fill=(200, 200, 210), width=3)
def vonk(img, t, t0):
    if not (t0 <= t < t0 + 1.2): return
    d = ImageDraw.Draw(img); cx, cy = 440, 470            # vonk boven de tv
    for k in range(8):
        h = k * math.pi / 4 + t * 3; r = 60 + 30 * math.sin(t * 20 + k)
        d.line((cx, cy, cx + math.cos(h) * r, cy + math.sin(h) * r), fill=(255, 210, 40), width=8)
def prijsbord(img, t, prijzen):
    d = ImageDraw.Draw(img); x0, y0 = 980, 520
    d.rectangle((x0, y0, x0 + 110, y0 + 190), fill=(250, 250, 255), outline=INK, width=5)                  # melkpak
    d.polygon([(x0, y0), (x0 + 55, y0 - 50), (x0 + 110, y0)], fill=(230, 230, 240), outline=INK)
    d.rectangle((x0 + 12, y0 + 60, x0 + 98, y0 + 120), fill=(70, 130, 220)); d.text((x0 + 16, y0 + 72), "MILK", font=font(FB, 32), fill=(255, 255, 255))
    nu = [pr for t0, pr in prijzen if t >= t0]
    if nu:
        t0 = max(t0 for t0, pr in prijzen if t >= t0); sch = ps.pop((t - t0) / 0.3)
        f = font(FB, int(72 * sch)); b = d.textbbox((0, 0), nu[-1], font=f); tw, th = b[2] - b[0], b[3] - b[1]
        bx, by = x0 + 55 - (tw + 44) / 2, 712                  # aan de plankrand onder het melkpak
        d.rounded_rectangle((bx, by, bx + tw + 44, by + th + 40), 14, fill=(255, 225, 60), outline=INK, width=5)
        d.text((bx + 22 - b[0], by + 20 - b[1]), nu[-1], font=f, fill=(200, 30, 30))
def banaan(img, x, y, s=1.0):                            # gebogen banaan met bruin steeltje en puntje
    d = ImageDraw.Draw(img); pts_b, pts_o = [], []
    for k in range(13):
        a = math.radians(200 + k * 11.7)
        pts_b.append((x + math.cos(a) * 52 * s, y - 10 * s + math.sin(a) * 34 * s))
        pts_o.append((x + math.cos(a) * 42 * s, y - 2 * s + math.sin(a) * 20 * s))
    d.polygon(pts_b + pts_o[::-1], fill=(250, 215, 60), outline=INK)
    d.line(pts_b, fill=INK, width=3); d.line(pts_o, fill=(200, 160, 40), width=2)
    d.rectangle((pts_b[-1][0] - 2, pts_b[-1][1] - 12 * s, pts_b[-1][0] + 8 * s, pts_b[-1][1] + 2), fill=(110, 80, 40))   # steeltje
    d.ellipse((pts_b[0][0] - 5 * s, pts_b[0][1] - 4 * s, pts_b[0][0] + 3 * s, pts_b[0][1] + 4 * s), fill=(80, 60, 35))     # puntje
def chefmuts(img, x, y, s):
    d = ImageDraw.Draw(img)
    for dx in (-26, 0, 26): d.ellipse((x + dx * s - 30 * s, y - 95 * s, x + dx * s + 30 * s, y - 35 * s), fill=(255, 255, 255), outline=INK, width=4)
    d.rectangle((x - 48 * s, y - 45 * s, x + 48 * s, y + 4 * s), fill=(255, 255, 255), outline=INK, width=4)
def rook(img, t, t0):
    if t < t0: return
    f = min(1, (t - t0) / 1.5)                           # zachte rookwolk: uit de keukendeur omhoog, dan een waas langs het plafond
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    for k in range(7):                                    # pluimen uit de deuropening
        fase = (t * 0.35 + k / 7) % 1; x = 1010 + 60 * math.sin(t * 1.5 + k * 2) * fase; y = 330 - 200 * fase; r = (35 + 45 * fase) * f
        d.ellipse((x - r, y - r, x + r, y + r), fill=(120, 120, 130, int(150 * (1 - 0.4 * fase))))
    for k in range(12):                                   # waas langs het plafond, groeit vanuit het midden
        x = 1010 + (k - 5.5) * 150 * f + 25 * math.sin(t * 1.1 + k); y = 170 + 25 * math.sin(t * 0.8 + k * 1.7); r = 90 + 15 * math.sin(t * 1.6 + k)
        d.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=(120, 120, 130, int(140 * f)))
    laag = laag.filter(ImageFilter.GaussianBlur(10)); img.paste(laag, (0, 0), laag)
    d = ImageDraw.Draw(img)                              # rookmelder aan het plafond
    d.ellipse((1380, 50, 1520, 100), fill=(245, 245, 245), outline=INK, width=4)
    if int(t * 3) % 2: d.ellipse((1438, 64, 1462, 86), fill=(240, 40, 40))
    if t < t0 + 4 and int(t * 3) % 2: kop(img, "BEEP! BEEP!", 1500, 130, 64, KL["rood"], 1)
def cereal(img, t, t0):
    if t < t0: return
    d = ImageDraw.Draw(img); sch = ps.pop((t - t0) / 0.3); cx, cy = 1722, 670     # op de rechter tafel, rechts van het kaarsje
    d.ellipse((cx - 82 * sch, cy - 20 * sch, cx + 82 * sch, cy + 20 * sch), fill=(250, 250, 250), outline=INK, width=4)
    d.ellipse((cx - 30 * sch, cy - 12 * sch, cx + 30 * sch, cy + 10 * sch), fill=(240, 200, 110), outline=INK, width=2)
    for k in range(7): a = k * 0.9; d.ellipse((cx + math.cos(a) * 18 * sch - 5, cy + math.sin(a) * 6 * sch - 5, cx + math.cos(a) * 18 * sch + 5, cy + math.sin(a) * 6 * sch + 5), fill=(200, 130, 50), outline=INK)
def biljet(img, t, t0):
    if t < t0: return
    leeg = bg(SC_NU.get("bg", "feit")).crop((100, 380, 900, 960)); img.paste(leeg, (910, 380))   # huisje + spaarvarken weg: lege muur en vloer
    d = ImageDraw.Draw(img); sch = ps.pop((t - t0) / 0.35); cx, cy = 1250, 530; w, h = 860 * sch, 330 * sch
    d.rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=(170, 210, 160), outline=(40, 80, 40), width=6)
    d.rectangle((cx - w / 2 + 20, cy - h / 2 + 20, cx + w / 2 - 20, cy + h / 2 - 20), outline=(60, 110, 60), width=3)
    for k, (r, m) in enumerate((("RESERVE BANK OF ZIMBABWE", 30), ("ONE HUNDRED TRILLION DOLLARS", 38), ("100 000 000 000 000", 52))):
        f = font(FB, int(m * sch)); tw = d.textlength(r, font=f); d.text((cx - tw / 2, cy - 110 * sch + k * 80 * sch), r, font=f, fill=(30, 70, 30))
    bron = "Source: Reserve Bank of Zimbabwe, Z$100 trillion banknote (2009)"; fb = font(FS, 26)
    bw = d.textlength(bron, font=fb); by = cy + h / 2 + 16
    d.rounded_rectangle((cx - bw / 2 - 14, by - 6, cx + bw / 2 + 14, by + 36), 10, fill=(255, 255, 255), outline=(60, 50, 50), width=2)
    d.text((cx - bw / 2, by), bron, font=fb, fill=(50, 40, 40))
def sheet(img, t, regels):
    if t < regels[0][0]: return
    d = ImageDraw.Draw(img); x0, y0 = 150, 330
    d.rectangle((x0 + 160, y0 + 400, x0 + 175, y0 + 640), fill=(120, 90, 60)); d.rectangle((x0 + 345, y0 + 400, x0 + 360, y0 + 640), fill=(120, 90, 60))
    d.rectangle((x0, y0, x0 + 600, y0 + 420), fill=(255, 255, 255), outline=INK, width=6)
    d.rectangle((x0, y0, x0 + 600, y0 + 70), fill=(60, 160, 90)); d.text((x0 + 20, y0 + 12), regels[0][1], font=font(FB, 44), fill=(255, 255, 255))
    for k, (t0, a, b) in enumerate(regels[1:]):
        if t < t0: continue
        y = y0 + 90 + k * 78; d.line((x0, y + 66, x0 + 600, y + 66), fill=(200, 200, 210), width=2)
        d.text((x0 + 20, y + 10), a, font=font(FS, 38), fill=INK); d.text((x0 + 580 - d.textlength(b, font=font(FB, 38)), y + 10), b, font=font(FB, 38), fill=(200, 40, 40))
def keukentafel(img, x0=380, x1=1600):                  # tafel met dichte voorkant tot de vloer: wie erachter staat, lijkt te zitten
    d = ImageDraw.Draw(img); d.rectangle((x0, 820, x1, 850), fill=(190, 140, 90), outline=INK, width=5)
    d.rectangle((x0 + 20, 850, x1 - 20, 1010), fill=(170, 120, 75), outline=INK, width=4)
    for x in range(x0 + 40, x1 - 40, 160): d.line((x, 860, x, 1000), fill=(150, 104, 64), width=3)
def kaars(img, t, x, y):
    d = ImageDraw.Draw(img); d.rectangle((x - 12, y - 70, x + 12, y), fill=(250, 245, 230), outline=INK, width=3)
    fl = 1 + 0.15 * math.sin(t * 13); d.ellipse((x - 11 * fl, y - 105 * fl, x + 11 * fl, y - 70), fill=(255, 200, 60), outline=(240, 120, 30), width=3)
def spelbord(img):                                       # bordspel van bovenaf (schuin): rand met gekleurde straten, midden groen
    d = ImageDraw.Draw(img); x0, y0, w, h, sk = 600, 752, 330, 64, 70
    def pt(u, v): return (x0 + u * w + (1 - v) * sk, y0 + v * h)
    d.polygon([pt(0, 0), pt(1, 0), pt(1, 1), pt(0, 1)], fill=(235, 240, 225), outline=INK)
    d.polygon([pt(0.12, 0.2), pt(0.88, 0.2), pt(0.88, 0.8), pt(0.12, 0.8)], fill=(190, 225, 190), outline=INK)
    KL_ = [(220, 60, 60), (240, 180, 40), (60, 170, 90), (60, 110, 220), (150, 80, 200), (240, 120, 40)]
    for k in range(6):
        u0, u1 = 0.12 + k * 0.127, 0.12 + (k + 1) * 0.127
        d.polygon([pt(u0, 0.02), pt(u1, 0.02), pt(u1, 0.16), pt(u0, 0.16)], fill=KL_[k])
        d.polygon([pt(u0, 0.84), pt(u1, 0.84), pt(u1, 0.98), pt(u0, 0.98)], fill=KL_[5 - k])
    d.ellipse((pt(0.45, 0.45)[0] - 9, pt(0.45, 0.45)[1] - 6, pt(0.45, 0.45)[0] + 9, pt(0.45, 0.45)[1] + 6), fill=(230, 60, 60), outline=INK)   # pionnetje
def donker(img, t, t0):
    if t < t0: return img
    f = min(1, (t - t0) / 0.15); zwart = Image.new("RGB", img.size, (10, 12, 30)); return Image.blend(img, zwart, 0.72 * f)
def gloed(img, x, y):
    g = Image.new("L", img.size, 0); dg = ImageDraw.Draw(g)
    for r in range(420, 0, -30): dg.ellipse((x - r, y - r * 0.7, x + r, y + r * 0.7), fill=int(150 * (1 - r / 420)))
    licht = Image.new("RGB", img.size, (255, 190, 90)); return Image.composite(licht, img, g.point(lambda v: int(v * 0.55)))
def accu(img, t, t0):
    if t < t0: return
    d = ImageDraw.Draw(img); x0, y0 = 1560, 260
    d.rounded_rectangle((x0, y0, x0 + 220, y0 + 100), 14, outline=(255, 255, 255), width=8); d.rectangle((x0 + 220, y0 + 30, x0 + 240, y0 + 70), fill=(255, 255, 255))
    if int(t * 2) % 2: d.rectangle((x0 + 14, y0 + 14, x0 + 34, y0 + 86), fill=(230, 50, 50))
    d.text((x0 + 60, y0 + 16), "0%", font=font(FB, 60), fill=(230, 50, 50))
def wang(img, x, y, s, t=0.0):                          # kiespijn: het gezicht zelf bolt uit (één vorm, geen losse bal)
    """(x, y) = bovenkant hoofd zoals poppetje() teruggeeft; s = schaal incl. 'groot'. Hoofd: middelpunt (x, y + 60s), straal 60s."""
    R = 60 * s; cx, cy = x, y + R; lw = max(3, int(4 * s))
    x0, y0 = int(cx - 1.4 * R), int(cy - 1.4 * R); w_, h_ = int(3.4 * R), int(2.8 * R)
    lx, ly = cx - x0, cy - y0                              # middelpunt hoofd in het stukje
    bx, by, rx, ry = lx + R * 0.56, ly + R * 0.56, R * 0.52, R * 0.46     # bult rechtsonder, steekt ±16% buiten het gezicht
    hoofd = Image.new("L", (w_, h_), 0); ImageDraw.Draw(hoofd).ellipse((lx - R, ly - R, lx + R, ly + R), fill=255)
    bult = Image.new("L", (w_, h_), 0); ImageDraw.Draw(bult).ellipse((bx - rx, by - ry, bx + rx, by + ry), fill=255)
    samen = ImageChops.lighter(hoofd, bult)
    buiten = ImageChops.subtract(bult, hoofd)              # alleen het stuk buiten het oude gezicht (ogen/bril blijven heel)
    stuk = img.crop((x0, y0, x0 + w_, y0 + h_))
    stuk.paste(ps.HUID, (0, 0), buiten.filter(ImageFilter.MaxFilter(3)))   # oude hoofdlijn in de bult weg
    rand = ImageChops.subtract(samen.filter(ImageFilter.MaxFilter(2 * lw + 1)), samen)
    stuk.paste(INK, (0, 0), rand)                          # één doorlopende buitenlijn om gezicht + bult
    gloed = Image.new("L", (w_, h_), 0); ImageDraw.Draw(gloed).ellipse((bx - rx * 0.35, by - ry * 0.25, bx + rx * 0.75, by + ry * 0.65), fill=110)
    gloed = ImageChops.multiply(gloed.filter(ImageFilter.GaussianBlur(R * 0.18)), samen)
    stuk.paste((235, 95, 85), (0, 0), gloed)               # zachte rode gloed, geen harde stip
    img.paste(stuk, (x0, y0))
    d = ImageDraw.Draw(img); tril = 3 * math.sin(t * 25)
    for k, (dx, dy) in enumerate(((1.35, -0.35), (1.5, 0.3), (1.32, 0.95))):   # pijnstreepjes naast de bult
        px, py = cx + R * dx + tril, cy + R * dy
        d.line((px, py, px + 14 * s, py - 8 * s, px + 6 * s, py + 2 * s, px + 22 * s, py - 6 * s), fill=(220, 40, 40), width=max(3, int(4 * s)))
def deur(img, open_):
    d = ImageDraw.Draw(img)
    if open_:                                            # op een kier (knop nog bij het touw), slaat daarna dicht
        d.polygon([(60, 300), (290, 325), (290, 935), (60, 960)], fill=(150, 100, 60), outline=INK); d.ellipse((252, 620, 274, 642), fill=(230, 200, 80), outline=INK)
    else: d.rectangle((60, 300, 330, 960), fill=(160, 110, 70), outline=INK, width=6); d.ellipse((290, 620, 312, 642), fill=(230, 200, 80), outline=INK)
def tandje(img, x, y):                                   # kies: bolle kroon met twee wortels
    d = ImageDraw.Draw(img); S = 1.4
    d.polygon([(x - 16 * S, y - 10 * S), (x - 12 * S, y + 16 * S), (x - 4 * S, y + 4 * S), (x + 4 * S, y + 4 * S), (x + 12 * S, y + 16 * S), (x + 16 * S, y - 10 * S)],
              fill=(255, 255, 255), outline=INK)
    d.ellipse((x - 17 * S, y - 22 * S, x + 17 * S, y - 2 * S), fill=(255, 255, 255), outline=INK, width=3)
    d.rectangle((x - 15 * S, y - 12 * S, x + 15 * S, y - 6 * S), fill=(255, 255, 255))
def tv(img, t, t0, laag_pop):
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 740, 95, 1340, 465          # aan de muur boven de bank (geen poot)
    d.rounded_rectangle((x0 - 16, y0 - 16, x1 + 16, y1 + 16), 18, fill=(25, 25, 32))
    if t < t0: d.rectangle((x0, y0, x1, y1), fill=(15, 15, 20)); return
    d.rectangle((x0, y0, x1, y1), fill=(120, 170, 220))
    sl = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    hx, hy = ps.poppetje(ImageDraw.Draw(sl), "ster", 1040, 595, 1.3, t, kijk=0.0, mond=0.6 * abs(math.sin(t * 9)), verbaasd=True, gebaar="schrik")
    sl = sl.resize((W, H), Image.LANCZOS).crop((x0, y0, x1, y1)); img.paste(sl, (x0, y0), sl)
    S = 1.3; cy = hy + 62 * S
    for k, ox in enumerate((-26, 26)):                  # tranen
        ty = cy + ((t * 90 + k * 30) % 50); d.ellipse((hx + ox * S - 9, ty, hx + ox * S + 9, ty + 24), fill=(90, 170, 255), outline=(40, 90, 160))
    d.rectangle((x0, y1 - 70, x1, y1), fill=(200, 30, 30)); br_ = "NOBODY WANTS HER AUTOGRAPH"; fz = 34
    while d.textlength(br_, font=font(FB, fz)) > x1 - x0 - 40: fz -= 1          # tekst past altijd binnen het scherm
    if fz < 24: LAYOUT.add("tv-balk te lang")
    d.text(((x0 + x1) / 2 - d.textlength(br_, font=font(FB, fz)) / 2, y1 - 35 - fz * 0.6), br_, font=font(FB, fz), fill=(255, 255, 255))
def kokosnoot(img, x, y, s=1.0):                         # open kokosnoot met rietje en parasolletje (zoals op Hawaii)
    d = ImageDraw.Draw(img)
    d.ellipse((x - 42 * s, y - 34 * s, x + 42 * s, y + 42 * s), fill=(120, 80, 45), outline=INK, width=4)
    for k in range(6): d.line((x - 30 * s + k * 12 * s, y - 10 * s, x - 34 * s + k * 12 * s, y + 30 * s), fill=(90, 60, 35), width=2)   # haren
    d.ellipse((x - 36 * s, y - 40 * s, x + 36 * s, y - 20 * s), fill=(250, 250, 245), outline=INK, width=3)                          # wit vruchtvlees
    d.ellipse((x - 26 * s, y - 36 * s, x + 26 * s, y - 24 * s), fill=(235, 235, 220))
    d.line((x + 6 * s, y - 30 * s, x + 26 * s, y - 92 * s), fill=(230, 60, 90), width=max(3, int(5 * s)))                             # rietje
    d.line((x - 12 * s, y - 30 * s, x - 22 * s, y - 80 * s), fill=(120, 90, 60), width=3)                                            # parasolstokje
    d.pieslice((x - 52 * s, y - 104 * s, x + 8 * s, y - 64 * s), 180, 360, fill=(60, 170, 220), outline=INK, width=2)
def zonnebrand(img, x, y, s):                         # verbrand: knalrode wangen en neus (gezicht blijft zichtbaar)
    S = s * ps.C["teach"].get("groot", 1); R = 60 * S; cy = y + R
    laag = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    d.ellipse((x - R * 0.95, cy - R * 0.95, x + R * 0.95, cy + R * 0.95), fill=(235, 70, 50, 95))
    d.rectangle((x - R, cy - R, x + R, cy - R * 0.25), fill=(0, 0, 0, 0))                       # niet over het haar
    img.paste(laag, (0, 0), laag)
    d = ImageDraw.Draw(img)
    for ox, oy in ((-0.45, 0.15), (0.5, 0.2), (0.1, -0.1)):                                      # vervellende plekjes
        d.ellipse((x + ox * R - 5, cy + oy * R - 3, x + ox * R + 5, cy + oy * R + 3), fill=(255, 235, 225))
def telefoon_bericht(img, t, regels):
    d = ImageDraw.Draw(img); x0, y0, x1, y1 = 1265, 70, 1805, 920
    d.rounded_rectangle((x0, y0, x1, y1), 48, fill=(25, 25, 32), outline=(10, 10, 14), width=6)
    d.rounded_rectangle((x0 + 18, y0 + 18, x1 - 18, y1 - 18), 34, fill=(245, 247, 250))
    d.rectangle((x0 + 18, y0 + 90, x1 - 18, y0 + 170), fill=(40, 110, 220)); d.text((x0 + 50, y0 + 105), "NEW MESSAGE", font=font(FB, 40), fill=(255, 255, 255))
    y = y0 + 210
    for r, kl in regels:
        f = font(FB, 40 if kl != "groot" else 54)
        woorden, lijn = r.split(), ""
        for w_ in woorden:
            if d.textlength(lijn + " " + w_, font=f) > x1 - x0 - 100: d.text((x0 + 50, y), lijn, font=f, fill=INK); y += 56; lijn = w_
            else: lijn = (lijn + " " + w_).strip()
        if d.textlength(lijn, font=f) > x1 - x0 - 80 or y > y1 - 80: LAYOUT.add(f"telefoontekst '{lijn}' past niet")
        d.text((x0 + 50, y), lijn, font=f, fill=(30, 160, 80) if kl == "groot" else INK); y += 80

def wasberen(img, t, t0):
    if t < t0: return
    top = SC_NU["_vuiltop"] if "_vuiltop" in SC_NU else 330
    groot_ = Image.new("RGBA", img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(groot_)
    for k, (x, y) in enumerate(((1540, top + 10), (1640, top - 5), (1740, top + 15))):
        y += 4 * math.sin(t * 5 + k); GR = (140, 140, 150)
        for r in range(4):                                 # gestreepte staart
            tx, ty = x - 40 - r * 16, y + 70 - r * 10
            d.ellipse((tx - 13, ty - 13, tx + 13, ty + 13), fill=GR if r % 2 == 0 else (60, 60, 70), outline=INK, width=3)
        d.ellipse((x - 36, y + 12, x + 36, y + 92), fill=GR, outline=INK, width=4)       # lijf
        d.ellipse((x - 18, y + 38, x + 18, y + 82), fill=(200, 200, 205))                # buik
        for ox in (-22, 22): d.ellipse((x + ox - 11, y + 74, x + ox + 11, y + 96), fill=(60, 60, 70), outline=INK, width=3)
        d.ellipse((x - 34, y - 30, x + 34, y + 30), fill=GR, outline=INK, width=4)
        d.rectangle((x - 30, y - 10, x + 30, y + 6), fill=(50, 50, 60))
        for ox in (-14, 14): d.ellipse((x + ox - 7, y - 8, x + ox + 7, y + 4), fill=(255, 255, 255)); d.ellipse((x + ox - 3, y - 5, x + ox + 3, y + 1), fill=INK)
        for ox in (-26, 26): d.polygon([(x + ox - 10, y - 22), (x + ox, y - 44), (x + ox + 10, y - 22)], fill=(140, 140, 150), outline=INK)
        d.arc((x - 12, y + 4, x + 12, y + 22), 20, 160, fill=INK, width=4)                 # blij lachje
    bx0, by0, bx1, by1 = 1440, top - 60, 1800, top + 120; stuk = groot_.crop((bx0, by0, bx1, by1))
    stuk = stuk.resize((int(stuk.width * 1.35), int(stuk.height * 1.35)), Image.LANCZOS)
    img.paste(stuk, (int(1590 - stuk.width / 2), int(top + 110 - stuk.height)), stuk)          # groter, onderkant óp de berg
def fooi(img, t, t0):
    if t < t0: return
    d = ImageDraw.Draw(img); sch = ps.pop((t - t0) / 0.3); cx, cy = 1530, 672    # briefje links van het kaarsje
    d.rectangle((cx - 75 * sch, cy - 24 * sch, cx + 75 * sch, cy + 24 * sch), fill=(170, 220, 160), outline=(40, 90, 40), width=3)
    f_ = font(FB, max(8, int(24 * sch))); d.text((cx - d.textlength("$1,000,000", font=f_) / 2, cy - 18 * sch), "$1,000,000", font=f_, fill=(30, 80, 30))
def huiswerk(img, t, t0, ox=0, oy=0):                    # alleen een stapel schriften + papier die snel hoog wordt (eigenaar: geen blaadje/tekst erop)
    if t < t0: return
    d = ImageDraw.Draw(img); KL = [(220, 70, 70), (70, 120, 220), (60, 170, 90), (240, 180, 40), (150, 90, 200)]
    n = min(14, int((t - t0) * 9) + 1); y = 818 + oy; x0 = 790 + ox
    for k in range(n):
        sch = k % 3 != 2                                   # 2 schriften, dan een dun stapeltje papier
        h = 22 if sch else 12; sx = x0 + (k * 7) % 13 - 6
        if sch: d.rounded_rectangle((sx, y - h, sx + 180, y), 4, fill=KL[k % 5], outline=INK, width=3); d.rectangle((sx + 4, y - h + 5, sx + 18, y - 5), fill=(250, 250, 250))
        else: d.rectangle((sx + 4, y - h, sx + 176, y), fill=(250, 250, 250), outline=INK, width=2)
        y -= h
SC_NU = {}; GEZ = {}; NAAM_GETOOND = False
ZOOM_AAN = True; TEKST_AAN = True                      # uit voor de herkenwachter (losse voorwerpen zonder zoom en zonder tekst)
def leeg_schap(img, groep):
    """Leeg schap tekenen in een deel van de winkel (snacks links, brood midden, wc-papier rechts): achterwand + planken."""
    x0, x1 = {0: (140, 760), 1: (760, 1330), 2: (1330, 1800)}[groep]
    d = ImageDraw.Draw(img); d.rectangle((x0, 190, x1, 731), fill=(238, 230, 214))
    for y0, y1 in ((287, 324), (438, 493), (587, 627)):
        h = y1 - y0; d.rectangle((x0, y0, x1, y0 + int(h * 0.4)), fill=(206, 213, 223)); d.rectangle((x0, y0 + int(h * 0.4), x1, y1), fill=(160, 170, 182))
        d.line((x0, y1, x1, y1), fill=(120, 128, 140), width=3)
    if groep == 0:                                       # winkelwagen weer voor het schap (donkerblauwe lijnen uit de achtergrond)
        k = np.array(bg("winkel").crop((180, 640, 470, 740))).astype(int)
        m = Image.fromarray((((k[..., 2] > k[..., 0] + 30) & (k[..., 0] < 110)) * 255).astype(np.uint8), "L")
        img.paste(bg("winkel").crop((180, 640, 470, 740)), (180, 640), m)
AUTO_RIJ = [(160, 0.15), (455, 0.6), (750, 0.55), (1045, 0.33), (1340, 0.75)]   # 5 plekken op de stoep, 281 px breed
def auto_rij(img, n, vanaf=0, t=None, t0=None):
    for j, (xx, tn) in enumerate(AUTO_RIJ[:n]):
        if j >= vanaf and t0 is not None and t < t0 + (j - vanaf) * 0.25: continue
        zet(img, "sportwagen", 80, xx, 748, op="stoep", tint=tn, spiegel=j >= 2)
_GLAS = {}
def glasmasker(n, vakken):
    """Pixels van ruiten (lichte lucht) binnen de raamvakken van achtergrond n -> masker (eenmalig)."""
    if n not in _GLAS:
        a = np.asarray(bg(n)).astype(int); r, g, b_ = a[..., 0], a[..., 1], a[..., 2]
        m = ((b_ > r + 12) & (b_ > 170)) | ((r > 225) & (g > 235) & (b_ > 235))
        vak = np.zeros(m.shape, bool)
        for x0, y0, x1, y1 in vakken: vak[y0:y1, x0:x1] = True
        _GLAS[n] = Image.fromarray(((m & vak) * 255).astype(np.uint8), "L")
    return _GLAS[n]
KEUKENRAMEN = [(80, 125, 295, 575), (695, 175, 1120, 515)]
def nacht_ramen(img, t, t0):                            # middernacht: ruiten donker met sterren, keuken iets donkerder
    f = min(1, (t - t0) / 0.5); m = glasmasker("keuken", KEUKENRAMEN).point(lambda v: int(v * f))
    img.paste((22, 26, 64), (0, 0), m); d = ImageDraw.Draw(img)
    for k in range(14):
        sx, sy = 720 + (k * 131) % 380, 200 + (k * 71) % 280
        if m.getpixel((sx, sy)) > 128: d.ellipse((sx - 3, sy - 3, sx + 3, sy + 3), fill=(255, 250, 220))
    if SC_NU.get("raampaard") is not None and t >= SC_NU["raampaard"]: raampaard(img, t, SC_NU["raampaard"])   # paard blijft in het raam
    return Image.blend(img, Image.new("RGB", img.size, (10, 12, 30)), 0.28 * f)
def raampaard(img, t, t0):                               # paard kijkt door het keukenraam naar binnen
    sp = sprite("paard", 250); laag = Image.new("RGBA", img.size, (0, 0, 0, 0)); laag.paste(sp, (int(880 - sp.width / 2), 300), sp)   # hoofd onder de koppen
    m = ImageChops.multiply(laag.split()[3], glasmasker("keuken", KEUKENRAMEN)); img.paste(laag, (0, 0), m)
def brandhout(img):                                      # stapel blokken hout op de vloer rechts naast de tafel (eigenaar: stoelstuk leek een telefoon -> weg)
    d = ImageDraw.Draw(img)
    for (x, y) in ((1350, 1040), (1450, 1040), (1400, 992), (1500, 992), (1450, 944)):
        d.rounded_rectangle((x - 50, y - 26, x + 50, y + 22), 14, fill=(150, 95, 55), outline=INK, width=3)
        d.ellipse((x + 26, y - 22, x + 50, y + 18), fill=(215, 170, 120), outline=INK, width=2)
def frame(t):
    global SC_NU
    k = max(i for i in range(len(SC)) if SC[i]["t"] <= t); sc = SC[k]; SC_NU = sc
    thuis = sc.get("thuis") is not None and t >= sc["thuis"]
    img = bg("kamer-jij" if thuis else sc["bg"]).copy(); WACHT.begin("kamer-jij" if thuis else sc["bg"], t)
    if sc.get("eet"):
        tb, tf, tm = sc["eet"]
        if t >= tb + 0.7:                                  # bloemen opgegeten: zelfde hekplanken eroverheen (planken zijn 115 px breed)
            schoon = bg("tuin")
            img.paste(schoon.crop((825, 425, 1170, 575)), (1170, 425)); img.paste(schoon.crop((830, 425, 870, 575)), (1515, 425))
            dd = ImageDraw.Draw(img)
            for sx in (1240, 1345, 1465):                  # afgeknabbelde steeltjes
                dd.line((sx, 572, sx, 540), fill=(80, 130, 70), width=9)
                dd.line((sx - 6, 540, sx - 2, 533, sx + 2, 541, sx + 6, 534), fill=(80, 130, 70), width=4)
        if t >= tf + 0.6:                                  # hap uit één plank: groene struiken erachter, gekartelde rand
            dd = ImageDraw.Draw(img)
            rand = [(1402, 395), (1385, 360), (1368, 402), (1350, 362), (1332, 405), (1314, 366), (1290, 398)]
            dd.polygon([(1286, 266), (1346, 214), (1406, 266)] + rand, fill=bg("tuin").getpixel((1346, 222)))
            dd.line(rand, fill=(110, 75, 50), width=5)
    nu = max((i for i, z in enumerate(Z) if z[0] - 0.05 <= t <= z[1] + 0.3), default=None)
    tekst_nu = Z[nu][2] if nu is not None else ""
    spreker = LIJF.get(Z[nu][4]) if nu is not None and Z[nu][4] != "N" else None
    # voorwerpen achter de poppetjes
    if sc.get("show"): auto_rij(img, 2)                  # achterste rij eerst, roze auto ervoor
    if sc.get("drie") is not None and t >= sc["drie"]: auto_rij(img, 5, vanaf=2, t=t, t0=sc["drie"])
    if sc.get("vol"): auto_rij(img, 5)
    if sc.get("auto") is not None:
        a = sc["auto"]; f = ps.ease((t - a) / 1.2); x = -500 + (480 + 500) * f
        if t >= a: zet(img, "sportwagen", 230, x, 975, op="weg")
    if sc.get("boot") is not None and t >= sc["boot"]:
        zet(img, "boot", int(330 * ps.pop((t - sc["boot"]) / 0.35)), 1180, 990, op="weg")
    if sc.get("stoel"): zet(img, "gamestoel", 560, 820, 980, op="vloer")
    if sc.get("paard"): WACHT.plaats("paard", (1100 - 285, 515, 1100 + 285, 985), op="gras")
    if sc.get("paard"):
        hap = any(e <= t < e + 0.9 for e in sc.get("eet", []))
        pd = sprite("paard", 470); hoek = -9 * abs(math.sin((t - 0) * 9)) if hap else 0   # hoofd omlaag = happen
        if hoek: pd = pd.rotate(hoek, resample=Image.BICUBIC, expand=True, center=(0, pd.height))
        img.paste(pd, (int(1100 - sprite("paard", 470).width / 2), int(985 - pd.height)), pd)
        if sc.get("eet") and t >= sc["eet"][2] + 0.9: WACHT.plaats("deurmat", (1330, 650, 1500, 740), op="bek", punt=(1385, 652)); mat(img, True)
    if sc.get("games") is not None and t >= sc["games"]: WACHT.plaats("spellen", (1440, 500, 1640, 980), op="vloer"); games(img, t, sc["games"])
    if sc.get("vol"):                                    # straat vol: 7 auto's, boot, (paard), vuilnis
        zet(img, "sportwagen", 230, 480, 975, op="weg"); zet(img, "boot", 300, 1180, 990, op="weg")
    if sc.get("vuil") is not None and t >= sc["vuil"]:
        hoog = 150 + min(1, (t - sc["vuil"]) / 3) * 230
        if sc.get("wasbeer") is not None and t >= sc["wasbeer"] - 3: hoog = 380 + min(1, (t - sc["wasbeer"] + 3) / 2) * 120   # hoger dan de boot
        zet(img, "vuilniszakken", int(hoog), 1720, 760, op="stoep"); sc["_vuiltop"] = 760 - hoog
    if sc.get("paard_straat") is not None and t >= sc["paard_straat"]: zet(img, "paard", 330, 1050, 985, op="weg")
    if sc.get("tv") is not None: WACHT.plaats("tv", (724, 79, 1356, 481), op="muur"); tv(img, t, sc["tv"], None)
    if sc.get("prijs"): WACHT.plaats("melkpak", (980, 470, 1090, 710), op="plank-4"); WACHT.plaats("prijskaartje", (950, 712, 1130, 800), op="aan:plankrand"); prijsbord(img, t, sc["prijs"])
    if sc.get("leeg"):
        for gr, t0 in enumerate(sc["leeg"]):
            if t >= t0: leeg_schap(img, gr)
    if sc.get("sheet") and t >= sc["sheet"][0][0]: WACHT.plaats("spreadsheetbord", (150, 330, 750, 970), op="vloer")
    if sc.get("sheet"): sheet(img, t, sc["sheet"])
    if sc.get("tand"):
        WACHT.plaats("deur", (60, 300, 330, 960), op="vloer"); ts_ = sc["tand"][2]; deur(img, t < ts_)
    if sc.get("kippen") is not None and t >= sc["kippen"]:
        for k, xx in enumerate((1640, 1745, 1850) if sc.get("tafelx") else (300, 420, 1390, 1500, 1610, 1720)): zet(img, "kip", 110, xx, 1000 - (k % 2) * 10 + 6 * math.sin(t * 6 + k), op="vloer", spiegel=k % 2 == 1)
    if sc.get("minibord") is not None and t >= sc["minibord"]:
        dd = ImageDraw.Draw(img)
        for cx_, cy_, w_, tf in ((330, 648, 110, "tafel-links"), (550, 596, 80, "tafel-achter-links"), (1430, 596, 80, "tafel-achter-rechts")):
            WACHT.plaats("minibord", (cx_ - w_, cy_ - 16, cx_ + w_, cy_ + 16), op=tf)
            dd.ellipse((cx_ - w_, cy_ - w_ * 0.22, cx_ + w_, cy_ + w_ * 0.22), fill=(252, 252, 252), outline=INK, width=3)
            dd.ellipse((cx_ - 7, cy_ - 6, cx_ + 7, cy_ + 3), fill=(120, 170, 90), outline=INK, width=2)
    if sc.get("raampaard") is not None and t >= sc["raampaard"]: WACHT.plaats("paard achter het raam", (735, 300, 1060, 515), op="aan:raam"); raampaard(img, t, sc["raampaard"])
    if sc.get("hout") is not None and t >= sc["hout"]: WACHT.plaats("brandhout", (1300, 918, 1550, 1062), op="vloer"); brandhout(img)
    if sc.get("router"):
        WACHT.plaats("router", (1065, 467, 1205, 572), op="aanrecht"); WACHT.plaats("keuken-tv", (330, 470, 550, 612), op="aanrecht-links")
        router(img, t, sc["router"])
    if thuis:
        zet(img, "gamestoel", 560, 820, 980, op="vloer"); games(img, 99, 0)
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); koppen = {}; GEZ.clear()
    sp = next((p for p in sc["pop"] if p["n"] == spreker), None)
    pops = [dict(n="you", x=1180, s=1.8, geb="vast")] if thuis else sc["pop"]; vast = []; koppen_x = {}
    for p in pops:
        x = p["x"]; loop = None
        if "loop" in p:
            a, b, x0, x1 = p["loop"]
            if t < a and x0 < -100: continue
            f = ps.ease((t - a) / max(0.1, b - a)); x = x0 + (x1 - x0) * f
            if a <= t < b: loop = (t - a) * 2.2
        if sp is not None and p is not sp: kijk = 0.9 if sp["x"] > x else -0.9
        else: kijk = 0.5 if x < 960 else -0.5
        geb = p.get("geb")
        if sc.get("slot") and t >= sc["slot"][0]: geb = "vast"
        if sc.get("kijk") is not None and t >= sc["kijk"]: kijk = 1.0 if x < 1200 else -1.0          # iedereen kijkt naar iemand anders
        if sc.get("banaan") and p["n"] == "mom" and sc["banaan"][0] <= t < sc["banaan"][1]: geb = "vast"
        if sc.get("oma_pad") and p["n"] == "oma" and t >= sc["oma_pad"][0][0]:
            pad = sc["oma_pad"]; x = pad[-1][1]
            for (ta, xa), (tb, xb) in zip(pad, pad[1:]):
                if ta <= t < tb:
                    x = xa + (xb - xa) * ps.ease((t - ta) / max(0.1, tb - ta))
                    if xa != xb: loop = (t - ta) * 2.2
                    break
            kijk = 0.9 if t < sc["oma_hand"][1] else -0.9
        if sc.get("oma_hand") and p["n"] == "oma":
            h0, h1 = sc["oma_hand"]
            if h0 <= t < h1: geb = "wijs"
            elif h1 <= t < sc["tand"][2]: geb = "wijslinks"
            if h0 <= t < sc["tand"][2]: loop = None if loop is None else loop
        if nu is not None:
            for s_, wie in NACTIE.items():
                if wie and tekst_nu.startswith(s_) and p["n"] == wie[0]: geb = wie[1]
        if sc.get("praten") is not None and sc["praten"] <= t < sc["praten"] + 3.0 and sp is None:
            geb = "praat"; kijk = 0.9 if (hash(p["n"]) + int(t)) % 2 else -0.9          # iedereen praat met elkaar
        if sp is p and nu is not None:
            geb = next((g for s_, g in ACTIE.items() if tekst_nu.startswith(s_)), geb)
        if geb == "praat" and not (sc.get("praten") is not None and sc["praten"] <= t < sc["praten"] + 3.0):
            LAYOUT.add(f"armgebaar 'praat' bij gewoon praten ({p['n']}, {t:.1f} s): weghalen")
        if sc.get("lopers") is not None and sc["lopers"] <= t < sc["lopers"] + 2.5: loop = t * 1.6; x = x - 120 * ((t - sc["lopers"]) / 2.5)
        if loop is not None and not (p["n"] == "oma" and geb in ("wijs", "wijslinks")): geb = "rennen"   # oma houdt het touw vast tijdens het lopen
        verb = any(w in tekst_nu for w in VERBAASD) and p["n"] in ("you", "dad", "mom", "sis"); boos_ = False
        emo = emotie(t, nu) if p["n"] in ("you", "dad", "mom", "sis", "teach", "kassa") else None
        if emo == "schrik": verb, boos_ = True, False
        elif emo == "verdriet": verb, boos_ = False, True
        elif emo == "blij": verb, boos_ = False, False
        telefoon_ = geb == "vast" and not (sc.get("banaan") and p["n"] == "mom")
        if nu is not None and tekst_nu.startswith("I can't charge") and p["n"] == "you": geb = "vast"; telefoon_ = True
        knip = (t + hash(p["n"]) % 7 * 0.4) % 3.4 < 0.13
        koppen[p["n"]] = ps.poppetje(d, p["n"], x, p.get("y", 960), p["s"], t, loop=loop, kijk=kijk, mond=luid(t, p["n"]), knipper=knip, verbaasd=verb, gebaar="telefoon" if telefoon_ else geb, boos=boos_)
        koppen_x[p["n"]] = x; GEZ[p["n"]] = (*koppen[p["n"]], p["s"] * ps.C[p["n"]].get("groot", 1))
        if telefoon_: vast.append(hand(p["n"], x, p.get("y", 960), p["s"], hoek=-32))
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    for hx, hy, S in vast: WACHT.plaats("telefoon in de hand", (hx - 14 * S, hy - 38 * S, hx + 14 * S, hy + 8 * S), op="aan:hand"); telefoontje(img, hx, hy, S, t)
    global NAAM_GETOOND; NAAM_GETOOND = False
    if NAAMLABELS and nu is not None and Z[nu][4] in NAAM and spreker in koppen:      # label boven het hoofd (eigenaar 25 nov: uit)
        hx_, hy_ = koppen[spreker]; extra_ = 0
        if spreker == "dad" and sc.get("muts") is not None and t >= sc["muts"]: extra_ = 150
        if spreker == "boss" and sc.get("kroon"): extra_ = 95
        dd = ImageDraw.Draw(img); fn = font(FB, 30); n_ = NAAM[Z[nu][4]]; nb = dd.textlength(n_, font=fn); yy = hy_ - 30 - extra_
        actief = [(y_, m_) for st_, s_, x_, y_, m_, kl_ in sc["kop"] if t >= st_]
        if any(abs((yy - 22) - y_) < m_ * 0.7 + 30 for y_, m_ in actief):   # botst met een kop -> label rechts naast het hoofd
            R_ = 60 * GEZ[spreker][2]; hx_ = hx_ + R_ + nb / 2 + 26; yy = hy_ + R_ * 0.55
        dd.rounded_rectangle((hx_ - nb / 2 - 14, yy - 42, hx_ + nb / 2 + 14, yy - 2), 10, fill=(120, 80, 220)); dd.text((hx_ - nb / 2, yy - 40), n_, font=fn, fill=(255, 255, 255))
        dd.polygon([(hx_ - 10, yy - 3), (hx_ + 10, yy - 3), (hx_, yy + 10)], fill=(120, 80, 220))
        NAAM_GETOOND = True
    if sc["naam"] == "klas" and not thuis:                # jij zit achter je bureau (ook als de juf terug is: huiswerk komt erop)
        if sc.get("zon") is None: tafel(img)
        else: tafel(img, 480, 1000)
    if sc.get("keukentafel"):
        kx0, kx1 = sc.get("tafelx", (380, 1600))
        WACHT.plaats("keukentafel", (kx0, 820, kx1, 1010), op="vloer"); keukentafel(img, kx0, kx1); WACHT.vlak("keukentafel", [kx0, kx1, 815, 850])
        if sc.get("brood_t") is not None and t >= sc["brood_t"]: zet(img, "brood", 85, 700, 826, op="keukentafel", voor=True)
    if sc.get("spel") is not None and t >= sc["spel"]: WACHT.plaats("spelbord", (600, 752, 1000, 820), op="keukentafel", voor=True); spelbord(img)
    if sc.get("kaars") is not None and t >= sc["kaars"]: WACHT.plaats("kaars", (1268, 715, 1292, 820), op="keukentafel", voor=True); kaars(img, t, 1280, 820)
    if sc.get("middernacht") is not None and t >= sc["middernacht"]: img = nacht_ramen(img, t, sc["middernacht"])
    if sc.get("donker") is not None:
        img = donker(img, t, sc["donker"])
        if sc.get("kaars") is not None and t >= sc["kaars"]: img = gloed(img, 1280, 760)
    if sc.get("accu") is not None: accu(img, t, sc["accu"])
    if sc.get("muts") is not None and t >= sc["muts"] and "dad" in koppen:
        mx_, my_ = koppen["dad"][0], koppen["dad"][1] + 8; WACHT.plaats("koksmuts", (mx_ - 80, my_ - 150, mx_ + 80, my_ + 8), op="aan:hoofd"); chefmuts(img, mx_, my_, 1.55)
    if sc.get("rook") is not None: rook(img, t, sc["rook"])
    if sc.get("cereal") is not None and t >= sc["cereal"]: WACHT.plaats("bord", (1640, 650, 1804, 690), op="tafel-rechts", voor=True)
    if sc.get("cereal") is not None: cereal(img, t, sc["cereal"])
    if sc.get("biljet") is not None: biljet(img, t, sc["biljet"])
    if sc.get("wasbeer") is not None and t >= sc["wasbeer"]: WACHT.plaats("wasberen", (1460, SC_NU.get("_vuiltop", 330) - 50, 1800, SC_NU.get("_vuiltop", 330) + 110), op="aan:vuilniszakken")
    if sc.get("wasbeer") is not None: wasberen(img, t, sc["wasbeer"])
    if sc.get("fooi") is not None and t >= sc["fooi"]: WACHT.plaats("fooi", (1455, 648, 1605, 696), op="tafel-rechts", voor=True)
    if sc.get("fooi") is not None: fooi(img, t, sc["fooi"])
    if sc.get("huiswerk") is not None and t >= sc["huiswerk"]:
        hw = WACHT.plaats("huiswerk", (784, 590, 976, 818), op="schoolbureau", voor=True); huiswerk(img, t, sc["huiswerk"], *hw)
    if sc.get("tand") and "dad" in koppen:
        t_in, t_touw, t_slam = sc["tand"]; hx, hy = koppen["dad"]; S = 1.6 * ps.C["dad"].get("groot", 1)
        if t < t_slam + 0.1: wang(img, hx, hy, S, t)
        mx, my = hx + 60 * S * 0.08, hy + 60 * S * 1.47       # mond
        if t_touw <= t < t_slam and "oma" in koppen_x:
            So = 1.6 * ps.C["oma"].get("groot", 1); ox = koppen_x["oma"]; sch_o = 960 - 92 * So - 83 * So
            rechts_ = t < sc["oma_hand"][1]
            ex, ey = ox + (125 if rechts_ else -125) * So, sch_o - 14 * So
            dd = ImageDraw.Draw(img); dd.line((mx, my, ex, ey), fill=(250, 250, 250), width=4)
            dd.ellipse((mx - 6, my - 6, mx + 6, my + 6), fill=(250, 250, 250), outline=INK)            # knoopje aan de tand
        if t_slam <= t < t_slam + 0.8:
            f = (t - t_slam) / 0.8; tx_, ty_ = mx + (300 - mx) * f, my - 260 * math.sin(math.pi * f)
            WACHT.plaats("tand", (tx_ - 26, ty_ - 32, tx_ + 26, ty_ + 24), op="aan:touw"); tandje(img, tx_, ty_)
    if sc.get("broodje") is not None and t >= sc["broodje"]: zet(img, "brood", 95, 1600, 845, op="hand:oma", voor=True)
    if sc.get("kassabel") is not None and sc["kassabel"] <= t < sc["kassabel"] + 2.2 and "kassa" in koppen:
        ballon(img, koppen["kassa"][0] + 170, koppen["kassa"][1] - 20, "$90", ps.pop((t - sc["kassabel"]) / 0.3))
    if sc.get("bel"):
        for t0, tekst in sc["bel"]:
            if t0 <= t < t0 + 1.3 and "dad" in koppen: ballon(img, koppen["dad"][0] + 260, koppen["dad"][1] - 40, tekst, ps.pop((t - t0) / 0.3))
    if sc.get("router"): vonk(img, t, sc.get("kapot", 1e9))
    if sc.get("banaan") and "mom" in koppen:
        t_pak, t_terug, _ = sc["banaan"]
        if t_pak <= t < t_terug: hx, hy, S = hand("mom", koppen_x["mom"], 960, 1.7); WACHT.plaats("banaan", (hx - 40, hy - 60, hx + 40, hy + 20), op="hand:mom", punt=(hx, hy), voor=True); banaan(img, hx, hy, 1.0)
        elif t < t_pak or t >= t_terug: WACHT.plaats("banaan", (843, 664, 957, 708), op="plank-4"); banaan(img, 900, 722, 1.1)
    if sc.get("zon") is not None and t >= sc["zon"] and "teach" in koppen: zonnebrand(img, koppen["teach"][0], koppen["teach"][1], 1.6)
    if sc.get("kokos") is not None and t >= sc["kokos"] and "teach" in koppen:
        St = 1.6 * ps.C["teach"].get("groot", 1); lx = koppen_x["teach"] - 44 * St - math.sin(math.radians(16)) * 82 * St   # linkerhand
        ly = 960 - 92 * St - 83 * St + math.cos(math.radians(16)) * 82 * St
        WACHT.plaats("kokosnoot", (lx - 50, ly - 60, lx + 50, ly + 40), op="hand:teach", punt=(lx, ly), voor=True); kokosnoot(img, lx, ly - 10, 1.2)
    if sc.get("slot"):
        t_bz, t_msg, i3, t_con = sc["slot"]
        if t >= t_msg: telefoon_bericht(img, t, [("Thanks for testing.", "n"), ("Round two starts tomorrow.", "n"), ("This time, only one person gets the money.", "n")] + ([("Congratulations.", "groot")] if t >= t_con else []))
    if sc.get("inbox") is not None and t >= sc["inbox"]:           # inbox op het linker beeldscherm
        WACHT.plaats("computerscherm met 240 e-mails", (280, 375, 505, 525), op="aan:bureau")
        dd = ImageDraw.Draw(img); dd.rectangle((292, 398, 482, 512), fill=(245, 248, 252))
        for k in range(4): dd.rectangle((302, 410 + k * 24, 470, 424 + k * 24), fill=(200, 210, 230))
        dd.ellipse((440, 380, 500, 430), fill=(220, 40, 40), outline=INK, width=3); dd.text((448, 390), "240", font=font(FB, 24), fill=(255, 255, 255))
    if sc.get("kroon") and "boss" in koppen:
        WACHT.plaats("kroon", (koppen["boss"][0] - 70, koppen["boss"][1] - 90, koppen["boss"][0] + 70, koppen["boss"][1] + 15), op="aan:hoofd"); kroon(img, koppen["boss"][0], koppen["boss"][1], 1.7)
    if sc.get("telefoon"): WACHT.plaats("bank-app", (1100, 110, 1600, 900), op="beeld"); telefoon(img, t)
    if sc.get("briefje") is not None and t >= sc["briefje"]: WACHT.plaats("briefje", (780, 345, 1140, 595), op="aan:deur", punt=(960, 470))
    if sc.get("briefje") is not None: briefje(img, t, sc["briefje"])
    WACHT.einde({n_: (hx_, hy_ + 60 * S_, 60 * S_) for n_, (hx_, hy_, S_) in GEZ.items()})
    # rustige push-in per scène (camera), geen effect bij de wissel zelf
    f = 1 + 0.06 * ps.ease((t - sc["t"]) / max(1.0, sc["eind"] - sc["t"]))
    if f > 1.001 and ZOOM_AAN:
        cw, ch = W / f, H / f; img = img.crop((int((W - cw) / 2), int((H - ch) * 0.45), int((W + cw) / 2), int((H - ch) * 0.45 + ch))).resize((W, H), Image.BICUBIC)
    # koppen NA de zoom: blijven scherp en vallen nooit buiten beeld
    if thuis and TEKST_AAN: kop(img, "9 HOURS LATER", 960, 120, 84, KL["geel"], ps.pop((t - sc["thuis"]) / 0.3))
    for st, s, x, y, m, kl in [] if not TEKST_AAN else ([] if sc.get("slot") and t >= sc["slot"][1] else sc["kop"]):
        later = [st2 for st2, s2, x2, y2, *_ in sc["kop"] if (x2, y2) == (x, y) and st2 > st]
        if t >= st and not (later and t >= min(later)): kop(img, s, x, y, m, KL[kl], ps.pop((t - st) / 0.3))
    if TEKST_AAN: ondertitel(img, t)
    return img

# ---------- geluidseffecten (zelf gemaakt, geen muziek) ----------
def geluid():
    rng = np.random.default_rng(5); uit = np.zeros(int((EIND + 1) * SR), np.float32)
    def tt(d): return np.arange(int(d * SR)) / SR
    def leg(x, t, v):
        i = int(t * SR); n = min(len(x), len(uit) - i)
        if n > 0 and i >= 0: uit[i:i + n] += v * x[:n].astype(np.float32)
    x = tt(0.45); bzz = np.sign(np.sin(2 * np.pi * 150 * x)) * 0.3 * (np.sin(2 * np.pi * 8 * x) > 0)
    x = tt(1.2); kaching = sum(np.sin(2 * np.pi * f * (x - o)) * (x > o) * np.exp(-np.maximum(0, x - o) * 5) for f, o in [(1319, 0), (1760, 0.08), (2637, 0.16)]) * 0.4 + rng.normal(0, 1, len(x)) * np.exp(-x * 40) * 0.3
    x = tt(1.4); vroem = np.sin(2 * np.pi * np.cumsum(60 + 90 * x / 1.4 + 8 * np.sin(2 * np.pi * 30 * x)) / SR) * np.minimum(1, x * 3) * np.exp(-np.maximum(0, x - 1.0) * 6) * 0.6
    x = tt(0.25); plof = np.sin(2 * np.pi * (90 - 60 * x) * x) * np.exp(-x * 18)
    x = tt(0.3); papier = np.convolve(rng.normal(0, 1, len(x)), np.ones(6) / 6, "same") * np.exp(-x * 12) * 0.6
    x = tt(0.9); tingel = sum(np.sin(2 * np.pi * f * (x - o)) * (x > o) * np.exp(-np.maximum(0, x - o) * 6) for f, o in [(1568, 0), (2093, 0.12)]) * 0.35
    x = tt(0.18); stap = np.sin(2 * np.pi * 110 * x) * np.exp(-x * 30) * 0.5
    x = tt(0.06); klik = rng.normal(0, 1, len(x)) * np.exp(-x * 90) + np.sin(2 * np.pi * 1200 * x) * np.exp(-x * 80)
    x = tt(0.7); knetter = rng.normal(0, 1, len(x)) * (rng.random(len(x)) > 0.93) * np.exp(-x * 3)
    x = tt(0.18); piep = np.sin(2 * np.pi * 3100 * x) * 0.5
    x = tt(0.8); uitgaan = np.sin(2 * np.pi * np.cumsum(220 - 180 * x / 0.8) / SR) * np.exp(-x * 3) * 0.6
    x = tt(0.6); klap = np.sin(2 * np.pi * 70 * x * (1 - 0.4 * x)) * np.exp(-x * 9) + rng.normal(0, 1, len(x)) * np.exp(-x * 35) * 0.6
    x = tt(0.25); tok = np.sin(2 * np.pi * (700 + 300 * np.sin(2 * np.pi * 14 * x)) * x) * np.exp(-x * 14) * 0.4
    x = tt(0.4); stempel = np.sin(2 * np.pi * 85 * x) * np.exp(-x * 14) + rng.normal(0, 1, len(x)) * np.exp(-x * 35) * 0.5
    # 25 nov (eigenaar keurde de Short met ECHTE geluiden goed): zelfde soort CC0-opnames uit ../geluiden (bron in gekozen.json)
    def echt(n, dur=None):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(HIER.parent / "geluiden" / f"{n}.mp3"), "-ac", "1", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.float32).copy(); x /= (np.abs(x).max() + 1e-6)
        if dur:
            m_ = min(len(x) - 1, int(dur * SR)); e = np.convolve(x ** 2, np.ones(SR // 10), "same")
            b_ = max(range(0, max(1, len(x) - m_), SR // 20), key=lambda i: e[i:i + m_].sum()); x = x[b_:b_ + m_]
        k_ = min(len(x) // 3, int(0.04 * SR)); x[:k_] *= np.linspace(0, 1, k_); x[-k_:] *= np.linspace(1, 0, k_); return x
    bzz, kaching, stap, vroem = echt("trillen", 0.45) * 0.7, echt("kassa"), echt("stappen", 0.25) * 0.7, echt("auto", 1.4)
    plof, papier, tingel, klik = echt("plof"), echt("papier-ritsel", 0.5), echt("ting", 0.9) * 0.7, echt("klik")
    knetter, uitgaan, klap, tok = echt("vonken", 0.7), echt("stroom-uit", 1.4), echt("deur-dicht"), echt("kip", 0.7) * 0.8
    stempel, hap_ = echt("stempel"), echt("paard-eet", 0.9)
    piep = echt("rookmelder", 0.6) * 0.6
    for j in range(3): leg(bzz, 0.05 + j * 0.6, 0.5)
    i1 = zi("It's 6 a.m."); leg(bzz, Z[i1][0] + 0.2, 0.5); leg(bzz, Z[i1][0] + 0.8, 0.5)
    leg(kaching, T_SALDO + 0.25, 0.7)
    for s in SC:
        if s["naam"] == "keuken" or "loop" in str(s["pop"]):
            for p in s["pop"]:
                if "loop" in p:
                    a, b = p["loop"][:2]
                    for q in np.arange(a, b, 0.22): leg(stap, q, 0.5)
        if s.get("auto") is not None: leg(vroem, s["auto"], 0.8)
        if s.get("drie") is not None: [leg(plof, s["drie"] + j * 0.25, 0.6) for j in range(3)]
        if s.get("boot") is not None: leg(plof, s["boot"], 0.9)
        if s.get("briefje") is not None: leg(papier, s["briefje"], 0.8)
        if s.get("kroon"): leg(tingel, s["t"] + 0.3, 0.5)
        for e in s.get("eet", []): leg(hap_, e + 0.1, 0.9)                     # echt paard dat kauwt
        if s.get("eet"): leg(echt("slok", 0.7), s["eet"][-1] + 1.1, 0.8)         # en een slok na de deurmat (grapje, net als in de Short)
        if s.get("vuil") is not None: [leg(plof, s["vuil"] + 0.5 + j * 0.4, 0.5) for j in range(6)]
        if s.get("tv") is not None: leg(klik, s["tv"], 0.8)
        for t0, tekst in s.get("bel", []): leg(klik if tekst.startswith("*") else bzz, t0, 0.6)
        if s.get("router"): [leg(klik, q, 0.8) for q in s["router"]]
        if s.get("kapot") is not None: leg(knetter, s["kapot"], 0.7)
        for t0, pr in s.get("prijs", []): leg(kaching, t0, 0.45)
        if s.get("muts") is not None: leg(plof, s["muts"], 0.6)
        if s.get("rook") is not None: [leg(piep, s["rook"] + q * 0.66, 0.5) for q in range(5)]
        if s.get("biljet") is not None: leg(papier, s["biljet"], 0.9)
        if s.get("donker") is not None: leg(uitgaan, s["donker"] - 0.1, 0.8)
        if s.get("kaars") is not None: leg(klik, s["kaars"], 0.5)
        if s.get("tand"): leg(klap, s["tand"][2], 1.0)
        if s.get("kippen") is not None: [leg(tok, s["kippen"] + q * 0.7, 0.5) for q in range(4)]
        if s.get("slot"): [leg(bzz, s["slot"][0] + q * 0.6, 0.6) for q in range(3)]; leg(bzz, s["slot"][3], 0.7)
        for st, tx, *_ in s["kop"]:
            if "SOLD OUT" in tx or "QUIT" in tx or "BROKEN" in tx or "GONE" in tx or "FIREWOOD" in tx: leg(stempel, st, 0.6)
    uit /= max(1, np.abs(uit).max() / 0.9)
    sf.write(HIER / "sfx.wav", uit, SR)

if __name__ == "__main__":
    if "--plaat" in sys.argv:
        ims = [frame(min(EIND - 0.3, z[0] + 0.8 * (z[1] - z[0]))).resize((400, 225)) for z in Z]
        for v in range(0, len(ims), 24):
            pl = Image.new("RGB", (400 * 6, 225 * 4))
            for i, im in enumerate(ims[v:v + 24]): pl.paste(im, (400 * (i % 6), 225 * (i // 6)))
            pl.save(HIER / f"plaat-{v // 24}.jpg", quality=80)
        print("platen", (len(ims) + 23) // 24); print("LAYOUT:", sorted(LAYOUT) or "alles past")
        print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); sys.exit()
    geluid()
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-i", str(HIER / "stem.wav"), "-i", str(HIER / "sfx.wav"), "-filter_complex",
                          "[1:a]apad[v];[2:a]volume=0.45[k];[v][k]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]",
                          "-map", "0:v", "-map", "[a]", "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                          "-t", f"{EIND:.2f}", str(HIER / "miljoen.mp4")], stdin=subprocess.PIPE)
    for i in range(int(EIND * FPS)):
        p.stdin.write(frame(i / FPS).tobytes())
        if i % (FPS * 20) == 0: print(f"{i / FPS:.0f} / {EIND:.0f} s", flush=True)
    p.stdin.close(); p.wait(); print("LAYOUT:", sorted(LAYOUT) or "alles past")
    print("SCENEWACHTER:", WACHT.schrijf(HIER / "SCENEWACHTER.md"), "fouten (zie SCENEWACHTER.md)"); print("KLAAR miljoen.mp4", round(EIND, 1), "s")
