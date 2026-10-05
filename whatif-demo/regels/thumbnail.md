# Thumbnail voor lange video's


Elke lange IfScape3D-video krijgt bij de upload meteen een thumbnail in de vaste stijl van
`branding/thumbnail-voorbeeld.jpg` (de wind-video), in de stijl van het grote What If-kanaal. Shorts: geen thumbnail.

Doel: altijd pakkend. De kijker moet nieuwsgierig worden en willen klikken. Laat het spannendste moment zien,
maar niet de afloop (wat gebeurt er hierna?); het getal moet verbazen (extreem, onverwacht). Vraag jezelf vóór
gebruik af: zou ik hierop klikken als ik door YouTube scroll? Zo niet: ander moment, groter onderwerp, minder tekst.

Stijl (elke keer hetzelfde, passend bij het onderwerp):
- 1280x720. Achtergrond = een echt frame uit de eigen 3D-video (plek van de climax), iets verzacht.
- Rechts groot en dichtbij waar de video om draait (het hoofdonderwerp: bij dinosaurussen een T-rex, bij wind
  wegvliegende auto's, bij kou een bevroren brug …), met de echte low-poly modellen uit de video,
  uitvergroot, schuin/wegvliegend, met witte snelheidsstrepen of ander effect dat bij de kracht past.
- Links weinig tekst, dik schreefloos lettertype (heavy, hoofdletters), wit met donkere rand/schaduw:
  hooguit 3 regels, één groot getal of extreem in geel (bv. "OVER | 1,000 | KM/H", "2X | GRAVITY", "−100 °C").
- Logo (bol met ring) linksboven. Rechtsonder leeg (videolengte).
- Geen gewonden, geen bloed; poppetjes mogen wel zichtbaar in de kracht staan.

Werkwijze:
1. Klaarzetten: `pip install -q fonttools brotli pillow`.
2. Achtergrond: frame uit de video (`ffmpeg -ss <s> -i <video> -frames:v 1 bg.png`), liefst zonder teller in beeld;
   modellen los renderen uit de engine (zelfde plek/props, transparante achtergrond) en erop plakken.
   (`whatif-demo/ifscape_thumbnail.py` maakt nog de oude, rustige stijl; alleen gebruiken als basis/noodoptie.)
3. Controle vóór gebruik: zelf openen en kijken: actie goed zichtbaar en niet achter de tekst, tekst leesbaar
   op telefoonformaat, logo staat erop, getal klopt met de video.
4. Uploaden: `tools/youtube_upload.py … --thumbnail <map>/thumbnail.jpg`, zodat hij er meteen op staat zodra de
   video live gaat (werkt sinds okt 2026). Lukt het niet: thumbnail naar de eigenaar sturen met
   YouTube Studio → Content → video → Thumbnail → Uploaden → Opslaan.

