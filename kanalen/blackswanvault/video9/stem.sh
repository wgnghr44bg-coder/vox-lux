#!/bin/bash
# Video 9: stem + Whisper-controle (tekst + woord) + muziek. Log C:\Users\rane\bsv-v9-stem.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video9
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) stem"; rm -f zinnen.json stem.wav; $OMNI stem.py 2>&1 | tail -2
for ronde in 1 2 3; do
  echo "=== $(date +%H:%M) whisper-$ronde"; $OMNI check_stem.py > check.log 2>&1; grep -v -E "Loading|transformers|W1120" check.log | tail -12
  FOUT=$(grep -oP "^FOUT: \K[0-9,]+" check.log); [ -z "$FOUT" ] && break
  [ $ronde = 3 ] && { echo "TEKST NOG FOUT: $FOUT"; break; }
  $OMNI stem.py --opnieuw "$FOUT" --seed $((100*ronde)) 2>&1 | tail -1
done
echo "=== $(date +%H:%M) woordcheck"; $OMNI woordcheck.py > woord.log 2>&1; grep "LET OP" woord.log | tail -40
echo "=== $(date +%H:%M) V9-STEM-KLAAR"
