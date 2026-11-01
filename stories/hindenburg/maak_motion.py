#!/usr/bin/env python3
"""Maakt motion.json (hoofdstukken, data, kaart, tijdlijn), effecten.tsv en youtube-beschrijving.txt
uit afbeeldingen-tijden-pauzes.tsv. Hoofdstuk = eerste beeld van elk bestand in src/."""
import csv, json, re
from pathlib import Path

d = Path(__file__).parent
rows = list(csv.DictReader(open(d / "afbeeldingen-tijden-pauzes.tsv", encoding="utf-8"), delimiter="\t"))
start = {r["slug"]: float(r["start"]) for r in rows}

TITELS = {
    "01": "Evening at Frankfurt", "02": "The Count and the Dream", "03": "Building the Hindenburg",
    "04": "The First Year", "04b": "How an Airship Floats", "04c": "The Road to Brazil",
    "05": "Boarding the Ship", "06": "The Passenger Decks", "07": "Below Deck", "08": "The Crew",
    "09": "The First Night", "10": "Tuesday over the Atlantic", "11": "The Second Night",
    "12": "Thursday Morning", "13": "Over New York", "14": "Waiting for the Storm",
    "15": "Lakehurst", "16": "The Landing", "17": "The Days After", "18": "What Remains",
    "19": "Friedrichshafen Today", "20": "Remembering the Airships", "21": "Goodnight, Hindenburg",
}
kapitels = []
for p in sorted((d / "src").glob("[0-9]*.txt")):
    key = re.match(r"\d\d[bc]?", p.name).group()
    slug = re.findall(r"\{img:([^}]+)\}", p.read_text(encoding="utf-8"))[0]
    kapitels.append((TITELS[key], start[slug]))

items = [{"soort": "hoofdstuk", "tijd": 10 if n == 1 else round(t + 3, 1), "nummer": n, "titel": titel}
         for n, (titel, t) in enumerate(kapitels, 1)]


def na(slug, s=25):
    return round(start[slug] + s, 1)


