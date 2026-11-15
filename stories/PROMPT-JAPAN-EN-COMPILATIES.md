# Japan ombouwen, compilaties, hoofdstuknamen, mythologie (eigenaar 15 nov 2026)

Start in een NIEUWE, korte sessie: "Lees stories/PROMPT-JAPAN-EN-COMPILATIES.md en voer het uit."
Lees eerst: `stories/AFSPRAKEN.md`, `stories/PROMPT-SCRIPTS-DEC.md`, `C:\Users\rane\Videos\Analyse grote kanalen - 15 nov 2026.txt`.
Houd het verbruik in de gaten: `python tools/claude_gebruik.py` (begin en na elke stap).

**Vaste regels:** altijd eerst vragen als iets geld kost of als er iets verwijderd wordt (ook op YouTube). Nooit
"Human Voiced" in een titel. Git alleen via de wachtrij: `python -c "import sys; sys.path.insert(0,'tools'); from gitveilig import bewaar; bewaar([...], '...')"`
(nooit losse `git pull`: de keten draait op de pc). Na elke stap: commit + push + één regel in `stories/ROUTINE-LOG.md`.

## Stap 1. japan-1600 (za 26 dec) ombouwen naar de nieuwe opbouw
Zoals `stories/londen-kerst-1843/` en `stories/bethlehem/` (opnieuw geschreven in `src-feiten/`).
- `src-feiten/`: `stijl.txt`, `begin.txt` (25-70 woorden, alleen verhaal: plaats + tijd + het thumbnailbeeld; geen
  "Let's begin", geen ontspanningszinnen), `abonneer.txt` (15-22 woorden, anders verwoord), `deel1.txt`-`deel3.txt`
  (± 85 blokken in 13 TOPICs, minstens 13.500 woorden, IMG/HEAD/BODY, geen BRIDGE), `slot.txt`.
- **Eerste TOPIC = de kern van de titel** "Life in Japan in the Age of the Samurai, 1600": het dagelijks leven van
  samoerai en gewone mensen rond 1600, niet eerst achtergrond.
- `bouw_script.py`, `maak_tijden.py`, `maak_motion.py` uit londen-kerst-1843; kaart in maak_motion: `gebied` is
  `[lon_min, lon_max, lat_min, lat_max]` (motion.py corrigeert de andere volgorde nu ook, maar schrijf hem goed).
- `planning.txt`: regel `thumbnail kenmerk: …` (kenmerkend beeld + mensen van toen die doen wat er gebeurde);
  status `script-klaar (nieuwe opbouw, opbouw Sleepy <datum>, Claude)`. Titel staat al goed.
- `youtube-beschrijving.txt` zoals thanksgiving-1621 (2 zinnen, vast stukje, Chapters, 15 hashtags).
- Controles, alle vier GOED: `script_leesbaar` (MAKKELIJK/GOED + TOON GOED), `check_afwisseling`,
  `script_check --zonder-model` (SCRIPT GOED) en `tools/afspraken_check.py stories/japan-1600`.

## Stap 2. Plan voor compilaties (NIETS uploaden; plan eerst aan de eigenaar voorleggen)
Voorbeelden: "8 Hours of Ancient History" (Egypte, Babylon, Rome, IJstijd, Bethlehem), "8 Hours of Medieval Life".
- Welke video's zijn al af: `planning.txt` status `klaar` + link; nog op de pc aanwezig (`stories/<map>/video/*-16mm.mp4`)
  of alleen op YouTube? (Na upload ruimt de keten bestanden op: kijk wat er nog is en wat opnieuw gerenderd moet.)
- Hoe aan elkaar zetten: `tools/montage_engine.sh` (stappen, 16mm, QC) en `tools/vervang_video.py` (upload, afspeellijst,
  publishAt). Hoofdstukken in de beschrijving = begintijd van elke video (+ eventueel hun eigen hoofdstukken).
- Titel volgens AFSPRAKEN (geen vraag; "8 Hours" hoort hier wél bij de vorm; nooit "Human Voiced").
- Lever: lijst kandidaat-compilaties, welke video's, totale duur, wat er technisch moet gebeuren, wat het kost (niets?),
  voorstel datum/plek. Wachten op akkoord van de eigenaar.

## Stap 3. Nieuwsgierigere hoofdstuknamen (alleen beschrijving)
Voor de komende video's (vanaf 23 nov) per TOPIC een nieuwsgierige hoofdstuknaam zoals ASMR Historian
("Saint Christopher, the Dog-Headed Martyr"). Alleen in `youtube-beschrijving.txt` (Chapters); de scripts en TOPIC-regels
blijven zoals ze zijn. Kloppende feiten, geen vragen, geen clickbait die het verhaal niet waarmaakt.
Lever eerst als voorstel (tabel per video: huidige naam -> voorstel); pas toepassen na akkoord.

## Stap 4. Voorstel mythologie of "complete history" voor januari
Draai `python tools/hype_wacht.py` (kost alleen YouTube-quota) en lees `stories/HYPE-SIGNAAL.md` en
`stories/concurrent.json`. Stel 2-3 onderwerpen voor (titel volgens AFSPRAKEN, beste datum in januari op ma/wo/za,
waarom: welke kanalen groeien ermee). Datums alleen veranderen met de eigenaar.
