# BlackswanVault: overdracht (stand vr 20 nov 2026, 21:45)

Vaste regels: `README.md` (getallen in cijfers, rustige beeldwissels, clip moet passen, uitspraak controleren, grafieklabels pas als de lijn er is, thumbnailstijl, stem blijft zakelijk-23). Planning: `../PLANNING-KANALEN.json`.

## Gepland op YouTube (privé, gaan vanzelf openbaar; kanaal gecontroleerd)
| dag | tijd | wat | id |
|---|---|---|---|
| za 21 nov | 15:00 | Why Is Take-Two's Stock Falling After GTA 6? (video3) | GEktvTAsVIw |
| za 21 nov | 17:00 | Short: GTA 6 Broke Records. So Why Did the Stock Fall? | HWcKzzN7PzI |
| zo 22 nov | 15:00 | Microsoft, JPMorgan and the FAA All Went Down. It Wasn't Hackers (video5) | nMqDK9HAAcA |
| zo 22 nov | 17:00 | Short: Microsoft, JPMorgan and the FAA All Went Down in One Week | l3tU0GKVldM |
| di 24 nov | 15:00 | Is AI Actually Working? Harvard Looked Inside 655 Companies (video6) | T8SutKp3Ao8 |
| di 24 nov | 17:00 | Short: Big Tech Is Spending $700 Billion on AI. For What? | _Te7gcc9RAs |

## Maandag 23 nov: markt-video (video4) — NOG NIET geüpload
- Titel: "The Nasdaq Just Fell 10%. Here's What Investors Are Afraid Of". Thumbnail: `video4/thumbnail-definitief.jpg` (NASDAQ / -13% / WHY?).
- Ma-ochtend: koersen ophalen (data/*.json, Yahoo), `{SLOT}` in `video4/script.txt` vervangen door 2-3 zinnen over de laatste stand (GEEN voorspelling), `stem.sh` + `mix.py` + `maak.sh`, controleren, eindversie naar eigenaar.
- Pas na akkoord eigenaar: privé uploaden met publishAt ma 15:00 (14:00Z), kanaal checken.
- Short: `shorts/markt-short-1.mp4` (zin 0-18), beschrijving `shorts/markt-short-1-beschrijving.txt` ({LINK} invullen), ma 17:00. Eigenaar zei "Ja" op 15:00/17:00.
- Beschrijving lange video nog schrijven (3 zinnen, hoofdstukken met cijfers, "Not financial advice.", 3 hashtags).

## Woensdag 25 nov: Black Friday (video7) — KLAAR, NOG NIET GEUPLOAD
- Titel: "Black Friday Will Hit $1 Trillion. Here's the Catch" (eigenaar vond de eerste titel onduidelijk; deze is nieuw, nog niet bevestigd).
- `video7/blackswanvault-blackfriday.mp4` (8,3 min) + `-klein.mp4`; beschrijving `video7/youtube-beschrijving.txt`; bronnen `video7/bronnen.md`.
- Thumbnail: `video7/thumb-a.jpg` / `-b` / `-c` ($1 TRILLION / BUT WHO PAYS?). Eigenaar moet nog kiezen.
- Short: `shorts/blackfriday-short-1.mp4` (zin 0-10, zonder ondertitels), beschrijving `shorts/blackfriday-short-1-beschrijving.txt` ({LINK} invullen).
- Pas na OK eigenaar: privé uploaden, publishAt wo 25 nov 15:00 (14:00Z) en Short 17:00 (16:00Z), kanaal checken.

## Do 26 t/m zo 29 nov: elke dag een hype-onderwerp (eigenaar 20 nov 21:40)
Eigenaar: "je mag die hele week volmaken met hype onderwerpen ... mits usage dat haalt; zo niet, sla het op GitHub op zodat ander account ook verder kan".
Het hoeft niet over AI te gaan, als het maar hype is (geld, bedrijven, beurs, economie). Per dag: lange video 15:00 + Short 17:00. Alles eerst laten zien, uploaden pas na OK.
Kandidaten (20 nov gezocht; YouTube-zoeken zat aan de quotalimiet, trending + web gebruikt):
- **do 26: Bitcoin-crash** (video8): ± $65.000, bijna -50% vanaf record $126.080 (6 okt 2025), 6 weken op rij omlaag, -17% in november, ETF-uitstroom, angstindex 13. Bronnen nog zelf nalezen (CoinDesk, Cointelegraph, ETF-cijfers).
- **SpaceX-aandeel**: beursgang juni 2026 (Nasdaq SPCX, $135), eind juli ± -50% vanaf piek; $24 mld plan Starbase-centrale. Eerst nieuws van november zoeken.
- **Trump draait importheffingen terug** (prijsverlaging?) — nog checken.
- **Netflix koopt MLB-honkbal** (19 nov) — sport + geld.
- **Oracle haalt $20 mld op voor AI** (schuld + aandelen).
- NIET: Nvidia-cijfers (video1 ging al over Huang; dubbel), storingen/hack (video5), AI-productiviteit (video6).
Werkwijze: kopieer video7 (`stem.sh`, `mix.py`, `maak.sh`, `render7-basis.py`, `thumb_v2.py`, `echt/`-tools) naar videoN; zie Gereedschap hieronder.

## Ritme vanaf 20 nov avond
Elke dag een lange video + Short als er goed nieuws is; anders alleen een Short. Thumbnailstijl v2 (README).

## Gereedschap (video7 is het nieuwste voorbeeld; render7.py = render7-basis.py + render7-shots.py + staart van video3/render3.py)
- `video5/`: stem.sh (stem + Whisper), mix.py, maak.sh, render5-basis.py + render5-shots.py → render5.py
  (`m=$(grep -n "^def shot_op" ../video3/render3.py | cut -d: -f1) && { cat render5-basis.py render5-shots.py; echo; tail -n +$m ../video3/render3.py; } > render5.py`).
  ZR() mag halve zinnen (49.5). `ZINNEN=<bestand>` om met andere tijden te renderen.
- Foto's: `echt/zoek.py` + `echt/dl.py naam=Titeldeel` (Wikimedia, credits in echt/bronnen.tsv). AI-beelden: `ai/prompts.txt` + `tools/comfy/comfy_batch.py`.
- Thumbnail: `video5/thumb_markt2.py <beeld> <regel1> <regel2> <uit> [regel3] [--geen-lijn]`; derde regel = prikkel, per video anders (niet steeds WHY?).
- Shorts: `shorts/maak_short.py` (knipt nu altijd vóór de volgende zin); woorden.json nakijken op dubbele stukken van Whisper.
- Beelden, stem en mp4 staan alleen op de pc (niet in git). Eigen stemopnames alleen in `~/vox-lux-stemmen/`.
