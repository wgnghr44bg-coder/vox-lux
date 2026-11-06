#!/usr/bin/env python3
"""Wait until YouTube has finished processing an uploaded video.

Run this after the upload and before deleting the video files on the pc: as long as
YouTube is still processing, the local mp4 is the only backup.

Usage:
    python tools/wacht_verwerkt.py VIDEO_ID [--uren 12]

Prints KLAAR and exits 0 when processing succeeded; prints MISLUKT (exit 1) when
YouTube reports a failure, and NOG BEZIG (exit 2) when it is not done within --uren.
"""
import argparse
import sys
import time
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent))
from youtube_upload import access_token  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("video_id")
p.add_argument("--uren", type=float, default=12)
a = p.parse_args()

eind = time.time() + a.uren * 3600
while True:
    v = requests.get("https://www.googleapis.com/youtube/v3/videos",
                     params={"part": "status,processingDetails", "id": a.video_id},
                     headers={"Authorization": f"Bearer {access_token()}"}).json()["items"][0]
    st, pd = v["status"]["uploadStatus"], v.get("processingDetails", {}).get("processingStatus")
    if st == "processed" or pd == "succeeded":
        print("KLAAR", st, pd)
        sys.exit(0)
    if pd in ("failed", "terminated") or st in ("failed", "rejected", "deleted"):
        print("MISLUKT", st, pd, v["status"].get("failureReason"), v["status"].get("rejectionReason"))
        sys.exit(1)
    if time.time() > eind:
        print("NOG BEZIG", st, pd)
        sys.exit(2)
    time.sleep(300)
