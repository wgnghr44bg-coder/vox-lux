# Notes for Claude sessions

- **"software"** → read `SOFTWARE.md` (overview of all tools and where they live).
  **"comfy"** → images, clips and local voice go via ComfyUI on the owner's pc: follow `tools/comfy/README.md`, never xAI.
- Free video tools (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, … plus OpenCV/ffmpeg) are installed at session
  start. See `tools/craft/README.md` for commands, costs and reusable example scripts.
- Talk Dutch with the user, simply. Always ask before anything that costs money (xAI images, voice, video).
- ElevenLabs is no longer used. Paid voice-overs: `tools/xai_voiceover.py` (xAI); free local voice (works, voice not yet chosen): `tools/comfy/voice_test_local.py`.
- REA (reverse engineering, https://github.com/morluto/rea): MCP server in `.mcp.json`, skill in
  `.claude/skills/reverse-engineer-anything`. Update with `npx rea-agents@latest` and bump the version in `.mcp.json`.
