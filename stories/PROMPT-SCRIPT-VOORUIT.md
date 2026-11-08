# Script vooruit schrijven (tweede Claude-account)

De eigenaar wil (1 nov 2026, "Script schrijven dan") dat een tweede Claude-account de scripts voor de
komende video's alvast schrijft. De pc-routine (`stories/PROMPT-ROUTINE-PC.md`) vindt ze dan op main
en maakt er beelden, stem en video van. Zo houdt het hoofdaccount meer ruimte over voor de montage.

**Gebruik:** open Claude Code (web, claude.ai/code, of de desktop-app) met de repo
`wgnghr44bg-coder/vox-lux` op branch `main`, en geef deze opdracht:

> Lees stories/PROMPT-SCRIPT-VOORUIT.md en schrijf het eerstvolgende script dat nog niet klaar is.

Eén script per keer. Het kost niets: je schrijft alleen tekst, je maakt geen beelden en geen stem.

## Welk script
Neem de eerstvolgende datum uit de "Nieuwe planning" in `stories/ONDERWERPEN.md` waarvoor nog geen map
in `stories/` bestaat met een `planning.txt` waarin dat onderwerp staat (kijk op main). Een datum met
"vrij" of "de routine kiest" sla je over: die beslist de routine zelf op de dag, op hype.
Controleer dat het onderwerp nog niet op het kanaal staat (`stories/ONDERWERPEN.md` "Al gemaakt").

## Wat je maakt
Een nieuwe map `stories/<korte-naam>/` (bv. `stories/gettysburg-1863/`), precies volgens **`stories/OPBOUW.md`**
(eigenaar 7 nov 2026: de vaste opbouw van de grote slaapkanalen). Voorbeeld: `stories/egypte-toetanchamon/`.

1. **`src-feiten/begin.txt`, `src-feiten/deel1.txt` … `deel3.txt`, `src-feiten/slot.txt`** in rustig Engels:
   - **Begin** (± 2 min): opening in de jij-vorm (wissel de soort af: scène, mythe, persoon, voorwerp, raadsel; nooit
     dezelfde soort als de vorige video), de grote vraag, een zachte abonneer-zin zonder druk, een reactievraag
     ("where are you listening from, and what time is it there?") en settle in. Geen "Tonight" of "Hello".
   - **Midden**: 8-12 onderwerpen. Elk onderwerp is een blok `TOPIC: <hoofdstuktitel>` met `BRIDGE: <1-2 overgangszinnen>`,
     gevolgd door 6-10 feitjes `IMG: <slug> | <beeld>` / `HEAD: <verrassende kopzin>` / `BODY: <± 150-220 woorden>`.
     Blokken gescheiden door een regel `===`. Samen **± 85-95 feitjes** (= beelden), **± 16.000-18.000 woorden**.
   - **Slot** (± 1 min): uitdoven naar een slaapbeeld, geen nieuwe feiten, de zin "another ... story ... on the screen",
     kort abonneren, en als laatste "Sleep well, and good night."
   - **Makkelijk te volgen** (eigenaar 2 nov 2026): korte, gewone zinnen (8-15 woorden, hooguit ± 2 komma's), gewone
     woorden, alsof je het een vriend vertelt. Weinig jaartallen en namen achter elkaar. Af en toe de jij-vorm en een
     vraag aan de luisteraar; mythe tegenover werkelijkheid waar het past; echte mensen en bronnen.
   - **Spanning alleen waar het verhaal zelf spannend is**, en dan rustig. Geen gruwelijke details, geen schrikmomenten.
2. **`bouw_script.py`**: kopie van `stories/egypte-toetanchamon/bouw_script.py` (roept `tools/bouw_feiten.py` aan).
   Draai hem: hij maakt `script-cues.txt` en `hoofdstukken.tsv` en meldt feitjes, onderwerpen en woorden.
   Daarna `python tools/check_afwisseling.py stories/<map>`: moet AFWISSELING GOED geven (niet alles hetzelfde laten klinken).
3. **`afbeeldingen-onderwerpen.tsv`**: per feitje `NNN.png<TAB><slug><TAB><Engelse beeldprompt>` (001, 002, …).
   Alleen wat in die tijd bestond, mensen in kleding van toen, liefst avondlicht. Geen tekst in beeld.
   Beschrijf wat er wél is; schrijf nooit "no cars" (dan tekent het model ze juist).
4. **`youtube-beschrijving.txt`**: volgens `stories/YOUTUBE-STANDAARD.md`, **zonder regen** (de muziek is een zacht
   432 Hz-koor), precies 15 hashtags. Bij "Chapters" de TOPIC-titels als `0:00:00 <naam>`; de routine vult de tijden in.
5. **`planning.txt`**:
   ```
   onderwerp <onderwerp zoals in ONDERWERPEN.md>
   status   script-klaar (<datum vandaag>, tweede account)
   datum    <ma/wo/za datum uit de planning> 21:00 NL
   titel    <vraag-titel> | History for Sleep   (zonder uren; wissel de soort af, zie OPBOUW.md)
   opening   scène | mythe | persoon | voorwerp | raadsel
   titelsoort life-really-like | how-survive | what-actually | why | what-happened
   thumbnail amberregel "<...>", hook "<...>", beeld: <korte beschrijving>
   soort    <playlist-soort voor tools/youtube_playlist.py: ramp, oorlog, reis, ...>
   ```
   Thumbnail volgens `stories/YOUTUBE-STANDAARD.md`: titelwoorden erin, één pakkend onderwerp dat past bij
   de titel, anders dan de laatste 3 thumbnails.

Commit alleen die map en push naar `main`. Raak niets anders aan, ook niet `ONDERWERPEN.md`.

## Wat de routine ermee doet
De routine ziet `status script-klaar` en slaat het onderwerp kiezen en het script schrijven over. Hij leest
het script nog één keer na (begin, onderwerpen, slot, lengte; zie OPBOUW.md), maakt beelden, stem, montage en controles,
en uploadt op de datum uit `planning.txt`. Daarna zet hij de status op klaar met de YouTube-link.
