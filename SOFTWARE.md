# Software-overzicht (vox-lux + ifscape3d-videos)

Eén plek om te zien welke software er is en waar alles staat.
Zegt de eigenaar **"software"** → begin hier. Zegt hij **"comfy"** → alles via ComfyUI op zijn pc (zie `tools/comfy/README.md`).

| Wat | Software | Waar | Kost geld? |
|---|---|---|---|
| Afbeeldingen | **ComfyUI** – Z-Image Turbo (pc eigenaar) | `tools/comfy/comfy_batch.py` + `tools/comfy/README.md` | Nee |
| Bewegende clips | **ComfyUI** – Wan 2.2 5B (pc eigenaar) | `tools/comfy/comfy_batch.py`, controle: `tools/comfy/check_clips.py` | Nee |
| **Stem (standaard)** | **pc** – Chatterbox als bm_george, rustig | `tools/comfy/make_voice_local.py`, proef: `tools/comfy/stem/standaardstem-proef.mp3` | Nee |
| Stem (alleen op verzoek) | xAI TTS (Atlas / Lux) | `tools/xai_voiceover.py`, `alteraqon/tools/make_voice.py` (branch `alteraqon`) | **Ja – eerst vragen** |
| Afbeeldingen / clips (oud) | xAI `grok-imagine` | `tools/xai_images.py` | **Ja – staat uit, alleen na uitdrukkelijk ja** |
| Montage, effecten, foto, geluid | **Craft-apps** (FilmCraft, EffectCraft, PhotoCraft, SoundCraft, …) | `tools/craft/README.md`, voorbeelden in `tools/craft/examples/` | Nee |
| Losse bewerking | ffmpeg, OpenCV, Pillow, numpy | overal in `tools/` | Nee |
| YouTube | upload / playlist / bereik | `tools/youtube_*.py` | Nee |
| Reverse engineering | REA | `.mcp.json`, `.claude/skills/reverse-engineer-anything` | Nee |
| ElevenLabs | **niet meer gebruiken** | – | – |

## Hoe het samenwerkt
1. **Cloudsessie** (Claude) schrijft het script, `prompts.txt` (beelden) en `comfy-clips.txt` (clips), commit + pusht.
2. **Pc van de eigenaar** draait ComfyUI en `tools/comfy/comfy_batch.py` → beelden/clips, en pusht die.
3. **Cloudsessie** controleert de clips (`check_clips.py`), maakt de stem en monteert met de Craft-apps + ffmpeg.

## Installatie
- Craft-apps + Python-libs: automatisch bij elke cloudsessie (`.claude/hooks/session-start.sh` → `tools/craft/install-craft.sh`).
- ComfyUI draait **niet** in de cloud, alleen op de pc (RTX 2080 Super, 8 GB). De cloudsessie kan er niet direct bij.

## Kanalen
- **IfScape3D** – repo `ifscape3d-videos` (3D-stijl, Atlas-stem).
- **Alteraqon** – "What if"-video's, branch `alteraqon` in deze repo (`alteraqon/README.md`).
- **Sleep Archives** – `stories/` in deze repo.
