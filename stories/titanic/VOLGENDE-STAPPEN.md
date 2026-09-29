# The Titanic: The Night It Sank — overdracht

## Wat klaar is (29-09-2026)
- Script: `the-titanic-the-night-it-sank.txt` (106.600 tekens, 15 hoofdstukken
  `01-belfast.txt` … `15-slot.txt`, 75 `{img:...}`-markeringen). Opzet: `OPZET.md`.
- Stem: xAI Lux, `audio/titanic-deel1..5.mp3` (1:50:15). NIET opnieuw maken:
  `tijdlijn.tsv` en `afbeeldingen-tijden.tsv` horen bij deze render.
- Met extra pauzes (`tools/add_pauses.py`): 2:14:11 (`tijdlijn-pauzes.tsv`,
  `afbeeldingen-tijden-pauzes.tsv`).
- 75 afbeeldingen (`grok-imagine-image`, $0,02) uit `afbeeldingen-onderwerpen.tsv`
  → `tools/make_image_prompts.py` → `afbeeldingen-prompts.md` → `tools/xai_images.py`.
- Muziek: `tools/ambient_432.py` in twee helften van 4040 s (seed 7 en 8) met een
  crossfade van 14 s; in één keer 8053 s liep het geheugen vol (14 GB).
- Video: `tools/make_video.py` (groepjes van 20 clips), 1080p25, 1,1 GB (niet in git).
- Thumbnail: `thumbnail.jpg` (achtergrond `thumbnail-achtergrond.jpg`, xAI).
- 4 Shorts (`shorts.tsv`, `shorts-intro/`), teksten in `shorts-teksten/`.

## Geüpload (privé, gepland; zie `planning.txt`)
- Lange video: https://youtu.be/aqbjvsBIQAE — openbaar ma 5 okt 2026 21:00
- Short 1-verrekijker: https://youtu.be/ytten26TTJ4 — di 6 okt 2026 18:00
- Short 4-foto: https://youtu.be/Jl75PNbdcWs — wo 7 okt 2026 18:00
- Beide Shorts op de TikTok-pagina (collectie `tiktoks`, `titanic-1-verrekijker`,
  `titanic-4-foto`).

## Kosten (xAI)
Stem ± $0,43, 75 afbeeldingen $1,50, thumbnail $0,02, 4 gesproken begintjes < $0,01:
samen ± $1,96.
