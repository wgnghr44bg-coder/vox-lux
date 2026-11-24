# Market Doodle — What If: vaste afspraken (eigenaar 22-23 nov 2026)

Voor elk Claude-account dat hiermee verdergaat. Kanaal @marketdoodle, token `YT_REFRESH_TOKEN_ALTERAQON`. FOCUS-kanaal.

## Wat het kanaal is
- Breed **What If** (niet alleen geld), Engels, voor de VS. Verhalen met **poppetjes die met code getekend zijn** (geen AI-video).
- Niche gekozen met `tools/niche_scan.py` (uitslag `kanalen/niche/ALLE-NICHES.md`): what if = geen grote kanalen, veel kleine winnaars.

## Ritme
- **Vaste dagen ma, wo, za** (eigenaar 23 nov avond, zelfde dagen als BlackswanVault): **lange video 17:00 NL** (± 3 min, **liggend** 1920x1080), **Short 19:00 NL** op dezelfde dag.
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
