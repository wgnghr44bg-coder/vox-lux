# Onderwerpen voor lange video's

Een nieuwe sessie zonder eigen onderwerp pakt het **eerste onderwerp uit "Nog te maken"
dat nog niet gebruikt is**. Gebruikt = het staat onder "Al gemaakt", of het staat al als
`onderwerp` in een `stories/*/planning.txt` op main of op een branch origin/claude/*.

**Sinds 27 okt 2026 gaat het Titanic-recept hieronder vóór alles** (ook vóór de afwisseling
met dagelijks leven en de Sleepy Facts-proef verderop in deze inleiding).

Onderwerpen staan zoals de titel moet worden (zonder " | History for Sleep"): als
**beleving** ("How…", "What Life Was Like…", "A Night in…"), want daar klikken slaapkijkers
op. De lijst wisselt af: om en om een **dagelijks-leven**-onderwerp (rustig, knus, werkt
het best in deze niche) en een bekend verhaal, liefst een **mysterie** (tot nu toe de best
bekeken video's: Somerton Man, Iron Mask, Colosseum), of een ramp, oorlog of beroemd persoon,
dat begint bij het gewone leven en daarna de gebeurtenis zelf volledig vertelt. Onderwerpen waarbij YouTube
vaker minder advertenties toont (martelingen, executies, moordzaken) staan achteraan.
Is de lijst op, verzin dan zelf nieuwe in dezelfde sfeer (vooral dagelijks leven) en zet
ze hier bij.

**Kanaalcijfers okt 2026:** de video's die een rustige beleving beloven (*Life Before Fire*,
*Life in Old San Francisco Before the 1906 Earthquake*) houden kijkers het langst vast (gemiddeld
15–19 min) en krijgen hun kijkers vooral via voorgestelde video's. Formuleer daarom ook een ramp,
mysterie of beroemd verhaal als beleving, en wissel de vorm af (`Life in … Before …`, `How … Lived`,
`What Life Was Like …`, `A Day in …`, `Life Aboard …`). Geen "Quiet"/"Calm" (zie YOUTUBE-STANDAARD.md, Titel).

Achter een onderwerp kan "(facts)" staan: dan wordt het een Sleepy Facts-video (losse
feitjes, zie stap 2 van PROMPT-NIEUWE-VIDEO.md). Proef sinds okt 2026: ± 1 op de 3 video's.

## Titanic-recept (eigenaar, 27 okt 2026): elke video zo
De eigenaar wil dat **alle** video's zo goed scoren als *Life Aboard the Titanic, April 1912*.
Cijfers 27 okt 2026: Titanic 850 views (± 80% van het kanaal), 9.400 min kijktijd, gemiddeld
36 min kijkduur, 3.723 vertoningen met 5,9% klikken; kijkers vooral via voorgestelde video's
(naast Titanic-slaapvideo's van grote kanalen) en uit de VS. De andere video's: 1-96 views,
meest 1-3% klikken.

**Waarom Titanic hard gaat (analyse 27 okt 2026, YouTube Analytics):**
- *Start (10-19 okt, ± 10 views/dag)*: vooral **voorgesteld** naast *What Titanic's Survivors Really
  Saw That Night 1912* van Dusk Voyages (uit op 10 okt; vanaf die dag de eerste voorgestelde views).
- *Doorbraak (20-25 okt)*: YouTube zet hem op de **startpagina** (bron "Browse"): 10 → 18 → 57 →
  52 → 64 → 114 views per dag. Dat doet YouTube pas als kijkers tevreden zijn.
- *Waarom tevreden*: kijkers laten hem **doorlopen**. Na 10% kijkt nog 31%, op de helft 24%, op 80%
  nog 21% (andere video's zakken naar 16-17%). Gemiddeld 36 min per kijker.
- *Op tv*: 134 views via **tv** (gem. 46 min): mensen zetten hem op in de slaapkamer. Bij de andere
  video's bijna geen tv-kijkers.
- *Klikken*: 5,9% op 3.723 vertoningen; titel met dezelfde trefwoorden als de grote video
  ("Titanic", "1912", "History for Sleep").
- *Vraag*: slaapvideo's over Titanic hebben samen ± 5 miljoen views.
Een video gaat dus hard als (1) het onderwerp veel vraag heeft en een groot kanaal er nu een hit
over heeft, (2) mensen klikken (≥ 5%), en vooral (3) mensen hem de hele nacht laten doorlopen:
een gelijkmatige, rustige stem en sfeer van begin tot eind, geen harde of drukke stukken, geen
herhaling of "nu wordt het spannend", en lang genoeg (± 2-2,5 uur).

Daarom voor elke nieuwe video:
0. **Nooit dubbel, en kies wat de meeste kans heeft** (gratis): draai
   `python3 tools/sleep_trends.py --check <kandidaten>` met de eerste ± 10 kandidaten. "AL GEMAAKT"
   = staat al op Sleep Archives: overslaan. Kies de kandidaat met de meeste views van bestaande
   slaapvideo's (veel vraag = YouTube heeft veel video's om ons naast te zetten), tenzij een
   datum (verjaardag, feestdag) een ander onderwerp nu sterker maakt.
   **Kijk daarna wat nu groeit**: `python3 tools/sleep_trends.py`. Waarom: 71 van de
   164 voorgestelde Titanic-views kwamen van één video, *What Titanic's Survivors Really Saw
   That Night 1912* van Dusk Voyages (uit 10 okt, 146.000 views); Titanic ging van ± 10 naar
   ± 90 views per dag. Staat er bij de grote slaapkanalen (Dusk Voyages, Bedtime & Historian,
   History Camp, Sleepy History with Oliver, Sleepy Old World, ...) een geschiedenis-slaapvideo die
   snel groeit en waarover wij nog niets hebben, en past het in het recept hieronder? Neem dat
   onderwerp dan vóór de lijst, met dezelfde trefwoorden (naam, jaar) in de titel, en breng
   hem binnen ± 3 weken uit. Grappige feitjes-compilaties en wetenschap overslaan.
1. **Wereldberoemd verhaal** waar grote slaapkanalen al goed lopende video's over hebben
   (dan zet YouTube ons ernaast). Liefst één plek/reis + één beroemde dag of nacht, en
   bekend bij Amerikanen. Geen puur dagelijks-leven-onderwerp en geen Sleepy Facts meer.
2. **Opbouw als `stories/titanic`** (15 hoofdstukken, ± 2 u): de plek en hoe het begon →
   het gewone leven van de mensen (rijk/arm, werk, eten) → de laatste gewone dag met kleine
   voortekenen → de beroemde dag/nacht zelf, stap voor stap, kalm en van een afstand →
   redding en wat daarna gebeurde → wat er nu nog van over is, zacht slot.
   Echte, met naam genoemde mensen volgen door het verhaal (zoals Andrews, de Straus'en,
   Molly Brown). Het begin volgt de huidige regels in PROMPT-NIEUWE-VIDEO.md.
3. **Titel met de bekende naam + maand en jaar**, als beleving: bv.
   `Life Aboard the Lusitania, May 1915`, `Life in Chicago Before the Great Fire of 1871`.
4. **Thumbnail met mensen** (eigenaar, 28 okt 2026): zoals de huidige Titanic-thumbnail
   `stories/titanic/thumbnail-v2.jpg`: **mensen van dat moment** dichtbij en herkenbaar (het
   orkest en passagiers aan dek in warm lamplicht), het beroemde onderwerp eromheen (schip,
   stad), warm licht tegen een koele avond, ontwerp v2 uit YOUTUBE-STANDAARD.md. **Nooit alleen
   een schip of gebouw zonder mensen** (de Mayflower-thumbnail was alleen een schip). Doel: ≥ 5% klikken.
5. Na upload: eindscherm naar de Titanic-video en in een passende afspeellijst zetten.

## Weekplanning (eigenaar, 27 okt 2026)
**2 video's per week: woensdag en zaterdag 21:00** (NL-tijd), allemaal volgens het Titanic-recept.
Alles gaat automatisch op de pc van de eigenaar: Windows Taakplanner start elke **zondag en
donderdag 09:00** `stories/PROMPT-ROUTINE-PC.md` (onderwerp, script, comfy-beelden, stem, montage,
upload). Problemen staan in `stories/ROUTINE-LOG.md`.
Vooruitblik (gekozen op 27 okt 2026 met `tools/sleep_trends.py --check`: hoeveel views de
bestaande slaapvideo's over het onderwerp samen hebben; Titanic: ± 5 miljoen):
**Nieuwe planning (eigenaar, 28 okt 2026: "echt bekende dingen die veel mensen aantrekken en waar nu
een hype is")**: alleen wereldberoemde onderwerpen, op een jubileum, feestdag of nieuwe film.
Edmund Fitzgerald, Franklin en Salem (minder bekend of Halloween voorbij) schuiven naar achteren.
- wo 28 okt: Life Aboard the Mayflower, 1620 (al openbaar)
- wo 4 nov: Life on the Oregon Trail, 1846 (klaar, privé geüpload op de pc)
- za 7 nov: Life in Europe During the Black Death, 1348 (± 640.000)
- wo 11 nov: Life in Tombstone, the Gunfight at the O.K. Corral, 1881 (Wild West ± 2,8 miljoen)
- za 14 nov: Life in Ancient Egypt When Tutankhamun Died, 1323 BC (± 3,4 miljoen)
- wo 18 nov: Life in Gettysburg, July 1863 (± 670.000; Gettysburg Address 19 nov)
- za 21 nov: Life in Dallas, November 1963 (Kennedy, 22 nov; film *November 1963* 4 dec)
- wo 25 nov: Life in Antarctica with Scott's Last Expedition, 1912 (± 2 miljoen)
- za 28 nov: Life at Pearl Harbor, December 1941 (± 3 miljoen; 85 jaar op 7 dec)
- wo 2 dec: Life in Philadelphia, July 1776 (Amerika 250 jaar)
- za 5 dec: Life in Ancient Troy, 1200 BC (film *The Odyssey*, 2026)
- wo 9 dec: Life in London Before the Great Fire of 1666 (± 80.000)
- za 12 dec: Life in the Trenches, Christmas 1914 (kerstbestand)
- wo 16 dec: How Medieval Peasants Survived Winter, 1300 (film *Werwulf* 25 dec)
- za 19 dec: Life in Bethlehem, the First Christmas (kerst)
Later: Edmund Fitzgerald (met "Lake Superior" in de titel), Franklin ("Arctic"), Salem (vóór Halloween 2027).

## Nog te maken
In de maak (andere sessie, okt 2026): **Life Aboard the Mayflower, 1620** (niet opnieuw
beginnen; uitbrengen vóór Thanksgiving 26 nov 2026).

Eerst deze (Titanic-recept, in deze volgorde; tussen haakjes: views van bestaande slaapvideo's
over het onderwerp, 27 okt 2026):
- Life on the Oregon Trail, 1846 (500.000)
- Life Aboard the Edmund Fitzgerald, November 1975 (70.000)
- Life Aboard Franklin's Lost Expedition, 1845 (140.000)
- Life in Europe During the Black Death, 1348 (640.000)
- Life in Gettysburg, July 1863 (670.000)
- Life in Salem During the Witch Trials, 1692 (115.000)
- Life in Tombstone, the Gunfight at the O.K. Corral, 1881 (Wild West 2,8 mln)
- Life at Pearl Harbor, December 1941 (3 mln; vóór 7 december uitbrengen)
- Life in Ancient Egypt When Tutankhamun Died, 1323 BC (Ancient Egypt 3,4 mln)
- Life in Antarctica with Scott's Last Expedition, 1912 (Antarctic 2 mln)
- Life with Lewis and Clark, 1804 (200.000)
- Life in London Before the Great Fire of 1666 (80.000)
- Life Aboard the Hindenburg, May 1937 (weinig slaapvideo's, maar Dusk Voyages bracht er 27 okt 2026 een uit)

Weinig vraag (< 25.000 views samen, alleen als stap 0 iets anders laat zien): Lusitania,
Shackleton/Endurance, Apollo 13, Great Chicago Fire, Jamestown, Johnstown, Galveston, Andrea Doria,
Carpathia, Britannic, Roanoke, Klondike.

Daarna (oude lijst): alleen een onderwerp dat als wereldberoemd verhaal in het
Titanic-recept past (bekende ramp, reis, mysterie of persoon); maak er dan een titel met
naam + jaar van. Verzin anders zelf nieuwe in de stijl van de lijst hierboven en zet ze erbij.
- The Tunguska Event
- What Medieval Monks Did All Day
- How People Lived Along the Nile in Ancient Egypt
- What Life Was Like as Rome Fell
- How Lighthouse Keepers Lived Alone at Sea
- A Day in a Medieval Castle
- How the People of Stonehenge Lived
- Life in a Samurai Household in Old Japan
- Inside a Victorian London Home
- How Pioneers Survived Winter on the American Frontier
- The Abandoned Island of Hashima
- What Life Was Like in Ancient Athens
- A Year on a Medieval Farm
- How Ancient Romans Ate, Slept and Kept Warm
- Life Inside a Medieval Monastery Library
- The Lost City of Atlantis
- How People Kept Warm Before Central Heating
- A Night in an 1800s Coaching Inn
- Rasputin: The Mad Monk
- How Inuit Families Lived Through the Arctic Winter
- Pripyat: The City Time Forgot
- Life in a Japanese Village During the Edo Period
- The Flying Dutchman Legend
- How Medieval Peasants Slept
- The Ghost Towns of the American West
- What Life Was Like on the Silk Road
- A Winter in Old Amsterdam
- The Curse of the Hope Diamond
- How Shepherds Lived in the Scottish Highlands
- Henry VIII's Six Wives
- Centralia: The Town on Fire
- The Bikini Atoll Nuclear Tests
- D-Day: The Longest Night
- The Siege of Leningrad
- The Battle of Stalingrad
- The Fall of Berlin 1945
- The USS Indianapolis Disaster
- The Bhopal Gas Disaster
- Three Mile Island
- Windscale: Britain's Nuclear Disaster
- Ivan the Terrible: Russia's Darkest Tsar
- Caligula: Rome's Maddest Emperor
- The Reign of Terror: France's Bloody Revolution
- The Spanish Inquisition
- The Plague Doctors of Europe
- Witch Trials of Medieval Europe
- The Abandoned Asylums of America
- The Amityville Horror: The True Story
- Elizabeth Báthory: The Blood Countess
- Life and Death in a Medieval Dungeon
- The Lindbergh Baby Kidnapping
- The Boston Strangler Case
- The Villisca Axe Murders

## Al gemaakt
- A Winter Hike to the Dyatlov Pass, 1959 (= de video "The Dyatlov Pass Mystery", live 12 okt 2026; titel wordt nog aangepast)
- The Somerton Man Mystery
- The Man in the Iron Mask
- Dark History of the Roman Colosseum
- The Tower of London (Guy Fawkes)
- The Dancing Plague
- The Mary Celeste
- The Dutch Hunger Winter (op YouTube als "The Winter That Came Before Freedom")
- The Darkest Punishments of Medieval Europe
- How Did Humans Survive Without Fire?
- Pompeii: The Last Day
- Chernobyl 1986
- The San Francisco Earthquake of 1906
- The Titanic: The Night It Sank (op YouTube als "Life Aboard the Titanic, April 1912"; de beste video, zie Titanic-recept)
- The Fall of Pompeii (dubbel met Pompeii: The Last Day, overgeslagen)
- How Vikings Survived the Long Dark Winter (facts)
- The Dyatlov Pass Mystery (op YouTube als "Dyatlov Pass: A Winter Night in the Urals")
