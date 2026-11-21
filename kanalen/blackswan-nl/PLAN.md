# GELDVERHAAL — BlackswanVault NL (plan 21 nov 2026, eigenaar: "dit lijkt me wel interessant")
Nederlandstalige versie van BlackswanVault, op het kanaal dat nu NOIRTRACES heet (NOIRTRACES: 1 video, 0 weergaven).

## STAND 21 nov 2026 13:05 (voor een ander account: begin hier)
- NAAM: **Geldverhaal** (eigenaar: "maak er maar van Geldverhaal"), handle **@Geldverhaal** (was vrij op 21 nov).
- Eigenaar zet in Studio NU: naam, beschrijving (`branding/kanaalbeschrijving.txt`), taal Nederlands, logo `branding/logo-definitief.png`,
  banner `branding/banner-definitief.jpg` (gekozen: logo munt + banner DONKER (alleen gouden beurslijn, donker.py); opnieuw maken: `python branding/maak.py`).
- 21 nov 13:20 VIA API GEDAAN: banner (banner-definitief.jpg, 'Alles over financiën'), beschrijving, zoekwoorden, taal nl, land NL.
  NIET via API mogelijk → eigenaar in Studio: kanaalNAAM 'Geldverhaal' en LOGO (profielfoto).
- HANDLE pas rond 2 dec 2026 te wijzigen (YouTube: 14 dagen na de vorige wijziging op 18 nov).
- Upload-token: `YT_KANAAL=altena` (sleutel ~/.yt-altena.json, zie CLAUDE.md). AI-label staat aan (ook op de oude Jack the Ripper-video).
- Vaste stem, schrijfstijl, NL-wachter: zie hieronder. VOLGENDE STAP: eerste 2-3 Nederlandse video's maken vóór 2 dec (eerst laten zien, uploaden pas na OK).
  Kandidaten: RAM (reserve1-ram, feiten nagekeken; NL-kant ASML), Costco (reserve3), ASML -9,3% (NL-wachter 21 nov), box 3 (leeft op NL-YouTube).
