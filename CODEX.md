# Overstappen naar OpenAI Codex

## 1. Eenmalig instellen (chatgpt.com/codex)
1. Ga naar **chatgpt.com/codex** → **Connect GitHub** → geef toegang tot `wgnghr44bg-coder` (alle repo's:
   `vox-lux`, `ifscape3d-videos`, `Script-`, `weekbudget`, `snorlax`).
2. Maak per repo een **Environment** aan:
   - **Setup script** (vox-lux):
     ```bash
     bash tools/craft/install-craft.sh
     pip install -q opencv-python-headless numpy pillow
     npm install
     ```
     (ifscape3d-videos: `bash tools/install-craft.sh`)
   - **Internet access**: aan (nodig voor Craft-apps, npm, pip, xAI).
   - **Secrets**: `XAI_API_KEY` (alleen als je de xAI-stem wilt gebruiken; kost geld).
     YouTube-scripts: dezelfde sleutels/tokens als nu bij Claude.
3. Codex CLI op je pc (optioneel): `npm i -g @openai/codex`, dan in de repo-map `codex`.
   REA toevoegen in `~/.codex/config.toml`:
   ```toml
   [mcp_servers.rea]
   command = "npx"
   args = ["-y", "rea-agents@6.4.0", "mcp"]
   ```

Codex leest automatisch `AGENTS.md` in elke repo – daar staan alle afspraken (Nederlands, eerst vragen bij kosten, comfy, software).

## 2. Startprompt (kopieer en plak in Codex)

```text
Je neemt het werk over van Claude Code voor mijn GitHub-account wgnghr44bg-coder.
Praat simpel Nederlands met mij.

Repo's:
- vox-lux: hoofdrepo met alle video-tools (tools/), de VOX Lux web-app, Sleep Archives (stories/),
  Alteraqon (branch alteraqon) en de IfScape3D render-engine (branch claude/whatif-machine).
- ifscape3d-videos: bronbestanden per IfScape3D-video (<datum>-<slug>/).
- Script-, weekbudget, snorlax: kleinere projecten.

Begin zo:
1. Lees AGENTS.md, SOFTWARE.md en README.md van de repo, en de bestanden in .claude/skills/*/SKILL.md.
2. Bekijk de laatste 20 commits (git log --oneline -20) en de open branches, zodat je weet waar we gebleven zijn.
3. Vat in 5–10 regels samen wat je ziet en wat de logische volgende stap is. Doe nog niets.

Vaste regels:
- Vraag altijd eerst toestemming voor alles wat geld kost (xAI-beelden, xAI-stem, video-API's).
- "comfy" = beelden/clips/stem via ComfyUI op mijn pc, nooit xAI. Jij schrijft de prompt-bestanden en pusht;
  ik draai comfy_batch.py op mijn pc en push het resultaat.
- "software" = lees SOFTWARE.md.
- Standaardstem: Chatterbox als bm_george, rustig (tools/comfy/make_voice_local.py, op mijn pc).
- ElevenLabs niet gebruiken.
- Werk op een eigen branch, commit + push, PR alleen als ik erom vraag. Geen mp4/wav committen.
- Houd AGENTS.md en CLAUDE.md gelijk als je afspraken aanpast, zodat ik kan wisselen tussen Codex en Claude.
```
