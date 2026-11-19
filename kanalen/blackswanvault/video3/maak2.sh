#!/bin/bash
# GTA 6 lange versie: nieuwe zinnen inspreken (oude hergebruikt), Whisper, muziek, render, samenvoegen. Log C:\Users\rane\bsv-gta.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video3
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) stem"; $OMNI stem.py --opnieuw 9999 2>&1 | tail -2
for ronde in 1 2 3; do
  echo "=== $(date +%H:%M) whisper-$ronde"; $OMNI check_stem.py > check.log 2>&1; grep -v "^\[transformers\]" check.log | tail -8
  FOUT=$(grep -oP "^FOUT: \K[0-9,]+" check.log); [ -z "$FOUT" ] && break
  [ $ronde = 3 ] && { echo "TEKST NOG FOUT: $FOUT (nakijken)"; break; }
  $OMNI stem.py --opnieuw "$FOUT" --seed $((100*ronde)) 2>&1 | tail -1
done
echo "=== $(date +%H:%M) muziek"; $OMNI mix.py 2>&1 | tail -1
echo "=== $(date +%H:%M) render"; python render3.py > render.log 2>&1; tail -1 render.log
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-gta6.mp4
ffmpeg -v error -y -i blackswanvault-gta6.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 300k -maxrate 350k -bufsize 700k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-gta6-klein.mp4
ls -la blackswanvault-gta6*.mp4; echo "=== $(date +%H:%M) GTA-KLAAR"
