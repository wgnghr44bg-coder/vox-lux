#!/usr/bin/env python3
"""Upload a video to YouTube with the YouTube Data API (resumable upload).

Credentials come from environment variables (never hardcode or commit them):
    YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN
The refresh token needs the https://www.googleapis.com/auth/youtube.upload scope.

Usage:
    python3 tools/youtube_upload.py video.mp4 --title "Pompeii: The Last Day | Sleep Documentary" \
        --description-file description.txt --tags "sleep,history,pompeii"

Videos are uploaded as private by default. Note: YouTube keeps videos from
unaudited API projects private anyway; publish them in YouTube Studio.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
CHUNK = 16 * 1024 * 1024  # 16 MB, a multiple of 256 KB as the API requires


def access_token() -> str:
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN")
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")
    res = requests.post(TOKEN_URL, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ["YT_REFRESH_TOKEN"],
        "grant_type": "refresh_token",
    }, timeout=60)
    if not res.ok:
        sys.exit(f"Token refresh failed ({res.status_code}): {res.text[:300]}")
    return res.json()["access_token"]


def upload(path: Path, metadata: dict, token: str) -> str:
    size = path.stat().st_size
    init = requests.post(
        UPLOAD_URL,
        params={"uploadType": "resumable", "part": "snippet,status"},
        headers={"Authorization": f"Bearer {token}",
                 "Content-Type": "application/json; charset=UTF-8",
                 "X-Upload-Content-Type": "video/*",
                 "X-Upload-Content-Length": str(size)},
        data=json.dumps(metadata), timeout=60)
    if not init.ok:
        sys.exit(f"Could not start upload ({init.status_code}): {init.text[:300]}")
    session_url = init.headers["Location"]

    sent = 0
    with path.open("rb") as f:
        while sent < size:
            f.seek(sent)
            chunk = f.read(CHUNK)
            end = sent + len(chunk) - 1
            for attempt in range(5):
                try:
                    res = requests.put(session_url, data=chunk, timeout=300, headers={
                        "Authorization": f"Bearer {token}",
                        "Content-Range": f"bytes {sent}-{end}/{size}"})
                except requests.RequestException:
                    res = None
                if res is not None and res.status_code in (200, 201):
                    return res.json()["id"]
                if res is not None and res.status_code == 308:  # chunk accepted
                    rng = res.headers.get("Range")
                    sent = int(rng.split("-")[1]) + 1 if rng else 0
                    break
                if res is not None and res.status_code < 500:
                    sys.exit(f"Upload failed ({res.status_code}): {res.text[:300]}")
                time.sleep(2 ** (attempt + 1))
            else:
                sys.exit("Upload failed after retries; run again to restart.")
            print(f"Uploaded {sent / size:.0%}", flush=True)
    sys.exit("Upload ended without a video id.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("video", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--description-file", type=Path)
    parser.add_argument("--tags", default="", help="comma-separated")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--category", default="27", help="YouTube category id (27 = Education)")
    args = parser.parse_args()

    metadata = {
        "snippet": {
            "title": args.title[:100],
            "description": args.description_file.read_text(encoding="utf-8")
            if args.description_file else "",
            "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
            "categoryId": args.category,
        },
        "status": {"privacyStatus": args.privacy, "selfDeclaredMadeForKids": False},
    }
    video_id = upload(args.video, metadata, access_token())
    print(f"Done: https://youtu.be/{video_id} ({args.privacy})")


if __name__ == "__main__":
    main()
