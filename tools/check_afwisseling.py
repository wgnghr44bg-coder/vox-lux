"""Klinkt deze video niet hetzelfde als de vorige? (eigenaar 8 nov 2026: "zorgen dat de opbouw goed blijft maar niet
alles hetzelfde klinkt").

Vergelijkt begin.txt, slot.txt en de BRIDGE-zinnen van <map> met die van alle andere video's (stories/*/src-feiten of
src/ met begin.txt) en meldt zinnen die te veel lijken (gelijkenis >= 0,75). Kijkt ook of `opening` en `titelsoort` in
planning.txt anders zijn dan bij de video met de datum ervoor.

Gebruik: python tools/check_afwisseling.py stories/<map>     -> AFWISSELING GOED of AFWISSELING FOUT (+ welke zinnen)
"""
import difflib, re, sys
from pathlib import Path

STORIES = Path(__file__).resolve().parent.parent / "stories"


def bron(m):
    for s in ("src-feiten", "src"):
        if (m / s / "begin.txt").exists():
            return m / s
    return None


def zinnen(m):
    s = bron(m)
    if not s:
        return []
    tekst = (s / "begin.txt").read_text(encoding="utf-8") + "\n" + \
        ((s / "slot.txt").read_text(encoding="utf-8") if (s / "slot.txt").exists() else "")
    for p in s.glob("deel*.txt"):
        tekst += "\n" + "\n".join(re.findall(r"^BRIDGE:\s*(.+)$", p.read_text(encoding="utf-8"), re.M))
    uit = []
    for z in re.split(r"(?<=[.!?])\s+", " ".join(tekst.split())):
        z = z.strip()
        if len(z.split()) >= 6 and not z.startswith("Sleep well, and good night"):   # de slotzin is bewust altijd gelijk
            uit.append(z)
    return uit


def planning(m):
    p = m / "planning.txt"
    t = p.read_text(encoding="utf-8") if p.exists() else ""
    g = lambda k: (re.search(rf"^{k}\s+(\S+)", t, re.M) or [None, None])[1]
    return {"datum": (re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M) or [None, ""])[1],
            "opening": g("opening"), "titelsoort": g("titelsoort")}


m = Path(sys.argv[1]).resolve()
fout = []
eigen = zinnen(m)
if not eigen:
    sys.exit(f"geen begin.txt in {m}")
norm = lambda z: re.sub(r"[^a-z ]", "", z.lower())
for ander in sorted(STORIES.iterdir()):
    if ander == m or not ander.is_dir():
        continue
    for z in eigen:
        for y in zinnen(ander):
            r = difflib.SequenceMatcher(None, norm(z), norm(y)).ratio()
            if r >= 0.75:
                fout.append(f"lijkt op {ander.name} ({r:.2f}): \"{z}\"  ~  \"{y}\"")
pl = planning(m)
vorige = sorted(((planning(a)["datum"], a.name, planning(a)) for a in STORIES.iterdir()
                 if a.is_dir() and a != m and planning(a)["datum"] and planning(a)["datum"] < (pl["datum"] or "9999")),
                key=lambda x: x[0])
if vorige:
    d, naam, v = vorige[-1]
    for k in ("opening", "titelsoort"):
        if pl[k] and pl[k] == v[k]:
            fout.append(f"{k} '{pl[k]}' is hetzelfde als de vorige video ({naam}, {d})")
for f in fout:
    print(f)
print("AFWISSELING FOUT: herschrijf deze zinnen anders" if fout else "AFWISSELING GOED")
sys.exit(1 if fout else 0)
