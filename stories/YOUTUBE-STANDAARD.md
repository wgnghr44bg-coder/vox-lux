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
   melodie. **Geen piano, geen scherpe geluiden.** Nooit muziek uit CapCut,
   TikTok of andere nummers gebruiken (auteursrecht).
4. **Video**
   ```
   python3 tools/make_video.py stories/<verhaal> --tijden afbeeldingen-tijden-pauzes.tsv \
       --audio stories/<verhaal>/video/stem-met-pauzes.wav \
       --muziek stories/<verhaal>/video/muziek432.wav --muziek-db -17
   ```
   1080p25, langzame zoom per afbeelding, zachte overgangen (1,5 s), drijvende mist.
   Muziek op -17 dB: duidelijk zachter dan de stem, vooral hoorbaar in de stiltes.
   Duurt ± 1,6× de videolengte (4 cores). Test eerst met `--tot 100`.
   Bij meer dan 20 afbeeldingen zet het script eerst groepjes van 20 clips aan elkaar
   (anders te weinig geheugen: 75 clips in één keer ging mis bij San Francisco 1906).

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
2. **Gesproken begin**: de eigenaar wil dat de stem begint met "Did you know? [pause] <weetje>",
   simpel Engels, nieuwsgierig makend, en het weetje moet in het stukje verteld worden.
   Tekst in `shorts-intro/<naam>.txt`, inspreken (eerst akkoord vragen, kost geld):
   `python3 tools/xai_voiceover.py stories/<verhaal>/shorts-intro/<naam>.txt --proxy-auth -o stories/<verhaal>/shorts-intro/<naam>.mp3`
   Tekst en mp3 in git houden (klein), dan hoeft het nooit opnieuw betaald te worden.
3. `python3 tools/make_short.py stories/<verhaal> --lijst shorts.tsv [--alleen <naam>]`
   → `video/shorts/<naam>.mp4` (1080x1920, schuivend beeld, mist, grote ondertitels,
   432 Hz-muziek op -17 dB). Geen eindtekst (de eigenaar wil het simpel; `--eindtekst` zet
   "Full sleep documentary on the channel" er toch in). ± 3 min per Short.
4. Eerst 1 proef in de chat (< 30 MB), pas na akkoord de rest.
5. YouTube: privé, Education, niet voor kinderen, AI gemarkeerd. Titel: korte rustige zin +
   ` | <korte naam> #Shorts`. Beschrijving: 1–2 zinnen, link naar de volledige video, de AI-regel,
   `#shorts #sleepdocumentary #<onderwerp> #history`. Teksten in `shorts-teksten/`.
6. TikTok: map "TikTok – <korte naam>" in Google Drive met een bijschrift per video. De video's
   zelf (± 10 MB) zijn te groot voor de Drive-koppeling: stuur ze in de chat.
