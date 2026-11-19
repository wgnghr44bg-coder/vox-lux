#!/bin/bash
# BlackSwanVault video 2 (Anthropic): slotkoers -> wachten op vrije videokaart -> stem + Whisper-controle -> muziek -> beeld -> video.
# Log: C:\Users\rane\bsv-anthropic.log. Laatste regel "ANTHROPIC-KLAAR" of een regel met "GESTOPT".
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/blackswanvault/video2
OMNI=C:/Users/rane/omnivoice-venv/Scripts/python.exe
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8
stap(){ echo; echo "=== $(date +%H:%M) $*"; }
stap wachten-op-videokaart
vrij=0
while [ $vrij -lt 2 ]; do
  n=$(powershell -NoProfile -Command "(Get-CimInstance Win32_Process | ? { \$_.Name -match 'python' -and \$_.CommandLine -match 'engine_stem|comfy_batch|beeldcheck|check_stem_tekst' }).Count")
  if [ "${n:-0}" -eq 0 ] 2>/dev/null; then vrij=$((vrij+1)); else vrij=0; fi
  sleep 60
done
curl -s -X POST localhost:8188/free -H "Content-Type: application/json" -d '{"unload_models":true,"free_memory":true}' >/dev/null
stap stem
rm -f zinnen.json stem.wav
$OMNI stem.py 2>&1 | tail -3
test -s stem.wav || { echo "GESTOPT: stem mislukt"; exit 1; }
stap slotkoers
for i in $(seq 1 40); do python slotkoers.py && break; sleep 300; done
grep -q "{SLOT}" script.txt && { echo "GESTOPT: geen slotkoers"; exit 1; }
stap stem-slotzinnen; $OMNI stem.py --opnieuw 9999 2>&1 | tail -2
for ronde in 1 2 3; do
  stap whisper-ronde-$ronde
  $OMNI check_stem.py > check.log 2>&1; tail -8 check.log
  FOUT=$(grep -oP "^FOUT: \K[0-9,]+" check.log)
  [ -z "$FOUT" ] && break
  [ $ronde = 3 ] && { echo "TEKST NOG FOUT: $FOUT (doorgegaan, nakijken)"; break; }
  $OMNI stem.py --opnieuw "$FOUT" --seed $((100*ronde)) 2>&1 | tail -2
done
stap muziek;  python mix.py 2>&1 | tail -2
stap render;  python render3.py > render.log 2>&1; tail -2 render.log
test -s video.mp4 || { echo "GESTOPT: render mislukt"; exit 1; }
stap samenvoegen
ffmpeg -v error -y -i video.mp4 -i mix.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart blackswanvault-anthropic.mp4
ffmpeg -v error -y -i blackswanvault-anthropic.mp4 -vf scale=1280:-2 -c:v libx264 -b:v 300k -maxrate 350k -bufsize 700k -preset fast -c:a aac -b:a 64k -movflags +faststart blackswanvault-anthropic-klein.mp4
ls -la blackswanvault-anthropic*.mp4
stap ANTHROPIC-KLAAR
