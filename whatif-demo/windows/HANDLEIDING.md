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
   - Het vraagt om je **xAI API-sleutel** voor de stem. Die maak je aan op https://console.x.ai onder *API Keys*.
     Je betaalt per gebruik, ongeveer 1 cent per Short. Je kunt de sleutel ook later invullen in `C:\AI\vox-lux\whatif-demo\.env`.
   - Tot slot maakt het één testbeeld, om te controleren dat alles werkt.
4. Zegt het script dat je PowerShell opnieuw moet openen? Doe dat en draai regel 3 nog een keer.
   Het script kun je altijd veilig opnieuw draaien.

Alleen kijken, niets installeren: `powershell -ExecutionPolicy Bypass -File C:\AI\setup.ps1 -CheckOnly`

## Elke video: alleen een onderwerp geven

Open Codex in de map `C:\AI\vox-lux\whatif-demo` en typ bijvoorbeeld:

> Maak een What if-Short over "What if the Sun disappeared?"

Codex volgt dan `AGENTS.md`:

1. Codex schrijft het script en het scenario met de bestaande bouwstenen.
2. Codex maakt de stem en **6 testbeelden**. Je krijgt het overzichtsbeeld te zien.
3. Jij zegt **"goed"**, of wat er anders moet.
4. Codex rendert de volledige video. Dat duurt 10–30 min.
5. Codex controleert de mp4: is hij er, speelt hij af, zitten beeld en geluid erin, klopt de lengte?
6. Codex bewaart de bronbestanden in `C:\AI\ifscape3d-videos`.

De video staat daarna in `C:\AI\vox-lux\whatif-demo\topics\<naam>\<naam>.mp4`.
**Er wordt nooit iets geüpload.** Dat doe je zelf.

## Zelf de commando's draaien (zonder Codex)

Ga eerst naar de juiste map:

```powershell
cd C:\AI\vox-lux\whatif-demo\windows
```

| Commando | Wat het doet |
|---|---|
| `.\whatif.ps1 stills 45` | Maakt de 6 testbeelden (de stem wordt eerst gemaakt) |
| `.\whatif.ps1 render 45` | Rendert de volledige video |
| `.\whatif.ps1 check 45` | Controleert de video en opent hem |
| `.\whatif.ps1 archive 45` | Bewaart de bronbestanden in het archief |
| `.\whatif.ps1 preview street wind` | Laat een plek zien, zonder kosten |

Weigert PowerShell het script? Draai dan eerst `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` en antwoord **J**.

## Problemen

| Melding | Oplossing |
|---|---|
| `Playwright not found` | Draai `npm install -g playwright@1.56.1` en daarna `npx playwright@1.56.1 install chromium` |
| `xAI TTS HTTP 401` | De sleutel in `whatif-demo\.env` klopt niet of ontbreekt |
| `ffmpeg` wordt niet gevonden | Sluit PowerShell, open een nieuw venster en draai `setup.ps1` nog een keer |
| Renderen gaat traag | Zet `WHATIF_GPU=1` in `.env`, of geef minder of meer workers: `.\whatif.ps1 render 45 -Workers 4` |
