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
    {"soort": "datum", "tijd": na("city-walls-towers-gates-tuscan-hills", 15), "regel1": "Spring, 1347", "regel2": "Florence, Tuscany"},
    {"soort": "datum", "tijd": na("summer-1347-wheat-harvest-golden-hills", 20), "regel1": "Summer, 1347", "regel2": "The Tuscan countryside"},
    {"soort": "datum", "tijd": na("ships-arriving-sicily-harbour-autumn", 20), "regel1": "October, 1347", "regel2": "Messina, Sicily"},
    {"soort": "datum", "tijd": na("pope-seated-between-two-great-fires-calm", 20), "regel1": "January, 1348", "regel2": "Avignon"},
    {"soort": "datum", "tijd": na("penitent-procession-candles-hymns-street", 20), "regel1": "Spring, 1348", "regel2": "Florence"},
    {"soort": "datum", "tijd": na("english-village-thatched-cottages-church-summer", 20), "regel1": "June, 1348", "regel2": "Melcombe, England"},
    {"soort": "datum", "tijd": na("medieval-wedding-procession-musicians-flowers", 20), "regel1": "Spring, 1349", "regel2": "Florence"},
    {"soort": "kaart", "tijd": na("caravan-steppe-camels-dusk-distant", 10), "titel": "The road of the sickness, 1346-1349",
     "gebied": [-6.0, 36.0, 34.0, 62.0],
     "plaatsen": [
         {"naam": "Caffa", "lon": 35.38, "lat": 45.03, "kant": "links"},
         {"naam": "Messina", "lon": 15.55, "lat": 38.19, "kant": "rechts"},
         {"naam": "Florence", "lon": 11.26, "lat": 43.77, "kant": "rechts"},
         {"naam": "Avignon", "lon": 4.81, "lat": 43.95, "kant": "links"},
         {"naam": "London", "lon": -0.13, "lat": 51.51, "kant": "rechts"},
         {"naam": "Bergen", "lon": 5.32, "lat": 60.39, "kant": "rechts"}]},
    {"soort": "tijdlijn", "tijd": na("florence-today-dome-rooftops-morning", 25), "punten": [
        ["1347", "Ships reach Sicily"], ["1348", "The sickness reaches Florence"],
        ["1353", "Boccaccio finishes the Decameron"], ["1436", "The great dome is finished"], ["Today", "The Misericordia still helps"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life in Europe During the Black Death, 1348", "intro": False, "slot": False, "items": items},
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
    "mist": ["florence-arno-river-dawn-1347", "caravan-steppe-camels-dusk-distant", "ships-arriving-sicily-harbour-autumn", "norwegian-fjord-wooden-church-forest-mist",
             "florence-winter-street-worried-merchants", "venice-harbour-officials-ships-waiting-lagoon"],
    "lichtstralen": ["orsanmichele-grain-market-madonna-candles", "baptistery-octagon-golden-mosaic-ceiling", "santa-maria-novella-church-morning-young-women", "hospital-long-hall-beds-nuns-candles",
                     "florence-spring-1348-almond-blossom-hills", "florence-today-dome-rooftops-morning", "painter-fresco-scaffold-church-wall"],
    "stof": ["wool-combers-workshop-long-room-morning", "wool-merchants-counting-house-florins", "cathedral-under-construction-scaffolding-1347", "abacus-school-boys-counting-beads-teacher",
             "apothecary-shop-herbs-jars-rosemary-bundles", "empty-piazza-noon-heat-pigeons", "chronicle-manuscript-pages-illuminated-letters"],
    "kaarslicht": ["old-chronicler-writing-book-study-lamp", "canopy-bed-painted-chest-candle-bedroom", "tavern-storyteller-listeners-candle-laughing", "old-manuscript-virgil-handwritten-note",
                   "unfinished-chronicle-page-quill-resting", "old-surgeon-writing-large-book-candle", "lanterns-shrine-street-corner-dusk", "penitent-procession-candles-hymns-street"],
    "vuur": ["family-supper-firelight-small-room-evening", "mother-servants-kitchen-top-floor-hearth", "pope-seated-between-two-great-fires-calm"],
    "vonken": ["cook-roasting-crane-kitchen-fire-pretty-girl"],
    "sterren": ["quiet-garden-twilight-fig-tree-roses", "italian-hill-village-quiet-dusk-church"],
    "vuurvliegjes": ["villa-garden-fountain-view-florence-hills", "fiesole-hill-view-florence-valley-evening", "arno-riverbank-summer-evening-swimmers-poplars", "poet-house-arqua-hills-vineyards-evening"],
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
