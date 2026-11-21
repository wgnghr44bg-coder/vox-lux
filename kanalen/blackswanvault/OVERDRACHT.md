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
| vr 27 nov | 15:00 | Elon Musk's SpaceX Just Fell Below Its IPO Price (video9; titel 21 nov aangepast, CTR-les) | uLoUpPHRz9g |
| vr 27 nov | 17:00 | Short: SpaceX Stock Fell Below Its $135 IPO Price | ZdwE2HdjVJg |

Thumbnails wo/do/vr (eigenaar 21 nov: "alle 3 goed, je leest en ziet meteen waar het over gaat"): het ONDERWERP zelf
(winkelwagen met lange kassabon / gebroken bitcoin / Starship), gemaakt met `thumb_ding.py`; niet meer een geschrokken gezicht.
Rood viel weg op rode achtergronden; letters hebben nu een zwarte rand.

**Hype-seintje (21 nov, werkt, getest):** `tools/swan_yt_wacht.py` (08:10 en 15:55) stuurt via de gratis app ntfy een melding
naar de telefoon van de eigenaar bij echt grote hype (STERK: YouTube + nieuws, of koers >= 2x de GROOT-grens) waar we nog geen
video over hebben; max 1x per onderwerp per dag. Kanaalnaam staat ALLEEN op de pc in `~/.swan-ntfy.json` (niet in de openbare repo).
Opnieuw testen: `python -c "import sys; sys.path.insert(0,'tools'); import swan_yt_wacht as w; w.seintje('Test','tekst')"`.
Er wordt niet vanzelf een video gemaakt: de eigenaar opent Claude en zegt "maak de hype-video".
Website (docs/status): planning per dag Swan | Sleep, "Hype nu" met nieuwswacht + YouTube-wachter; NOIRTRACES staat er niet meer op.

**Verzetten mag (eigenaar 21 nov):** komt er echt grote hype (STERK in de wachters), dan mag een geplande privé-video
naar een latere dag (publishAt aanpassen via de API, kanaal checken) om plaats te maken. Nieuwe video eerst laten zien.

**CTR-les (21 nov, Studio-AI):** Nvidia 4,6% vs Anthropic 1,6%. Anthropic-video (5C2MIFhR314) kreeg nieuwe thumbnail met Claude-logo
(`video2/thumbnail-definitief.jpg`, oud: thumbnail-oud.jpg). Titels: mens/drama en bekende naam als het echt klopt.

## Reservevideo's (eigenaar 21 nov: "maak video's voor reserve")
Video's die niet verouderen, voor dagen zonder groot nieuws. Soorten: "Why X got so expensive", "Can X come back?", "How X makes money".
- `reserve1-ram/`: waarom RAM zo duur is. Titel "Why RAM Costs 4x More. AI Is Eating Your Memory". Script KLAAR (1.480 woorden, feiten nagekeken, bronnen.md).
  Stem gestart 21 nov 10:50 (los proces, log C:\Users\rane\bsv-r1-stem.log, eind "R1-STEM-KLAAR"; LET OP/FOUT-regels nakijken).
  AI-beelden: taak "BlackswanVault reserve1 beelden" 12:00 en 13:30 (beelden.sh, alleen als de stem klaar is; log bsv-r1-beelden.log).
  NOG DOEN (Claude): Wikimedia-foto's, render-shots per @scene (zie video9), Short, thumbnail, beschrijving met hoofdstukken; dan aan eigenaar laten zien.
- `reserve2-intel/`: kan Intel terugkomen? CONCEPT-script (21 nov 10:55), feiten met * in bronnen.md nog nakijken (vooral 2024-2025 uit eigen kennis), koers nu ophalen. Eigenaar 21 nov: "schrijf alleen scripts" (geen productie zonder vraag).
  Stand 10:54: 1.240 woorden (± 7 min) → nog ± 200 woorden erbij; opening gaat nu over rally + val van 27% op 30 okt. Koersgrafiek 2026 uit Yahoo halen (bronnen tegenstrijdig).
- `reserve3-costco/`: hoe Costco geld verdient ("Costco Sells a $1.50 Hot Dog. Here's How It Made $9 Billion"). CONCEPT-script, FY2026-cijfers nagekeken, rest (*) nakijken in bronnen.md.
- Volgende reserve-ideeën (nog niets gedaan): "Why Concert Tickets Cost So Much" (Live Nation/Ticketmaster, rechtszaak DOJ), "Can Boeing Come Back?". Telkens: mens/bekende naam in de titel als het klopt (CTR-les).

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
- **za 28 / zo 29: WACHTEN (eigenaar 21 nov: "deze week zit al vol, is wachten niet beter").** Nieuws moet vers zijn:
  do 26 onderwerp kiezen met nieuwswacht + YouTube-wachter (stories/nieuws.json, stories/yt-hype-swan.json), do/vr maken,
  vr 27 laten zien, na OK inplannen. Kandidaten 21 nov: Nvidia SEC-onderzoek boekhouding (NYT, "said to"; ColdFusion-video 20x),
  dure RAM/geheugenchips (Logically Answered 5x), Oracle $20 mld, goud/zilver (vooral India). Overige kandidaten (20 nov):
  - **Oracle haalt $20 mld op** (aandelen + schuld) voor AI-datacenters — checken.
  - **Beurs in correctie (vr 20 nov)**: S&P 500 > 10% onder de top, Nasdaq 100 -3,8% op één dag, Nvidia -7%, VIX 31. LET OP: maandag-video4 gaat al over de Nasdaq; alleen als vervolg met nieuw nieuws.
  - **Anthropic na de beursgang** ($81,3 mld, dag 1 +17%, dag 2 -10 à 12%): overlap met video2 en video8, alleen als er groot nieuw nieuws is.
  - AFGEVALLEN (bleek nieuws van nov 2025): importheffingen op voedsel terug, Netflix-MLB-deal.
  - Morgen (21 nov) eerst YouTube-zoeken (quota is dan weer vrij) op meest bekeken geld-/bedrijfsnieuws.
  - 21 nov: YouTube-wachter gemaakt: `tools/swan_yt_wacht.py` (Taakplanner "BlackswanVault YouTube-wachter", 08:10 en 15:55)
    → `stories/yt-hype-swan.json`; STERK = groot op YouTube én in de nieuwswacht. Eerste uitslag: AI-crash beurs (→ ma video4),
    Anthropic -25%?, GOUD/ZILVER (12 kanalen) = mogelijk nieuw onderwerp.
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
