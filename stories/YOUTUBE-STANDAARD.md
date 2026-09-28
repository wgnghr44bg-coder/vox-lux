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
Meld de eigenaar de link en wat nog in YouTube Studio moet: nalopen, AI-melding
controleren, Visibility → Public. Herinner eraan dat de refresh token 7 dagen
geldig is (zie `stories/pompeii/VOLGENDE-STAPPEN.md`).
