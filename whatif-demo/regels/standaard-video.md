# Standaard IfScape3D-video (eigenaar, 11 okt 2026) – lees dit eerst

De eigenaar: "zo wil ik alle video's voor IfScape3D hebben". Voorbeeld: **What if a giant sinkhole appeared downtown?**
(`sinkhole-downtown/`, https://youtu.be/830xM-fU-d4). Deze regels gaan vóór oudere regels die ermee botsen
(logo-moment, POV-stijl A / A-B-afwisseling, eindkaart, tempo 1.05).

## Beeld
- Low-poly 3D (stijl gravity-straatversie): echte plek met auto's, simpele poppetjes, gebouwen; verticaal 1080x1920.
- Eén doorlopende, spannende camerabeweging (geen harde cuts): begint op ooghoogte, gaat mee met wat er gebeurt
  (bij sinkhole: van straatniveau omhoog tot hoog boven het gat).
- Titel in schreefletter (Playfair) in beeld bij de start; daarna linksboven klein label + groot getal
  (bijv. DEPTH 90 m) met eventueel een tweede regel (WIDTH 100 m). Korte kernzin als caption (cursief) bij de feiten.
- GEEN logo of watermerk, GEEN eindkaart, GEEN zwart eindscherm met tekst: het laatste beeld blijft staan.
- Wat de stem zegt, zie je (lek → water bij putdeksel, scheuren, politie + hekken, kruispunt valt weg, gat groeit).
- Geen geweld, geen herkenbare personen; mensen en auto's zijn veilig weg (check in de scène: minimale afstand > 5 m).

## Verhaal en stem: opbouw en stem van de gravity-video (eigenaar, 11 okt 2026)
Voorbeeld: "What if gravity suddenly doubled?" (branch claude/whatif-gravity-doubled, `whatif-demo/gravity-doubled/script.txt`).
Elke video volgt die opbouw, aangepast aan het onderwerp (nooit zinnen letterlijk overnemen):
1. "Imagine… [pause] in a single second/minute, <het onderwerp gebeurt>." + één zin wat dat betekent.
2. Waar je staat: "You are standing on/at …" (de plek in beeld).
3. Het normale getal → het nieuwe getal (zoals 9,8 → 19,6 m/s²); de teller loopt mee.
4. Wat je zelf merkt (lichaam, gewicht, oren), met een getal erbij ("If you weighed …").
5. Mensen reageren (stoppen, gaan zitten, lopen weg); auto's, bomen, dingen op straat.
6. Een natuurkundig feit met getal.
7. Het escaleert: dingen breken/vallen, één groot beeld (de kraan).
8. Uitleg waarom het misgaat ("Buildings are designed with a safety margin. But …").
9. Climax met stilte (meerdere [long pause]; in `lines` een getal, ± 3–4 s).
10. Nasleep: het stof zakt, wat er nog staat.
11. Slotzin die blijft hangen (geen vraag nodig): de blijvende gevolgen voor "you".
- Lengte ± 60–90 s (130–200 woorden). Engels, "you", Europese eenheden. Feiten kloppen en staan met bronnen in `upload.json`.
- Stem: **xAI Lux, tempo 0.9, per zin ingesproken met vaste pauzes** ([pause] 0,5 s, [long pause] 1 s, 0,3 s na een zin):
  `tools/xai_voiceover.py` (standaard in make_whatif.py: VOICE lux, SPEED 0.9, oneTake uit). Gemeten: zelfde toonhoogte (± 130 Hz)
  en tempo als de gravity-video. Niet zelf een andere stem kiezen.

## Werkwijze
1. Eerst alleen testbeelden (overzichtsplaat ± 6 shots) naar de eigenaar; géén stem of video vóór akkoord.
2. Na akkoord: stem → geluid (make_sound.py) → render (1080x1920, op de achtergrond met lange timeout: ± 35 min).
3. Controle: 1080x1920, duur, geluid, `ffmpeg -v error -i x.mp4 -f null -`, overzichtsplaat bekijken.
4. Kijkversie < 30 MB naar de eigenaar (SendUserFile) + TikTok-tekst; die versie gaat in git.
5. YouTube alleen na akkoord van de eigenaar: kanaal whatif, openbaar, playlist "What If".
   Beschrijving kort en zonder alles te verklappen (begin van het verhaal + vraag aan de kijker + 3–4 hashtags).

## Nieuw onderwerp maken (engine, sinds 11 okt 2026)
De engine (`engine/`) maakt de standaard vanzelf zodra een scenario een `camPath` heeft: titel in beeld, geen logo,
geen fade/eindkaart, één doorlopende camerabeweging (Catmull-Rom door de punten). Sjabloon: `topics/standaard-sinkhole/`
(de sinkhole-video op plek `street` + kracht `sinkhole`).
1. Kopieer `topics/standaard-sinkhole/` naar `topics/<slug>/`; pas aan: `topic` (slug, place, force, title), `lines`
   (± 130 woorden, "Imagine…", stille climax als getal), `hud`/`counter` (label + getal, tweede regel via `second.fn(v, t)`),
   `camPath` ([t, positie, kijkpunt]), `beats`, `captions`, `upload` (beschrijving zonder spoilers).
2. Kies een bestaande plek (`engine/places/`: street, river-city, boulevard, harbor, mountain-village, nature-park, suburb,
   airport, colosseum, prehistoric, indoors) en kracht (`engine/forces/`: wind, cold, heat, quake, water, tide, gravity,
   eruption, alien, day, sinkhole). Alleen bouwen wat echt nog niet bestaat.
3. Mensen veilig weg: `beats.shelter` (+ `flee: [x, z]` om ze weg te laten lopen in plaats van naar binnen).
4. `python3 make_whatif.py <nr> --stills` → testbeelden naar de eigenaar; na akkoord `python3 make_whatif.py <nr>`
   (stem Atlas 1.00, render, geluid, mp4). Render op de achtergrond met lange timeout.
