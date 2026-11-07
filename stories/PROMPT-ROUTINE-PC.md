# Sleep Archives – automatische routine op de pc

De eigenaar wil dat alles automatisch gebeurt (27 okt 2026): **3 video's per week, maandag, woensdag en
zaterdag 21:00 NL-tijd** (eigenaar 4 nov 2026; maandag vanaf 16 nov 2026), volgens het Titanic-recept
(stories/ONDERWERPEN.md). Geen Shorts. Deze prompt draait op de pc van de eigenaar (Windows Taakplanner
start `claude -p` op **zondag, dinsdag en donderdag 09:00**; elke run maakt één video),
want ComfyUI, de stem en het videobestand staan alleen daar. Niemand kijkt mee: vraag niets,
werk alles af.

1. `git checkout main && git pull`. Start ComfyUI als `http://127.0.0.1:8188` niet antwoordt en
   wacht tot hij klaar is.
   **Eerst: is een vorige run blijven hangen?** Staat er een `stories/*/planning.txt` op `status   bezig (..., routine)`
   zonder link, ouder dan 1 dag, en is die video nog niet op YouTube? Maak die dan eerst af vanaf de stap waar hij
   bleef (de bestanden staan nog in deze map) in plaats van een nieuwe te beginnen (Tombstone, 2 nov 2026).
   **Welke plek?** Elke run vult de **eerstvolgende open plek**: maandag, woensdag of zaterdag 21:00, minstens
   2 dagen na vandaag, waarvoor nog geen video op YouTube staat en geen planning.txt op `bezig` of `klaar` staat
   (3 per week, eigenaar 4 nov 2026). Heeft een `script-klaar` planning.txt precies die datum, maak die. Is de plek
   vrij (elke maandag, en de "vrij"-plekken in ONDERWERPEN.md), kies dan hype of reservescript (zie hieronder).
   Pak nooit een script met een latere datum zolang er een eerdere plek open is.
   **Daarna: ligt er een script klaar?** (eigenaar, 1 nov 2026: een tweede Claude-account schrijft de scripts
   vooruit, zie `stories/PROMPT-SCRIPT-VOORUIT.md`.) Zoek op main naar `stories/*/planning.txt` met
   `status   script-klaar`. Neem daarvan die met de vroegste `datum` die minstens 2 dagen na vandaag ligt.
   - Dat is je video. Sla stap 2 en 3 over: onderwerp, datum, titel, thumbnail en soort staan in die planning.txt.
   - Schrijf geen nieuw script. Draai `python stories/<map>/bouw_script.py` en lees het script één keer
     na volgens stap 2 van PROMPT-NIEUWE-VIDEO.md (begin, abonneer-zin, einde, ± 20.000 woorden, opbouw zoals hieronder bij "Script-opbouw",
     ± 90 beelden). Herstel kleine fouten zelf.
   - Zet de status op `bezig (<datum>, routine)` (commit + push), zodat een volgende run hem niet ook pakt.
     Na de upload wordt het `klaar` met de link (stap 6).
   - Een `datum` uit zo'n planning.txt telt als bezet. Een hype verschuift een klaar script niet.
   Is er geen klaar script, ga dan gewoon verder met stap 2.
   **Reservescripts** (eigenaar, 3 nov 2026): planning.txt met `datum    reserve (geen datum)` en
   `status   script-klaar` zijn klaar geschreven voor de vrije plekken ("vrij, de routine kiest het onderwerp op hype").
   Is de eerstvolgende plek (minstens 2 dagen na vandaag) zo'n vrije plek en vindt stap 2 daar geen duidelijke hype
   (wereldberoemd, ≥ 10.000 views per dag, nog niet bij ons), neem dan het eerste reservescript (op mapnaam),
   zet zijn `datum` op die plek en ga verder zoals bij een klaar script hierboven. Is er wel een hype, maak dan de hype.
