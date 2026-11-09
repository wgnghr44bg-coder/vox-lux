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
    {"soort": "datum", "tijd": na("ten-roads-countryside-aerial", 15), "regel1": "Spring, 1863", "regel2": "Gettysburg, Pennsylvania"},
    {"soort": "datum", "tijd": na("confederate-soldiers-march-rain-town", 20), "regel1": "June 26, 1863", "regel2": "Gettysburg"},
    {"soort": "datum", "tijd": na("union-cavalry-riding-through-town-cheering", 20), "regel1": "June 30, 1863", "regel2": "Washington Street"},
    {"soort": "datum", "tijd": na("townspeople-rooftops-watching-distant-smoke", 20), "regel1": "July 1, 1863", "regel2": "Gettysburg"},
    {"soort": "datum", "tijd": na("officer-on-rocky-hilltop-telescope", 20), "regel1": "July 2, 1863", "regel2": "Little Round Top"},
    {"soort": "datum", "tijd": na("small-brick-house-kitchen-bread-dough", 20), "regel1": "July 3, 1863", "regel2": "Baltimore Street"},
    {"soort": "datum", "tijd": na("white-tent-hospital-rows-trees", 20), "regel1": "Summer, 1863", "regel2": "Camp Letterman"},
    {"soort": "datum", "tijd": na("dinner-table-lamplight-guests-1863", 20), "regel1": "November 18, 1863", "regel2": "The Wills house"},
    {"soort": "datum", "tijd": na("veterans-reunion-1913-handshake", 20), "regel1": "July, 1913", "regel2": "Gettysburg"},
    {"soort": "kaart", "tijd": na("night-camp-tents-stars-hills", 10), "titel": "Ten roads into Gettysburg, June 1863",
     "gebied": [-79.0, 38.6, -75.8, 40.6],
     "plaatsen": [
         {"naam": "Gettysburg", "lon": -77.23, "lat": 39.83, "kant": "links"},
         {"naam": "Chambersburg", "lon": -77.66, "lat": 39.94, "kant": "links"},
         {"naam": "Harrisburg", "lon": -76.88, "lat": 40.27, "kant": "rechts"},
         {"naam": "York", "lon": -76.73, "lat": 39.96, "kant": "rechts"},
         {"naam": "Baltimore", "lon": -76.61, "lat": 39.29, "kant": "rechts"},
         {"naam": "Washington", "lon": -77.04, "lat": 38.90, "kant": "links"}]},
    {"soort": "tijdlijn", "tijd": na("gettysburg-battlefield-today-monuments", 25), "punten": [
        ["July 1863", "Three days of battle"], ["Nov 1863", "Lincoln's few words"], ["1865", "The war ends"],
        ["1889", "Tillie writes her book"], ["1913", "The great reunion"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Gettysburg, July 1863", "intro": False, "slot": False, "items": items},
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
    "mist": ["misty-dawn-fields-west-of-town", "rainy-june-afternoon-street", "rain-falling-town-dawn-july", "white-smoke-cloud-over-fields-distant",
             "presidential-train-countryside-november", "wagon-train-rain-night-mountain-road"],
    "lichtstralen": ["church-sunday-families-1863", "church-turned-hospital-women-water", "lutheran-seminary-gardens-students-walking", "young-teacher-sitting-with-soldier",
                     "carriage-workshop-painter-gold-lines", "sewing-circle-women-open-windows", "national-cemetery-curved-rows-trees-evening"],
    "stof": ["general-store-counter-1863", "army-column-marching-dusty-road", "soldiers-crowding-farm-pump-heat", "young-ladies-seminary-classroom-desks",
             "old-man-cobbler-workshop", "hot-morning-baltimore-street-quiet"],
    "kaarslicht": ["girl-window-candle-night", "family-cellar-candle-preserves-jars", "small-farmhouse-lamplit-generals-night", "telegram-reading-candlelight",
                   "general-meade-tent-maps", "professor-colonel-writing-letter-tent", "family-reading-letter-parlour-lamp", "elderly-statesman-library-books-lamp",
                   "dinner-table-lamplight-guests-1863"],
    "vuur": ["mother-cookstove-breakfast-children", "washday-iron-kettle-backyard-line", "evening-camp-coffee-fires-harmonica"],
    "vonken": ["young-soldiers-faces-campfire-night", "cavalry-campfires-fields-dusk"],
    "sterren": ["night-camp-tents-stars-hills", "night-town-lamps-every-window", "crowd-serenade-house-night-band"],
    "vuurvliegjes": ["front-step-evening-neighbours", "june-fields-wheat-golden-farmhouse", "battlefield-dusk-deer-fields-fireflies", "round-tops-wooded-hills-dusk"],
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
