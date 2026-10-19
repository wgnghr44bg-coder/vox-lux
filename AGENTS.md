# AGENTS.md – Alteraqon-shorts zelfstandig maken (pc van de eigenaar)

Dit bestand is voor een AI-agent (OpenCode / LongCat) op de pc van de eigenaar. Volledige regels: `alteraqon/README.md` (lees die eerst).
Werk op branch `alteraqon` (deze map: `vox-lux-alteraqon`). Schrijf kort en in het Nederlands naar de eigenaar.

## Opdracht "Maak een Alteraqon-short: What if …?"
Voer alle stappen zelf uit. Stop alleen bij een echte blokkade en meld dan exact wat er misgaat.
**De eigenaar zit NIET achter de pc** (hij volgt alles op zijn iPhone). Vraag hem nooit om zelf een commando te draaien,
iets te installeren of een omgeving te activeren: zoek het zelf uit en doe het zelf. Vragen mag alleen over inhoud (onderwerp, keuze).

### 0a. Zelf onderwerpen kiezen (eigenaar 20 okt 2026: "gemixt, over van alles, maar spannend en boeiend")
Geeft de eigenaar geen onderwerp, dan kies je (met @scriptschrijver) zelf:
- **Wissel af** tussen categorieën; nooit twee keer achter elkaar dezelfde: ruimte · menselijk lichaam · dieren/natuur ·
  aarde/weer/rampen · oceaan · techniek/internet · geschiedenis ("what if X never happened") · natuurkunde/tijd · samenleving.
- **Nooit herhalen**: kijk eerst welke onderwerpen al in `alteraqon/*/upload.json` (titels) staan.
- **Alleen sterke onderwerpen**: een vraag die iedereen meteen wil weten (eerste 2 seconden!), een beeldbare ramp/verandering,
  en een ECHT verrassend feit als twist. Geen twist te vinden met bron? Kies een ander onderwerp.
- Titelvorm: `What if <korte, concrete vraag>?` (max ±50 tekens), bijv. "What if the oceans disappeared?".

### 0. Wie doet wat (eigenaar 19 okt 2026)
- **Script, feiten en beeldprompts (stap 2, 3, 3b) laat je ALTIJD schrijven door de subagent `@scriptschrijver`**
  (beste gratis model voor schrijven/kennis). Geef hem het onderwerp + de map; hij schrijft `script-cues.txt`, `prompts.txt`
  en `bronnen.txt`. Jij (het hoofdmodel) voert daarna uit: beelden, stem, shots, render, push.
- **Elk beeld laat je beoordelen door `@beeldcontrole`** (stap 4).
- Bestaat een subagent niet: STOP en meld "subagent <naam> ontbreekt" – schrijf het script dan niet zelf.

### Script-checklist (voor @scriptschrijver; check_short.py controleert een deel automatisch)
- Het verhaal is één lijn: wat-als → wat jij meemaakt → "Then." → tijdstappen → twist. De twist mag het verhaal
  NIET tegenspreken (niet eerst "je wordt verteerd" en daarna "dat kan niet").
- De twist is een ECHT, nagezocht feit dat bij het onderwerp hoort (echte gebeurtenis/record/persoon), het liefst verrassend.
- Elk getal en elke oorzaak staat in `bronnen.txt`: één regel per feit: `<feit> | <URL>` (minstens 2 bronnen, echte URL's
  die je hebt geopend). Niet zeker? Weglaten.
- Geen gruwel/bloed-details; spannend mag, smerig niet.
- Elk beeld toont letterlijk de zin; geen tekst/cijfers/kranten/grafieken in beeld (zie stap 3).

### 1. Voorbereiden
- `git pull origin alteraqon`
- Map: `alteraqon/<datum van vandaag>-<korte-slug>/` (bijv. `2026-10-20-sun-vanished`). Kopieer niet het sjabloon blind; volg het voorbeeld `alteraqon/2026-10-18-moon-disappeared/`.

