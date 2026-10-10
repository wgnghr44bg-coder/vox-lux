# IfScape3D – instructies voor Codex (lokale Windows-pc)

De eigenaar geeft alleen een onderwerp, bijvoorbeeld: *Maak een What if-Short over "What if the Sun disappeared?"*.
Jij maakt daarvan een Short met de bestaande engine. Antwoord kort en in het Nederlands.

## Harde regels

- **Nooit uploaden of publiceren.** Gebruik `publish_whatif.py` en `tools/youtube_upload.py` niet.
- **Altijd stoppen na de testbeelden.** Je mag pas verder renderen als de eigenaar "goed" zegt.
- Gebruik de bestaande engine: `engine/places/*` voor plekken, `engine/forces/*` voor krachten en de bakstenen uit de tabel in
  `AUTOMATISCH.md` ("De engine"). Bouw alleen iets nieuws als het onderwerp echt niet past, en kopieer dan de meest verwante plek of kracht.
- Zet nooit sleutels in code of git. Sleutels staan in `whatif-demo/.env`, en dat bestand staat niet in git.
- Voeg geen betaalde dienst toe zonder eerst de kosten te melden. De stem (xAI "atlas") kost ± 1 cent per Short.
- Overschrijf of verwijder geen bestaande topics of video's.
- Commit naar je eigen branch in `vox-lux`. Push alleen als de eigenaar dat vraagt.

## Werkwijze per onderwerp

Alle commando's draaien vanuit `C:\AI\vox-lux\whatif-demo\windows`.

1. **Controleren.** Kijk in `onderwerpen.md` ("Al op het kanaal" en de tabel) of het onderwerp nog niet bestaat.
   Bestaat het al: meld dat en stop.
2. **Nummer en rij.** Voeg onderaan de tabel in `onderwerpen.md` een rij toe met het volgende vrije nummer, de vraag
   (zonder "What if"), de plek, de kracht en status `in de maak <datum>`.
3. **Scenario.** Dit is het enige creatieve werk.
   - Maak `topics/<slug>/scenario.js` door de meest verwante bestaande Short te kopiëren,
     bijvoorbeeld `topics/gravity-doubled/scenario.js` (stijl B), `topics/moon-closer/scenario.js` (stijl A) of `topics/earth-stopped/scenario.js`.
   - Pas aan: `topic` (`number`, `slug`, `place`, `force`, `question`, `title`), teller, `lines`, shots, beats, `end` en `upload`.
   - Volg de regels uit `AUTOMATISCH.md`: hoofdstuk 2 (scriptregels, beeldregels en camerastijl) en "Losse regels"
     (stem atlas 1.05, Europese eenheden).
   - Kort samengevat: Engels, 170–210 woorden, de eerste zin is "Imagine" + het onderwerp, alleen natuurkunde die klopt,
     rustige opbouw, de teller loopt mee, een stille climax en een mooi laatste beeld.
     Wat de stem zegt, is te zien. Geen gewonden, geen eindkaart.
   - Wissel om en om tussen stijl A en B: `regels/stijl-afwisseling.md`.
4. **Zes testbeelden.** Draai `.\whatif.ps1 stills <nr>`. Dit maakt eerst de stem.
   - Bekijk `topics/<slug>/stills/overzicht.jpg` zelf kritisch tegen de beeldregels.
   - Hooguit één keer bijsturen.
   - Laat het overzicht dan aan de eigenaar zien en **wacht op goedkeuring**.
5. **Volledige video** (na "goed"). Draai `.\whatif.ps1 render <nr>`. Dat duurt ± 10–30 min, afhankelijk van de pc.
   Resultaat: `topics/<slug>/<slug>.mp4` (1080×1920, 30 fps) en `upload.json`.
6. **Controle.** Draai `.\whatif.ps1 check <nr>`. Je moet "CONTROLE GOED" zien, de video heeft een videostroom én een audiostroom,
   en de duur is ± 60–100 s. Volg daarnaast `regels/qc.md` punt 2–4, met de hand.
   - Faalt de controle: repareer en draai opnieuw. Bij een renderfout: `render`. Alleen geluid: `python ..\make_whatif.py <nr> --from audio`.
   - Faalt het daarna nog steeds: niet doorgeven, wel melden wat er mis is.
7. **Bewaren.** Draai `.\whatif.ps1 archive <nr>`. Dit kopieert de bronbestanden naar `C:\AI\ifscape3d-videos\<datum>-<slug>\` en commit lokaal.
   - Commit eerst je engine-wijzigingen in `vox-lux`, zodat `ENGINE.txt` naar de juiste commit wijst.
   - Push het archief alleen als de eigenaar dat vraagt.
8. **Afronden.** Zet de status in `onderwerpen.md` op `gemaakt <datum>, bij eigenaar (niet geüpload)`.
   Meld de eigenaar:
   - de titel;
   - de stijl (A of B);
   - het pad naar de mp4;
   - de TikTok-tekst (`tiktok` uit `upload.json`);
   - of de controle goed was.

## Handig

- Een plek bekijken zonder onderwerp, zonder kosten: `.\whatif.ps1 preview <plek> <kracht>`, bijvoorbeeld `preview street wind`.
- Eigen tijden voor de testbeelden: `.\whatif.ps1 stills <nr> -Times 5,20,35,50,60,75`.
- Sneller renderen met de videokaart: zet `WHATIF_GPU=1` in `.env`. Het beeld kan dan iets afwijken van de cloud-renders.
- `AUTOMATISCH.md` is geschreven voor de dagelijkse cloudsessie van Claude. Upload, `USAGE.md` en TikTok-pagina gelden hier
  **niet**. De regels voor script, beeld en engine gelden wel.
