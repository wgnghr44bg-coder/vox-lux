#!/bin/bash
# Reserve 1 (RAM): AI-beelden via ComfyUI, alleen als de stem klaar is (pc: één zware taak tegelijk). Log C:\Users\rane\bsv-r1-beelden.log
cd /c/Users/rane/Documents/vox-lux-routine
grep -q "R1-STEM-KLAAR" /c/Users/rane/bsv-r1-stem.log || { echo "$(date +%H:%M) stem nog niet klaar, niets gedaan"; exit 0; }
echo "=== $(date +%H:%M) beelden"
python tools/comfy/comfy_batch.py tools/comfy/zimage_api.json kanalen/blackswanvault/reserve1-ram/ai 2>&1 | tail -5
curl -s -X POST http://127.0.0.1:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
ls kanalen/blackswanvault/reserve1-ram/ai/afbeeldingen | wc -l; echo "=== $(date +%H:%M) R1-BEELDEN-KLAAR"
