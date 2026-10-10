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
