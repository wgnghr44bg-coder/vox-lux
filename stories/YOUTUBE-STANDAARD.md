# YouTube-standaard voor alle sleep documentaries

Gebruik deze instellingen bij **elke** upload met `tools/youtube_upload.py`,
tenzij de eigenaar iets anders vraagt. Alles wordt privé geüpload (Google
vergrendelt uploads van niet-geauditeerde API-projecten op privé); de eigenaar
zet de video zelf op openbaar in YouTube Studio.

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
sounds, no jump scares, just a gentle voice and softly changing images.

Chapters
0:00:00 <eerste hoofdstuk>
<tijd> <hoofdstuk>   ← uit de tijdlijn (tijdlijn.tsv) van de video, 10–15 stuks

Narration and images were created with the help of AI. The story is based on
historical sources<, noem de belangrijkste bron>.

#sleepdocumentary #<onderwerp> #history
```
- Eerste hoofdstuk altijd op 0:00:00, minstens 3 hoofdstukken, elk ≥ 10 s.

## Tags
Altijd: `sleep documentary, history for sleep, bedtime story, relaxing history,
sleep story` + 4–6 onderwerp-tags.

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
