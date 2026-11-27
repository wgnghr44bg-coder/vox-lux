# Market Doodle — What If: vaste afspraken (eigenaar 22-23 nov 2026)

Voor elk Claude-account dat hiermee verdergaat. Kanaal @marketdoodle, token `YT_REFRESH_TOKEN_ALTERAQON`. FOCUS-kanaal.

## Wat het kanaal is
- Breed **What If** (niet alleen geld), Engels, voor de VS. Verhalen met **poppetjes die met code getekend zijn** (geen AI-video).
- Niche gekozen met `tools/niche_scan.py` (uitslag `kanalen/niche/ALLE-NICHES.md`): what if = geen grote kanalen, veel kleine winnaars.

## Ritme
- **Vaste dagen ma, wo, za** (eigenaar 23 nov avond, zelfde dagen als BlackswanVault): **lange video 17:00 NL** (± 3 min, **liggend** 1920x1080), **Short 19:00 NL**. **Elke dag een Short** (eigenaar 24 nov: 3 lang per week + elke dag Short, rond 22 dec evalueren op views/kijkduur).
- **Shorts**: eigen ideeën, elk een **eigen nieuw What If-onderwerp**, gemaakt zoals de eerste Short (Qhjfoib3FIA): staand, ± 60-70 s.
- **Onderwerp kies je zelf**, niet eerst voorleggen, nooit herhalen. Kies wat nu goed loopt op YouTube.

