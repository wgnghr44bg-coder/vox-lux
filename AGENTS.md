# AGENTS.md – Alteraqon-shorts zelfstandig maken (pc van de eigenaar)

Dit bestand is voor een AI-agent (OpenCode / LongCat) op de pc van de eigenaar. Volledige regels: `alteraqon/README.md` (lees die eerst).
Werk op branch `alteraqon` (deze map: `vox-lux-alteraqon`). Schrijf kort en in het Nederlands naar de eigenaar.

## Opdracht "Maak een Alteraqon-short: What if …?"
Voer alle stappen zelf uit. Stop alleen bij een echte blokkade en meld dan exact wat er misgaat.
**De eigenaar zit NIET achter de pc** (hij volgt alles op zijn iPhone). Vraag hem nooit om zelf een commando te draaien,
iets te installeren of een omgeving te activeren: zoek het zelf uit en doe het zelf. Vragen mag alleen over inhoud (onderwerp, keuze).

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
`python alteraqon/tools/comfy_batch.py C:\comfy-workflows\zimage_api.json alteraqon/<map> --short`
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
  Commit + push daarna `upload.json` en meld de link aan de eigenaar.

## Niet doen
- Geen betaalde API's (xAI, ElevenLabs) zonder uitdrukkelijk ja.
- Nooit uit jezelf uploaden naar YouTube. Alleen als de eigenaar in DEZE sessie letterlijk vraagt om een video online / op YouTube te zetten (zie stap 9).
- Geen scripts in `alteraqon/tools/` aanpassen. Geen andere branches of video-mappen aanraken.
- Geen nieuwe branch `alteraqon` aanmaken; hij bestaat op origin.
