Onderwerp: <leeg laten = volgende uit stories/ONDERWERPEN.md>

Maak volledig zelfstandig een nieuwe sleep documentary over het onderwerp hierboven,
volgens stories/YOUTUBE-STANDAARD.md op main. Kijk bij stories/pompeii hoe het de
vorige keer is gedaan (script, tijdlijn, afbeeldingen-prompts, VOLGENDE-STAPPEN.md).
Vraag mij tussendoor niets: werk alles af, controleer zelf de kwaliteit en plan de
uploads volgens het schema hieronder. Stop alleen en vraag mij iets als:
- de totale kosten (stem + afbeeldingen + thumbnail) boven $3 zouden komen, of
- iets echt niet lukt (bv. de YouTube-token werkt niet).
- xAI geeft een fout over tegoed/betaling (bv. 402, "insufficient credits",
  "billing"): stop dan meteen en begin je laatste bericht met
  "⚠️ ZET GELD OP xAI" en daaronder: ga naar console.x.ai → Billing → Add credits.
  Geef je plek vrij: verwijder je stories/<map>/planning.txt, commit en push
  (en merge dat naar main), zodat de volgende sessie hetzelfde onderwerp en
  dezelfde datum weer kan pakken. Er is dan nog niets geüpload.

Budget: maximaal $3 per video. Houd bij wat elke betaalde stap kost en tel het op.
Maak een afbeelding hooguit 1 keer opnieuw; niets anders opnieuw laten genereren.

