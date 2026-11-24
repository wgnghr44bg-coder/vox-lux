# Prompt: verder met studio3d (three.js) — stand 24 nov 2026, ± 01:30

Plak dit in een nieuwe Claude Code-sessie op de pc van de eigenaar (map `C:\Users\rane\Documents\vox-lux-routine`):

---
Je gaat verder met het werk van een ander Claude-account. Praat Nederlands, simpel. Lees eerst `CLAUDE.md` en
`kanalen/marketdoodle/WHATIF-AFSPRAKEN.md` (vaste regels Market Doodle: eerst laten zien, niets zelf uploaden, geen muziek,
geen effect bij scènewissel, eigen stem verteller, enz.).

**Doel:** de eigenaar liet een Short zien (@RicksClips3000, "The Job Nobody Wants in Japan") met échte animatie:
3D-ruimtes in tekenfilm-look (platte kleuren + zwarte lijnen), personages die bewegen, en een camera die doorlopend door
de ruimte beweegt (van een klok omlaag naar een persoon, inzoomen, uitzoomen). Onze stilstaande-plaatjes-proef keurde hij af
("jij hebt stilstaande beelden na elkaar"). Hij koos **three.js** (sneller dan Blender). Maak een **proef van ± 10-12 s**
en laat die zien. Niet uploaden.

**Wat er al is** (`kanalen/marketdoodle/studio3d/`):
- `npm install` gedaan: `three@0.170.0`, `puppeteer-core@23.10.4` (geen Chromium gedownload; gebruik **Edge**:
  `C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`).
- `proef-data.json` + `proef.wav`: stem en woordtijden van het begin van de eerste Short (keuken: "It's 7:15 in the morning.
  You walk into the kitchen. And above your dad's head, there's a glowing number. $64,000." + papa: "Morning, buddy. Why are
  you staring at me?"), `mond` = mondopening van papa per beeldje (30 fps), `EIND` ± 12,1 s.
- `scene.html` (GESCHREVEN, NOG NIET GETEST): keuken in 3D (MeshToonMaterial + OutlineEffect), wandklok op 7:15,
  jij (blauwe hoodie) en papa (groen, bril) als 3D-poppetjes in onze stijl, lopen/zwaaien/praten/knipperen/verbaasd,
  glimmend getal boven papa ($??? → $64,000), camera-reis (`REIS`), ondertitels 1-2 woorden groot in het midden.
  Functie `window.render(t)` geeft een JPEG (dataURL) van 1080x1920 terug; `window.klaar` = true als geladen.

**Nog te doen:**
1. `render.mjs` schrijven: kleine statische webserver (node `http`) op deze map (scene.html, proef-data.json, node_modules),
   Edge headless starten met puppeteer-core (`--use-angle=d3d11 --enable-gpu --ignore-gpu-blocklist`, viewport 1080x1920),
   wachten op `window.klaar`, voor elk beeldje `page.evaluate(t => render(t), i/30)` en de JPEG naar ffmpeg pipen
   (`-f image2pipe -c:v mjpeg -r 30 -i -` + `proef.wav`, libx264 crf 20, yuv420p, loudnorm -14) → `proef3d.mp4`.
2. Testen en fouten in scene.html oplossen (console-fouten van de pagina loggen). Beelden nakijken (contactblad):
   klopt alles als een film? (eerst gebeurt iets, dan de reactie; camera laat zien wie praat; niets ongepasts).
3. Proef naar de eigenaar sturen (SendUserFile, display render). Vragen wat beter moet.
4. Daarna eventueel uitbouwen tot een "studio": draaiboek per video (ruimte, wie waar, acties, camera) → video.

**Let op:** de pc heeft weinig geheugen. 's Nachts (22:00-08:00) maakt de pc Sleep Archives (bewaker + routine_lokaal).
Zware dingen alleen als die niet draait, of eerst `~/gpu-bezet.lock` zetten en na afloop weghalen (bewaker wacht dan).
Commit alleen tekstbestanden via `tools/gitveilig.py` (geen node_modules, mp4, wav).
---
