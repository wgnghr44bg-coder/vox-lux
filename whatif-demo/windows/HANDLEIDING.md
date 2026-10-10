# IfScape3D op je Windows-pc – handleiding

## Eenmalig: installeren (± 15 min)

1. Open **PowerShell**: druk op Start, typ `PowerShell` en druk op Enter.
2. Plak dit en druk op Enter:

   ```powershell
   New-Item -ItemType Directory -Force C:\AI | Out-Null
   Invoke-WebRequest https://raw.githubusercontent.com/wgnghr44bg-coder/vox-lux/claude/whatif-machine/whatif-demo/windows/setup.ps1 -OutFile C:\AI\setup.ps1
   powershell -ExecutionPolicy Bypass -File C:\AI\setup.ps1
   ```

3. Het script doet het volgende:
   - Het laat eerst een overzicht van je pc zien: Windows, processor, geheugen, videokaart en welke programma's er al zijn.
   - Het vraagt of het ontbrekende programma's mag installeren: Git, Node.js, Python en FFmpeg, via winget en gratis.
     Vraagt Windows daarna om toestemming, klik dan **Ja**.
   - Het zet beide projecten in `C:\AI`. Bestaande mappen worden niet overschreven.
   - Het installeert de onderdelen: three.js, Playwright met Chromium en de Python-pakketten.
   - Het vraagt om je **xAI API-sleutel** (voor het scenario en de stem). Die maak je aan op https://console.x.ai onder *API Keys*.
     Je betaalt per gebruik, ongeveer 5 cent per Short. Je kunt de sleutel ook later invullen in `C:\AI\vox-lux\whatif-demo\.env`.
   - Tot slot maakt het één testbeeld, om te controleren dat alles werkt.
4. Zegt het script dat je PowerShell opnieuw moet openen? Doe dat en draai regel 3 nog een keer.
   Het script kun je altijd veilig opnieuw draaien.

Alleen kijken, niets installeren: `powershell -ExecutionPolicy Bypass -File C:\AI\setup.ps1 -CheckOnly`

## Elke video: één commando

Open een PowerShell-venster en typ:

```powershell
whatif "What if the Sun disappeared?"
```

Er komt geen Claude of Codex aan te pas. De schrijfstap doet **Grok** (xAI), met dezelfde sleutel als de stem. Dan gebeurt dit:

1. **Grok kiest een opzet.** Het kijkt in `onderwerpen.md` of het onderwerp al gemaakt is; is dat zo, dan stopt het.
   Staat het onderwerp al als *gepland* op de lijst, dan gebruikt het dat nummer. Daarna kiest het een plek, een kracht
   en een bestaande Short als voorbeeld.
2. **Grok schrijft het script en het scenario.** Het script is Engels, 175–205 woorden, en begint met "Imagine …".
   Het scenario regelt de shots, de teller en de effecten.
3. **De engine test het scenario zelf.** Laadt het? Klopt de tijdlijn? Lukken de beelden? Klopt het aantal woorden?
   Bij een fout krijgt Grok de melding terug en verbetert het, tot 4 keer.
4. **Grok bekijkt zelf 6 testbeelden.** Kloppen teller, tekst en beeld met wat de stem zegt? Duidelijke fouten verbetert het meteen.
5. **De stem wordt gemaakt** (xAI "atlas") en je krijgt de **6 testbeelden** te zien.
6. PowerShell vraagt: **Goed?**
   - Druk op **Enter** om de video te laten maken.
   - Of typ in gewoon Nederlands wat er anders moet, bijvoorbeeld `het water moet echt de straten in lopen`
     of `derde beeld staat achter een pilaar`. Grok past het aan en je krijgt nieuwe testbeelden.
   - Typ `n` om te stoppen. Later ga je verder met `whatif render <nr>`.
7. **De video wordt gemaakt, met geluid** (stem, achtergrondgeluid en effecten). Dat duurt 10–30 min.
8. **Controle en archief:** speelt de video af, zitten beeld en geluid erin, hapert er niets?
   Daarna worden de bronbestanden bewaard in `C:\AI\ifscape3d-videos` en gaat de mp4 open, met de titel en de TikTok-tekst.

**Kosten:** ongeveer 5–10 cent per Short bij xAI (scenario, controle en stem). Dat gaat van je xAI-tegoed af.
Elke aanpassing na de testbeelden kost ongeveer 1–3 cent.
**Er wordt nooit iets geüpload.** Dat doe je zelf.

De video staat in `C:\AI\vox-lux\whatif-demo\topics\<naam>\<naam>.mp4`.

