#!/bin/bash
# Na de beelden: zin 307 opnieuw, tijden + pauzes + tekstcontrole opnieuw, dan montage. Stopt bij tekstfouten.
cd /c/Users/rane/Documents/vox-lux-routine
M=stories/_nt-jack-the-ripper; N=_nt-jack-the-ripper; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 REPO=C:/Users/rane/Documents/vox-lux-routine
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
until grep -q "=== .* 16mm" /c/Users/rane/nt-ripper.log && ! pgrep -f maak.sh >/dev/null 2>&1; do sleep 30; done
sleep 60
stap aantal-beelden; ls $M/afbeeldingen/*.png | wc -l
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
FOUT=307
for ronde in 1 2 3; do
  stap herstel-ronde-$ronde
  if [ -n "$FOUT" ]; then $OMNI tools/engine_stem.py $M --hergebruik --opnieuw "$FOUT" --seed-extra $((3000*ronde)) 2>&1 | tail -2; fi
  bash tools/prep_engine.sh $N > $V/prep.log 2>&1; tail -12 $V/prep.log
  FOUT=$(grep -oP "TEKST FOUT.*?$N\s+\K[\d ]+$" $V/prep.log | tr ' ' ',')
  [ -z "$FOUT" ] && break
done
if [ -n "$FOUT" ]; then echo "TEKST NOG FOUT: $FOUT - gestopt"; exit 1; fi
stap muziek;  $OMNI tools/engine_muziek.py $M 2>&1 | tail -1; MDB=$(cat $V/muziek-db.txt)
stap montage; python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
stap volume;  python tools/eind_volume.py $V/$N.mp4 $V/$N-14.mp4 2>&1 | tail -2
stap 16mm;    python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 --zonder-vuur | tail -1
stap FASE2-KLAAR
