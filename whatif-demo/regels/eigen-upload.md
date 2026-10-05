# Video van de eigenaar uploaden


Stuurt de eigenaar een (ondertitelde) video in de chat met de vraag hem te plaatsen:
1. Bekijk hem eerst (een paar beelden + decodeercontrole: `ffmpeg -v error -i <bestand> -f null -`).
2. Upload precies dat bestand, niet opnieuw coderen:
   `python3 tools/youtube_upload.py <bestand> --channel whatif --title "What if …?" --description-file d.txt --tags "…" --privacy public`
   Openbaar, categorie Education (27), Engels, niet voor kinderen, AI-label aan, geen thumbnail.
3. Korte, menselijke beschrijving:
   POV-zin + emoji / één feit / een vraag aan de kijker + 👇 / 3-4 hashtags waarvan #whatif en #shorts.
   Geen regel "Animated with code / AI voice" (eigenaar, okt 2026); wel het AI-vinkje bij upload.
   Titel zonder #shorts. ±10 tags (what if, onderwerp, science, physics, simulation, 3d animation, IfScape3D).
4. Zet de video in de playlist "What If".
5. Werk onderwerpen.md bij (status "geüpload <datum> <link>") en meld de link.

