#!/bin/sh
# Gratis geluidseffecten met ffmpeg -> tools/remotion/demo/public/buried/
# Gebruik (vanuit vox-lux): sh alteraqon/2026-10-13-buried-or-cremated/make_sfx.sh
set -e
OUT=tools/remotion/demo/public/buried
mkdir -p "$OUT"
F="ffmpeg -v error -y"
# donkere drone (100 s): lage tonen + gefilterde ruis, langzaam zwellend
$F -f lavfi -i "sine=f=55:d=100" -f lavfi -i "sine=f=82.4:d=100" -f lavfi -i "anoisesrc=c=brown:a=0.4:d=100" \
  -filter_complex "[0]volume=0.5[a];[1]volume=0.25,tremolo=f=0.15:d=0.6[b];[2]lowpass=f=180,volume=0.5[c];[a][b][c]amix=3:normalize=0,afade=t=in:d=3,volume=0.6" \
  -b:a 128k "$OUT/drone.mp3"
# lage klap (bij elke tijdstempel)
$F -f lavfi -i "sine=f=48:d=1.6" -f lavfi -i "anoisesrc=c=brown:a=0.9:d=0.3" \
  -filter_complex "[0]afade=t=out:st=0.05:d=1.5[a];[1]lowpass=f=300,afade=t=out:d=0.3[b];[a][b]amix=2:normalize=0,volume=1.6" \
  -b:a 128k "$OUT/hit.mp3"
# zware dreun (deksel dicht, "Then.")
$F -f lavfi -i "sine=f=38:d=2.5" -f lavfi -i "anoisesrc=c=brown:a=1:d=0.6" \
  -filter_complex "[0]afade=t=out:st=0.05:d=2.4[a];[1]lowpass=f=220,afade=t=out:d=0.6[b];[a][b]amix=2:normalize=0,volume=2.2" \
  -b:a 128k "$OUT/thud.mp3"
# vuur (knetteren + gebrul, 12 s, loopbaar)
$F -f lavfi -i "anoisesrc=c=brown:a=0.8:d=12" -f lavfi -i "anoisesrc=c=white:a=0.25:d=12" \
  -filter_complex "[0]lowpass=f=400,tremolo=f=3:d=0.3[a];[1]highpass=f=2500,tremolo=f=11:d=0.9,volume=0.4[b];[a][b]amix=2:normalize=0,volume=0.9" \
  -b:a 128k "$OUT/fire.mp3"
# opstijgende raket
$F -f lavfi -i "anoisesrc=c=pink:a=0.9:d=5" -filter_complex "lowpass=f=900,afade=t=in:d=1.5,afade=t=out:st=3.5:d=1.5,volume=0.9" -b:a 128k "$OUT/rocket.mp3"
echo "sfx klaar in $OUT"
