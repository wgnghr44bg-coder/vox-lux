# Notes for Claude sessions

## Eerst lezen: de vaste afspraken voor Sleep Archives (eigenaar 7-8 nov 2026)
- **Stand van zaken en wat er nog moet**: `stories/OVERDRACHT-AUDIO.md`.
- **Stem en muziek staan vast in `audio_engine/B1.json`** ("B1-stem met achtergrondmuziek"): stem `narrator-e`
  (speed 0.54, pauzes ×1,4, warme klank) met muziek **W3** "diep en donker-warm" (elke 6 s een ander akkoord, 11 LUFS
  onder de stem, seed 1939). Alle gereedschap leest dit via `tools/b1.py`; het stemmodel staat vast op één versie. Controle vóór elke video: `tools/b1_check.py` moet "B1 GOED" geven. **Niets aan de stem of muziek veranderen
  zonder de eigenaar** ("dat er geen fouten kunnen zijn in stem en geluid"); geen rubberband/tempo/toonhoogte op de stem
  ("anders is het meteen een robot"). Slaap 3, George, regen en de oude 432-muziek worden niet meer gebruikt.
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
- Lange ketens (stem + montage ± 12 uur) als los proces starten (`Start-Process`), niet als achtergrondtaak (die stopt na 2 uur).

- **"script vooruit"** of "schrijf het volgende script" → `stories/PROMPT-SCRIPT-VOORUIT.md` (tweede account schrijft scripts vooruit; de pc-routine pakt ze op).
- **"software"** → read `SOFTWARE.md` (overview of all tools and where they live).
  **"comfy"** → images, clips and local voice go via ComfyUI on the owner's pc: follow `tools/comfy/README.md`, never xAI.
- Free video tools (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, … plus OpenCV/ffmpeg) are installed at session
  start. See `tools/craft/README.md` for commands, costs and reusable example scripts.
- Talk Dutch with the user, simply. Always ask before anything that costs money (xAI images, voice, video).
- ElevenLabs is no longer used. **Standard voice and music since 8 Nov 2026: B1 + W3 from `audio_engine/B1.json`** (see the
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
