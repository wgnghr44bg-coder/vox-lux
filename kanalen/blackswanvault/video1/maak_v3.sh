#!/bin/bash
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video1
echo "=== $(date +%H:%M) render"
python render3.py > render3.log 2>&1
echo "=== $(date +%H:%M) samenvoegen"
ffmpeg -v error -y -i video-v3.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-nvidia-v3.mp4
ffmpeg -v error -y -i blackswanvault-nvidia-v3.mp4 -vf scale=1280:-2 -c:v libx264 -crf 25 -preset fast -c:a aac -b:a 128k -movflags +faststart blackswanvault-nvidia-v3-720p.mp4
ls -la blackswanvault-nvidia-v3*.mp4
echo "=== $(date +%H:%M) V3-KLAAR"
