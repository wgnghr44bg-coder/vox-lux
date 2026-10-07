# What if – automatisch de volgende video maken en uploaden

Deze instructies volgt de dagelijkse sessie ("Maak en upload de volgende What if-video volgens
whatif-demo/AUTOMATISCH.md"). Antwoord aan het eind in het Nederlands, kort.

## Routine en uploaden (eigenaar, okt 2026)

Shorts (sinds 7 okt 2026): NIET uploaden, zonder ingebrande ondertitels maken en aan de eigenaar geven
(TikTok); zie `regels/shorts-via-eigenaar.md`. Dat gaat vóór alles hieronder over Shorts.

De dagelijkse routine mag lange video's zelf uploaden, altijd privé met een geplande publicatie
(publishAt), zodat de eigenaar tot dat moment kan ingrijpen in YouTube Studio:
- Short: niet uploaden (zie hierboven); de eigenaar stuurt hem met ondertitels terug.
- Lange video (16:9): privé, live op de datum uit `USAGE.md` (planning) of anders de eerstvolgende woensdag of zaterdag 21:00 (2 per week),
  altijd met thumbnail (`--thumbnail`, stijl en controle: `regels/thumbnail.md`).
Wat er gemaakt wordt, volgt de planning in `USAGE.md` (root); past het niet in het budget: niets maken, wel melden.

## Losse regels (alleen lezen als nodig)

- Stem (eigenaar, 7 okt 2026): xAI "atlas" in documentairestijl, tempo 1.05, mét alle pauzes ([pause], [long pause],
  zinspauze en kommapauze), voor Shorts én lange video's (staat vast in make_whatif.py; geen voiceSpeed in scenario.js
  zetten tenzij de eigenaar dat vraagt). Sleep Archives: Lux op 0.9. Niet zelf een andere stem of tempo kiezen.

- Lange video (16:9): thumbnail-stijl en -controle in `regels/thumbnail.md` (altijd met thumbnail uploaden).
- QC vóór elke upload (lang) of doorgeven (Short), verplicht: `regels/qc.md` – alleen bij "✅ VIDEO APPROVED".
- Shorts gaan via de eigenaar (geen upload, geen ingebrande ondertitels): `regels/shorts-via-eigenaar.md`.
- Eigenaar stuurt zelf een video om te plaatsen: `regels/eigen-upload.md`.
- Shorts om en om in stijl A (POV) en B (gravity-stijl): `regels/stijl-afwisseling.md`.
- Opbouw van Shorts (sinds 7 okt 2026): zelfde als lange video's, maar korter: `regels/lange-video-opbouw.md` (onderaan).
- TikTok: geen Google Drive meer; de Shorts komen op de pagina "IfScape3D TikToks" (vanaf za 10 okt 2026).

## Lange video's: lengte en opbouw (eigenaar, okt 2026)

VASTE OPBOUW SINDS 7 OKT 2026: `regels/lange-video-opbouw.md` (± 3–4 min, tijdsprongen, gravity-stijl). Die gaat vóór
de punten hieronder over lengte (8 min) en eerste zin.

- Minimaal 8 minuten (eigenaar; mid-roll-grens), ± 8–9 min, 5–7 hoofdstukken van ± 1–1,5 min, per hoofdstuk een nieuwe plek of stap; stap voor stap erger
  (zoals de wind-video), climax in het laatste kwart.
- Sterke opening zonder vooruitblik: meteen "Imagine …" over een beeld waar al iets onrustigs gebeurt, teller in beeld.
- Nooit hetzelfde hoogtepunt (eigenaar, 7 okt 2026): elke video een eigen climax en eigen beelden. Wat al gebruikt is
  (zie "Al gebruikt" in onderwerpen.md) niet nog eens als hoogtepunt, ook niet in een andere video of als Short ↔ lang.
- Eerste zin (eigenaar, 7 okt 2026): altijd "Imagine" + de titel, bijv. titel "What if the Sun went out?" →
  "Imagine the Sun went out." Mag na een korte intro van een paar seconden (beeld + geluid, nog geen stem).
- Na de eerste lange video's samen met de eigenaar de kijkduur (Betrokkenheid) bekijken; blijven kijkers tot het eind,
  dan naar 10 minuten. Usage ± 5–7% per lange video.

## Zuinig werken (eigenaar, okt 2026)

