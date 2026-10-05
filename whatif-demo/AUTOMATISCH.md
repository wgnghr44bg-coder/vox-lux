# What if – automatisch de volgende video maken en uploaden

Deze instructies volgt de dagelijkse sessie ("Maak en upload de volgende What if-video volgens
whatif-demo/AUTOMATISCH.md"). Antwoord aan het eind in het Nederlands, kort.

## Zuinig werken (eigenaar, okt 2026)

- Gebruik bestaande plekken en krachten; bouw alleen iets nieuws als het onderwerp echt niet past.
- Eén testronde per video: één testblad bekijken, één keer bijsturen, dan de volledige render.
- Vraag de wensen vooraf in één keer; niet halverwege van richting veranderen.
- Korte berichten: resultaat + video, geen lange uitleg.
- Meerdere video's in één sessie maken als de eigenaar daarom vraagt (code maar één keer inlezen).

## Usage bijhouden (eigenaar, okt 2026)

Vóór elke run: lees `USAGE.md` (in de root), reken met de schattingen uit of de run nog past tot zaterdag
12:00 (eerst ruimte voor de geplande Sleep-runs en 10% buffer). Na de run: voeg een regel toe aan het log
(kanaal, short/lang, geschatte kosten). Stuurt de eigenaar een Usage-screenshot, vul dan de echte stand in en
stel de schattingen bij.

## Glitch op straat (eigenaar, okt 2026)

In de wind-video (lange video, hoofdstuk straat) zat een glitch in beeld. Bij elke video met de plek
`street` extra opletten: niet alleen stills bekijken, maar ook een kort stukje video van de straat-shots
(beeld voor beeld) op flikkeren, verspringen of haperen controleren, en pas renderen als het weg is.

## Lange video's (16:9): altijd een thumbnail (eigenaar, okt 2026)

Elke lange IfScape3D-video krijgt bij de upload meteen een thumbnail in de vaste stijl van
`branding/thumbnail-voorbeeld.jpg` (de wind-video), in de stijl van het grote What If-kanaal. Shorts: geen thumbnail.

Doel: altijd pakkend. De kijker moet nieuwsgierig worden en willen klikken. Laat het spannendste moment zien,
maar niet de afloop (wat gebeurt er hierna?); het getal moet verbazen (extreem, onverwacht). Vraag jezelf vóór
gebruik af: zou ik hierop klikken als ik door YouTube scroll? Zo niet: ander moment, groter onderwerp, minder tekst.

Stijl (elke keer hetzelfde, passend bij het onderwerp):
- 1280x720. Achtergrond = een echt frame uit de eigen 3D-video (plek van de climax), iets verzacht.
- Rechts groot en dichtbij waar de video om draait (het hoofdonderwerp: bij dinosaurussen een T-rex, bij wind
  wegvliegende auto's, bij kou een bevroren brug …), met de echte low-poly modellen uit de video,
  uitvergroot, schuin/wegvliegend, met witte snelheidsstrepen of ander effect dat bij de kracht past.
- Links weinig tekst, dik schreefloos lettertype (heavy, hoofdletters), wit met donkere rand/schaduw:
  hooguit 3 regels, één groot getal of extreem in geel (bv. "OVER | 1,000 | KM/H", "2X | GRAVITY", "−100 °C").
- Logo (bol met ring) linksboven. Rechtsonder leeg (videolengte).
- Geen gewonden, geen bloed; poppetjes mogen wel zichtbaar in de kracht staan.

Werkwijze:
1. Klaarzetten: `pip install -q fonttools brotli pillow`.
2. Achtergrond: frame uit de video (`ffmpeg -ss <s> -i <video> -frames:v 1 bg.png`), liefst zonder teller in beeld;
   modellen los renderen uit de engine (zelfde plek/props, transparante achtergrond) en erop plakken.
   (`whatif-demo/ifscape_thumbnail.py` maakt nog de oude, rustige stijl; alleen gebruiken als basis/noodoptie.)
3. Controle vóór gebruik: zelf openen en kijken: actie goed zichtbaar en niet achter de tekst, tekst leesbaar
   op telefoonformaat, logo staat erop, getal klopt met de video.
4. Uploaden: `tools/youtube_upload.py … --thumbnail <map>/thumbnail.jpg`, zodat hij er meteen op staat zodra de
   video live gaat (werkt sinds okt 2026). Lukt het niet: thumbnail naar de eigenaar sturen met
   YouTube Studio → Content → video → Thumbnail → Uploaden → Opslaan.

## Uploaden van een video die de eigenaar stuurt (eigenaar, okt 2026)

Stuurt de eigenaar een (ondertitelde) video in de chat met de vraag hem te plaatsen:
1. Bekijk hem eerst (een paar beelden + decodeercontrole: `ffmpeg -v error -i <bestand> -f null -`).
2. Upload precies dat bestand, niet opnieuw coderen:
   `python3 tools/youtube_upload.py <bestand> --channel whatif --title "What if …?" --description-file d.txt --tags "…" --privacy public`
   Openbaar, categorie Education (27), Engels, niet voor kinderen, AI-label aan, geen thumbnail.
3. Korte, menselijke beschrijving:
   POV-zin + emoji / één feit / een vraag aan de kijker + 👇 / 3-4 hashtags waarvan #whatif en #shorts.
   Geen regel "Animated with code / AI voice" (eigenaar, okt 2026); wel het AI-vinkje bij upload.
   Titel zonder #shorts. ±10 tags (what if, onderwerp, science, physics, simulation, 3d animation, IfScape3D).
4. Zet de video in de playlist "What If".
5. Werk onderwerpen.md bij (status "geüpload <datum> <link>") en meld de link.

## 0. Klaarzetten

```bash
git fetch origin claude/whatif-machine && git checkout claude/whatif-machine && git pull origin claude/whatif-machine
cd whatif-demo && npm ci && cd ..
pip install -q numpy scipy requests imageio-ffmpeg
```

## 1. Onderwerp kiezen

- Neem in `whatif-demo/onderwerpen.md` het eerste onderwerp met status `gepland`.
- Regel: een andere plek dan de vorige video. Is de plek gelijk aan die van de laatst geüploade video,
  neem dan het volgende `gepland`-onderwerp.
- Staan er minder dan 5 onderwerpen op `gepland`, voeg er onderaan nieuwe toe (nooit een dubbel).

## 2. Scenario schrijven (het enige creatieve werk)

Maak `whatif-demo/topics/<slug>/scenario.js` (kopieer `topics/gravity-doubled/scenario.js`).
Daarin staat alleen: onderwerp (`topic`: number, slug, place, force, question, title), teller (`hud`,
`counter`, `range`), zinnen (`lines`), tijden (shots, captions, beats – allemaal via `at('id')`, dus
op de gemeten zinstijden), eindtekst (`end`) en uploadtekst (`upload`: title met `#shorts`,
description, tags, tiktok).

Script-regels:
- Engels, eerste zin "Imagine" + het onderwerp + `long`, 170–210 woorden, tweede persoon ("you").
- Alleen natuurkunde die klopt, verteld als "would". Twijfel je aan een getal: weglaten.
- Rustige opbouw → kracht groeit (teller loopt mee) → climax waarin de stem zwijgt (een getal als
  pauze, bijv. `6` = 6 s stilte) → laatste zinnen over het beeld.
- Opening (eigenaar, okt 2026): geen titel in beeld. De eerste zin is altijd "Imagine" + het onderwerp,
  bijv. "Imagine the Earth stopped spinning." Daarna rustig beginnen en de spanning steeds verder
  opbouwen tot de climax (teller versnelt, `audio: { heartbeat, riser }` in scenario.js).
- Kanaalnaam in beeld (eigenaar, okt 2026): één keer per video kijkt de POV-camera ±1,6 s naar het logo
  (branding/logo-cut.png: alleen bol + naam) en draait dan weer weg. Het logo moet passen in de scène:
  op een reclamebord, tv-scherm, auto, reddingsband, t-shirt/jas van iemand (`driver: { logo: 'front' }` in props.car)
  of als graffiti op een muur – nooit als los bord aan een gebouw. Elke plek heeft een vaste plek (E.brandSpot); `beats.brand` kiest
  eventueel het moment, `brand: false` zet het uit.
- Auto's: voorop twee losse koplampen, achterop één lange lichtbalk.
- Wat de stem zegt, moet je ook zien (eigenaar, okt 2026): zegt de stem "engines stop", laat dan een auto
  stoppen en de bestuurder uitstappen en weglopen (`beats.driver` in river-city).
- Geen haak of flash-forward aan het begin (eigenaar, okt 2026): het verhaal begint gewoon bij het
  begin en loopt op volgorde. Gebruik `hook` in scenario.js dus niet.
- Netjes afsluiten (eigenaar, okt 2026): geen eindkaart en geen tekst aan het eind; de stem sluit af
  en het beeld vloeit uit (standaard naar zwart, `endStyle: 'white'` naar wit, bijv. als de zon het
  beeld wit brandt). Laat het laatste shot iets moois tonen (geen verkoold of leeg beeld).
- Eén korte kernzin tegelijk als caption, nooit de hele zin.

Camerastijl (eigenaar, okt 2026): standaard de toeschouwer-stijl – wijde, stabiele shots waarin je oorzaak en
gevolg in één beeld ziet (zoals de zwaartekracht-video, die het beter doet op TikTok). POV alleen als kort
accent (2–3 s) op het spannendste moment. Lange video's: liggend 16:9, 720p.

Beeld-regels (stijl zoals earth-stops):
- Low-poly, flat-shaded, matte kleuren, echte schaal, serieuze belichting; stabiele camera.
- Elke vernielfase hooguit 4–5 s per shot (wissel van shot); grote brokken nooit beeldvullend of
  door de camera; in stof altijd silhouetten zichtbaar; geen abstracte effecten (geen glasbarsten);
  geen gewonden of lichamen (mensen gaan op tijd naar binnen: beat `shelter`); geen neon of game-UI.

### De engine (whatif-demo/engine/)

| bestand | wat |
|---|---|
| `core.js` | renderer, lucht, licht, materialen, gevels, register (bend/breaks/falls/floods/lights/frost) |
| `physics.js` | debris eenmalig gesimuleerd (zwaartekracht, lucht, water/drijven), EVENTS voor geluid en schok |
| `dust.js`, `hud.js`, `timeline.js`, `main.js` | stof/sneeuw/spray, tekstlaag, scenario → TL, hoofdlus en camera |
| `props.js`, `blocks.js`, `crowd.js` | palmen, bomen, lantaarns, borden, auto's, mensen; gebouwen, huizen, watertoren |
| `places/*.js` | plekken: `street` (stadsstraat), `river-city` (rivierstad met hangbrug), `boulevard` (strandboulevard), `mountain-village` (besneeuwd bergdorp) |
| `forces/*.js` | krachten: `wind`, `gravity` (zwaartekracht), `water` (stijgen/zakken), `cold` (kou/duisternis) |

Elke plek zegt zelf wat kan buigen (`E.bend`), breken (`E.breaks`, met sterkte per kracht), vallen
(`E.falls`, met `rank` voor `beats.falls`) en onderlopen (`E.floods`), en levert `shots` en `look`.
Elke kracht levert `level(t)`, `field(t)` (g, lucht, waterstand), `lateral`, `droop`, `timeOf(sterkte)`,
`fallMode` en `look`. Bovenaan elk plek- en krachtbestand staan de beats die het gebruikt.

Past het onderwerp niet bij een bestaande plek of kracht, bouw dan een nieuwe in `engine/places/` of
`engine/forces/` (zelfde vorm als de bestaande, kopieer de meest verwante) en houd die – ze blijven
bewaard voor volgende video's. Proef een plek zonder onderwerp met:
`node whatif-demo/engine/render.mjs 'preview:<plek>:<kracht>:[[0,"wide"],[20,"..."]]' stills 5 25 40`.

## 3. Testbeelden (maximaal 2 rondes)

```bash
python3 whatif-demo/make_whatif.py <nr> --stills          # maakt ook de stem (xAI, ± 1 cent)
```
Bekijk `topics/<slug>/stills/overzicht.jpg` (6 beelden) zelf kritisch tegen de regels hierboven.
Pas zo nodig scenario/plek aan en draai `--stills` nog één keer (eigen tijden: `--times 12,30,...`).

## 4. Video maken

```bash
python3 whatif-demo/make_whatif.py <nr> --from render     # stem bestaat al; ± 15 min
```
Resultaat: `topics/<slug>/<slug>.mp4` (1080x1920, 30 fps) en `upload.json`. Shorts hebben geen thumbnail nodig.

## 5. Controleren en uploaden

```bash
python3 whatif-demo/publish_whatif.py <nr>
```
- Draait eerst `tools/check_video.py`; alleen bij "CONTROLE GOED" wordt er geüpload.
- YouTube: kanaal `whatif` (`YT_WHATIF_REFRESH_TOKEN`), privé met publicatie de volgende dag
  18:00 Europe/Amsterdam, AI-label aan, als Short (verticaal, < 3 min, `#shorts`). Ontbreekt de token,
  dan wordt de upload overgeslagen en staat dat in de status – meld dat.
- Zet de TikTok-map klaar: `whatif-demo/tiktok/<datum>-<slug>/` (mp4, tiktok.txt).
- Werkt `onderwerpen.md` bij.

Faalt de controle: lees de melding, repareer (meestal render opnieuw met `--from render` of geluid
met `--from audio`), en probeer nog één keer. Lukt het dan nog niet: niet uploaden, wel melden.

## 6. Google Drive (TikTok)

Zet met de Google Drive-connector de bestanden uit `whatif-demo/tiktok/<datum>-<slug>/` in de
map "TikTok klaar" (maak die aan als hij niet bestaat; per video een submap `<datum>-<slug>`). Lukt dat
niet (geen connector, geen rechten), meld het dan; de map in de repo blijft de bron.

## 7. Vastleggen

Commit en push naar `claude/whatif-machine` (geen pull request): scenario.js, script.txt, voice.mp3,
voice-times.tsv, timing.json, mp4, upload.json, tiktok.txt, onderwerpen.md en nieuwe
engine-onderdelen. Geen stills, geen wav's (staat in `.gitignore`).

Meld kort: onderwerp, link (of waarom niet geüpload), publicatietijd, Drive gelukt ja/nee.
