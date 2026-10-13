# Alles van Claude naar OpenAI Codex

Hier staat alles wat Claude Code nu doet, zodat Codex het kan overnemen.
Codex leest `AGENTS.md` vanzelf; dit bestand is de uitleg + startprompt voor de eigenaar.

## 1. Eenmalig instellen in Codex (chatgpt.com/codex)
1. **Connect GitHub** → geef toegang tot `wgnghr44bg-coder` (alle repo's:
   `vox-lux`, `ifscape3d-videos`, `Script-`, `weekbudget`, `snorlax`).
2. Maak een **Environment** voor `vox-lux` (en een voor `ifscape3d-videos`):
   - **Setup script** (vox-lux):
     ```bash
     bash tools/craft/install-craft.sh          # FilmCraft, EffectCraft, PhotoCraft, SoundCraft, ...
     pip install -q opencv-python-headless numpy pillow
     command -v ffmpeg || (apt-get update && apt-get install -y ffmpeg)
     npm install
     ```
     (ifscape3d-videos: `bash tools/install-craft.sh`)
   - **Internet access**: aan.
   - **Secrets** (zelfde waarden als nu bij Claude; nooit in de chat of in GitHub zetten):
     | Naam | Waarvoor |
     |---|---|
     | `YT_CLIENT_ID`, `YT_CLIENT_SECRET` | YouTube-scripts |
     | `YT_REFRESH_TOKEN` | Sleep Archives |
     | `YT_WHATIF_REFRESH_TOKEN` | IfScape3D |
     | `YT_REFRESH_TOKEN_ALTERAQON` | Alteraqon |
     | `XAI_API_KEY` | xAI-stem (kost geld, alleen op verzoek) |
3. **Codex CLI op je pc** (handig, want ComfyUI en de stem draaien daar): `npm i -g @openai/codex`,
   dan in de map `vox-lux` het commando `codex`. REA toevoegen in `~/.codex/config.toml`:
   ```toml
   [mcp_servers.rea]
   command = "npx"
   args = ["-y", "rea-agents@6.4.0", "mcp"]
   ```
4. **Vaste routines**: Claude had 4 automatische taken (staan nu allemaal UIT). De volledige prompts staan in
   `docs/codex/routines/`. In Codex plak je zo'n prompt als nieuwe taak wanneer hij aan de beurt is
   (of zet hem in een automatische/geplande taak als je Codex-abonnement dat heeft):
   - `1-sleep-archives-video.md` – zo + do 08:54
   - `2-ifscape3d-video.md` – ma, wo, vr, za 13:47
   - `3-wekelijkse-youtube-check.md` – maandag 17:52
   - `4-maandelijkse-youtube-audit.md` – de 8e van de maand 17:52

## 2. Startprompt (kopieer en plak in Codex)