## Altijd eerst laten zien (eigenaar: "laat eerst zien wat je gaat doen dus niks zelf doen")
- Niets op YouTube/het kanaal veranderen zonder dat de eigenaar het resultaat gezien heeft en "ja" zegt: video, thumbnail, titel, beschrijving, banner, upload, openbaar zetten.
- Upload: eerst privé, verwerkt afwachten, `snippet.channelTitle` = Market Doodle controleren, AI-label aan (API laat het niet terugzien: eigenaar checkt in Studio).
- **Shorts krijgen geen thumbnail** (alleen lange video's).

## Stijl
- Verhaal zoals de grote what-if kanalen: begin met een scène ("It's 7:15... you walk into the kitchen"), dan de vraag, dan **regels**, dan het verhaal dat steeds gekker wordt, **één echt feit met bron**, eindigen met een **cliffhanger**. **Simpel** en met **humor**.
- Vaste familie: jij (blauwe hoodie), papa (bril, groen), mama (paardenstaart, paars), zusje (staartjes, geel). Meer mensen in beeld mag "als het maar klopt".
- **Geen effect bij scènewissel** (gewoon knippen, ook geen fade aan het eind). **Geen muziek.**
- **Geluidseffecten mag** (eigenaar 23 nov): alleen wat je in de scène echt hoort (voetstappen, klik, papier, hap, klok), zelf gemaakt (`short-pauze/geluid.py`), zacht onder de stem.
- **Niets ongepasts of ongemakkelijks** (eigenaar 23 nov): bv. geen ouder die bij een kind de badkamer in loopt. Geen rare ogen (geen dichte ogen of doorzichtige gezichten waar het niet klopt), geen "zzz" als het verhaal niet zegt dat iemand slaapt.
- **Alles moet kloppen als een film** (eigenaar 23 nov): eerst gebeurt iets (juf praat, bal vliegt), dan pas de reactie (knop, stilstand). Spullen echt in de hand (`gebaar="vast"`/`"haar"`), poppetje loopt naar dingen toe en kijkt ernaar. **Geen grote tekst bovenin die hetzelfde zegt als de ondertitel.**
- Ondertitels onderin, gesproken woord geel. **Geen naamlabels of tekens bij de personages** (eigenaar 25 nov: "alle tekens bij de characters mogen ook weg"; `NAAMLABELS = False`): wie praat zie je aan de mond. Getallen/labels gloeiend boven hoofden waar het past. Schaduw onder poppetjes.
- Bedragen in één eenheid (bv. alles per jaar).
- **Geen Wan/AI-videoclips** (vervormt, eigenaar: "geen optie").

## Stemmen (OmniVoice, op de pc)
- Verteller: **eigen-stem-swan, speed 1.05** (eigen stem van de eigenaar; geluid alleen op de pc, nooit op GitHub).
- Iedereen houdt zijn **eigen** stem (ook bij een lichaamsruil): jij `whatif-zoon`, papa `whatif-papa`, mama `whatif-moeder2`, zusje `whatif-meisje`, juf `whatif-juf`, baas `whatif-baas`.
- Mama en zusje moeten duidelijk verschillen (eigenaar koos optie A). Elke zin nakijken met Whisper.

## Thumbnail (alleen lange video's)
- **Vaste huisstijl (eigenaar 26 nov 2026, na CTR 0,97% van de oude oranje Swap-thumb):** links/rechts twee scènes (voor/na of
  wie/wie), **witte lijn** in het midden, achtergronden iets **vaag**, poppetjes **groot**, max. **2 schuine banners** (wit met zwarte
  rand op rood/groen/blauw) en hooguit één groot getal in de scène (bv. "4/10" op het bord). **Weinig spullen** ("het is teveel op
  een thumbnail"). Geen naamlabels/pijlen.
- **Wie is wie moet je zien zonder tekst:** grootteverschil (kind klein achter groot bureau, papa groot achter piepklein
  schoolbankje) en kleding ruilen (kind in pak met das, papa met kinderpetje) - zo doen de best bekeken video's het.
- Voorbeelden: `video-swap/drie/thumb4.py`, `video-miljoen/thumbnail3.py` (banner-functie daarin hergebruiken).
- Altijd zelf klein bekijken (246x138, telefoon) en controleren dat niets zweeft/overlapt (getal niet achter een hoofd).

## Gereedschap
- Poppetjes + Short: `proef-pop-short/pop_short.py` (functie `poppetje`, 10+ personages).
- Lange video: `video-swap/drie/` — `stem.py` (stemmen) → `woordtijden.py` (Whisper) → `maak3.py --plaat` (controle) → `maak3.py` (render, als los proces via `render.ps1`).
- Achtergronden: ComfyUI Z-Image (`tools/comfy/comfy_batch.py`, lege ruimtes zonder mensen/tekst; let op nep-letters).
- Banner/logo: `proef-pop-short/branding.py` (licht, familiefoto; logo = jongen verbaasd).
- Pc heeft weinig geheugen: één zware taak tegelijk.

## Online (stand 24 nov 2026, ± 12:00)
- Short: Qhjfoib3FIA (What If You Could See How Much Everyone Earns?), 23 nov.
- Lang: jJacEFpBrXY (What If You Swapped Lives With Your Dad for a Week?), 23 nov.
- Short: -tP-eeJUYtU (What If You Built a Real Cyborg?), 24 nov (eigenaar zette hem zelf openbaar). Pause Time (13EHf4WZdWs) is verwijderd.
- Short: 3Tk4Cf0zR2w (What If You Invested $100 in NVIDIA in 1999?), 26 nov ± 21:20 openbaar (eigenaar: "zet hem maar online"), AI-label via API meegestuurd.
- **Ingepland op YouTube: NIETS** (eigenaar 24 nov: "er staat nu niks gepland"). Volgende plekken: wo 25 nov en za 28 nov (lang 17:00, Short 19:00), onderwerp nog kiezen.

## GOEDGEKEURD SJABLOON VOOR ELKE NIEUWE VIDEO, SHORTS ÉN LANG (eigenaar 25 nov 2026: "de video is goed, graag opslaan voor nieuwe shorts en long video's")
De $1 Million-video (`video-miljoen/`, "What If Everyone Got $1 Million? (It Goes Wrong Fast)") is goedgekeurd: "perfect".
Elke nieuwe Short en lange video wordt op precies deze manier gemaakt en gecontroleerd. Kopieer `video-miljoen/maak_miljoen.py`
als begin (voor een Short: staand 1080x1920, ± 45-50 s, zelfde poppetjes, zelfde controles).

**Maken**
- Script volgens "VASTE WERKWIJZE LANGE VIDEO" hieronder (chaos in seconde 1, dagen, feit, cliffhanger, running gags, geen muziek).
- Elke zin: wat gezegd wordt staat in beeld op het woord (`kw(zin, woord)`); wat de verteller alleen vertelt hoeft niet.
- Gezicht past bij de zin: emotielijsten `SCHRIK` / `VERDRIET` / `BLIJ` (eerste woorden van de zin, hoofdletters maakt niet uit).
- Gebaar past bij de zin (`ACTIE`/`NACTIE`), armen nooit door een ander heen. Geen naamlabels (25 nov).
- Elk voorwerp via `WACHT.plaats(naam, box, op=...)` op een vlak uit `achtergronden.json` (nieuwe achtergrond: eerst meten met
  `tools/meet_achtergrond.py` en vlakken/muren/meubels toevoegen). Logische plek (huiswerk op een bureau, tv aan de muur, bord op
  tafel); ontbreekt het meubel, teken het erbij. Simpel: geen extra labels/blaadjes als het beeld al duidelijk is.

- **Geluid = echte opnames** (eigenaar 25 nov: "echte geluidseffecten ... als een paard eet dat gesmek, mag wel een beetje
  humor in zitten"; Short goedgekeurd): CC0 van freesound.org in `geluiden/` (bron in `gekozen.json`), op het woord geplakt,
  zacht onder de stem, met een grapje waar het kan (slok na het opeten, steeds hardere kassa-piep, krekels bij een ongemakkelijke
  stilte). `geluidcheck()` in de renderer: elk geluid alleen als het ding erbij in beeld is. Voorbeeld: `short-miljoen/maak_short.py`.
- **Grappen en gezichten vanzelf** (eigenaar 25 nov: "het paard naar de camera laten kijken met een vraagteken ... zulke dingen
  moet je erbij doen en het moet vanzelf gaan, ook met uitdrukking van gezichten"): `tools/grappenkiezer.py <map>` maakt een
  voorstel (`grappen.json`: per regel gezicht, wie, woord, camera; **GEEN striptekens ? ... ! boven hoofden**, eigenaar 25 nov: "laat die tekens maar weg"), Claude loopt het na (max. ±1 per
  3 regels, alleen wie echt in beeld is) en de renderer tekent het (`stripteken()`, kijken in de camera). Echte stilte met
  `STILTE|2.0` in het script met **precies één krekel-tjirp** (eigenaar: "1 krekel, dit lijken er wel 100") en de familie die **langzaam** opzij kijkt; de geluidcheck eist minstens 1,5 s stilte.
  **Krekel niet elke keer** (eigenaar 26 nov: "krekel geluid hoeft niet elke keer erin"): af en toe, niet als vast trucje;
  een korte pauze (`STILTE|1.0`) zonder geluid mag ook.
  **Stilte + naar elkaar kijken is GEEN vast einde** (eigenaar 26 nov: "dat naar elkaar kijken hoeft niet, die stilte alleen
  als het past"): alleen gebruiken als de grap er echt om vraagt.
- **Gewoon praten = geen armgebaar** (eigenaar 25 nov); alleen een gebaar als de zin erom vraagt. De renderer meldt het in LAYOUT.
- **Verteller per zin inspreken met pauze** (eigenaar 25 nov: "It's 6 a.m. Your bank app gaat te snel"): `stem.py` + `tools/tempowachter.py`.
- **Tempo verteller: 180 woorden/min** (eigenaar 25 nov: 161 te langzaam, 200 te snel, 180 "dit is goed" voor Short én lange video). Na stem.py + woordtijden.py: `tools/stemtempo.py <map> 180`, dan tempowachter.

**Controleren vóór de eigenaar iets ziet (is Claude's taak, niet die van de eigenaar)**
1. Render-uitvoer: `LAYOUT: alles past` en `SCENEWACHTER: 0 fouten` (`SCENEWACHTER.md`).
2. `python tools/herkenwachter.py <map>` -> een hulpje dat het verhaal niet kent noemt elk genummerd voorwerp; verkeerd genoemd =
   opnieuw tekenen.
3. `python tools/rariteitenwachter.py <video.mp4>` (beelden elke 2 s met de zin eronder) + nakijkronde volgens `tools/NAKIJKEN.md`
   (hulpjes per blad, vaste vragenlijst: zweeft iets, logische plek, gezicht past bij de zin, tekst over belangrijke delen).
4. `tools/beeldwachter.py` (zegt het beeld wat de zin zegt).
4b. `tools/achtergrondwachter.py <map>/afbeeldingen` (tekst moet bij het voorwerp passen: MILK alleen op melk) en
   `tools/tempowachter.py <map>` (verteller houdt pauze tussen zinnen, niet te snel). Beide 0 fouten.
5. Alles herstellen, opnieuw renderen, herstelde momenten zelf nakijken. Vindt de eigenaar toch iets: **de controle aanpassen**
   zodat die soort fout voortaan automatisch gevonden wordt, niet alleen het ene beeld.
6. Klaar: `python tools/seintje.py "Titel" "Tekst"` (ntfy), video sturen (`display: render`; telefoon < 30 MB).

**Uploaden** pas na "ja" van de eigenaar: privé, `snippet.channelTitle` = Market Doodle, AI-label aan, titel stijl
"What If ...? (It Goes Wrong Fast)", thumbnail alleen bij lange video's.

## VASTE WERKWIJZE LANGE VIDEO (eigenaar 24 nov 2026: "zet dit zo vast voor andere nieuwe video's")
Voorbeeld en sjabloon: `video-miljoen/` (What If Everyone on Earth Got $1 Million Tonight?). Eigenaar vond de proef "perfect".
Aanleiding: de eerste lange video (Swapped Lives) kreeg 6 views; AI Studio-analyse: saai begin (regels), stilstaande
poppetjes, uitleg i.p.v. beeld, te kort, onderwerp los van de Shorts.
- **Lengte: minimaal 8 minuten** (± 1.400 woorden, 115 zinnen; tempo 180 woorden/min via tools/stemtempo.py). Steeds gekker met nieuwe gebeurtenissen,
  nooit opvulling/uitleg.
- **Onderwerp in de lijn van een Short die al loopt** (geld, techniek, superkrachten, overleven), zodat die Short de lange
  video als "Gerelateerde video" kan krijgen.
- **Opbouw (zoals miljoen):**
  1. Seconde 1 = midden in de chaos, iemand roept iets ("Mom! Dad! Check your phones! Now!") + meteen het gekke beeld.
  2. Familie reageert (iedereen eigen zin), dan pas "So, what happens next?" met een belofte ("Day one is amazing. Day two is
     weird. And by day thirty... well."). **Geen regels-blok, geen titelkaart.**
  3. **Dagen** (Day 1, 2, 3 ... 30), elke dag één nieuwe gekke gebeurtenis die erger wordt. "DAY X" geel linksboven.
  4. Halverwege **het echte feit, verweven in het verhaal** (personage reageert erop), met bron onderin beeld.
  5. Omslag: mensen gaan samenwerken / leren iets (kort, één zin les).
  6. **Cliffhanger** als laatste zin + korte reactie ("Congratulations." – "Oh no.").
- **Humor (eigenaar: "laat het script zo, ik vind hem leuk"):** running gags die terugkomen (Mister Pancake, papa's "How hard can
  it be?", de boot op de oprit), droge verteller-zinnen ("Nobody asked for a spreadsheet."), een twist aan het eind van een stuk
  (reparateur zit op een jacht; juf gaf haar miljoen uit aan één kokosnoot; eiland zonder wc), korte reacties van zusje.
  Geen kindertekenfilm.
- **Geen muziek** (eigenaar 24 nov, na muziekproeven: "ik hoef geen muziek"). Stiltes opvangen met strakke timing,
  geluidseffecten van wat je ziet (telefoon trilt, kassa, deur slaat, rookmelder, kippen, stempel bij "SOLD OUT") en beweging.
- **Laten zien wat er gezegd wordt:** elk voorwerp/elke handeling uit de zin staat in beeld op het moment van het woord
  (woordtijden uit Whisper, `kw(zin, woord)`): telefoon in de hand, saldo dat verspringt, auto rijdt binnen, paard eet,
  prijskaartje dat oploopt, chef-muts, rook, briefje op de deur. Voorwerpen: ComfyUI Z-Image op witte achtergrond, uitgeknipt.
  Camera: rustige push-in per scène (6%), gewoon knippen tussen scènes.
- **Stemzinnen niet "One. Million. Dollars."** (punt na elk woord klinkt als een robot) maar natuurlijk: "One million dollars?! No way!".
- **Altijd eerst een proef van 2 minuten** laten zien, daarna pas de hele video.
- **BEELDWACHTER verplicht** (eigenaar 24 nov: "er moet een wachter op komen die controleert dat er op beeld gedaan wordt wat er
  gezegd wordt"): `python tools/beeldwachter.py <video.mp4> <zinnen.json>` (gratis, Ollama: qwen3:14b bepaalt per vertellerzin wat
  je moet zien, qwen2.5vl:7b kijkt naar 3 beelden). Uitslag in `BEELDWACHTER.md`; elke terechte melding herstellen en opnieuw
  draaien. Onzin-meldingen (iets wat de zin juist ontkent, of niet te tekenen is) mag je negeren, maar noem ze aan de eigenaar.
- **EXTRA CONTROLE VOOR HET VERSTUREN, ook verplicht** (eigenaar 24 nov, na een zwevende roze schijf bij papa's kiespijn en
  tekst buiten kaders: "dit moet echt beter gecontroleerd worden, graag extra controle of wachter op"):
  1. `tekstcheck.py` -> elk moment met tekst (koppen, prijskaartje, sheet, biljet, tv, telefoon) op bladen; alles moet leesbaar,
     goed gespeld en binnen zijn kader staan. Programmacheck `LAYOUT` (in de renderer) meldt koppen buiten beeld en tekst die
     niet past; moet leeg zijn.
  2. `python tools/rariteitenwachter.py <video.mp4>` -> elke 2 s een beeld, 12 per blad (`rariteiten/overzicht-NN.jpg`).
     **Claude loopt ALLE bladen zelf na** op: zwevende of losse vormen, half weggepoetste plekken, voorwerpen over gezichten,
     afgesneden hoofden/tekst, tekst buiten kaders. Het kleine beeldmodel (`--model`) is onbetrouwbaar (zag blosjes als fout,
     miste een echte losse schijf) en nooit de enige controle.
  3. Gevonden fouten herstellen, opnieuw renderen, de herstelde momenten opnieuw bekijken. Pas dan naar de eigenaar.
  Lessen uit miljoen: koppen ná de camera-zoom tekenen (anders valt "DAY X" links af); iets "opgegeten/weg" tonen door de
  schone achtergrond terug te plakken op precies de goede plek (niet een los stuk eroverheen); dieren/voorwerpen altijd met lijf
  en op iets staand, nooit losse koppen; rook zacht en doorzichtig, niet als grijze schijven.
  **NIETS MAG ZWEVEN** (eigenaar 24 nov, tweede ronde: "deze beelden kloppen niet"): elk voorwerp staat op iets wat in de
  achtergrond zit (auto's op de stoep/weg, router op het aanrecht met stekker in een stopcontact, bord op een tafel, mat op de
  grond) of wordt vastgehouden/hangt aan iets (mat in de bek, touw precies naar de mond). Wat in de zin genoemd wordt moet er
  echt zijn ("TV broken" -> er staat een tv die kapotgaat). Voorwerpen niet over elkaar schuiven. Verbrand/ziek = hele gezicht
  getint, geen losse rode stippen (clown). Tranen blijven op de wangen. Bij het nalopen per beeld vragen: waar staat dit op?
  **EN: WAAR HOORT HET LOGISCH?** (eigenaar 24 nov: "waarom maak je geen bureau waar het huiswerk zich opstapelt, je moet het
  echt slimmer doen"). Niet alleen "niet zweven", maar de plek die je in het echt zou kiezen: huiswerk op het bureau (jij zit
  erachter), bord op tafel, tv aan de muur. Ontbreekt dat meubel, dan teken je het erbij. "Op de vloer gezet zodat het niet
  zweeft" is meestal fout. Gezicht past bij de zin (teleurgesteld bij "a little less happy", niet lachen).
  Automatisch: `tools/scenewachter.py` + `achtergronden.json` (elk voorwerp `op=`), nakijkronde volgens `tools/NAKIJKEN.md`.
- Stem nakijken met Whisper (woorden.json vs script); verkeerd verstaan -> die zin opnieuw met `OPNIEUW=<nrs>` (andere seed).
- Gereedschap: `video-miljoen/stem.py` -> `woordtijden.py` -> `maak_miljoen.py --plaat` (controlebladen) -> `maak_miljoen.py`
  (render) -> beeldwachter.

## Lessen uit de cijfers (Studio-rapport 23 nov 2026)
- Short "How Much Everyone Earns": 1.235 views, 52% bekeken vs. 48% weggeswipet, 67,6% gemiddeld bekeken (0:47), 29 likes, +3 abonnees. Werkt: meteen een beeld dat iedereen snapt in seconde 1 ("glowing number above your dad's head").
- Lange video "Swapped Lives": 27 vertoningen, kijker weg na 0:15 (bij de regels). Les: **eerste 5 seconden = midden in de chaos**, regels pas daarna.
- **Shorts ± 45-50 s** (niet 60-70 s).
- Zoektermen die mensen al naar ons brengen: superkrachten ("everyone gets superpowers overnight") en overleven ("can you survive being swallowed"). Kies zulke onderwerpen.
- Kijkers: 74% mobiel; tijden 17:00/19:00 NL passen.

## 3D met three.js (eigenaar 24 nov 2026) — GESTOPT
- **Eigenaar 24 nov middag: "Stop maar, we houden het op de detail versie van de 2D".** De What If-video's blijven 2D (poppetjes uit code op ComfyUI-achtergronden), met **meer details**: echte voorwerpen als losse plaatjes (bv. koelkast uit de achtergrond geknipt, AI-rugzak met witte achtergrond weg, `short-cyborg/sprites.py`), spullen echt in de hand. Het 3D-werk hieronder blijft bewaard maar wordt niet gebruikt.
- Eigenaar: "Ik wil gewoon dezelfde beeld houden van 2D alleen jij zet het om in 3D met threejs ... ik wil de armen enzo alles blijven zien".
  Dus: **dezelfde poppetjes** (rond hoofd, puntogen, blauwe hoodie, papa met bril, enz.) en dezelfde soort ruimtes, maar **in 3D**,
  met een camera die door de ruimte beweegt (zoals de voorbeeld-Short van @RicksClips3000).
- Programma: `kanalen/marketdoodle/studio3d/` — `scene.html` (three.js: toon-materiaal + omtreklijnen, poppetjes, ruimte, camera-reis `REIS`,
  ondertitels 1-2 woorden) + `render.mjs` (Edge headless via puppeteer-core -> ffmpeg). `node render.mjs uit.mp4`. 12 s video = ± 12 s rekentijd.
- Eerste goedgekeurde proef: `proef3d.mp4` (keuken, klok 7:15, jij loopt binnen, getal boven papa, papa zwaait/praat). Eigenaar: "Ja".
- Regels die de eigenaar bij de proef gaf: **lopen = gezicht in de looprichting** (niet achteruit), **kijken naar wie/wat de tekst noemt**
  (jij kijkt naar papa bij "your dad's head", papa draait naar jou), **bril moet er normaal uitzien** (glazen plat op het gezicht, brug, pootjes).
- 24 nov (keuken 1 min, `studio3d/keuken1min/`): **bril weg bij papa**; **blosjes plat op de huid zonder zwarte rand** (anders lijken het neuzen);
  **camera rustig**: vooral wijde/halfwijde shots, lang stilstaan, langzaam bewegen, niet steeds inzoomen, nooit door hoofden heen;
  getallen alleen boven wie op dat moment centraal staat (anders overlappen ze). Mama, zusje, postbode staan al in 3D.

## Gebaren van de poppetjes (24 nov, eigenaar: "andere bewegingen dan alleen zwaaien")
`pop_short.poppetje(..., gebaar=...)`: zwaai, wijs, wijslinks, vast (iets vasthouden), haar, schouders, stamp, **juich** (armen omhoog),
**schrik** (handen omhoog, trillen), **denk** (hand aan de kin), **facepalm**, **heupen** (handen in de zij, ellebogen), **klap**, **duim** (duim omhoog),
**praat** (handen bewegen mee met praten), **armen-open** ('wat?!'), **rennen** (met loop=), **knik** (ja), **nee** (nee schudden).
Overzicht: `proef-pop-short/gebaren.jpg` (maken met `gebaren_demo.py`). Kies per zin een gebaar dat bij de tekst past; niet steeds zwaaien.
- **YouTube-beschrijving kort** (eigenaar 25 nov): openingsvraag, hoofdstukken, vraag voor de reacties, hashtags. Geen samenvatting, geen bronregel, geen regel over geluidseffecten.
- **Elke keer een nieuw onderwerp** (eigenaar 25 nov): geen extra Shorts uit een bestaande lange video. Ritme (eigenaar 25 nov): om de dag een lange video met een Short over hetzelfde onderwerp; de dag ertussen een losse Short over een nieuw onderwerp.

- **Opening Shorts** (eigenaar 26 nov, Black Friday): begin met "Imagine ..." + het onderwerp en schets daarna **meerdere
  scenario's** (week 1, week 2, ...) i.p.v. één lijn; niet elke keer dezelfde opbouw (geen telefoon-begin als vast trucje).
- **Meer eigen stemmen** (eigenaar 26 nov): niet alleen papa, mama, zoon en dochter laten praten; ook bijfiguren (kassière, agent, buurman, ...) krijgen een eigen stem (OmniVoice voice design in `stem.py`, `ONTWERP`) en praten zelf, ook tegen elkaar, i.p.v. dat de verteller hun zin zegt.
- **Maatwachter** (eigenaar 26 nov: "waarom ben ik zo klein, het klopt gewoon niet"): elke achtergrond krijgt in `achtergronden.json` een `maat` (horizon + k, opgemeten aan deur/bank/bureau/mensen). De scènewachter controleert met `WACHT.persoon(naam, voet_y, lengte)` of elk poppetje 75-130% van de echte maat op die plek is; zonder opgemeten maat = FOUT. Getekende meubels moeten passen bij wat er in de achtergrond staat (geen tweede pc 'op de grond').
- **Tekstwachter** (eigenaar 26 nov: "sommige beelden kloppen niet met de tekst ... zorg dat er een controle op staat"): `tools/tekstwachter.py` kijkt per zin: (1) jaartal gezegd maar ander jaar in beeld, (2) spreker niet in beeld, (3) juichen bij spijt / facepalm bij blijdschap, (4) genoemd = gezien (`ZIE`-regels per short: "playstation" -> ps2, "chips" -> videokaart, "hundred dollars" -> $100 ...). Elke render schrijft `TEKSTWACHTER.md` (moet 0 zijn) en `TEKSTCONTROLE.jpg` (per zin begin/midden/eind) die ik zelf naloop vóór ik iets stuur. Snel: `maak_short.py --tekst`.
- **Vastgehouden voorwerpen** tellen mee in de gezichtscontrole (niet voor het eigen gezicht); grote koppen mogen niet over een naamlabel vallen (LAYOUT).
- **Shorts blijven steken op ± 1.200 views** (Studio-AI-analyse 27 nov, 4 Shorts): 97% komt uit de Shorts-feed, 96% nieuwe kijkers. "Bleef kijken" is maar 52-62% (doel **70%+**). Kijkers haken vooral af in **0-6 s** en rond **28-32 s**. Afgekeken: 31-47%. Beste was NVIDIA, omdat de vraag meteen in zin 1 staat. Slechtste was $1M, die met een dialoog begint ("Mom, Dad...") en de vraag pas na 4-5 s stelt. Daarom voortaan:
  1. **Seconde 0-2: de What If-vraag zelf**, met een sterk bewegend beeld. Geen begroeting, dialoog of trage opbouw vooraf.
  2. **Lengte 35-45 s** (niet 55-70), vooral het midden strakker.
  3. **Laatste zin loopt terug in het begin** (loop), zodat hij vanzelf opnieuw start.
- **NIEUW RITME (27 nov, eigenaar: "doe maar wat jij denkt het beste is") — vervangt 'om de dag een lange video' en 'vaste dagen ma, wo, za':** **elke dag één sterke Short** (19:00 NL, of eerder op de dag zelf als het onderwerp een hype van die dag is) en **één lange video per week, op zaterdag 17:00 NL**, over het grootste onderwerp van die week, met een Short erbij. Reden: Shorts halen ± 1.200 views, lange video's nog maar tientallen. Rond 22 dec evalueren: komen Shorts ruim boven 1.200 en groeien de abonnees, dan terug naar vaker lang.
- Short: Lg-Beh3sS7M (What If Black Friday Never Ended?, 42 s), ingepland 27 nov 17:00 NL openbaar.
- Short: Awzd3RcysAE (What If You Built A Shark That Can Walk?, 42 s, hype 'snake that can fly'), ingepland 27 nov 14:00 NL openbaar.
- **VASTE SHORTREGELS, ELKE NIEUWE SHORT (eigenaar 27 nov: "zorg dat je je eraan houdt, elke nieuwe video, zet dat vast")** – automatisch gecontroleerd door `tools/shortregels.py` (SHORTREGELS in de render-uitvoer, moet "alles goed" zijn):
  1. **Haak:** eerste zin begint met "What if" en de vraag is binnen 3,2 s uitgesproken; in het allereerste beeld staat al iets bijzonders (game-HUD, het dier/ding, een grote prijs) én de camera beweegt (snelle zoom). Geen leeg beeld met alleen een poppetje.
  2. **Lengte:** 35-45 s.
  3. **Loop:** de laatste zin wijst terug naar het begin (onderwerp opnieuw genoemd of een vervolg-haak zoals "Day thirty is way worse").
  Daarnaast blijven alle andere controles verplicht: tekstwachter (genoemd = gezien, spreker, gevoel, RIJDEN: wie rijdt zit ín de auto, DOEN: wat iemand doet zie je), scènewachter + maat, LAYOUT (ook: grote tekst niet over een gezicht), geluidcheck, tempowachter per zin (ook personages, korte uitroepen niet afraffelen) en zelf TEKSTCONTROLE.jpg nalopen.
- Lang: fqN3ZBbJ_tM (What If GTA 6 Was Real Life? (It Goes Wrong Fast), 8:26, thumbnail v2 = game-cover-collage, eigenaar: "nieuwe"), ingepland za 28 nov 17:00 NL.
- Short: AA_YjRHlkQw (What If GTA 6 Was Real Life?, 35 s), ingepland za 28 nov 19:00 NL. Na publicatie: in Studio de Short koppelen aan de lange video (Gerelateerde video).
- **Thumbnail bij een game-onderwerp** (eigenaar 27 nov, GTA 6: "zoals de cover van GTA 6 zelf maar dan onze style"): collage van 5 panelen + 1 titelpaneel met witte randen, zonsondergang-kleuren op de achtergrond, poppetjes fel; nooit het echte logo/artwork van de game (beschermd). Voorbeeld: `video-gta-echt/thumbnail2.py`.
- **Stemtempo per ZIN, geen sprongen** (eigenaar 27 nov: "soms praat hij ineens te snel ... zorg dat dat niet meer voorkomt"): `tools/stemtempo.py` zet elke vertellerzin los op ± 195 woorden/min binnen de zin (personages alleen trager als ze te snel zijn); `tools/tempowachter.py` keurt af bij een tempo-SPRONG van meer dan 25% tussen twee vertellerzinnen, een zin onder 160 of boven 225, en afgeraffelde korte uitroepen. Getest op de GTA-stem: oude manier 28 fouten, nieuwe manier 0. Moet 0 zijn vóór het renderen.
- **TikTok @marketdoodle** (eigenaar 27 nov: "ik wil automatisch dat jij alles kan"): posten via Claude in Chrome (extensie in de Chrome van de eigenaar, ingelogd op TikTok). Werkwijze: short kopiëren naar de scratchpad van de sessie (alleen daar mag file_upload lezen, max 10 MB), tiktok.com/tiktokstudio/upload, bestand in de verborgen file-input zetten, bijschrift uit `tiktok/teksten.txt`, onder 'Meer weergeven' **'Door AI gegenereerde content' aan**, en VLAK VOOR 'Plaatsen' de eigenaar om ja vragen. Accountinstellingen (bv. automatische contentcontroles) niet zelf aanzetten. **Elke short gaat op TikTok op hetzelfde tijdstip als op YouTube** (TikTok 'Plannen', eigenaar 27 nov); bestand > 10 MB eerst kleiner maken (± 1,5 Mbit/s). Eerste: haai-short 27 nov ± 15:20.

