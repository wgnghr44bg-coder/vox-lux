# Controlelijst vóór elke upload (eigenaar, okt 2026)

"Geen haper, stotter of kraak — alles vloeiend." Alleen als ALLES klopt wordt een video
geüpload; anders niet uploaden en de eigenaar een ⚠️-melding met de reden sturen.
Automatisch: `python3 tools/check_video.py stories/<map> video/<naam>-motion.mp4` → "CONTROLE GOED".

## Geluid
1. **Stem blijft niet hangen** — geen pauze midden in een woord; hooguit 2 losse korte
   geluidjes in de hele video (`check_video.py`, en `add_pauses.py` zet pauzes altijd in echte stiltes).
2. **Pauzes alleen op de goede plek** — na elke zin, en kleine pauzes alleen bij echte komma's.
3. **Geen kraak** — geen decodeerfouten (`ffmpeg -v error` leeg) en geen vervorming (geluid op het maximum).
4. **Geen stotteren/haperen in de video zelf** — geluid van de video per halve seconde gelijk aan de bron.
5. **Stem in één stuk gemaakt** — nooit in stukken op bytegrootte knippen.

## Beeld
6. **Beeld loopt niet vast** — nergens langer dan 8 s stilstaand.
7. **Titels niet over elkaar** — intro, hoofdstukken, datumkaartjes en kaarten nooit tegelijk (motion.py schuift zelf op).
8. **Lengte** — beeld en geluid precies even lang.

## Inhoud
9. **Begin** — "Tonight we are going … years back, to …" en meteen het verhaal (geen welkom, vraag of abonneren).
10. **Einde** — korte afronding, vraag om te abonneren, verwijzing naar de volgende video, "Sleep well, and good night."
11. **Stem en muziek** — Lux (snelheid 0.9, net iets zwaarder via add_pauses), 432 Hz op -20 dB, geen andere geluiden.
12. **Titel, thumbnail, beschrijving** — titel eindigt op "| History for Sleep", rustige v2-thumbnail, hoofdstuktijden kloppen.

Nooit een video opnieuw uploaden die al eens openbaar is geweest.
