#!/usr/bin/env python3
"""Thumbnail impressions and click-through rate per video, via the YouTube Reporting API.

The Analytics API does not offer these metrics, the Reporting API does (report type
`channel_reach_basic_a1`). It works with daily bulk reports: once a reporting job exists,
YouTube writes one CSV per day; the first ones appear after 1-2 days. A job changes
nothing on the channel or its videos.

The Reporting API must be enabled once in the Google Cloud project of the token
(console.cloud.google.com > APIs & Services > YouTube Reporting API > Enable).

Usage:
    python3 tools/youtube_reach.py              # create the job if needed, print totals per video
    python3 tools/youtube_reach.py --json       # same, as JSON
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import defaultdict

import requests

from youtube_upload import access_token

API = "https://youtubereporting.googleapis.com/v1/"
REPORT_TYPE = "channel_reach_basic_a1"
JOB_NAME = "Sleep Archives reach"


def get(token: str, path: str, **params) -> dict:
    res = requests.get(API + path, headers={"Authorization": f"Bearer {token}"},
                       params=params, timeout=60)
    res.raise_for_status()
    return res.json()


def job_id(token: str) -> tuple[str, bool]:
    """The existing reach job, or a new one. Returns (id, created_now)."""
    for job in get(token, "jobs").get("jobs", []):
        if job["reportTypeId"] == REPORT_TYPE:
            return job["id"], False
    types = [t["id"] for t in get(token, "reportTypes").get("reportTypes", [])]
    if REPORT_TYPE not in types:
        sys.exit(f"Report type {REPORT_TYPE} not offered. Available: {', '.join(types)}")
    res = requests.post(API + "jobs", headers={"Authorization": f"Bearer {token}"}, timeout=60,
                        json={"reportTypeId": REPORT_TYPE, "name": JOB_NAME})
    res.raise_for_status()
    return res.json()["id"], True


def rows(token: str, job: str) -> list[dict]:
    """All CSV rows of all reports of the job (the newest report per day wins)."""
    reports, page = [], None
    while True:
        body = get(token, f"jobs/{job}/reports", **({"pageToken": page} if page else {}))
        reports += body.get("reports", [])
        page = body.get("nextPageToken")
        if not page:
            break
    newest: dict[str, dict] = {}
    for r in reports:
        day = r["startTime"][:10]
        if day not in newest or r["createTime"] > newest[day]["createTime"]:
            newest[day] = r
    out = []
    for r in newest.values():
        res = requests.get(r["downloadUrl"], headers={"Authorization": f"Bearer {token}"}, timeout=120)
        res.raise_for_status()
        out += list(csv.DictReader(io.StringIO(res.content.decode("utf-8"))))
    return out


def per_video(data: list[dict]) -> list[dict]:
    totals: dict[str, dict] = defaultdict(lambda: {"impressions": 0, "clicks": 0.0, "days": set()})
    for row in data:
        n = int(float(row.get("video_thumbnail_impressions") or 0))
        ctr = float(row.get("video_thumbnail_impressions_ctr") or 0)
        t = totals[row["video_id"]]
        t["impressions"] += n
        t["clicks"] += n * ctr
        t["days"].add(row["date"])
    return sorted(({"video": v, "impressions": t["impressions"],
                    "ctr": round(100 * t["clicks"] / t["impressions"], 1) if t["impressions"] else 0.0,
                    "from": min(t["days"]), "to": max(t["days"])} for v, t in totals.items()),
                  key=lambda x: -x["impressions"])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    token = access_token()
    job, created = job_id(token)
    if created:
        print(f"Reporting job created ({job}). First data in 1-2 days.", file=sys.stderr)
    result = per_video(rows(token, job))
    if args.json:
        print(json.dumps(result, indent=1))
    elif not result:
        print("No reports yet (YouTube needs 1-2 days after the job is created).")
    else:
        for r in result:
            print(f"{r['video']}  {r['impressions']:>7} impressions  {r['ctr']:>5.1f}% CTR  "
                  f"({r['from']} .. {r['to']})")


if __name__ == "__main__":
    main()
