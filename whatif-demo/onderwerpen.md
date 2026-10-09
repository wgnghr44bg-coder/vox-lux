# What if – onderwerpen voor het automatische kanaal

Eén video per dag, van boven naar beneden. De geplande sessie pakt het eerste onderwerp met
status `gepland`, zet het na de upload op `geüpload <datum> <link>` en voegt zo nodig nieuwe
onderwerpen onderaan toe (nooit een onderwerp dat al in deze lijst staat).
Regels: elke dag een andere plek dan de vorige video; geen gewonden of lichamen in beeld;
alleen natuurkunde die klopt, verteld als "would".

## Al op het kanaal (IfScape3D, stand 2026-10-05) – geen dubbele video's

| Datum | Soort | Duur | Titel | Link |
|---|---|---|---|---|
| 2026-10-04 | Short | 1:27 | What if gravity suddenly doubled? | https://youtu.be/DE61_VUIuCw |
| 2026-10-04 | Short | 0:57 | What if the Sun came closer to Earth? | https://youtu.be/i2pChBmzRDs |
| 2026-10-05 | Short | 1:30 | What if Earth suddenly stopped spinning? | https://youtu.be/Bkd2gh_IlU0 |
| 2026-10-05 | Lang | 4:04 | What if the wind never stopped? (20 to 1,000 km/h) | https://youtu.be/1LNaLpmOcuM |
| 2026-10-07 | Lang | 8:28 | What if the Sun went out? | verwijderd door eigenaar (glitch op straat); wordt opnieuw gemaakt |

Regel (eigenaar, okt 2026): vóór het kiezen van een onderwerp de uploads van het kanaal ophalen (API: uploads-playlist
van kanaal `whatif`) en vergelijken met deze tabel en de lijst hieronder. Hetzelfde onderwerp nooit nog een keer, ook
niet als Short ↔ lange video, tenzij de eigenaar daarom vraagt. Lijkt een onderwerp erg op een bestaande video, kies
dan een duidelijk andere hoek of een ander onderwerp. Na elke upload deze tabel bijwerken.

## Al gebruikt als hoogtepunt (niet herhalen)

| Video | Hoogtepunt |
|---|---|
| Gravity suddenly doubled? | hangbrug zakt door en breekt, torens storten in (rivierstad) |
| The temperature dropped to −100°C? | rivier bevriest, brug barst (rivierstad) |
| Earth stopped spinning? | wind 1.037 mph door de straat aan zee |
| The wind never stopped? | straat → boulevard → rivierstad, brug bezwijkt |
| The Sun came closer to Earth? | sneeuw smelt, bosbranden (bergdorp) |
| The Sun went out? (v2, verwijderd) | 8:20 aftellen, het licht valt weg in de stad |
| The Sun went out? (v3, script eigenaar, in de maak) | tijdsprongen dag 0 → jaar 1.000: strand, straat, bergdorp (meer bevriest), bevroren kust |
| The Moon started falling? (in de maak) | haven loopt onder, schepen op straat (h1); climax: maan breekt op de Roche-grens tot een ring |

## Categorieën en bouwplan (eigenaar, okt 2026)

