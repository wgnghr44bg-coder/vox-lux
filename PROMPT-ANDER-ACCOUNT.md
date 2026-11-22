# Prompt voor een ander Claude-account (stand za 21 nov 2026, ± 14:45)

Plak dit in een nieuwe Claude Code-sessie op de pc van de eigenaar (map `C:\Users\rane\Documents\vox-lux-routine`):

---
Je neemt het werk over van een ander Claude-account voor de YouTube-kanalen van de eigenaar. Praat Nederlands, simpel.
Lees EERST: `CLAUDE.md`, `kanalen/blackswanvault/README.md`, `kanalen/blackswanvault/OVERDRACHT.md`, `kanalen/blackswan-nl/PLAN.md`.
Vaste regels: uploaden altijd eerst privé en kanaal controleren (`snippet.channelTitle`); openbaar of publishAt alleen met OK van de eigenaar;
vraag eerst als iets geld kost; eigen stembestanden nooit op GitHub (repo is openbaar); committen alleen via
`python -c "import sys; sys.path.insert(0,'tools'); from gitveilig import bewaar; bewaar([...], '...')"`; AI-label aan; cijfers altijd nakijken
(slotkoersen, niet koersen van tijdens de handel); video's sturen met SendUserFile `display: "render"` + kleine versie.
Pc heeft weinig geheugen: één zware taak tegelijk, als los proces (Start-Process), geen eigen wachtlussen op de achtergrond.

VASTE WERKWIJZE nieuwskanalen (BlackswanVault + Geldverhaal): nieuwsvideo's hooguit 1-2 dagen vooruit, wachters kiezen elke ochtend het onderwerp,
reservevideo's voor rustige dagen, Shorts dezelfde dag (zie kanalen/blackswanvault/README.md). Sleep Archives mag ver vooruit.

## 0. NIEUW (22 nov nacht): getekende video's (whiteboard) — lees `kanalen/TEKENSTIJL.md`
Eigenaar: "zo is het perfect eigenlijk". Beste voorbeeld: `kanalen/blackswanvault/proef-teken/nvidia3/`. Kanaal Alteraqon is leeggemaakt om om te bouwen (taal/onderwerp nog bevestigen).
Sleep Archives staat STIL tot de eigenaar "hervatten" zegt (zie TEKENSTIJL.md, onderaan). BlackswanVault en Geldverhaal: alleen op hype (wachters).

## 1. Geldverhaal (NL-kanaal, was NOIRTRACES) — video 1 loopt
- Map `kanalen/blackswan-nl/video1/`. Titel: "Anthropic Naar De Beurs, ASML Zakt 9%: Barst De AI-Bubbel?" (`youtube-titel.txt`).
- Thumbnail: `thumbnail-definitief.jpg` (gemaakt door de eigenaar; verzonnen percentages zijn eruit gehaald — nooit verzonnen cijfers).
- Script `script.txt` (± 8 min, natuurlijk Nederlands), bronnen `bronnen.md`, beelden per zin `render-shots.py`.
- BEZIG: `keten2.sh` (log `C:\Users\rane\geld-v1b.log`): nieuwe zinnen inspreken → Whisper → muziek → render → `geldverhaal-asml.mp4` + `-klein.mp4`.
  Klaar als de log eindigt met `GELD-V1-KLAAR`. Bij `GESTOPT`: render.log lezen.
- Daarna: (a) `check.log` nakijken (Whisper per zin; fout verstaan → `stem.py --opnieuw <nr> --seed <n>`), (b) `plaat.jpg` bekijken
  (passen de beelden? geen personen die het niet zijn), (c) Short maken: `python ../../blackswanvault/shorts/maak_short.py . geldverhaal-asml.mp4 0 15 "<KOP>" short.mp4 --zonder-ondertitels`
  (zinnen 0..15 = opening t/m "…de nieuwste chips maken"; controleer de nummers in zinnen.json), titel `short-titel.txt`, beschrijving `short-beschrijving.txt` ({LINK} invullen),
  (d) hoofdstuktijden in `youtube-beschrijving.txt` ({HOOFDSTUKKEN}) uit zinnen.json, (e) video + Short naar de eigenaar sturen.