2. **Onderwerp** volgens stap 0 van het Titanic-recept in stories/ONDERWERPEN.md: nooit een
   onderwerp dat al op Sleep Archives staat (`python tools/sleep_trends.py --check ...` toont
   "AL GEMAAKT") of al in een stories/*/planning.txt op main of origin/claude/* staat; kies van de
   rest het onderwerp met de meeste kans (meeste views van bestaande slaapvideo's, of nu hard
   groeiend bij een groot kanaal volgens `python tools/sleep_trends.py`). Is er geen duidelijke
   winnaar, neem dan het eerste vrije onderwerp uit "Eerst deze".
   **Planning bijsturen op hype (eigenaar, 28 okt 2026)**: neem standaard het onderwerp dat in de
   "Nieuwe planning" in ONDERWERPEN.md op die datum staat. Draai eerst `python tools/sleep_trends.py --days 30`:
   groeit er nu een **wereldberoemd** onderwerp hard bij een groot kanaal (≥ 10.000 views per dag) dat
   nog niet bij ons staat, maak dat dan in plaats van het geplande, en schuif het geplande en de rest
   één plek op in de lijst (commit + push). **Nooit** vervangen of verschuiven: een onderwerp met een
   vaste datum (jubileum, feestdag, filmpremière, bv. Kennedy 21 nov, Pearl Harbor 28 nov, kerst);
   schuif dan de flexibele onderwerpen eromheen. Zet in ROUTINE-LOG.md welke hype je zag en wat je koos.
3. **Datum**: de eerste vrije maandag, woensdag of zaterdag 21:00, minstens 2 dagen na vandaag. Zet
   `stories/<map>/planning.txt` meteen op main (commit + push), zodat een volgende run hem ziet.
4. **Maken** volgens stories/PROMPT-NIEUWE-VIDEO.md en stories/YOUTUBE-STANDAARD.md, met deze
   afwijkingen:
   - **Script-opbouw: precies volgens `stories/OPBOUW.md`** (eigenaar 7 nov 2026: "zoals je zegt houden we het zo";
     het recept van de grote slaapkanalen). Kort: vraag-titel; begin van ± 2 min zonder "Tonight"/"Hello" (opening in
     de jij-vorm, grote vraag, zachte abonneer-zin, reactievraag "waar luister je vandaan", settle in); midden met
     8-12 onderwerpen (TOPIC + BRIDGE) van elk 6-10 feitjes met een eigen beeld; einde dat uitdooft naar een slaapbeeld,
     volgende-video-zin ("another ... story/video ... on the screen", voor de QC) en "Sleep well, and good night."
     Wissel de soort opening en titel af (zie OPBOUW.md, "Afwisseling"). Bestanden: `src-feiten/begin.txt`,
     `deel*.txt` (TOPIC/BRIDGE- en IMG/HEAD/BODY-blokken), `slot.txt`; bouw_script.py zoals stories/ww2-facts.
     In maak_motion.py staat `"intro": False, "slot": False` (geen Sleep Archives-beeld); hoofdstukken = de TOPICs.
     Ook een klaar of reservescript eerst zo ombouwen (zelfde onderwerp en feiten, nieuwe opbouw), dan pas beelden en stem.
     Lengte: ± 17.000-20.000 woorden (met de B1-stem ± 2,5-3 uur).
   - Beelden via comfy (`tools/comfy/comfy_batch.py`, tools/comfy/README.md). **Nooit xAI of iets
     anders dat geld kost.**
   - **Elk beeld nakijken op dingen die er toen nog niet waren** (Tombstone 3 nov 2026: 60 van de 90 beelden hadden
     auto's, campers, moderne huizen, straatlantaarns of plafondventilatoren). Maak overzichtsvellen (12 per vel) en
     bekijk ze allemaal vóór de montage. Wat helpt in de prompt: beschrijf wat er wél is ("only horses, wagons, wooden
     false-front buildings, dirt roads; any distance shows only open desert") en bij binnenscènes "an indoor scene,
     enclosed by walls, a plain ceiling of bare wooden planks with one oil lamp". Schrijf nooit "no ceiling fans" of
     "no cars": dan tekent het model ze juist. Afgekeurde beelden naar `<map>/afgekeurd/` en opnieuw maken.
   - **Stem en muziek: Audio Engine** (eigenaar 6 nov 2026; vervangt Slaap 3 en de oude 432-muziek met regen).
     **Naam: "B1-stem met achtergrondmuziek" (kort "B1")** (eigenaar 7 nov 2026) = stem `narrator-e` + koor `referentie`.
     **Stem: `narrator-e`** (eigenaar 7 nov 2026, proef B1: "Ik wil deze als standaard stem"): een ontworpen oudere
     Britse man (OmniVoice "male, elderly, moderate pitch, british accent", seed 27; niemand gekloond), rustiger en
     warmer dan narrator-b. Zet `stories/<map>/stem.json` neer als kopie van stories/ww2-facts/stem.json:
     `engine_voice` narrator-e, `speed` 0.54, `seed` 7, `pauze` 1.4, `muziek_onder` 11, `muziek_seed` 1939 (koor 11 LUFS onder de stem, elke video dezelfde akkoordenreeks als proef A0; eigenaar 7 nov avond: "B1 zoals hij was", de rustigere versie met tempo 0.92 is afgewezen), `klank` warme EQ
     (`highpass=f=60,lowshelf=f=180:g=3,highshelf=f=4500:g=-4,deesser=i=0.3,acompressor=...`). Stem:
     `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_stem.py <map>` (zelfde voice.mp3 + voice-times.tsv
     als vroeger, ± 110 woorden/min). Dan
     `python tools/add_pauses.py --niet-zwaarder --kort <map>` en `python tools/zachte_stem.py <map>` (leest de klank
     uit stem.json). **Muziek**: `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/engine_muziek.py <map>`
     (zacht koor met strijkers in 432 Hz, elke 7 s een ander akkoord, geen regen, al gedukt onder de stem); die
     schrijft video/muziek432.wav en video/muziek-db.txt. Gebruik dat getal als `--muziek-db` bij make_video,
     stil_tikjes, check_video en qc_video (niet meer -26). herstel_zinnen.py gebruikt vanzelf de stem uit stem.json.
     Uitleg en interface: audio_engine/README.md.
     (ffmpeg `ebur128`). Meldt check_video "stem blijft hangen" (bij OmniVoice: adem-tikjes vóór een zin), draai dan
     `python tools/stil_tikjes.py <map> <video>-motion.mp4 <video>-schoon.mp4` en controleer opnieuw.
     **Tekstcontrole (verplicht, eigenaar 31 okt 2026: "Tonight we we are going")**: draai
     `C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/check_stem_tekst.py <map> --wav <map>/video/stem-met-pauzes-voor-tikjes.wav`
     (Whisper zin voor zin, letterlijk: dubbele, weggevallen en hangende woorden; geeft de zinnummers). Die zinnen
     opnieuw inspreken met `tools/herstel_zinnen.py <map> <nrs>` (zelfde plek,
     geen nieuwe montage), dan stil_tikjes, check_video en check_stem_tekst (op de schone stem) opnieuw. Pas bij TEKST GOED uploaden. Zet hem als laatste stap op -14 LUFS met `python tools/eind_volume.py <video>.mp4 <video>-14.mp4`
     (eigenaar, 31 okt 2026: "net zo hard als de meeste sleep history video's"). **Daarna 16mm-look** (eigenaar 3 nov 2026,
     voor alle lange video's): `python tools/film16.py <video>-14.mp4 <video>-16mm.mp4` (± 80 min); draai qc_video op
     het 16mm-bestand en upload die versie. Niets aan de look veranderen (geen flikkeren, geen lichtvlek, geen diepte). Met stem narrator-e
     (± 110 woorden/min) geeft ± 20.000 woorden ± 3 uur.
   - Pc-paden (test 27 okt 2026): De beelden-workflow is `tools/comfy/zimage_api.json`
     (staat alleen op de pc, niet in git; ontbreekt hij, kijk dan in de hoofdmap van de repo).
   - Titel (eigenaar 7 nov 2026, "zonder uren"): een **vraag** zoals Sleepy History, eindigend op ` | History for Sleep`,
     zonder aantal uren, bv. "What Was Life Really Like in Tombstone? | History for Sleep". Bekende naam erin, ± 50-70 tekens.
     Staat er in planning.txt nog een oude titel (met `<N> Hours`), maak er dan zo'n vraag-titel van.
   - **Thumbnail: automatisch** (eigenaar, 1 nov 2026: "nu kun je ze automatisch instellen bij elke nieuwe video").
     Staat er in planning.txt `thumbnail gekozen door eigenaar: <bestand>`, gebruik dan precies dat bestand.
     Anders maak je hem zelf, zonder te vragen, volgens YOUTUBE-STANDAARD.md (Thumbnail):
     - Maak via comfy (gratis) 3 beelden van het **kenmerkende** onderwerp uit de `thumbnail`-regel in planning.txt,
       groot rechts in beeld, links onderin rustig en donkerder. Zet in de prompt "no text, no letters".
     - Zet er de tekst op met `tools/make_thumbnail.py <beeld> thumbnail.jpg --hook "<titelwoorden>" --title "<plaats of maand  ·  jaar>"`.
       Gebruik nooit uren.
     - **Bekijk alle 3** en kies de beste. Valt een beeld af, dan vervalt hij: rare letters of een fout bord
       ("TOMBE 881"), een vreemd gevormd voorwerp, tekst over een gezicht, of een beeld dat lijkt op een van de
       laatste 3 thumbnails van het kanaal.
       Zijn ze alle 3 slecht, maak er dan 3 nieuwe.
     - Voorbeelden die de eigenaar koos: `stories/hindenburg/thumbnail-gekozen.jpg` (luchtschip met mensen op de pier),
       `stories/tombstone-1881/thumbnail-gekozen.jpg` (westernstraat in de avond),
       `stories/egypte-toetanchamon/thumbnail-gekozen.jpg` (gouden masker).
   - **Abonneer-zin** in het begin (± 1 min, na de grote vraag, zie OPBOUW.md), kort en rustig, zonder druk, per video
     anders verwoord; het einde vraagt nog één keer kort.
   - **Avondeffect v2** (eigenaar, 30 okt 2026): `tools/make_video.py` maakt het beeld standaard iets donkerder
     met zachte donkere randen, kleuren gewoon (geen gele lucht). Niet uitzetten; de thumbnail blijft helder.
     Vraag in de beeldprompts liefst om avondlicht (kampvuur, lamp, schemering).
   - **Geen ondertitels** (eigenaar, 28 okt 2026): niet in beeld en niet als ondertitelbestand op YouTube.
   - Kwaliteitscontrole zoals in de prompt (`tools/qc_video.py`); fouten zelf herstellen.
5. **Uploaden**: privé met publishAt op de geplande tijd naar **Sleep Archives**
   (`YT_REFRESH_TOKEN`, `tools/youtube_upload.py`), met titel, beschrijving, tags en thumbnail.
   Zet hem meteen in de afspeellijsten: `python tools/youtube_playlist.py --soort <soort> <id>`
   (zet hem ook in "Full Documentaries"); hooguit 2 soorten, bv. reizen `reis`, rampen `ramp`,
   oorlog `oorlog`. **Nooit nieuwe afspeellijsten maken** (eigenaar). Controleer dat hij erin staat. Controleer via de API dat `snippet.channelTitle` "Sleep Archives" is; anders
   meteen verwijderen en stoppen.
6. Zet de link en de kosten (€0) in planning.txt, commit en push naar main.
   **Wacht eerst tot YouTube klaar is met verwerken** (eigenaar, 6 nov 2026; Egypte bleef 8+ uur "processing"
   terwijl de bestanden al weg waren): `python tools/wacht_verwerkt.py <id> --uren 12`. Bij KLAAR: opruimen.
   Bij MISLUKT: verwijder de video op YouTube (na controle kanaal, privé en titel), upload het bestand opnieuw
   (stap 5) en wacht weer. Bij NOG BEZIG: niet opruimen; laat de bestanden staan en schrijf het in
   `stories/ROUTINE-LOG.md`, dan kijkt een volgende sessie ernaar.
   **Opruimen** (eigenaar, 31 okt 2026: "doe dit zo elke keer"): staat de video gecontroleerd op YouTube
   (juiste kanaal, thumbnail, afspeellijsten) én is hij klaar met verwerken, verwijder dan de grote bestanden van die video op de pc:
   alle `*.mp4` en `*.wav` in `stories/<map>/video/` (ook `clips/`). Beelden, script, stem-mp3 en tekstbestanden blijven.
   Vervang je een oude video op YouTube door een nieuwe, verwijder dan ook het oude bestand. Nooit iets anders
   (games, eigen opnames) aanraken.
7. Lukt iets niet (ComfyUI start niet, sleutel ontbreekt, schijf vol), verwijder dan je
   planning.txt van main zodat de volgende run de datum weer kan pakken, en schrijf in
   `stories/ROUTINE-LOG.md` (op main) in simpel Nederlands wat er misging en wat de eigenaar moet doen.
