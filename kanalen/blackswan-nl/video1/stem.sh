#!/bin/bash
# Geldverhaal video 1: stem per zin + Whisper-controle (nl). Log C:\Users\rane\geld-v1-stem.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswan-nl/video1
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
echo "=== $(date +%H:%M) stem"; rm -f zinnen.json stem.wav; $OMNI stem.py 2>&1 | tail -2
echo "=== $(date +%H:%M) whisper"; $OMNI check_nl.py > check.log 2>&1; grep -E "^ ?[0-9]+ |^   ->" check.log > check-kort.log
echo "=== $(date +%H:%M) GELD-V1-STEM-KLAAR"
