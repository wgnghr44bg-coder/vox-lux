#!/bin/bash
# Geldverhaal video 1: na de stem -> AI-beelden -> muziek -> render -> samenvoegen. Log C:\Users\rane\geld-v1.log
R=/c/Users/rane/Documents/vox-lux-routine; V=$R/kanalen/blackswan-nl/video1; cd $V
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
until grep -q "GELD-V1-STEM-KLAAR" /c/Users/rane/geld-v1-stem.log; do sleep 20; done
echo "=== $(date +%H:%M) beelden"; cd $R; python tools/comfy/comfy_batch.py tools/comfy/zimage_api.json kanalen/blackswan-nl/video1/ai 2>&1 | tail -3
curl -s -X POST http://127.0.0.1:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null; cd $V
for f in ai/afbeeldingen/*.png; do n=$(basename $f .png); python -c "from PIL import Image; Image.open('$f').convert('RGB').save('echt/$n.jpg',quality=92)"; grep -q "^$n	" echt/bronnen.tsv || printf "$n\tAI\tGeldverhaal (ComfyUI, Z-Image)\tAI\t-\n" >> echt/bronnen.tsv; done
echo "=== $(date +%H:%M) muziek"; $OMNI mix.py 2>&1 | tail -1
echo "=== $(date +%H:%M) render"; m=$(grep -n "^def shot_op" $R/kanalen/blackswanvault/video3/render3.py | cut -d: -f1)
{ cat render9-basis.py render-shots.py; echo; tail -n +$m $R/kanalen/blackswanvault/video3/render3.py; } > render1.py
python render1.py --plaat plaat.jpg > plaat.log 2>&1; tail -1 plaat.log
python render1.py > render.log 2>&1; tail -1 render.log
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart geldverhaal-asml.mp4
ffmpeg -v error -y -i geldverhaal-asml.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 900k -maxrate 1100k -bufsize 2200k -preset fast -c:a aac -b:a 96k -movflags +faststart geldverhaal-asml-klein.mp4
ls -la geldverhaal-asml*.mp4; echo "=== $(date +%H:%M) GELD-V1-KLAAR"
