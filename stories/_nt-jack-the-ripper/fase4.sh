#!/bin/bash
# NOIRTRACES video 1, fase 4 (19 nov): 5 zinnen zonder "fog" (eigenaar: "best wel vaak het woord fog") opnieuw inspreken,
# dan prep met tekstcontrole (max 3 herstelrondes), muziek, montage, volume, 16mm zonder vuur en de haperingcontroles.
cd /c/Users/rane/Documents/vox-lux-routine
M=stories/_nt-jack-the-ripper; N=_nt-jack-the-ripper; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 REPO=C:/Users/rane/Documents/vox-lux-routine
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
rm -f $V/clips/tmp-* $V/clips/groep-*
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
stap stem; $OMNI tools/engine_stem.py $M --hergebruik 2>&1 | grep -E "hergebruikt|klaar|Error|error" | tail -3
FOUT=""
for ronde in 1 2 3 4; do
  stap prep-ronde-$ronde
  bash tools/prep_engine.sh $N > $V/prep.log 2>&1; tail -6 $V/prep.log
  FOUT=$(grep -oP "TEKST FOUT.*?$N\s+\K[\d ]+$" $V/prep.log | tr ' ' ',')
  [ -z "$FOUT" ] && break
  [ $ronde = 4 ] && { echo "TEKST NOG FOUT: $FOUT - gestopt"; exit 1; }
  $OMNI tools/engine_stem.py $M --hergebruik --opnieuw "$FOUT" --seed-extra $((3000*ronde)) 2>&1 | tail -2
done
grep -q "TEKST GOED" $V/prep.log || { echo "GEEN TEKST GOED - gestopt"; exit 1; }
stap muziek;  $OMNI tools/engine_muziek.py $M 2>&1 | tail -1; MDB=$(cat $V/muziek-db.txt)
stap montage; python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
test -s $V/$N.mp4 || { echo "MONTAGE MISLUKT"; exit 1; }
stap volume;  python tools/eind_volume.py $V/$N.mp4 $V/$N-14.mp4 2>&1 | tail -2
stap 16mm;    python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 --zonder-vuur 2>&1 | tail -3
test -s $V/$N-16mm.mp4 || { echo "16MM MISLUKT"; exit 1; }
stap haperingen-stem; python tools/hapering_check.py $M 2>&1 | tail -12
stap vergelijk-bron;  python tools/vergelijk_bron.py $M $V/$N-16mm.mp4 2>&1 | head -12
stap FASE4-KLAAR
