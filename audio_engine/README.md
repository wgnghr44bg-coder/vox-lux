# Audio Engine (lokaal, gratis)

Stem en achtergrondmuziek voor documentaires, Shorts en What If-video's, helemaal op de eigen pc:

De vaste combinatie heet **"B1-stem met achtergrondmuziek"** (kort **B1**, eigenaar 7 nov 2026): stem `narrator-e`
met de muziekstijl `referentie` eronder.

- **Stem:** OmniVoice op de videokaart (RTX 2080 SUPER). De vaste verteller is **narrator-e**: een oudere Britse man,
  door de eigenaar gekozen op 7 nov 2026 (proef B1), rustiger en warmer dan de vorige (narrator-b). Hij is ontworpen,
  niet van iemand gekloond. Video-instellingen: speed 0.54, pauzes 40% langer, warme EQ (zie stories/ww2-facts/stem.json).
- **Muziek:** zelf uitgerekend in Python, in **432 Hz** (A4 = 432 Hz), met elke **7 seconden** een ander akkoord.
  Hij wordt gemaakt uit een drone, strijkers, een synthetisch koor, zachte pianotonen en sfeerlagen.
  Er zit geen AI-muziek, geen samples en geen bestaande muziek in.
- **Mix:** de muziek staat automatisch onder de stem en zakt iets weg als er gesproken wordt (ducking).
  De eindmix komt op -14 LUFS en -1 dBTP. Je krijgt hem als WAV (48 kHz, 24-bit) en als MP3 (320 kbit/s).

## Starten

Dubbelklik op `start_audio_engine.bat`. Dan opent http://127.0.0.1:7865 met drie tabbladen:

- **Voice Studio:** script typen of een .txt importeren, een stem kiezen, de snelheid instellen, de stem maken,
  luisteren en downloaden. Hier kun je ook meerdere scripts tegelijk laten inspreken (batch) of een nieuwe stem ontwerpen.
- **Music Studio:** de stijl, lengte, toonsoort, akkoordwissel en de sterkte per laag kiezen, en de galm, het
  low-pass-filter, de stereobreedte en het volume instellen. Daarna muziek maken en downloaden, ook als losse lagen (stems).
- **Final Mix:** een stem en muziek kiezen of uploaden (of de muziek automatisch precies op lengte laten maken),
  de volumes en de ducking instellen en de eindmix maken.

Alles komt in `output/` terecht. Bij elke uitvoer hoort een `config.json`, waarmee je precies hetzelfde opnieuw kunt maken.

## Zonder interface

```
C:\Users\rane\omnivoice-venv\Scripts\python.exe main.py voice script.txt
C:\Users\rane\omnivoice-venv\Scripts\python.exe main.py music --minutes 120 --preset referentie
C:\Users\rane\omnivoice-venv\Scripts\python.exe main.py mix output\voice\<map>\voice.wav
C:\Users\rane\omnivoice-venv\Scripts\python.exe main.py music --config output\music\<map>\config.json
```

## Stijlen (presets)

- **referentie** (standaard): nagemaakt op het voorbeeld van de eigenaar (6 nov 2026). Dat is één zachte, aangehouden
  klank tussen ±250 en 800 Hz, zonder bas en zonder hoog, die meteen vanaf het begin klinkt. De muziek staat 11 LUFS
  onder de stem. Daardoor zit er net als in het voorbeeld ±19 dB tussen gesproken woorden en de muziek.
- **cinematic:** alle lagen, met een opbouw: eerst de drone, dan de strijkers, het koor en de piano, daarna diepere akkoorden.

## Wat OmniVoice wel en niet kan

Een stem ontwerpen gaat alleen met deze kenmerken: man of vrouw, leeftijd, toonhoogte, fluisteren en accent.
Woorden als "warm", "hees" of "borstklank" begrijpt OmniVoice niet. Daarom wordt een stem eenmalig ontworpen
(kenmerken + seed) en daarna bij elke zin gekloond vanaf dezelfde referentie-opname (`voices/<naam>/ref.wav`).
Zo klinkt hij overal hetzelfde. Nadruk en pauzes regel je in de tekst zelf: met komma's, een lege regel, `[pause]`
of `[long-pause]`.

## Installatie (staat al op de pc)

- Python-omgeving: `C:\Users\rane\omnivoice-venv` met torch 2.8 (CUDA 12.8), omnivoice 0.2.1 en gradio
  (zie `requirements.txt`).
- FFmpeg: de full build van gyan.dev, en die moet in het PATH staan.
- Testen: `C:\Users\rane\omnivoice-venv\Scripts\python.exe tests\run_tests.py`. Voeg `long` toe om ook 2 uur
  muziek te testen. De uitslag komt in `output/tests/test-report.json`.
