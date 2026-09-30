# The San Francisco Earthquake of 1906 — overdracht

## Wat klaar is (29-09-2026)
- Script: `san-francisco-1906.txt` (samengevoegd uit de genummerde stukken, zie `OPZET.md`),
  14.987 woorden, 75 `{img:...}`-markeringen.
- Stem: xAI Lux, 1:33:07 → `audio/sf1906-deel1..4.mp3` (achter elkaar = de hele render).
  NIET opnieuw maken: `tijdlijn.tsv` en `afbeeldingen-tijden.tsv` horen bij deze render.
- Met extra pauzes (`tools/add_pauses.py`): 1:53:01 → `tijdlijn-pauzes.tsv`,
  `afbeeldingen-tijden-pauzes.tsv`.
- 75 afbeeldingen (`grok-imagine-image`, $0,02 per stuk) uit `afbeeldingen-prompts.md`.
  Bekend foutje: 062 (Angel Island ± 1910) toont de Golden Gate Bridge; op enkele
  beelden staan in de verte moderne torens.
- Thumbnail: `thumbnail.jpg` (achtergrond `thumbnail-achtergrond.jpg`, xAI).
- YouTube-teksten: `youtube-beschrijving.txt`, Shorts in `shorts-teksten/`.
- Shorts: `shorts.tsv` (4 stuks), gesproken begin in `shorts-intro/`.
  Geüpload: 1-wijn en 3-caruso. Niet geüpload: 2-zuurdesem, 4-hydrant.
- Geüpload 29-09-2026 (privé, gepland via publishAt):
  - lang: https://youtu.be/TRcttN943sA — openbaar za 3 okt 21:00
  - Short 1-wijn: https://youtu.be/KaB4T_to8a8 — zo 4 okt 18:00
  - Short 3-caruso: https://youtu.be/vfsBvOUu63k — ma 5 okt 18:00
- Upload en planning: `upload.sh`, `planning.txt` (met links).
- 30-09-2026: nieuwe versie v2 (motion graphics + effecten, `motion.json`, `effecten.tsv`):
  https://youtu.be/6FIgJoXzr3Q — openbaar za 3 okt 21:00; oude TRcttN943sA verwijderen.

## Lessen
- 75 clips in één ffmpeg-stap → geheugentekort. `tools/make_video.py` zet nu eerst
  groepjes van 20 aan elkaar. `--preset veryfast` voor de eindvideo scheelt veel tijd.
- Een herstart van de container stopt lopende renders; bestanden in `video/`
  (niet in git) blijven wel staan zolang de sessie bestaat.
- `tools/youtube_upload.py --publish-at <UTC>` plant de publicatie (privé tot dan).

## Kosten (xAI)
- Stem: 86.127 tekens × $4,20 per miljoen ≈ $0,36
- Afbeeldingen: 75 + 1 opnieuw (045) = 76 × $0,02 ≈ $1,52
- Thumbnail-achtergrond: $0,02
- Gesproken begin Shorts: 434 tekens ≈ $0,002
- Totaal ≈ $1,90
