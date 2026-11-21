#!/bin/bash
# Geldverhaal video 1, ronde 2: alleen nieuwe zinnen inspreken (Anthropic-opening), dan muziek, render, samenvoegen. Log C:\Users\rane\geld-v1b.log
R=/c/Users/rane/Documents/vox-lux-routine; cd $R/kanalen/blackswan-nl/video1
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) stem (alleen nieuwe zinnen)"; $OMNI stem.py --opnieuw 9999 --seed 7 2>&1 | tail -1
$OMNI check_nl.py > check.log 2>&1; grep -E "^ ?[0-9]+ |^   ->" check.log | head -12
echo "=== $(date +%H:%M) muziek"; $OMNI mix.py 2>&1 | tail -1
echo "=== $(date +%H:%M) render"; m=$(grep -n "^def shot_op" $R/kanalen/blackswanvault/video3/render3.py | cut -d: -f1)
{ cat render9-basis.py render-shots.py; echo; tail -n +$m $R/kanalen/blackswanvault/video3/render3.py; } > render1.py
python render1.py --plaat plaat.jpg > plaat.log 2>&1; tail -1 plaat.log
python render1.py > render.log 2>&1; tail -1 render.log
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart geldverhaal-asml.mp4
ffmpeg -v error -y -i geldverhaal-asml.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 900k -maxrate 1100k -bufsize 2200k -preset fast -c:a aac -b:a 96k -movflags +faststart geldverhaal-asml-klein.mp4
ls -la geldverhaal-asml*.mp4; echo "=== $(date +%H:%M) GELD-V1-KLAAR"
