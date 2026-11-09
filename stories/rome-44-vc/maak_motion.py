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
    {"soort": "datum", "tijd": na("roof-tiles-frost-smoke-rising-hills-pale-sky", 15), "regel1": "January, 44 BC", "regel2": "Rome"},
    {"soort": "datum", "tijd": na("river-rubicon-small-stream-winter-soldiers-crossing", 20), "regel1": "January, 49 BC", "regel2": "The river Rubicon"},
    {"soort": "datum", "tijd": na("roman-family-counting-days-calendar-wall", 20), "regel1": "1 January, 45 BC", "regel2": "The new calendar begins"},
    {"soort": "datum", "tijd": na("forum-rostra-golden-chair-purple-robe-crowd", 20), "regel1": "15 February, 44 BC", "regel2": "The Lupercalia, Rome"},
    {"soort": "datum", "tijd": na("lepidus-house-dinner-evening-lamps-friends", 20), "regel1": "14 March, 44 BC", "regel2": "Evening, Rome"},
    {"soort": "datum", "tijd": na("roman-bedroom-night-shutters-open-moonlight-curtains", 60), "regel1": "15 March, 44 BC", "regel2": "The Ides of March"},
    {"soort": "datum", "tijd": na("comet-over-rome-night-summer-sky", 20), "regel1": "July, 44 BC", "regel2": "The Julian star"},
    {"soort": "kaart", "tijd": na("grain-ships-harbour-amphorae-unloading", 10), "titel": "The Roman world, 44 BC",
     "gebied": [-6.0, 36.0, 28.0, 47.0],
     "plaatsen": [
         {"naam": "Rome", "lon": 12.48, "lat": 41.89, "kant": "rechts"},
         {"naam": "Alexandria", "lon": 29.92, "lat": 31.20, "kant": "rechts"},
         {"naam": "Athens", "lon": 23.73, "lat": 37.98, "kant": "rechts"},
         {"naam": "Rhodes", "lon": 28.22, "lat": 36.43, "kant": "rechts"},
         {"naam": "Apollonia", "lon": 19.47, "lat": 40.72, "kant": "links"}]},
    {"soort": "tijdlijn", "tijd": na("augustus-mature-statue-toga-calm-forum-dignified", 25), "punten": [
        ["49 BC", "Caesar crosses the Rubicon"], ["45 BC", "The new calendar begins"],
        ["44 BC", "The Ides of March"], ["27 BC", "Octavius becomes Augustus"], ["Today", "Flowers in the Forum"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Ancient Rome When Caesar Died, 44 BC", "intro": False, "slot": False, "items": items},
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
    "mist": ["rome-seven-hills-tiber-river-winter-morning-44bc", "roof-tiles-frost-smoke-rising-hills-pale-sky", "river-rubicon-small-stream-winter-soldiers-crossing", "grain-barges-tiber-oxen-towpath-warehouses",
             "palatine-hill-cave-lupercal-fig-tree-february", "caldarium-steam-hot-pool-bathers-soft-light"],
    "lichtstralen": ["capitoline-temple-jupiter-gilded-roof-morning-sun", "temple-interior-cella-large-statue-goddess-dim-light", "roman-villa-library-shelves-scroll-cases-sunlight", "theatre-of-pompey-garden-colonnade-statues-fountains",
                     "distant-view-columns-hall-doorway-figures-crowding", "temple-divine-julius-ruins-niche-flowers-forum", "curia-senate-house-bronze-doors-forum-sunlight"],
    "stof": ["dawn-roman-street-shutters-opening-shops-bakers", "crowded-roman-street-people-many-lands-morning", "forum-morning-crowds-basilica-arcades-lawyers", "roman-bookshop-scroll-shelves-arcade-customers",
             "craftsmen-street-blacksmith-potter-acrobat", "circus-maximus-chariots-racing-crowds-sunlit-sand", "architects-plans-model-temple-table-workshop"],
    "kaarslicht": ["triclinium-dining-room-painted-walls-three-couches", "cicero-older-man-writing-letter-study-scrolls", "marcus-brutus-serious-roman-reading-philosophy-lamp", "roman-woman-noble-lamp-thoughtful-night",
                   "lepidus-house-dinner-evening-lamps-friends", "villa-interior-egyptian-greek-furnishings-lamps-evening", "family-offering-household-shrine-incense-bread-wine", "saturnalia-feast-family-gifts-candles-merry-room"],
    "vuur": ["temple-vesta-round-sacred-fire-priestesses", "dark-roman-street-night-torch-slaves-lighting-way"],
    "vonken": ["roman-snack-bar-counter-clay-jars-street"],
    "sterren": ["sosigenes-astronomer-instruments-night-sky-roof", "comet-over-rome-night-summer-sky", "statue-capitol-night-small-notes-scrolls"],
    "vuurvliegjes": ["two-men-walking-garden-path-dusk-quiet-talk", "gardens-of-caesar-across-tiber-villa-view-city", "coastal-villa-formiae-sea-evening-calm-cypress"],
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
