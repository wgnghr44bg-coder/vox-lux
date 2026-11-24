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
- Ondertitels onderin, gesproken woord geel, naamlabel bij wie praat. Getallen/labels gloeiend boven hoofden waar het past. Schaduw onder poppetjes.
- Bedragen in één eenheid (bv. alles per jaar).
- **Geen Wan/AI-videoclips** (vervormt, eigenaar: "geen optie").

## Stemmen (OmniVoice, op de pc)
- Verteller: **eigen-stem-swan, speed 1.05** (eigen stem van de eigenaar; geluid alleen op de pc, nooit op GitHub).
- Iedereen houdt zijn **eigen** stem (ook bij een lichaamsruil): jij `whatif-zoon`, papa `whatif-papa`, mama `whatif-moeder2`, zusje `whatif-meisje`, juf `whatif-juf`, baas `whatif-baas`.
- Mama en zusje moeten duidelijk verschillen (eigenaar koos optie A). Elke zin nakijken met Whisper.

## Thumbnail (alleen lange video's)
- Fel oranje met stralen, 1-2 poppetjes met sterke emotie, groot woord bovenin **op een donkere balk met gele rand** (eigenaar koos B). Voorbeeld: `video-swap/drie/thumb.py`.

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
- **Ingepland op YouTube: NIETS** (eigenaar 24 nov: "er staat nu niks gepland"). Volgende plekken: wo 25 nov en za 28 nov (lang 17:00, Short 19:00), onderwerp nog kiezen.

## VASTE WERKWIJZE LANGE VIDEO (eigenaar 24 nov 2026: "zet dit zo vast voor andere nieuwe video's")
Voorbeeld en sjabloon: `video-miljoen/` (What If Everyone on Earth Got $1 Million Tonight?). Eigenaar vond de proef "perfect".
Aanleiding: de eerste lange video (Swapped Lives) kreeg 6 views; AI Studio-analyse: saai begin (regels), stilstaande
poppetjes, uitleg i.p.v. beeld, te kort, onderwerp los van de Shorts.
- **Lengte: minimaal 8 minuten** (± 1.400 woorden, 115 zinnen; tempo ± 178 woorden/min). Steeds gekker met nieuwe gebeurtenissen,
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
