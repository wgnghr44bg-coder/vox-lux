# GELDVERHAAL — BlackswanVault NL (plan 21 nov 2026, eigenaar: "dit lijkt me wel interessant")
Nederlandstalige versie van BlackswanVault, op het kanaal dat nu NOIRTRACES heet (NOIRTRACES: 1 video, 0 weergaven).

## STAND 21 nov 2026 13:05 (voor een ander account: begin hier)
- NAAM: **Geldverhaal** (eigenaar: "maak er maar van Geldverhaal"), handle **@Geldverhaal** (was vrij op 21 nov).
- Eigenaar zet in Studio NU: naam, beschrijving (`branding/kanaalbeschrijving.txt`), taal Nederlands, logo `branding/logo-definitief.png`,
  banner `branding/banner-definitief.jpg` (gekozen: logo munt + banner A grachten; opnieuw maken: `python branding/maak.py`).
- HANDLE pas rond 2 dec 2026 te wijzigen (YouTube: 14 dagen na de vorige wijziging op 18 nov).
- Upload-token: `YT_KANAAL=altena` (sleutel ~/.yt-altena.json, zie CLAUDE.md). AI-label staat aan (ook op de oude Jack the Ripper-video).
- Vaste stem, schrijfstijl, NL-wachter: zie hieronder. VOLGENDE STAP: eerste 2-3 Nederlandse video's maken vóór 2 dec (eerst laten zien, uploaden pas na OK).
  Kandidaten: RAM (reserve1-ram, feiten nagekeken; NL-kant ASML), Costco (reserve3), ASML -9,3% (NL-wachter 21 nov), box 3 (leeft op NL-YouTube).
- Oude video "Who Was Jack the Ripper?" (AXKM1BEMq10) past niet meer bij het kanaal: eigenaar vragen of die privé mag.
## Afspraken
- Geen 1-op-1 vertaling (risico "hergebruikte inhoud" bij partnerprogramma): elk verhaal een Nederlandse kant (ASML, AEX, euro's, wat betekent het voor NL),
  eigen Nederlandse stem, titels, thumbnails en tekst in beeld.
- Beelden: ZOVEEL MOGELIJK ECHTE beelden en foto's (Wikimedia, vrije licentie), AI alleen waar dat niet kan (eigenaar 21 nov).
- Kanaalbeschrijving: open zeggen dat het de Nederlandse versie van BlackswanVault is. AI-label aan.
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