Planning (werkt ook als er meerdere sessies tegelijk lopen):
A. Doe dit als allereerste, vóór het script:
   - `git fetch origin` en lees ALLE bestanden `stories/*/planning.txt` op origin/main
     én op alle branches origin/claude/* (bv. met `git ls-tree` + `git show`).
   - Het schema (vaste dagen, ook in het weekend):
       lange video: maandag, woensdag en zaterdag om 21:00 Nederlandse tijd;
       Shorts (TikTok): elke dag 2, om 10:00 en 20:00, van de laatste lange video:
       ma-video -> di + wo (4 Shorts), wo-video -> do + vr + za (6 Shorts),
       za-video -> zo + ma (4 Shorts). De eigenaar post ze zelf op TikTok.
       YouTube-Short: alleen de sterkste (short1), de dag na de lange video om 20:00
       (regel `yt-short`). De rest gaat NIET naar YouTube (eigenaar, okt 2026: de
       groei komt van lange video's; Shorts-kijkers kijken zelden lang).
   - Onderwerp: is het hierboven leeg, neem dan het eerste onderwerp uit
     "Nog te maken" in stories/ONDERWERPEN.md (op main) dat nog niet als
     `onderwerp` in een planning.txt staat (main of origin/claude/*).
   - Kies het eerste vrije moment voor de lange video: een maandag, woensdag of
     zaterdag, minstens 2 dagen na vandaag, die nog niet in een planning.txt staat
     (en na de laatste lange video die er al staat).
   - Schrijf direct `stories/<map>/planning.txt` met alle tijden, bv. voor een
     woensdag-video:
       onderwerp The Fall of Rome
       lang   2026-10-07 21:00
       yt-short 2026-10-08 20:00
       short1 2026-10-08 10:00
       short2 2026-10-08 20:00
       short3 2026-10-09 10:00
       short4 2026-10-09 20:00
       short5 2026-10-10 10:00
       short6 2026-10-10 20:00
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
   1 uur 40 (± 110.000 tekens). Houd het op ± 2 uur
   (eigenaar): niet bewust langer maken.
   Vertel rustig. Begin bij het **dagelijks leven** (wonen, eten, werk, het weer), zodat de
   kijker de plek en de mensen leert kennen. Vertel daarna de **gebeurtenis of het mysterie
   zelf** volledig en duidelijk, kalm en zonder gruwelijke details: dit is de kern en krijgt
   minstens een derde van de video. Sluit af met wat er daarna gebeurde en wat er vandaag
   nog van over is. (Richtlijn, geen vaste verdeling: bij een mysterie is het mysterie het
   grootste deel; bij een dagelijks-leven-onderwerp is er vaak geen gebeurtenis.)
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
5. Video met de vaste welkomst ("Welcome back to Sleep Archives.", add_pauses.py --welkom),
   extra pauzes, 432 Hz-muziek, mist en rustig bewegend beeld; daarna in
   één ronde de motion graphics (intro, hoofdstuktitels, datumkaartjes, oude kaart,
   citaat, tijdlijn, afsluiting) en de zachte effecten op alle passende scènes (as,
   sneeuw, regen, mist, vonken, vuur, kaarslicht, lichtstralen, stof, vuurvliegjes,
   sterren) met tools/motion.py, precies zoals stap 4 en 5 van de standaard.
   Controleer zelf proefbeelden van elk onderdeel (--proef), een paar beelden uit de
   eindvideo en het geluid tot het eind. Upload het -motion-bestand.
6. Thumbnail met tools/make_thumbnail.py in het v2-ontwerp (NOOIT `--stijl v1`): hook van
   2-4 woorden, warm beeld met mensen rechts/midden; zie "Thumbnail" in de standaard.
   Altijd **rustig**: het moment vóór de gebeurtenis, de ramp hooguit als klein lichtje of
   rook in de verte; geen ontploffingen, angstige gezichten of woorden als "Exploded".
   Past geen beeld uit de video, maak er één met xAI ($0,02). Sla hem op als
   `stories/<map>/thumbnail-v2.jpg` en bekijk hem zelf naast
   `stories/pompeii/thumbnail-v2.jpg`, `stories/titanic/thumbnail-v2.jpg` en
   `stories/tunguska/thumbnail-v2.jpg`: zelfde stijl en sfeer? Zo niet, opnieuw.
7. Upload de lange video privé en gepland (datum uit planning.txt) met titel,
   beschrijving, hoofdstukken, tags en thumbnail volgens de standaard. Controle vóór
   de upload: titel = belevingstitel + " | History for Sleep" (nooit "| Sleep
   Documentary", nooit een kale onderwerpnaam; is het onderwerp uit ONDERWERPEN.md toch
   kaal, maak er dan zelf een rustige belevingstitel van), ≤ 70 tekens.
8. Shorts: maak er zoveel als er Short-plekken in planning.txt staan (4, of 6 bij
   een woensdag-video) volgens "Shorts" in stories/YOUTUBE-STANDAARD.md (met de link
   van stap 7): meteen een spannend begin zonder pauzes, 35-45 s, synchrone
   ondertitels, een datumkaartje bovenin en passende effecten via motion.py, zonder
   intro of outro. Zet ze ALLEMAAL met hun TikTok-bijschrift en TikTok-datum (short1..N)
   op de TikTok-pagina (zie "TikTok-overzicht" in de standaard). Geen Google Drive.
   Upload alleen short1 (de sterkste) naar YouTube: privé, gepland op `yt-short`.
8b. Playlists: zet de lange video en alle Shorts in de playlists (mag terwijl ze nog
   gepland/privé staan):
   python3 tools/youtube_playlist.py --soort <soort> <lang-id> <yt-short-id>
   Soort: ramp, oudheid, middeleeuwen, mysterie, oorlog of verlaten (uitleg bovenin het
   script). Kies de soort die het best past; maak nooit een playlist per onderwerp.
   Noem de playlists in het overzicht van stap 10.
9. Werk planning.txt bij met de YouTube-links en een blok "Kosten" met wat elk
   betaald onderdeel echt gekost heeft (stem, afbeeldingen incl. opnieuw gemaakte,
   thumbnail, gesproken begin van de Shorts) en het totaal in dollars; noem ook hoeveel
   tekens de stem had en hoeveel afbeeldingen er gemaakt zijn. Verplaats het onderwerp in
   stories/ONDERWERPEN.md naar "Al gemaakt". Maak een pull request naar main en
   merge die zelf (GitHub-tools). Heeft die een conflict met main, haal main
   binnen, los het op en merge daarna.
10. Geef me tot slot een kort overzicht:
    - de YouTube-links met de geplande datums en tijden;
    - wat het totaal gekost heeft (per onderdeel);
    - wat ik nog moet doen: in YouTube Studio controleren of alles "Gepland"
      staat, bij de YouTube-Short de lange video instellen als "Gerelateerde video",
      en de TikToks plaatsen vanaf de TikTok-pagina.

Afspraken: praat Nederlands met mij, eenvoudig. Noem tijden in Nederlandse tijd.
Sla alles op en push naar je branch.
