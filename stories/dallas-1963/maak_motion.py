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
    {"soort": "datum", "tijd": na("pegasus-neon-horse-tower-dawn", 20), "regel1": "Autumn 1963", "regel2": "Dallas, Texas"},
    {"soort": "datum", "tijd": na("air-force-one-andrews-takeoff-morning", 15), "regel1": "Thursday, 21 November 1963", "regel2": "Washington to Texas"},
    {"soort": "datum", "tijd": na("rainy-parking-lot-crowd-umbrellas-morning", 15), "regel1": "Friday, 22 November 1963  ·  Morning", "regel2": "Fort Worth, Texas"},
    {"soort": "datum", "tijd": na("love-field-crowd-fence-sunshine", 20), "regel1": "22 November 1963  ·  Midday", "regel2": "Love Field, Dallas"},
    {"soort": "datum", "tijd": na("air-force-one-cabin-oath-ceremony", 20), "regel1": "22 November 1963  ·  Afternoon", "regel2": "Love Field, Dallas"},
    {"soort": "datum", "tijd": na("funeral-washington-horses-caisson-crowds", 25), "regel1": "25 November 1963", "regel2": "Washington and Arlington"},
    {"soort": "kaart", "tijd": na("san-antonio-crowds-sunny-1963", 10), "titel": "Texas, November 1963",
     "gebied": [-100.2, -93.8, 28.8, 33.6],
     "plaatsen": [
         {"naam": "Dallas", "lon": -96.80, "lat": 32.78, "kant": "rechts"},
         {"naam": "Fort Worth", "lon": -97.33, "lat": 32.75, "kant": "links"},
         {"naam": "Houston", "lon": -95.37, "lat": 29.76, "kant": "rechts"},
         {"naam": "San Antonio", "lon": -98.49, "lat": 29.42, "kant": "links"}]},
    {"soort": "tijdlijn", "tijd": na("apollo-moon-landing-astronaut-flag-1969", 25), "punten": [
        ["1963", "A bright November in Dallas"], ["1964", "The Warren Commission report"],
        ["1970", "The memorial opens"], ["1989", "The museum opens"], ["Today", "Dealey Plaza is a landmark"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Dallas, November 1963", "intro": False, "slot": False, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def hms(x):
    x = int(x)
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}"

besch = (d / "youtube-beschrijving.txt").read_text(encoding="utf-8")
kop = besch.split("Chapters")[0]
tail = besch.split("Chapters")[1].split("\n\n", 1)[1]
ch = "\n".join(f"{hms(0 if n == 0 else t)} {titel}" for n, (titel, t) in enumerate(kapitels))
(d / "youtube-beschrijving.txt").write_text(f"{kop}Chapters\n{ch}\n\n{tail}", encoding="utf-8")

EFF = {
    "mist": ["trinity-river-levees-cottonwoods", "rainy-parking-lot-crowd-umbrellas-morning", "pegasus-neon-horse-tower-dawn", "window-view-sun-breaking-through-clouds"],
    "lichtstralen": ["window-view-street-park-dusk-office", "dealey-plaza-park-colonnade-1963", "air-force-one-sunset-flight-east", "sixth-floor-museum-quiet-window-boxes",
                     "texas-storm-clouds-prairie-evening", "kennedy-memorial-dallas-white-walls-sky"],
    "stof": ["supermarket-aisle-1963-shopping-cart", "department-store-escalator-shoppers-1963", "dress-factory-showroom-seamstresses", "school-book-depository-red-brick-building",
             "downtown-main-street-crowds-confetti", "love-field-crowd-fence-sunshine", "oil-wells-east-texas-1930s", "old-red-courthouse-log-cabin-park"],
    "kaarslicht": ["hotel-suite-paintings-lamps-night", "family-dinner-table-fried-chicken-iced-tea", "family-watching-black-white-tv", "oval-office-president-desk-evening",
                   "dressmaker-office-1963-man-glasses", "trade-mart-lunch-tables-waiting-guests"],
    "vuur": ["movie-theatre-marquee-evening", "friday-night-football-stadium-lights"],
    "vonken": ["state-fair-big-tex-families", "dallas-skyline-dusk-lights-neon-horse", "dealey-plaza-flowers-night-street-lamps"],
    "sterren": ["little-house-night-porch-light", "little-house-night-porch-light-rain", "dealey-plaza-flowers-night-street-lamps"],
    "vuurvliegjes": ["backyard-swing-set-two-boys-playing", "grandfather-grandchildren-garden-sunday", "abraham-zapruder-older-man-garden-quiet", "family-picnic-lake-zoo-weekend"],
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
