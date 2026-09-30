# YouTube-standaard voor alle sleep documentaries

Gebruik deze instellingen bij **elke** upload met `tools/youtube_upload.py`,
tenzij de eigenaar iets anders vraagt. Alles wordt privé geüpload; de eigenaar
zet de video zelf op openbaar in YouTube Studio (dat werkt: bij Pompeii werd de
upload niet op privé vergrendeld).

## Video maken (standaard sinds Pompeii)
Kost alleen de stem (xAI) en de afbeeldingen (xAI, ± $0,05 per stuk); de rest is gratis.
1. **Afbeeldingen** — `python3 tools/xai_images.py stories/<verhaal> all`
   (Grok Imagine quality, 16:9, uit `afbeeldingen-prompts.md`). Eerst 3 proefbeelden
   tonen en akkoord vragen, want het kost geld.
2. **Langere pauzes** — `python3 tools/add_pauses.py stories/<verhaal>`
   Na elke zin extra stilte: 0,7 s + 0,1 s per seconde zinslengte (max. 2,2 s),
   bovenop de bestaande pauze. Lange zinnen krijgen zo meer rust. Maakt
   `video/stem-met-pauzes.wav`, `tijdlijn-pauzes.tsv` en `afbeeldingen-tijden-pauzes.tsv`.
   De video wordt ± 22 % langer (Pompeii: 1:47 → 2:11).
3. **Achtergrondmuziek** — `python3 tools/ambient_432.py stories/<verhaal>/video/muziek432.wav --duur <lengte in s + 2>`
   Zelfgemaakt, 432 Hz-stemming, rechtenvrij. Zachte, ronde tonen (zuivere
   sinussen, niets boven ± 700 Hz, trage inzet), traag wisselende akkoorden,
   een zachte brom die in ± 50 s langzaam op en neer gaat, en af en toe een rustige
   melodie. **Geen piano, geen scherpe geluiden.** Boven ± 1 u 45 loopt het geheugen
   vol: maak dan twee helften (`--seed 7` en `--seed 8`) en zet ze met een crossfade
   van 14 s aan elkaar (zie `stories/titanic/VOLGENDE-STAPPEN.md`). Nooit muziek uit CapCut,
   TikTok of andere nummers gebruiken (auteursrecht).
