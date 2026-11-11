# Video opnieuw maken volgens de nieuwe regels (eigenaar 11 nov 2026)

Eigenaar 11 nov 2026: "Je mag de video's opnieuw maken volgens de nieuwe regels, met de nieuwe stem en toon, alle
video's moeten opnieuw." Deze prompt maakt **één** video (de map staat in de opdracht) helemaal opnieuw en vervangt de
versie die al privé op YouTube staat. Hij draait op de pc via `tools/opnieuw_keten.ps1` (`claude -p`). Niemand kijkt
mee: vraag niets, werk alles af. Lukt iets niet, schrijf het in `stories/ROUTINE-LOG.md` en stop (niets verwijderen).

Nieuwe regels (lees ze eerst): `CLAUDE.md` ("Eerst lezen" en "Stand 11 nov 2026"), `stories/OPBOUW.md` (opbouw + toon),
`stories/PROMPT-SCRIPT-PC.md` (schrijfregels, "Toon zoals de grote slaapkanalen"), `audio_engine/B1.json` (vaste stem:
de eigen stem van de eigenaar, W3-muziek 19 LUFS onder). Voor alles wat hier niet staat: `stories/PROMPT-ROUTINE-PC.md`
stap 4-6 (beelden, thumbnail, stem, montage, controles, upload, opruimen).

1. `git pull`. Zet in `stories/<map>/planning.txt` de status op `bezig (opnieuw <datum>, nieuwe regels)` (commit + push).
2. **Script in de nieuwe toon.** Herschrijf `src-feiten/begin.txt`, `deel*.txt` (HEAD, BODY, BRIDGE) en `slot.txt` in de
   nieuwe toon (voorbeeld: `stories/_toon-proef/gettysburg-nieuwe-toon.txt`). **Zelfde feiten, niets verzinnen; laat
   elke `IMG:`-regel en `TOPIC:`-regel precies staan** (dan passen de bestaande beelden en hoofdstukken nog). Opbouw volgens
   OPBOUW.md. Draai `python stories/<map>/bouw_script.py`, dan moeten allemaal goed zijn:
   - `python tools/script_leesbaar.py stories/<map>` → `MAKKELIJK` én `TOON GOED`
   - `python tools/check_afwisseling.py stories/<map>` → `AFWISSELING GOED`
   - `python -c "import sys; sys.path.insert(0,'tools'); import script_check as s; from pathlib import Path; print(s.controleer(Path('stories/<map>'), met_model=False)[0])"` → `[]`
   Commit + push het script.
3. **Beelden.** Staan alle beelden uit prompts.txt al in `afbeeldingen/` (en zijn ze eerder goedgekeurd), gebruik ze.
   Anders maken en controleren zoals PROMPT-ROUTINE-PC.md stap 4 (comfy, `tools/beeldcheck.py`). Thumbnail: bestaat
   `thumbnail-gekozen.jpg`, houd hem; anders maken zoals PROMPT-ROUTINE-PC.md.
4. **Stem en muziek** met de vaste stem: eerst `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/b1_check.py`
   (moet `B1 GOED`), dan de stem helemaal opnieuw (géén `--hergebruik`, de stem is nieuw):
   `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_stem.py stories/<map>`, dan
   `bash tools/prep_engine.sh <map>` (tekstcontrole; bij TEKST FOUT die zinnen opnieuw met `engine_stem.py --hergebruik
   --opnieuw <nrs> --seed-extra 3000` en prep opnieuw, max 3 rondes).
5. **Montage**: `bash tools/montage_engine.sh <map> "<titel uit planning.txt>" thumbnail-gekozen.jpg`. Die doet muziek,
   beweging, tikjes, controles, -14 LUFS, 16mm, QC en de strenge haperingcontrole (`tools/vergelijk_bron.py`).
   Alleen verder als `CONTROLE GOED`, `TEKST GOED`, `APPROVED` én bij de haperingcontrole `<0.6: 0`.
6. **Upload en vervangen**: `python tools/vervang_video.py stories/<map> --video stories/<map>/video/<map>-16mm.mp4
   --publish-at <datum uit planning.txt 21:00 NL in UTC, bv. 2026-11-14T20:00:00Z> --thumbnail stories/<map>/thumbnail-gekozen.jpg
   --soort <soort uit planning.txt> --oud <de youtu.be-id die nu in planning.txt staat, als die er is> --tags "<5 tags>"`.
   Dat uploadt privé met publicatietijd, zet afspeellijsten, wacht tot YouTube klaar is, verwijdert pas dan de oude
   privéversie (alleen als die privé is en op Sleep Archives staat), ruimt op en werkt planning.txt bij.
   Ligt de publicatiedatum minder dan 6 uur in de toekomst of al voorbij: niet uploaden, in ROUTINE-LOG.md zetten.
7. Eén regel in `stories/ROUTINE-LOG.md`: `<map>: opnieuw gemaakt (nieuwe toon, eigen stem), <link>`. Commit + push.
