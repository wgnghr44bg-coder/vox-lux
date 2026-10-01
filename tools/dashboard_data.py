#!/usr/bin/env python3
"""Collect everything the channel dashboard shows, as one JSON document.

Reads the YouTube Data and Analytics APIs (same token as youtube_upload.py) and the
`stories/*/planning.txt` files on origin/main and origin/claude/* (new format:
`onderwerp`, `lang`, `yt-short`, `shortN` lines). Run `git fetch origin` first.

Usage:
    python3 tools/dashboard_data.py > /tmp/dashboard.json

Output keys: watch_hours_12m, updated, channel, period, daily, top, traffic, youtube_schedule,
planning, playlists. Times are Dutch local time ("YYYY-MM-DD HH:MM").
"""

from __future__ import annotations

import datetime as dt
import json
import re
import subprocess
from zoneinfo import ZoneInfo

import requests

from youtube_tidy import call
from youtube_upload import access_token

NL = ZoneInfo("Europe/Amsterdam")
REPORTS = "https://youtubeanalytics.googleapis.com/v2/reports"


def nl_time(iso: str) -> str:
    t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00")).astimezone(NL)
    return t.strftime("%Y-%m-%d %H:%M")


def seconds(iso: str) -> int:
    """ISO 8601 duration (PT1H2M3S) to seconds."""
    h, m, s = (int(x or 0) for x in re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso).groups())
    return h * 3600 + m * 60 + s


def report(token: str, start: dt.date, end: dt.date, **params) -> list[dict]:
    res = requests.get(REPORTS, headers={"Authorization": f"Bearer {token}"}, timeout=60,
                       params={"ids": "channel==MINE", "startDate": start.isoformat(),
                               "endDate": end.isoformat(), **params})
    res.raise_for_status()
    body = res.json()
    names = [c["name"] for c in body.get("columnHeaders", [])]
    return [dict(zip(names, row)) for row in body.get("rows", [])]


def totals(token: str, start: dt.date, end: dt.date) -> dict:
    rows = report(token, start, end, metrics="views,estimatedMinutesWatched,subscribersGained,"
                  "subscribersLost")
    return rows[0] if rows else {"views": 0, "estimatedMinutesWatched": 0,
                                 "subscribersGained": 0, "subscribersLost": 0}


def git(*args: str) -> str:
    return subprocess.run(["git", *args], capture_output=True, text=True).stdout


def planning() -> list[dict]:
    """New-format planning.txt files on main and claude/* branches, one per topic."""
    found: dict[str, dict] = {}
    refs = ["origin/main"] + [r.strip() for r in git("branch", "-r").splitlines()
                              if r.strip().startswith("origin/claude/")]
    for ref in refs:
        for path in git("ls-tree", "-r", "--name-only", ref, "stories").splitlines():
            if not path.endswith("/planning.txt"):
                continue
            text = git("show", f"{ref}:{path}")
            m = re.search(r"^onderwerp\s+(.+)$", text, re.M)
            if not m:
                continue  # old free-form file; YouTube itself is the source for those
            slots = {k: v.strip() for k, v in re.findall(
                r"^(lang|yt-short|short\d+)\s+(\d{4}-\d\d-\d\d \d\d:\d\d)", text, re.M)}
            links = re.findall(r"https://youtu\.be/[\w-]+", text)
            entry = {"onderwerp": m.group(1).strip(), "map": path.split("/")[1],
                     "slots": slots, "links": links, "branch": ref.removeprefix("origin/"),
                     "kosten": "Kosten" in text}
            old = found.get(entry["onderwerp"])
            if not old or (ref == "origin/main") or len(links) > len(old["links"]):
                found[entry["onderwerp"]] = entry
    return sorted(found.values(), key=lambda e: e["slots"].get("lang", ""))


def main() -> None:
    token = access_token()
    today = dt.datetime.now(NL).date()
    end = today - dt.timedelta(days=1)
    start = end - dt.timedelta(days=27)
    prev_end, prev_start = start - dt.timedelta(days=1), start - dt.timedelta(days=28)

    ch = call("GET", "channels", token, params={"part": "snippet,statistics,contentDetails",
                                                "mine": "true"})["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in call(
        "GET", "playlistItems", token,
        params={"part": "contentDetails", "playlistId": uploads, "maxResults": 50})["items"]]
    videos = call("GET", "videos", token, params={
        "part": "snippet,status,statistics,contentDetails", "id": ",".join(ids)})["items"]
    by_id = {v["id"]: v for v in videos}

    schedule = []
    for v in videos:
        st, sn = v["status"], v["snippet"]
        short = seconds(v["contentDetails"]["duration"]) <= 180
        when = st.get("publishAt") if st["privacyStatus"] != "public" else sn["publishedAt"]
        schedule.append({"id": v["id"], "title": sn["title"], "short": short,
                         "status": "gepland" if st.get("publishAt") and st["privacyStatus"] != "public"
                         else st["privacyStatus"], "when": nl_time(when) if when else "",
                         "views": int(v["statistics"].get("viewCount", 0))})
    schedule.sort(key=lambda s: s["when"])

    top = report(token, start, end, dimensions="video", sort="-views", maxResults=10,
                 metrics="views,estimatedMinutesWatched,averageViewPercentage,subscribersGained")
    for row in top:
        v = by_id.get(row["video"])
        row["title"] = v["snippet"]["title"] if v else row["video"]

    playlists = call("GET", "playlists", token, params={
        "part": "snippet,contentDetails", "mine": "true", "maxResults": 50})["items"]

    year = report(token, end - dt.timedelta(days=364), end, dimensions="creatorContentType",
                  metrics="estimatedMinutesWatched")
    long_minutes = sum(r["estimatedMinutesWatched"] for r in year
                       if r["creatorContentType"] != "shorts")

    out = {
        "watch_hours_12m": round(long_minutes / 60, 1),  # Partner Programme: Shorts don't count
        "updated": dt.datetime.now(NL).strftime("%Y-%m-%d %H:%M"),
        "channel": {"title": ch["snippet"]["title"], "handle": ch["snippet"].get("customUrl"),
                    **{k: int(v) for k, v in ch["statistics"].items() if isinstance(v, str) and v.isdigit()}},
        "period": {"start": start.isoformat(), "end": end.isoformat(),
                   "now": totals(token, start, end),
                   "before": totals(token, prev_start, prev_end)},
        "daily": report(token, start, end, dimensions="day", sort="day",
                        metrics="views,estimatedMinutesWatched,subscribersGained"),
        "top": top,
        "traffic": report(token, start, end, dimensions="insightTrafficSourceType",
                          sort="-views", metrics="views,estimatedMinutesWatched"),
        "youtube_schedule": schedule,
        "planning": planning(),
        "playlists": [{"title": p["snippet"]["title"],
                       "count": p["contentDetails"]["itemCount"]} for p in playlists],
    }
    print(json.dumps(out, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
