#!/usr/bin/env python3
"""Maakt motion.json (hoofdstukken, data, kaart, citaten, tijdlijn) en effecten.tsv uit afbeeldingen-tijden-pauzes.tsv."""
import csv, json
from pathlib import Path

d = Path(__file__).parent
rows = list(csv.DictReader(open(d / "afbeeldingen-tijden-pauzes.tsv", encoding="utf-8"), delimiter="\t"))
t = {int(r["slug"][:2]): float(r["start"]) for r in rows}          # feitje-nummer -> start

# hoofdstukken = de onderwerpen (TOPIC) uit src/deel*.txt, via tools/bouw_feiten.py -> hoofdstukken.tsv (OPBOUW.md)
HOOFDSTUKKEN = [(int(s[:2]), titel) for titel, s in
                (l.split("\t") for l in (d / "hoofdstukken.tsv").read_text(encoding="utf-8").split("\n") if l.strip())]
def _hms(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}"


_b = (d / "youtube-beschrijving.txt").read_text(encoding="utf-8")
_kop, _rest = _b.split("Chapters", 1)
_ch = "\n".join(f"{_hms(0 if n == 0 else t[f])} {titel}" for n, (f, titel) in enumerate(HOOFDSTUKKEN))
(d / "youtube-beschrijving.txt").write_text(f"{_kop}Chapters\n{_ch}\n\n{_rest.split(chr(10) + chr(10), 1)[1]}", encoding="utf-8")

items = [{"soort": "hoofdstuk", "tijd": 10 if n == 1 else t[f] + 1.5, "nummer": n, "titel": titel}
         for n, (f, titel) in enumerate(HOOFDSTUKKEN, 1)]


def plus(f, s=25):
    return round(t[f] + s, 1)


items += [
    {"soort": "datum", "tijd": plus(1, 40), "regel1": "3 September 1939", "regel2": "Britain"},
    {"soort": "datum", "tijd": plus(11), "regel1": "Autumn 1940", "regel2": "London"},
    {"soort": "datum", "tijd": plus(36), "regel1": "1939  ·  Chain Home", "regel2": "The English coast"},
    {"soort": "kaart", "tijd": plus(46, 30), "titel": "Europe, 1939–1945", "gebied": [-11, 40, 36, 61],
     "plaatsen": [
         {"naam": "London", "lon": -0.13, "lat": 51.51, "kant": "links"},
         {"naam": "Bletchley Park", "lon": -0.74, "lat": 52.0, "kant": "boven"},
         {"naam": "Dunkirk", "lon": 2.38, "lat": 51.03, "kant": "rechts"},
         {"naam": "Paris", "lon": 2.35, "lat": 48.86, "kant": "onder"},
         {"naam": "Amsterdam", "lon": 4.9, "lat": 52.37, "kant": "rechts"},
         {"naam": "Copenhagen", "lon": 12.57, "lat": 55.68, "kant": "rechts"},
         {"naam": "Leningrad", "lon": 30.32, "lat": 59.94, "kant": "onder"},
         {"naam": "Moscow", "lon": 33.0, "lat": 55.76, "kant": "onder"},
         {"naam": "Lisbon", "lon": -9.14, "lat": 38.72, "kant": "rechts"}]},
    {"soort": "datum", "tijd": plus(50), "regel1": "9 August 1942", "regel2": "Leningrad"},
    {"soort": "datum", "tijd": plus(54), "regel1": "19 January 1943", "regel2": "Ottawa, Canada"},
    {"soort": "citaat", "tijd": plus(62, 60),
     "tekst": "Go out into the darkness and put your hand into the Hand of God.",
     "bron": "Minnie Louise Haskins, read by King George VI, Christmas 1939"},
    {"soort": "datum", "tijd": plus(63), "regel1": "May 1940", "regel2": "Dunkirk"},
    {"soort": "datum", "tijd": plus(65, 30), "regel1": "6 June 1944", "regel2": "Normandy"},
    {"soort": "datum", "tijd": plus(69), "regel1": "24 August 1944", "regel2": "Paris"},
    {"soort": "datum", "tijd": plus(71), "regel1": "5 May 1945", "regel2": "The Netherlands"},
    {"soort": "datum", "tijd": plus(72), "regel1": "8 May 1945", "regel2": "London"},
    {"soort": "citaat", "tijd": plus(79, 50),
     "tekst": "We the peoples of the United Nations, determined to save succeeding generations from the scourge of war.",
     "bron": "Charter of the United Nations, 1945"},
    {"soort": "datum", "tijd": plus(77), "regel1": "4 July 1954", "regel2": "The last ration book"},
    {"soort": "tijdlijn", "tijd": plus(85, 15), "punten": [
        ["1939", "The war begins"], ["1940", "Dunkirk and the Blitz"],
        ["1944", "D-Day in Normandy"], ["1945", "Peace returns"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Quiet WW2 Facts to Fall Asleep To", "intro": False, "slot": False, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# effecten per beeld, op woorden in de slug
regels = [
    (("night", "stars", "astrodome"), [("sterren", 0.7)]),
    (("fireside", "campfire", "brew-up", "desert"), [("vonken", 0.5)]),
    (("candle", "radio", "wireless", "christmas", "attic", "lamplight", "kitchen", "knitting", "letter"), [("kaarslicht", 0.7)]),
    (("snow", "lights-across"), [("sneeuw", 0.5)]),
    (("dawn", "mist", "field", "canal", "harbour", "sea", "beach", "ship", "boat"), [("mist", 0.5)]),
    (("evening", "dusk", "sunset", "garden", "allotment", "harvest"), [("vuurvliegjes", 0.5)]),
    (("factory", "laboratory", "loft", "station", "church", "hall", "room", "store", "grocer"), [("stof", 0.5)]),
]
uit = ["van\ttot\teffect\tsterkte\tx\ty"]
for r in rows:
    for woorden, effecten in regels:
        if any(w in r["slug"] for w in woorden):
            for e, s in effecten:
                uit.append(f"{float(r['start']):.2f}\t{float(r['end']):.2f}\t{e}\t{s}\t\t")
            break
(d / "effecten.tsv").write_text("\n".join(uit) + "\n", encoding="utf-8")
print(len(items), "items,", len(uit) - 1, "effecten")
