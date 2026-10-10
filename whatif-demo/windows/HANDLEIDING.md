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

## Elke video: één commando

Open een PowerShell-venster en typ:

```powershell
whatif "What if the Sun disappeared?"
```

Dan gebeurt dit vanzelf:

1. **Codex** schrijft het Engelse script (170–210 woorden) en het scenario: plek, kracht, camerashots en teller.
   Het gebruikt daarvoor de bestaande bouwstenen. Bestaat het onderwerp al, dan stopt het.
2. De **stem** wordt gemaakt (xAI "atlas", ± 1 cent), samen met **6 testbeelden**. Het overzichtsbeeld gaat vanzelf open.
3. PowerShell vraagt: **Goed?**
   - Druk op **Enter** (of typ `j`) om de video te laten maken.
   - Typ wat er anders moet, bijvoorbeeld `meer mensen op straat, laatste beeld een zonsopkomst`.
     Codex past het scenario aan en je krijgt nieuwe testbeelden.
   - Typ `n` om te stoppen. Later ga je verder met `whatif render <nr>`.
4. De **video wordt gerenderd en het geluid wordt eronder gezet**: stem, achtergrondgeluid en effecten.
   Dat duurt 10–30 min. Je hoeft niets te doen.
5. Er volgt een **controle**: speelt de video af, zitten beeld en geluid erin, klopt de lengte, hapert er niets?
6. De **bronbestanden** worden bewaard in `C:\AI\ifscape3d-videos`, en de mp4 gaat open.
   Daarbij krijg je de titel en de TikTok-tekst te zien.

De video staat in `C:\AI\vox-lux\whatif-demo\topics\<naam>\<naam>.mp4`.
**Er wordt nooit iets geüpload.** Dat doe je zelf.

Wil je liever in Codex zelf werken? Open Codex in `C:\AI\vox-lux\whatif-demo` en typ
*Maak een What if-Short over "…"*. Codex volgt dan dezelfde stappen uit `AGENTS.md`.

## Zelf de commando's draaien (zonder Codex)

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

Weigert PowerShell het script? Draai dan eerst `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` en antwoord **J**.

## Problemen

| Melding | Oplossing |
|---|---|
| `Playwright not found` | Draai `npm install -g playwright@1.56.1` en daarna `npx playwright@1.56.1 install chromium` |
| `xAI TTS HTTP 401` | De sleutel in `whatif-demo\.env` klopt niet of ontbreekt |
| `ffmpeg` wordt niet gevonden | Sluit PowerShell, open een nieuw venster en draai `setup.ps1` nog een keer |
| Renderen gaat traag | Zet `WHATIF_GPU=1` in `.env`, of geef minder of meer workers: `.\whatif.ps1 render 45 -Workers 4` |
