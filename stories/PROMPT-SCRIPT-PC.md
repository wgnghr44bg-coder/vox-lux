# Scripts maken: één recept voor iedereen (eigenaar 8 nov 2026)

Dit voorschrift gebruiken **de scriptgenerator op de pc**, **het tweede account** (via PROMPT-SCRIPT-VOORUIT.md) en
**de routine** (als die zelf een script moet ombouwen). Zo doet iedereen precies hetzelfde en maakt het niet uit wie
het script schrijft (eigenaar 8 nov: "Doet de generator precies hetzelfde als wat het 2e account zou doen?").

Start: "Lees stories/PROMPT-SCRIPT-PC.md en voer het uit". Werk af zonder te vragen. **Eén script per keer.**
Alleen tekst: geen beelden, geen stem, geen video, niets wat geld kost, de videokaart niet gebruiken.

## 0. Begin
`git checkout main && git pull`. Lees CLAUDE.md, stories/OPBOUW.md en dit voorschrift.
Wie ben je? Zet dat straks in de status: `scriptgenerator pc`, `tweede account` of `routine`.

## 1. Welk script
Alleen datums **vanaf vandaag + 2 dagen** (datum = regel `datum` in planning.txt). In deze volgorde:
1. **Ombouwen**: het `stories/*/planning.txt` met `status   script-klaar` waarin **niet** "nieuwe opbouw" staat, met de
   **vroegste datum**. Reservescripts (`datum    reserve (geen datum)`) pas als er geen gedateerde meer over zijn.
2. Is alles omgebouwd: **nieuw schrijven** voor de eerstvolgende datum uit de "Nieuwe planning" in
   stories/ONDERWERPEN.md waarvoor nog geen map in stories/ bestaat. Een datum met "vrij" of "de routine kiest" sla je
   over (die kiest de routine op hype). Controleer dat het onderwerp nog niet op het kanaal staat ("Al gemaakt").
3. Niets te doen: één regel in stories/ROUTINE-LOG.md en stop.

## 2. Het script maken (ombouwen én nieuw: dezelfde bestanden)
**Ombouwen**: lees het oude script (`src/*.txt` of `script-cues.txt`, plus `prompts.txt`) en gebruik die feiten en die
rustige toon; niets verzinnen. Laat de oude bestanden staan. **Nieuw**: maak een map `stories/<korte-naam>/` en
schrijf uit eigen kennis; alleen feiten die kloppen.

In `stories/<map>/src-feiten/`, precies volgens stories/OPBOUW.md (voorbeeld stories/egypte-toetanchamon/src-feiten/):
- `begin.txt` (± 250-300 woorden): opening in de jij-vorm, **andere soort** dan de vorige video (regel `opening` in de
  planning.txt van de video met de datum ervoor): scène, mythe, persoon, voorwerp of raadsel. Geen "Tonight", geen
  "Hello". Dan de grote vraag, een zachte abonneer-zin zonder druk, een reactievraag (waar luister je, hoe laat is het)
  en settle in, **elke keer helemaal anders verwoord** dan in eerdere video's.
- `deel1.txt`, `deel2.txt`, `deel3.txt`: 8-13 onderwerpen (`TOPIC:` + `BRIDGE:`), samen **± 85-95 feitjes**
  (`IMG: <slug> | <beeldbeschrijving in het Engels>` / `HEAD: <verrassende kopzin>` / `BODY: <± 150-220 woorden>`),
  blokken gescheiden door een regel `===`.
- `slot.txt` (± 120-160 woorden): uitdoven naar een slaapbeeld, geen nieuwe feiten, een zin met "another ... story ...
  on the screen" (voor de QC), kort abonneren, en als laatste "Sleep well, and good night."
