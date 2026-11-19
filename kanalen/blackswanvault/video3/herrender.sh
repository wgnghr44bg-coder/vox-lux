#!/bin/bash
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video3; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) render"; python render3.py > render.log 2>&1; tail -1 render.log
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-gta6.mp4
ffmpeg -v error -y -i blackswanvault-gta6.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 300k -maxrate 350k -bufsize 700k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-gta6-klein.mp4
echo "=== $(date +%H:%M) KLAAR-gta6"
