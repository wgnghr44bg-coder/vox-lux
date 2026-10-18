# AGENTS.md – Alteraqon-shorts zelfstandig maken (pc van de eigenaar)

Dit bestand is voor een AI-agent (OpenCode / LongCat) op de pc van de eigenaar. Volledige regels: `alteraqon/README.md` (lees die eerst).
Werk op branch `alteraqon` (deze map: `vox-lux-alteraqon`). Schrijf kort en in het Nederlands naar de eigenaar.

## Opdracht "Maak een Alteraqon-short: What if …?"
Voer alle stappen zelf uit. Stop alleen bij een echte blokkade en meld dan exact wat er misgaat.

### 1. Voorbereiden
- `git pull origin alteraqon`
- Map: `alteraqon/<datum van vandaag>-<korte-slug>/` (bijv. `2026-10-20-sun-vanished`). Kopieer niet het sjabloon blind; volg het voorbeeld `alteraqon/2026-10-18-moon-disappeared/`.

### 2. Script (`script-cues.txt`)
- Engels, ±130–150 woorden (≈60 s), korte spannende zinnen. Elke regel eindigt op `[pause]` of `[long pause]`.
- `{img:M01}` op een eigen regel vóór elk stukje tekst; ±1 beeld per zin, 17–20 beelden.
- Opbouw: opening "What if …?" → POV-opbouw → "Then." (eigen beeld, witte flits + klap) → 3–4 tijdstappen met groot getal
  → "But here's the twist." met een ECHT feit → "So remember." + vraag aan de kijker.
- Getallen VOLUIT schrijven ("nineteen sixty-nine", "three point eight"), anders spreekt Chatterbox ze verkeerd uit.
- Feiten: alleen algemeen bekende, controleerbare feiten. Noteer per feit een bron (URL) voor het eindrapport.
  Twijfel je aan een getal, zeg "about" / "could" of laat het weg.

### 3. Beeldprompts (`prompts.txt`), één regel per beeld: `M01|<prompt>`
- Begin foto's met: `Cinematic photo, vertical 9:16, hyperrealistic, dramatic lighting, epic, high detail, no text, no logos,`
- Wetenschap/ruimte/lichaam: `Scientific 3D render, vertical 9:16, photorealistic, cinematic lighting, epic, high detail, no text, no labels, no logos,`
- Elk beeld toont LETTERLIJK wat er in die zin gezegd wordt; "wow"-beelden. Geen gezichten of handen in close-up; mensen alleen als silhouet/van achteren.
- Noem iets wat NIET in beeld mag NOOIT bij naam (ook niet als "no moon"): het model tekent het dan juist. Beschrijf alleen wat er wél is.
- Geen echte merken/logo's.

### 4. Beelden maken (ComfyUI moet draaien op http://127.0.0.1:8188)
`python alteraqon/tools/comfy_batch.py C:\comfy-workflows\zimage_api.json alteraqon/<map> --short`
- Bekijk ELK beeld. Klopt het niet met de zin (verkeerde/extra objecten, tekst, vervormde mensen): pas het prompt aan,
  gooi de png weg en draai opnieuw (alleen ontbrekende worden gemaakt). Max 3 pogingen per beeld.
- Geen bewegende clips tenzij de eigenaar erom vraagt.

### 5. Stem (vaste stem: Chatterbox `chatterbox_als_bm_george_rustig`, gratis)
`python alteraqon/tools/make_voice_local.py alteraqon/<map> ..\stem-cache --pause-ms 350 --long-pause-ms 800 --sentence-pause-ms 250`
- Eerst `--dry-run` om de regelnummers te zien. Controleer daarna `voice-times.tsv` (aantal regels, "Then." op de verwachte regel).

### 6. `shots.py` (zie `alteraqon/2026-10-18-moon-disappeared/shots.py`)
- `(regel in voice-times.tsv, beeld, beweging, filter, (label, groot getal) of None, [effect])`
- beweging: `in`, `out`, `up`, `shake`, `punch`; effect (optioneel): `dust`, `ash`, `embers`, `rain`.
- Shot bij "Then.": filter `FLASH`, en `BANG = <index van die shot, vanaf 0>`; `FADE_IN = 0`.
- Tijdstempels bij de tijdstappen/twist, bijv. `("NO MOON","1 DAY")`. Groot getal max ±12 tekens (anders past het niet).

### 7. Video renderen (uitvoer BUITEN de repo)
`python alteraqon/tools/make_video.py alteraqon/<map> C:\Users\rane\Videos\alteraqon`
Controle: `ffprobe` → 1080x1920, video + audio, duur 55–65 s; `ffmpeg -v error -i <mp4> -f null -` geeft niets.

### 8. Afronden
- `upload.json` (zie voorbeeld + YouTube-regels in README: titel `What if …? <emoji>`, algemene beschrijving zonder feiten/twist, 4 hashtags incl. #shorts, 4 tags).
- Voeg de video toe onder "Video's" in `alteraqon/README.md` (één regel).
- `git add alteraqon/<map> alteraqon/README.md` – NOOIT een eind-mp4 in git.
- `git commit -m "<slug>: nieuwe short (beelden, stem, shots)"` en `git push origin alteraqon`.
- Rapport aan de eigenaar: pad van de mp4, duur, kosten (0: alles lokaal), korte samenvatting, feiten met bronnen, twijfels, beelden die niet lukten.

## Niet doen
- Geen betaalde API's (xAI, ElevenLabs) zonder uitdrukkelijk ja. Niet uploaden naar YouTube.
- Geen scripts in `alteraqon/tools/` aanpassen. Geen andere branches of video-mappen aanraken.
- Geen nieuwe branch `alteraqon` aanmaken; hij bestaat op origin.
