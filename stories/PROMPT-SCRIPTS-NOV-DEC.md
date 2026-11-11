# Scripts voor de planning van 16 nov t/m 16 dec 2026 (eigenaar 11 nov 2026)

Start: "Lees stories/PROMPT-SCRIPTS-NOV-DEC.md en voer het uit". Werk af zonder te vragen.

De eigenaar heeft op 11 nov de planning gekozen op hype en jaardagen (gemeten met `tools/sleep_trends.py`). De datums
staan al in de planning.txt van elke map. Jouw taak: **de scripts maken, in deze volgorde**, elk precies volgens
`stories/PROMPT-SCRIPT-PC.md` (stap 0, 2, 3 en 4; stap 1 "welk script" sla je over, die volgorde staat hieronder).
Alleen tekst: geen beelden, geen stem, geen video, niets wat geld kost. Eén script per keer: na elk script
committen en pushen naar main, dan het volgende.

## Volgorde (de eerste twee zijn haastig)
| # | Map | Datum | Wat |
|---|---|---|---|
| 1 | `crisis-1933` | **ma 16 nov** | ombouwen naar nieuwe opbouw + nieuwe toon (Great Depression, groeit nu: Sleepy History Channel ± 3.900 views/dag) |
| 2 | `thanksgiving-1621` (nieuw) | **wo 25 nov** | **nieuw schrijven**: de eerste Thanksgiving in Plymouth, herfst 1621 (Wampanoag en Pilgrims, het eerste jaar na de Mayflower). Titel bv. "What Was the First Thanksgiving Really Like? \| History for Sleep". Sluit aan op onze Mayflower-video (die groeit nu door Thanksgiving); niet dezelfde feiten als die video herhalen (https://youtu.be/_duWLxwIEss; script op branch `mayflower-pc`, `git show origin/mayflower-pc:stories/mayflower/...`). Soort `reis` (zie tools/youtube_playlist.py) |
| 3 | `pearl-harbor-1941` | za 28 nov | nieuwe toon (al nieuwe opbouw) |
| 4 | `boeren-winter-1300` | wo 2 dec | ombouwen + nieuwe toon (winter/kou is nu hot) |
| 5 | `kerst-loopgraven-1914` | za 5 dec | ombouwen + nieuwe toon |
| 6 | `rome-44-vc` | wo 9 dec | nieuwe toon (al nieuwe opbouw) |
| 7 | `zwarte-dood-1348` | za 12 dec | ombouwen + nieuwe toon; ook de 7 feitjes uit scriptcheck.json vervangen |
| 8 | `scott-antarctica-1912` | wo 16 dec | nieuwe toon (al nieuwe opbouw) |

Al klaar in de nieuwe toon (niet aankomen): babylon-600-vc (za 14 nov), gettysburg-1863 (wo 18 nov), dallas-1963
(za 21 nov), egypte-toetanchamon (ma 23 nov). tombstone-1881 is naar reserve gezet.

## Nieuwe toon
Zoals stories/OPBOUW.md en het voorbeeld `stories/_toon-proef/gettysburg-begin-en-hoofdstuk1.txt` (de eigenaar vond dat
"perfect"): jij-vorm, vragen aan de luisteraar, de verteller als persoon ("I've always liked that"), spreektaal.
Bij een script dat al de nieuwe opbouw heeft: `tools/toon_bijwerken.py stories/<map> stories/<map>/toon/<naam>.json`
(zoals bij babylon-600-vc, dallas-1963 enz.; zelfde feiten en IMG-regels). Controle:
`python tools/script_leesbaar.py stories/<map>` moet **MAKKELIJK** én **TOON GOED** geven, en de afwisselingscontrole
**AFWISSELING GOED** (opening en titelsoort anders dan de video ervoor in de planning hierboven).

## Klaar
Per script één regel in stories/ROUTINE-LOG.md (zoals PROMPT-SCRIPT-PC.md stap 4). Commit alleen de map van dat script
(geen beelden of audio) en ROUTINE-LOG.md. Lukt een script niet, zet niets half op main en schrijf in ROUTINE-LOG.md wat
er misging, en ga door met het volgende. De pc maakt de video's (stem: eigen stem, speed 0.9, zonder bass, B1.json).