- Uploaden pas na OK: `YT_KANAAL=altena python tools/youtube_upload.py ...` (zelfde kanaal-ID UC_6p9gp5aBf-eHY5VmJEw4w), privé, kanaal checken.
- Kanaal: naam "Geldverhaal" en logo zet de eigenaar zelf in Studio (API kan dat niet); handle @Geldverhaal kan pas ± 2 dec.
  Banner, beschrijving (staat LOS van BlackswanVault, niet noemen), taal nl zijn al gezet.
- Uitspraak: "Claude" niet laten zeggen (wordt "kloot"); zeg "een van de bekendste chatbots", toon Claude in beeld. Elke nieuwe zin met Whisper nakijken op zulke woorden.
- Vaste dingen: stem `richard-nl` speed 1.1 seed 1, PER ZIN (stem.py; per alinea is afgewezen); afkortingen die fout gaan als letters (A E X, S E C);
  thumbnailstijl `kanalen/blackswan-nl/thumb_geld.py` (gouden balken, rood getal, beeld over hele thumbnail; nooit Swan-stijl);
  grafieken tonen top en laagste; echte beelden waar het mag en past, AI-beelden zonder mensen.
- Volgende video's: RAM (script `kanalen/blackswanvault/reserve1-ram`, NL-versie schrijven), box 3, wat de NL-wachter (`tools/nl_wacht.py`, `stories/nl-hype.json`) aangeeft.

## 2. BlackswanVault (Engels)
- Alles t/m vr 27 nov staat privé ingepland (tabel in OVERDRACHT.md). AI-label staat aan op alle video's (ook Sleep Archives en NOIRTRACES).
- OPEN, EIGENAAR NOG VRAGEN: in video8 (Bitcoin, do 26) en video9 (SpaceX, vr 27) staan cijfers van vóór de beurssluiting:
  "Nasdaq 100 almost 4%" moet "more than 5%" (slot -5,6%); goud "about 2.5% to $3,536" moet "about 4.6% to about $3,515"; goud "more than 35% below peak" is ± 34%.
  BEZIG (eigenaar zei "ja", 21 nov): `kanalen/blackswanvault/fix-cijfers.sh`, log C:\Users\rane\fix-cijfers.log; zie OVERDRACHT. Oorspronkelijk plan: alleen die zinnen opnieuw inspreken (`stem.py --opnieuw`), tekst in beeld aanpassen
  (render8-shots.py regel met "-3.8%" en "$3,536"; render9-shots.py "Nasdaq 100 almost -4%"), opnieuw renderen, privé uploaden met DEZELFDE publishAt, pas daarna oude weg.
- Wo 25 nov avond: actualiteitscheck Bitcoin/SpaceX-video's (zie OVERDRACHT): koersen flink veranderd → slotzin 'laatste stand' + evt. titel aanpassen.
- Ma 23 nov: Nasdaq-video (video4) bijwerken met laatste koersen + grafiek met top/laagste (code: `kanalen/blackswan-nl/video1/render.py` lijn(hoog_laag=True)), laten zien, uploaden na OK.
- Do 26: onderwerpen za 28 / zo 29 kiezen met de wachters. Reserve-scripts: `reserve1-ram` (stem al klaar), `reserve2-intel`, `reserve3-costco` (concepten).
- Titels: mens of bekende naam als het klopt (CTR-les: Nvidia 4,6% vs Anthropic 1,6%).

## 3. Wachters en seintjes (draaien vanzelf)
- `tools/nieuwswacht.py` (08:00/15:45), `tools/swan_yt_wacht.py` (08:10/15:55), `tools/nl_wacht.py` (08:20/16:05) → website `docs/status`.
- Telefoon-seintjes via ntfy (kanaalnaam alleen op de pc in `~/.swan-ntfy.json`). 28 nov 10:00: herinnering cijfers vergelijken (Sleep + Swan). 7 dec 10:00: Geldverhaal (2 weken na eerste video; datum meeschuiven als die later online komt).
---
