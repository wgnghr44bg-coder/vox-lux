#!/bin/bash
# Video 7: render + samenvoegen (stem/mix al klaar). Log C:\Users\rane\bsv-v7.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video7
export PYTHONUTF8=1
echo "=== $(date +%H:%M) render"; python render7.py > render.log 2>&1; grep -v "Broken pipe" render.log | tail -1
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-blackfriday.mp4
ffmpeg -v error -y -i blackswanvault-blackfriday.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 400k -maxrate 450k -bufsize 900k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-blackfriday-klein.mp4
ls -la blackswanvault-blackfriday*.mp4; echo "=== $(date +%H:%M) V7-KLAAR"
