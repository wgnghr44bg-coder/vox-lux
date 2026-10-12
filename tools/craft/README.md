# Craft video toolkit (free)

Every cloud session of this repo installs the free **ArtCraft Crafting Apps** automatically
(`.claude/hooks/session-start.sh` → `tools/craft/install-craft.sh`). They land in `/opt/craft`
and their commands are on `PATH`:

| App | Like | CLI |
|---|---|---|
| FilmCraft | Premiere Pro (edit, colour, audio, export) | `filmcraft-cli` |
| EffectCraft | After Effects (animation, keyframes, JSX scripting) | `effectcraft-cli` |
| PhotoCraft | Photoshop | `photocraft-cli` |
| VectorCraft | Illustrator | `vectorcraft-cli` |
| LightCraft | Lightroom | `lightcraft-cli` |
| DesignCraft | InDesign | `designcraft-cli` |
| PdfCraft | Acrobat | `pdfcraft-cli` |
| SoundCraft | Pro Tools (record, edit, mix audio) | `soundcraft-cli` |
| WordCraft | Word | `wordcraft-cli` |
| GridCraft | Excel (repo `sheetcraft`) | `gridcraft-cli` |
| DeckCraft | PowerPoint (repo `slidecraft`) | `deckcraft-cli` |

ArtCraft itself (the AI studio) has no Linux build and is not installed.
Python libs for the example scripts: `opencv-python-headless`, `numpy`, `pillow` (also installed).

## Costs
- Craft apps, ffmpeg, Python effects, synthesized sound: **free**.
- xAI images (`grok-imagine-image`, ~$0.02 each, also charged when moderation rejects one),
  xAI TTS voice (Atlas) and xAI video clips (~$0.19 each) cost money: **always ask first**.
- ElevenLabs is **not used** any more.

## Examples (`examples/`)
Working scripts from earlier videos. Paths inside are from the session they were made in;
adjust them before reuse.

| Script | What it does |
|---|---|
| `whatif_scenes.py` | What If short: 7 scenes from images, Ken Burns + per-scene motion (ECG line, flickering/going-out lights, light beams, falling sand, crowd ripple), counters, labels, auto-fit captions |
| `whatif_mix.py` | Mixes voice lines + synthesized drone, whooshes, impacts and ambience into one track |
| `warp_beat.py` | Hyperspace star tunnel + flying through images on the beat (procedural nebulae/planet, synth beat) |
| `photo_animate.py` | Animate a single photo: TV content, recoil, thumbs, LED pulse (gamer room) |
| `pov_camera.py` | POV head-camera motion on an existing video |
| `synth_sfx.py` | Synthesized SFX: gunshots, clicks, footsteps, groans, room tone |
| `cutout_cars.py` | Cut cars out of a still and rebuild the empty road (clean plate) |
| `effectcraft_cars.jsx` | EffectCraft JSX: cars driving away in perspective (render with `effectcraft-cli render`) |

## FilmCraft assembly (headless)
```sh
filmcraft-cli --save-as p.fcproj exec file.newProject name=Short
filmcraft-cli --project p.fcproj --save exec file.newSequence '{"name":"Short","width":1080,"height":1920,"fps":30}'
filmcraft-cli --project p.fcproj --save import scene1.mp4 scene2.mp4 mix.wav     # prints item ids
filmcraft-cli --project p.fcproj --save run place.jsonl   # {"id":"timeline.place","params":{"item":8,"track":"V1","seconds":0}}
filmcraft-cli --project p.fcproj export out.mp4 --format h264
```
Limits: people in a still cannot really walk with these tools; that needs AI video clips (paid) or 3D.
