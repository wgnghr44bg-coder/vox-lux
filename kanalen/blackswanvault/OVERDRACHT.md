# BlackswanVault: overdracht (stand za 21 nov 2026)

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
| wo 25 nov | 15:00 | Black Friday Starts a $1 Trillion Season. Here's the Catch (video7) | c4xgBH1o4AE |
| wo 25 nov | 17:00 | Short: Black Friday Season Hits $1 Trillion. Half the Growth Is Just Prices | 8de6ZH3YYp4 |
| do 26 nov | 15:00 | Bitcoin Just Lost Half Its Value. Here's Who Is Selling (video8) | JW4e9rWlukk |
| do 26 nov | 17:00 | Short: Bitcoin Fell Below $60,000. Here's Who Is Selling | gtqCj_lhfm4 |
| vr 27 nov | 15:00 | SpaceX Stock Just Fell Below Its IPO Price. December 8 Could Make It Worse (video9) | uLoUpPHRz9g |
| vr 27 nov | 17:00 | Short: SpaceX Stock Fell Below Its $135 IPO Price | ZdwE2HdjVJg |

Thumbnails wo/do/vr (eigenaar 21 nov: "alle 3 goed, je leest en ziet meteen waar het over gaat"): het ONDERWERP zelf
(winkelwagen met lange kassabon / gebroken bitcoin / Starship), gemaakt met `thumb_ding.py`; niet meer een geschrokken gezicht.
Rood viel weg op rode achtergronden; letters hebben nu een zwarte rand.

## Maandag 23 nov: markt-video (video4) — NOG NIET geüpload
- Titel: "The Nasdaq Just Fell 10%. Here's What Investors Are Afraid Of". Thumbnail: `video4/thumbnail-definitief.jpg` (NASDAQ / -13% / WHY?).
- Ma-ochtend: koersen ophalen (data/*.json, Yahoo), `{SLOT}` in `video4/script.txt` vervangen door 2-3 zinnen over de laatste stand (GEEN voorspelling), `stem.sh` + `mix.py` + `maak.sh`, controleren, eindversie naar eigenaar.
- Pas na akkoord eigenaar: privé uploaden met publishAt ma 15:00 (14:00Z), kanaal checken.
- Short: `shorts/markt-short-1.mp4` (zin 0-18), beschrijving `shorts/markt-short-1-beschrijving.txt` ({LINK} invullen), ma 17:00. Eigenaar zei "Ja" op 15:00/17:00.
- Beschrijving lange video nog schrijven (3 zinnen, hoofdstukken met cijfers, "Not financial advice.", 3 hashtags).

## Woensdag 25 t/m vrijdag 27 nov: GEUPLOAD (privé, gepland; zie tabel)

## Do 26 t/m zo 29 nov: elke dag een hype-onderwerp (eigenaar 20 nov 21:40)
Eigenaar: "je mag die hele week volmaken met hype onderwerpen ... mits usage dat haalt; zo niet, sla het op GitHub op zodat ander account ook verder kan".
Het hoeft niet over AI te gaan, als het maar hype is (geld, bedrijven, beurs, economie). Per dag: lange video 15:00 + Short 17:00. Alles eerst laten zien, uploaden pas na OK.
- do 26 (Bitcoin) en vr 27 (SpaceX): geüpload, zie tabel.
- **za 28 / zo 29: nog maken.** Overige kandidaten (20 nov):
  - **Oracle haalt $20 mld op** (aandelen + schuld) voor AI-datacenters — checken.
  - **Beurs in correctie (vr 20 nov)**: S&P 500 > 10% onder de top, Nasdaq 100 -3,8% op één dag, Nvidia -7%, VIX 31. LET OP: maandag-video4 gaat al over de Nasdaq; alleen als vervolg met nieuw nieuws.
  - **Anthropic na de beursgang** ($81,3 mld, dag 1 +17%, dag 2 -10 à 12%): overlap met video2 en video8, alleen als er groot nieuw nieuws is.
  - AFGEVALLEN (bleek nieuws van nov 2025): importheffingen op voedsel terug, Netflix-MLB-deal.
  - Morgen (21 nov) eerst YouTube-zoeken (quota is dan weer vrij) op meest bekeken geld-/bedrijfsnieuws.
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