Doel: gevarieerde What if-video's over 14 categorieën. Nooit twee keer achter elkaar dezelfde categorie
(en ook niet dezelfde plek). Bakstenen: hooguit twee nieuwe per week (eigenaar, 7 okt 2026; was één), alleen
na de reset (zaterdag 12:00) en als `USAGE.md` er ruimte voor laat (eerst Sleep-runs + geplande video's + 10% buffer).

| # | Categorie | Voorbeeld | Kan nu? | Baksteen nodig |
|---|---|---|---|---|
| 1 | Earth & Nature | What if Earth stopped spinning? | ja | – |
| 2 | Space & Universe | What if the Sun suddenly disappeared? | ja voor maan/aarde (maan op schaal, ruimte-shot, getij, haven; okt 2026); ringen/meteoren volgen met Moon-video | Hemel (rest: ringen, meteoren) |
| 3 | Human Body | What if humans never needed sleep? | nee | Mensen dichtbij |
| 4 | Civilization & Society | What if everyone disappeared for 24 hours? | deels (Tijd klaar 9 okt; lege stad/park volgt) | Tijd & stad |
| 5 | Technology & AI | What if AI controlled the world? | nee | Tijd & stad (+ robots) |
| 6 | History | What if the Roman Empire never fell? | deels (Rome 80 n.Chr.: straat, Colosseum, Romeinen, menigte; nog niet: hypogeum, leeuw) | Oude plek (Rome) – plek `colosseum`, `ancient.js`, kracht `day` |
| 7 | Disasters & Survival | What if a supervolcano erupted tomorrow? | deels: aardbeving, natuurpark, sirene/wegblokkade klaar (9 okt); as, lava, bosbrand, lahar, aslucht volgen | Aarde beweegt (rest) |
| 8 | Animals & Evolution | What if dinosaurs never went extinct? | ja (hond, vos, hert, vogels + dino's, olifant, mammoet, oerwoud, hekken: 9 okt) | – (plan: long/dinosaurs/plan.md) |
| 9 | Science & Physics | What if gravity suddenly disappeared? | ja | – |
| 10 | Aliens & Mysteries | What if aliens contacted Earth tomorrow? | nee | Hemel (ufo) |
| 11 | Horror & Dark What If | What if nobody could die after midnight? | deels (nacht via Tijd) | Tijd & stad (nacht); spanning door sfeer, nooit gewonden/lichamen |
| 12 | Money & Economy | What if everyone received €1 million? | nee | Mensen dichtbij (+ drukte, prijzenteller) |
| 13 | Psychology & Human Behavior | What if everyone could read minds? | nee | Mensen dichtbij |
| 14 | Alternate Worlds | What if Earth had rings like Saturn? | nee | Hemel |

Bouwvolgorde bakstenen (± usage eenmalig): 1 Hemel – planeten, ringen, tweede zon, ufo (± 3%) →
2 Aarde beweegt – aardbeving, as, lava (± 4%) → 3 Tijd & stad – dag/nacht, lege stad, lichten uit, natuur groeit terug (± 4%) →
4 Mensen dichtbij – grotere poppetjes, interieur, uitdrukking (± 5%) → 5 Oude plek – Romeinse stad (± 4%) →
6 Dieren – dino's (± 5–6%).
Klaar (9 okt 2026): **Tijd** (`engine/time.js`, `TL.time`: dag/nacht, wolken, seizoenen, regen, sneeuw, gras, klimop, jonge bomen,
stof, roest, kapotte ramen; kracht `calm` = geen kracht) en **Dieren** (`engine/animals.js`, `TL.animals`: hond (met lege riem),
vos, hert, groepjes, vogels). Ook klaar: **Kleine dingen** (`engine/small.js`). Testbeelden: `topics/proef-tijd`, `topics/proef-dieren`, `topics/humans-1-street`. Is een baksteen klaar: zet "Kan nu?" op ja en voeg onderwerpen uit die categorie toe aan de lijst.
Klaar (9 okt 2026, dino-sessie): **Grote dieren** (`engine/big-animals.js`: T. rex, langnek, triceratops, raptor, pterosauriër, olifant,
mammoet, spitsmuis; lopen, kop draaien, brullen, kuddes), plek **oerwoud** (`places/prehistoric.js`), **Hekken** (`engine/fences.js`: omheining,
wachttoren, poort) en geluid (stappen, brullen, oerwoud). Testbeelden: `topics/dino-lineup`, `topics/dino-proef-park`, `topics/dino-c1-jungle`.

| # | What if… | Plek | Kracht / beeld | Status |
|---|---|---|---|---|
| 1 | Gravity suddenly doubled? | Rivierstad met hangbrug | Zwaartekracht: brug zakt door, torens storten recht in | geüpload 2026-10-04 https://youtu.be/DE61_VUIuCw (openbaar, straatversie van de eigenaar) |
| 2 | The Moon disappeared? | Haven bij nacht | Getij valt weg, schepen op het droge, donkere nachten | gepland |
| 3 | All the ice on Earth melted? | Strandboulevard | Zee stijgt meter voor meter | gepland |
| 4 | The Sun went out? | Bergdorp, straat, boulevard, rivierstad (lange video) | Steeds donkerder en kouder, alles bevriest | opnieuw in de maak (oude versie verwijderd 7 okt: glitch op straat); bron: ifscape3d-videos/2026-10-07-sun-went-out |
| 5 | A megaquake hit? | Buitenwijk met huizen | Golvende grond, scheuren, huizen schuiven | gepland |
| 6 | A world without internet? | Stad bij avond | Lichten gaan blok voor blok uit | gepland |
| 7 | The oceans disappeared? | Kustdorp met vuurtoren | Zeebodem valt droog, schepen liggen scheef | gepland |
| 8 | A 1 km asteroid hit the ocean? | Kustplaats met pier | Flits aan de horizon, tsunami die nadert | gepland |
| 9 | Gravity disappeared for 5 seconds? | Pretpark en plein | Alles zweeft omhoog, dan valt alles terug | gepland |
| 10 | Earth spun twice as fast? | Tropisch eiland | Kortere dagen, harde wind, zee bolt op | gepland |
| 11 | A solar storm hit Earth? | Noordelijke stad bij nacht | Noorderlicht, stroomnet valt uit | gepland |
| 12 | It rained for a whole year? | Rivierdorp in een dal | Water stijgt, straten worden rivieren | gepland |
| 13 | A Category 6 hurricane hit? | Kuststad met palmbomen | Orkaanwind en stormvloed | gepland |
| 14 | Earth warmed by 10 °C? | Woestijnstad | Hitte, zinderende lucht, droogvallende rivier | gepland |
| 15 | The Moon was twice as close? | Kustplaats met kliffen | Enorme getijden, grote maan | gepland |
| 16 | Earth lost its magnetic field? | Stad met radiotoren | Kompas draait, satellieten vallen uit, noorderlicht overal | gepland |
| 17 | Earth stopped orbiting the Sun? | Akkerland met boerderij | Kou die maand na maand toeneemt | gepland |
| 18 | A sinkhole opened under a city? | Winkelstraat (andere wijk) | Grond zakt weg, straat breekt open | gepland |
| 19 | The Gulf Stream stopped? | Grachtenstad | Strenge winters, bevroren grachten | gepland |
| 20 | Earth tilted on its side? | Weiland en dorp | Zon die niet meer ondergaat, extreme seizoenen | gepland |
| 21 | A giant dam broke? | Dal met stuwmeer en dorp | Vloedgolf door het dal | gepland |
| 22 | All volcanoes erupted at once? | Eilanddorp | Aswolken, lava in de verte, donkere lucht | gepland |
| 23 | A black hole passed the solar system? | Skyline bij nacht | Sterren buigen, getijden worden wild | gepland |
| 24 | Lightning never stopped? | Open vlakte met windmolens | Onweer zonder einde | gepland |
| 25 | Antarctica's ice slid into the sea? | Havenstad | Zeespiegel springt omhoog | gepland |
| 26 | A meteor shower lit up the night? | Camping in het bos | Vuurstrepen, inslagen in de verte | gepland |
| 27 | Earth had two suns? | Woestijn met rotsbogen | Dubbele schaduwen, geen echte nacht | gepland |
| 28 | Earth stopped spinning? | Stadsstraat aan zee | Wind van 1,037 mph | geüpload 2026-10-05 https://youtu.be/Bkd2gh_IlU0 |
| 29 | Yellowstone erupted? | Natuurpark met bizons | Aswolk en asregen | wordt de lange video "What if a supervolcano erupted?" (plan: long/supervolcano/plan.md) |
| 30 | The air got twice as thick? | Bergweg met uitzichtpunt | Zware lucht, vogels en vliegtuigen anders | gepland |
| 31 | The Sun came closer to Earth? | Besneeuwd bergdorp | Hitte: zon groter en feller, sneeuw smelt, bosbranden | geüpload 2026-10-04 https://youtu.be/i2pChBmzRDs (openbaar, ondertitelde versie van de eigenaar) |
| 32 | The temperature dropped to −100°C? | Rivierstad met hangbrug | Kou: rivier bevriest, rijp, adem bevriest, brug barst | geüpload 2026-10-06 https://youtu.be/0Kvcuv5-3EQ (openbaar, Short, door eigenaar aangeleverd; staat ook al op TikTok) |
| 33 | The wind never stopped? (lange video 16:9) | Straat → boulevard → rivierstad | Wind 20 → 1.000 km/u, brug bezwijkt | geüpload 2026-10-05 https://youtu.be/1LNaLpmOcuM (openbaar, 4:04) |
| 35 | You were trapped inside the Colosseum for one day? (lange video 16:9, History) | Rome → Colosseum → hypogeum → nacht | Tijd van de dag DAWN → NIGHT, menigte, velarium, paniek (geen geweld in beeld) | hoofdstuk 1 testbeelden, wacht op akkoord; plan: long/colosseum/plan.md |
| 34 | Every human disappeared? (lange video 16:9, script eigenaar, max. 25 jaar) | Straat → rivierstad → park/buitenwijk → straat | Mensen weg, lichten uit, natuur neemt de stad terug (bakstenen Tijd, Dieren, park) | gepland na de Sun-video; plan: long/humans-disappeared/plan.md |
| 35 | A supervolcano erupted? (lange video 16:9) | Natuurpark → dal → stad → Europese kust | Aardbeving, uitbarsting, as, vulkanische winter (15 → 8.000 km) | hoofdstuk 1 als proef (9 okt); plan: long/supervolcano/plan.md |
| 36 | The Moon started falling toward Earth? (lange video 16:9) | Haven → (stad/bergen) → ruimte | Getij steeds hoger, maan groter, Roche-grens 18.000 km: maan breekt tot ring, meteoren | in de maak (proef hoofdstuk 1: topics/moon-c1-harbor); let op: #2 en #15 lijken hierop (getij/haven) |
| 37 | Dinosaurs never went extinct? (lange video 16:9) | Oerwoud → dinopark → storm → stad bij nacht | Dino's komen steeds dichterbij (1 km → 3 m) | in de maak; plan: long/dinosaurs/plan.md |
| 38 | A zoo's animals all escaped? | Dierentuin (hekken, poort) → stad | Olifanten en giraffen in de straat, iedereen binnen | gepland (bakstenen Dieren, Hekken) |
| 39 | Mammoths came back? | Toendra/bergdorp in de winter | Kudde mammoeten door het dorp, sneeuw | gepland (Grote dieren: mammoth) |
