#!/bin/bash
# Gebruik: prep.sh <map>  (na make_voice_omni): tijden, pauzes, zachte klank en tekstcontrole (Whisper).
set -e
cd ${REPO:-C:/Users/rane/Documents/vox-lux-routine}
M=stories/$1; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
mkdir -p $M/video
stap tijden; python $M/maak_tijden.py | tail -2
stap pauzes; python tools/add_pauses.py --niet-zwaarder --kort $M 2>&1 | tail -3
stap zacht;  python tools/zachte_stem.py $M 2>&1 | tail -2
test -s $M/video/stem-met-pauzes.wav
stap tekst;  $OMNI tools/check_stem_tekst.py $M 2>&1 | tr '\r' '\n' | grep -E "^zin +[0-9]+ |zinnen gecontroleerd|TEKST" | tail -30
stap KLAAR
