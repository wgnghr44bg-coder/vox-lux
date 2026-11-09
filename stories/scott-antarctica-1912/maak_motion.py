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
    {"soort": "datum", "tijd": na("old-wooden-whaling-ship-oak-bow", 15), "regel1": "June 1910", "regel2": "Cardiff, Wales"},
    {"soort": "datum", "tijd": na("lyttelton-harbour-green-hills-1910", 20), "regel1": "November 1910", "regel2": "Lyttelton, New Zealand"},
    {"soort": "datum", "tijd": na("ross-island-coast-cape-black-rocks", 20), "regel1": "4 January 1911", "regel2": "Cape Evans, Antarctica"},
    {"soort": "datum", "tijd": na("last-sunset-before-winter-ice-hut", 20), "regel1": "23 April 1911", "regel2": "The last sunset before winter"},
    {"soort": "datum", "tijd": na("polar-night-snow-plain-stars-moonlight", 15), "regel1": "July 1911", "regel2": "On the way to Cape Crozier"},
    {"soort": "datum", "tijd": na("ponies-sledges-leaving-hut-spring", 20), "regel1": "1 November 1911", "regel2": "Cape Evans"},
    {"soort": "datum", "tijd": na("small-tent-flag-alone-snow-plain", 20), "regel1": "14 December 1911", "regel2": "The South Pole"},
    {"soort": "datum", "tijd": na("five-men-standing-pole-flag-wind", 20), "regel1": "17 January 1912", "regel2": "The South Pole"},
    {"soort": "datum", "tijd": na("snow-cairn-ski-cross-plain-sunlight", 20), "regel1": "12 November 1912", "regel2": "The Great Ice Barrier"},
    {"soort": "kaart", "tijd": na("men-studying-map-lamplit-hut-table", 10), "titel": "The road to the Pole, 1911",
     "gebied": [158.0, 180.0, -85.0, -76.5],
     "plaatsen": [
         {"naam": "Cape Evans", "lon": 166.42, "lat": -77.64, "kant": "links"},
         {"naam": "Cape Crozier", "lon": 169.27, "lat": -77.46, "kant": "rechts"},
         {"naam": "One Ton Depot", "lon": 169.0, "lat": -79.5, "kant": "rechts"},
         {"naam": "Beardmore Glacier", "lon": 171.0, "lat": -83.5, "kant": "rechts"}]},
    {"soort": "tijdlijn", "tijd": na("wooden-cross-observation-hill-view", 25), "punten": [
        ["1910", "The Terra Nova leaves Cardiff"], ["1911", "A winter in the hut"],
        ["1912", "Two teams reach the Pole"], ["1913", "The ship sails home"], ["Today", "The hut still stands"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Antarctica with Scott's Last Expedition, 1912", "intro": False, "slot": False, "items": items},
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
    "mist": ["first-iceberg-grey-sea-ship", "ship-in-pack-ice-midnight-sun", "mount-erebus-smoking-volcano-sea", "tents-snowed-in-glacier-foot-mountains",
             "emperor-penguins-huddle-winter-twilight", "sastrugi-snow-ridges-plateau-low-sun", "quiet-tent-glacier-foot-evening-light"],
    "lichtstralen": ["sun-returns-horizon-golden-ice", "hut-cape-evans-erebus-behind-sunlight", "men-hauling-sledges-beardmore-glacier", "wooden-cross-observation-hill-view",
                     "snow-cairn-ski-cross-plain-sunlight", "cape-evans-hut-today-erebus-sunlight", "men-sitting-outside-hut-golden-midnight"],
    "stof": ["crowded-ship-deck-crates-hay-coal", "stokers-shovelling-coal-furnace-glow", "ponies-in-snow-stables-blankets", "short-red-haired-officer-ship-stores",
             "packing-ration-bags-hut-table", "fossil-leaf-stone-museum-lamp", "sculptor-woman-studio-london-1910"],
    "kaarslicht": ["wardroom-supper-swinging-lamps-ship", "wardroom-long-table-acetylene-lamps", "crowded-bunks-saddles-clothes-hut", "pianola-gramophone-corner-hut-lamplight",
                   "midwinter-feast-flags-table-celebration", "scott-writing-journal-cubicle-candle", "candle-tent-writing-letters-quiet", "second-winter-hut-thirteen-men-lamp"],
    "vuur": ["hut-kitchen-stove-cook-bread", "five-men-inside-small-tent-stove-cocoa"],
    "sneeuw": ["siberian-sled-dogs-curled-snow", "men-leading-ponies-moonlight-sea-ice", "three-tired-men-arriving-hut-dawn", "tall-man-quiet-tent-evening-stove"],
    "sterren": ["aurora-australis-green-curtains-hut", "polar-night-snow-plain-stars-moonlight", "small-tent-lantern-glow-dark-snow"],
    "vuurvliegjes": [],
}
STERK = {"lichtstralen": 0.7, "stof": 0.6, "kaarslicht": 0.7, "vuur": 0.8, "sneeuw": 0.5, "mist": 0.5, "sterren": 0.8, "vuurvliegjes": 0.7}
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