- `stijl.txt`: één stijlzin voor alle beelden (tijd, plaats, materialen, kleding, en "Cinematic realistic photograph,
  wide 16:9 landscape, soft natural light, calm and peaceful mood, highly detailed, no text, no letters, no logos").
  **Beschrijf wat er wél is**; schrijf nooit "no cars"/"no modern ..." (dan tekent het model ze juist). Bij IMG: wat er
  te zien is, liefst avondlicht (lamp, vuur, schemering); binnen: "an indoor scene, enclosed by walls, a plain ceiling".

Schrijfregels (eigenaar 2 nov 2026): korte, gewone zinnen (8-15 woorden, hooguit ± 2 komma's), gewone woorden, alsof je
het een vriend vertelt. Weinig jaartallen en namen achter elkaar. Af en toe de jij-vorm en een vraag aan de luisteraar;
mythe tegenover werkelijkheid waar het past; echte mensen en bronnen. Spanning alleen waar het verhaal zelf spannend is,
en dan rustig. Geen gruwelijke details, geen schrikmomenten.

**Toon zoals de grote slaapkanalen (eigenaar 11 nov 2026: "Ja doe maar")**: niet als een voorleesboek, maar als iemand
die naast je zit en tegen jóu praat. Voorbeeld: `stories/_toon-proef/gettysburg-nieuwe-toon.txt` (zelfde feiten als het
eerste hoofdstuk van Gettysburg, nieuwe toon). Per hoofdstuk (TOPIC) minstens:
- één stuk in de **jij-vorm** met zintuigen ("You go up the narrow stairs. The steps creak under your feet."), en een
  vaste "jij" door de hele video (een reiziger, een buurmeisje, een nieuwe arbeider) waar je steeds naar teruggaat;
- één **vraag aan de luisteraar** ("Would you have guessed…?", "Could you have slept in a hut like this?");
- af en toe **"You might think… But…"** (mythe tegenover werkelijkheid) en een nuance met "Yet…".
In de hele video ook:
- een paar keer de **verteller als persoon** ("I've always liked that.", "I find that rather comforting, don't you?");
- **spreektaal**: samentrekkingen (it's, there's, you'd, they'll) en praatwoordjes ("Now,", "So,", "Of course,", "Honestly,");
- af en toe een **zachte glimlach** of een vreemd weetje (nooit plat, nooit spot) en **kleine cijfers uit het dagelijks
  leven** (wat iets kostte, hoe lang een wandeling duurde), alleen als ze kloppen.
Blijft gelijk: makkelijk Engels (korte zinnen, gewone woorden), rustig tempo, niets gruwelijks.
**Controle**: `python tools/script_leesbaar.py stories/<map>` moet `MAKKELIJK` én `TOON GOED` geven.

Daarna in `stories/<map>/`:
- `bouw_script.py`: kopie van stories/egypte-toetanchamon/bouw_script.py. Draai `python stories/<map>/bouw_script.py`:
  dat maakt script-cues.txt, hoofdstukken.tsv, prompts.txt en afbeeldingen-onderwerpen.tsv.
- `maak_motion.py`: kopie van stories/egypte-toetanchamon/maak_motion.py; pas alleen de data, kaart, tijdlijn en
  effecten aan dit onderwerp aan (slugs zonder nummer, zoals in de IMG-regels). Hoofdstukken komen uit hoofdstukken.tsv.
- `youtube-beschrijving.txt`: volgens stories/YOUTUBE-STANDAARD.md, **zonder regen** ("deep and warm 432 Hz music in the
  background"), precies 15 hashtags, bij "Chapters" de TOPIC-titels als `0:00:00 <naam>` (de routine vult de tijden in).

**Controles (allemaal verplicht):** ± 85-95 feitjes, ± 16.000-18.000 woorden, "begin ja", "slot ja", en
`python tools/check_afwisseling.py stories/<map>` = `AFWISSELING GOED` (anders de gemelde zinnen helemaal anders
schrijven en opnieuw bouwen), en `python tools/script_check.py stories/<map>` = `SCRIPT GOED` (vorm, woorden die niet bij
de tijd passen, elk feitje en hoofdstuk over het onderwerp; eigenaar 9 nov 2026). De pc controleert dit 's nachts ook zelf
(tools/zelfcontrole.py) en zet een afgekeurd script terug naar ombouwen.

## 3. Planning
In `stories/<map>/planning.txt` (bij nieuw: maak hem aan):
```
onderwerp <onderwerp zoals in ONDERWERPEN.md>
status   script-klaar (nieuwe opbouw, <datum vandaag>, <wie: scriptgenerator pc / tweede account / routine>)
datum    <ma/wo/za datum> 21:00 NL
titel    <vraag-titel> | History for Sleep        (zonder uren; andere titelsoort dan de vorige video)
opening   scène | mythe | persoon | voorwerp | raadsel
titelsoort life-really-like | how-survive | what-actually | why | what-happened
thumbnail amberregel "<plaats of maand · jaar>", hook "<titelwoorden>", beeld: <korte beschrijving>
soort    <playlist-soort voor tools/youtube_playlist.py: ramp, oorlog, reis, ...>
```
Bij ombouwen: laat onderwerp, datum, thumbnail en soort staan, vervang status en titel en voeg opening/titelsoort toe.
Staat er `thumbnail gekozen ...` en heeft dat beeld uren of oude tekst, zet er dan bij: `thumbnail opnieuw maken (geen uren)`.
Thumbnail volgens stories/YOUTUBE-STANDAARD.md: titelwoorden erin, nooit uren, anders dan de laatste 3 thumbnails.

## 4. Klaar
Commit **alleen die map** (en ROUTINE-LOG.md) met een duidelijke boodschap, `git pull --rebase`, push naar main.
Eén regel in stories/ROUTINE-LOG.md: datum, map, "omgebouwd" of "nieuw geschreven", wie, aantal feitjes en woorden.
Lukt iets niet, zet dan niets half op main: schrijf in ROUTINE-LOG.md wat er misging.
