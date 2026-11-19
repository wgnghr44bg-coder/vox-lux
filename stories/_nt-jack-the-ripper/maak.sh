#!/bin/bash
# NOIRTRACES video 1: Jack the Ripper. Zelfde straat als Sleep Archives, met stem.json (noirtraces-stem, alleen B-effect).
cd /c/Users/rane/Documents/vox-lux-routine
M=stories/_nt-jack-the-ripper; N=_nt-jack-the-ripper; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 REPO=C:/Users/rane/Documents/vox-lux-routine
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
stap stem;    $OMNI tools/engine_stem.py $M 2>&1 | tail -3
test -s $M/voice.mp3 || { echo "STEM MISLUKT"; exit 1; }
stap prep;    bash tools/prep_engine.sh $N 2>&1 | tail -15
stap beelden; python tools/comfy/comfy_batch.py tools/comfy/zimage_api.json $M 2>&1 | tail -3
stap muziek;  $OMNI tools/engine_muziek.py $M 2>&1 | tail -1; MDB=$(cat $V/muziek-db.txt)
stap montage; python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
stap volume;  python tools/eind_volume.py $V/$N.mp4 $V/$N-14.mp4 2>&1 | tail -2
stap 16mm;    python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 --zonder-vuur | tail -1
stap KLAAR
