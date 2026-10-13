# Notes for Claude sessions

- Free video tools (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, … plus OpenCV/ffmpeg) are installed at session
  start. See `tools/craft/README.md` for commands, costs and reusable example scripts.
- Talk Dutch with the user, simply. Always ask before anything that costs money (xAI images, voice, video).
- ElevenLabs is no longer used. Voice-overs: `tools/xai_voiceover.py` (xAI only).
- REA (reverse engineering, https://github.com/morluto/rea): MCP server in `.mcp.json`, skill in
  `.claude/skills/reverse-engineer-anything`. Update with `npx rea-agents@latest` and bump the version in `.mcp.json`.
