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
    {"soort": "datum", "tijd": na("aloha-tower-boat-day-crowds-leis", 20), "regel1": "1941", "regel2": "Honolulu, Oahu"},
    {"soort": "datum", "tijd": na("battleship-row-ford-island-morning-calm", 60), "regel1": "1941", "regel2": "Pearl Harbor"},
    {"soort": "datum", "tijd": na("northern-bay-snow-ships-anchored-fog", 20), "regel1": "26 November 1941", "regel2": "The Kuril Islands"},
    {"soort": "datum", "tijd": na("captain-inspection-sailors-rows-deck", 60), "regel1": "Saturday, 6 December 1941", "regel2": "Pearl Harbor"},
    {"soort": "datum", "tijd": na("sunday-dawn-oahu-mountains-clouds-pink", 60), "regel1": "Sunday, 7 December 1941  ·  Dawn", "regel2": "Oahu, Hawaii"},
    {"soort": "datum", "tijd": na("radar-station-hilltop-north-shore-dawn", 20), "regel1": "7 December 1941  ·  7:02 am", "regel2": "Opana radar station"},
    {"soort": "datum", "tijd": na("workers-factory-gathered-around-radio", 20), "regel1": "8 December 1941", "regel2": "Washington"},
    {"soort": "datum", "tijd": na("admiral-nimitz-arriving-flying-boat-harbour", 20), "regel1": "25 December 1941", "regel2": "Pearl Harbor"},
    {"soort": "kaart", "tijd": na("sugar-cane-fields-wind-plantation-houses", 10), "titel": "Oahu, 1941",
     "gebied": [-158.30, -157.62, 21.24, 21.72],
     "plaatsen": [
         {"naam": "Honolulu", "lon": -157.86, "lat": 21.31, "kant": "rechts"},
         {"naam": "Pearl Harbor", "lon": -157.97, "lat": 21.36, "kant": "links"},
         {"naam": "Waikiki", "lon": -157.83, "lat": 21.28, "kant": "rechts"},
         {"naam": "Schofield Barracks", "lon": -158.06, "lat": 21.50, "kant": "links"},
         {"naam": "Kaneohe Bay", "lon": -157.78, "lat": 21.45, "kant": "rechts"}]},
    {"soort": "tijdlijn", "tijd": na("arizona-memorial-white-calm-water-morning", 25), "punten": [
        ["1940", "The fleet moves to Hawaii"], ["1941", "A Sunday morning in December"],
        ["1945", "The war ends in Tokyo Bay"], ["1962", "The Arizona Memorial opens"], ["Today", "A quiet place of memory"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life at Pearl Harbor, December 1941", "intro": False, "slot": False, "items": items},
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
    "mist": ["oahu-green-mountains-sea-dawn-1941", "taro-terraces-windward-valley-cliffs", "sunday-dawn-oahu-mountains-clouds-pink", "small-destroyer-patrol-calm-sea-dawn",
             "northern-bay-snow-ships-anchored-fog", "quiet-sky-over-harbour-late-morning-haze"],
    "lichtstralen": ["palm-trees-hibiscus-garden-trade-wind", "church-service-deck-sailors-folding-chairs", "navy-nurses-hospital-ward-white-uniforms", "arizona-memorial-white-calm-water-morning",
                     "plantation-village-church-bell-sunday", "oil-drops-rainbow-rings-calm-water"],
    "stof": ["navy-yard-workers-cranes-dry-dock", "fish-market-chinatown-morning-1941", "department-store-christmas-tinsel-palms", "young-man-recruiting-office-1939",
             "plantation-workers-pineapple-fields-mountains", "football-stadium-crowd-sunny-afternoon"],
    "kaarslicht": ["reveille-sailors-waking-bunks-ship", "young-sailor-writing-letter-bunk-lamp", "family-radio-news-living-room-1941", "admiral-study-calligraphy-quiet-evening",
                   "young-pilots-ship-quarters-letters-lamp", "blackout-house-candle-family-night", "honolulu-christmas-1941-quiet-blackout", "mess-attendant-white-jacket-wardroom"],
    "vuur": ["sugar-cane-fields-wind-plantation-houses"],
    "vonken": ["white-house-lawn-christmas-tree-evening", "hawaiian-musicians-ukulele-evening-lanai"],
    "sterren": ["moonlit-harbour-battleships-silhouettes", "movie-screen-deck-sailors-stars", "sailor-rail-night-harbour-lights-thinking"],
    "vuurvliegjes": ["wooden-house-porch-valley-rain-evening", "navy-family-small-house-garden-evening", "steel-guitar-player-porch-evening"],
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
