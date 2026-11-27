"""Oude Market Doodle-figuren als plaatjes voor de 3D-haai (eigenaar 27 nov: "kun je de personage meer in de oude style").
Mensen: pop_short.poppetje (zelfde tekening als de 2D-shorts), per gebaar / schrik / knipper / mondvorm (lipsync) / loopfase.
Haai: het oude haai-plaatje uit short-haai met de oude grijze benen en rode sneakers, per loopfase en oogstand.
Schrijft public/oud/*.png; de 3D-wereld laadt ze in."""
import math, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

HIER = Path(__file__).resolve().parent
MD = HIER.parent.parent
sys.path.insert(0, str(MD / "proef-pop-short"))
import types, os, json, tempfile, numpy as np
_sf = types.ModuleType("soundfile"); _sf.read = lambda *a, **k: (np.zeros(10, np.float32), 24000); sys.modules.setdefault("soundfile", _sf)
_tmp = Path(tempfile.mkdtemp()); (_tmp / "proef-whatif2").mkdir(); (_tmp / "a").mkdir()
_z = json.load(open(MD / "short-haai" / "zinnen.json", encoding="utf-8")) * 3
(_tmp / "proef-whatif2" / "zinnen.json").write_text(json.dumps(_z)); (_tmp / "proef-whatif2" / "woorden.json").write_text("[]")
_cwd = os.getcwd(); os.chdir(_tmp / "a")
import pop_short as ps
os.chdir(_cwd)

UIT = HIER / "public" / "oud"; UIT.mkdir(parents=True, exist_ok=True)
SS = ps.SS
CW, CH, FX, FY, S = 500, 780, 250, 750, 2.0          # doek, voetpunt, schaal
VIS = [None, "A", "E", "O", "U", "M", "F", "L"]
ps.BEWEGEN = False; ps.LEVENDIG = False