items += [
    {"soort": "datum", "tijd": na("airship-frankfurt-evening", 60), "regel1": "3 May 1937  ·  Evening", "regel2": "Frankfurt, Germany"},
    {"soort": "datum", "tijd": na("first-flight-over-lake-constance", 20), "regel1": "4 March 1936", "regel2": "Lake Constance"},
    {"soort": "datum", "tijd": na("engines-starting-propellers-turning", 25), "regel1": "3 May 1937  ·  8 pm", "regel2": "The airfield at Frankfurt"},
    {"soort": "datum", "tijd": na("sunrise-over-the-atlantic-from-window", 15), "regel1": "4 May 1937  ·  Morning", "regel2": "The North Atlantic"},
    {"soort": "datum", "tijd": na("fishing-village-seen-from-above", 5), "regel1": "5 May 1937  ·  Afternoon", "regel2": "Newfoundland"},
    {"soort": "datum", "tijd": na("new-york-skyline-from-the-harbour-afternoon", 20), "regel1": "6 May 1937  ·  Afternoon", "regel2": "New York"},
    {"soort": "datum", "tijd": na("lakehurst-naval-air-station-hangar-evening", 25), "regel1": "6 May 1937  ·  Evening", "regel2": "Lakehurst, New Jersey"},
    {"soort": "kaart", "tijd": na("sunrise-over-the-atlantic-from-window", 160), "titel": "Frankfurt to Lakehurst, 1937",
     "gebied": [-82, 36, 16, 58],
     "plaatsen": [
         {"naam": "Frankfurt", "lon": 8.68, "lat": 50.11, "kant": "onder"},
         {"naam": "Ireland", "lon": -8.2, "lat": 52.9, "kant": "boven"},
         {"naam": "Newfoundland", "lon": -55.5, "lat": 48.5, "kant": "boven"},
         {"naam": "Boston", "lon": -71.06, "lat": 42.36, "kant": "boven"},
         {"naam": "New York", "lon": -74.0, "lat": 40.71, "kant": "rechts"},
         {"naam": "Lakehurst", "lon": -74.33, "lat": 40.03, "kant": "onder"}],
     "route": [[8.68, 50.11], [2.0, 52.0], [-8.2, 52.5], [-30, 50.5], [-52.5, 47.0], [-63, 44.5], [-71.06, 42.36],
               [-74.0, 40.71], [-74.33, 40.03]]},
    {"soort": "tijdlijn", "tijd": na("graf-zeppelin-resting-in-hangar-1937", 40), "punten": [
        ["1900", "The first Zeppelin flies"], ["1929", "Around the world"],
        ["1936", "The Hindenburg's first flight"], ["1937", "The last crossing"]]},
]
items.sort(key=lambda i: i["tijd"])
json.dump({"onderwerp": "Life Aboard the Hindenburg, May 1937", "intro": True, "slot": True, "items": items},
          open(d / "motion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# effecten per beeld, op woorden in de slug (geen vuur of rook bij de landing)
regels = [
    (("stars", "night", "lamps-on-the-field"), [("sterren", 0.7)]),
    (("tea", "cabin", "lounge", "smoking", "writing", "kitchen", "baker", "radio-room", "dinner", "album", "letters-on"), [("kaarslicht", 0.6)]),
    (("dawn", "sunrise", "sea", "coast", "shore", "lake", "rhine", "canal", "mist", "fishing", "biscay", "cape-verde", "atlantic"), [("mist", 0.5)]),
    (("evening", "sunset", "dusk", "twilight", "golden", "clouds", "afternoon"), [("lichtstralen", 0.6)]),
    (("hall", "hangar", "keel", "store", "museum", "room", "workers", "gas-cell", "riveting", "covering"), [("stof", 0.6)]),
    (("farmland", "garden", "field", "meadow"), [("vuurvliegjes", 0.4)]),
]
uit = ["van\ttot\teffect\tsterkte\tx\ty"]
for r in rows:
    if any(w in r["slug"] for w in ("landing-lines", "ground-crew-hurrying", "evening-sky-over-the-lakehurst")):
        continue
    for woorden, effecten in regels:
        if any(w in r["slug"] for w in woorden):
            for e, s in effecten:
                uit.append(f"{float(r['start']):.2f}\t{float(r['end']):.2f}\t{e}\t{s}\t\t")
            break
(d / "effecten.tsv").write_text("\n".join(uit) + "\n", encoding="utf-8")


def hms(x):
    h, rest = divmod(int(x), 3600)
    return f"{h}:{rest // 60:02d}:{rest % 60:02d}"


tekst = f"""Drift off to the quiet days of a journey aboard the airship Hindenburg, from the evening she rose from the airfield at Frankfurt in May 1937 to the green fields of New Jersey. A calm history for sleep.
Walk the passenger decks with the stewards and the cabin boy, listen to the engines at night, watch the coast of Newfoundland and the towers of New York from the promenade windows, and follow the last evening at Lakehurst slowly and from a distance, to the quiet places that remember her today.

A calm, slow-paced history documentary for sleep and relaxation. No loud
sounds, no jump scares, just a gentle voice, soft 432 Hz background music
with smooth, gentle rain sounds and softly changing images.

Chapters
""" + "\n".join(f"{hms(0 if n == 1 else t + 3)} {titel}" for n, (titel, t) in enumerate(kapitels, 1)) + """

#sleepdocumentary #hindenburg #historyforsleep #sleepstory #rainsounds #432hz #boringhistory #bedtimestory #fallasleep #relaxinghistory #sleepsounds #sleepmusic #zeppelin #airship #calmhistory
"""
(d / "youtube-beschrijving.txt").write_text(tekst, encoding="utf-8")
print(len(items), "items,", len(uit) - 1, "effecten,", len(kapitels), "hoofdstukken")
