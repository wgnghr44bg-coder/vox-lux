# BlackswanVault NL (plan 21 nov 2026, eigenaar: "dit lijkt me wel interessant")
Nederlandstalige versie van BlackswanVault, op het kanaal dat nu NOIRTRACES heet (NOIRTRACES: 1 video, 0 weergaven).
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
## VASTE STEM (21 nov 2026): `richard-nl`, speed 0.96, seed 1 (proef r2b-seed1; eigenaar koos "Seed1").
Kloon via OmniVoice van het eigen stembestand van de eigenaar; geluid ALLEEN op de pc: C:\Users\rane\vox-lux-stemmen\richard\ref.wav (nooit op GitHub).
Gebruik: VoiceConfig(voice="richard-nl", speed=0.96, seed=1, ...) zoals video9/stem.py. Geen tempo/toonhoogte-trucs achteraf.
## Taal (eigenaar 21 nov): scripts in JUIST Nederlands. Vóór de stem nalezen op spelling (zoveel/zover aaneen), dubbele woorden ("maar ... maar"),
anglicismen en inhoud (bv. "hoeveelheid geheugen", niet "aantal chips"). Na de stem: Whisper (taal nl) per zin; verkeerd verstaan → zin opnieuw met ander seed.
