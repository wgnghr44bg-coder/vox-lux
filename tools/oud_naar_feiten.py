"""Oud script (stories/<map>/src/NN-*.txt met {img:slug}) omzetten naar de nieuwe opbouw (src-feiten/deel1-3.txt met
TOPIC/IMG/HEAD/BODY), zonder feiten te veranderen. Elk {img:}-stuk wordt één feitje: HEAD = eerste zin, BODY = de rest.
Begin, slot en BRIDGE-zinnen schrijf je daarna met de hand (src-feiten/begin.txt, slot.txt; BRIDGE via toon_bijwerken.py).

Gebruik: python tools/oud_naar_feiten.py stories/<map> <groepen.json>
groepen.json: [["<TOPIC-titel>", ["01-...txt", "02-...txt"]], ...]   (8-13 groepen, in volgorde)
"""
import json, re, sys
from pathlib import Path

m = Path(sys.argv[1])
groepen = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
beeld = {}
for r in (m / "src" / "beelden.tsv").read_text(encoding="utf-8").splitlines():
    if "\t" in r:
        s, p = r.split("\t", 1)
        beeld[s.strip()] = p.strip()


def zinnen(t):
    return [z for z in re.split(r"(?<=[.!?])\s+", t.strip()) if z]


blokken = []
for titel, bestanden in groepen:
    feiten = []
    for b in bestanden:
        t = (m / "src" / b).read_text(encoding="utf-8")
        t = re.sub(r"^\s*--\s*$", "", t, flags=re.M)
        t = re.sub(r"\[(long-)?pause\]", "", t)
        for stuk in re.split(r"(?=\{img:)", t):
            mm = re.match(r"\{img:([^}]+)\}\s*(.*)", stuk, re.S)
            if not mm:
                continue
            slug, tekst = mm.group(1).strip(), " ".join(mm.group(2).split())
            z = zinnen(tekst)
            if len(z) < 2:
                continue
            prompt = beeld.get(slug, slug.replace("-", " "))
            prompt = re.sub(r"^A calm, warmly lit scene:\s*", "", prompt)
            feiten.append(f"IMG: {slug} | {prompt}\nHEAD: {z[0]}\nBODY: {' '.join(z[1:])}")
    blokken.append((titel, feiten))
per = -(-len(blokken) // 3)
(m / "src-feiten").mkdir(exist_ok=True)
for d in range(3):
    uit = []
    for titel, feiten in blokken[d * per:(d + 1) * per]:
        uit.append(f"TOPIC: {titel}" if titel == blokken[0][0] else f"TOPIC: {titel}\nBRIDGE: ...")
        uit += feiten
    (m / "src-feiten" / f"deel{d + 1}.txt").write_text("\n===\n".join(uit) + "\n", encoding="utf-8")
print(f"{sum(len(f) for _, f in blokken)} feitjes in {len(blokken)} onderwerpen")
