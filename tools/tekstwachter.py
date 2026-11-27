"""Tekstwachter (eigenaar 26 nov 2026: "Sommige beelden kloppen niet met de tekst, let daar a.u.b. op" en "zorg dat er een
controle op staat" – na: juichen bij "I could've been rich?!", '2026' in beeld terwijl de verteller "1999" zegt, geen chips bij
"everyone needs NVIDIA chips", geen PlayStation bij "I needed a PlayStation 2", PS2 voor het gezicht).

Kijkt PER ZIN of het beeld past bij wat er gezegd wordt:
  1. JAARTAL   noemt de zin een jaar (1999, 2002, 2000s) en staat er in beeld alleen een ánder jaar -> FOUT.
  2. SPREKER   wie praat, moet tijdens zijn zin in beeld staan (gezicht binnen de camera-uitsnede) -> anders FOUT.
  3. GEVOEL    zin met spijt/schrik/verlies terwijl de spreker juicht / duim omhoog -> FOUT;
               blije zin terwijl de spreker facepalm / handen op het hoofd doet -> FOUT.
  4. GENOEMD = GEZIEN  regels {"playstation": ["ps2"], "chips": ["videokaart-hand"], "hundred dollars": ["tekst:$100"]}:
               komt het woord in de zin voor, dan moet (één van) die voorwerpen of teksten tijdens de zin in beeld zijn -> anders FOUT.
  5. BLAD      blad(mp4, uit): per zin 3 beelden (begin/midden/eind) met de zin eronder, voor de eigen beeldcontrole.

Gebruik in een renderer (naast de scènewachter):
    TW = Tekstwachter(Z, ZIE, lijf=LIJF)                       # Z = zinnen.json [(t0, t1, tekst, scène, rol)], LIJF = rol -> poppetje
    TW.zie(t, nu, voorwerpen=[(naam, box)], teksten=[...], koppen={naam: (x, y)}, gebaren={naam: gebaar}, crop=(x0, y0, x1, y1))
    TW.schrijf(Path("TEKSTWACHTER.md"))  -> aantal fouten
"""
import re, subprocess
from pathlib import Path

SPIJT = ("could've", "could have", "lose", "lost", "sold", "why", "needed", "never", "for this", "broke", "missed", "should've")
BLIJ = ("congratulations", "fortune", "island", "retiring", "baby go", "deal", "rich!", "we did it", "yes!")
JUICH = {"juich", "zwaai", "duim", "klap"}
WEE = {"facepalm", "hoofdhanden"}

def jaren(s):
    """Alle jaartallen in een tekst als bereiken: '1999' -> (1999,1999), '2000s' -> (2000,2009), '2000 – 2005' -> (2000,2005)."""
    uit = []
    for a, b in re.findall(r"\b((?:19|20)\d\d)\s*[–-]\s*((?:19|20)\d\d)\b", s): uit.append((int(a), int(b)))
    s2 = re.sub(r"\b(?:19|20)\d\d\s*[–-]\s*(?:19|20)\d\d\b", " ", s)
    for j, s_ in re.findall(r"\b((?:19|20)\d\d)('?s)?\b", s2): uit.append((int(j), int(j) + 9) if s_ else (int(j), int(j)))
    return uit

def _naam_gebaar(g):
    return g if isinstance(g, str) else None

