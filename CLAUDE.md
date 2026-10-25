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
- Nooit knipperen of flikkeren in beeld (Shorts én lange video's). Twee vlakken op precies dezelfde plek (vloer op een
  muur-/blokrand, kleed op de vloer) en heel laag strijklicht met schaduwen knipperen: laat vlakken nooit samenvallen en
  zet de zon minstens ±15° hoog. Controleer vóór het renderen elk beeld (30 per seconde) en daarna de echte MP4 met
  `python tools/threejs/check_flicker.py` (zie `tools/threejs/README.md`); er mag geen "KNIPPEREN" uitkomen.
- YouTube: elke What If-video (Short én lang) gaat naar het kanaal **IfScape3D**, nooit naar Sleep Archives. Upload met
  `tools/youtube_upload.py --channel whatif` en volg `tools/threejs/YOUTUBE-IFSCAPE3D.md` (titel, beschrijving, tags,
  instellingen). Sleep Archives (`--channel sleep`) is alleen voor History for Sleep. Alleen uploaden als de eigenaar erom vraagt.
