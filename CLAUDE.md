# Notes for Claude sessions

- **"software"** → read `SOFTWARE.md` (overview of all tools and where they live).
  **"comfy"** → images, clips and local voice go via ComfyUI on the owner's pc: follow `tools/comfy/README.md`, never xAI.
- Free video tools (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, … plus OpenCV/ffmpeg) are installed at session
  start. See `tools/craft/README.md` for commands, costs and reusable example scripts.
- Talk Dutch with the user, simply. Always ask before anything that costs money (xAI images, voice, video).
- ElevenLabs is no longer used. Standard voice (free, owner's pc): Chatterbox imitating Kokoro bm_george, calm – `tools/comfy/make_voice_local.py`.
  xAI voice (`tools/xai_voiceover.py`) only on request; it costs money.
- REA (reverse engineering, https://github.com/morluto/rea): MCP server in `.mcp.json`, skill in
  `.claude/skills/reverse-engineer-anything`. Update with `npx rea-agents@latest` and bump the version in `.mcp.json`.
- Video's (shorts én lange video's) altijd sturen als afspeelbare video (SendUserFile met `display: "render"`), zodat de eigenaar
  hem in de speler via de deel-knop rechtsboven kan opslaan. Is het bestand groter dan ±50 MB, stuur dan ook een kleinere versie
  (bv. 720p, ±1,1 Mbit/s) mee.