class Tekstwachter:
    def __init__(self, zinnen, regels=None, lijf=None):
        self.Z = zinnen; self.regels = {k.lower(): v for k, v in (regels or {}).items()}; self.lijf = lijf or {}
        self.per = {i: dict(jaren=set(), spreker_gezien=False, gebaren=[], gezien=set(), teksten=set()) for i in range(len(zinnen))}

    def zie(self, t, nu, voorwerpen=(), teksten=(), koppen=None, gebaren=None, crop=None):
        if nu is None or nu not in self.per: return
        z = self.Z[nu]
        if not (z[0] - 0.05 <= t <= z[1] + 0.05): return
        P = self.per[nu]; x0, y0, x1, y1 = crop or (0, 0, 10 ** 6, 10 ** 6)
        def binnen(b): return b[2] > x0 and b[0] < x1 and b[3] > y0 and b[1] < y1
        for naam, box in voorwerpen:
            if binnen(box): P["gezien"].add(naam)
        for s in teksten:
            P["teksten"].add(s)
            for r in jaren(s): P["jaren"].add(r)
        sp = self.lijf.get(z[4])
        for naam, (hx, hy) in (koppen or {}).items():
            if x0 <= hx <= x1 and y0 <= hy <= y1: P["gezien"].add(naam)
            if naam == sp and x0 <= hx <= x1 and y0 <= hy <= y1: P["spreker_gezien"] = True
        if sp and gebaren and sp in gebaren: P["gebaren"].append(_naam_gebaar(gebaren[sp]))

    def fouten(self):
        uit = []
        for i, z in enumerate(self.Z):
            P = self.per[i]; tekst = z[2]; laag = tekst.lower(); t = z[0]
            gezegd = jaren(tekst)
            if gezegd and P["jaren"]:
                past = any(a <= g0 and g1 <= b or a <= g0 <= b for (g0, g1) in gezegd for (a, b) in P["jaren"])
                if not past:
                    ib = ", ".join(sorted({f"{a}" if a == b else f"{a}-{b}" for a, b in P["jaren"]}))
                    uit.append((t, "jaartal", f'zegt "{tekst}" maar in beeld staat alleen {ib}'))
            sp = self.lijf.get(z[4])
            if sp and not P["spreker_gezien"]: uit.append((t, "spreker", f'{z[4]} praat ("{tekst}") maar staat niet in beeld'))
            g = [x for x in P["gebaren"] if x]
            if any(w in laag for w in SPIJT) and any(x in JUICH for x in g):
                uit.append((t, "gevoel", f'"{tekst}" is spijt/schrik, maar {z[4]} juicht ({", ".join(sorted(set(g) & JUICH))})'))
            if any(w in laag for w in BLIJ) and not any(w in laag for w in SPIJT) and any(x in WEE for x in g):
                uit.append((t, "gevoel", f'"{tekst}" is blij, maar {z[4]} doet {", ".join(sorted(set(g) & WEE))}'))
            for woord, nodig in self.regels.items():
                if woord in laag:
                    ok = any((n[6:] in " ".join(P["teksten"])) if n.startswith("tekst:") else (n in P["gezien"]) for n in nodig)
                    if not ok: uit.append((t, "genoemd", f'zegt "{woord}" maar er is geen {" / ".join(nodig)} in beeld'))
        return uit

    def schrijf(self, pad):
        f = self.fouten(); r = ["# Tekstwachter", "", f"**{len(f)} fouten** (beeld past niet bij wat er gezegd wordt).", ""]
        for t, soort, tekst in f: r.append(f"- {int(t // 60)}:{t % 60:04.1f} **FOUT** {soort}: {tekst}")
        Path(pad).write_text("\n".join(r) + "\n", encoding="utf-8"); return len(f)

def blad(mp4, zinnen, uit, breed=270, hoog=None):      # hoog: voor liggende video (bv. 400x225)
    """Overzichtsblad: per zin begin/midden/eind-beeld met de zin eronder (voor de eigen beeldcontrole)."""
    from PIL import Image, ImageDraw, ImageFont
    import io
    try: f = ImageFont.truetype("arialbd.ttf", 18)
    except OSError: f = ImageFont.load_default()
    hoog = hoog or int(breed * 16 / 9); rij = []
    for i, z in enumerate(zinnen):
        ims = []
        for tt in (z[0] + 0.3, (z[0] + z[1]) / 2, z[1] - 0.1):
            b = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{tt:.2f}", "-i", str(mp4), "-frames:v", "1", "-vf", f"scale={breed}:{hoog}",
                                "-f", "image2", "-c:v", "png", "-"], capture_output=True).stdout
            ims.append(Image.open(io.BytesIO(b)).convert("RGB") if b else Image.new("RGB", (breed, hoog)))
        cel = Image.new("RGB", (breed * 3, hoog + 70), (255, 255, 255)); [cel.paste(im, (k * breed, 0)) for k, im in enumerate(ims)]
        d = ImageDraw.Draw(cel); d.text((8, hoog + 6), f"{i}  {z[4]}  {z[0]:.1f}s", font=f, fill=(150, 0, 0))
        d.text((8, hoog + 32), z[2][:70], font=f, fill=(0, 0, 0)); rij.append(cel)
    per = 4; kol = [rij[k:k + per] for k in range(0, len(rij), per)]
    B = Image.new("RGB", (breed * 3 * per, (hoog + 70) * len(kol)), (255, 255, 255))
    for r_, cs in enumerate(kol):
        for c_, cel in enumerate(cs): B.paste(cel, (c_ * breed * 3, r_ * (hoog + 70)))
    B.save(uit, quality=80); return uit
