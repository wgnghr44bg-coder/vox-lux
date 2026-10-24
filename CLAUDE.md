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
- Daglicht mag: een video hoeft niet alleen 's nachts of in het donker te spelen. Donker is goed waar het logisch is (in
  een walvis, de diepzee), maar je moet altijd kunnen zien waar de zin over gaat. `check_frames.mjs` meldt donkere beelden
  (< 38/255): bekijk ze en maak ze alleen lichter als het donker daar niet logisch is of het onderwerp niet te zien is.
