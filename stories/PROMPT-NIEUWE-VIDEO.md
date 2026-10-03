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
       GEEN Shorts meer (eigenaar, okt 2026): niet maken, niet uploaden, niet op TikTok.
   - Onderwerp: is het hierboven leeg, neem dan het eerste onderwerp uit
     "Nog te maken" in stories/ONDERWERPEN.md (op main) dat nog niet als
     `onderwerp` in een planning.txt staat (main of origin/claude/*). Schrijf het
     onderwerp in planning.txt zonder " (facts)".
   - Kies het eerste vrije moment voor de lange video: een maandag, woensdag of
     zaterdag, minstens 2 dagen na vandaag, die nog niet in een planning.txt staat
     (en na de laatste lange video die er al staat).
   - Schrijf direct `stories/<map>/planning.txt` met de tijd, bv. voor een woensdag-video:
       onderwerp The Fall of Rome
       lang   2026-10-07 21:00
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
2. Schrijf een rustig Engels script, zonder gruwelijke details. **Begin (eigenaar, okt 2026, definitief)**: na de vaste
   welkomst ("Welcome back to Sleep Archives.", via add_pauses --welkom) komt precies
   ÉÉN zin die de luisteraar naar plek en tijd brengt, elke video in andere woorden;
   daarna [long-pause] ÉÉN rustige, nieuwsgierig makende vraag waar de video antwoord op
   geeft (bv. "How did ordinary families live through months of snow and darkness, with
   only a fire, a few animals, and each other?"), [long-pause], dan één korte vraag om te
   abonneren in eigen woorden (bv. "If you enjoy these quiet journeys, you are welcome to
   subscribe. It helps other sleepy listeners find their way here."), [long-pause] en
   meteen het verhaal met een concreet beeld. **Einde**: een korte afronding, nog één keer
   vragen om te abonneren, een zin dat er een volgende video op het scherm staat ("There
   should be another quiet story waiting on the screen now, if you are still awake.") en
   als laatste "Sleep well, and good night." (eigenaar, okt 2026, naar een groot
   slaapkanaal; goedgekeurd voorbeeld: stories/VOORBEELD-SLEEPY-FACTS.txt). Verder niets: geen
   "close your eyes", geen geruststelling ("not frightening"), geen "nothing to remember",
   geen "breathe / listen / settle in / rest", geen ontspanningszinnen. Het verhaal begint
   zo ± 40 seconden na de start. Goedgekeurde voorbeelden (niet letterlijk hergebruiken):
   "Tonight we drift north, a thousand years back, to the snowy fjords of Norway.
   [long-pause] Somewhere in the west of Norway, the snow begins to fall." en
   "We are travelling to the winter of 1959, to the quiet white mountains of the Ural.
   [long-pause] In a small wooden station at the edge of the forest, ten young friends
   are packing their rucksacks." Nooit zinnen overnemen uit eerdere scripts; vergelijk
   de eerste 20 zinnen met stories/pompeii, san-francisco-1906, titanic en de vorige
   video en herschrijf wat (bijna) gelijk is. Ook verder in het script
   geen vaste zinnen die in elke video terugkomen (YouTube kan dat als herhalende inhoud
   zien). De uiteindelijke
   video (met de extra pauzes) moet minimaal 2 uur zijn: met de rustigere stem (0.9) en de
   pauzes is dat ± 90.000 tekens script (Tunguska: 113.000 tekens zou nu ± 2 u 40 worden).
   Houd het op ± 2 uur
   (eigenaar): niet bewust langer maken.
   Vertel rustig. Begin bij het **dagelijks leven** (wonen, eten, werk, het weer), zodat de
   kijker de plek en de mensen leert kennen. Vertel daarna de **gebeurtenis of het mysterie
   zelf** volledig en duidelijk, kalm en zonder gruwelijke details: dit is de kern en krijgt
   minstens een derde van de video. Sluit af met wat er daarna gebeurde en wat er vandaag
   nog van over is. (Richtlijn, geen vaste verdeling: bij een mysterie is het mysterie het
   grootste deel; bij een dagelijks-leven-onderwerp is er vaak geen gebeurtenis.)
   **Sleepy Facts (proef, eigenaar okt 2026)**: staat er achter het onderwerp in
   ONDERWERPEN.md "(facts)", schrijf het script dan niet als één doorlopend verhaal maar
   als ± 70-90 losse feitjes over het onderwerp, elk ± 200-250 woorden (± 1,5 min): een
   korte kopzin die het feitje noemt ("A Viking longhouse had no chimney at all."),
   [pause], dan rustig uitleggen met concrete beelden, en eindigen met een kalme,
   beschouwende zin. Na elk feitje [long-pause]. Zelfde begin en einde als hierboven;
   houd een logische volgorde aan (bv. van herfst naar winter naar voorjaar). Titel:
   "Sleepy Facts About <onderwerp> | History for Sleep" (≤ 70 tekens), thumbnail-hook
   bv. "SLEEPY FACTS". Zet in planning.txt een regel `vorm facts`, zodat de cockpit later
   kan vergelijken hoe feitjes- en verhaalvideo's het doen.
3. Stem: xAI, stem Lux op snelheid 0.9 (standaard in tools/xai_voiceover.py; niet aanpassen). Controleer daarna dat de video met pauzes minimaal 2 uur wordt.
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
   extra pauzes, haardvuur met zachte regen onder de hele video (GEEN 432 Hz-muziek;
   eigenaar, okt 2026; zie stap 3 van de standaard), mist en rustig bewegend beeld; daarna in
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
8. Geen Shorts (eigenaar, okt 2026): sla dit over, ook niet voor TikTok.
8b. Playlists: zet de lange video in de playlists (mag terwijl hij nog gepland/privé staat):
   python3 tools/youtube_playlist.py --soort <soort> <lang-id>
   Soort: ramp, oudheid, middeleeuwen, mysterie, oorlog of verlaten (uitleg bovenin het
   script). Kies de soort die het best past; maak nooit een playlist per onderwerp.
   Noem de playlists in het overzicht van stap 10.
9. Werk planning.txt bij met de YouTube-links en een blok "Kosten" met wat elk
   betaald onderdeel echt gekost heeft (stem, afbeeldingen incl. opnieuw gemaakte,
   thumbnail) en het totaal in dollars; noem ook hoeveel
   tekens de stem had en hoeveel afbeeldingen er gemaakt zijn. Verplaats het onderwerp in
   stories/ONDERWERPEN.md naar "Al gemaakt". Maak een pull request naar main en
   merge die zelf (GitHub-tools). Heeft die een conflict met main, haal main
   binnen, los het op en merge daarna.
10. Geef me tot slot een kort overzicht:
    - de YouTube-links met de geplande datums en tijden;
    - wat het totaal gekost heeft (per onderdeel);
    - wat ik nog moet doen: in YouTube Studio controleren of alles "Gepland"
      staat.

Afspraken: praat Nederlands met mij, eenvoudig. Noem tijden in Nederlandse tijd.
Sla alles op en push naar je branch.
