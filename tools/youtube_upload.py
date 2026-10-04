#!/usr/bin/env python3
"""Upload a video to YouTube with the YouTube Data API (resumable upload).

Credentials come from environment variables (never hardcode or commit them):
    YT_CLIENT_ID, YT_CLIENT_SECRET and the refresh token of the channel:
    YT_REFRESH_TOKEN (--channel main, the existing channel, default) or
    YT_WHATIF_REFRESH_TOKEN (--channel whatif, the "What if" Shorts channel)
The refresh token needs the https://www.googleapis.com/auth/youtube.upload scope
(or the broader .../auth/youtube scope, which tools/youtube_tidy.py also needs).

Usage:
    python3 tools/youtube_upload.py video.mp4 --title "Pompeii: The Last Day | Sleep Documentary" \
        --description-file description.txt --tags "sleep,history,pompeii"

Videos are uploaded as private, not made for kids, and marked as containing
AI-generated content by default (see stories/YOUTUBE-STANDAARD.md). Note: YouTube keeps videos from
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
THUMB_URL = "https://www.googleapis.com/upload/youtube/v3/thumbnails/set"
CHUNK = 16 * 1024 * 1024  # 16 MB, a multiple of 256 KB as the API requires


CHANNEL_TOKENS = {"main": "YT_REFRESH_TOKEN", "whatif": "YT_WHATIF_REFRESH_TOKEN"}
TOKEN_VAR = CHANNEL_TOKENS["main"]


def access_token() -> str:
    missing = [k for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", TOKEN_VAR)
               if not os.environ.get(k)]
    if missing:
        sys.exit(f"Missing environment variables: {', '.join(missing)}")
    res = requests.post(TOKEN_URL, data={
        "client_id": os.environ["YT_CLIENT_ID"],
        "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": os.environ[TOKEN_VAR],
        "grant_type": "refresh_token",
    }, timeout=60)
    if not res.ok:
        sys.exit(f"Token refresh failed ({res.status_code}): {res.text[:300]}")
    return res.json()["access_token"]


def upload(path: Path, metadata: dict, token: str) -> str:
    size = path.stat().st_size

    def start(meta: dict) -> requests.Response:
        return requests.post(
            UPLOAD_URL,
            params={"uploadType": "resumable", "part": "snippet,status"},
            headers={"Authorization": f"Bearer {token}",
                     "Content-Type": "application/json; charset=UTF-8",
                     "X-Upload-Content-Type": "video/*",
                     "X-Upload-Content-Length": str(size)},
            data=json.dumps(meta), timeout=60)

    init = start(metadata)
    if init.status_code == 400 and "containsSyntheticMedia" in init.text:
        print("Note: API rejected containsSyntheticMedia; set the AI label in YouTube Studio.")
        metadata["status"].pop("containsSyntheticMedia", None)
        init = start(metadata)
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


def set_thumbnail(video_id: str, path: Path, token: str) -> None:
    ctype = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    res = requests.post(THUMB_URL, params={"videoId": video_id, "uploadType": "media"},
                        headers={"Authorization": f"Bearer {token}", "Content-Type": ctype},
                        data=path.read_bytes(), timeout=120)
    if res.ok:
        print("Thumbnail set.")
    else:  # the video itself is fine; set the thumbnail in YouTube Studio instead
        print(f"Thumbnail failed ({res.status_code}): {res.text[:300]}")


def main() -> None:
    global TOKEN_VAR
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("video", type=Path, nargs="?")
    parser.add_argument("--channel", choices=sorted(CHANNEL_TOKENS), default="main",
                        help="main = YT_REFRESH_TOKEN, whatif = YT_WHATIF_REFRESH_TOKEN")
    parser.add_argument("--status", metavar="VIDEO_ID",
                        help="only print the video's status (privacy, upload/rejection state, publishAt)")
    parser.add_argument("--title")
    parser.add_argument("--description-file", type=Path)
    parser.add_argument("--tags", default="", help="comma-separated")
    parser.add_argument("--privacy", choices=["private", "unlisted", "public"], default="private")
    parser.add_argument("--category", default="27", help="YouTube category id (27 = Education)")
    parser.add_argument("--language", default="en",
                        help="title/description and spoken language (default: en)")
    parser.add_argument("--no-synthetic", action="store_true",
                        help="do not mark the video as containing AI-generated content")
    parser.add_argument("--publish-at",
                        help="schedule: RFC3339 UTC time, e.g. 2026-10-03T19:00:00Z "
                             "(video stays private until then, then becomes public)")
    parser.add_argument("--thumbnail", type=Path,
                        help="JPG/PNG up to 2 MB, set after upload (channel must be verified)")
    args = parser.parse_args()
    TOKEN_VAR = CHANNEL_TOKENS[args.channel]
    if args.status:
        res = requests.get("https://www.googleapis.com/youtube/v3/videos",
                           params={"part": "status,processingDetails", "id": args.status},
                           headers={"Authorization": f"Bearer {access_token()}"}, timeout=60)
        items = res.json().get("items", []) if res.ok else []
        print(json.dumps(items[0] if items else res.text[:300], indent=1))
        return
    if not args.video or not args.title:
        parser.error("video and --title are required for an upload")

    metadata = {
        "snippet": {
            "title": args.title[:100],
            "description": args.description_file.read_text(encoding="utf-8")
            if args.description_file else "",
            "tags": [t.strip() for t in args.tags.split(",") if t.strip()],
            "categoryId": args.category,
            "defaultLanguage": args.language,
            "defaultAudioLanguage": args.language,
        },
        "status": {"privacyStatus": args.privacy, "selfDeclaredMadeForKids": False,
                   "containsSyntheticMedia": not args.no_synthetic},
    }
    if args.publish_at:
        if args.privacy != "private":
            parser.error("--publish-at needs --privacy private")
        metadata["status"]["publishAt"] = args.publish_at
    video_id = upload(args.video, metadata, access_token())
    when = f", public at {args.publish_at}" if args.publish_at else ""
    print(f"Done: https://youtu.be/{video_id} ({args.privacy}{when})")
    if args.thumbnail:
        set_thumbnail(video_id, args.thumbnail, access_token())


if __name__ == "__main__":
    main()