```text
Je neemt het werk over van Claude Code voor mijn GitHub-account wgnghr44bg-coder.
Praat simpel Nederlands met mij.

MIJN REPO'S EN KANALEN
- vox-lux: hoofdrepo met alle video-tools (tools/) en de VOX Lux web-app.
  - Sleep Archives (YouTube, history for sleep): map stories/ op main.
  - Alteraqon ("What if"-documentaires, verticaal): branch alteraqon, map alteraqon/.
  - IfScape3D render-engine + planning: branch claude/whatif-machine
    (USAGE.md, whatif-demo/AUTOMATISCH.md, whatif-demo/onderwerpen.md, whatif-demo/regels/).
  - YouTube-wijzigingslog: branch claude/youtube-log (stories/WIJZIGINGEN-LOG.md).
- ifscape3d-videos: bronbestanden per IfScape3D-video (<datum>-<slug>/).
- Script-, weekbudget, snorlax: kleinere projecten.

MIJN SOFTWARE (overzicht: SOFTWARE.md)
- ComfyUI (op mijn pc, gratis): beelden met Z-Image Turbo, clips met Wan 2.2.
  Script tools/comfy/comfy_batch.py, uitleg tools/comfy/README.md.
  Clips controleren: tools/comfy/check_clips.py (ifscape3d-videos: tools/check_clips.py)
  → clips/CHECKED.txt (naam OK / USE <s> / STILL).
- Craft-apps (gratis): FilmCraft, EffectCraft, PhotoCraft, SoundCraft, LightCraft, VectorCraft,
  DesignCraft, PdfCraft, WordCraft, GridCraft, DeckCraft, CADCraft.
  Installeren: bash tools/craft/install-craft.sh. Uitleg en voorbeelden: tools/craft/README.md, tools/craft/examples/.
- ffmpeg, OpenCV, Pillow, numpy voor losse bewerkingen.
- Video-scripts: make_video.py, make_short.py, make_thumbnail.py, effects.py, motion.py,
  ambient_432.py, ambient_sfx.py, qc_video.py, check_video.py (in tools/).
- YouTube: tools/youtube_upload.py, youtube_playlist.py, youtube_reach.py, youtube_tidy.py, dashboard_data.py.
  Sleutels staan als secrets in de omgeving; nooit tonen, nooit om vragen.
- Reverse engineering: REA (npx -y rea-agents@6.4.0 mcp), uitleg .claude/skills/reverse-engineer-anything/SKILL.md.
- xAI-beelden (tools/xai_images.py): KOST GELD, staat uit, alleen na mijn uitdrukkelijke ja.
- ElevenLabs: NIET meer gebruiken.

STEM (gratis, op mijn pc – de "comfy-stem")
- Standaard: Chatterbox die Kokoro bm_george nadoet, rustig (exaggeration 0.4, cfg 0.5).
- Script: tools/comfy/make_voice_local.py. Voorbeeldstem: tools/comfy/stem/voorbeeld-george.mp3.
  Proef: tools/comfy/stem/standaardstem-proef.mp3. Installatie: zie tools/comfy/voice_test_local.py.
- Werkwijze: jij schrijft <map>/script-cues.txt ({img:ID} op eigen regel, [pause], [long pause]),
  controleert met: python tools/comfy/make_voice_local.py <map> --dry-run
  en pusht. Ik draai op mijn pc: python tools/comfy/make_voice_local.py <map>
  → voice.mp3 + voice-times.tsv (stem start op 0,8 s). Ik push, jij pullt en monteert.
- Alteraqon gebruikt kortere pauzes: --pause-ms 350 --long-pause-ms 800 --sentence-pause-ms 250,
  getallen voluit schrijven.
- xAI-stem (tools/xai_voiceover.py): KOST GELD, alleen als ik erom vraag.

HOE HET SAMENWERKT
1. Jij schrijft script, prompts.txt (beelden) en comfy-clips.txt (clips) en pusht.
2. Ik draai ComfyUI (comfy_batch.py) en de stem (make_voice_local.py) op mijn pc en push het resultaat.
3. Jij pullt, controleert clips, maakt QC en monteert met Craft-apps + ffmpeg.
ComfyUI en de stem zijn vanuit de cloud NIET bereikbaar; dat loopt altijd via mij.

VASTE TAKEN (prompts in docs/codex/routines/, nu gepauzeerd)
- Sleep Archives video (zo + do), IfScape3D video's + Shorts + TikTok-pagina (ma/wo/vr/za),
  wekelijkse YouTube-check (ma), maandelijkse YouTube-audit (8e).
  Doe deze alleen als ik zeg welke ik wil.

STAP 1 – EERST LEZEN (nog niets veranderen)
1. Lees AGENTS.md, CLAUDE.md, SOFTWARE.md, README.md, CODEX.md, tools/comfy/README.md,
   tools/craft/README.md en .claude/skills/*/SKILL.md.
2. Bekijk git log --oneline -20, alle branches (git branch -r --sort=-committerdate) en open pull requests.
3. Lees USAGE.md op branch claude/whatif-machine (planning) en alteraqon/README.md op branch alteraqon.
4. Kijk welke video's nog niet af zijn (geen voice.mp3, upload.json of clips/CHECKED.txt).

STAP 2 – SAMENVATTEN
Maximaal 10 korte regels: wat je vond, waar we gebleven zijn, wat de logische volgende stap is.

STAP 3 – VRAGEN AAN MIJ (wacht op mijn antwoord)
1. Aan welk kanaal werken we: IfScape3D, Alteraqon of Sleep Archives?
2. Bestaande video afmaken (welke?) of een nieuwe (welk onderwerp)?
3. Lange video of Short?
4. Draait ComfyUI nu op mijn pc?
5. Stem: standaard (Chatterbox, gratis) of xAI (kost geld)?
6. Uploaden naar YouTube of alleen klaarzetten?
7. Moet een van de vaste taken weer aan?

VASTE REGELS
- Vraag ALTIJD eerst toestemming voor alles wat geld kost.
- "comfy" = alles via ComfyUI op mijn pc, nooit via xAI. "software" = lees SOFTWARE.md.
- Werk op een eigen branch, commit en push. PR alleen als ik erom vraag.
  (Uitzondering: de IfScape3D-taak pusht direct naar claude/whatif-machine.)
- Geen mp4, wav of andere grote bestanden committen.
- Nooit een video opnieuw uploaden of verwijderen op YouTube.
- Twijfel je? Vraag het me, niet gokken.
- Pas je afspraken aan, pas dan AGENTS.md en CLAUDE.md allebei aan,
  zodat ik kan blijven wisselen tussen Codex en Claude.
```

## 3. Waar Claude laatst mee bezig was (13 okt 2026)
| Wat | Waar |
|---|---|
| Alteraqon: *What if you stopped drinking water?* (6 clips, rest foto + Ken Burns) | vox-lux, branch `alteraqon` |
| Alteraqon: superpower, countdown, clone, dinosaur asteroid, iron vanished, gravity stronger | branch `alteraqon` |
| IfScape3D: *What if Earth stopped spinning?* in Comfy-stijl (Z-Image testbeeld) | ifscape3d-videos, branch `claude/earth-stops-spinning` |
| IfScape3D: oceans dried up, sinkhole, tsunami, groottevergelijking | vox-lux, branch `claude/whatif-machine` |
| Megalodon: realistischer bewerkte versie | vox-lux, branch `claude/eigen-poppetjes` |
| Comfy + standaardstem + software-overzicht | gemerged in `main` (beide repo's) |
| Craft-apps installer, REA | gemerged / branch `claude/artcraft-video-creation-jgxhnj`, `claude/rea-agents-setup-1ho5zc` |
| Camera-bewegingen, nieuwe plek 'plaza' voor de 3D-engine | branches `claude/camera-beelden-implementatie-6jmi11`, `claude/jolly-hopper-mejg3p` |
| Planning YouTube/TikTok gepauzeerd | branch `claude/youtube-tiktok-planning-pause-hkakak` |
| Sleep Archives: Dyatlov (live wo 14 okt 21:00), Vikings, Tunguska, Titanic | `stories/` + branches `claude/festive-ramanujan-*` |

Codex kan dit zelf nakijken met `git branch -r --sort=-committerdate`.
