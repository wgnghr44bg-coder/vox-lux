# Market Doodle — What If: vaste afspraken (eigenaar 22-23 nov 2026)

Voor elk Claude-account dat hiermee verdergaat. Kanaal @marketdoodle, token `YT_REFRESH_TOKEN_ALTERAQON`. FOCUS-kanaal.

## Wat het kanaal is
- Breed **What If** (niet alleen geld), Engels, voor de VS. Verhalen met **poppetjes die met code getekend zijn** (geen AI-video).
- Niche gekozen met `tools/niche_scan.py` (uitslag `kanalen/niche/ALLE-NICHES.md`): what if = geen grote kanalen, veel kleine winnaars.

## Ritme
- **3 lange video's per week**: ma, wo, vr, ± 3 min, **liggend** 1920x1080 (liggend telt als lange video = kijkuren). 17:00 NL, nog te bevestigen.
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

## Online
- Short: Qhjfoib3FIA (What If You Could See How Much Everyone Earns?), 23 nov.
- Lang: jJacEFpBrXY (What If You Swapped Lives With Your Dad for a Week?), 23 nov.
