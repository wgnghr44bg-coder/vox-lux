# What if – automatisch de volgende video maken en uploaden

Deze instructies volgt de dagelijkse sessie ("Maak en upload de volgende What if-video volgens
whatif-demo/AUTOMATISCH.md"). Antwoord aan het eind in het Nederlands, kort.

## Zuinig werken (eigenaar, okt 2026)

- Gebruik bestaande plekken en krachten; bouw alleen iets nieuws als het onderwerp echt niet past.
- Eén testronde per video: één testblad bekijken, één keer bijsturen, dan de volledige render.
- Vraag de wensen vooraf in één keer; niet halverwege van richting veranderen.
- Korte berichten: resultaat + video, geen lange uitleg.
- Meerdere video's in één sessie maken als de eigenaar daarom vraagt (code maar één keer inlezen).

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
- Engels, begint met "Imagine…" + `pause`, 170–210 woorden, tweede persoon ("you").
- Alleen natuurkunde die klopt, verteld als "would". Twijfel je aan een getal: weglaten.
- Rustige opbouw → kracht groeit (teller loopt mee) → climax waarin de stem zwijgt (een getal als
  pauze, bijv. `6` = 6 s stilte) → laatste zinnen over het beeld.
- Geen haak of flash-forward aan het begin (eigenaar, okt 2026): het verhaal begint gewoon bij het
  begin en loopt op volgorde. Gebruik `hook` in scenario.js dus niet.
- Netjes afsluiten (eigenaar, okt 2026): geen eindkaart en geen tekst aan het eind; de stem sluit af
  en het beeld vloeit uit (standaard naar zwart, `endStyle: 'white'` naar wit, bijv. als de zon het
  beeld wit brandt). Laat het laatste shot iets moois tonen (geen verkoold of leeg beeld).
- Eén korte kernzin tegelijk als caption, nooit de hele zin.

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
