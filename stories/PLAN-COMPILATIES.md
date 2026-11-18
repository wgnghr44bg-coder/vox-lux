# Plan compilaties (stap 2, 18 nov 2026) – AKKOORD eigenaar 18 nov ("hou je gewoon aan de planning")

| | Oudheid | Middeleeuwen |
|---|---|---|
| datum | ma 4 jan 2027 21:00 | ma 11 jan 2027 21:00 |
| onderdelen | IJstijd, Egypte, Babylon, Rome, Bethlehem | Boeren in de winter, Zwarte Dood, Dansplaag, Tower of London |
| klaar op | laatste deel (Bethlehem) 23 dec | laatste deel (Tower) 30 dec |
| duur (geschat) | ± 10 u 45 min | ± 8 u 45 min |
| titel (uren naar beneden) | 10 Hours of Ancient History \| History for Sleep | 8 Hours of Medieval Life \| History for Sleep |
| kosten | EUR 0 | EUR 0 |

Duur: gemeten stem IJstijd 2:04, Egypte 2:12, Babylon 2:05; de rest geschat uit het aantal woorden (± 2:10 per video).
YouTube-grens is 12 uur: beide passen.

## Techniek
1. Eindversies bewaren: tools/vervang_video.py zet sinds 18 nov de `<map>-16mm.mp4` van een onderdeel in
   `C:\Users\rane\vox-lux-compilaties\` in plaats van hem weg te gooien (± 150 GB vrij op C:).
2. Babylon en Egypte zijn al opgeruimd: opnieuw monteren uit de bestaande stem en beelden (montage_engine.sh, geen nieuwe
   stem, geen nieuwe beelden), eind december als de pc vrij is. Tijd: ± een nacht per video.
3. Aan elkaar zetten met ffmpeg zonder opnieuw te coderen (zelfde instellingen uit dezelfde straat), daarna qc + haperingcontrole.
4. Beschrijving: hoofdstukken = begin van elke video (+ de belangrijkste eigen hoofdstukken).
5. Thumbnail: v3-stijl, rustige scène uit de periode, GEEN uren erop (afspraak).
6. Upload privé met publishAt, kanaal controleren, afspeellijst; zoals vervang_video.py.
