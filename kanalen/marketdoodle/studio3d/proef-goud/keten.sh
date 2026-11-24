#!/bin/bash
# proef-goud: wacht tot de beeldcheck klaar is -> stem -> Whisper -> woordtijden -> opnemen -> mixen. Log: ~/goud3d.log
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/marketdoodle/studio3d/proef-goud
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe; export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
bezig() { powershell -NoProfile -c "@(Get-CimInstance Win32_Process -Filter \"Name like 'python%'\" | ? { \$_.CommandLine -match 'beeldcheck' }).Count"; }
[ -n "$NU" ] || while [ "$(bezig | tr -d '')" != "0" ]; do echo "$(date +%H:%M) wacht op beeldcheck"; sleep 60; done
[ -n "$NU" ] || curl -s -X POST http://127.0.0.1:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
echo "=== $(date +%H:%M) stem"; $OMNI stem.py 2>&1 | grep -v "Loading weights" | tail -3
echo "=== $(date +%H:%M) controle"; $OMNI check_stem.py 2>&1 | grep -v "Loading weights\|Warning\|warn" > check.log; tail -8 check.log
echo "=== $(date +%H:%M) woordtijden"; $OMNI ../../../blackswan-nl/proef-teken/woordtijden.py en 2>&1 | tail -1
python maak_data.py && python geluid.py || { echo GESTOPT; exit 1; }
echo "=== $(date +%H:%M) opnemen"; rm -rf frames; node render.mjs 8781 2>&1 | grep -v "^\[pagina\] THREE" | tail -3
echo "=== $(date +%H:%M) mixen"
ffmpeg -y -loglevel error -framerate 30 -i frames/%05d.jpg -i stem.wav -stream_loop -1 -i ../../video1/muziek.wav -i sfx.wav \
  -filter_complex "[2:a]volume=0.07[m];[1:a]apad[v];[3:a]volume=0.6[k];[v][m][k]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]" \
  -map 0:v -map "[a]" -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart proef-goud-3d.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 proef-goud-3d.mp4; ls -la proef-goud-3d.mp4
echo "=== $(date +%H:%M) KLAAR"
