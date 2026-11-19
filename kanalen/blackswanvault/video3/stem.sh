#!/bin/bash
# GTA 6: stem + Whisper-controle (max 3 rondes). Log C:\Users\rane\bsv-gta-stem.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video3
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) stem"; rm -f zinnen.json stem.wav; $OMNI stem.py 2>&1 | tail -2
for ronde in 1 2 3; do
  echo "=== $(date +%H:%M) whisper-$ronde"; $OMNI check_stem.py > check.log 2>&1; tail -6 check.log
  FOUT=$(grep -oP "^FOUT: \K[0-9,]+" check.log); [ -z "$FOUT" ] && break
  [ $ronde = 3 ] && { echo "TEKST NOG FOUT: $FOUT"; break; }
  $OMNI stem.py --opnieuw "$FOUT" --seed $((100*ronde)) 2>&1 | tail -1
done
echo "=== $(date +%H:%M) muziek"; python mix.py 2>&1 | tail -1
echo "=== $(date +%H:%M) GTA-STEM-KLAAR"
