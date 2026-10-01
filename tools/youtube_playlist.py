#!/usr/bin/env python3
"""Put a new sleep documentary and its Shorts in the channel's playlists.

The channel keeps a fixed set of playlists (no playlist per topic, that gets messy):
the long video goes in "History for Sleep – Full Documentaries", and the long video
and its Shorts together go in the playlist for their kind of topic (--soort).
A kind's playlist is created the first time it is needed.

Usage:
    python3 tools/youtube_playlist.py --soort ramp LONG_ID SHORT_ID SHORT_ID ...

Kinds (--soort):
    ramp          Disasters & Catastrophes   (Titanic, Chernobyl, Tunguska, ...)
    oudheid       Ancient World              (Pompeii, Rome, Egypt, prehistory, ...)
    middeleeuwen  Medieval Life              (Black Death, witch trials, ...)
    mysterie      Dark History & Mysteries   (Somerton Man, Dyatlov Pass, ...)
    oorlog        War & Survival             (Hunger Winter, Leningrad, D-Day, ...)
    verlaten      Lost & Abandoned Places    (Hashima, Centralia, ghost towns, ...)

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
KINDS = {
    "ramp": ("Disasters & Catastrophes",
             "Great disasters of history, told slowly and calmly for sleep: the full "
             "documentaries and short stories."),
    "oudheid": ("Ancient World",
                "Life in the ancient world and before: calm history for sleep, full "
                "documentaries and short stories."),
    "middeleeuwen": ("Medieval Life",
                     "Daily life and dark days in the Middle Ages: calm history for sleep, "
                     "full documentaries and short stories."),
    "mysterie": ("Dark History & Mysteries", "Unsolved mysteries and the darker side of history."),
    "oorlog": ("War & Survival",
               "How ordinary people lived through war: calm history for sleep, full "
               "documentaries and short stories."),
    "verlaten": ("Lost & Abandoned Places",
                 "Abandoned towns, lost cities and forgotten places: calm history for sleep."),
}


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
    parser.add_argument("long", nargs="?", help="video id of the long documentary ('-' for none)")
    parser.add_argument("shorts", nargs="*", help="video ids of its Shorts")
    parser.add_argument("--soort", required=True, choices=KINDS, help="kind of topic")
    args = parser.parse_args()
    token = access_token()
    mine = call("GET", "playlists", token,
                params={"part": "snippet", "mine": "true", "maxResults": 50})["items"]
    existing = {p["snippet"]["title"]: p["id"] for p in mine}
    long = [args.long] if args.long and args.long != "-" else []
    if long:
        add(token, existing, *FULL, long)
    add(token, existing, *KINDS[args.soort], long + args.shorts)


if __name__ == "__main__":
    main()
