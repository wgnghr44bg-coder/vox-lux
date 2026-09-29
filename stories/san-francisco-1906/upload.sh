#!/usr/bin/env bash
# Upload volgens planning.txt: privé + publishAt. Draai vanuit de repo-root.
set -euo pipefail
S=stories/san-francisco-1906
TAGS="sleep documentary, history for sleep, bedtime story, relaxing history, sleep story, 432hz, san francisco, 1906 earthquake, san francisco earthquake, great fire of 1906, california history"
STAGS="sleep documentary, history for sleep, bedtime story, relaxing history, sleep story, 432hz, san francisco, 1906 earthquake, shorts"

out=$(python3 tools/youtube_upload.py $S/video/san-francisco-1906.mp4 \
  --title "The San Francisco Earthquake of 1906 | Sleep Documentary" \
  --description-file $S/youtube-beschrijving.txt --tags "$TAGS" --category 27 \
  --publish-at 2026-10-03T19:00:00Z --thumbnail $S/thumbnail.jpg | tee /dev/stderr)
LONG=$(grep -o 'https://youtu.be/[A-Za-z0-9_-]*' <<<"$out" | head -1)
echo "LANG: $LONG"

upload_short() {  # naam publishAt
  local n=$1 at=$2 f=$S/shorts-teksten/$1-youtube.txt
  sed -i "s#Full sleep documentary: LINK#Full sleep documentary: $LONG#" "$f"
  local title; title=$(sed -n 's/^TITEL: //p' "$f")
  tail -n +3 "$f" > "$S/video/$n-beschrijving.txt"
  python3 tools/youtube_upload.py $S/video/shorts/$n.mp4 --title "$title" \
    --description-file "$S/video/$n-beschrijving.txt" --tags "$STAGS" --category 27 \
    --publish-at "$at" | grep -o 'https://youtu.be/[A-Za-z0-9_-]*' | head -1
}
S1=$(upload_short 1-wijn 2026-10-04T16:00:00Z); echo "SHORT1: $S1"
S3=$(upload_short 3-caruso 2026-10-05T16:00:00Z); echo "SHORT3: $S3"

sed -i "s#^lange video:.*#lange video: $LONG#; s#^Short 1:.*#Short 1: $S1#; s#^Short 3:.*#Short 3: $S3#" $S/planning.txt