def mens(naam, gebaar=None, verb=False, kn=False, vis=None, loop=None, t=0.0, boos=False):
    im = Image.new("RGBA", (CW * SS, CH * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    ps.poppetje(d, naam, FX, FY, S, t, loop=loop, mond=0.8 if vis else 0.0, knipper=kn, verbaasd=verb, gebaar=gebaar if loop is None else "rennen",
                boos=boos, viseem=vis, bewegen=False)
    return im.resize((CW, CH), Image.LANCZOS)


NAMEN = []
def sla(im, naam):
    im.save(UIT / f"{naam}.png", optimize=True); NAMEN.append(naam)


n = 0
ROLLEN = {"you": ["none", "zwaai0", "zwaai1", "zwaai2", "zwaai3", "schrik", "hoofdhanden"],
          "sis": ["none", "juich0", "juich1"],
          "dad": ["none", "hoofdhanden", "armen-open"],
          "friend": ["none"], "rich": ["none"]}
for naam, gebs in ROLLEN.items():
    praat = naam in ("you", "sis", "dad")
    for g in gebs:
        geb = None if g == "none" else g.rstrip("0123456789"); t = int(g[-1]) * 0.07 if g[-1].isdigit() else 0.0
        for verb in (0, 1):
            for vis in (VIS if praat else [None]):
                sla(mens(naam, geb, bool(verb), False, vis, t=t), f"{naam}_{g}_{verb}_0_{vis or 'x'}"); n += 1
            sla(mens(naam, geb, bool(verb), True, None, t=t), f"{naam}_{g}_{verb}_1_x"); n += 1
    if naam in ("sis", "friend", "rich"):                                   # lopen / rennen
        for i in range(16):
            for verb in (0, 1):
                sla(mens(naam, None, bool(verb), False, None, loop=i / 8), f"{naam}_loop{i}_{verb}"); n += 1

# ---------------- de oude haai ----------------
def los(im, tol=30):
    im = im.convert("RGB"); w, h = im.size; m = im.copy()
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(m, p, (255, 0, 255), thresh=tol)
    a = Image.eval(ImageChops.difference(m, Image.new("RGB", m.size, (255, 0, 255))).convert("L"), lambda v: 255 if v > 8 else 0)
    out = im.convert("RGBA"); out.putalpha(a); return out.crop(a.getbbox()), a.getbbox()

bron = Image.open(MD / "short-haai" / "afbeeldingen" / "haai.png")
lijf, box = los(bron)
L = 1000; lijf = lijf.resize((L, int(lijf.height * L / lijf.width)), Image.LANCZOS); hs = lijf.height
k = L / (box[2] - box[0])
oog = (835, 167)                                        # oog in het geschaalde haai-plaatje (nagemeten)
m = L / 2.0                                             # px per meter (haai = 2 m, zoals HAAI_L)
INK = (45, 38, 40)
been = 0.85 * m; top = 20; voet = int(top + 0.74 * hs + been)
HW, HH = L + 40, voet + 30
print("haai", HW, HH, "voet", voet, "oog", oog)


def haai(loop, oogstand, rechts=True):
    im = Image.new("RGBA", (HW * SS, HH * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    P = lambda x, y: (x * SS, y * SS)
    bob = abs(math.sin(loop * math.pi)) * 0.04 * m if loop is not None else 0
    t0 = top + 0.0 - bob; x0 = 20
    dik = max(6, int(0.17 * m)); grijs = (120, 130, 145)
    for k_, fx in enumerate((0.40, 0.58)):
        hx = x0 + L * fx; hy = t0 + 0.70 * hs
        zw = math.sin((loop or 0) * math.pi + k_ * math.pi) * 0.35 if loop is not None else 0
        vx, vy = hx + math.sin(zw) * been, hy + math.cos(zw) * been
        d.line((*P(hx, hy), *P(vx, vy)), fill=INK, width=(dik + 8) * SS); d.line((*P(hx, hy), *P(vx, vy)), fill=grijs, width=dik * SS)
        sw_ = 0.30 * m
        d.rounded_rectangle((*P(vx - 0.08 * m, vy - 0.11 * m), *P(vx + sw_, vy + 0.02 * m)), int(0.05 * m * SS), fill=(220, 50, 50), outline=INK, width=4 * SS)
        d.line((*P(vx - 0.08 * m, vy - 0.01 * m), *P(vx + sw_, vy - 0.01 * m)), fill=(255, 255, 255), width=max(3, int(0.03 * m)) * SS)
    im = im.resize((HW, HH), Image.LANCZOS)
    im.alpha_composite(lijf, (x0, int(t0)))
    d = ImageDraw.Draw(im); ox, oy = x0 + oog[0], t0 + oog[1]; r = 0.045 * L
    if oogstand == "slaap":                              # ooglid: stukje huid van net achter het oog eroverheen, dan een dichte boog
        re_ = 0.031 * L; dx = int(2.4 * re_); ox -= 2; oy += 3
        stuk = im.crop((int(ox - re_ - dx), int(oy - re_), int(ox + re_ - dx), int(oy + re_)))
        masker = Image.new("L", stuk.size, 0); ImageDraw.Draw(masker).ellipse((0, 0, stuk.size[0] - 1, stuk.size[1] - 1), fill=255)
        im.paste(stuk, (int(ox - re_), int(oy - re_)), masker); d = ImageDraw.Draw(im)
        d.arc((ox - re_ * 0.9, oy - re_ * 0.7, ox + re_ * 0.9, oy + re_ * 0.5), 15, 165, fill=INK, width=6)
    elif oogstand == "bang":
        d.ellipse((ox - r * 0.78, oy - r * 0.78, ox + r * 0.78, oy + r * 0.78), fill=(255, 255, 255), outline=INK, width=5)
        d.ellipse((ox - r * 0.3, oy - r * 0.3, ox + r * 0.3, oy + r * 0.3), fill=INK)
        d.ellipse((ox + r * 2.2, oy - r * 3.6, ox + r * 3.0, oy - r * 2.2), fill=(160, 215, 255), outline=INK, width=4)
    return im


for i in range(16):
    for o in ("gewoon", "bang"):
        sla(haai(i / 8, o), f"haai_loop{i}_{o}"); n += 1
for o in ("gewoon", "slaap", "bang"):
    sla(haai(None, o), f"haai_stil_{o}"); n += 1
(HIER / "src" / "videos" / "haai" / "oudmaat.ts").write_text(
    f"// gemaakt door maak_oude_figuren.py\nexport const HAAI_PX = {{ w: {HW}, h: {HH}, voet: {voet}, m: {m} }};\nexport const MENS_PX = {{ w: {CW}, h: {CH}, voet: {FY} }};\n", encoding="utf-8")
print("plaatjes:", n)
with open(HIER / "src" / "videos" / "haai" / "oudmaat.ts", "a", encoding="utf-8") as f:
    f.write("export const NAMEN: string[] = " + json.dumps(NAMEN) + ";\n")
