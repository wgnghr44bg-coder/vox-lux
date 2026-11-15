# Scripts voor eind november en december (eigenaar 14 nov 2026)

Start: "Lees stories/PROMPT-SCRIPTS-DEC.md en voer het uit." Werk af zonder te vragen. **Alleen tekst**: geen beelden,
geen stem, geen video, niets wat geld kost. Eén map per keer, alleen jouw map aanraken. Vóór elke map `git pull` en kijk
of hij al klaar is (status bevat "opbouw Sleepy"): dan overslaan.

**Alle vaste afspraken staan samen in `stories/AFSPRAKEN.md`** (gecontroleerd door `tools/afspraken_check.py`).

## Vaste afspraken (eigenaar 14 nov 2026)
- **Planning = het beste voor het kanaal en mee met de hype.** De planning hieronder is daarop gemaakt (hype-wachter
  `tools/hype_wacht.py`, elke dag 08:30, uitkomst op de website en in `stories/HYPE-SIGNAAL.md`). Verander geen datums
  zonder de eigenaar; vrije plekken zijn bewust open gelaten voor nieuwe hype.
- **Thumbnail (VAST, elke video):** stijl zoals Babylon (maanlogo, groot wit onderwerp, geel jaartal, links) en rechts
  één scène waaraan je meteen ziet waar de video over gaat: het kenmerkende beeld groot, mét mensen uit die tijd die doen
  wat er toen gebeurde. Nooit een losse willekeurige vrouw. Zet in planning.txt een regel
  `thumbnail kenmerk: <beeld + mensen + wat er gebeurt>`. Code: `tools/thumbnail_v3.py`, `stories/thumbnails-v3.json`.
- **Titel (VAST, eigenaar 14 nov 2026, op basis van CTR-cijfers):** concreet, met plaats en/of jaartal, geen vraag.
  Werkt: "Life Aboard the Titanic, April 1912" (4,8%), "How Vikings Survived the Long Dark Winter" (7,4%).
  Werkt niet: "What Was Everyday Life Like During WW2?" (0,7%), "Why Was Babylon the Greatest City on Earth?" (2,5%).
  Vormen: "Life in <plaats>, <jaar>", "Life Aboard <schip>, <jaar>", "How <mensen> Survived <iets>", "<Gebeurtenis>, <jaar>".
  Altijd met " | History for Sleep" erachter. Titelsoort hoeft niet meer af te wisselen.
- **Begin (VAST, eigenaar 14 nov 2026; in de eerste minuut haakt ruim de helft af):** eerste zin meteen concreet
  (plaats + tijd + beeld), geen inleiding. De abonneerzin NIET in begin.txt maar in `src-feiten/abonneer.txt`; die
  klinkt na het tweede feitje (rond minuut 3). begin.txt 25-70 woorden: 2-3 zinnen verhaal, geen "Let's begin";
  GEEN ontspanningszinnen (eigenaar 15 nov: "veel korter").
- **Script-opbouw:** precies zoals `stories/PROMPT-OMBOUW-SLEEPY.md` (kalme gids, IMG/HEAD/BODY, geen BRIDGE, geen
  jij-vorm, geen vragen, geen "I", geen verzonnen hoofdpersonen, kort begin en slot). Controles en afronden ook daar.

## Planning en wat er per script nog moet

| datum | map | wat | wie |
|---|---|---|---|
| ma 23 nov | `ijstijd-20000-vc` | **nieuw script** (IJstijd-hype bij 3 kanalen) | hoofdsessie (14 nov) |
| ma 30 nov | `blackbeard-1718` | ombouwen naar Sleepy | hoofdsessie (14 nov) |
| wo 2 dec | `alchemie-steen-der-wijzen` | **nieuw script** (hype Philosopher's Stone) | hoofdsessie (14 nov) |
| wo 9 dec | `rome-44-vc` | KLAAR (15 nov, hoofdsessie) | - |
| za 12 dec | `zwarte-dood-1348` | KLAAR (15 nov, hoofdsessie) | - |
| ma 14 dec | `scott-antarctica-1912` | KLAAR (15 nov, hoofdsessie) | - |
| za 19 dec | `londen-kerst-1843` | ombouwen uit de oude opbouw (datum = 183 jaar A Christmas Carol) | ander account |
| wo 23 dec | `bethlehem` | ombouwen uit de oude opbouw | ander account |
| wo 16 dec | `man-ijzeren-masker-1703` | KLAAR (15 nov, hoofdsessie, nieuw geschreven) | - |
| ma 21 dec | `mary-celeste-1872` | KLAAR (15 nov, hoofdsessie, nieuw geschreven) | - |
| ma 28 dec | `dansplaag-1518` | **nieuw script** (gezocht: dancing plague) | volgende vrije sessie |
| wo 30 dec | `tower-of-london-1536` | **nieuw script** (gezocht: tower of london) | volgende vrije sessie |
| za 26 dec | `japan-1600` | ombouwen uit de oude opbouw (ninja-hype) | ander account |

Al klaar (niets meer aan doen): crisis-1933, gettysburg-1863, dallas-1963, thanksgiving-1621, boeren-winter-1300,
kerst-loopgraven-1914, pearl-harbor-1941. Vrije plekken in december zijn nu gevuld met onderwerpen waar kijkers op zoeken (YouTube Studio, 14 nov).

## Oude opbouw (londen, bethlehem, japan): eerst omzetten
Heeft de map nog geen `src-feiten/`, maak die dan zoals bij `stories/thanksgiving-1621/`: `stijl.txt` (één regel
beeldstijl), `begin.txt`, `deel1.txt`-`deel3.txt` met `TOPIC:` en blokken `IMG: <slug> | <beeldbeschrijving>`,
`HEAD:`, `BODY:` gescheiden door `===`, en `slot.txt`; kopieer `bouw_script.py`, `maak_tijden.py`, `maak_motion.py` uit
thanksgiving-1621. Ongeveer 85-90 blokken in 12-13 onderwerpen (TOPIC), ± 15.000 woorden. Beeldbeschrijvingen: alleen
wat er in die tijd bestond, geen tekst/letters. `tools/oud_naar_feiten.py` kan helpen bij het omzetten.

## Nieuw script (ijstijd, alchemie)
Zelfde opbouw als hierboven. Ook `youtube-beschrijving.txt` (2 zinnen over de video, het vaste stukje "A calm,
slow-paced history documentary for sleep…", "Chapters" met alle TOPIC-titels, 15 hashtags), zoals thanksgiving-1621.

## Na elk script
Controles (allemaal goed): `script_leesbaar` (MAKKELIJK/GOED + TOON GOED), `check_afwisseling` (AFWISSELING GOED),
`script_check --zonder-model` (SCRIPT GOED). Status: `script-klaar (nieuwe opbouw, opbouw Sleepy <datum>, Claude)`.
Commit alleen jouw map + één regel in `stories/ROUTINE-LOG.md`, `git pull --rebase`, push. De website
(https://wgnghr44bg-coder.github.io/vox-lux/status/) leest de planning en het logboek vanzelf.
