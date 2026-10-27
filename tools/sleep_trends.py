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
    python3 tools/sleep_trends.py --check Hindenburg Lusitania "Apollo 13"
        # per topic: do we already have it (our own uploads), and how big are the
        # existing sleep videos about it (demand). Highest score = best chance.
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


def our_titles(token: str) -> list[str]:
    """Titles of all uploads of the channel of the token (Sleep Archives)."""
    channel = get(token, "channels", part="contentDetails", mine="true")["items"][0]
    uploads = channel["contentDetails"]["relatedPlaylists"]["uploads"]
    titles, page = [], None
    while True:
        body = get(token, "playlistItems", part="snippet", playlistId=uploads, maxResults=50,
                   **({"pageToken": page} if page else {}))
        titles += [i["snippet"]["title"] for i in body.get("items", [])]
        page = body.get("nextPageToken")
        if not page:
            return titles


def check(token: str, topics: list[str]) -> None:
    """Per topic: our existing videos about it, and the demand for sleep videos about it."""
    ours = our_titles(token)
    now = datetime.now(timezone.utc)
    results = []
    for topic in topics:
        mine = [t for t in ours if topic.lower() in t.lower()]
        ids = [i["id"]["videoId"] for i in get(
            token, "search", part="id", q=f"{topic} sleep", type="video",
            videoDuration="long", maxResults=50).get("items", [])]
        videos = get(token, "videos", part="snippet,statistics",
                     id=",".join(ids)).get("items", []) if ids else []
        # only sleep videos that are really about the topic
        videos = [v for v in videos if topic.lower() in v["snippet"]["title"].lower()
                  and "sleep" in v["snippet"]["title"].lower()]
        total = sum(int(v["statistics"].get("viewCount", 0)) for v in videos)
        recent = [v for v in videos if (now - datetime.fromisoformat(
            v["snippet"]["publishedAt"].replace("Z", "+00:00"))).days <= 60]
        best = max(videos, key=lambda v: int(v["statistics"].get("viewCount", 0)), default=None)
        results.append((0 if mine else total, topic, mine, len(videos), len(recent), total, best))
    results.sort(key=lambda r: r[0], reverse=True)
    for _, topic, mine, count, recent, total, best in results:
        status = f"AL GEMAAKT: {mine[0]}" if mine else "nieuw"
        top = (f"best: {int(best['statistics'].get('viewCount', 0)):,} "
               f"({best['snippet']['channelTitle'][:20]})") if best else "best: -"
        print(f"{topic:<24} {status:<14.60} {count:>2} sleep video's, {recent} recent, "
              f"{total:>10,} views samen, {top}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--days", type=int, default=45)
    ap.add_argument("--top", type=int, default=30)
    ap.add_argument("--check", nargs="+", metavar="TOPIC",
                    help="score these topics instead of listing trends")
    args = ap.parse_args()
    token = access_token()
    if args.check:
        check(token, args.check)
        return
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
