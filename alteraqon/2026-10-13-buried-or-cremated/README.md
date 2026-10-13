# What happens to you if you're buried or cremated? (3D)

Alteraqon-short, 1080x1920, Engels, **volledig 3D** (Remotion + three.js, gratis). Geen ComfyUI-beelden nodig.
Code: `tools/remotion/demo/src/whatif/` (`Buried.tsx`, `buried-scenes.tsx`, `props.tsx`).

## Stappen
1. **Stem (pc eigenaar, gratis, standaardstem):**
   ```
   git fetch origin claude/cavalry-op-github-5t9zml && git checkout claude/cavalry-op-github-5t9zml && git pull
   python tools/comfy/make_voice_local.py alteraqon/2026-10-13-buried-or-cremated --pause-ms 350 --long-pause-ms 800 --sentence-pause-ms 250
   git add alteraqon/2026-10-13-buried-or-cremated/voice.mp3 alteraqon/2026-10-13-buried-or-cremated/voice-times.tsv
   git commit -m "Stem buried-or-cremated" && git push
   ```
2. **Cloudsessie:** tijden overnemen en renderen
   ```
   python3 alteraqon/2026-10-13-buried-or-cremated/make_timeline.py
   sh alteraqon/2026-10-13-buried-or-cremated/make_sfx.sh        # alleen als public/buried/ leeg is
   cd tools/remotion/demo && npx remotion render BuriedOrCremated out/buried-or-cremated.mp4
   ```
Zonder `voice-times.tsv` schat `make_timeline.py` de tijden (proefversie zonder stem).