- Oude video "Who Was Jack the Ripper?" (AXKM1BEMq10) past niet meer bij het kanaal: eigenaar vragen of die privé mag.
## Afspraken
- Geen 1-op-1 vertaling (risico "hergebruikte inhoud" bij partnerprogramma): elk verhaal een Nederlandse kant (ASML, AEX, euro's, wat betekent het voor NL),
  eigen Nederlandse stem, titels, thumbnails en tekst in beeld.
- Beelden: ZOVEEL MOGELIJK ECHTE beelden en foto's (Wikimedia, vrije licentie), AI alleen waar dat niet kan (eigenaar 21 nov).
- Kanaal staat LOS van BlackswanVault (eigenaar 21 nov: "dit staat los van blackswan"): niet noemen in beschrijving of video's. Wel: eigen NL-inhoud, AI-label aan.
## Stappen
1. Proefstemmen (KLAAR 21 nov 11:35): stemproef/stem-a..d.mp3 (a man middelbaar, b man lager, c man jonger, d vrouw); alle vier door Whisper woord voor woord verstaan. Eigenaar kiest.
2. Eigenaar: kanaal hernoemen in Studio (naam, handle, beschrijving, taal Nederlands). Naam nog kiezen.
3. Eén testvideo (NL-versie van een sterke video, bv. Nvidia/Jensen) → laten zien → na 2 weken kijken of het aanslaat.
## Beelden (eigenaar 21 nov): echte beelden moeten GOED zijn en PASSEN bij wat er gezegd wordt; anders liever een goed AI-beeld.
## NL-wachter (21 nov): `tools/nl_wacht.py`, taak "BlackswanVault NL-wachter" 08:20 en 16:05 → stories/nl-hype.json
- Nieuws: nu.nl Economie, Financieel Dagblad, NOS Economie (RSS, 36 uur). Koersen: AEX + ASML, Shell, ING, Adyen, Prosus, Unilever, Ahold, Heineken, Philips, ABN, BESI, bitcoin (EUR).
- YouTube NL (regio NL, taal nl, 72 uur). Gevonden NL-kanalen over geld: DoopieCash, Geld op Geld, DeAandeelHouder TV, Focuss Op Financiën (nog toevoegen als "kanalen zoals wij").
- Eerste uitslag 21 nov: ASML -9,3% (GROOT), AI-aandelen uitverkoop na Anthropic (FD+NOS), goud daalt; YouTube NL: Anthropic-beursgang, bitcoin.
## VASTE STEM (21 nov 2026, bijgewerkt): `richard-nl` met OmniVoice, speed 1.1, seed 1, pauze 0.28 s tussen zinnen (na een vraag 0.45 s).
Eigenaar koos eerst seed 1 (0.96), wilde sneller; na herschreven tekst in natuurlijk Nederlands: "1 klinkt nu wel goed" (OmniVoice boven Chatterbox). Voorbeeld: stemproef/proef1min.py.
Kloon via OmniVoice van het eigen stembestand van de eigenaar; geluid ALLEEN op de pc: C:\Users\rane\vox-lux-stemmen\richard\ref.wav (nooit op GitHub).
Gebruik: VoiceConfig(voice="richard-nl", speed=0.96, seed=1, ...) zoals video9/stem.py. Geen tempo/toonhoogte-trucs achteraf.
## Taal (eigenaar 21 nov): scripts in JUIST Nederlands. Vóór de stem nalezen op spelling (zoveel/zover aaneen), dubbele woorden ("maar ... maar"),
anglicismen en inhoud (bv. "hoeveelheid geheugen", niet "aantal chips"). Na de stem: Whisper (taal nl) per zin; verkeerd verstaan → zin opnieuw met ander seed.
## Schrijfstijl NL (21 nov, eigenaar: "vergelijk het script echt met andere Nederlandse tekst")
Vergeleken met NOS/nu.nl Economie (gem. 16,6 woorden per zin; onze vertaalde proef 11,4 met Engelse zinsbouw):
- Schrijf zoals een Nederlander praat, niet vertaald: "Kort gezegd:" i.p.v. "Het korte antwoord is:", "Hoe kan dat?" i.p.v. "Dus wat is er gebeurd?",
  "kwam uit op", "inmiddels", "ruim", "vrijwel", "vorig jaar zomer"; werkwoord achteraan in bijzinnen is goed.
- Niet alleen korte hakzinnen; afwisselen met normale zinnen met "want", "en", "toch".
- Geen Engelse woordvolgorde of uitdrukkingen ("haalde binnen", "simpelweg"), geen dubbele woorden; spelling (zoveel, zover).
- Klemtoon: OmniVoice legt Nederlandse klemtoon soms verkeerd (model vooral Engels/Chinees) → Chatterbox Multilingual (taal nl) getest als alternatief.
## Onderwerp kanaal (eigenaar 21 nov): geldzaken, bedrijven, beleggen ("zoals DoopieCash, investeren enz.").
Onze stijl: uitleg met verhalen + Nederlandse kant (ASML, AEX, box 3, sparen, huizen), GEEN persoonlijk beleggingsadvies (AFM) → "Dit is geen beleggingsadvies."
Naamvoorstellen (handles 21 nov gecheckt): Het Geldverhaal @Geldverhaal (advies), Beurs & Bedrijven, Zwarte Zwaan, BlackswanVault NL — vrij; Geld Uitgelegd en Geldzaken bezet.

## NL-wachter uitgebreid (21 nov 13:15, eigenaar: "aandelen bedrijven wereldwijd, niet beperken tot AEX; wat is nu hype in Nederland")
- Koersen: AEX + NL-bedrijven + wereldwijd (Nvidia, Apple, Tesla, Microsoft, Broadcom, S&P, Nasdaq, olie, goud, bitcoin).
- Nieuwsnamen: ook buitenlandse bedrijven (Tesla, Apple, OpenAI, Anthropic, SpaceX, Intel, Samsung, Boeing, ...).
- Kanalen zoals wij (NL): DoopieCash, Focuss Op Financiën, DeAandeelHouder TV, Tom Lassing - Beursbox, Geld op Geld, Investeren doe je zo.
- Seintje ntfy "Geldverhaal: hype?" (zelfde ntfy-kanaal als BlackswanVault), max 1x per onderwerp per dag (stories/nl-seintjes.txt).
- Website: kolom "Geldverhaal" in "Hype nu" (docs/status, data uit stories/nl-hype.json).
- Eerste uitslag: Anthropic STERK (7 NL-kanalen), Nvidia STERK; uitschieters: "Aandelen dalen hard" (Geld op Geld 31x), Anthropic (DoopieCash 22x).
## Grafieken (eigenaar 21 nov): in ELKE koersgrafiek de top en het laagste punt tonen (groene/rode stip + "Top €1.721" / "Laagste €1.168"),
verschijnt pas als de lijn er is. Code: proef-asml/render.py, lijn(..., hoog_laag=True). Geldt ook voor BlackswanVault (overnemen in videoN/render.py).
## Stem: PER ZIN inspreken (stem.py) — eigenaar 21 nov na vergelijking: "hou het op de vorige proef, die is beter als de laatste".
Alinea-methode hieronder is GETEST EN AFGEWEZEN (niet gebruiken). Wel: afkorting A E X als letters schrijven; ASML gewoon (werd goed uitgesproken).
(oud) Alinea-proef:
`proef-asml/stem_alinea.py`: hele @scene in één keer (zinnen lopen door), Whisper-woordtijden voor zinsgrenzen, cache per alinea
(`--opnieuw 2 --seed 40` = alleen alinea 2 opnieuw). Afkortingen in script.txt als losse letters: "A S M L", "A E X". Controle: `check_nl.py --alinea`.
## Beelden en personen (eigenaar 21 nov): "gebruik de echte beelden die mogen, maar geen personen plaatsen die het niet zijn".
Echte foto alleen van de ECHTE persoon (bv. Jensen Huang, Dario Amodei). AI-beelden: GEEN mensen (prompt: no people, no humans, no hands).
## Thumbnail-stijl Geldverhaal (eigenaar 21 nov: "moet echt anders, lijkt teveel op Swan"): `thumb_geld.py`
Beeld over de hele thumbnail (geen donkere linkerkant), zwarte tekst in GOUDEN balken, getal wit in ROOD blok, Segoe UI Black,
Geldverhaal-logo rechtsboven. Nooit de Swan-stijl (Impact, rood/wit met zwarte rand, donkere linkerkant).
## Uitspraak: "Claude" NIET laten uitspreken (OmniVoice NL zegt "kloot"/"klad"/"cloud"; 21 nov getest). Zeg "een van de bekendste chatbots", toon "Claude" in beeld.

## Cijfers vergelijken: ntfy-seintje ma 7 dec 2026 10:00 (taak "Geldverhaal cijfers 7 dec", tools/herinner_geldverhaal.py) = 2 weken na de eerste video (gepland ± 23 nov). Komt de eerste video later online, de datum in de taakplanner meeschuiven.

## VASTE WERKWIJZE NIEUWSKANALEN (eigenaar 21 nov 2026: "voor sleep kun je best vooruit werken, maar voor swan lijkt het me lastig als je echt live nieuws wilt brengen")
Geldt voor BlackswanVault en Geldverhaal (Sleep Archives mag wél ver vooruit).
1. Nieuwsvideo's hooguit 1-2 dagen vooruit maken (zelfde dag of dag ervoor); nooit een week op de plank.
2. Elke ochtend kiezen de wachters het onderwerp (nieuwswacht 08:00, swan_yt_wacht 08:10, nl_wacht 08:20; seintje bij grote hype).
3. Dagen zonder groot nieuws: reservevideo's die niet verouderen (RAM, Costco, Intel, ...) — die mogen wél vooruit.
4. Shorts op dezelfde dag als de lange video.
5. Toch al vooruit ingepland nieuws: de avond ervoor actualiteitscheck (koersen veranderd? slotzin/titel aanpassen).
Eigenaar opent dagelijks Claude voor onderwerp en akkoord; zonder Claude maakt de pc geen nieuwe nieuwsvideo.
