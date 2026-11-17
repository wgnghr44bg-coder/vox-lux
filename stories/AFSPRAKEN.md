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
- **Eerste onderwerp = de kern van de titel (15 nov, YouTube Studio):** bij Titanic haakten kijkers af toen het verhaal
  na het begin naar de scheepswerf in Belfast ging, terwijl ze kwamen voor het leven aan boord. Dus het eerste TOPIC gaat
  over wat de titel belooft (aan boord, kerstavond in de loopgraven, het oogstfeest); achtergrond komt daarna.
- **Abonneerzin:** niet in het begin maar in `src-feiten/abonneer.txt`; klinkt na feitje 2 (rond minuut 3). Elke video
  anders verwoord, maar even lang: 15-22 woorden (eigenaar 15 nov, zoals Gettysburg: 18 woorden).
- **Slot:** terugblik, "another … story … on the screen", kort abonneren, als laatste "Sleep well, and good night."
- Controles: `script_leesbaar` (GOED + TOON GOED), `check_afwisseling`, `script_check` (SCRIPT GOED).

## Beelden
- **Elk beeld een eigen plek en eigen licht (17 nov 2026, Dallas: "vaak dezelfde afbeelding"):** `src-feiten/stijl.txt`
  noemt alleen plaats + tijd en de filmlook. Nooit een vaste buitenscène (straat, gebouwen, lucht, avondlicht) in de
  stijlzin: die overstemt de beschrijving en dan wordt een diner, kantoor of woonkamer steeds dezelfde straat.
  `tools/bouw_feiten.py` kort de stijlzin daarom zelf in. Beschrijf binnen-scènes als binnen, en wissel af in plek,
  afstand (wijd, half, dichtbij) en licht (ochtend, middag, avond, lamplicht).

## Titel
- Concreet met plaats en/of jaartal, **geen vraag**, altijd `| History for Sleep` erachter, geen uren.
- Vormen: "Life in <plaats>, <jaar>", "Life Aboard <schip>, <jaar>", "How <mensen> Survived <iets>", "<Gebeurtenis>, <jaar>".
  (CTR 14 nov: Titanic/Mayflower 4,8%, Vikings 7,4%; vraagtitels WW2 0,7%, Babylon 2,5%.)

## Thumbnail
- Stijl zoals Babylon: maanlogo "SLEEP ARCHIVES", groot wit onderwerp, geel jaartal, links.
- Rechts één scène waaraan je meteen ziet waar de video over gaat: het kenmerkende beeld groot, mét mensen uit die tijd
  die doen wat er toen gebeurde. Nooit een losse willekeurige vrouw. Niets moderns, geen zwevende voorwerpen.
- In `planning.txt` een regel `thumbnail kenmerk: …`; de keten maakt hem met `tools/thumbnail_v3.py`.

## Afspeellijsten
- De keten zet elke nieuwe video automatisch in "History for Sleep – Full Documentaries" en in de lijst van zijn soort
  (`soort` in planning.txt): ramp, oudheid, middeleeuwen, mysterie, oorlog, verlaten, reis. Geen nieuwe lijsten
  (eigenaar 28 okt). Afspeellijsten laten YouTube na een video automatisch de volgende spelen: meer kijktijd 's nachts.

## Planning
- Ma, wo en za 21:00 (NL). Zo dat het beste is voor het kanaal en mee met de hype: hype-wachter (elke dag 08:30),
  jaardagen, en onderwerpen waar kijkers op zoeken (YouTube Studio). Datums alleen veranderen met de eigenaar.

## Altijd eerst vragen
- Alles wat geld kost, en alles wat iets verwijdert (ook video's op YouTube). Video's niet opnieuw uploaden of
  verwijderen: titel en thumbnail kunnen in YouTube Studio worden aangepast zonder views te verliezen.

## Tweede kanaal: Noir Traces (was Altena; vast sinds 17 nov 2026)
- Kanaal **Noir Traces** (naam op YouTube NOIRTRACES, eerst Altena; UC_6p9gp5aBf-eHY5VmJEw4w): bodycam, verhoren, arrestaties (kanalen/bodycam/PLAN.md). Beschrijving + trefwoorden gezet 17 nov. Sleutelnaam blijft "altena". staat op een **ander e-mailadres** dan Sleep Archives. Gekoppeld met
  alle rechten (uploaden, aanpassen, statistieken) via `python tools/youtube_koppel.py altena --schrijf`
  (zelfde Google-app "Vox Lux Uploader"; redirect `http://127.0.0.1:8765` staat in de Cloud Console).
- Sleutel staat op de pc in `~/.yt-altena.json` (**buiten git**, nooit committen).
- Kiezen: zet `YT_KANAAL=altena`, dan gebruikt `tools/youtube_upload.access_token()` (en alles wat die gebruikt)
  Altena. Zonder `YT_KANAAL` blijft alles op Sleep Archives. Controle: `python tools/youtube_koppel.py altena --test`.
- Stand 17 nov: 4 abonnees, 0 video's, beschrijving "Njoy Life". **Niche en naam kiest de eigenaar nog**; advies: een
  andere slaapniche dan geschiedenis (mythologie, natuur/heelal) zodat de kanalen niet met elkaar concurreren.
- **Let op vóór de eerste Altena-upload:** `tools/vervang_video.py` controleert dat een upload op "Sleep Archives"
  staat en verwijdert hem anders meteen. Die controle eerst kanaal-afhankelijk maken (naam uit `YT_KANAAL`).
- Kanaalnaam en profielfoto kan alleen de eigenaar in Studio veranderen; Claude maakt de afbeeldingen.
