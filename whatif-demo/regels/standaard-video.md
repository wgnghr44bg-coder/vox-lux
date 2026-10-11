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

## Verhaal en stem
- Engels, ± 45–60 s, ± 130 woorden. Eerste woord "Imagine…" + het onderwerp.
- Opbouw: rustig begin → oorzaak → kleine tekens → spanning (mensen weg) → climax met ± 3 s stilte →
  getallen → echte voorbeelden (twist) → slotvraag aan de kijker.
- Stem: xAI Atlas, **tempo 1.00** (eigenaar, 11 okt 2026), één take, documentairepauzes (make_whatif.one_take).
- Eenheden Europees (m, km, km/h, °C).
- Elke feitelijke bewering klopt en is controleerbaar: bronnen in `upload.json` ("bronnen"), voorzichtig formuleren ("roughly").

## Werkwijze
1. Eerst alleen testbeelden (overzichtsplaat ± 6 shots) naar de eigenaar; géén stem of video vóór akkoord.
2. Na akkoord: stem → geluid (make_sound.py) → render (1080x1920, op de achtergrond met lange timeout: ± 35 min).
3. Controle: 1080x1920, duur, geluid, `ffmpeg -v error -i x.mp4 -f null -`, overzichtsplaat bekijken.
4. Kijkversie < 30 MB naar de eigenaar (SendUserFile) + TikTok-tekst; die versie gaat in git.
5. YouTube alleen na akkoord van de eigenaar: kanaal whatif, openbaar, playlist "What If".
   Beschrijving kort en zonder alles te verklappen (begin van het verhaal + vraag aan de kijker + 3–4 hashtags).
