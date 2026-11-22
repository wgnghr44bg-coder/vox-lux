#!/bin/bash
# Market Doodle video1: render lang + Short, mixen, controle (log C:\Users\rane\md1-render.log)
cd /c/Users/rane/Documents/vox-lux-routine/kanalen/marketdoodle/video1
export PYTHONUTF8=1 PYTHONIOENCODING=utf-8; T=../../blackswan-nl/proef-teken
mix() {  # beeld stem muziek teken uit
  ffmpeg -v error -y -i $1 -i $2 -stream_loop -1 -i $3 -i $4 -filter_complex "[2:a]volume=0.07[m];[1:a]apad[v];[3:a]volume=0.55[k];[v][m][k]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart $5 || { echo GESTOPT mix; exit 1; }
}
if [ "$1" != "short" ]; then
if [ ! -s beeld.mp4 ]; then echo "=== $(date +%H:%M) render lang"; python $T/teken_anim.py scene.json beeld.mp4 || { echo GESTOPT render; exit 1; }; fi
python $T/geluid.py scene.json teken.wav; python muziek.py scene.json zinnen.json muziek.wav
mix beeld.mp4 stem.wav muziek.wav teken.wav market-doodle-ai-selloff.mp4
echo "--- freezedetect lang"; ffmpeg -i market-doodle-ai-selloff.mp4 -vf freezedetect=n=0.0005:d=1.5 -map 0:v -f null - 2>&1 | grep freeze_ | head -20; echo "--- einde freeze"
ffmpeg -v error -y -i market-doodle-ai-selloff.mp4 -vf scale=854:480 -c:v libx264 -b:v 700k -c:a aac -b:a 96k -movflags +faststart market-doodle-ai-selloff-klein.mp4
fi
[ "$1" = "lang" ] && { echo "=== $(date +%H:%M) LANG-KLAAR"; exit 0; }
echo "=== $(date +%H:%M) short"
python maak_short.py && python $T/volgorde.py short/scene.json || { echo GESTOPT short-plan; exit 1; }
python $T/teken_anim.py short/scene.json short/beeld.mp4 || { echo GESTOPT render-short; exit 1; }
python $T/geluid.py short/scene.json short/teken.wav; python muziek.py short/scene.json short/zinnen.json short/muziek.wav
mix short/beeld.mp4 short/stem.wav short/muziek.wav short/teken.wav market-doodle-short.mp4
echo "--- freezedetect short"; ffmpeg -i market-doodle-short.mp4 -vf freezedetect=n=0.0005:d=1.5 -map 0:v -f null - 2>&1 | grep freeze_ | head -20; echo "--- einde freeze"
ffmpeg -v error -y -i market-doodle-short.mp4 -vf scale=540:960 -c:v libx264 -b:v 900k -c:a aac -b:a 96k -movflags +faststart market-doodle-short-klein.mp4
ls -la *.mp4
echo "=== $(date +%H:%M) MD1-KLAAR"