### 2. Script (`script-cues.txt`)
- Engels, ±105–120 woorden (≈60–70 s met het rustige tempo), korte spannende zinnen. Elke regel eindigt op `[pause]` of `[long pause]`.
- `{img:M01}` op een eigen regel vóór elk stukje tekst; ±1 beeld per zin, 17–20 beelden.
- Opbouw: opening "What if …?" → POV-opbouw → "Then." (eigen beeld, witte flits + klap) → 3–4 tijdstappen met groot getal
  → "But here's the twist." met een ECHT feit → "So remember." + vraag aan de kijker.
- Tijdstappen: de STEM zegt "After one day.", het tijdstempel in beeld toont alleen `("NO MOON","1 DAY")` (zonder AFTER; max ±13 tekens).
  Geen opvulzinnen als "Right now." na de openingsvraag.
- Getallen VOLUIT schrijven ("nineteen sixty-nine", "three point eight"), anders spreekt Chatterbox ze verkeerd uit.
- Feiten: alleen algemeen bekende, controleerbare feiten. Noteer per feit een bron (URL) voor het eindrapport.
  Twijfel je aan een getal, zeg "about" / "could" of laat het weg.

### 3. Beeldprompts (`prompts.txt`), één regel per beeld: `M01|<prompt>`
- Begin foto's met: `Epic cinematic photo, vertical 9:16, award-winning, hyperrealistic, dramatic volumetric light, high contrast, frozen motion, high detail, no text, no logos,`
- Wetenschap/ruimte/lichaam: `Epic scientific 3D render, vertical 9:16, photorealistic, dramatic cinematic lighting, glowing highlights, high contrast, high detail, no text, no labels, no logos,`
- Elk beeld toont LETTERLIJK wat er in die zin gezegd wordt; "wow"-beelden. Geen gezichten of handen in close-up; mensen alleen als silhouet/van achteren.
- Noem iets wat NIET in beeld mag NOOIT bij naam (ook niet als "no moon"): het model tekent het dan juist. Beschrijf alleen wat er wél is.
- Geen echte merken/logo's.
- Geen linialen, meetlatten, grafieken, klokken of borden: het model maakt daar onleesbare cijfers/tekst van.
- Echte (historische) personen nooit herkenbaar of als nep-"foto": alleen silhouet, van achteren, of een voorwerp van hen.
- Feiten over oorzaken ("zijn hart faalde") altijd nazoeken; liever weglaten dan gokken.

### 3a. DUIDELIJK boven alles (eigenaar 19 okt 2026: "zorg alleen voor duidelijke afbeeldingen")
Het beeldmodel kan alleen eenvoudige, echt fotografeerbare scènes goed maken. Daarom:
- Eén hoofdonderwerp dat in één oogopslag herkenbaar is (een walvis, een boot, een maan). Liefst GEEN mensen; hoogstens één
  klein silhouet op afstand als schaal.
- Geen onmogelijke camerastandpunten ("view from inside the mouth/body", "looking out from inside") en geen combinaties als
  "mens in/onder/op een dier" – dat geeft rare, vervormde beelden.
- Abstracte zinnen ("total darkness", "pressure", "you think it's the end") vertalen naar één eenvoudig concreet beeld
  (zwart water met een paar belletjes, een duikbril die wegdrijft, één luchtbel die naar het licht stijgt).
- Kort prompt: onderwerp + wat het doet + plek + licht. Geen opsommingen van 6 dingen tegelijk.
- @beeldcontrole keurt af als je het beeld niet binnen 1 seconde snapt.
- **Schrijf elk prompt als een bestaande fotosoort**, dan maakt het model de juiste houding/actie:
  `aerial drone photo of …` (van bovenaf), `wildlife telephoto photo of …`, `macro photo of …`, `underwater photo of …`.
  Het model heeft vaste gewoontes (bijv. "humpback" = altijd een springende walvis); noem dan expliciet wat er WEL gebeurt
  ("mouth wide open full of water seen from above") en gebruik een andere fotosoort.
