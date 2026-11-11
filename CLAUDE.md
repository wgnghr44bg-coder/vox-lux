# Notes for Claude sessions

## Eerst lezen: de vaste afspraken voor Sleep Archives (eigenaar 7-8 nov 2026)
- **Stand van zaken en wat er nog moet**: `stories/OVERDRACHT-AUDIO.md`.
- **Stem en muziek staan vast in `audio_engine/B1.json`** (sinds 11 nov 2026, eigenaar: "zo is het perfect, ik wil deze
  als vaste stem houden"): stem **`eigen-stem`** = de eigen stem van de eigenaar ("calm and gentle voice"), **speed 0.9**
  (rustiger, ± 120 woorden/min; sinds 11 nov middag), **klank zonder bass**, **zonder verteller F**, gewone pauzes (pauze 1.4, **nergens langer dan 2 s stil**: max_pauze, 11 nov avond), met muziek
  **W3** "diep en donker-warm" (elke 6 s een ander akkoord, **19 LUFS onder de stem**, seed 1939). Het stembestand staat
  alleen op de pc: `C:\Users\rane\vox-lux-stemmen\eigen-stem\ref.wav` (voice.json "ref_pc"; de repo is openbaar, dus
  nooit op GitHub zetten). De oude vaste stem (narrator-e met verteller F, 11 LUFS) staat in `audio_engine/B1-oud-narrator-e.json`. Alle gereedschap leest dit via `tools/b1.py`; het stemmodel staat vast op één versie. Controle vóór elke video: `tools/b1_check.py` moet "B1 GOED" geven. **Niets aan de stem of muziek veranderen
  zonder de eigenaar** ("dat er geen fouten kunnen zijn in stem en geluid"); geen rubberband/tempo/toonhoogte op de stem
  ("anders is het meteen een robot"). Slaap 3, George, regen en de oude 432-muziek worden niet meer gebruikt. Bevestigd 10 nov 2026 na proeven met andere stemmen, langere pauzes en zachtere muziek: "Stem en muziek gewoon laten zoals het was".
- **Opbouw van elke video**: `stories/OPBOUW.md` (begin van ± 2 min zonder "Tonight", 8-13 onderwerpen met feitjes,
  slot dat uitdooft; soort opening en titel afwisselen). Script bouwen met `tools/bouw_feiten.py`.
- **Videostraat**: `stories/PROMPT-ROUTINE-PC.md` (engine_stem → prep_engine → montage_engine → upload).
  Afgekapte zinnen: `tools/engine_stem.py <map> --hergebruik --opnieuw <nrs> --seed-extra <n>`.
- **Titels**: vraag-titel zonder uren, `| History for Sleep`. **Thumbnails: nooit uren erop.**
- **Oude video vervangen**: nieuwe privé uploaden met dezelfde publicatietijd, kanaal controleren,
  `tools/wacht_verwerkt.py`, en pas daarna de oude verwijderen.
- **Proeven sturen**: lukt SendUserFile niet, zet het geluid dan op een privé Artifact-pagina (mp3 in de pagina);
  de eigenaar luistert op zijn telefoon. Bij stem/muziek liefst alleen geluid, zonder beeld.
- De eigenaar geeft altijd toestemming voor PowerShell-opdrachten op de pc; vraag wel altijd eerst als iets geld kost.
- **Zonder Claude (in test)**: lokale modellen via Ollama, `tools/scriptgen/generator.py`, `tools/beeldcheck.py` (dubbele beeldcontrole), `tools/routine_lokaal.py`. Zie `stories/OVERDRACHT-AUDIO.md`, "Zonder Claude".
- Lange ketens (stem + montage ± 12 uur) als los proces starten (`Start-Process`), niet als achtergrondtaak (die stopt na 2 uur).

- **"script vooruit"**, "schrijf het volgende script" of "scriptgenerator" → `stories/PROMPT-SCRIPT-PC.md`: één recept voor scriptgenerator, tweede account en routine (eerst oude scripts ombouwen, dan nieuwe schrijven).
- **"software"** → read `SOFTWARE.md` (overview of all tools and where they live).
  **"comfy"** → images, clips and local voice go via ComfyUI on the owner's pc: follow `tools/comfy/README.md`, never xAI.
- Free video tools (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, … plus OpenCV/ffmpeg) are installed at session
  start. See `tools/craft/README.md` for commands, costs and reusable example scripts.
- Talk Dutch with the user, simply. Always ask before anything that costs money (xAI images, voice, video).
- ElevenLabs is no longer used. **Standard voice and music: `audio_engine/B1.json`** (since 11 Nov 2026: the owner's own voice `eigen-stem`, speed 0.9, no bass + W3 at 19 LUFS under; see the
  section above; the old standard Slaap 3 + rain is replaced). Last step stays `tools/eind_volume.py in.mp4 uit.mp4`: -14 LUFS.
  George/Chatterbox (`make_voice_local.py`) only on request. xAI voice (`tools/xai_voiceover.py`) only on request; it costs money.
- REA (reverse engineering, https://github.com/morluto/rea): MCP server in `.mcp.json`, skill in
  `.claude/skills/reverse-engineer-anything`. Update with `npx rea-agents@latest` and bump the version in `.mcp.json`.
- Video's (shorts én lange video's) altijd sturen als afspeelbare video (SendUserFile met `display: "render"`), zodat de eigenaar
  hem in de speler via de deel-knop rechtsboven kan opslaan. Is het bestand groter dan ±50 MB, stuur dan ook een kleinere versie
  (bv. 720p, ±1,1 Mbit/s) mee.
- YouTube-kanalen hebben elk een eigen refresh token (zelfde `YT_CLIENT_ID`/`YT_CLIENT_SECRET`):
  `YT_REFRESH_TOKEN` = Sleep Archives, `YT_WHATIF_REFRESH_TOKEN` = IfScape3D (What If-video's),
  `YT_REFRESH_TOKEN_ALTERAQON` = Alteraqon. Upload met het juiste token
  (bv. `YT_REFRESH_TOKEN="$YT_WHATIF_REFRESH_TOKEN" python3 tools/youtube_upload.py ...`) en controleer
  vóór het openbaar zetten via de API (`snippet.channelTitle`) dat de video op het goede kanaal staat.

## Stand 9 nov 2026 (middag): test zonder Claude loopt, rest op pauze
- `tools/testnu.ps1` draait los op de pc (log `C:\Users\rane\nachttest.log`, ook op de website): 1) Gettysburg ombouwen
  met de lokale generator, 2) nieuw script Salem 1692 (`stories/_test-nieuw`), 3) `routine_lokaal.py --test-tot-beelden` op Gettysburg.
