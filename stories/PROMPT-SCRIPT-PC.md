# Scriptgenerator op de pc (automatisch, eigenaar 8 nov 2026: "Kun jij geen script generator maken voor de pc")

Start met: "Lees stories/PROMPT-SCRIPT-PC.md en voer het uit" (in een sessie op de pc, of later als dagelijkse taak als de
eigenaar die zelf aanzet). Werk af zonder te vragen. **Eén script per run.**
Alleen tekst: geen beelden, geen stem, geen video, niets wat geld kost. De videokaart niet gebruiken.

## 0. Begin
`git checkout main && git pull`. Lees CLAUDE.md, stories/OPBOUW.md en deze prompt.

## 1. Welk script
Kies in deze volgorde (datum = regel `datum` in planning.txt; alleen datums **vanaf vandaag + 2 dagen**):
1. **Ombouwen**: het `stories/*/planning.txt` met `status   script-klaar` waarin **niet** "nieuwe opbouw" staat, met de
   **vroegste datum**. (Reservescripts met `datum    reserve (geen datum)` pas als er geen gedateerde meer over zijn.)
2. Is alles al omgebouwd: **schrijf een nieuw script** voor de eerstvolgende datum in de "Nieuwe planning" van
   stories/ONDERWERPEN.md waarvoor nog geen map bestaat (zoals stories/PROMPT-SCRIPT-VOORUIT.md stap "Welk script").
3. Is er niets te doen: schrijf één regel in stories/ROUTINE-LOG.md en stop.

## 2. Ombouwen (zelfde onderwerp en feiten, nieuwe opbouw)
Lees het oude script (`src/*.txt` of `script-cues.txt`, plus `prompts.txt`). Maak in dezelfde map
`src-feiten/` precies volgens stories/OPBOUW.md, voorbeeld stories/egypte-toetanchamon/src-feiten/:
- `begin.txt`: begin van ± 250-300 woorden. Kies een **andere soort opening** dan de vorige video in de planning
  (regel `opening` in de planning.txt van de video met de datum ervoor): scène, mythe, persoon, voorwerp of raadsel.
  Geen "Tonight", geen "Hello". Met grote vraag, zachte abonneer-zin, reactievraag ("where are you listening from, and
  what time is it there?") en settle in.
- `deel1.txt`, `deel2.txt`, `deel3.txt`: 8-13 onderwerpen (`TOPIC:` + `BRIDGE:`), samen **± 85-95 feitjes**
  (`IMG: <slug> | <beeldbeschrijving in het Engels>` / `HEAD:` / `BODY:` van ± 150-220 woorden), blokken gescheiden door `===`.
  Gebruik de feiten en de rustige toon van het oude script; niets verzinnen. Korte zinnen, weinig jaartallen.
- `slot.txt`: ± 120-160 woorden, uitdoven naar een slaapbeeld, "another ... story ... on the screen", kort abonneren,
  als laatste "Sleep well, and good night."
- `stijl.txt`: één stijlzin voor alle beelden van dit onderwerp (tijd, plaats, materialen, kleding, "Cinematic realistic
  photograph, wide 16:9 landscape, soft natural light, calm and peaceful mood, no text, no letters, no logos").
  **Beschrijf wat er wél is**; schrijf nooit "no cars"/"no modern ..." (dan tekent het model ze juist).
  De beeldbeschrijving bij IMG: wat er te zien is, liefst avondlicht (lamp, vuur, schemering).
- `bouw_script.py`: kopie van stories/egypte-toetanchamon/bouw_script.py. Draai `python stories/<map>/bouw_script.py`:
  dat maakt script-cues.txt, hoofdstukken.tsv, prompts.txt en afbeeldingen-onderwerpen.tsv.
  Controleer: ± 85-95 feitjes, ± 16.000-18.000 woorden, "begin ja", "slot ja", en `python tools/check_afwisseling.py stories/<map>` = AFWISSELING GOED (anders de gemelde zinnen helemaal anders schrijven).
- `maak_motion.py`: kopie van stories/egypte-toetanchamon/maak_motion.py; pas alleen de data, kaart, tijdlijn en
  effecten aan dit onderwerp aan (slugs zonder nummer, zoals in de IMG-regels). Hoofdstukken komen uit hoofdstukken.tsv.
- `youtube-beschrijving.txt`: volgens stories/YOUTUBE-STANDAARD.md, **zonder regen** ("deep and warm 432 Hz music in the
  background"), precies 15 hashtags, bij "Chapters" de TOPIC-titels als `0:00:00 <naam>`.
- Laat de oude bestanden (src/, oude bouw_script) staan; de nieuwe bouw_script.py vervangt de oude.

## 3. Planning bijwerken
In planning.txt van die map:
- `status   script-klaar (nieuwe opbouw, <datum vandaag>, scriptgenerator pc)`
- `titel    <vraag-titel> | History for Sleep` (zonder uren; andere `titelsoort` dan de vorige video)
- `opening   <soort>` en `titelsoort <soort>` (zie OPBOUW.md "Afwisseling")
- Staat er `thumbnail gekozen ...` met uren of oude tekst op het beeld, zet er dan bij: `thumbnail opnieuw maken (geen uren)`.

## 4. Klaar
Commit **alleen die map** (en eventueel ROUTINE-LOG.md) met een duidelijke boodschap, `git pull --rebase`, push naar main.
Schrijf in stories/ROUTINE-LOG.md één regel: datum, map, "omgebouwd" of "nieuw geschreven", aantal feitjes en woorden.
Lukt iets niet, zet dan niets half op main: schrijf in ROUTINE-LOG.md wat er misging.
