Onderwerp: Pompeii: The Last Day
Map: stories/pompeii
Link volledige video: https://youtu.be/vgRDl6UwYlo

(Voor een andere video: verander alleen de drie regels hierboven.)

Maak 1 Short van mijn sleep documentary met het onderwerp hierboven. Upload hem naar YouTube en stuur hem in de chat, zodat ik hem voor TikTok kan downloaden.

Alles staat op de hoofdbranch `main` van wgnghr44bg-coder/vox-lux. Lees eerst:
- `stories/YOUTUBE-STANDAARD.md` (stijl, muziek, instellingen, uploadregels)
- `stories/pompeii/VOLGENDE-STAPPEN.md` (overdracht en YouTube-token) en, als die er is,
  de `VOLGENDE-STAPPEN.md` in de map hierboven

Wat ik wil:
1. **1 Short van 45–60 seconden**, verticaal 1080x1920. Kies zelf het mooiste of spannendste
   stukje uit het verhaal (bij Pompeii bijvoorbeeld de wolk boven de Vesuvius, de nacht van
   Plinius, de herontdekking, de mensen van Pompeii). Het stukje begint aan het begin van een zin en
   eindigt aan het eind van een zin. De eerste zin moet nieuwsgierig maken.
2. **Maak ze uit de bestanden in de map** (de lange video staat niet in git):
   stem = `audio/*-deel*.mp3` met extra pauzes via `tools/add_pauses.py`,
   beelden = `afbeeldingen/NNN.jpg` met de tijden uit `afbeeldingen-tijden-pauzes.tsv`,
   tekst en tijden per zin = `tijdlijn-pauzes.tsv`.
   - Beeld: de 16:9-afbeelding vult het hele scherm en schuift langzaam van links naar
     rechts (of andersom). Zachte overgangen en de drijvende mist, net als de lange video.
   - **Grote ondertitels** per zin, wit met donkere rand, in het midden onderaan.
     Zet ze in beeld met Pillow; de ffmpeg-build heeft geen drawtext.
   - **Achtergrondmuziek** met `tools/ambient_432.py`, precies zoals in de standaard
     (zacht, 432 Hz, geen piano, niets scherps), op -17 dB onder de stem.
   - Laatste 3 seconden: een rustige tekst "Full sleep documentary on the channel".
   - Staat `tools/make_short.py` er al (van een vorige keer), gebruik die dan. Anders:
     schrijf hem zo dat hij voor elke video werkt, en zet de werkwijze in de standaard.
3. **Stuur de Short eerst** in de chat (< 30 MB) en wacht op mijn akkoord. Wil ik iets
   anders, pas hem dan aan of kies een ander stukje.
4. **YouTube**: upload de Short na mijn akkoord met `tools/youtube_upload.py`: privé, categorie Education,
   niet voor kinderen, AI gemarkeerd. Titel: een korte, rustige zin over het stukje +
   ` | <korte naam van het onderwerp> #Shorts` (max. 100 tekens). Beschrijving: 1–2 zinnen, een link naar de
   volledige video (link hierboven), de AI-regel en `#shorts #sleepdocumentary #<onderwerp> #history`.
   Tags zoals in de standaard. Geen aparte thumbnail nodig.
5. **TikTok**: de Short uit stap 3 kan ik uit de chat downloaden.
   Geef er een TikTok-bijschrift bij (kort, rustig, 3–5 hashtags zoals
   #sleepstory #<onderwerp> #history #432hz). Ik post ze zelf op TikTok. Geen Google Drive.
6. Sla alles op en push naar de branch (de video's zelf niet in git, die zijn te groot).

Afspraken:
- Praat Nederlands met mij, eenvoudig. Ik werk op telefoon en laptop.
- Alles hierboven is gratis. Vraag altijd eerst als iets geld kost (xAI, ElevenLabs).
- Noem tijden in Nederlandse tijd.
- Nooit muziek van CapCut, TikTok of anderen gebruiken.
- Test eerst alleen het verversen van de YouTube-token (de Google-app staat op
  "In production", de token blijft geldig). Werkt het niet, leg dan uit hoe ik een nieuwe token maak.
- Als alles klaar is: geef de YouTube-links en zeg wat ik nog moet doen
  (in YouTube Studio een publicatiedatum plannen, TikTok posten).
