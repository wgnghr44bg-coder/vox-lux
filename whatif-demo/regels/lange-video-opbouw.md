# Lange video's: vaste opbouw (eigenaar, 7 okt 2026)

Voorbeeld: "What if the Sun went out?" v3 (`topics/sun-c1-beach` … `sun-c4-coast`, script van de eigenaar).
Deze regels gaan vóór de oudere regels over lengte en opening in AUTOMATISCH.md.

## Lengte
- ± 3–4 minuten, 3–4 hoofdstukken van ± 1 min, elk op een andere plek. Pas naar 8+ min als het kanaal
  gemonetiseerd is of als de kijkduur (Betrokkenheid) laat zien dat kijkers tot het eind blijven.

## Verhaal: sprongen in de tijd, stap voor stap erger
- Opening (haak): "Imagine …" over het onderwerp, dan wat het níet is en de verrassing
  (bijv. "Not exploding. Not slowly disappearing. Just… gone." / "But here's the terrifying part.").
- Daarna stappen die steeds erger worden, met een duidelijke marker die de stem uitspreekt én die in beeld staat.
  Dat kan tijd zijn (DAY 1 → MONTH 1 → YEAR 1,000) maar ook iets anders, passend bij het onderwerp
  (bijv. 100 °C → 500 °C → 1.000 °C bij vuur, 50 → 300 km/u bij wind, 1 m → 50 m bij water).
- Elke stap is erger dan de vorige; feiten met getallen erbij (zoals gravity: "−17 °C na een week").
- Elk hoofdstuk eindigt met een cliffhanger-zin ("But this is only the beginning.", "But then comes the truly terrifying part.").
- Slot: de grootste climax in het laatste hoofdstuk, dan een vraag aan de kijker
  ("How long do you think humanity would actually survive?").
- Per hoofdstuk één stille climax van 5–6 s (getal als pauze in `lines`).

## Beeld: gravity-stijl
- Toeschouwer-shots (wijd, stabiel, `tripod: true`), geen POV.
- Titelkaart bij de start (`showTitle: true`, `title`, `titleOut`) en eindkaart in het laatste hoofdstuk
  (`end: { title, lines }` met `beats.end`/`beats.dark`).
- Teller in beeld, passend bij het onderwerp (eigenaar): de grootheid die het verhaal drijft, bijv.
  vuur/hitte → °C/°F, wind → km/u, water → meters, zwaartekracht → g, licht → %, aardbeving → magnitude,
  tijd → dag/jaar. Eronder eventueel een tweede regel (bijv. °F of "YOU WEIGH" zoals bij gravity) en, als het
  verhaal in tijdsprongen loopt, de tijdstap: `hud.subAt: [[t, 'DAY 1'], …]` (engine/hud.js).
- Wat de stem zegt, moet je zien (lichten aan, mensen kijken omhoog, auto stopt, meer bevriest …).

## Variatie (nooit hetzelfde)
- Nooit zinnen overnemen uit eerdere video's; ook de haak- en cliffhanger-zinnen per video anders verwoorden.
- Geen hoogtepunt of beeld herhalen uit "Al gebruikt" (onderwerpen.md); zeker niet weer de bevroren rivier/brug.
- Elke video andere plekken-volgorde en andere tijdstappen.

## Stem, pauzes en geluid (eigenaar, 7 okt 2026 – na de Sun-video v3)
- Rustig maar niet stilvallen (eigenaar, 7 okt 2026: "zonder pauzes voelt het gehaast"): tussen zinnen een korte
  pauze (`'pause'`), na een belangrijke zin of bij een nieuwe stap (DAY 1, WEEK 1 …) `'long'`. Nooit langer dan
  ± 1 s stil, behalve de stille climax (± 3 s, mét actie in beeld).
  Hoofdstukken eindigen ± 1,5 s na de laatste zin (geen lange staart; cross-fade 1 s).
  Dit gaat vóór "mét alle pauzes" in AUTOMATISCH.md.
- Geen gekraak: bij kou `audio: { hiss: -40, ice: -32 }` in scenario.js (vorst-sis uit, ijs zacht).
- Beeld vloeiend met de stem: shot wisselen per stap (± elke 5–10 s), niet bij elke zin.

- Stem in één keer (eigenaar, 7 okt 2026): make_whatif.py laat de hele tekst in één xAI-aanvraag inspreken
  (`one_take`, standaard aan; `oneTake: false` in topic = oude manier per zin). De stem maakt zelf de pauzes; de
  zinstijden komen uit de stiltes. Klinkt veel natuurlijker dan los geknipte zinnen.

## Eenheden: Europees (eigenaar, 9 okt 2026)
- Alleen °C (geen °F), meters/kilometers, km/u, kilo, 24-uursklok (12:08, niet 12:08 PM). Ook in de stem en ondertitels.

## Inhoud en veiligheid
- Alleen natuurkunde die klopt; twijfel = weglaten. Geen geweld in tekst ("fighting" → "compete").
- Geen gewonden of lichamen in beeld.

## Werkwijze met de eigenaar
- Eerst lezen wat de eigenaar stuurt en vragen beantwoorden, dán pas verder werken.
- De eigenaar mag een eigen script sturen: feiten checken, kleine aanpassingen voorstellen, akkoord vragen.
- Eerst een proef van ± 1 min (hoofdstuk 1) sturen; na akkoord de rest.
- Niets uploaden of inplannen zonder akkoord. Usage boven 85%: alleen met uitdrukkelijk akkoord van de eigenaar.
- Korte berichten in het Nederlands.

## Shots die niet werken (getest)
- `mountain-village`: `village`, `square`, `church`, `lakeside` worden geblokkeerd door huizen/daken → gebruik `wide`, `lake`, `mountains`.
- `boulevard`: `wide` heeft een palm vooraan (in het donker een zwart silhouet) → bij nacht liever `sea`, `beach`, `hotels`.

## Shorts: dezelfde opbouw, korter (eigenaar, 7 okt 2026)
- Shorts volgen dezelfde opbouw (haak "Imagine …", stappen die erger worden met marker in beeld, teller passend
  bij het onderwerp, feiten met getallen, cliffhanger-zin, vraag aan de kijker aan het eind), maar korter:
  ± 60–90 s, 1 plek (hooguit 2), 3–4 stappen, één stille climax.
- De A/B-test (`regels/stijl-afwisseling.md`) blijft: alleen de camera verschilt (A = POV, B = toeschouwer/gravity).