- Nooit twee keer (bijna) hetzelfde beeld in één video; elk beeld een andere fotosoort of hoek.
- **Onmogelijke beweging** (iets dat achteruit/omhoog/de verkeerde kant op gaat, tijd die terugloopt): een foto kan geen
  richting tonen. Toon het als **bevroren moment**: dingen die onmogelijk stil in de lucht hangen (regendruppels, koffie-spat,
  vogels, scherven, waterval-druppels "suspended in mid-air, frozen in time"). @beeldcontrole keurt zo'n beeld goed als het
  de zin duidelijk symboliseert ("de tijd is gestopt/omgekeerd") – geef hem dat mee.

### 3a+. Spectaculair binnen duidelijk (eigenaar 19 okt 2026: "spannender en spectaculairder, maar op basis van het script")
Elk beeld blijft één duidelijk onderwerp dat precies de zin toont, maar dan op het spannendste moment en in het mooiste licht:
- **Het hoogtepunt van de zin**: niet "een walvis", maar "een walvis die met open bek uit zee knalt, water spat alle kanten op".
- **Dramatisch licht/weer** dat het model goed kan: tegenlicht bij zonsondergang, onweer met bliksem, lichtbundels door water of
  wolken, gloed van lava/vuur, maanlicht. Nooit vlak daglicht.
- **Bevroren actie**: spatten, scherven, stof, vonken, golven, schuim midden in de lucht.
- **Extreem schaalverschil**: het enorme ding groot in beeld, een klein bootje/huisje/silhouet ernaast.
- **Spannende hoek**: kikvorsperspectief van onderaf, of vogelvlucht van bovenaf; geen saaie ooghoogte.
- Voorbeeld: zin "Rivers and lakes shrink." → niet "a dry river", maar "a cracked dry riverbed seen from above at sunset,
  a lone stranded boat lying in the mud, long dramatic shadows, heat haze".
- @beeldcontrole beoordeelt ook: "is dit spannend genoeg voor de eerste seconde van een Short?" Saai = opnieuw.

### 3b. Impact (eigenaar 18 okt 2026: beelden moeten mensen vasthouden)
- **M01 = de hook**: het meest spectaculaire beeld van de hele video (de eerste seconde beslist of iemand blijft kijken).
  Toon meteen het extreme gevolg (bijv. een reus die door het dak breekt), niet een rustige opbouwscène.
- Toon het MOMENT, niet de situatie: iets breekt, barst, valt, explodeert, scheurt, stroomt – midden in de actie.
- Schaal voelbaar maken: lage camerahoek, kleine mensen/auto's/huizen naast het enorme ding.
- Eén duidelijk onderwerp, groot in beeld, in het midden/bovenste deel (onderste derde = ondertitels, linksboven = tijdstempel).
- Sterk licht en contrast: tegenlicht, randlicht, één accentkleur; geen vlak grijs of saai binnenlicht.
- Wissel shots af: totaal – close-up/macro – vogelvlucht – POV; nooit twee keer hetzelfde soort beeld achter elkaar.
- Elk prompt = onderwerp + actie + schaal + camerahoek + licht + sfeer.
- Test bij elk beeld: "snapt iemand zónder geluid wat er in deze zin gebeurt?" Zo niet: opnieuw.
- Het beeld bij "Then." toont HET omslagmoment van dít onderwerp (de maan die breekt, het hoofd dat door het plafond gaat,
  een zonnevlam …) – NOOIT een lichtflits, starburst, lichtring of lichtstraal: de witte flits zit al in de montage.
- Het twist-beeld en het slotbeeld krijgen extra drama (dat bepaalt of mensen reageren en blijven hangen).

