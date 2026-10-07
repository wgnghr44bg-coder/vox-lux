# Lange video's: vaste opbouw (eigenaar, 7 okt 2026)

Voorbeeld: "What if the Sun went out?" v3 (`topics/sun-c1-beach` … `sun-c4-coast`, script van de eigenaar).
Deze regels gaan vóór de oudere regels over lengte en opening in AUTOMATISCH.md.

## Lengte
- ± 3–4 minuten, 3–4 hoofdstukken van ± 1 min, elk op een andere plek. Pas naar 8+ min als het kanaal
  gemonetiseerd is of als de kijkduur (Betrokkenheid) laat zien dat kijkers tot het eind blijven.

## Verhaal: sprongen in de tijd, stap voor stap erger
- Opening (haak): "Imagine …" over het onderwerp, dan wat het níet is en de verrassing
  (bijv. "Not exploding. Not slowly disappearing. Just… gone." / "But here's the terrifying part.").
- Daarna tijdsprongen met een duidelijke marker die de stem uitspreekt én die in beeld staat,
  bijv. DAY 0 → DAY 1 → DAY 3 → DAY 7 → MONTH 1 → YEAR 1 → YEAR 100 → YEAR 1,000 (passend bij het onderwerp).
- Elke stap is erger dan de vorige; feiten met getallen erbij (zoals gravity: "−17 °C na een week").
- Elk hoofdstuk eindigt met een cliffhanger-zin ("But this is only the beginning.", "But then comes the truly terrifying part.").
- Slot: de grootste climax in het laatste hoofdstuk, dan een vraag aan de kijker
  ("How long do you think humanity would actually survive?").
- Per hoofdstuk één stille climax van 5–6 s (getal als pauze in `lines`).

## Beeld: gravity-stijl
- Toeschouwer-shots (wijd, stabiel, `tripod: true`), geen POV.
- Titelkaart bij de start (`showTitle: true`, `title`, `titleOut`) en eindkaart in het laatste hoofdstuk
  (`end: { title, lines }` met `beats.end`/`beats.dark`).
- Teller in beeld met de tijdsmarker eronder: `hud.subAt: [[t, 'DAY 1'], …]` (engine/hud.js), plus een
  tweede regel (bijv. °F, of W/m²) zoals "YOU WEIGH" bij gravity.
- Wat de stem zegt, moet je zien (lichten aan, mensen kijken omhoog, auto stopt, meer bevriest …).

## Variatie (nooit hetzelfde)
- Nooit zinnen overnemen uit eerdere video's; ook de haak- en cliffhanger-zinnen per video anders verwoorden.
- Geen hoogtepunt of beeld herhalen uit "Al gebruikt" (onderwerpen.md); zeker niet weer de bevroren rivier/brug.
- Elke video andere plekken-volgorde en andere tijdstappen.

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
