#!/bin/bash
# 21 nov: slotkoersen i.p.v. koersen van vóór de sluiting (Nasdaq 100 -5,6%, goud -4,6% naar $3.515, ± 1/3 onder top, VIX 36).
# video8 (Bitcoin) zinnen 88,94,95; video9 (SpaceX) zin 3 + SpaceX-Short. Log C:\Users\rane\fix-cijfers.log
B=/c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault; OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
wacht_render() {   # pc heeft weinig geheugen: niet renderen zolang een ander account rendert (bv. Geldverhaal render1.py)
  while powershell -NoProfile -c "if (Get-CimInstance Win32_Process | Where-Object { \$_.CommandLine -match 'render1\.py|render[0-9]+\.py' -and \$_.CommandLine -notmatch 'powershell' }) { exit 0 } else { exit 1 }"; do sleep 30; done
}
m=$(grep -n "^def shot_op" $B/video3/render3.py | cut -d: -f1)
for v in 8 9; do
  cd $B/video$v; naam=$([ $v = 8 ] && echo bitcoin || echo spacex); nrs=$([ $v = 8 ] && echo 88,94,95 || echo 3)
  echo "=== $(date +%H:%M) video$v stem $nrs"
  for f in stem.wav zinnen.json mix.wav blackswanvault-$naam.mp4 blackswanvault-$naam-klein.mp4; do cp -n $f oud-voor-fix-$f 2>/dev/null; done
  $OMNI stem.py --opnieuw $nrs --seed 300 2>&1 | tail -1
  $OMNI check_stem.py > check-fix.log 2>&1; grep -E "^FOUT|OK|GOED" check-fix.log | tail -2
  echo "=== $(date +%H:%M) video$v muziek"; $OMNI mix.py 2>&1 | tail -1
  { cat render$v-basis.py render$v-shots.py; echo; tail -n +$m $B/video3/render3.py; } > render$v.py
  wacht_render; echo "=== $(date +%H:%M) video$v render"; bash maak.sh 2>&1 | tail -3
done
echo "=== $(date +%H:%M) spacex-short"; cd $B/shorts
cp -n spacex-short-1.mp4 oud-voor-fix-spacex-short-1.mp4 2>/dev/null
python maak_short.py ../video9 ../video9/blackswanvault-spacex.mp4 0 11 "SPACEX JUST FELL BELOW ITS IPO PRICE" spacex-short-1.mp4 --zonder-ondertitels 2>&1 | tail -1
echo "=== $(date +%H:%M) FIX-KLAAR"