4. **Video**
   ```
   python3 tools/make_video.py stories/<verhaal> --tijden afbeeldingen-tijden-pauzes.tsv \
       --audio stories/<verhaal>/video/stem-met-pauzes.wav \
       --muziek stories/<verhaal>/video/muziek432.wav --muziek-db -17
   ```
   1080p25, zachte overgangen (1,5 s), drijvende mist. Het beeld beweegt steeds rustig:
   elke 18 s een nieuwe beweging (inzoomen, opzij schuiven, uitzoomen, andere kant op),
   zodat het ook bij afbeeldingen van 1,5 minuut nooit stilstaat (eigenaar: "mag iets meer
   bewegen"). De clips worden in 4K/RGB gemaakt (vloeiend) en 4 tegelijk.
   Muziek op -17 dB: duidelijk zachter dan de stem, vooral hoorbaar in de stiltes.
   Duurt ± 1× de videolengte (4 cores). Test eerst met `--tot 100`.
   Bij meer dan 20 afbeeldingen zet het script eerst groepjes van 20 clips aan elkaar
   (anders te weinig geheugen: 75 clips in één keer ging mis bij San Francisco 1906).
5. **Motion graphics + zachte effecten** — `tools/motion.py` (gratis, geen xAI), in één ronde
   over de video uit stap 4. Upload daarna het `-motion`-bestand.
   ```
   python3 tools/motion.py stories/<verhaal>/video/<naam>.mp4 stories/<verhaal>/video/<naam>-motion.mp4 \
       --plan stories/<verhaal>/motion.json --effecten stories/<verhaal>/effecten.tsv
   ```
   Duurt ± 0,65× de videolengte (± 80 min bij 2 uur). Voorbeeld: `stories/pompeii/motion.json`;
   alle velden staan bovenin `tools/motion.py`. Tijden in seconden **mét** de extra pauzes
   (uit `tijdlijn-pauzes.tsv`, dezelfde als de hoofdstukken in de beschrijving).
   **motion.json** — altijd:
   - `"intro": true` (eerste 9 s: sterren, maan, SLEEP ARCHIVES + onderwerp) en
     `"slot": true` (laatste 14 s: Goodnight · Sleep well · Subscribe), `"onderwerp"` = titel zonder
     " | Sleep Documentary".
   - **Hoofdstuktitel** bij elk hoofdstuk uit de beschrijving: `tijd` = begin hoofdstuk + 3 s
     (het eerste hoofdstuk op 10 s, na de intro), `nummer` 1, 2, 3…, titel in Title Case.
   - **Datumkaartjes** (3–5): op belangrijke momenten, ± 20 s na het begin van dat stuk:
     `regel1` = datum/tijd (bv. "14 April 1912  ·  23:40"), `regel2` = plaats. Alleen
     feiten die in het script staan.
   - **Oude kaart** (1, als het onderwerp over plekken of een reis gaat): `gebied`
     (lon/lat, niet te groot: de plaatsen moeten leesbaar zijn), 4–8 `plaatsen` met juiste
     coördinaten (`berg`/`rook` voor een vulkaan), en een `route` als er een reis is.
     Kustlijnen komen vanzelf (Natural Earth, wordt 1× gedownload).
   - **Citaat** (0–2): alleen een **echt, bekend** citaat uit een historische bron (brief,
     dagboek, krant, oude vertaling), woordelijk en met `bron`. Twijfel je, laat het weg;
     nooit zelf een citaat verzinnen.
   - **Tijdlijn** (1, meestal in het laatste deel): 3–4 punten, `[jaartal, korte tekst]`.
   - Nooit twee onderdelen tegelijk (het script waarschuwt bij overlap); ± 7 s hoofdstuk,
     8 s datum, 16 s kaart, ± 10 s citaat, 9 s tijdlijn.
   - Controleer elk onderdeel met een proefbeeld (seconden, bv. midden in de kaart):
     `python3 tools/motion.py <video>.mp4 proef.jpg --plan ... --proef 3345` en bekijk het.
   **effecten.tsv** — kolommen `van	tot	effect	sterkte	x	y`, tijden in seconden uit
   `afbeeldingen-tijden-pauzes.tsv` (x/y alleen voor kaarslicht/vuur: plek van de vlam,
   0..1 van breedte/hoogte; leeg = standaard). De eigenaar wil ze **allemaal gebruiken
   waar ze passen** (alle soorten die bij het onderwerp horen, verspreid over de video):
   | effect | waar |
   |---|---|
   | `as` | uitbarsting, brand, as, puin |
   | `sneeuw` | winter, kou, bergen |
   | `regen` | regen, storm (rustig), grijze dagen, zee bij slecht weer |
   | `mist` | ochtend, water, moeras, spookachtige/stille plekken, rook in de verte |
   | `vonken` | vuur, fakkels, smidse, lantaarns |
   | `vuur` | kampvuur, haard, brand in beeld (warme gloed van onderen + vonkjes) |
   | `kaarslicht` | kaars, olielamp, lantaarn in een kamer (zet x/y op de vlam) |
   | `lichtstralen` | zon of maan door ramen, bomen, wolken; kerken, zalen (beste op donkere beelden) |
   | `stof` | binnen in zonlicht, oude zalen, bibliotheken, ruïnes |
   | `vuurvliegjes` | zomeravond, tuinen, velden, bos bij schemer |
   | `sterren` | buiten bij nacht, heldere hemel |
   - Eén effect tegelijk, behalve rustige combinaties: `mist` + `sterren`, `mist` + `regen`,
     `stof` + `lichtstralen`, `kaarslicht` + `stof`. Sterkte 0.6–1.0.
   - Samen ± 40–50 % van de video; niet op scènes waar niets past (geen regen in de woestijn).
   - Controleer elk effect met `--proef` op een tijd midden in het stuk; te druk → lagere sterkte,
     niet te zien → 1.0 of een ander beeld.
   **Shorts** krijgen géén intro of outro (eigenaar), wél na `make_short.py` één ronde
   `motion.py` met een **datumkaartje** bovenin (eerste 9 s: datum/tijd + plaats van dat
   stukje) en de **passende effecten** (zelfde tabel; kies wat bij de beelden van de Short
   past, bv. sterren + mist bij nacht op zee, stof bij een ochtend na een aardbeving):
   ```
   echo '{"items": [{"soort": "datum", "tijd": 0.8, "duur": 9, "regel1": "14 April 1912  ·  Night", "regel2": "North Atlantic"}]}' > video/shorts/<naam>-motion.json
   printf 'van\ttot\teffect\tsterkte\n0\t70\tsterren\t1.0\n0\t70\tmist\t0.6\n' > video/shorts/<naam>-effecten.tsv
   python3 tools/motion.py video/shorts/<naam>.mp4 video/shorts/<naam>-fx.mp4 \
       --plan video/shorts/<naam>-motion.json --effecten video/shorts/<naam>-effecten.tsv
   ```
   Upload en plaats op de TikTok-pagina het `-fx`-bestand. ± 4 min per Short.

## Titel
Altijd **precies het onderwerp dat de eigenaar stuurt**, met ` | Sleep Documentary`
erachter. Niets aan het onderwerp veranderen of zelf verzinnen. Staat
"Sleep Documentary" er al in, dan niet dubbel toevoegen. (Max. 100 tekens.)
Voorbeeld: onderwerp `Pompeii: The Last Day` → `Pompeii: The Last Day | Sleep Documentary`

## Beschrijving (Engels, rustige toon)
```
Drift off to the story of <onderwerp in één zin: wat, waar, wanneer>.
<2 zinnen over wat de kijker meemaakt in het verhaal.>

A calm, slow-paced history documentary for sleep and relaxation. No loud
sounds, no jump scares, just a gentle voice, soft 432 Hz background music
and softly changing images.

Chapters
0:00:00 <eerste hoofdstuk>
<tijd> <hoofdstuk>   ← uit tijdlijn-pauzes.tsv (de tijden mét extra pauzes!), 10–15 stuks

Narration and images were created with the help of AI. The story is based on
historical sources<, noem de belangrijkste bron>.

#sleepdocumentary #<onderwerp> #history
```
- Eerste hoofdstuk altijd op 0:00:00, minstens 3 hoofdstukken, elk ≥ 10 s.

## Tags
Altijd: `sleep documentary, history for sleep, bedtime story, relaxing history,
sleep story, 432hz` + 4–6 onderwerp-tags.

## Instellingen
- Categorie: Education (`--category 27`)
- Niet voor kinderen (`selfDeclaredMadeForKids: false`)
- AI-inhoud gemarkeerd (`containsSyntheticMedia: true`, standaard in het script)
- Privé
- Thumbnail: **altijd in hetzelfde ontwerp**, zodat kijkers de serie herkennen.
  Maak hem met `tools/make_thumbnail.py` (niet zelf een ander ontwerp maken):
  ```
  python3 tools/make_thumbnail.py <beeld.jpg> thumbnail.jpg --title "<onderwerp>"
  ```
  - Ontwerp (zoals populaire slaapgeschiedenis-kanalen, met eigen tekst):
    helder, kleurrijk beeld; bovenaan groot "SLEEP DOCUMENTARY"; linksonder een
    kleine regel (het deel na de ":" in het onderwerp) en daaronder het
    onderwerp enorm groot. Alle tekst extra dik, wit, met donkere rand en gloed;
    het onderwerp krijgt een lichte maanlichtgloed.
  - Achtergrond: aparte thumbnail-afbeelding via xAI (`grok-imagine-image`,
    $0,02): filmisch, verzadigde kleuren, een duidelijk onderwerp (plek,
    gebouw, landschap of mensen op afstand), contrast tussen warm lamplicht en
    een koele blauwe nacht, donkerder bovenaan en linksonder voor de tekst,
    16:9, geen tekst. Anders een kleurrijk beeld uit de video.
  - `--title`: het onderwerp zoals de eigenaar het stuurt (zonder
    "| Sleep Documentary"), bv. `Pompeii: The Last Day`.
  - Beeld: een sprekend beeld uit de video met een rustig midden. Afspraken van
    de eigenaar over wélk beeld gaan voor.
  - Uploaden kan alleen als het kanaal geverifieerd is (youtube.com/verify).

## Na de upload
Meld de eigenaar de link(s) en wat nog in YouTube Studio moet (altijd deze lijst):
1. Nalopen: titel, beschrijving, thumbnail, AI-melding ("Altered content": Yes).
2. Publicatie plannen: Zichtbaarheid → Planning (datum en tijd kiezen).
3. **Bij elke Short de lange video koppelen**: Content → Shorts → Short openen →
   **Gerelateerde video** → de lange video kiezen → Opslaan. Dit kan niet via de
   API, alleen in Studio (kanaal is daarvoor geverifieerd).
4. TikTok: de goedgekeurde Shorts uit de chat downloaden en posten met het bijschrift.
De refresh token blijft geldig (app "In production"); test hem wel eerst.

## Shorts (sinds Pompeii)
Uit een bestaande sleep documentary, alles gratis behalve het gesproken begin (xAI, < 1 cent).
1. Kies stukjes van 45–60 s (begin en eind op een zinsgrens) en zet ze in
   `stories/<verhaal>/shorts.tsv` (kolommen `naam`, `van`, `tot` = zinsnummers uit
   `tijdlijn-pauzes.tsv`). Eerst `tools/add_pauses.py` draaien als `video/stem-met-pauzes.wav` ontbreekt.
2. **Gesproken begin**, altijd in drie stukjes met `[pause]` ertussen (eigenaar):
   `Did you know? [pause] <waar het over gaat + jaar>. [pause] <het weetje>.`
   Voorbeeld: "Did you know? [pause] The Titanic sank in April 1912. [pause] The two lookouts
   high in the mast had no binoculars." Of: "Did you know? [pause] Vesuvius buried Pompeii in
   79 AD. [pause] A famous Roman admiral simply went to sleep." Het middelste stuk zegt kort
   de gebeurtenis/plek en het jaar, zodat een kijker die niets weet het meteen snapt; het
   weetje wordt in het stukje verteld. Simpel Engels, samen ± 25 woorden.
   Tekst in `shorts-intro/<naam>.txt`, inspreken (kost < 1 cent; de routine mag dit binnen
   haar budget, een losse sessie vraagt eerst akkoord):
   `python3 tools/xai_voiceover.py stories/<verhaal>/shorts-intro/<naam>.txt --proxy-auth -o stories/<verhaal>/shorts-intro/<naam>.mp3`
   Tekst en mp3 in git houden (klein), dan hoeft het nooit opnieuw betaald te worden.
3. `python3 tools/make_short.py stories/<verhaal> --lijst shorts.tsv [--alleen <naam>]`
   → `video/shorts/<naam>.mp4` (1080x1920, schuivend beeld, mist, grote ondertitels in korte
   stukjes (tot 9 woorden) die woord voor woord op de stem zijn gelegd (pocketsphinx, gratis,
   wordt vanzelf geïnstalleerd; het script meldt "ondertitels: X van Y zinnen woord voor
   woord gelijk" — lukt een zin niet, dan schat het op de stiltes),
   432 Hz-muziek op -17 dB). Geen eindtekst (de eigenaar wil het simpel; `--eindtekst` zet
   "Full sleep documentary on the channel" er toch in). ± 3 min per Short.
4. Eerst 1 proef in de chat (< 30 MB), pas na akkoord de rest.
5. YouTube: privé, Education, niet voor kinderen, AI gemarkeerd. Titel: korte rustige zin +
   ` | <korte naam>` (NIET "#Shorts" in de titel; #shorts alleen in de beschrijving). Beschrijving: 1–2 zinnen, link naar de volledige video, de AI-regel,
   `#shorts #sleepdocumentary #<onderwerp> #history`. Teksten in `shorts-teksten/`.
6. TikTok: zet elke geplande Short met bijschrift op de TikTok-pagina (zie
   "TikTok-overzicht" hieronder). Geen Google Drive.

## TikTok-overzicht (voor de eigenaar)
Alle Shorts die op YouTube gepland staan, komen ook op één vaste pagina:
https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ (Artifact "Sleep Archives TikToks"; database-collectie `tiktoks`).
Zet na de YouTube-upload elke geplande Short erop:
1. Upload het mp4-bestand als asset: Artifact-tool, `url` = de pagina hierboven,
   `asset: true`, `file_path(s)` = de Short(s). Bewaar het teruggegeven id en url.
2. Schrijf per Short één document met ArtifactData (`action: "set"`, `url` = de pagina,
   `collection: "tiktoks"`, `doc_id: "<map>-<shortnaam>"`), met deze velden:
   `onderwerp` (titel van de lange video zonder "| Sleep Documentary"), `titel`
   (YouTube-titel van de Short zonder " | …"), `datum` (publicatie in
   Nederlandse tijd als "JJJJ-MM-DDTUU:MM"), `bijschrift` (TikTok-bijschrift),
   `video_id`, `video_url` (de url uit stap 1, bv. "/_blob/<id>"), `bestand`
   (bv. "<map>-<naam>.mp4"), `youtube` (link van de Short), `geplaatst: false`.
Lukt dit niet, stuur de Shorts dan in de chat zoals voorheen.
