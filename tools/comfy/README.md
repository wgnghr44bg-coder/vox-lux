# ComfyUI (gratis, op de pc van de eigenaar)

Zegt de eigenaar **"comfy"**, dan gaan beelden, clips en (lokale) stem via deze route – **niet** via xAI.
ComfyUI draait op de pc (RTX 2080 Super, 8 GB) op `http://127.0.0.1:8188`. De cloudsessie kan er niet bij:
die maakt de prompt-bestanden, pusht, en vraagt de eigenaar het script op zijn pc te draaien.

## Eenmalig op de pc
In ComfyUI: Workflow > Browse Templates, draai het template één keer met de hand en sla het op via Workflow > Export (API):
- beelden: **Z-Image Turbo** → `zimage_api.json`
- clips: **Wan 2.2 5B Video Generation** (met startbeeld) → `wan_i2v_api.json`

## Beelden (Z-Image Turbo)
Bestand `<map>/prompts.txt` → `<map>/afbeeldingen/NAAM.png`
```
python tools/comfy/comfy_batch.py zimage_api.json <map>            # 16:9, 1280x720
python tools/comfy/comfy_batch.py zimage_api.json <map> --short    # staand 1088x1920 (Shorts)
```

## Clips (Wan 2.2 5B)
Bestand `<map>/comfy-clips.txt`, startbeeld `afbeeldingen/NAAM.png` (of `.jpg`) → `<map>/clips/NAAM.mp4` (1024x576, 5 s)
```
python tools/comfy/comfy_batch.py wan_i2v_api.json <map> [NAAM ...]
```
- Bestaande bestanden worden overgeslagen; opnieuw starten kan altijd. Alleen standaard-Python nodig.
- In elke clip-prompt: "Everything stays solid and unchanged, no morphing, no new objects, slow gentle movement".
- Voorbeeld-prompts: `alteraqon/2026-10-13-donut-earth/` (branch `alteraqon`),
  `2026-10-12-mosasaurus/comfy-prompts.md` (repo `ifscape3d-videos`, branch `claude/earth-stops-spinning`).

## Clipcontrole (verplicht)
Wan vervormt soms (dier wordt ander dier, staart wordt schoen). Elke clip eerst controleren:
```
python3 tools/comfy/check_clips.py <map>/clips      # overzichtsblad per clip in <map>/build/check/
```
Bekijk elk blad, noteer in `<map>/clips/CHECKED.txt`: `naam OK`, `naam USE <seconden>` of `naam STILL`.
Fout? Opnieuw laten maken met een andere seed (gratis).

## Standaardstem (gratis, op de pc)
**Chatterbox die Kokoro bm_george nadoet, rustig** (keuze eigenaar 13 okt 2026). Proef: `stem/standaardstem-proef.mp3`.
```
python tools/comfy/make_voice_local.py <map>      # <map>/script-cues.txt -> voice.mp3 + voice-times.tsv
```
Zelfde scriptopmaak als bij xAI (`{img:ID}`, `[pause]`, `[long pause]`); `--dry-run` toont alleen de zinnen.
Voorbeeldstem voor Chatterbox: `stem/voorbeeld-george.mp3`, instellingen exaggeration 0.4, cfg 0.5.

### Stemtest (alle proefstemmen)
Kokoro + Chatterbox, gratis en mag op een kanaal met inkomsten. Installeren in een **aparte** omgeving (uitleg bovenin):
```
python tools/comfy/voice_test_local.py      # -> stemtest/*.wav
```
Werkt op de pc (13 okt 2026): 6 Kokoro- + 3 Chatterbox-stemmen staan als mp3 in
`alteraqon/2026-10-13-donut-earth/stemtest/` (branch `alteraqon`).
xAI (`tools/xai_voiceover.py`) alleen nog als de eigenaar daar om vraagt: kost geld, dus eerst vragen.

## Herkomst
Scripts zijn kopieën: `comfy_batch.py` en `voice_test_local.py` van branch `alteraqon` (`alteraqon/tools/`),
`check_clips.py` van `ifscape3d-videos` (branch `claude/earth-stops-spinning`). Verbeter je ze, houd beide gelijk.