### 4. Beelden maken (ComfyUI moet draaien op http://127.0.0.1:8188)
**Beeldcontrole = past het beeld bij de ZIN?** Geef `@beeldcontrole` per beeld (max 2 tegelijk) de gesproken zin uit
`script-cues.txt` mee en vraag letterlijk: "Toont dit beeld wat deze zin zegt? Beschrijf eerst wat je ziet, antwoord dan JA/NEE."
Alleen JA telt; mooi-maar-iets-anders = NEE = opnieuw met een ander prompt (andere fotosoort/hoek).
**Beelden altijd laten beoordelen door de subagent `@beeldcontrole`** (draait op een gratis model dat beelden
kan zien). Kun jij zelf geen afbeeldingen bekijken, gebruik hem dan ZEKER; nooit een beeld goedkeuren zonder dat het bekeken is.
Bestaat de subagent niet: meld dat in het rapport en zet "beelden niet bekeken" bovenaan.
**Vast beeldmodel (eigenaar 19 okt 2026): FLUX.2 [klein] 4B** (GGUF Q4_K_M, Apache 2.0) – volgt prompts veel beter dan Z-Image:
`python alteraqon/tools/comfy_batch.py C:\comfy-workflows\flux2klein_api.json alteraqon/<map> --short`
(Z-Image `zimage_api.json` alleen nog als reserve als Flux niet werkt.) Walvissen/dieren: schrijf "toothless mouth lined with
baleen" e.d. erbij – Flux tekent anders tanden.
- Bekijk ELK beeld. Klopt het niet met de zin (verkeerde/extra objecten, tekst, vervormde mensen): pas het prompt aan,
  gooi de png weg en draai opnieuw (alleen ontbrekende worden gemaakt). Max 3 pogingen per beeld.
- **Geen bewegende clips** (eigenaar 19 okt 2026: "laat die bewegende filmpjes maar zitten"). Alleen foto's + Ken Burns.
  Maak geen `comfy-clips.txt` en draai Wan niet.

### 5. Stem (vaste stem: Chatterbox `chatterbox_als_bm_george_rustig`, gratis)
`python alteraqon/tools/make_voice_local.py alteraqon/<map> ..\stem-cache --pause-ms 700 --long-pause-ms 1600 --sentence-pause-ms 600 --speed 0.92`
- Tempo (eigenaar 19 okt 2026: nog steeds te snel): lange pauzes + trager. Script dan ±105–120 woorden voor ±60–70 s.
- Draai dit met de Python waarin `chatterbox-tts` staat (niet de gewone python). Staat hieronder nog geen pad: zoek naar
  `...\Scripts\python.exe` waarmee `python -c "import chatterbox"` lukt (o.a. onder C:\Users\rane), en zet het pad hier:
  - Chatterbox-python: C:\Users\rane\Documents\Standaardproject\whatif\stem-env\Scripts\python.exe
- De stem duurt enkele minuten: start hem op de ACHTERGROND (anders kapt jouw shell-time-out hem af), NA de beelden
  (wacht tot ComfyUI klaar is: `curl -s http://127.0.0.1:8188/queue` → queue_running leeg):
  `Start-Process <Chatterbox-python> -ArgumentList 'alteraqon\tools\make_voice_local.py','alteraqon\<map>','..\stem-cache','--pause-ms','700','--long-pause-ms','1600','--sentence-pause-ms','600','--speed','0.92' -RedirectStandardOutput alteraqon\<map>\voice.log -WindowStyle Hidden`
  en kijk elke minuut of `voice-times.tsv` er is. Afgebroken? Gewoon opnieuw starten: de cache houdt klare zinnen.
- Eerst `--dry-run` om de regelnummers te zien. Controleer daarna `voice-times.tsv` (aantal regels, "Then." op de verwachte regel).

