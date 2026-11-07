#!/bin/bash
# Gebruik: montage.sh <map> "<titel>" <thumbnail-bestand>
# Audio Engine (eigenaar 6 nov 2026): muziek uit tools/engine_muziek.py, muziekniveau uit video/muziek-db.txt.
set -e
cd ${REPO:-C:/Users/rane/Documents/vox-lux-routine}
M=stories/$1; N=$1; TITEL="$2"; THUMB=$M/$3; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
mkdir -p $V
test -s $V/stem-met-pauzes.wav
stap muziek;      $OMNI tools/engine_muziek.py $M 2>&1 | tail -1; MDB=$(cat $V/muziek-db.txt)
stap montage;     python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
test -s $V/$N.mp4
stap motion;      python $M/maak_motion.py | tail -1; python tools/motion.py $V/$N.mp4 $V/$N-motion.mp4 --plan $M/motion.json --effecten $M/effecten.tsv 2>&1 | tail -2
test -s $V/$N-motion.mp4
stap tikjes;      python tools/stil_tikjes.py $M $V/$N-motion.mp4 $V/$N-schoon.mp4 --muziek-db $MDB 2>&1 | tail -3
test -s $V/$N-schoon.mp4
stap check;       python tools/check_video.py $M video/$N-schoon.mp4 --muziek-db $MDB 2>&1 | tail -8
stap tekst;       $OMNI tools/check_stem_tekst.py $M 2>&1 | tr '\r' '\n' | grep -E "^zin +[0-9]+ |zinnen gecontroleerd|TEKST" | tail -12
stap volume;      python tools/eind_volume.py $V/$N-schoon.mp4 $V/$N-14.mp4 2>&1 | tail -2
test -s $V/$N-14.mp4
stap 16mm;        python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 | tail -1
test -s $V/$N-16mm.mp4
stap qc;          python tools/qc_video.py $M video/$N-16mm.mp4 --titel "$TITEL" --thumbnail $THUMB --beschrijving $M/youtube-beschrijving.txt --muziek-db $MDB --beelden ok --teksten ok --historisch ok --kijker ok 2>&1 | sed -n '/VIDEO QC REPORT/,$p' | head -40
stap KLAAR