- Gebruik bestaande plekken en krachten; bouw alleen iets nieuws als het onderwerp echt niet past.
- Eén testronde per video: één testblad bekijken, één keer bijsturen, dan de volledige render.
- Vraag de wensen vooraf in één keer; niet halverwege van richting veranderen.
- Korte berichten: resultaat + video, geen lange uitleg.
- Routine: per run 2 Shorts (code maar één keer inlezen), live op twee verschillende dagen; lange video's één per run.
- Lees alleen wat de taak van vandaag nodig heeft; regels voor andere taken staan in `regels/`.

## Usage bijhouden (eigenaar, okt 2026)

Vóór elke run: lees `USAGE.md` (in de root), reken met de schattingen uit of de run nog past tot zaterdag
12:00 (eerst ruimte voor de geplande Sleep-runs en 10% buffer). Na de run: voeg een regel toe aan het log
(kanaal, short/lang, geschatte kosten). Stuurt de eigenaar een Usage-screenshot, vul dan de echte stand in en
stel de schattingen bij.

## Ondertitels: verplichte controle vóór upload (eigenaar, okt 2026)

(Sinds 7 okt 2026 geldt dit voor geen enkele video meer: Shorts krijgen hun ondertitels van de eigenaar in TikTok
(`regels/shorts-via-eigenaar.md`) en lange video's (16:9) krijgen géén ondertitels – nooit met `--subs` bouwen.)

Shorts krijgen Engelse ondertitels (3–5 woorden per keer, ingebrand, synchroon met de stem). Bij het bouwen van
`--subs` hoort een controle-script (zoals `tools/check_video.py` bij Sleep); zonder "SUBS GOED" niet uploaden:
- Timing: elke ondertitel valt binnen de gemeten zinstijd (`voice-times.tsv`), start hooguit 0,15 s vóór de stem,
  geen overlap, geen gat > 0,4 s midden in een zin, elke ondertitel ≥ 0,6 s in beeld.
- Tekst: exact gelijk aan het script (geen ontbrekende of dubbele woorden), max ± 32 tekens per regel, max 2 regels.
- Beeld: de tekst valt niet over de teller of het logo; leesbaar (wit met donkere rand).
- Vloeiend: `tools/check_video.py` op het eindbestand (geen haperende stem, decodeerfouten, renderfouten of
  stilstaand beeld) + geen flikkerende of verspringende ondertitels (beeld voor beeld bij de wissels kijken).
- Zelf kijken: overzichtsplaat met een beeld per ondertitel-wissel bekijken; bij twijfel een stukje als video.
Faalt iets: repareren en opnieuw controleren; lukt het niet, dan niet uploaden en melden.

## Glitch op straat (eigenaar, okt 2026)

In de wind-video (lange video, hoofdstuk straat) zat een glitch in beeld. Bij elke video met de plek
`street` extra opletten: niet alleen stills bekijken, maar ook een kort stukje video van de straat-shots
(beeld voor beeld) op flikkeren, verspringen of haperen controleren, en pas renderen als het weg is.

## 0. Klaarzetten

```bash
git fetch origin claude/whatif-machine && git checkout claude/whatif-machine && git pull origin claude/whatif-machine
cd whatif-demo && npm ci && cd ..
pip install -q numpy scipy requests imageio-ffmpeg
```

## 1. Onderwerp kiezen

- Haal eerst de uploads van het kanaal op en vergelijk met "Al op het kanaal" in `onderwerpen.md`: nooit een dubbele
  video (Short of lang).
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
- Shorts wisselen sinds 7 okt 2026 om en om tussen stijl A (POV, de regels hieronder) en stijl B (gravity-stijl):
  zie `regels/stijl-afwisseling.md`; voor stijl B gelden de afwijkingen uit die tabel.
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

## 7. Vastleggen

Bronbestanden per video (eigenaar, 7 okt 2026) – VERPLICHT, ook bij lange video's:
repo `wgnghr44bg-coder/ifscape3d-videos` (branch `main`, zie README daar), map `<datum>-<slug>/` met alle
scenario.js-bestanden, script.txt, voice.mp3, voice-times.tsv, timing.json, upload.json (met YouTube-link),
thumbnail en `ENGINE.txt` (commit van vox-lux waarmee gerenderd is). Geen mp4, stills of wav's.
Zonder deze map is een video later niet te repareren.

Daarna commit en push naar `claude/whatif-machine` in vox-lux (geen pull request): onderwerpen.md, USAGE.md
en nieuwe engine-onderdelen.

Meld kort: onderwerp, link (of waarom niet geüpload), publicatietijd, bronbestanden opgeslagen ja/nee.
