Onderwerp: Pompeii: The Last Day
Map: stories/pompeii
Link volledige video: https://youtu.be/vgRDl6UwYlo

(Voor een andere video: verander alleen de drie regels hierboven.)

Maak 4 Shorts als keuze van mijn sleep documentary met het onderwerp hierboven. Alleen de Shorts die ik goedkeur gaan naar YouTube; ik download ze uit de chat voor TikTok.

Alles staat op de hoofdbranch `main` van wgnghr44bg-coder/vox-lux. Lees eerst:
- `stories/YOUTUBE-STANDAARD.md` (stijl, muziek, instellingen, uploadregels)
- `stories/pompeii/VOLGENDE-STAPPEN.md` (overdracht en YouTube-token) en, als die er is,
  de `VOLGENDE-STAPPEN.md` in de map hierboven

Wat ik wil:
1. **4 Shorts van 45–60 seconden** als keuze, verticaal 1080x1920. Kies zelf de 4 mooiste of
   spannendste stukjes uit het verhaal, zo verschillend mogelijk (bij Pompeii bijvoorbeeld de wolk boven de Vesuvius, de nacht van
   Plinius, de herontdekking, de mensen van Pompeii). Elk stukje begint aan het begin van een zin en
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
3. **Stuur alle 4 in de chat** (elk < 30 MB), genummerd 1–4, met per Short één zin waar hij
   over gaat. Wacht dan op mijn keuze: ik zeg welke nummers goed zijn (bv. "1 en 3").
   Wil ik iets anders aan een Short, pas die dan aan en stuur hem opnieuw.
4. **YouTube**: upload alleen de goedgekeurde Shorts, elk apart, met `tools/youtube_upload.py`: privé, categorie Education,
   niet voor kinderen, AI gemarkeerd. Titel: een korte, rustige zin over het stukje +
   ` | <korte naam van het onderwerp> #Shorts` (max. 100 tekens). Beschrijving: 1–2 zinnen, een link naar de
   volledige video (link hierboven), de AI-regel en `#shorts #sleepdocumentary #<onderwerp> #history`.
   Tags zoals in de standaard. Geen aparte thumbnail nodig.
5. **TikTok**: de goedgekeurde Shorts download ik uit de chat.
   Geef per goedgekeurde Short een TikTok-bijschrift (kort, rustig, 3–5 hashtags zoals
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
