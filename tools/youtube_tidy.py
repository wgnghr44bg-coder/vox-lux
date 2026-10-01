#!/usr/bin/env python3
"""Tidy up the channel: playlists, titles, category, tags and language.

Needs a refresh token with the https://www.googleapis.com/auth/youtube scope
(youtube.upload alone cannot edit videos or create playlists).

Usage:
    python3 tools/youtube_tidy.py            # dry run: only shows what would change
    python3 tools/youtube_tidy.py --apply    # make the changes

Safe to run more than once: existing playlists (same title) and videos already
in a playlist are skipped, and videos already up to date are left alone.
"""

from __future__ import annotations

import argparse
import sys

import requests

from youtube_upload import access_token

API = "https://www.googleapis.com/youtube/v3/"
EDUCATION = "27"
LANGUAGE = "en"

SLEEP_TAGS = ["sleep documentary", "history for sleep", "sleep history", "bedtime story",
              "relaxing history", "documentary for sleep", "calm narration", "sleep archives"]
SHORT_TAGS = ["history", "dark history", "history facts", "did you know", "mystery",
              "shorts", "sleep archives"]

# Older uploads: new title (None = keep) and extra topic tags.
VIDEOS = {
    "QrAyJC0RrHY": ("Life Before Fire: How Early Humans Survived the Night | History for Sleep",
                    SLEEP_TAGS + ["prehistory", "early humans", "life before fire", "stone age"]),
    "Wod4U-a2YM8": ("Chernobyl: The Night of April 26, 1986 | History for Sleep",
                    SLEEP_TAGS + ["chernobyl", "chernobyl 1986", "pripyat", "soviet history"]),
    "CZaQsA93coI": ("The Dutch Hunger Winter of 1944–1945 | History for Sleep",
                    SLEEP_TAGS + ["dutch hunger winter", "hongerwinter", "ww2 netherlands",
                                  "world war 2"]),
    "JG5ad1Y3K44": ("The Darkest Punishments of Medieval Europe | Dark History for Sleep",
                    SLEEP_TAGS + ["dark history", "medieval punishments", "medieval europe",
                                  "middle ages"]),
    "cETEZwKusWw": ("The Man in the Iron Mask: Who Was He? 🕯️",
                    SHORT_TAGS + ["the man in the iron mask", "iron mask", "louis xiv", "bastille"]),
    "1O5hspxIYoI": ("The Man With No Identity: The Somerton Man Mystery 🕯️",
                    SHORT_TAGS + ["somerton man", "tamam shud", "unsolved mystery", "australia"]),
    "OzYxgUQ7mQE": ("The Ship That Returned Without Its Crew: The Mary Celeste",
                    SHORT_TAGS + ["mary celeste", "ghost ship", "unsolved mystery"]),
    "3shZWi_N7fw": (None, SHORT_TAGS + ["guy fawkes", "tower of london", "gunpowder plot"]),
    "AQFodxgd2K0": (None, SHORT_TAGS + ["colosseum", "ancient rome", "gladiators"]),
    "phK3ZXsEXXY": (None, SHORT_TAGS + ["dancing plague", "dancing plague of 1518",
                                        "strasbourg"]),
    "Ges1LKW9AR8": (None, None),
}
# Uploaded before tools/youtube_upload.py set a language: only the language is fixed.
NO_LANGUAGE = ["2CY3BfnZ1rY", "VuTN5ReMzLk", "6FIgJoXzr3Q", "0iOdbDQx7y4", "1HghOMqmILo",
               "7CoI1PwR-0E", "g9IrntwGDuw"]

