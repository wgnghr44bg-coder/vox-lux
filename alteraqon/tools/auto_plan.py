"""Alteraqon nachtrun: hoeveel video's moeten er vannacht gemaakt worden?

Gebruik:  python alteraqon/tools/auto_plan.py [kanaalmap=alteraqon | absoluut pad naar andere repo]   -> {"shorts": 3, "long": 1, "shorts_ingepland": 2, "long_ingepland": 0}
Kijkt naar "publish_at" in <kanaalmap>/*/upload.json (lange video = map met thumbnail.json) en vult de wachtrij aan:
- channel.json in de kanaalmap: "shorts_per_night" (standaard 3) en "long" (false = geen lange video's).
- Shorts: tot er minstens SHORT_BUFFER Shorts in de toekomst ingepland staan, max 3 per nacht.
- Lange video: 1 als er geen lange video meer in de toekomst ingepland staat.
"""
import datetime as dt, glob, json, os, sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(REPO, sys.argv[1] if len(sys.argv) > 1 else "alteraqon")   # absoluut pad mag ook (andere repo)
_ch = os.path.join(ROOT, "channel.json")
CH = json.load(open(_ch, encoding="utf-8")) if os.path.exists(_ch) else {}
SHORT_BUFFER = MAX_SHORTS = int(CH.get("shorts_per_night", 3))   # Alteraqon: 3 = 1 dag vooruit bij 3 Shorts per dag

now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
fut = {"short": 0, "long": 0}
for p in glob.glob(os.path.join(ROOT, "*", "upload.json")):
    try:
        pa = json.load(open(p, encoding="utf-8")).get("publish_at")
    except Exception:
        continue
    if pa and pa > now:
        fut["long" if os.path.exists(os.path.join(os.path.dirname(p), "thumbnail.json")) else "short"] += 1

print(json.dumps({"shorts": max(0, min(MAX_SHORTS, SHORT_BUFFER - fut["short"])),
                  "long": 0 if fut["long"] or not CH.get("long", True) else 1,
                  "shorts_ingepland": fut["short"], "long_ingepland": fut["long"]}))
