#!/usr/bin/env python3
"""Put a new sleep documentary and its Shorts in the channel's playlists.

The long video goes in "History for Sleep – Full Documentaries"; the long video and
its Shorts together go in a playlist of their own (created when missing). With
--mystery the Shorts also go in "Dark History & Mysteries".

Usage:
    python3 tools/youtube_playlist.py --playlist "Tunguska 1908" \
        --description "The Tunguska Event for sleep: the full documentary and short stories." \
        LONG_ID SHORT_ID SHORT_ID ...

Safe to run more than once: existing playlists (same title) and videos already in a
playlist are skipped. Scheduled (still private) videos can be added; viewers see them
once they go public.
"""

from __future__ import annotations

import argparse

from youtube_tidy import LANGUAGE, call
from youtube_upload import access_token

FULL = ("History for Sleep – Full Documentaries",
        "Long, calm history documentaries to fall asleep to. Let them play one after another.")
MYSTERY = ("Dark History & Mysteries", "Unsolved mysteries and the darker side of history.")


def add(token: str, existing: dict[str, str], title: str, description: str,
        videos: list[str]) -> None:
    pid = existing.get(title)
    have: set[str] = set()
    if pid:
        have = {i["contentDetails"]["videoId"] for i in call(
            "GET", "playlistItems", token,
            params={"part": "contentDetails", "playlistId": pid, "maxResults": 50})["items"]}
    else:
        pid = call("POST", "playlists", token, params={"part": "snippet,status"}, json={
            "snippet": {"title": title, "description": description, "defaultLanguage": LANGUAGE},
            "status": {"privacyStatus": "public"}})["id"]
        existing[title] = pid
    todo = [v for v in videos if v not in have]
    for vid in todo:
        call("POST", "playlistItems", token, params={"part": "snippet"}, json={
            "snippet": {"playlistId": pid,
                        "resourceId": {"kind": "youtube#video", "videoId": vid}}})
    print(f"{title}: {len(todo)} added, {len(videos) - len(todo)} already there")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("long", help="video id of the long documentary")
    parser.add_argument("shorts", nargs="*", help="video ids of its Shorts")
    parser.add_argument("--playlist", required=True,
                        help="title of the topic playlist, e.g. 'Tunguska 1908'")
    parser.add_argument("--description", default="",
                        help="topic playlist description (only used when it is created)")
    parser.add_argument("--mystery", action="store_true",
                        help="also put the Shorts in 'Dark History & Mysteries'")
    args = parser.parse_args()
    token = access_token()
    mine = call("GET", "playlists", token,
                params={"part": "snippet", "mine": "true", "maxResults": 50})["items"]
    existing = {p["snippet"]["title"]: p["id"] for p in mine}
    add(token, existing, *FULL, [args.long])
    add(token, existing, args.playlist, args.description
        or f"{args.playlist} for sleep: the full documentary and short stories.",
        [args.long, *args.shorts])
    if args.mystery and args.shorts:
        add(token, existing, *MYSTERY, args.shorts)


if __name__ == "__main__":
    main()
