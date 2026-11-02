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
Een nieuwe map `stories/<korte-naam>/` (bv. `stories/tombstone-1881/`), net zoals `stories/oregon-trail/`:

1. **`src/01-<deel>.txt`, `src/02-<deel>.txt`, …**: het script in rustig Engels, in 15–20 delen (= hoofdstukken).
   - Een alinea gescheiden door een lege regel = `[pause]`. Een regel met alleen `--` = `[long-pause]`.
   - `{img:<slug>}` op een eigen regel waar een nieuw beeld begint: ± elke 1,5 minuut, samen **± 85–95 beelden**.
   - Lengte: **± 17.000 woorden** gesproken tekst (geeft ± 2 uur met de lange pauzes).
   - Begin, abonneer-zin, einde, toon en verboden dingen: precies volgens stap 2 van
     `stories/PROMPT-NIEUWE-VIDEO.md` en de opbouw van `stories/titanic/OPZET.md`
     (eerst het gewone leven, dan rustig de gebeurtenis zelf, geen gruwelijke details, geen "nu wordt het spannend").
   - Voorbeeld van de vorm: `stories/oregon-trail/src/`.
   - **Makkelijk te volgen** (eigenaar 2 nov 2026): korte, gewone zinnen, gemiddeld 15–19 woorden en hooguit ± 2 komma's (check-grens: 20 woorden, 3 komma's)
     per zin. Geen lange opsommingen als "the meat, and the milk, and the butter, and the cheese": kies er twee of drie.
     Goed voorbeeld: `stories/tombstone-1881/`. Te druk (niet zo doen): de eerste versies van cleopatra t/m india-boeddha.
   - **Simpel verteld** (eigenaar 2 nov 2026): gewone, makkelijke woorden, alsof je het verhaal rustig aan een vriend
     vertelt. Moeilijke woorden of namen kort uitleggen. Niet te veel jaartallen en namen achter elkaar.
   - **Simpel mét spanning, alleen waar het spannend is** (eigenaar 2 nov 2026: "spannend alleen bij stukken die spannend zijn"; het blijft een slaapvideo). Niets verzinnen: rustige hoofdstukken over het dagelijks leven blijven rustig. Waar het verhaal zelf spannend is, vertel je het zo, rustig: iets wat op het spel staat, een vraag die de luisteraar wil weten
     ("But no one in the town knows yet what the autumn will bring."), een gevaar dat langzaam dichterbij komt.
     Geen schrikmomenten, geen harde woorden, geen cliffhanger-kreten.
   - Check: `python tools/script_leesbaar.py stories/<map>` moet GOED geven.
2. **`src/beelden.tsv`**: per slug één regel `<slug><TAB><Engelse beeldbeschrijving>`. Alleen wat in die
   tijd bestond, mensen in kleding van toen, liefst avondlicht (lamp, vuur, schemering). Geen tekst in beeld.
3. **`bouw_script.py`**: kopie van `stories/oregon-trail/bouw_script.py`, met `STYLE`, `PLEK` en de kopregel
   van `prompts.txt` aangepast aan dit onderwerp. Draai `python stories/<map>/bouw_script.py`: hij maakt
   `script-cues.txt`, `prompts.txt` en `afbeeldingen-onderwerpen.tsv` en meldt het aantal woorden en beelden.
4. **`youtube-beschrijving.txt`**: volgens `stories/YOUTUBE-STANDAARD.md` (Beschrijving), met regen-zin en
   precies 15 hashtags. Bij "Chapters" de hoofdstuknamen **zonder tijden**, één per regel als `0:00:00 <naam>`;
   de routine vult de echte tijden in na de stem.
5. **`planning.txt`**:
   ```
   onderwerp <onderwerp zoals in ONDERWERPEN.md>
   status   script-klaar (<datum vandaag>, tweede account)
   datum    <wo/za datum uit de planning> 21:00 NL
   titel    <titel> | <N> Hours of History for Sleep   (de routine vult N in na de montage)
   thumbnail amberregel "<...>", hook "<...>", beeld: <korte beschrijving>
   soort    <playlist-soort voor tools/youtube_playlist.py: ramp, oorlog, reis, ...>
   ```
   Thumbnail volgens `stories/YOUTUBE-STANDAARD.md`: titelwoorden erin, één pakkend onderwerp dat past bij
   de titel, anders dan de laatste 3 thumbnails.

Commit alleen die map en push naar `main`. Raak niets anders aan, ook niet `ONDERWERPEN.md`.

## Wat de routine ermee doet
De routine ziet `status script-klaar` en slaat het onderwerp kiezen en het script schrijven over. Hij leest
het script nog één keer na (begin, abonneer-zin, einde, lengte), maakt beelden, stem, montage en controles,
en uploadt op de datum uit `planning.txt`. Daarna zet hij de status op klaar met de YouTube-link.