- Op pauze tot de eigenaar de test heeft goedgekeurd: taken "Sleep Archives routine" en "scriptgenerator" staan UIT (Disabled);
  Tombstone (`tools/tombstone_herstel.ps1`) en Egypte (montage + upload) staan stil. Oude privé versies uitgesteld naar ma 16 en ma 23 nov 21:00.
- Na de test: laat de eigenaar de scripts en beelden zien naast een Claude-script (Dallas). Pas na OK: taken omzetten naar
  `tools/routine_lokaal.py` en `tools/scriptgen/generator.py` en weer aanzetten; daarna Tombstone en Egypte afmaken vóór 16/23 nov.
## Stand 9 nov 2026 (avond): test zonder Claude GESTOPT
Eigenaar: "ik laat het script wel hier maken en de rest via pc". Dus: **scripts maakt een Claude-account** (PROMPT-SCRIPT-PC.md,
zoals het tweede account 9 nov deed: Scott, Pearl Harbor, Rome, Zwarte Dood), **de rest doet de pc** (taak "Sleep Archives routine"
weer AAN; taak "scriptgenerator" blijft UIT). De lokale generator (tools/scriptgen) wordt niet gebruikt.
Tombstone en Egypte lopen via `tools/hervat_tombstone_egypte.ps1` (log C:\Users\rane\hervat.log): vervangen de oude privé versies op 16 en 23 nov.
Gettysburg (wo 18 nov) staat weer op "script-klaar (oude opbouw)": een Claude-account of de routine bouwt het om.
## Stand 11 nov 2026: verteller F en nieuwe toon (eigenaar)
- **Stem**: B1 blijft dezelfde stem, maar vertelt nu als slaapverteller ("F zoals nu kan dat"): instellingen in
  `audio_engine/B1.json` ("speed" 0.50 + blok "verteller"). `tools/engine_stem.py` doet dit vanzelf; `tools/b1_check.py`
  is opnieuw vastgelegd (B1 GOED). Proeven: `tools/b1_proef.py` (standaard F; `--zonder-verteller` voor de oude).
