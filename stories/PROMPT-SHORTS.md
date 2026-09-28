Maak Shorts van mijn sleep documentary "Pompeii: The Last Day". Upload ze naar YouTube en zet ze in mijn Google Drive voor TikTok.

Werk op branch `claude/zen-dirac-ywl398` van wgnghr44bg-coder/vox-lux. Lees eerst:
- `stories/YOUTUBE-STANDAARD.md` (stijl, muziek, instellingen, uploadregels)
- `stories/pompeii/VOLGENDE-STAPPEN.md` (overdracht en YouTube-token)

Wat ik wil:
1. **4 Shorts van 45–60 seconden**, verticaal 1080x1920. Kies zelf de mooiste of spannendste
   stukjes uit het verhaal (bijvoorbeeld de wolk boven de Vesuvius, de nacht van Plinius, de
   herontdekking, de mensen van Pompeii). Een stukje begint aan het begin van een zin en
   eindigt aan het eind van een zin. De eerste zin moet nieuwsgierig maken.
2. **Maak ze uit de bestanden in de repo** (de lange video staat niet in git):
   stem = `audio/pompeii-deel1..5.mp3` met extra pauzes via `tools/add_pauses.py`,
   beelden = `afbeeldingen/NNN.jpg` met de tijden uit `afbeeldingen-tijden-pauzes.tsv`,
   tekst en tijden per zin = `tijdlijn-pauzes.tsv`.
   - Beeld: de 16:9-afbeelding vult het hele scherm en schuift langzaam van links naar
     rechts (of andersom). Zachte overgangen en de drijvende mist, net als de lange video.
   - **Grote ondertitels** per zin, wit met donkere rand, in het midden onderaan.
     Zet ze in beeld met Pillow; de ffmpeg-build heeft geen drawtext.
   - **Achtergrondmuziek** met `tools/ambient_432.py`, precies zoals in de standaard
     (zacht, 432 Hz, geen piano, niets scherps), op -17 dB onder de stem.
   - Laatste 3 seconden: een rustige tekst "Full sleep documentary on the channel".
   - Schrijf hiervoor `tools/make_short.py` en zet het werk ook in de standaard.
3. **Stuur eerst 1 proef-Short** in de chat (< 30 MB) en wacht op mijn akkoord.
   Pas daarna de andere 3 maken.
4. **YouTube**: upload elke Short met `tools/youtube_upload.py`: privé, categorie Education,
   niet voor kinderen, AI gemarkeerd. Titel: een korte, rustige zin over het stukje +
   ` | Pompeii #Shorts` (max. 100 tekens). Beschrijving: 1–2 zinnen, een link naar de
   volledige video (die link geef ik je), de AI-regel en `#shorts #sleepdocumentary #pompeii #history`.
   Tags zoals in de standaard. Geen aparte thumbnail nodig.
5. **Google Drive voor TikTok**: zet de 4 video's in een map "TikTok – Pompeii" in mijn
   Google Drive, met een tekstbestand met per video een TikTok-bijschrift (kort, rustig,
   3–5 hashtags zoals #sleepstory #pompeii #history #432hz). Ik post ze zelf op TikTok.
   Lukt uploaden naar Drive niet (bestand te groot voor de koppeling), stuur de video's
   dan hier in de chat zodat ik ze op mijn telefoon kan bewaren.
6. Sla alles op en push naar de branch (de video's zelf niet in git, die zijn te groot).

Afspraken:
- Praat Nederlands met mij, eenvoudig. Ik werk op telefoon en laptop.
- Alles hierboven is gratis. Vraag altijd eerst als iets geld kost (xAI, ElevenLabs).
- Noem tijden in Nederlandse tijd.
- Nooit muziek van CapCut, TikTok of anderen gebruiken.
- De YouTube-token verloopt 7 dagen nadat hij is aangemaakt. Test eerst alleen het
  verversen. Werkt het niet, leg dan uit hoe ik een nieuwe token maak.
- Als alles klaar is: geef de YouTube-links en zeg wat ik nog moet doen
  (op Openbaar zetten, TikTok posten).
