# Mayflower — wat nog moet (27 okt 2026)

## Stand
- 67 van de 84 beelden zijn goed (gecontroleerd). **17 ontbreken nog** (tweede keuring afgekeurd):
  007 008 011 014 019 020 051 061 065 066 067 068 070 072 073 074 077 — nieuwe prompts staan al in `prompts.txt`.
- Stem nog niet gemaakt.
- Muziek (ambient 432, gratis) wordt in de cloud gemaakt; ondertitels, render en upload ook in de cloud.

## Op de pc van de eigenaar (gratis), vanuit de map vox-lux
```
git pull
python tools/comfy/comfy_batch.py zimage_api.json stories/mayflower          # alleen de 17 ontbrekende
python tools/comfy/make_voice_local.py stories/mayflower                      # stem-env actief; -> voice.mp3 + voice-times.tsv
git add stories/mayflower && git commit -m "mayflower: laatste beelden en stem (lokaal)" && git push
```
Daarna in de cloud: beelden keuren, muziek + ondertitels, MP4 renderen, versturen.
