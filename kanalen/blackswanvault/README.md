# BlackswanVault (@blackswanvault): werkwijze (stand 19 nov 2026)

Dit is het **FOCUS-kanaal** (eigenaar 19 nov avond). Het gaat over zakelijk en economisch nieuws in de stijl van ColdFusion, in het Engels, voor kijkers in de VS.
Planning en ritme staan in `kanalen/PLANNING.md`: 1 grote lange video per week + 1 extra lange bij groot nieuws (alleen als hij net zo goed is) + elke dag een Short (eigenaar 20 nov; na 4 weken evalueren op kijkduur). Opbouw nieuwsvideo: antwoord binnen 2 min, geschiedenis daarna; titels ±40 tekens.
Sleutel: `YT_WHATIF_REFRESH_TOKEN`.

## Vaste regels van de eigenaar
- **Pakkend beeld (eigenaar 19 nov: "let daar op bij andere video's, maak het wel pakkend voor de mensen"):** geen saaie algemene achtergronden (controller, code op een scherm, lege serverruimte, een console op een tafel) als er iets sprekenders is. Kies het meest opvallende echte beeld dat bij de zin past (officieel artwork/screenshot, persfoto, sterke foto). Grote tekst op een druk beeld altijd met een donkere balk erachter. Controleer elke video met `render3.py --plaat` op saaie of herhaalde achtergronden.
- **Geen claims (eigenaar 19 nov: "doe wat mag volgens YouTube, ik wil geen claims"):** alleen vrije licenties (Wikimedia CC/PD, met vermelding) of eigen AI-beelden (ComfyUI, "AI-generated image" in beeld). GEEN officieel artwork/screenshots van bedrijven of games in de video. Uitzondering (eigenaar 19 nov, keuze B): de thumbnail mag de officiële cover/key art van het onderwerp gebruiken (klein risico; bij een melding alleen de thumbnail vervangen). Verder geen trailers, geen gelekt materiaal, geen nagemaakte game-personages of logo's in AI-beelden. **Volgorde (eigenaar 19 nov, nogmaals):** 1) echte beelden (vrije foto's) als ze goed en pakkend zijn en passen; 2) anders een goede AI-afbeelding; 3) echte video mag ook, maar alleen vrij te gebruiken en van goede kwaliteit (scherp, rustig, niet schokkerig). **Stockvideo (eigenaar 19 nov):** echte, scherpe stockvideo via `stock/mixkit.py` (Mixkit, gratis licentie, geen sleutel nodig; "Video: Mixkit" in beeld). Werkwijze: `python stock/mixkit.py zoek "<term>"` geeft een voorbeeldplaat in `stock/voorbeeld/`; kies, dan `python stock/mixkit.py haal <id> videoN`; in render3 gebruik je `F("v:mk-<id>")` (ook in `fot`/`lijst`). Geen clips met een echt spel of tv-beeld op een scherm. Pexels/Pixabay kunnen ook, maar daarvoor heb je een gratis API-sleutel van de eigenaar nodig (`kanalen/bodycam/zoek_vrije_videos.py`). **Nooit fragmenten uit nieuwsprogramma's** (CNBC, Bloomberg, Fox enz.): Content ID, dus claims. **Geen halve beelden:** niet zo ver inzoomen dat er een half mens of onderwerp in beeld staat, en geen vage of onscherpe foto's. Laat niet meer dan ± 4 zinnen op hetzelfde beeld staan, en gebruik hetzelfde beeld niet 3 keer. Opsommingen: alle regels in dezelfde stijl. Zoek per video eerst echt beeld en video op Wikimedia Commons (ook video's), NASA, Amerikaanse overheid (PD) en vergelijkbare vrije bronnen, vóór AI.
- **Lengte: minimaal 8 minuten** (eigenaar 19 nov: "Ja minimaal 8 min"); vanaf 8 min mag YouTube ook halverwege reclame tonen. Meer verhaal en context, geen opvulling of herhaling.
- **Beeld:**
  - Per zin een beeld dat letterlijk past bij de tekst:
    - persoon: echte foto met naam;
    - bedrijf: gebouw of logo;
    - document: eigen documentkaart;
    - getal: grafiek.
  - Wissel om de 1 à 2 zinnen van beeld, niet sneller. Vooral in de eerste minuut niet te snel.
  - **Geen slechte of schokkerige video's.** Gebruik scherpe vrije foto's (Wikimedia, met vermelding in beeld) of goede AI-foto's die bij de tekst passen.
  - Geen AI-gezichten van echte mensen.
- **Geluid:**
  - Stem `zakelijk-23` op speed 1.0.
  - Zelfgemaakte muziek (`mix.py`), zonder geluidseffecten.
  - Geen hoofdstukkaarten in beeld, geen intro, geen zwaan, geen outro of abonneer-oproep.
- **Tekst:**
  - Alleen bevestigde feiten (`bronnen.md` per video). Schattingen benoemen we als schatting.
  - **Niets twee keer vertellen** (hetzelfde bedrag of feit maar één keer).
  - **Getallen in cijfers** in titel, beschrijving en hoofdstukken ($81 billion, 19 million, Day 1), nooit uitgeschreven (eigenaar 20 nov). Alleen in script.txt voor de stem mogen ze uitgeschreven blijven.
  - **Rustige beeldwissels** (eigenaar 20 nov: "komt weer zo druk over"): elk beeld minstens ± 4 s in beeld (korte zinnen samen op één beeld), overgang ± 0,7 s zacht overvloeien.
  - **Uitspraak controleren** (eigenaar 20 nov, "launched" klonk raar): na de stem `check_stem.py` én `woordcheck.py` (Whisper per woord) draaien; elke zin waar Whisper een ander woord hoort (bv. "all fall platforms") opnieuw inspreken met een andere seed, of anders verwoorden.
  - **Grafieken: getal pas als de lijn er is** (eigenaar 20 nov: "zorg dat dit altijd zo blijft"). Een label op een koersgrafiek (-7%, +6%, $262) hangt aan een datum en verschijnt pas als de lijn die datum bereikt (`koers(..., labels=[("2025-05-02", x, y, "-7%", ROOD)])`); zinnummers zijn niet toegestaan (render3 stopt dan). Na elke wijziging van het script: zinnummers in SHOTS opnieuw nalopen (elke tekst moet bij een zin binnen dat beeld horen) en een controleplaat maken (`render3.py --plaat`).
  - **Korte vraag** ("Why?"): 1,2 s stilte ervoor en 1,6 s erna (stem.py).
  - **Clip moet passen bij wat er gezegd wordt**; past geen echte clip, dan liever een AI-beeld dat er in het algemeen bij hoort (eigenaar 20 nov, Zynga met een schreeuwende gamer).
  - **Opsommingen rustig:** elk item een eigen korte zin op een eigen regel in `script.txt`. Die krijgt 0,6 s pauze, en elk item komt apart in beeld.
- **Beschrijving:** 3 zinnen, hoofdstukken, "Not financial advice." en 3 hashtags. Geen streepjes en geen dubbele punten in kanaalteksten.
- **Thumbnail:** andere tekst dan de titel. Letters nooit over het onderwerp. Met `thumb.py`: links grote letters, rechts het onderwerp; logo van het bedrijf erbij (`THUMB_MERK=...`). Thumbnail: officiële cover/key art mag (keuze B, eigenaar 19 nov); in de video zelf niet.
- **Vaste thumbnailstijl (eigenaar 20 nov, markt-video: "zet dit zo vast, dat spreekt mensen aan"):** links zwart verloop met korte regels Impact-letters onder elkaar: onderwerp in wit (bv. NASDAQ), het harde cijfer groot in rood (bv. -13%), en een prikkel in wit die nieuwsgierig maakt, per video anders (niet steeds WHY?; eigenaar 20 nov: "hoeft niet bij elk why, gewoon iets wat mensen nieuwsgierig maakt"; bv. NOT HACKERS., AI DID THIS?); logo linksboven (rond). Rechts een beeld met emotie (bv. trader met hoofd in handen) en, bij koersen, de echte koerslijn in rood eroverheen die eindigt met een stip. Het cijfer op de thumbnail is het echte, harde cijfer (mag scherper zijn dan de titel, nooit overdreven). Script: `video4/thumb_markt2.py <beeld> <regel1> <regel2> <uit.jpg> [regel3]`; voorbeeld `video4/thumbnail-definitief.jpg`.
- **YouTube:**
  - Altijd eerst privé uploaden en via de API het kanaal controleren.
  - Openbaar alleen na een expliciete OK van de eigenaar.
  - AI-label aan (`containsSyntheticMedia`). Na elke wijziging van de status controleren of het nog aan staat.

## Mappen
- **`video1/` (Nvidia, online: https://youtu.be/ioMjKb2_dVI)**
  - `script.txt`: één zin per regel, met `@scene`-markeringen.
  - `stem.py` → `stem.wav` + `zinnen.json`.
  - `check_stem.py`: Whisper-controle.
  - `mix.py`: muziek.
  - `render.py` / `render2.py` / `render3.py`: beeld per zin, als lijst `SHOTS`.
  - `maak_v3.sh`.
- **`video2/` (Anthropic IPO, privé gepland vr 20 nov 15:00: https://youtu.be/5C2MIFhR314)**
  - Zelfde opbouw, plus `slotkoers.py`, dat de slotkoers van dag 1 in het script zet, en `maak.sh` (de hele keten).
  - Controleplaat: `python render3.py --plaat uit.jpg`.
- **`video3/` (GTA 6 / Take-Two):** `bronnen.md`. Wacht op de officiële verkoopcijfers van Take-Two (verwacht uiterlijk 23 nov).
- **`shorts/`**
  - `maak_short.py <videomap> <video.mp4> <zin_a> <zin_b> "<KOP>" <uit.mp4>` maakt een staande Short (1080x1920) uit de lange video. De 16:9-video staat in het midden, met een kop bovenin en grote ondertiteling: hele zinsdelen tot de komma of punt (max. 2 regels, lange zinnen in gelijke delen), blokken zonder overlap en altijd op dezelfde plek (bovenste regel vast), zodat niets op en neer springt (eigenaar 19 nov). De ondertiteling volgt de woordtijden van Whisper op de stem (`woorden.py`, op de CPU). Getallen staan in cijfers (eigenaar: "je mag ook cijfers gebruiken").
  - Kies een stuk van 30 tot 55 s met een haak en een open vraag aan het eind.
  - **Geen # in de titel** (ook niet #Shorts; eigenaar 20 nov). Hashtags alleen onderaan de beschrijving.
  - Voorbeeld: `nvidia-short-1` = zin 0 t/m 9 van video 1.
- **Beelden en geluid** (echt/*.jpg, *.wav, *.mp4) staan **alleen op de pc**, niet in git. `echt/bronnen.tsv` bevat de vermeldingen.

## De videokaart delen
- Er is maar één videokaart.
- Zolang `~/gpu-bezet.lock` bestaat, start `tools/keten_bewaker.py` geen Sleep-keten.
- Sleep Archives en NOIRTRACES staan op pauze (taak "Sleep Archives bewaker" staat uit).
- **Stem blijft zakelijk-23 (eigenaar 20 nov):** proeven met ontworpen stem E, eigen opnames 'Yessssssaaasss' (eigen-stem-swan) en 'Trrr' (eigen-stem-trrr) gemaakt (`stemproef/`); eigenaar: "ik laat het zo met de stem die ik al had". De eigen opnames staan alleen op de pc (`~/vox-lux-stemmen/`).
