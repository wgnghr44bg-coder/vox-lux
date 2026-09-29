Onderwerp: <bv. The Titanic: The Night It Sank>

Maak volledig zelfstandig een nieuwe sleep documentary over het onderwerp hierboven,
volgens stories/YOUTUBE-STANDAARD.md op main. Kijk bij stories/pompeii hoe het de
vorige keer is gedaan (script, tijdlijn, afbeeldingen-prompts, VOLGENDE-STAPPEN.md).
Vraag mij tussendoor niets: werk alles af, controleer zelf de kwaliteit en plan de
uploads volgens het schema hieronder. Stop alleen en vraag mij iets als:
- de totale kosten (stem + afbeeldingen + thumbnail) boven $3 zouden komen, of
- iets echt niet lukt (bv. de YouTube-token werkt niet).

Budget: maximaal $3 per video. Houd bij wat elke betaalde stap kost en tel het op.
Maak een afbeelding hooguit 1 keer opnieuw; niets anders opnieuw laten genereren.

Planning (werkt ook als er meerdere sessies tegelijk lopen):
A. Doe dit als allereerste, vóór het script:
   - `git fetch origin` en lees ALLE bestanden `stories/*/planning.txt` op origin/main
     én op alle branches origin/claude/* (bv. met `git ls-tree` + `git show`).
   - Het schema: elke 2 dagen een lange video om 21:00 Nederlandse tijd; de dag
     erna 2 Shorts van die video, om 12:00 en 18:00.
   - Kies de eerste vrije datum voor de lange video: minstens 2 dagen na vandaag,
     en precies 2 dagen na de laatste lange video die al in een planning.txt staat
     (staat er nog niets, of ligt die datum in het verleden: over 2 dagen).
   - Schrijf direct `stories/<map>/planning.txt` met de drie tijden, bv.:
       lang   2026-10-03 21:00
       short1 2026-10-04 12:00
       short2 2026-10-04 18:00
     commit en push dit meteen, zodat andere sessies deze datum zien.
B. Upload alles privé én gepland (status.publishAt). Voeg zo nodig een
   --publish-at optie toe aan tools/youtube_upload.py. Reken de Nederlandse tijd
   goed om naar UTC (zomertijd = UTC+2, wintertijd = UTC+1).
C. YouTube staat ongeveer 6 uploads per dag toe (alle sessies samen). Krijg je
   een quota-fout (403 quotaExceeded), probeer het dan na 09:00 Nederlandse tijd
   opnieuw (plan zo nodig een herinnering met send_later). De geplande datums
   blijven gewoon staan.

Stappen:
1. Test of de YouTube-token werkt (niets uploaden). Doe daarna de planning (A).
2. Schrijf een rustig Engels script, zonder gruwelijke details. De uiteindelijke
   video (met de extra pauzes) moet minimaal 2 uur zijn, dus de stem zelf minstens
   1 uur 40 (± 110.000 tekens).
3. Stem: xAI, stem Lux. Controleer daarna dat de video met pauzes minimaal 2 uur wordt.
4. Afbeeldingen: 75 stuks, verdeeld over de hele video (± elke 1,5 min).
   - Elk beeld laat de scène zien die op dat moment verteld wordt: de plek, de
     mensen, het moment of de gebeurtenis uit dat stuk tekst. Zet de
     {img:...}-markeringen in het script waar de scène verandert.
   - Geschikt voor YouTube: geen bloed, geen geweld in beeld, geen lijken of
     gewonden, niets schokkends. Rustige, filmische sfeer, geen tekst.
   - Model grok-imagine-image ($0,02; pas MODEL aan in tools/xai_images.py).
   - Bekijk zelf elk beeld. Maak een beeld (hooguit 1 keer) opnieuw als het tekst
     bevat, vervormd is of niet bij de scène past.
5. Video met extra pauzes, 432 Hz-muziek en mist, zoals de standaard. Controleer
   zelf een paar beelden uit de video en het geluid tot het eind.
6. Thumbnail met tools/make_thumbnail.py in dezelfde stijl.
7. Upload de lange video privé en gepland (datum uit planning.txt) met titel,
   beschrijving, hoofdstukken, tags en thumbnail volgens de standaard.
8. Shorts: maak er 4 volgens stories/PROMPT-SHORTS.md (met de link van stap 7).
   Kies zelf de 2 beste en upload die privé en gepland (short1 en short2 uit
   planning.txt). Stuur alle 4 in de chat (elk < 30 MB) met een TikTok-bijschrift
   per Short, zodat ik ze kan downloaden. Geen Google Drive.
9. Werk planning.txt bij met de YouTube-links. Maak een pull request naar main.
   Heeft die een conflict met main, haal main binnen en los het zelf op.
10. Geef me tot slot een kort overzicht:
    - de YouTube-links met de geplande datums en tijden;
    - wat het totaal gekost heeft (per onderdeel);
    - wat ik nog moet doen: in YouTube Studio controleren of alles "Gepland"
      staat, bij elke Short de lange video instellen als "Gerelateerde video",
      de pull request mergen, en TikTok posten.

Afspraken: praat Nederlands met mij, eenvoudig. Noem tijden in Nederlandse tijd.
Sla alles op en push naar je branch.
