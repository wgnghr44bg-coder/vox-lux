"""Hoe uniek is een incident op YouTube? Zoekt per onderwerp de 25 meest bekeken video's en telt views/kanalen.

  python kanalen/bodycam/uniek_check.py "Marvin Morales fentanyl bodycam" "Trader Joe's Silver Lake standoff"

Kost YouTube-quotum (gratis): 100 per onderwerp + 1. Gebruikt het token van Sleep Archives alleen om te ZOEKEN (lezen).
Uitkomst: weinig video's / weinig views = kans om uniek te zijn; veel grote kanalen = al vaak gedaan.
"""
import json, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools"))
from youtube_upload import access_token

API = "https://www.googleapis.com/youtube/v3/"


def get(pad, token, **p):
    req = urllib.request.Request(API + pad + "?" + urllib.parse.urlencode(p), headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def check(onderwerp, token):
    zoek = get("search", token, part="snippet", q=onderwerp, type="video", maxResults=25, order="viewCount")
    ids = [i["id"]["videoId"] for i in zoek.get("items", [])]
    if not ids:
        return {"onderwerp": onderwerp, "video's": 0, "max_views": 0, "top": []}
    st = get("videos", token, part="statistics,snippet", id=",".join(ids))
    rij = sorted(({"views": int(v["statistics"].get("viewCount", 0)), "kanaal": v["snippet"]["channelTitle"],
                   "titel": v["snippet"]["title"]} for v in st["items"]), key=lambda x: -x["views"])
    relevant = [r for r in rij if any(w.lower() in r["titel"].lower() for w in onderwerp.split()[:2])]
    return {"onderwerp": onderwerp, "totaal_gevonden": zoek.get("pageInfo", {}).get("totalResults"),
            "relevant": len(relevant), "views_relevant": sum(r["views"] for r in relevant),
            "max_views": relevant[0]["views"] if relevant else 0, "top": relevant[:3]}


if __name__ == "__main__":
    tok = access_token()
    for o in sys.argv[1:]:
        r = check(o, tok)
        print(f"\n## {o}\n  relevante video's in top 25: {r.get('relevant')}  samen {r.get('views_relevant', 0):,} views")
        for t in r["top"]:
            print(f"   {t['views']:>11,}  {t['kanaal'][:25]:25}  {t['titel'][:80]}")
