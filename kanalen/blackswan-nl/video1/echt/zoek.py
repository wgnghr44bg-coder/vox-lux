import json, sys, re, urllib.parse
from wm import get
API = "https://commons.wikimedia.org/w/api.php?"
uit = {}
for q in sys.argv[1:]:
    p = {"action": "query", "format": "json", "generator": "search", "gsrnamespace": 6, "gsrsearch": q, "gsrlimit": 12,
         "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1920}
    r = get(API + urllib.parse.urlencode(p))
    rows = []
    for pg in (r.get("query", {}).get("pages", {}) or {}).values():
        ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
        lic = em.get("LicenseShortName", {}).get("value", "")
        art = re.sub("<[^>]+>", "", em.get("Artist", {}).get("value", ""))[:60]
        rows.append({"titel": pg["title"], "w": ii["width"], "h": ii["height"], "lic": lic, "artist": art.strip(),
                     "url": ii.get("thumburl") or ii["url"], "page": ii["descriptionurl"]})
        print(f"{q[:18]:18s} | {ii['width']}x{ii['height']} | {lic[:14]:14s} | {pg['title'][5:80]}")
    uit[q] = rows
json.dump(uit, open("zoek-%s.json" % re.sub(r'\W+', '_', sys.argv[1])[:20], "w"), indent=1)
