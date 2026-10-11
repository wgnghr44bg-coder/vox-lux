# Alteraqon – "What if"-documentaires (YouTube: @alteraqon)

Apart kanaal, los van IfScape3D (3D-render, Atlas-stem) en Sleep Archives.

## Stijl
- Verticaal 1080x1920, ca. 60–70 s, Engels.
- AI-foto's (xAI `grok-imagine-image`, 9:16), één beeld per gesproken zin, langzame zoom/pan, koele documentaire-grade + lichte filmkorrel.
- Stem: xAI **Lux**, tempo 0.9, pauzes 900/1700 ms + 600 ms na elke zin (`[pause]` achter elke regel).
- Tijdstempels als korte lower-third (~2,6 s): goud lijntje schuift in, label in Inter SemiBold, groot getal in Inter Display Light.
- Ondertitels in Inter SemiBold. Donkere drone + lage klap bij elke tijdstempel.

## Per video
Map `<datum>-<slug>/`: `script-cues.txt` (tekst + `{img:Sxx}`), `prompts.txt`, `afbeeldingen/`, `voice.mp3`,
`voice-times.tsv`, `make.py` (beeld + tekst + eindmix), `upload.json`. Geen mp4 in git.

Kosten per video: ca. $0,30 (≈13 afbeeldingen à $0,02 + een paar cent stem).

## Video's
- `2026-10-10-humans-vanish/` – What if all humans vanished? (eindversie: `doc/make-doc-lux.py`)
- `2026-10-10-struck-by-lightning/` – What if you got struck by lightning? (`make.py`)
- `2026-10-10-asteroid-missed/` – What if the asteroid that killed the dinosaurs had missed? **Lange video**, 16:9 1920x1080, ca. 3 min (`make.py`, `make_thumbnail.py` → `thumbnail.jpg`)

## Opbouw van elke video (sjabloon = de lightning-video)
Kopieer `_sjabloon/` naar `<datum>-<slug>/` en vul in. Verhaal in 6 stappen, ca. 18 zinnen, 65–75 s:
1. **Opening:** "Imagine… <onderwerp>. What would happen…?" (zegt meteen waar de video over gaat; geen titel in beeld)
2. **POV-opbouw:** jij staat ergens, kleine voortekenen, spanning.
3. **Het moment:** één kort woord ("Then.") + witte flits en knal (`BANG` in shots.py).
4. **Feiten met grote getallen:** elk feit een eigen beeld + tijdstempel (label + getal, ~2,6 s in beeld).
5. **Dieptepunt, dan de twist ("But…"):** verrassend detail, goede afloop, een bizar echt record.
6. **Slot:** "So remember." + les of vraag aan de kijker.

Regels: één beeld per (deel)zin, wissel precies op de stem; elke zin eindigt op `[pause]` of `[long pause]`;
feiten alleen als ze algemeen bekend en controleerbaar zijn; ca. 13 afbeeldingen (≈ $0,30 per video).

Stappen (vanuit de map `vox-lux`):
```
cp -r alteraqon/_sjabloon alteraqon/<datum>-<slug>       # daarna script-cues.txt, prompts.txt, shots.py, upload.json invullen
python3 alteraqon/tools/make_images.py alteraqon/<datum>-<slug>
python3 alteraqon/tools/make_voice.py  alteraqon/<datum>-<slug>
python3 alteraqon/tools/make_video.py  alteraqon/<datum>-<slug> <tmpmap>    # -> <tmpmap>/<slug>.mp4
```
In `shots.py` verwijst het eerste getal naar de regel in `voice-times.tsv` (pas invullen ná make_voice).

## Lange video (16:9, ca. 3 min) – voorbeeld: de asteroid-video
Zelfde stijl, maar liggend en ca. 40 zinnen / 38 beelden (≈ $0,80 aan beelden + een paar cent stem):
- `python3 alteraqon/tools/make_images.py <map> 16:9` (beelden 16:9; `T01` = basis voor de thumbnail)
- `python3 alteraqon/tools/make_voice.py <map> <cachemap buiten repo>` (cache: na inkorten alleen nieuwe zinnen betalen)
- `make.py`: beelden volgen de kolom `image` in voice-times.tsv; tijdstempels per regelnummer; label linksboven
  scheidt feiten (`REAL HISTORY`) van speculatie (`ALTERNATE TIMELINE · SPECULATION`).
- Thumbnail 1280x720 met `make_thumbnail.py` in de videomap (tekst links, YouTube zet de duur rechtsonder).
- YouTube-tekst als hieronder, maar zonder `#shorts`.

## YouTube-tekst (vaste opzet, eigenaar okt 2026: kort en simpel)
Per video invullen met het onderwerp; niet meer feiten erbij zetten.

- **Titel:** `What if <vraag>? <emoji>`
- **Beschrijving:** één regel met 2–3 korte, verrassende feiten + twist, een vraag aan de kijker met 👇, dan 4 hashtags.
- **Tags:** 4 stuks: `what if`, onderwerp, langere zoekterm, `science`.
- In Studio: "Gewijzigde of synthetische content" → **Ja**.

Voorbeeld (lightning):
```
What if you got struck by lightning? ⚡
```
```
300 million volts. Five times hotter than the Sun. And yet, most people survive.

Would you go outside during a storm? 👇

#whatif #lightning #science #shorts
```
```
what if, lightning, struck by lightning, science
```
