# QC vóór upload/doorgeven – IfScape3D (eigenaar, 7 okt 2026, verplicht)

Net als bij Sleep Archives (stories/QC-CHECKLIST.md): eerst controleren, dan pas uploaden (lang) of doorgeven (Short).
Alleen bij "✅ VIDEO APPROVED — READY FOR UPLOAD" verder. Faalt iets: oorzaak oplossen, opnieuw renderen, opnieuw QC.
Lukt het na 1 reparatie niet: NIET uploaden, wel melden wat er mis is.

1. Techniek – `tools/check_video.py` per hoofdstuk/Short (`--stem voice.mp3 --bron mix.wav`) én op de samengevoegde lange
   video (decodeerfouten, haperende stem, stilstaand beeld > 8 s, lengte beeld = geluid): moet "CONTROLE GOED" geven.
2. Beeld – zelf kijken:
   - overzichtsplaat met 1 beeld per 2 s per hoofdstuk (ffmpeg `fps=1/2,scale=320:-1,tile=6x5`): geen zwarte/lege
     beelden, geen objecten door elkaar, camera niet in muren/grond, logo-moment goed;
   - bij elke shotwissel ± 0,5 s ervoor en erna beeld voor beeld (ffmpeg `-ss … -frames:v 15`): geen flikkeren, verspringen,
     motion blur over de wissel of haperen (dit was de straat-glitch van 7 okt).
3. Geluid – stem is Atlas (1.05) met pauzes; stem verstaanbaar boven de muziek; geen klik of gat bij hoofdstukovergangen.
4. Inhoud – wat de stem zegt is ook te zien; getallen op de teller kloppen met de stem; lange video ≥ 8:00 en begint met
   "Imagine" + titel; geen ondertitels ingebrand.
5. Upload-tekst en thumbnail – titel/beschrijving/tags uit upload.json, thumbnail volgens regels/thumbnail.md (zelf openen).
6. Voorproefje – stuur na QC 1 minuut uit de lange video (vanaf ± 1:00, < 15 MB) met SendUserFile (display "render"),
   zodat de eigenaar hem in de sessie kan bekijken; vermeld in de melding dat het voorproefje in de sessie staat.

Schrijf het resultaat per punt (✅/❌) kort in de melding.