- **Tekst**: nieuwe toon zoals de grote slaapkanalen (jij-vorm, vragen, verteller als persoon, spreektaal), zie
  stories/OPBOUW.md en stories/PROMPT-SCRIPT-PC.md; voorbeeld `stories/_toon-proef/`. `tools/script_leesbaar.py` meet TOON.
- **Op pauze** (eigenaar: "we gaan het toch anders doen"): taak "Sleep Archives routine" UIT, Tombstone-opnieuw gestopt.
  Babylon (za 14 nov) mocht afmaken. Tombstone-privéversie 03VXrW2gb7g heeft geen publicatietijd.
- Gemeten (11 nov): grote kanalen 131-169 woorden/min, ons oude B1 129-140; met F ± 119.
## Stand 11 nov 2026 (later): eigen stem is de vaste stem (eigenaar)
- **Stem**: de eigen stem van de eigenaar (opname "Beste voice ever", eigenaar: "Van mezelf"), gekloond met OmniVoice:
  `audio_engine/voices/eigen-stem/voice.json` ("calm and gentle voice"). Het geluid zelf (ref.wav + de hele opname) staat
  alleen op de pc in `C:\Users\rane\vox-lux-stemmen\eigen-stem\` (de repo is openbaar). Speed 1.0, geen verteller F
  (eigenaar: "laat verteller F weg, pak de normale stem"); het F-blok staat als "verteller_uit" in B1.json en wordt niet gebruikt.
- **Muziek**: W3, **19 LUFS onder de stem** (eigenaar: "zo is het perfect"; proeven 11 → 15 → 19). Gemeten 11 nov: grote
  slaapkanalen met muziek zitten ± 15-25 onder de stem, drie van de zeven gebruiken geen muziek.
- `tools/b1_check.py` is opnieuw vastgelegd met de eigen stem (B1 GOED). `tools/b1_proef.py` maakt de vaste proef van 1 min;
  `tools/proef_andere_stem.py` voor proeven met een andere stem (`--zonder-verteller`, `--muziek-onder`).
- Proeftekst nieuwe toon: `stories/_toon-proef/gettysburg-begin-en-hoofdstuk1.txt` (de eigenaar vond deze proef "perfect").

## Stand 11 nov 2026 (middag): alle geplande video's opnieuw, nu GESTOPT op verzoek van de eigenaar
- Eigenaar: "alle video's opnieuw volgens de nieuwe regels" (eigen stem uit B1.json + nieuwe toon). Daarna: "Stop maar even met alles".
- **Scripts in de nieuwe toon** (geschreven door Claude in de cloud, met `tools/toon_bijwerken.py` + `stories/<map>/toon/*.json`;
  zelfde feiten en IMG-regels): babylon-600-vc, tombstone-1881, gettysburg-1863, dallas-1963, egypte-toetanchamon zijn KLAAR
  (MAKKELIJK, TOON GOED, AFWISSELING GOED). Nog te doen: scott-antarctica-1912, pearl-harbor-1941, rome-44-vc, zwarte-dood-1348
  (bij Zwarte Dood ook 7 feitjes vervangen, zie scriptcheck.json).
- **Video's maken** zonder Claude-agent: in `C:\Users\rane\Documents\vox-lux-routine`:
  `python -u tools/routine_lokaal.py --opnieuw babylon-600-vc,tombstone-1881,gettysburg-1863,dallas-1963,egypte-toetanchamon,scott-antarctica-1912,pearl-harbor-1941,rome-44-vc,zwarte-dood-1348`
  (log `C:\Users\rane\opnieuw-keten2.log`). Per video: wacht op TOON GOED, beelden (bestaande worden hergebruikt; hooguit 3
  hardnekkige beelden vervangen door het beeld ervoor), eigen stem, montage met strenge haperingcontrole, dan de privéversie op
  YouTube vervangen (`--oud` uit planning.txt). Een video wordt alleen overgeslagen als "<map>: opnieuw gemaakt" in ROUTINE-LOG.md staat.
  **STAAT STIL** (eigenaar: stoppen). Er is nog niets vervangen. Gettysburg heeft al een nieuwe voice.mp3 met de eigen stem (wordt hergebruikt).
- Een Claude-agent op de pc starten (`claude -p ... --dangerously-skip-permissions`) wordt door de beveiliging geblokkeerd; daarom deze route.
- **Open vraag aan de eigenaar**: langere pauzes ("mag wel meer pauzes, de stem zelf niet veranderen")? Proef B (pauze 1.9 in plaats van
  1.4) is gemaakt, C (2.4) niet. Pauzes kunnen ook achteraf bij de voorbereiding (add_pauses), zonder de stem opnieuw in te spreken.
- YouTube nu: Babylon 8Mm2NOlyL3U privé (za 14 nov), Egypte iMkB7sUR8UU privé (ma 23 nov), Tombstone 03VXrW2gb7g privé ZONDER publicatietijd.
- Let op bij git: nooit een hele story-map toevoegen (beelden, voice.mp3 > 100 MB); alleen losse tekstbestanden.
## Stand 11 nov 2026 (middag, later): rustiger en zonder bass (eigenaar)
- Na proeven (pauzes, komma-pauze, helderder, speed 1.0/0.9/0.8, zonder bass, lagere muziek) koos de eigenaar de proef
  "begin van Gettysburg, zonder bass, speed 0.9": "Ja dit is goed zo, zet dit vast, alle video's zo maken".
- In `audio_engine/B1.json`: **speed 0.9** (± 120 woorden/min, OmniVoice spreekt zelf langzamer) en **klank zonder bass**
  (`highpass=f=110,lowshelf=f=220:g=-4,highshelf=f=4500:g=-2,...`). Pauzes (1.4) en muziek (W3, 19 onder) bleven gelijk.
  `tools/b1_check.py` is opnieuw vastgelegd (B1 GOED). Alle video's worden zo gemaakt; een stem die met speed 1.0 of de
  warme klank is gemaakt (bv. Gettysburg voice.mp3 van vanochtend) moet opnieuw.
- Gemeten 11 nov: grote kanalen pauzeren ± 0,5 s tussen zinnen, wij ± 0,9 s (pauze 1.4); de eigenaar hield 1.4.
## Stand 11 nov 2026 (14:11): keten loopt volgens de nieuwe planning
- Eigenaar: "planning starten, controleren op flikkeren of stem niet goed, alles vloeiend zonder haperen". Planning
  16 nov - 16 dec (hype en jaardagen) staat in de planning.txt's; scripts doet het andere account (`stories/PROMPT-SCRIPTS-NOV-DEC.md`).
- Los proces op de pc (pid 19860), log `C:\Users\rane\opnieuw-keten3.log`, uitslagen in stories/ROUTINE-LOG.md:
  `routine_lokaal.py --opnieuw babylon-600-vc,gettysburg-1863,crisis-1933,dallas-1963,egypte-toetanchamon,thanksgiving-1621,pearl-harbor-1941,boeren-winter-1300,kerst-loopgraven-1914,rome-44-vc,zwarte-dood-1348,scott-antarctica-1912`
  Wacht per video op het script in de nieuwe toon (TOON GOED); een video gaat alleen online als beeldcontrole, B1 GOED,
  tekstcontrole (Whisper), qc (o.a. flikkering) en de strenge haperingcontrole allemaal goed zijn; anders blijft de oude versie staan.
