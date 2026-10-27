#!/usr/bin/env python3
"""Which history-for-sleep videos of big channels are growing fast right now (views per day).

Sleep Archives' best video (Titanic) took off because YouTube suggested it next to a fast-growing
Titanic sleep video of Dusk Voyages. A new video on the same topic as such a hit, released within
a few weeks, has the best chance of the same. This lists the recent videos of the channels below
plus a search for "history for sleep", sorted by views per day. Read-only, costs no money
(only YouTube API quota).

Usage:
    python3 tools/sleep_trends.py               # last 45 days, top 30
    python3 tools/sleep_trends.py --days 60 --top 50
"""

from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone

import requests

from youtube_upload import access_token

API = "https://www.googleapis.com/youtube/v3/"

# Channels that sent us the most viewers via suggested videos (Analytics, Oct 2026),
# plus the big ones in the niche. Add a channel when it shows up as a source.
CHANNELS = {
    "UC-FQ-9IZKcL1RuEpQzTSCzg": "Dusk Voyages",
    "UC6LYB8YhQKo2H6EK3q6U6kw": "Bedtime & Historian",
    "UCejT2lhBB_Dawo5sVTGuXFQ": "History Camp",
    "UCcUEjyUhd-s3Dj0TS0Ekjow": "Sleepy History with Oliver",
    "UCYz9vNXXwBBOvTsmrMh32yg": "Sleepy Old World",
    "UClNq-P2k7NowmhK5ZOoAK9Q": "Sleepy Quiet Historian",
    "UCuij7G73h2G1F69VTrBrM7A": "Boring History Story Relaxing",
}
SEARCH = "history for sleep"


def get(token: str, path: str, **params) -> dict:
    res = requests.get(API + path, headers={"Authorization": f"Bearer {token}"},
                       params=params, timeout=60)
    res.raise_for_status()
    return res.json()


def recent_ids(token: str, since: datetime) -> set[str]:
    ids = set()
    for channel in CHANNELS:
        uploads = "UU" + channel[2:]
        for item in get(token, "playlistItems", part="contentDetails", playlistId=uploads,
                        maxResults=50).get("items", []):
            if item["contentDetails"].get("videoPublishedAt", "") >= since.isoformat():
                ids.add(item["contentDetails"]["videoId"])
    for item in get(token, "search", part="id", q=SEARCH, type="video", order="viewCount",
                    publishedAfter=since.strftime("%Y-%m-%dT%H:%M:%SZ"), maxResults=50,
                    videoDuration="long").get("items", []):
        ids.add(item["id"]["videoId"])
    return ids


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--top", type=int, default=30)
    args = ap.parse_args()
    token = access_token()
    now = datetime.now(timezone.utc)
    ids = sorted(recent_ids(token, now - timedelta(days=args.days)))
    rows = []
    for i in range(0, len(ids), 50):
        for v in get(token, "videos", part="snippet,statistics",
                     id=",".join(ids[i:i + 50])).get("items", []):
            published = datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))
            age = max((now - published).total_seconds() / 86400, 1)
            views = int(v["statistics"].get("viewCount", 0))
            rows.append((views / age, views, published.date(), v["snippet"]["channelTitle"],
                         v["snippet"]["title"], v["id"]))
    rows.sort(reverse=True)
    for per_day, views, date, channel, title, vid in rows[:args.top]:
        print(f"{per_day:>7.0f}/day {views:>8} views  {date}  {channel[:24]:<24}  {title}  ({vid})")


if __name__ == "__main__":
    main()
