# YouTube-standaard voor alle sleep documentaries

Gebruik deze instellingen bij **elke** upload met `tools/youtube_upload.py`,
tenzij de eigenaar iets anders vraagt. Alles wordt privé geüpload; de eigenaar
zet de video zelf op openbaar in YouTube Studio (dat werkt: bij Pompeii werd de
upload niet op privé vergrendeld).

**Nooit een video opnieuw uploaden die al eens openbaar is geweest** (eigenaar, okt 2026:
Pompeii is 3 keer geüpload en kreeg na de eerste keer bijna geen vertoningen meer; YouTube
ziet een kopie als herhaalde inhoud en laat hem nauwelijks zien). Wil je iets verbeteren,
pas dan bij de bestaande video de titel, thumbnail of beschrijving aan.

## Video maken (standaard sinds Pompeii)
Kost alleen de stem (xAI) en de afbeeldingen (xAI, ± $0,05 per stuk); de rest is gratis.
1. **Afbeeldingen** — `python3 tools/xai_images.py stories/<verhaal> all`
   (Grok Imagine quality, 16:9, uit `afbeeldingen-prompts.md`). Eerst 3 proefbeelden
   tonen en akkoord vragen, want het kost geld.
2. **Langere pauzes** — `python3 tools/add_pauses.py stories/<verhaal>` (ZONDER --welkom: sinds
   3 okt 2026 begint het script zelf met "Tonight we are going ... years
   back, to ...", zie stap 2 van PROMPT-NIEUWE-VIDEO.md). Alle tijden schuiven vanzelf mee. (Voor Shorts niet van belang.)
   Na elke zin extra stilte: 0,7 s + 0,1 s per seconde zinslengte (max. 2,2 s),
   bovenop de bestaande pauze. Lange zinnen krijgen zo meer rust. Maakt
   `video/stem-met-pauzes.wav`, `tijdlijn-pauzes.tsv` en `afbeeldingen-tijden-pauzes.tsv`.
   De video wordt ± 22 % langer (Pompeii: 1:47 → 2:11).
3. **Achtergrond: alleen 432 Hz-muziek, zacht** (eigenaar, okt 2026, definitief: geen vuur,
   regen of andere geluiden). `python3 tools/ambient_432.py stories/<verhaal>/video/muziek432.wav --duur <lengte in s + 2>`
   (boven ± 1 u 45: twee helften met `--seed 7` en `--seed 8`, met 14 s crossfade aan elkaar;
   zie `stories/titanic/VOLGENDE-STAPPEN.md`). Op -20 dB onder de stem (standaard in make_video.py; eigenaar 3 okt).
   **Stem** (eigenaar, okt 2026, na veel proefjes): xAI-stem **Lux**, snelheid 0.9 (10% langzamer);
   `add_pauses.py` maakt hem daarna net iets zwaarder en warmer, zet na elke zin een pauze
   en bij elke komma/adempauze een kleine extra pauze (0,25 s). Dit zijn de standaardwaarden
   van de tools.
4. **Video**
   ```
   python3 tools/make_video.py stories/<verhaal> --tijden afbeeldingen-tijden-pauzes.tsv \
       --audio stories/<verhaal>/video/stem-met-pauzes.wav \
       --muziek stories/<verhaal>/video/muziek432.wav
   ```
   1080p25, zachte overgangen (1,5 s), drijvende mist. Het beeld beweegt steeds rustig:
   elke 18 s een nieuwe beweging (inzoomen, opzij schuiven, uitzoomen, andere kant op),
   zodat het ook bij afbeeldingen van 1,5 minuut nooit stilstaat (eigenaar: "mag iets meer
   bewegen"). De clips worden in 4K/RGB gemaakt (vloeiend) en 4 tegelijk.
   Muziek op -20 dB: zacht op de achtergrond.
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
     " | History for Sleep".
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
   (Shorts zijn gestopt, okt 2026.) **Shorts** kregen géén intro of outro (eigenaar), wél na `make_short.py` één ronde
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

## Titel (sinds okt 2026)
Mensen zoeken in deze niche op **"History for Sleep"** en klikken op titels die een
**beleving** beloven (hoe leefden ze, wat deden ze de hele dag, de laatste rustige
nacht), niet op een kale onderwerpnaam. Grote kanalen: "How Medieval Peasants Survived
the Coldest Nights", "What Did Medieval Peasants Do All Day".
- Titel = **het onderwerp uit `ONDERWERPEN.md`** (die staan er al als belevingstitel
  in) + ` | History for Sleep`. Bijvoorbeeld
  `What Life Was Like in Pompeii Before Vesuvius | History for Sleep`.
- Stuurt de eigenaar zelf een onderwerp, gebruik dat precies zoals gestuurd (niets
  aan veranderen) met ` | History for Sleep` erachter.
- Kort houden: liefst ≤ 70 tekens in totaal (op een telefoon wordt de rest afgeknipt).
  Max. 100 tekens.
- "Sleep documentary" staat dan in de beschrijving en de tags, niet meer in de titel.
- Een video die eenmaal openbaar is: titel/thumbnail aanpassen in Studio, **niet**
  verwijderen en opnieuw uploaden (dan begint hij weer bij nul).

## Beschrijving (Engels, rustige toon)
```
Drift off to the story of <onderwerp in één zin: wat, waar, wanneer>.
(Eerste regel = wat je in de zoekresultaten ziet: laat "history for sleep" of
"sleep documentary" er liefst in terugkomen.)
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
Altijd: `history for sleep, boring history for sleep, sleep documentary, bedtime story,
relaxing history, sleep story, 432hz` + 4–6 onderwerp-tags.

## Instellingen
- Categorie: Education (`--category 27`)
- Niet voor kinderen (`selfDeclaredMadeForKids: false`)
- AI-inhoud gemarkeerd (`containsSyntheticMedia: true`, standaard in het script)
- Privé
- Thumbnail: **altijd in hetzelfde ontwerp (v2, sinds okt 2026)**, zodat kijkers de serie
  herkennen. Maak hem met `tools/make_thumbnail.py` (niet zelf een ander ontwerp maken):
  ```
  python3 tools/make_thumbnail.py <beeld.jpg> thumbnail.jpg --hook "<2-4 woorden>" --title "<plaats>  ·  <jaar>"
  ```
  Voorbeelden: `stories/pompeii/thumbnail-v2.jpg` (`--hook "Before the Ash" --title "Pompeii  ·  79 AD"`),
  `stories/titanic/thumbnail-v2.jpg`, `stories/san-francisco-1906/thumbnail-v2.jpg`.
  - Ontwerp: linksboven klein het logo (maantje + SLEEP ARCHIVES); linksonder een kleine
    amberkleurige regel (plaats · jaar) en daaronder de **hook** heel groot, wit, extra dik.
    Geen grote "SLEEP DOCUMENTARY"-balk meer: die ruimte is voor het beeld. De tekst blijft
    in de linker ± helft, want rechtsonder zet YouTube de videolengte (in de Studio-app heel groot).
  - **Altijd rustig** (eigenaar, okt 2026): toon het moment **vóór** de gebeurtenis, warm en
    knus; de ramp of het mysterie hooguit als kleine hint in de verte (een lichtje in de lucht,
    rook ver weg). Nooit ontploffingen, vuurballen groot in beeld, angstige gezichten of
    woorden als "Exploded", "Death", "Horror" in de hook: slaapkijkers zoeken rust.
    Voorbeeld: Tunguska = oma en kleindochter bij de samovar, klein lichtspoor, hook
    "The Last Quiet Morning" (`stories/tunguska/thumbnail-v2.jpg`).
  - **Hook**: 2–4 woorden die een gevoel of beleving geven, niet de hele titel. Bv.
    "Before the Ash", "The Last Quiet Night", "Old San Francisco", "Winter in a Viking Hut".
  - **Beeld**: warm en knus, met **mensen** in beeld (een figuur bij een lamp, vuur of
    kaars), warm oranje licht tegen een koele blauwe/paarse avond. De mensen en hun
    gezichten staan **rechts of in het midden**, links onderin moet rustig zijn voor de
    tekst. Bekijk het resultaat: staat de tekst over een gezicht, kies een ander beeld.
  - Kies eerst een passend beeld uit de video (gratis). Is er geen goed beeld met mensen,
    maak dan één aparte thumbnail-afbeelding via xAI (`grok-imagine-image`, $0,02):
    filmisch, verzadigd, mensen rechts in warm lamplicht, links onderin rustig en
    donkerder, 16:9, geen tekst.
  - Na publicatie: test in Studio met **Test & Compare** twee varianten (andere hook
    of ander beeld); YouTube kiest zelf de winnaar.
  - Oud ontwerp (v1) kan nog met `--stijl v1 --title "<onderwerp>"`, niet meer gebruiken
    voor nieuwe video's.
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

## Shorts (GESTOPT okt 2026 — eigenaar: geen Shorts meer maken; hieronder alleen ter info)
Uit een bestaande sleep documentary, alles gratis behalve het gesproken begin (xAI, < 1 cent).
**Alle Shorts gaan naar TikTok; alleen de sterkste (short1) ook naar YouTube**, de dag na de
lange video om 20:00 (de eigenaar uploadt die zelf vanaf de pagina, sinds okt 2026). Reden (cijfers sept 2026): Shorts gaven veel weergaven maar bijna geen
abonnees, de groei in deze niche komt van lange video's, en zo blijven er uploads over.
Shorts met een rustig "Did you know? [pause] …"-begin werden het snelst weggeswiped (± 37%
bekeken); mysterie-Shorts die meteen spannend beginnen het best (tot 145%).
1. Kies stukjes van 35–45 s (begin en eind op een zinsgrens) en zet ze in
   `stories/<verhaal>/shorts.tsv` (kolommen `naam`, `van`, `tot` = zinsnummers uit
   `tijdlijn-pauzes.tsv`). Eerst `tools/add_pauses.py` draaien als `video/stem-met-pauzes.wav` ontbreekt.
2. **Gesproken begin**: één of twee korte zinnen die **meteen** het spannendste zeggen, zonder
   "Did you know?" en zonder `[pause]` (de eerste 2 seconden beslissen of iemand blijft).
   Noem plek en jaar kort, zodat een kijker die niets weet het snapt. Simpel Engels, ± 15-20
   woorden. Voorbeelden: "Sixty kilometres from the blast, a farmer felt his shirt catch fire.
   Siberia, 1908." / "The two men watching for icebergs had no binoculars. Titanic, 1912."
   Tekst in `shorts-intro/<naam>.txt`, inspreken (kost < 1 cent; de routine mag dit binnen
   haar budget, een losse sessie vraagt eerst akkoord):
   `python3 tools/xai_voiceover.py stories/<verhaal>/shorts-intro/<naam>.txt --proxy-auth -o stories/<verhaal>/shorts-intro/<naam>.mp3`
   Tekst en mp3 in git houden (klein), dan hoeft het nooit opnieuw betaald te worden.
3. `python3 tools/make_short.py stories/<verhaal> --lijst shorts.tsv [--alleen <naam>]`
   → `video/shorts/<naam>.mp4` (1080x1920, 30 beelden/s, schuivend beeld, mist, GEEN
   ondertitels (eigenaar, okt 2026; `--ondertitels` zet ze toch aan), lange slaappauzes
   automatisch ingekort tot 0,4 s,
   432 Hz-muziek op -26 dB, zelfde als de lange video; geen natuurgeluiden). Geen eindtekst (de eigenaar wil het simpel; `--eindtekst` zet
   "Full sleep documentary on the channel" er toch in). ± 3 min per Short.
4. Eerst 1 proef in de chat (< 30 MB), pas na akkoord de rest.
5. YouTube (alleen short1): NIET zelf uploaden — de eigenaar doet dat zelf vanaf de
   pagina (YouTube-kaart, zie "TikTok-overzicht"). Bij het uploaden: Education, niet voor
   kinderen, AI gemarkeerd. Titel:
   spannend en nieuwsgierig makend, met hoofdletters per woord en eventueel één emoji
   (zoals de best lopende Shorts), + ` | <korte naam + jaar>`, bv.
   "His Shirt Caught Fire 60 km From the Blast 🔥 | Tunguska 1908" (NIET "#Shorts" in de titel; #shorts alleen in de beschrijving). Beschrijving: 1–2 zinnen, link naar de volledige video, de AI-regel,
   `#shorts #sleepdocumentary #<onderwerp> #history`. Teksten in `shorts-teksten/`.
6. TikTok-bijschrift: begint net als de Short meteen met het spannendste (geen "Did you
   know?"), max. ± 100 tekens + 4-5 hashtags, bv. "60 km from the blast, his shirt caught
   fire 🔥 #history #darkhistory #historytok #tunguska #sleepstory". Kies #mystery of
   #unsolved bij mysteries.
   Zet ALLE Shorts met bijschrift op de TikTok-pagina (zie
   "TikTok-overzicht" hieronder). Geen Google Drive.

## TikTok-overzicht (voor de eigenaar)
Alle Shorts (ook die niet naar YouTube gaan) komen op één vaste pagina:
https://claude.ai/artifact/G4rD4rSmPFCxjZiA5PueXQ (Artifact "Sleep Archives TikToks"; database-collectie `tiktoks`).
Zet elke Short erop (`datum` = de TikTok-datum uit planning.txt, short1..N):
1. Upload het mp4-bestand als asset: Artifact-tool, `url` = de pagina hierboven,
   `asset: true`, `file_path(s)` = de Short(s). Bewaar het teruggegeven id en url.
2. Schrijf per Short één document met ArtifactData (`action: "set"`, `url` = de pagina,
   `collection: "tiktoks"`, `doc_id: "<map>-<shortnaam>"`), met deze velden:
   `onderwerp` (titel van de lange video zonder "| History for Sleep" of "| Sleep Documentary"), `titel`
   (YouTube-titel van de Short zonder " | …"), `datum` (publicatie in
   Nederlandse tijd als "JJJJ-MM-DDTUU:MM"), `bijschrift` (TikTok-bijschrift),
   `video_id`, `video_url` (de url uit stap 1, bv. "/_blob/<id>"), `bestand`
   (bv. "<map>-<naam>.mp4"), `youtube` (link van de Short, of "" als hij niet op YouTube
   staat), `geplaatst: false`.
3. De YouTube-Short (short1) komt er een tweede keer op als YouTube-kaart: doc_id
   `<map>-yt`, zelfde video, plus `platform: "youtube"`, `datum` = `yt-short` uit
   planning.txt, `titel` = volledige YouTube-titel, `beschrijving` = YouTube-beschrijving.
   De pagina toont die met een rode rand en "Voor YouTube"; de eigenaar uploadt hem zelf.
Lukt dit niet, stuur de Shorts dan in de chat zoals voorheen.
