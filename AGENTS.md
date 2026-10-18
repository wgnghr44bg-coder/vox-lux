# AGENTS.md – Alteraqon-shorts zelfstandig maken (pc van de eigenaar)

Dit bestand is voor een AI-agent (OpenCode / LongCat) op de pc van de eigenaar. Volledige regels: `alteraqon/README.md` (lees die eerst).
Werk op branch `alteraqon` (deze map: `vox-lux-alteraqon`). Schrijf kort en in het Nederlands naar de eigenaar.

## Opdracht "Maak een Alteraqon-short: What if …?"
Voer alle stappen zelf uit. Stop alleen bij een echte blokkade en meld dan exact wat er misgaat.
**De eigenaar zit NIET achter de pc** (hij volgt alles op zijn iPhone). Vraag hem nooit om zelf een commando te draaien,
iets te installeren of een omgeving te activeren: zoek het zelf uit en doe het zelf. Vragen mag alleen over inhoud (onderwerp, keuze).

### 1. Voorbereiden
- `git pull origin alteraqon`
- Map: `alteraqon/<datum van vandaag>-<korte-slug>/` (bijv. `2026-10-20-sun-vanished`). Kopieer niet het sjabloon blind; volg het voorbeeld `alteraqon/2026-10-18-moon-disappeared/`.

### 2. Script (`script-cues.txt`)
- Engels, ±120–135 woorden (≈60–70 s met het rustige tempo), korte spannende zinnen. Elke regel eindigt op `[pause]` of `[long pause]`.
- `{img:M01}` op een eigen regel vóór elk stukje tekst; ±1 beeld per zin, 17–20 beelden.
- Opbouw: opening "What if …?" → POV-opbouw → "Then." (eigen beeld, witte flits + klap) → 3–4 tijdstappen met groot getal
  → "But here's the twist." met een ECHT feit → "So remember." + vraag aan de kijker.
- Tijdstappen altijd met "After": gesproken "After one day.", tijdstempel `("NO MOON","AFTER 1 DAY")` (groot getal max ±13 tekens).
  Geen opvulzinnen als "Right now." na de openingsvraag.
- Getallen VOLUIT schrijven ("nineteen sixty-nine", "three point eight"), anders spreekt Chatterbox ze verkeerd uit.
- Feiten: alleen algemeen bekende, controleerbare feiten. Noteer per feit een bron (URL) voor het eindrapport.
  Twijfel je aan een getal, zeg "about" / "could" of laat het weg.

### 3. Beeldprompts (`prompts.txt`), één regel per beeld: `M01|<prompt>`
- Begin foto's met: `Cinematic photo, vertical 9:16, hyperrealistic, dramatic lighting, epic, high detail, no text, no logos,`
- Wetenschap/ruimte/lichaam: `Scientific 3D render, vertical 9:16, photorealistic, cinematic lighting, epic, high detail, no text, no labels, no logos,`
- Elk beeld toont LETTERLIJK wat er in die zin gezegd wordt; "wow"-beelden. Geen gezichten of handen in close-up; mensen alleen als silhouet/van achteren.
- Noem iets wat NIET in beeld mag NOOIT bij naam (ook niet als "no moon"): het model tekent het dan juist. Beschrijf alleen wat er wél is.
- Geen echte merken/logo's.
- Geen linialen, meetlatten, grafieken, klokken of borden: het model maakt daar onleesbare cijfers/tekst van.
- Echte (historische) personen nooit herkenbaar of als nep-"foto": alleen silhouet, van achteren, of een voorwerp van hen.
- Feiten over oorzaken ("zijn hart faalde") altijd nazoeken; liever weglaten dan gokken.

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
- Het twist-beeld en het slotbeeld krijgen extra drama (dat bepaalt of mensen reageren en blijven hangen).