**Goed om te weten:** Grok maakt een werkende video, maar kijkt minder scherp dan een mens.
Bekijk de 6 testbeelden dus echt, en zeg wat er beter kan. Zo blijft de kwaliteit goed.

## Aanpassen wat je wilt

**Tijdens het maken** (bij de vraag "Goed?"): typ in gewoon Nederlands wat er anders moet. Grok past het aan en je krijgt nieuwe testbeelden.
Dat kan zo vaak als je wilt.

**Na afloop** (de video is al klaar):

```powershell
whatif aanpassen 12 "de climax moet langer duren en eindig met een zonsopkomst"
```

Grok past het scenario aan. Daarna volgen testbeelden, jouw akkoord, een nieuwe video en de controle, net als eerst.
Het nummer staat aan het eind van elke run ("whatif aanpassen 12 ...") en in `onderwerpen.md`.

Zo schrijf je een goede aanpassing:
- **Zeg wat je ziet en wat je wilt**: "beeld 3 staat achter een pilaar, kies een wijd shot van de rivier".
- **Gebruik de tijd of het beeldnummer**: "bij 'Ten metres' moet het water al in de straat staan".
- **Geef een getal waar dat kan**: "laat het water 15 m stijgen", "de stilte bij de climax 6 seconden".
- **Tekst en stem kun je ook aanpassen**: "laatste zin: Where would you go?", "minder getallen, meer gevoel", "stijl A (POV)".
- **Eén of twee punten tegelijk** werkt beter dan tien.

Wat níet kan met een aanpassing: een plek of object dat nog niet in de engine zit (bijvoorbeeld Mars, een ruimtestation
of een vliegtuig van binnen). Grok kiest dan de best passende bestaande plek.

## De camera: de regisseur

Bij elke video kiest de **regisseur** (`director.py`) automatisch per zin de camera:
- Elk camerastandpunt heeft een label in `engine/shots.json`: overzicht, hoog, middel, dichtbij, POV, telelens of lucht, en wat je ziet.
- Grok zegt per zin waar die over gaat en hoe spannend die is.
- Filmregels bepalen de keuze. De video opent met een overzicht. Een detail krijgt een close-up. POV is alleen een kort accent
  (hooguit 3 keer). Na de climax volgt een overzicht. Nooit twee keer hetzelfde shot achter elkaar, en een standpunt hooguit 3 keer.
  Er wordt gewisseld op een pauze in de stem.
- Waar het spannend is, worden 2–3 opties gerenderd en kiest Grok het beeld waarop je het best ziet wat de stem zegt.
  Een beeld dat geblokkeerd wordt door iets op de voorgrond, valt af.
- Nieuwe bouwstenen (zoals het zinkgat) krijgen vanzelf een eigen overzichtsshot en close-up.

Alleen de camera opnieuw laten kiezen, eventueel met een wens:

```powershell
whatif camera 12 "meer close-ups van de auto's, eindig hoog boven de stad"
```

Dat kost ongeveer 1–2 cent.

## Losse stappen

Ga eerst naar de juiste map:

```powershell
cd C:\AI\vox-lux\whatif-demo\windows
```

Na de installatie kun je ook overal `whatif` typen in plaats van `.\whatif.ps1`.

| Commando | Wat het doet |
|---|---|
| `.\whatif.ps1 stills 45` | Maakt de 6 testbeelden (de stem wordt eerst gemaakt) |
| `.\whatif.ps1 render 45` | Rendert de volledige video |
| `.\whatif.ps1 check 45` | Controleert de video en opent hem |
| `.\whatif.ps1 archive 45` | Bewaart de bronbestanden in het archief |
| `.\whatif.ps1 preview street wind` | Laat een plek zien, zonder kosten |
| `python ..\make_topic.py --fix 45 "tekst"` | Laat Grok het scenario van onderwerp 45 aanpassen |

Weigert PowerShell het script? Draai dan eerst `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` en antwoord **J**.

## Problemen

| Melding | Oplossing |
|---|---|
| `Playwright not found` | Draai `npm install -g playwright@1.56.1` en daarna `npx playwright@1.56.1 install chromium` |
| `xAI TTS HTTP 401` | De sleutel in `whatif-demo\.env` klopt niet of ontbreekt |
| `ffmpeg` wordt niet gevonden | Sluit PowerShell, open een nieuw venster en draai `setup.ps1` nog een keer |
| Renderen gaat traag | Zet `WHATIF_GPU=1` in `.env`, of geef minder of meer workers: `.\whatif.ps1 render 45 -Workers 4` |