### 6. `shots.py` (zie `alteraqon/2026-10-18-moon-disappeared/shots.py`)
- `(regel in voice-times.tsv, beeld, beweging, filter, (label, groot getal) of None, [effect])`
- beweging: `in`, `out`, `up`, `shake`, `punch`; effect (optioneel): `dust`, `ash`, `embers`, `rain`.
- Shot bij "Then.": filter `FLASH`, en `BANG = <index van die shot, vanaf 0>`; `FADE_IN = 0`.
- Tijdstempels bij de tijdstappen/twist, bijv. `("NO MOON","1 DAY")` – zonder "AFTER" (dat zegt alleen de stem). Groot getal max ±13 tekens (anders past het niet).

### 7. Video renderen (uitvoer BUITEN de repo)
`make_video.py` draait eerst `alteraqon/tools/check_short.py` en weigert te renderen bij een FOUT. Los elke FOUT op
(script/prompts/shots/upload.json aanpassen, zo nodig stem opnieuw) – nooit de controle omzeilen of uitzetten.
`python alteraqon/tools/make_video.py alteraqon/<map> C:\Users\rane\Videos\alteraqon`
Controle: `ffprobe` → 1080x1920, video + audio, duur 60–75 s; `ffmpeg -v error -i <mp4> -f null -` geeft niets.

