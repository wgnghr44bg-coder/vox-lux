#!/bin/sh
# Final video: silent 720x1280 render + mix.wav -> 1080x1920 mp4 (H.264 + AAC), as earth-stops.
#   sh lib/finish.sh internet-gone internet-disappeared.mp4
set -e
D="$1"; OUT="$D/$2"
ffmpeg -y -loglevel error -i "$D/silent.mp4" -i "$D/mix.wav" -vf scale=1080:1920:flags=lanczos \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT"
echo "ok: $OUT"
