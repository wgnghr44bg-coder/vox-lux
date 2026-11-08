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
    {"soort": "datum", "tijd": na("desert-hills-dawn-prospector", 40), "regel1": "1877", "regel2": "The hills of southern Arizona"},
    {"soort": "datum", "tijd": na("mesa-sunset-mountains-distant", 20), "regel1": "Spring 1879", "regel2": "Goose Flats, Arizona Territory"},
    {"soort": "datum", "tijd": na("newspaper-office-printing-press", 20), "regel1": "1 May 1880", "regel2": "The first issue of the Epitaph"},
    {"soort": "datum", "tijd": na("earp-wagons-arriving-1879", 25), "regel1": "End of 1879", "regel2": "The Earp family arrives in Tombstone"},
    {"soort": "datum", "tijd": na("two-riders-arriving-grand-hotel", 0) if False else na("wagon-arriving-town-evening-wind", 20), "regel1": "25 October 1881  ·  Evening", "regel2": "Tombstone, Arizona Territory"},
    {"soort": "datum", "tijd": na("grey-dawn-allen-street-empty", 20), "regel1": "26 October 1881  ·  Morning", "regel2": "Allen Street, Tombstone"},
    {"soort": "kaart", "tijd": na("hilltop-view-valley-afternoon", 10), "titel": "Southern Arizona, 1881",
     "gebied": [-113.5, 30.8, -106.5, 35.3],
     "plaatsen": [
         {"naam": "Tombstone", "lon": -110.07, "lat": 31.71, "kant": "rechts"},
         {"naam": "Tucson", "lon": -110.97, "lat": 32.22, "kant": "boven"},
         {"naam": "Phoenix", "lon": -112.07, "lat": 33.45, "kant": "boven"},
         {"naam": "Bisbee", "lon": -109.93, "lat": 31.45, "kant": "onder"},
         {"naam": "Mexico", "lon": -110.5, "lat": 31.05, "kant": "onder"}]},
    {"soort": "tijdlijn", "tijd": na("colton-california-orange-groves", 0) if False else na("ed-schieffelin-cabin-oregon-woods", 80), "punten": [
        ["1877", "Ed Schieffelin finds silver"], ["1879", "The town is laid out"],
        ["1881", "The afternoon on Fremont Street"], ["1929", "John Clum passes away"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in the Wild West: Tombstone, 1881", "intro": False, "slot": False, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# beschrijving: tijden mét pauzes
def hms(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}"

besch = (d / "youtube-beschrijving.txt").read_text(encoding="utf-8")
kop = besch.split("Chapters")[0]
tail = besch.split("Chapters")[1].split("\n\n", 1)[1]
ch = "\n".join(f"{hms(0 if n == 0 else t)} {titel}" for n, (titel, t) in enumerate(kapitels))
(d / "youtube-beschrijving.txt").write_text(f"{kop}Chapters\n{ch}\n\n{tail}", encoding="utf-8")

# effecten: wat past bij het beeld (woestijn: geen regen, geen sneeuw behalve winterbeeld)
EFF = {
    "lichtstralen": ["tombstone-street-morning-1881", "small-adobe-church-evening", "church-sunday-congregation", "hotel-parlour-piano-evening",
                     "courthouse-museum-today", "restaurant-white-tablecloths-lamps", "schoolhouse-children-teacher"],
    "stof": ["adobe-and-wooden-buildings", "water-wagon-barrels", "ore-wagons-desert-road", "allen-street-afternoon-boardwalk",
             "posse-riders-desert-road", "wagon-arriving-town-evening-wind", "fourth-street-cold-midday", "cowboys-riding-into-town-dusk",
             "four-men-walking-fremont-street", "ok-corral-stable-yard", "funeral-procession-brass-band", "tombstone-today-allen-street-boardwalk"],
    "kaarslicht": ["miners-candles-underground", "miners-lunch-break-candlelight", "parsons-writing-diary-lamp", "nellie-evening-porch-lamp",
                   "boarding-room-stove-night", "boarding-house-room-night-window", "house-window-lamp-evening-wind", "poker-game-late-night-lamp",
                   "doc-kate-hotel-balcony", "saloon-interior-lamplight-piano", "oriental-saloon-faro-table"],
    "vuur": ["prospector-campfire-night", "cowboy-campfire-coffee-night"],
    "vonken": ["hitching-rail-horses-dusk", "schieffelin-hall-evening-crowd", "tombstone-street-dusk-lamps-october", "hoisting-works-headframe"],
    "mist": ["desert-hills-dawn-prospector", "miners-walking-to-shift-dawn", "grey-dawn-allen-street-empty", "october-morning-town-cool",
             "distant-view-street-smoke-haze", "morning-after-quiet-town", "stamp-mill-river-cottonwoods", "glenwood-springs-hotel-mountains"],
    "sterren": ["fremont-first-street-night-quiet", "full-moon-over-dragoon-mountains", "tombstone-night-stars-desert-slot",
                "boothill-graveyard-evening-light", "valley-sunset-windmill-quiet"],
    "sneeuw": ["winter-tombstone-frost-roofs"],
    "vuurvliegjes": ["rose-tree-courtyard-white-blossoms", "schieffelin-monument-hills-sunset", "spring-desert-flowers-town-distance"],
}
STERK = {"lichtstralen": 0.7, "stof": 0.6, "kaarslicht": 0.7, "vuur": 0.8, "vonken": 0.6, "mist": 0.5, "sterren": 0.8, "sneeuw": 0.7, "vuurvliegjes": 0.7}
slugs = [re.sub(r"^\d+-", "", r["slug"]) for r in rows]   # cues heten NN-slug
eff = []
for e, lijst in EFF.items():
    for s in lijst:
        i = slugs.index(s)
        eff.append((start[s], float(rows[i]["end"]), e, STERK[e]))
        if e == "sterren" and s in ("fremont-first-street-night-quiet", "full-moon-over-dragoon-mountains"):
            eff.append((start[s], float(rows[i]["end"]), "mist", 0.4))
eff.sort()
with open(d / "effecten.tsv", "w", encoding="utf-8") as f:
    f.write("van\ttot\teffect\tsterkte\tx\ty\n")
    for a, b, e, s in eff:
        f.write(f"{a:.2f}\t{b:.2f}\t{e}\t{s}\t\t\n")
tot = sum(b - a for a, b, e, s in eff if e != "mist" or True)
print(f"{len(kapitels)} hoofdstukken, {len(items)} onderdelen, effecten {tot / eind:.0%} van de video")
