#!/usr/bin/env python3
"""Maakt motion.json (hoofdstukken, data, kaart, tijdlijn), effecten.tsv en youtube-beschrijving.txt
uit afbeeldingen-tijden-pauzes.tsv. Hoofdstuk = begin van het eerste bestand van elke regel in HOOFDSTUKKEN.txt."""
import csv, json, re
from pathlib import Path

d = Path(__file__).parent
rows = list(csv.DictReader(open(d / "afbeeldingen-tijden-pauzes.tsv", encoding="utf-8"), delimiter="\t"))
start = {re.sub(r"^\d+-", "", r["slug"]): float(r["start"]) for r in rows}   # cues heten NN-slug (feitjes-opbouw)
eind = float(rows[-1]["end"])

# hoofdstukken van de feitjes-opbouw (7 nov 2026): titel -> eerste beeld van dat deel
HOOFDSTUKKEN = [(titel, re.sub(r"^\d+-", "", s)) for titel, s in   # onderwerpen uit tools/bouw_feiten.py (OPBOUW.md)
                (l.split("\t") for l in (d / "hoofdstukken.tsv").read_text(encoding="utf-8").split("\n") if l.strip())]
kapitels = [(titel, start[slug]) for titel, slug in HOOFDSTUKKEN]

items = [{"soort": "hoofdstuk", "tijd": 10 if n == 1 else round(t + 3, 1), "nummer": n, "titel": titel}
         for n, (titel, t) in enumerate(kapitels, 1)]


def na(slug, s=25):
    return round(start[slug] + s, 1)


items += [
    {"soort": "datum", "tijd": na("first-sight-of-tower-haze", 10), "regel1": "Spring, 600 BC", "regel2": "Babylon, on the Euphrates"},
    {"soort": "datum", "tijd": na("flat-roof-family-sleeping-stars", 15), "regel1": "A summer night, 600 BC", "regel2": "A house in Babylon"},
    {"soort": "datum", "tijd": na("akitu-festival-boats-statues-river", 15), "regel1": "The New Year, in spring", "regel2": "Babylon"},
    {"soort": "datum", "tijd": na("cyrus-entering-babylon-peaceful-crowd", 15), "regel1": "539 BC", "regel2": "The Persians enter Babylon"},
    {"soort": "datum", "tijd": na("koldewey-excavation-railway-workers", 20), "regel1": "1899", "regel2": "Robert Koldewey begins to dig"},
    {"soort": "kaart", "tijd": na("mesopotamia-plain-two-rivers", 25), "titel": "Mesopotamia, 600 BC",
     "gebied": [41.0, 51.0, 29.5, 37.5],
     "plaatsen": [
         {"naam": "Babylon", "lon": 44.42, "lat": 32.54, "kant": "rechts"},
         {"naam": "Nineveh", "lon": 43.15, "lat": 36.36, "kant": "rechts"},
         {"naam": "Ur", "lon": 46.10, "lat": 30.96, "kant": "rechts"},
         {"naam": "Susa", "lon": 48.25, "lat": 32.19, "kant": "links"}]},
    {"soort": "tijdlijn", "tijd": na("ruined-mounds-desert-palms", 25), "punten": [
        ["600 BC", "Nebuchadnezzar rules Babylon"], ["539 BC", "Cyrus enters the city"],
        ["323 BC", "Alexander dies in Babylon"], ["1899", "Koldewey begins to dig"], ["Today", "Babylon is a World Heritage Site"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Ancient Babylon, 600 BC", "intro": False, "slot": False, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def hms(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}"

besch = (d / "youtube-beschrijving.txt").read_text(encoding="utf-8")
kop = besch.split("Chapters")[0]
tail = besch.split("Chapters")[1].split("\n\n", 1)[1]
ch = "\n".join(f"{hms(0 if n == 0 else round(t + 3))} {titel}" for n, (titel, t) in enumerate(kapitels))   # zelfde tijd als de titel in beeld (QC)
(d / "youtube-beschrijving.txt").write_text(f"{kop}Chapters\n{ch}\n\n{tail}", encoding="utf-8")

EFF = {
    "mist": ["traveller-boat-euphrates-morning", "fishermen-dawn-nets-herons", "first-sight-of-tower-haze", "irrigation-canals-palm-groves",
             "mesopotamia-plain-two-rivers", "southern-marsh-reed-houses-canoe", "baking-flatbread-clay-oven-dawn", "ziggurat-base-today-reeds-water"],
    "lichtstralen": ["throne-room-blue-facade-lions", "esagila-temple-courtyard-priests", "ishtar-gate-front-blue-towers", "processional-way-lions-blue",
                     "gate-today-berlin-museum-hall", "clay-library-shelves-archive", "babylon-legacy-clock-stars-museum", "palace-collection-old-statues-hall"],
    "stof": ["market-street-merchants-donkeys", "camel-caravan-arriving-at-gate", "brickmakers-wooden-moulds-yard", "plain-street-low-wooden-door",
             "seed-plough-oxen-barley-field", "ruined-mounds-desert-palms", "koldewey-excavation-railway-workers", "weavers-dyers-goldsmiths-workshops",
             "eight-city-gates-god-names", "tablets-drying-in-sun-rows", "stamped-bricks-king-name-closeup", "walls-chariot-top-herodotus"],
    "kaarslicht": ["house-furniture-lamps-chests", "priests-feeding-god-golden-table", "creation-poem-recited-priests", "household-shrine-evening-prayer",
                   "tavern-keeper-woman-serving", "beer-drinkers-straws-large-jar", "ration-tablet-storeroom-palace", "scholar-reading-tablet-magnifier",
                   "base-sixty-wedge-numbers-tablet", "square-diagonal-tablet-numbers"],
    "vuur": ["festival-night-lamps-rooftops", "king-before-marduk-statue-ceremony"],
    "vonken": ["procession-through-ishtar-gate-statues", "quay-evening-families-water", "gods-of-babylon-shrine-statues"],
    "sterren": ["flat-roof-family-sleeping-stars", "astronomers-roof-night-tablets", "night-sky-moon-planets-tower", "priests-climbing-ziggurat-stars", "zodiac-star-pictures-bull-lion"],
    "vuurvliegjes": ["hanging-gardens-imagined-terraces", "judean-exiles-canal-willows-dusk", "palace-roof-walk-evening-city", "grandmother-telling-stories-gilgamesh"],
}
STERK = {"lichtstralen": 0.7, "stof": 0.6, "kaarslicht": 0.7, "vuur": 0.8, "vonken": 0.6, "mist": 0.5, "sterren": 0.8, "vuurvliegjes": 0.7}
slugs = [re.sub(r"^\d+-", "", r["slug"]) for r in rows]   # cues heten NN-slug
eff = []
for e, lijst in EFF.items():
    for s in lijst:
        i = slugs.index(s)
        eff.append((start[s], float(rows[i]["end"]), e, STERK[e]))
eff.sort()
with open(d / "effecten.tsv", "w", encoding="utf-8") as f:
    f.write("van\ttot\teffect\tsterkte\tx\ty\n")
    for a, b, e, s in eff:
        f.write(f"{a:.2f}\t{b:.2f}\t{e}\t{s}\t\t\n")
tot = sum(b - a for a, b, e, s in eff)
print(f"{len(kapitels)} hoofdstukken, {len(items)} onderdelen, effecten {tot / eind:.0%} van de video")