### 4. Beelden maken (ComfyUI moet draaien op http://127.0.0.1:8188)
`python alteraqon/tools/comfy_batch.py C:\comfy-workflows\zimage_api.json alteraqon/<map> --short`
- Bekijk ELK beeld. Klopt het niet met de zin (verkeerde/extra objecten, tekst, vervormde mensen): pas het prompt aan,
  gooi de png weg en draai opnieuw (alleen ontbrekende worden gemaakt). Max 3 pogingen per beeld.
- Geen bewegende clips tenzij de eigenaar erom vraagt.

### 5. Stem (vaste stem: Chatterbox `chatterbox_als_bm_george_rustig`, gratis)
`python alteraqon/tools/make_voice_local.py alteraqon/<map> ..\stem-cache --pause-ms 500 --long-pause-ms 1200 --sentence-pause-ms 400 --speed 0.95`
- Tempo (eigenaar 18 okt 2026): rustiger dan eerst, langere pauzes + iets trager. Script dan ±120–135 woorden voor ±60–70 s.
- Draai dit met de Python waarin `chatterbox-tts` staat (niet de gewone python). Staat hieronder nog geen pad: zoek naar
  `...\Scripts\python.exe` waarmee `python -c "import chatterbox"` lukt (o.a. onder C:\Users\rane), en zet het pad hier:
  - Chatterbox-python: C:\Users\rane\Documents\Standaardproject\whatif\stem-env\Scripts\python.exe
- Eerst `--dry-run` om de regelnummers te zien. Controleer daarna `voice-times.tsv` (aantal regels, "Then." op de verwachte regel).

### 6. `shots.py` (zie `alteraqon/2026-10-18-moon-disappeared/shots.py`)
- `(regel in voice-times.tsv, beeld, beweging, filter, (label, groot getal) of None, [effect])`
- beweging: `in`, `out`, `up`, `shake`, `punch`; effect (optioneel): `dust`, `ash`, `embers`, `rain`.
- Shot bij "Then.": filter `FLASH`, en `BANG = <index van die shot, vanaf 0>`; `FADE_IN = 0`.
- Tijdstempels bij de tijdstappen/twist, bijv. `("NO MOON","AFTER 1 DAY")`. Groot getal max ±13 tekens (anders past het niet).

### 7. Video renderen (uitvoer BUITEN de repo)
`python alteraqon/tools/make_video.py alteraqon/<map> C:\Users\rane\Videos\alteraqon`
Controle: `ffprobe` → 1080x1920, video + audio, duur 55–65 s; `ffmpeg -v error -i <mp4> -f null -` geeft niets.

### 8. Afronden
- `upload.json` (zie voorbeeld + YouTube-regels in README: titel `What if …? <emoji>`, algemene beschrijving zonder feiten/twist, 4 hashtags incl. #shorts, 4 tags).
- Voeg de video toe onder "Video's" in `alteraqon/README.md` (één regel).
- `git add alteraqon/<map> alteraqon/README.md` – NOOIT een eind-mp4 in git.
- `git commit -m "<slug>: nieuwe short (beelden, stem, shots)"` en `git push origin alteraqon`.
- **Kijklink voor de iPhone (via Tailscale)**: de eigenaar kijkt op zijn iPhone, alleen binnen zijn Tailscale-netwerk.
  - Tailscale-IP van deze pc: `tailscale ip -4` (begint met 100.).
  - Draait er nog geen server op poort 8765 (`Test-NetConnection <ip> -Port 8765`), start hem op de achtergrond, ALLEEN op het Tailscale-IP (nooit 0.0.0.0):
    `Start-Process python -ArgumentList '-m','http.server','8765','--bind','<ip>','--directory','C:\Users\rane\Videos\alteraqon' -WindowStyle Hidden`
  - Link: `http://<ip>:8765/<slug>.mp4` – open hem zelf even met `curl -I` (moet 200 geven) voordat je hem doorgeeft.
  - Vraagt Windows Firewall om toestemming: meld dat de eigenaar "Privé netwerk" moet toestaan.
  - Zet de link bovenaan het rapport. (Op de iPhone: link openen in Safari = kijken; deelknop → "Bewaar in Bestanden" = downloaden.)
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
