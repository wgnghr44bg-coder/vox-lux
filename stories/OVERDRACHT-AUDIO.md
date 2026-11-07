# Overdracht (7 nov 2026, nacht) – nieuwe stem, muziek en opbouw

Lees eerst CLAUDE.md, audio_engine/README.md en stories/PROMPT-ROUTINE-PC.md. Praat Nederlands, simpel. Alles gratis/lokaal.

## Besluiten van de eigenaar (6-7 nov 2026)
- **Muziek: klaar en goed** ("de achtergrond muziek is perfect"): Audio Engine-preset `referentie` (zacht koor/strijkers,
  432 Hz, elke 7 s een ander akkoord, geen regen), in de videostraat via `tools/engine_muziek.py <map>`.
- **Opbouw** zoals Sleepy History: ± 90 losse feitjes (kopzin + ± 200 woorden), **geen intro** (meteen eerste feitje,
  geen "Tonight..."), **geen Sleep Archives-begin/-einde** (`"intro": False, "slot": False` in maak_motion.py),
  kort slot (± 30 s, per video anders, met volgende-video-zin, abonneren, "Sleep well, and good night.").
- **Titels**: vraag-titels zonder uren, bv. "What Was Life Really Like in Tombstone? | History for Sleep".
- **Stem: NOG NIET GEKOZEN.** Eigenaar wil: rustiger en warmer, "dat je echt van in slaap valt", zoals de opdracht
  (Britse man 60-70, diep, warm, borstklank, licht hees/ademend, kalm). Afgewezen: professor-1..4, verteller-1..4
  (audio_engine/voices/), narrator-c/d. Laatst gestuurd: stem B (narrator-b) nog rustiger, 111 en 104 woorden/min
  (speed 0.54 + rubberband tempo 0.85/0.80 + warme EQ `lowshelf=f=180:g=3,highshelf=f=4500:g=-4,deesser=i=0.3,
  acompressor=threshold=-24dB:ratio=2.5:attack=15:release=250:makeup=1.5`). Daarna vroeg hij: "compleet andere Britse
  stemmen die lijken op de video" (Sleepy History, https://youtu.be/Ah58uaESJzc: ± 99 Hz, helderheid ± 1000 Hz,
  ± 130 woorden/min). Plan: veel OmniVoice-ontwerpen (male, middle-aged/elderly, low/moderate pitch, british accent,
  nieuwe seeds) meten op toonhoogte/helderheid/melodie/tempo (scratchpad-script stond in verteller_zoek.py), beste 4
  als proef met het koor sturen (zelfde stukje WW2: tweede feitje over de verduistering). **Niet** iemands stem klonen.
- Zet de gekozen stem daarna in `stories/<map>/stem.json` (engine_voice, speed, klank) en in PROMPT-ROUTINE-PC.md.

## Stand van de video's
- **WW2 Facts (za 7 nov 21:00)**: de OUDE versie hVg9nrutQVI (Slaap 3) gaat vanavond online. Nieuwe versie niet af.
- **Tombstone (wo 11 nov, privé 4RjjJh-j5a0)**: omgeschreven naar 90 feitjes (src-feiten/, bouw_script.py,
  maak_motion.py, beschrijving zonder regen). Nog te doen: stem (na de stemkeuze), dan
  `tools/prep_engine.sh`, herstel_zinnen, `tools/montage_engine.sh tombstone-1881 "<titel>" thumbnail-gekozen.jpg`,
  upload privé (publishAt 2026-11-11T20:00:00Z, playlist mysterie), kanaal Sleep Archives controleren,
  `tools/wacht_verwerkt.py`, dan pas de oude privéversie verwijderen.
- **Egypte (za 14 nov, privé ctC36HRFIac)**: src-feiten/deel1.txt klaar (feitjes 1-31 bij beelden 001-031).
  Nog schrijven: deel2/deel3 (feitjes 32-92, één per beeld 032-092, zie afbeeldingen-onderwerpen.tsv), dan
  bouw_script.py en maak_motion.py ombouwen zoals bij tombstone-1881, beschrijving zonder regen.
- **Gettysburg (wo 18) en volgende**: de routine bouwt elk script zelf om (staat in het voorschrift).

## Gereedschap
- Stem: `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_stem.py stories/<map> [--hergebruik]`
- Montage: `REPO=... bash tools/prep_engine.sh <map>` en `bash tools/montage_engine.sh <map> "<titel>" <thumbnail>`
- Video bekijken/beluisteren: `.../python.exe tools/kijk_video.py <youtube-link>`
- Proeven: audio_engine (narrate, generate, mix); interface: audio_engine/start_audio_engine.bat
