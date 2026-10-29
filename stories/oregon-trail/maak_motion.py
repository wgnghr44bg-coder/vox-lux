#!/usr/bin/env python3
"""Maakt motion.json (titels, data, kaart, citaten, tijdlijn) en effecten.tsv uit afbeeldingen-tijden-pauzes.tsv."""
import csv, json
from pathlib import Path

d = Path(__file__).parent
rows = list(csv.DictReader(open(d / "afbeeldingen-tijden-pauzes.tsv", encoding="utf-8"), delimiter="\t"))
t = {r["slug"]: float(r["start"]) for r in rows}

hoofdstukken = [
    ("independence-square-spring", "Independence, Missouri"), ("farm-family-reading-letter", "Who Goes West"),
    ("wagons-leaving-into-prairie", "On the Way"), ("dawn-camp-wagons-circle", "A Day on the Trail"),
    ("mother-dutch-oven-baking", "Women and Children"), ("oxen-team-with-names", "The Animals"),
    ("platte-river-wide-shallow", "Along the Platte"), ("night-camp-under-stars", "A Night on the Prairie"),
    ("fiddle-dance-inside-circle", "Music and Friendship"), ("courthouse-rock-distance", "The Great Rocks"),
    ("dry-hills-sagebrush-trail", "Independence Rock"), ("sweetwater-valley-snowy-peaks", "South Pass"),
    ("fort-bridger-log-post", "Two Roads"), ("fort-hall-white-walls", "Along the Snake"),
    ("worn-wagon-repairs-camp", "Mending and Trading"), ("grande-ronde-valley", "The Blue Mountains"),
    ("rafts-on-columbia-river", "The Last Miles"), ("applegate-party-southern-road", "Tabitha Brown"),
    ("choosing-land-claim-meadow", "A New Home"), ("many-wagons-later-years", "What Remains"),
]
items = []
for n, (slug, titel) in enumerate(hoofdstukken, 1):
    items.append({"soort": "hoofdstuk", "tijd": 10 if n == 1 else t[slug] + 1.5, "nummer": n, "titel": titel})

def plus(slug, s=25):
    return round(t[slug] + s, 1)

items += [
    {"soort": "datum", "tijd": plus("outfitters-store-counter"), "regel1": "May 1846", "regel2": "Independence, Missouri"},
    {"soort": "citaat", "tijd": plus("young-parkman-st-louis-levee", 15),
     "tekst": "Last spring, 1846, was a busy season in the City of St. Louis.",
     "bron": "Francis Parkman, The Oregon Trail"},
    {"soort": "kaart", "tijd": plus("wagons-leaving-into-prairie", 30), "titel": "The Oregon Trail, 1846",
     "gebied": [-128, -90, 37, 49],
     "plaatsen": [
         {"naam": "Independence", "lon": -94.42, "lat": 39.09, "kant": "onder"},
         {"naam": "Fort Laramie", "lon": -104.56, "lat": 42.21, "kant": "onder"},
         {"naam": "South Pass", "lon": -108.9, "lat": 42.36, "kant": "boven"},
         {"naam": "Fort Hall", "lon": -112.45, "lat": 43.02, "kant": "onder"},
         {"naam": "The Dalles", "lon": -121.18, "lat": 45.6, "kant": "boven"},
         {"naam": "Oregon City", "lon": -122.6, "lat": 45.36, "kant": "links"}],
     "route": [[-94.42, 39.09], [-95.7, 39.05], [-97.0, 39.8], [-98.9, 40.67], [-100.8, 41.05], [-103.0, 41.7],
               [-104.56, 42.21], [-106.3, 42.85], [-107.13, 42.49], [-108.9, 42.36], [-110.1, 42.1],
               [-111.6, 42.65], [-112.45, 43.02], [-114.8, 42.6], [-116.95, 43.8], [-118.1, 45.3],
               [-119.5, 45.7], [-121.18, 45.6], [-122.6, 45.36]]},
    {"soort": "datum", "tijd": plus("fort-laramie-adobe-walls"), "regel1": "June 1846", "regel2": "Fort Laramie"},
    {"soort": "datum", "tijd": plus("fourth-of-july-celebration", 10), "regel1": "4 July 1846", "regel2": "Independence Rock"},
    {"soort": "citaat", "tijd": plus("two-roads-wagons-dividing", 30),
     "tekst": "Never take no cutoffs, and hurry along as fast as you can.",
     "bron": "Virginia Reed, letter, 1847"},
    {"soort": "datum", "tijd": plus("oregon-city-falls-cabins"), "regel1": "Autumn 1846", "regel2": "Oregon City"},
    {"soort": "datum", "tijd": plus("salem-cabin-christmas-rain", 5), "regel1": "Christmas Day 1846", "regel2": "Salem, Oregon"},
    {"soort": "tijdlijn", "tijd": plus("railroad-across-plains", 15), "punten": [
        ["1843", "The first large wagon trains"], ["1846", "Tabitha Brown and Parkman go west"],
        ["1869", "The railroad crosses the continent"], ["Today", "The wagon ruts can still be seen"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life on the Oregon Trail, 1846", "intro": True, "slot": True, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# effecten per beeld, op woorden in de slug
regels = [
    (("night", "stars", "moonlight"), [("sterren", 0.7)]),
    (("campfire", "firelight", "fireside", "fire", "hymn", "fiddle"), [("vonken", 0.6)]),
    (("lantern", "christmas", "reading", "cabin-christmas"), [("kaarslicht", 0.8)]),
    (("dawn", "first-light", "river", "falls", "gorge", "forest", "mist", "springs", "valley"), [("mist", 0.6)]),
    (("rain", "storm"), [("regen", 0.6)]),
    (("evening", "dusk", "sunset"), [("vuurvliegjes", 0.6)]),
    (("dusty", "desert", "dry", "sagebrush", "ruts", "store", "blacksmith", "nooning"), [("stof", 0.6)]),
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
