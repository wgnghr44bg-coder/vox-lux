# Vaste opbouw van elke video (eigenaar 7 nov 2026: "zoals je zegt houden we het zo")

Gemaakt na het vergelijken van de grote slaapkanalen (Sleepy History Channel, Sleepy History with Oliver,
Dusk Voyages, Boring History Secrets, Sleepless Historian, Just About Earth, Sleepy Time Historian). Ze volgen
allemaal hetzelfde recept. Wij doen dat ook, met twee eigen keuzes: **geen "Tonight"/"Hello"** (eigenaar 7 nov:
meteen beginnen) en de **B1-stem met achtergrondmuziek**.

Het recept is elke video hetzelfde; de woorden en beelden zijn elke keer anders.

## Titel
Een vraag over hoe het echt was, eindigend op ` | History for Sleep`, zonder uren, ± 50-70 tekens.
Wissel de soort af (nooit twee keer dezelfde soort na elkaar):
"What Was Life Really Like in …?", "How Did People Survive …?", "What Did … Actually …?", "Why Did …?",
"What Happened to … After …?".

## 1. Begin (± 2 minuten, ± 250-300 woorden)
In deze volgorde:
1. **Opening in de jij-vorm**, meteen in het onderwerp. Wissel de soort af (nooit twee keer dezelfde na elkaar):
   - een scène ("Imagine stepping down from a dusty stagecoach in the autumn of 1881…")
   - een mythe die niet klopt ("We picture cavemen running from tigers. But the truth was quieter…")
   - één persoon ("In November 1922, a man held a candle up to a small hole in a wall…")
   - één voorwerp ("On the brow of a golden coffin lay a small wreath of dried flowers…")
   - een raadsel ("About 700 people survived that night, and they could not agree on what they saw.")
2. **De grote vraag** van de video, rustig gesteld, en één zin waar we heen gaan ("Stay with me, and we'll find out.").
3. **Zachte abonneer-zin zonder druk**, elke keer anders verwoord
   ("If you enjoy these slow journeys, subscribing helps, but only if tonight's story earns it.").
4. **Vraag voor de reacties**: waar luister je vandaan en hoe laat is het daar (elke keer anders verwoord).
5. **Settle in**: lichten dimmen, ademhaling vertragen, gemakkelijk liggen (2-3 korte zinnen).
6. Dan zonder overgang het eerste onderwerp.

## 2. Midden (± 2,5 uur, ± 16.000-18.000 woorden)
- **8-12 onderwerpen** ("hoofdstukken"), elk ± 12-20 minuten, die als één reis in elkaar overlopen.
  Soms 8 lange, soms 12 kortere: wissel af.
- Elk onderwerp begint met **een overgangszin of twee** (BRIDGE) die het vorige zacht afsluit en het nieuwe opent
  ("The fields are quiet now. But in the city across the river, something else is stirring.").
- Elk onderwerp bestaat uit **6-10 feitjes**, elk met een eigen beeld (± elke 1,5-2 minuten):
  een kopzin die zelf al verrast (HEAD), dan ± 150-220 woorden rustige uitleg (BODY): wat er was, hoe het werkte,
  een nuance met "Yet…" of "That does not mean…", en een stille slotgedachte.
- **Toon**: alsof je het een vriend vertelt. Af en toe de jij-vorm ("You would notice your breath…") en af en toe
  een vraag aan de luisteraar ("Would you have trusted that?"). Mythe tegenover werkelijkheid waar het past.
  Echte mensen en echte bronnen (een brief, een dagboek, een vondst).
- Korte, gewone zinnen (8-15 woorden), weinig namen en jaartallen, niets wat je moet onthouden om verder te kunnen.
  Spanning alleen waar het verhaal zelf spannend is, en dan rustig. Geen gruwelijke details, geen schrikmomenten.

## 3. Einde (± 1 minuut, ± 120-160 woorden)
- **Uitdoven, geen nieuwe feiten**: terug naar een slaapbeeld dat bij het onderwerp past (een kampvuur dat
  uitdooft, lampen die doven, sterren boven de woestijn, de Nijl in het donker). Kortere zinnen.
- Eén zin dat er nog een rustig verhaal klaarstaat (moet "another ... story/video ... on the screen" bevatten,
  voor de QC) en kort abonneren.
- Als laatste: "Sleep well, and good night."

## Afwisseling (zodat het niet eentonig wordt)
**Eigenaar 8 nov 2026: "zorgen dat de opbouw goed blijft maar niet alles hetzelfde klinkt".** De opbouw is altijd gelijk,
de woorden nooit. Schrijf de abonneer-zin, de reactievraag, settle in, de overgangszinnen en het slot **elke video
helemaal opnieuw** (andere zinsbouw en andere beelden, niet alleen één woord anders: dus niet steeds "If you enjoy these
… journeys into the past", "But only if this story earns it", "There is nothing left to follow"). Alleen "Sleep well,
and good night." blijft altijd hetzelfde.
**Verplicht vóór een script klaar is**: `python tools/check_afwisseling.py stories/<map>` moet `AFWISSELING GOED`
geven (vergelijkt begin, slot en overgangszinnen met alle andere video's, en opening/titelsoort met de vorige video).

Kijk naar de laatste 3 video's (planning.txt, regel `opening` en `titelsoort`) en kies een **andere** soort
opening en titel. Wissel ook het soort onderwerp (dagelijks leven, ramp/mysterie, persoon, plek, oorlog), het aantal
onderwerpen en het slotbeeld. Zet in planning.txt:
```
opening   scène | mythe | persoon | voorwerp | raadsel
titelsoort life-really-like | how-survive | what-actually | why | what-happened
```

## Bestanden (zo leest bouw_script.py het)
In `stories/<map>/src-feiten/`:
- `begin.txt`: het begin (alinea's gescheiden door een lege regel = korte pauze).
- `deel1.txt`, `deel2.txt`, …: blokken gescheiden door een regel `===`. Twee soorten blokken:
  ```
  TOPIC: <hoofdstuktitel voor de beschrijving>
  BRIDGE: <1-2 overgangszinnen, gesproken vóór het volgende feitje>
  ===
  IMG: <slug> | <korte beeldbeschrijving in het Engels>
  HEAD: <verrassende kopzin>
  BODY: <± 150-220 woorden>
  ===
  ```
  Elk TOPIC-blok staat vóór het eerste feitje van dat onderwerp; het eerste onderwerp heeft geen BRIDGE nodig.
- `slot.txt`: het einde (alinea's gescheiden door een lege regel).
Voorbeeld: `stories/ww2-facts/`, `stories/tombstone-1881/`, `stories/egypte-toetanchamon/`.
