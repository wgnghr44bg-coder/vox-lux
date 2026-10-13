---
name: comfy
description: Beelden, bewegende clips en lokale stem maken via ComfyUI op de pc van de eigenaar (gratis). Gebruik als de eigenaar "comfy" of "ComfyUI" zegt, of beelden/clips wil zonder xAI.
---
Volg `tools/comfy/README.md`. Kort:
1. Schrijf `prompts.txt` (beelden) en/of `comfy-clips.txt` (clips) in de videomap, commit en push.
2. Vraag de eigenaar op zijn pc te draaien: `python tools/comfy/comfy_batch.py zimage_api.json <map>` (beelden, `--short` voor staand)
   en daarna `python tools/comfy/comfy_batch.py wan_i2v_api.json <map>` (clips). ComfyUI is vanuit de cloud niet bereikbaar.
3. Na zijn push: pull, controleer elke clip met `python3 tools/comfy/check_clips.py <map>/clips` en noteer `clips/CHECKED.txt`.
4. Monteer met de Craft-apps (`tools/craft/README.md`). Stem: lokaal (Kokoro/Chatterbox, testfase) of xAI (kost geld, eerst vragen).
Gebruik nooit xAI voor beelden of clips als de eigenaar "comfy" zegt.