PLAYLISTS = [
    ("History for Sleep – Full Documentaries",
     "Long, calm history documentaries to fall asleep to. Let them play one after another.",
     ["2CY3BfnZ1rY", "VuTN5ReMzLk", "6FIgJoXzr3Q", "QrAyJC0RrHY", "JG5ad1Y3K44",
      "CZaQsA93coI", "Wod4U-a2YM8"]),
    ("Titanic", "The Titanic for sleep: the full documentary and short stories from 1912.",
     ["2CY3BfnZ1rY", "1HghOMqmILo", "0iOdbDQx7y4"]),
    ("Pompeii", "Pompeii before Vesuvius: the full sleep documentary and short stories.",
     ["VuTN5ReMzLk", "Ges1LKW9AR8"]),
    ("San Francisco 1906", "Old San Francisco and the 1906 earthquake: the full sleep "
     "documentary and short stories.", ["6FIgJoXzr3Q", "g9IrntwGDuw", "7CoI1PwR-0E"]),
    ("Dark History & Mysteries", "Unsolved mysteries and the darker side of history.",
     ["JG5ad1Y3K44", "1O5hspxIYoI", "cETEZwKusWw", "OzYxgUQ7mQE", "3shZWi_N7fw",
      "AQFodxgd2K0", "phK3ZXsEXXY"]),
]


def call(method: str, path: str, token: str, **kw) -> dict:
    res = requests.request(method, API + path, headers={"Authorization": f"Bearer {token}"},
                           timeout=60, **kw)
    if not res.ok:
        sys.exit(f"{method} {path} failed ({res.status_code}): {res.text[:300]}")
    return res.json() if res.content else {}


def tidy_videos(token: str, apply: bool) -> None:
    ids = list(VIDEOS) + NO_LANGUAGE
    items = call("GET", "videos", token, params={"part": "snippet", "id": ",".join(ids)})["items"]
    for v in items:
        s = v["snippet"]
        title, tags = VIDEOS.get(v["id"], (None, None))
        new = {"title": title or s["title"], "description": s["description"],
               "tags": tags or s.get("tags", []), "categoryId": EDUCATION,
               "defaultLanguage": LANGUAGE, "defaultAudioLanguage": LANGUAGE}
        # YouTube stores tags sorted, so compare them regardless of order.
        changes = [k for k in new if (sorted(new[k]) != sorted(s.get(k, [])) if k == "tags"
                                      else new[k] != s.get(k))]
        if not changes:
            print(f"ok       {s['title']}")
            continue
        print(f"update   {s['title']}\n         -> {', '.join(changes)}"
              + (f": {new['title']}" if "title" in changes else ""))
        if apply:
            call("PUT", "videos", token, params={"part": "snippet"},
                 json={"id": v["id"], "snippet": new})


def tidy_playlists(token: str, apply: bool) -> None:
    mine = call("GET", "playlists", token,
                params={"part": "snippet", "mine": "true", "maxResults": 50})["items"]
    existing = {p["snippet"]["title"]: p["id"] for p in mine}
    for title, description, videos in PLAYLISTS:
        pid = existing.get(title)
        have: set[str] = set()
        if pid:
            have = {i["contentDetails"]["videoId"] for i in call(
                "GET", "playlistItems", token,
                params={"part": "contentDetails", "playlistId": pid, "maxResults": 50})["items"]}
        todo = [v for v in videos if v not in have]
        print(f"{'playlist' if pid else 'new list'} {title}: {len(todo)} video(s) to add")
        if not apply or not todo:
            continue
        if not pid:
            pid = call("POST", "playlists", token, params={"part": "snippet,status"}, json={
                "snippet": {"title": title, "description": description,
                            "defaultLanguage": LANGUAGE},
                "status": {"privacyStatus": "public"}})["id"]
        for vid in todo:
            call("POST", "playlistItems", token, params={"part": "snippet"}, json={
                "snippet": {"playlistId": pid,
                            "resourceId": {"kind": "youtube#video", "videoId": vid}}})


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--apply", action="store_true", help="make the changes (default: dry run)")
    args = parser.parse_args()
    token = access_token()
    tidy_videos(token, args.apply)
    tidy_playlists(token, args.apply)
    print("Done." if args.apply else "Dry run: nothing changed. Use --apply to make the changes.")


if __name__ == "__main__":
    main()
