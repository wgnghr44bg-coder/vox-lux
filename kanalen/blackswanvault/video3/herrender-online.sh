#!/bin/bash
# 20 nov: zinnen 44 (GTA Online), 63, 71 opnieuw ingesproken; alleen muziek + render. Log C:\Users\rane\bsv-gta-online.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video3
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) muziek"; $OMNI mix.py 2>&1 | tail -1
echo "=== $(date +%H:%M) render"; python render3.py > render.log 2>&1; tail -1 render.log
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-gta6.mp4
ffmpeg -v error -y -i blackswanvault-gta6.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 400k -maxrate 450k -bufsize 900k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-gta6-klein.mp4
ls -la blackswanvault-gta6*.mp4; echo "=== $(date +%H:%M) GTA-ONLINE-KLAAR"
