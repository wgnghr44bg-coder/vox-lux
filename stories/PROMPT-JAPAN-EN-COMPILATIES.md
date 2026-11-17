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
**Staan al in de planning** (eigenaar 15 nov): `stories/compilatie-oudheid` (ma 4 jan) en `stories/compilatie-middeleeuwen`
(ma 11 jan), status `compilatie-plan (wacht op akkoord eigenaar)`; de bewaker slaat ze over. Werk het plan uit op die
datums (onderdelen staan in planning.txt; aantal uren in de titel = echte duur, naar beneden afgerond).
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

## Stap 4b. Januari herzien op hype (VOORLEGGEN, niets zelf veranderen)
De januaridatums komen van het tweede account (1 nov), van vóór de hype-wachter. Gebruik dezelfde uitkomst als stap 4
(`stories/hype.json`, `HYPE-SIGNAAL.md`, `concurrent.json`) en maak één voorstel voor heel januari:
- per januari-video: past hij nog, of is er een betere plek/een beter onderwerp? (jaardagen, hype, wat groeit)
- kansen die de hype-wachter op 16 nov al zag: **drooglegging** (16 jan, 107 jaar; reservescript `new-york-1925`),
  **goudkoorts** (24 jan, 179 jaar; reservescript `goudkoorts-1849`), **mythologie / "complete history"** (groeit bij
  meerdere kanalen: "Founding Myths of Ancient Cities", "8 Hours of Random Mythology", "Complete History of the Wars of
  the Roses"), samen met stap 4
- compilaties blijven op ma 4 en ma 11 jan staan
Lever als tabel: datum | nu gepland | voorstel | waarom (bron uit de hype-wachter). **Leg dit voor aan de eigenaar en
verander geen enkele datum of map voordat hij akkoord geeft.** Pas daarna stap 5 (alleen de video's die blijven of
erbij komen ombouwen).

## Stap 5. Januari-scripts ombouwen naar de nieuwe opbouw (zoals japan in stap 1)
Deze staan nog in de oude opbouw (tweede account, 1-2 nov). De bewaker begint ± 14 dagen vooraf; `afspraken_check` houdt
oude scripts tegen, dus ze moeten **vóór ± 18 dec** om (eerste: philadelphia, za 2 jan). Op datumvolgorde, één map per
keer, zoveel als het verbruik toelaat (tussendoor `python tools/claude_gebruik.py`; nieuwe sessie als hij groot wordt):

| datum | map |
|---|---|
| za 2 jan | philadelphia-1776 |
| wo 6 jan | troje |
| za 9 jan | franklin-1845 |
| wo 13 jan | lewis-en-clark-1804 |
| za 16 jan | londen-1666 |
| wo 20 jan | tenochtitlan-1519 |
| za 23 jan | klooster-1150 |
| wo 27 jan | kasteel-1250 |
| za 30 jan | zijderoute-1271 |

**Eerst stap 4b (akkoord eigenaar op de januariplanning).** Per map: zelfde eisen als stap 1 (src-feiten, kort begin, abonneer.txt, eerste TOPIC = kern van de titel, ± 85 blokken,
≥ 13.500 woorden, thumbnail kenmerk, youtube-beschrijving, vier controles GOED). **Titel** nieuw volgens AFSPRAKEN:
de oude titels hebben nog "| <N> Hours of History for Sleep" (moet "| History for Sleep" worden, geen vraag).
Status `script-klaar (nieuwe opbouw, opbouw Sleepy <datum>, Claude)`. Februari volgt later in een eigen prompt.

## Stap 6 (eigenaar 17 nov, na reacties onder Mayflower): beroemde dingen kloppend + uitspraak
Reacties: "AI slop ... human voiced" en "check the correct pronunciation ... the image that introduces this video
about the Mayflower has very little resemblance to the vessel" (zie stories/CIJFERS-NULMETING.md).
- Vaste, historisch kloppende beschrijving voor beroemde schepen/gebouwen/voorwerpen (bv. `stories/<map>/kenmerken.txt`
  of een gedeelde lijst in tools/), die de beeldprompts en de thumbnail gebruiken en die beeldcheck controleert.
  Eerst voor de komende video's: blackbeard-1718 (Queen Anne's Revenge, 30 nov), scott-antarctica-1912 (Terra Nova),
  mary-celeste-1872, tower-of-london-1536 (White Tower), pearl-harbor-1941 (USS Arizona), kerst-loopgraven-1914.
- Uitspraaklijst voor de stem (OmniVoice): lastige namen fonetisch vervangen alleen in de tekst voor de stem
  (bv. Massasoit, Sekigahara, Tokugawa, Edo, Saint-Mars, Pignerol, Strasbourg). Testen met een korte proef.
- Nooit "human voiced" beweren. Kosten: geen (lokaal). Daarna één regel in ROUTINE-LOG.md.
