#!/bin/bash
# NOIRTRACES video 1, fase 3 (19 nov): montage met 5 vervangen beelden (008 015 040 043 063), dan volume, 16mm zonder vuur
# en de controles op haperingen (stem t.o.v. de bron). Stem en tekstcontrole zijn al klaar in fase 2.
cd /c/Users/rane/Documents/vox-lux-routine
M=stories/_nt-jack-the-ripper; N=_nt-jack-the-ripper; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 REPO=C:/Users/rane/Documents/vox-lux-routine
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
MDB=$(cat $V/muziek-db.txt)
stap montage; python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
test -s $V/$N.mp4 || { echo "MONTAGE MISLUKT"; exit 1; }
stap volume;  python tools/eind_volume.py $V/$N.mp4 $V/$N-14.mp4 2>&1 | tail -2
stap 16mm;    python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 --zonder-vuur 2>&1 | tail -3
test -s $V/$N-16mm.mp4 || { echo "16MM MISLUKT"; exit 1; }
stap haperingen-stem; python tools/hapering_check.py $M 2>&1 | tail -12
stap vergelijk-bron;  python tools/vergelijk_bron.py $M $V/$N-16mm.mp4 2>&1 | head -12
stap FASE3-KLAAR
