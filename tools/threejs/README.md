# Three.js-animaties (staande video, 9:16)

Elke animatie is één HTML-bestand: openen in de browser = afspelen, met tijdbalk, knop **Sound** (geluidseffecten)
en knop **Voice** (eigen stem laden). `H` of `?clean=1` verbergt de knoppen.

| Bestand | Wat |
|---|---|
| `daily-grind.html` | koffiezaak-diorama, 10 s loop |
| `shark-pool.html` | haai in zwembad + filterinstallatie, 60 s |
| `never-stopped-raining.html` | What If: het stopt nooit met regenen, 80 s (met geluidseffecten en MP4-export) |
| `insects-human-size.html` | What If: insecten zo groot als mensen, 80 s (doorsnede tracheeën, mierenhoop, Meganeura) |
| `insects-horror.html` | What If: insecten zo groot als mensen, horrorversie, 90 s (slaapkamer, stad, supermarkt, koningin, schuilkelder; harde cut naar zwart). Ondertitels volgen de stem, `WARP` zet videotijd om naar verhaaltijd |
| `whale-swallowed.html` | Imagine being swallowed by a whale, ±2:09 (bultrug van binnen, ontsnapping naar het oppervlak, potvis en een reusachtige schaduw; cliffhanger met harde cut naar zwart). Ondertitels volgen de Chatterbox-stem (`whale-swallowed/voice-times.tsv`) |

## Alles in één keer op de pc (PowerShell)
Vanuit de map `vox-lux`:
```
.\tools\threejs\make-whatif.ps1 -Html tools\threejs\never-stopped-raining.html
.\tools\threejs\make-whatif.ps1 -Story "What if the Moon disappeared?"
```
Het script haalt de ondertitels uit de pagina, rendert de MP4 met geluidseffecten (videokaart), maakt de stem
(Chatterbox, gratis, `stem-env`) en mixt die eronder → `<naam>\<naam>-voice.mp4`.
Met `-Story` schrijft OpenCode eerst een nieuwe animatie volgens `whatif-prompt.md`. Dat gebruikt een AI-model:
met een betaald model (bijvoorbeeld Claude via een API-sleutel) kost dat geld, het script vraagt eerst toestemming.
Opties: `-NoVoice`, `-NoGpu`, `-SkipRender`, `-StemEnv <map>`, `-Model <provider/model>`.
Nodig: Node.js, Python, ffmpeg; Playwright wordt de eerste keer zelf geïnstalleerd.

## Losse stappen
- `make_cues.py <pagina> <map>`: ondertitels → `cues.tsv` + `script-cues.txt`
- `export_mp4.mjs <pagina> <uit.mp4> [--gpu]`: MP4 renderen (met de geluidseffecten van de pagina)
- `place_voice.py <map> [--video <mp4>]`: stem op de ondertiteltijden zetten en onder de video mixen

Een nieuwe animatie werkt met deze tools als ze dezelfde opbouw heeft als `never-stopped-raining.html`
(`SCENES` met `subtitles`, `buildSfx`, `?render=1` met `renderAt`/`renderSoundtrack`); zie `whatif-prompt.md`.
