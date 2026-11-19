#!/bin/bash
# NOIRTRACES video 2: H.H. Holmes. Zelfde straat als Jack the Ripper (fase4): stem (noirtraces-stem, stem.json), prep met
# tekstcontrole (max 4 rondes), beelden (Z-Image), muziek (alleen B-effect), montage, volume, 16mm zonder vuur, haperingcontroles.
# Wacht eerst tot de Anthropic-keten klaar is en de videokaart vrij is; zet ~/gpu-bezet.lock zodat de Sleep-bewaker wacht.
# Log: C:\Users\rane\nt-holmes.log
cd /c/Users/rane/Documents/vox-lux-routine
M=stories/_nt-hh-holmes; N=_nt-hh-holmes; V=$M/video; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
LOCK=/c/Users/rane/gpu-bezet.lock
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8 REPO=C:/Users/rane/Documents/vox-lux-routine
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
stap wachten-op-anthropic
until grep -qE "ANTHROPIC-KLAAR|GESTOPT" /c/Users/rane/bsv-anthropic.log 2>/dev/null; do sleep 120; done
stap wachten-op-videokaart
vrij=0
while [ $vrij -lt 3 ]; do
  n=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | ? { \$_.Name -match 'python' -and \$_.CommandLine -match 'engine_stem|comfy_batch|beeldcheck|check_stem|stem.py' }).Count")
  if [ "${n:-0}" -eq 0 ] 2>/dev/null; then vrij=$((vrij+1)); else vrij=0; fi
  sleep 60
done
echo "NOIRTRACES Holmes $(date)" > $LOCK
trap 'rm -f $LOCK' EXIT
( while [ -f $LOCK ]; do touch $LOCK; sleep 1800; done ) &
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
stap stem; $OMNI tools/engine_stem.py $M 2>&1 | tail -3
test -s $M/voice.mp3 || { echo "GESTOPT: stem mislukt"; exit 1; }
FOUT=""
for ronde in 1 2 3 4; do
  stap prep-ronde-$ronde
  bash tools/prep_engine.sh $N > $M/prep.log 2>&1; tail -6 $M/prep.log
  FOUT=$(grep -oP "TEKST FOUT.*?$N\s+\K[\d ]+$" $M/prep.log | tr ' ' ',')
  [ -z "$FOUT" ] && break
  [ $ronde = 4 ] && { echo "GESTOPT: TEKST NOG FOUT: $FOUT"; exit 1; }
  $OMNI tools/engine_stem.py $M --hergebruik --opnieuw "$FOUT" --seed-extra $((3000*ronde)) 2>&1 | tail -2
done
grep -q "TEKST GOED" $M/prep.log || { echo "GESTOPT: geen TEKST GOED"; exit 1; }
stap beelden; python tools/comfy/comfy_batch.py tools/comfy/zimage_api.json $M 2>&1 | tail -3
stap aantal-beelden; ls $M/afbeeldingen/*.png | wc -l
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
stap muziek;  $OMNI tools/engine_muziek.py $M 2>&1 | tail -1; MDB=$(cat $V/muziek-db.txt)
stap montage; python tools/make_video.py $M --tijden afbeeldingen-tijden-pauzes.tsv --audio $V/stem-met-pauzes.wav --muziek $V/muziek432.wav --muziek-db $MDB --naam $N 2>&1 | tail -3
test -s $V/$N.mp4 || { echo "GESTOPT: montage mislukt"; exit 1; }
stap volume;  python tools/eind_volume.py $V/$N.mp4 $V/$N-14.mp4 2>&1 | tail -2
stap 16mm;    python tools/film16.py $V/$N-14.mp4 $V/$N-16mm.mp4 --zonder-vuur 2>&1 | tail -3
test -s $V/$N-16mm.mp4 || { echo "GESTOPT: 16mm mislukt"; exit 1; }
stap haperingen-stem; python tools/hapering_check.py $M 2>&1 | tail -12
stap vergelijk-bron;  python tools/vergelijk_bron.py $M $V/$N-16mm.mp4 2>&1 | head -12
stap HOLMES-KLAAR