### 8. Afronden
- `upload.json` (zie voorbeeld + YouTube-regels in README: titel `What if …? <emoji>`, algemene beschrijving zonder feiten/twist, 4 hashtags incl. #shorts, 4 tags).
- In `upload.json` ook `"tiktok"`: 1–2 korte prikkelende zinnen met emoji (de twist niet verklappen, wel "wait for the twist"),
  een vraag aan de kijker met 👇, en 3–5 hashtags (altijd #whatif en #fyp + onderwerp). Max 2200 tekens.
- Voeg de video toe onder "Video's" in `alteraqon/README.md` (één regel).
- `git add alteraqon/<map> alteraqon/README.md` – NOOIT een eind-mp4 in git.
- `git commit -m "<slug>: nieuwe short (beelden, stem, shots)"` en `git push origin alteraqon`.
- **Kijklink voor de iPhone (via Tailscale)**: de eigenaar kijkt op zijn iPhone, alleen binnen zijn Tailscale-netwerk.
  - Tailscale-IP van deze pc: `tailscale ip -4` (begint met 100.).
  - Server: `alteraqon/tools/serve_videos.py` (bekijken + downloaden), ALLEEN op het Tailscale-IP (nooit 0.0.0.0).
    Test met `curl -s http://<ip>:8765/` of het overzicht "Alteraqon-video's" terugkomt. Zo niet (geen server, of nog de oude
    `python -m http.server`): stop wat er op poort 8765 draait
    (`Get-NetTCPConnection -LocalPort 8765 -State Listen | % { Stop-Process -Id $_.OwningProcess -Force }`) en start:
    `Start-Process python -ArgumentList 'alteraqon\tools\serve_videos.py','<ip>','8765','C:\Users\rane\Videos\alteraqon' -WindowStyle Hidden`
  - Links (controleer elk met `curl -I`, moet 200 geven; de downloadlink moet `Content-Disposition: attachment` hebben):
    - Overzicht: `http://<ip>:8765/`
    - Bekijken: `http://<ip>:8765/<slug>.mp4`
    - Downloaden: `http://<ip>:8765/<slug>.mp4?download=1` (iPhone: komt in Bestanden > Downloads)
  - Vraagt Windows Firewall om toestemming: meld dat de eigenaar "Privé netwerk" moet toestaan.
  - Zet de drie links bovenaan het rapport.
- Rapport aan de eigenaar: kijklink, pad van de mp4, duur, kosten (0: alles lokaal), korte samenvatting, feiten met bronnen, twijfels, beelden die niet lukten.

### 9. Online zetten (alleen als de eigenaar zegt "zet <video> op YouTube" / "zet online")
- Vereist de Windows-omgevingsvariabelen `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN_ALTERAQON`. Ontbreken ze: meld dat
  en stop (vraag NOOIT om de waarden in de chat; nooit in git, logs of rapporten zetten).
- `python alteraqon/tools/upload_short.py alteraqon/<map> C:\Users\rane\Videos\alteraqon\<slug>.mp4`
  (standaard openbaar; `--privacy unlisted` of `private` als de eigenaar dat vraagt). Ontbreekt de module requests: `pip install requests`.
- Het script controleert de video, weigert een tweede upload en zet de YouTube-link in `upload.json`.
  Commit + push daarna `upload.json` en meld de YouTube-link aan de eigenaar, met daaronder de TikTok-tekst (uit `upload.json`)
  in een kopieerbaar blok, plus de downloadlink van de mp4 (om in TikTok te plaatsen).

### 9b. Inplannen (eigenaar 20 okt 2026: vast uploadschema)
- Zegt de eigenaar "zet <video> op het schema" / "plan <video> in": upload met `--schedule` (lange video: `--schedule --long`).
  De video gaat privé naar YouTube en wordt automatisch openbaar op het eerstvolgende vrije tijdstip uit `alteraqon/schedule.json`
  (nu: Shorts 3x per dag 09:00/14:00/19:00, lange video's om de 2 dagen 15:00, Nederlandse tijd). Het tijdstip komt als `publish_at` in upload.json.
- Meld de eigenaar: YouTube-link + datum/tijd van publicatie (Nederlandse tijd) + TikTok-tekst/downloadlink (bij Shorts).
- "Zet online" zonder "schema" = meteen openbaar (stap 9).

### 10. Automatisch inplannen (eigenaar 20 okt 2026: "hij mag alles automatisch online zetten")
Na stap 8 zet je ELKE nieuwe video (Short én lange video) zelf op het schema, zonder te vragen:
`python alteraqon/tools/upload_short.py alteraqon/<map> C:\Users\rane\Videos\alteraqon\<slug>.mp4 --schedule` (lange video: `--schedule --long`).
Alleen als ALLES klopt:
- `check_short.py` groen en de render-controle (formaat, duur, geen decodeerfouten) goed;
- elk beeld JA bij @beeldcontrole (geen beeld met "max pogingen, toch NEE");
- de twist en elk getal staan met echte bron in `bronnen.txt`; geen twijfel over feiten.
Klopt iets niet: NIET uploaden, wel renderen + kijklink, en in het rapport bovenaan "NIET ingepland: <reden>".
Na het inplannen: commit + push `upload.json` (met `youtube` en `publish_at`), en rapporteer bovenaan:
YouTube-link, publicatiedatum/-tijd in Nederlandse tijd, kijk- en downloadlink; bij Shorts ook de TikTok-tekst in een kopieerbaar blok.

### 11. Nachtrun (eigenaar 20 okt 2026: "ik wil alles helemaal automatisch")
De Windows-taak `Alteraqon-Nachtrun` start elke nacht `alteraqon/tools/auto_run.ps1`. Die doet `git pull`, start ComfyUI en de
kijkserver, bepaalt met `auto_plan.py` hoeveel video's nodig zijn (Shorts aanvullen tot 3 ingepland, 1 lange video als er geen
meer ingepland staat) en start per video een verse sessie `opencode run "NACHTRUN …"`.
In een NACHTRUN:
- Er is niemand: stel NOOIT een vraag en wacht nergens op; beslis zelf (onderwerp, keuzes). Lukt iets echt niet: sla die video over.
- Volg alle stappen (0a, 0–8, 10) precies zoals gewoonlijk; inplannen alleen als alles klopt (stap 10).
- Rapport: voeg ONDERAAN toe aan `C:\Users\rane\Videos\alteraqon\rapport-<datum>.txt` (nooit overschrijven, UTF-8), max ±15 regels:
  `=== <titel> ===`, ingepland op <datum/tijd NL> + YouTube-link (of `NIET ingepland: <reden>`), kijk- en downloadlink,
  bronnen van de twist, beelden die niet lukten, en bij Shorts de TikTok-tekst. De eigenaar leest dit op zijn iPhone
  via `http://<tailscale-ip>:8765/` (kopje "Nachtrapporten").
- Commit + push zoals gewoonlijk; raak `alteraqon-auto.json` (instellingen van de pc, buiten git) niet aan.

## Lange YouTube-video (opdracht "Maak een lange Alteraqon-video: What if …?") – eigenaar 19 okt 2026
Zelfde regels als de Short (stap 0–9, beeldregels 3/3a/3a+/3b, Flux, @scriptschrijver, @beeldcontrole), met deze verschillen:
- **Voorbeeld = `alteraqon/2026-10-11-sky-countdown/`** (eigenaar: "heel goed voorbeeld"). @scriptschrijver leest eerst
  `script-cues.txt`, `upload.json` en `thumbnail.jpg` daarvan en volgt die stijl: wereldwijd mysterie, elke scène een andere plek
  of persoon ("In Tokyo… In New York…"), aftellende spanning met tijdstempels, ±450 woorden / 40 beelden / ±3 min,
  thumbnail met korte prikkelende tekst links en een gloeiend detail rechts.
- **Lengte/opbouw**: 3–5 min, ±300–480 woorden, 35–50 beelden. Opbouw in hoofdstukken: hook (eerste 10 s het spannendste
  beeld + de vraag) → opbouw → "Then." → 5–7 tijdstappen met tijdstempels → dieptepunt → "But here's the twist." (echt feit,
  bronnen) → slot met vraag aan de kijker. Spannend blijven: elke 20–30 s iets nieuws.
- **Beelden liggend 16:9**: `comfy_batch.py` ZONDER `--short` (1280x720). Prompts beginnen met `… vertical 9:16 …` vervangen
  door `… wide 16:9 …`. Onderste vijfde = ondertitels, linksboven = tijdstempel.
- **shots.py**: zet `LONG = True` (make_video maakt dan 1920x1080 en mixt `music.mp3`).
- **Muziek**: `python alteraqon/tools/make_music.py alteraqon/<map>` (na de stem; `--mood hopeful` voor een lichter onderwerp).
- **Thumbnail** (verplicht): maak een extra beeld `T01` in `prompts.txt` – het spannendste moment, onderwerp RECHTS, links rustige
  donkere ruimte – en `thumbnail.json`:
  `{"image": "T01", "small": "WHAT IF A WHALE…", "lines": ["SWALLOWED", "YOU?"], "accent": "red"}`
  (2–3 regels, max ±10 tekens per regel, prikkelend, de twist NIET verklappen). Dan
  `python alteraqon/tools/make_thumbnail.py alteraqon/<map>` → `thumbnail.jpg`; laat @beeldcontrole hem beoordelen
  ("zou jij hierop klikken? tekst leesbaar op telefoonformaat?").
- **upload.json**: zonder `#shorts`; beschrijving mag 2–4 zinnen + vraag + 3–4 hashtags; GEEN `"tiktok"` (TikTok-tekst alleen bij Shorts).
- **Controle**: duur 3–5 min, 1920x1080. Kijklink zoals bij Shorts.
- **Online zetten**: `python alteraqon/tools/upload_short.py alteraqon/<map> <mp4> --long` (met `--schedule` voor het schema).
  De thumbnail gaat automatisch mee zodra het kanaal geverifieerd is; lukt het niet, meld dat en stuur de eigenaar de
  downloadlink van thumbnail.jpg (kopieer hem naar C:\Users\rane\Videos\alteraqon\<slug>-thumbnail.jpg; link via de kijk-server).

## Niet doen
- Geen betaalde API's (xAI, ElevenLabs) zonder uitdrukkelijk ja.
- Niet uploaden als de video NIET aan alle eisen van stap 10 voldoet; dan alleen rapporteren.
- Geen scripts in `alteraqon/tools/` aanpassen. Geen andere branches of video-mappen aanraken.
- Geen nieuwe branch `alteraqon` aanmaken; hij bestaat op origin.
