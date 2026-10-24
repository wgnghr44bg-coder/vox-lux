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
- Elke video (Short én lange video): controleer vóór het renderen en daarna op de echte MP4 met
  `tools/threejs/check_frames.mjs` (contactbladen + console-fouten). Geen glinsterpuntjes, flikkering, strepen of andere rare
  dingen in beeld; alles moet vloeiend lopen. Zie "Quality check" in `tools/threejs/whatif-prompt.md`.
- Video's mogen nooit te donker zijn (ook nacht-, diepzee- of "donker"-scènes): het onderwerp is duidelijk belicht en
  op een telefoon goed te zien. `check_frames.mjs` meldt elk te donker beeld (gemiddelde helderheid < 38/255); maak die
  shots lichter, behalve het bedoelde vervagen naar zwart aan het eind (`--fade-from`).
