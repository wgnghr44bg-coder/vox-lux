# Vaste afspraken voor elke video (eigenaar, bijgewerkt 14 nov 2026)

Elke sessie, elk account en de keten op de pc houden zich hieraan. `tools/afspraken_check.py stories/<map>` controleert
dit; `tools/routine_lokaal.py` draait die controle vóór elke video en begint niet als er iets niet klopt.

## Geluid
- **Stem:** de eigen stem van de eigenaar ('Yesss', OmniVoice), snelheid 0.9, instellingen uit `audio_engine/B1.json`.
  Geen klonen van andermans stem. `stories/<map>/stem.json` mag alleen afwijken met `eigenaar_afwijking`.
- **Achtergrond:** open haard + B-effect (432 Hz), 10 LUFS onder de stem (`B1.json` → `achtergrond`, geluiden in
  `~/vox-lux-geluiden`, alleen op de pc). Geen oude W3-muziek. Ook proeven (`tools/b1_proef.py`) gebruiken deze achtergrond.

## Script (opbouw Sleepy History)
- Kalme gids, verleden tijd, IMG/HEAD/BODY-blokken (feit, uitleg, bewijs, nuance, slotgedachte), geen BRIDGE.
- Geen jij-vorm, geen vragen, geen "I", geen verzonnen hoofdpersonen, alleen kloppende feiten. Makkelijk Engels.
- **Begin (15 nov, eigenaar: "veel korter, rest your shoulders blah blah duurt te lang"):** 25-70 woorden, 2-3 zinnen die
  meteen het verhaal neerzetten (plaats + tijd + het beeld van de thumbnail). Geen "Let's begin" (15 nov). GEEN ontspanningszinnen
  (rest your shoulders, breathe, let your …), geen "In this story we will …".
- **Abonneerzin:** niet in het begin maar in `src-feiten/abonneer.txt`; klinkt na feitje 2 (rond minuut 3).
- **Slot:** terugblik, "another … story … on the screen", kort abonneren, als laatste "Sleep well, and good night."
- Controles: `script_leesbaar` (GOED + TOON GOED), `check_afwisseling`, `script_check` (SCRIPT GOED).

## Titel
- Concreet met plaats en/of jaartal, **geen vraag**, altijd `| History for Sleep` erachter, geen uren.
- Vormen: "Life in <plaats>, <jaar>", "Life Aboard <schip>, <jaar>", "How <mensen> Survived <iets>", "<Gebeurtenis>, <jaar>".
  (CTR 14 nov: Titanic/Mayflower 4,8%, Vikings 7,4%; vraagtitels WW2 0,7%, Babylon 2,5%.)

## Thumbnail
- Stijl zoals Babylon: maanlogo "SLEEP ARCHIVES", groot wit onderwerp, geel jaartal, links.
- Rechts één scène waaraan je meteen ziet waar de video over gaat: het kenmerkende beeld groot, mét mensen uit die tijd
  die doen wat er toen gebeurde. Nooit een losse willekeurige vrouw. Niets moderns, geen zwevende voorwerpen.
- In `planning.txt` een regel `thumbnail kenmerk: …`; de keten maakt hem met `tools/thumbnail_v3.py`.

## Planning
- Ma, wo en za 21:00 (NL). Zo dat het beste is voor het kanaal en mee met de hype: hype-wachter (elke dag 08:30),
  jaardagen, en onderwerpen waar kijkers op zoeken (YouTube Studio). Datums alleen veranderen met de eigenaar.

## Altijd eerst vragen
- Alles wat geld kost, en alles wat iets verwijdert (ook video's op YouTube). Video's niet opnieuw uploaden of
  verwijderen: titel en thumbnail kunnen in YouTube Studio worden aangepast zonder views te verliezen.
