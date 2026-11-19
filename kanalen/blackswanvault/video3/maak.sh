#!/bin/bash
# GTA 6: wacht op stem.sh (GTA-STEM-KLAAR), dan render + samenvoegen. Log C:\Users\rane\bsv-gta.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video3
until grep -qE "GTA-STEM-KLAAR" /c/Users/rane/bsv-gta-stem.log; do sleep 60; done
echo "=== $(date +%H:%M) render"; python render3.py > render.log 2>&1; tail -2 render.log
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
echo "=== $(date +%H:%M) samenvoegen"
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-gta6.mp4
ffmpeg -v error -y -i blackswanvault-gta6.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 400k -maxrate 450k -bufsize 900k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-gta6-klein.mp4
ls -la blackswanvault-gta6*.mp4; echo "=== $(date +%H:%M) GTA-KLAAR"
