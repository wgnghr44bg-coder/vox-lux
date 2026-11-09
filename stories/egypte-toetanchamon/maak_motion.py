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
    {"soort": "datum", "tijd": na("winter-nile-fields-green-morning", 20), "regel1": "Winter, 1323 BC", "regel2": "Thebes, Egypt"},
    {"soort": "datum", "tijd": na("funeral-boats-crossing-nile-dawn", 15), "regel1": "Spring, 1323 BC", "regel2": "The Nile at Thebes"},
    {"soort": "datum", "tijd": na("howard-carter-valley-1920s", 20), "regel1": "Autumn 1922", "regel2": "The Valley of the Kings"},
    {"soort": "datum", "tijd": na("workmen-baskets-rubble-valley", 25), "regel1": "4 November 1922", "regel2": "The Valley of the Kings"},
    {"soort": "datum", "tijd": na("sealed-doorway-staircase-sunlight", 72), "regel1": "26 November 1922  ·  Afternoon", "regel2": "The tomb of Tutankhamun"},
    {"soort": "datum", "tijd": na("carter-team-cataloguing-objects", 95), "regel1": "February 1923", "regel2": "The sealed doorway is opened"},
    {"soort": "kaart", "tijd": na("amarna-city-desert-river", 10), "titel": "Egypt, 1323 BC",
     "gebied": [28.5, 35.5, 23.8, 31.4],
     "plaatsen": [
         {"naam": "Thebes", "lon": 32.64, "lat": 25.72, "kant": "rechts"},
         {"naam": "Amarna", "lon": 30.90, "lat": 27.64, "kant": "rechts"},
         {"naam": "Memphis", "lon": 31.25, "lat": 29.85, "kant": "rechts"},
         {"naam": "Aswan", "lon": 32.90, "lat": 24.09, "kant": "rechts"}]},
    {"soort": "tijdlijn", "tijd": na("burial-chamber-painted-walls-quiet", 25), "punten": [
        ["1323 BC", "Tutankhamun is buried"], ["1922", "Howard Carter finds the tomb"],
        ["1923", "The sealed doorway is opened"], ["Today", "The treasures rest in one museum"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Ancient Egypt When Tutankhamun Died, 1323 BC", "intro": False, "slot": False, "items": items},
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
    "mist": ["nile-dawn-reeds-boat", "nile-flood-fields-water", "winter-nile-fields-green-morning", "funeral-boats-crossing-nile-dawn",
             "workers-walking-path-cliffs-dawn", "royal-couple-boat-marsh-lotus", "mourners-white-linen-riverbank", "golden-barge-towed-river"],
    "lichtstralen": ["priests-temple-hall-columns", "palace-hall-painted-floor", "sun-disk-rays-relief", "royal-family-sun-rays-art",
                     "burial-chamber-golden-shrine", "sealed-doorway-staircase-sunlight", "museum-hall-golden-treasures", "golden-throne-queen-anointing"],
    "stof": ["thebes-street-market-morning", "abandoned-city-sand-drifting", "sledge-pulled-by-officials-desert", "desert-road-travellers-caravan",
             "workmen-baskets-rubble-valley", "valley-of-kings-procession-sunlight", "harvest-golden-wheat-sickles", "farmers-ploughing-oxen-field",
             "stonemason-chiselling-name-temple", "carter-team-cataloguing-objects", "antechamber-golden-couches-statues", "valley-of-kings-today-morning"],
    "kaarslicht": ["painters-tomb-wall-lamplight", "palace-room-lamps-night-quiet", "candlelight-glimpse-gold-dark", "cat-sleeping-house-niche",
                   "golden-mask-lamplight-tomb", "treasury-room-anubis-shrine", "burial-chamber-painted-walls-quiet", "musicians-harp-lute-banquet",
                   "goldsmiths-workshop-mask-making", "antechamber-golden-couches-statues"],
    "vuur": ["village-evening-families-roofs", "funeral-feast-desert-evening"],
    "vonken": ["luxor-temple-colonnade-torches", "riverbank-night-families-lamps", "luxor-temple-evening-lights", "officials-resealing-tomb-torch"],
    "sterren": ["western-cliffs-night-stars-nile", "riverbank-night-families-lamps", "dusk-thebes-western-cliffs"],
    "vuurvliegjes": ["queen-ankhesenamun-palace-garden", "memphis-palace-river-pyramids", "felucca-nile-sunset-modern-timeless", "palace-terrace-sunset-couple"],
}
STERK = {"lichtstralen": 0.7, "stof": 0.6, "kaarslicht": 0.7, "vuur": 0.8, "vonken": 0.6, "mist": 0.5, "sterren": 0.8, "vuurvliegjes": 0.7}
slugs = [re.sub(r"^\d+-", "", r["slug"]) for r in rows]   # cues heten NN-slug
eff = []
for e, lijst in EFF.items():
    for s in lijst:
        i = slugs.index(s)
        eff.append((start[s], float(rows[i]["end"]), e, STERK[e]))
        if e == "sterren" and s == "western-cliffs-night-stars-nile":
            eff.append((start[s], float(rows[i]["end"]), "mist", 0.4))
eff.sort()
with open(d / "effecten.tsv", "w", encoding="utf-8") as f:
    f.write("van\ttot\teffect\tsterkte\tx\ty\n")
    for a, b, e, s in eff:
        f.write(f"{a:.2f}\t{b:.2f}\t{e}\t{s}\t\t\n")
tot = sum(b - a for a, b, e, s in eff)
print(f"{len(kapitels)} hoofdstukken, {len(items)} onderdelen, effecten {tot / eind:.0%} van de video")
