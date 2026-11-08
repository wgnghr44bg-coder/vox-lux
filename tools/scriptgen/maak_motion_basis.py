#!/usr/bin/env python3
"""Algemene maak_motion.py (scriptgenerator, 8 nov 2026): hoofdstukken uit hoofdstukken.tsv, effecten gekozen op woorden
in de beeldbeschrijving (afbeeldingen-onderwerpen.tsv), youtube-beschrijving met hoofdstuktijden. Geen intro/slot-beeld."""
import csv, json, re
from pathlib import Path

d = Path(__file__).parent
rows = list(csv.DictReader(open(d / "afbeeldingen-tijden-pauzes.tsv", encoding="utf-8"), delimiter="\t"))
start = {re.sub(r"^\d+-", "", r["slug"]): float(r["start"]) for r in rows}
eind = float(rows[-1]["end"])
HOOFDSTUKKEN = [(t, re.sub(r"^\d+-", "", s)) for t, s in
                (l.split("\t") for l in (d / "hoofdstukken.tsv").read_text(encoding="utf-8").split("\n") if l.strip())]
kapitels = [(t, start[s]) for t, s in HOOFDSTUKKEN if s in start]
items = [{"soort": "hoofdstuk", "tijd": 10 if n == 1 else round(t + 3, 1), "nummer": n, "titel": titel}
         for n, (titel, t) in enumerate(kapitels, 1)]
json.dump({"onderwerp": d.name, "intro": False, "slot": False, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def hms(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}"


besch = (d / "youtube-beschrijving.txt").read_text(encoding="utf-8")
kop, rest = besch.split("Chapters", 1)
staart = rest.split("\n\n", 1)[1] if "\n\n" in rest else ""
(d / "youtube-beschrijving.txt").write_text(
    f"{kop}Chapters\n" + "\n".join(f"{hms(0 if n == 0 else t)} {titel}" for n, (titel, t) in enumerate(kapitels)) +
    f"\n\n{staart}", encoding="utf-8")

# effecten op woorden in de beeldbeschrijving (zelfde soorten en sterktes als de handgemaakte video's)
beschr = {}
ond = d / "afbeeldingen-onderwerpen.tsv"
if ond.exists():
    for r in csv.DictReader(open(ond, encoding="utf-8"), delimiter="\t"):
        beschr[r["slug"]] = r.get("prompt", "").lower()
REGELS = [("sterren", 0.8, r"\bstars?\b|night sky|moonlit|moon"), ("vuur", 0.8, r"campfire|bonfire|hearth|fireplace"),
          ("kaarslicht", 0.7, r"candle|oil lamp|lamplight|lantern"), ("mist", 0.5, r"\bmist|\bfog|dawn|haze"),
          ("stof", 0.6, r"dust|desert|road|street|workshop|field"), ("lichtstralen", 0.7, r"sunbeam|rays|window light|church|hall"),
          ("sneeuw", 0.7, r"\bsnow|winter|frost"), ("vuurvliegjes", 0.7, r"garden|meadow|summer evening")]
eff, slugs = [], [r["slug"] for r in rows]
for i, r in enumerate(rows):
    tekst = beschr.get(re.sub(r"^\d+-", "", r["slug"]), "")
    for e, sterk, pat in REGELS:
        if re.search(pat, tekst):
            eff.append((float(r["start"]), float(r["end"]), e, sterk))
            break
with open(d / "effecten.tsv", "w", encoding="utf-8") as f:
    f.write("van\ttot\teffect\tsterkte\tx\ty\n")
    for a, b, e, s in sorted(eff):
        f.write(f"{a:.2f}\t{b:.2f}\t{e}\t{s}\t\t\n")
print(f"{len(kapitels)} hoofdstukken, {len(items)} onderdelen, effecten {sum(b - a for a, b, e, s in eff) / eind:.0%} van de video")
