# AGENTS.md – instructies voor OpenAI Codex (en andere AI-agents)

Codex leest dit bestand automatisch. Het is dezelfde afspraak als `CLAUDE.md` (voor Claude).
Pas je iets aan de werkafspraken aan, houd `CLAUDE.md` en `AGENTS.md` gelijk.

## Werkafspraken met de eigenaar
- Praat **simpel Nederlands**.
- **Vraag altijd eerst toestemming** voor alles wat geld kost (xAI-beelden, xAI-stem, video-API's).
- ElevenLabs wordt **niet meer** gebruikt.
- Werk op een eigen branch, commit met duidelijke berichten, push, en maak alleen een PR als de eigenaar dat vraagt.
- Geen mp4's, wav's of grote bestanden committen (staan op YouTube / te groot voor GitHub).

## Trefwoorden
- **"software"** → lees `SOFTWARE.md` (alle tools en waar ze staan).
- **"comfy"** → beelden, clips en lokale stem via ComfyUI op de pc van de eigenaar, **nooit via xAI**.
  Volg `tools/comfy/README.md`. ComfyUI is vanuit de cloud niet bereikbaar: schrijf `prompts.txt` /
  `comfy-clips.txt`, push, en vraag de eigenaar `python tools/comfy/comfy_batch.py ...` op zijn pc te draaien.
  Na zijn push: clips controleren met `python3 tools/comfy/check_clips.py <map>/clips` → `clips/CHECKED.txt`.

## Stem (gratis, op de pc van de eigenaar)
- Standaard: Chatterbox als Kokoro bm_george, rustig (exaggeration 0.4, cfg 0.5) → `tools/comfy/make_voice_local.py <map>`.
  Leest `<map>/script-cues.txt` (`{img:ID}`, `[pause]`, `[long pause]`) → `voice.mp3` + `voice-times.tsv`.
  In de cloud alleen `--dry-run`; de echte stem draait de eigenaar op zijn pc. Voorbeeldstem: `tools/comfy/stem/voorbeeld-george.mp3`.

## Tools
- xAI-stem (`tools/xai_voiceover.py`) alleen op verzoek, kost geld. Sleutels staan als secrets in de omgeving (`XAI_API_KEY`, `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`, `YT_WHATIF_REFRESH_TOKEN`, `YT_REFRESH_TOKEN_ALTERAQON`); nooit tonen.
- Montage/effecten/foto/geluid: Craft-apps (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, …) + ffmpeg/OpenCV.
  Installeren: `bash tools/craft/install-craft.sh`. Uitleg + voorbeelden: `tools/craft/README.md`.
- YouTube: `tools/youtube_*.py`.
- Web-app (VOX Lux, Vite/React): `npm install`, `npm run dev`, `npm run build`. Zie `README.md`.
- Reverse engineering: REA (`npx -y rea-agents@6.4.0 mcp`), instructies in
  `.claude/skills/reverse-engineer-anything/SKILL.md`.

## Vaste taken
De 4 vaste routines (Sleep Archives video, IfScape3D video, wekelijkse YouTube-check, maandaudit) staan in
`docs/codex/routines/`. Alleen uitvoeren als de eigenaar dat vraagt. Meer uitleg: `CODEX.md`.

## "Skills" (staan in `.claude/skills/`, gewoon Markdown – ook bruikbaar voor Codex)
- `software/SKILL.md` – software-overzicht
- `comfy/SKILL.md` – ComfyUI-werkwijze
- `reverse-engineer-anything/SKILL.md` – REA

## Kanalen / repo's
- **Sleep Archives** – `stories/` in deze repo.
- **Alteraqon** – "What if"-video's, branch `alteraqon` (`alteraqon/README.md`).
- **IfScape3D** – repo `wgnghr44bg-coder/ifscape3d-videos` (bronbestanden per video; render-engine in deze repo, branch `claude/whatif-machine`).
- Overige repo's van de eigenaar: `Script-`, `weekbudget`, `snorlax`.
