import json, re, urllib.parse
from wm import get
API = "https://commons.wikimedia.org/w/api.php?"
L = {"rockstar-north":"20231022 Rockstar North.jpg","rockstar-north-b":"Studios Rockstar North Édimbourg 1.jpg",
"zelnick":"Strauss Zelnick, 2015 (16339090774).jpg","miami-ocean":"Miami Beach - Ocean Drive (2023).jpg",
"miami-night":"Miami night skyline by Don Ramey Logan.jpg","miami-night-b":"Miami Night Skyline from across the Biscayne Bay-Downtown-March 2011.JPG",
"ps5":"PlayStation 5 and DualSense (2).jpg","dualsense":"Playstation 5 DualSense controller in Midnight Black, 2026-02-07 (front).jpg",
"gamestop":"GameStop Retail Store - Vallejo - California (50906730711).jpg","ebgames":"EB Games Store at Oshawa Centre, October 17 2026 (01).jpg",
"edinburgh":"Dusky Edinburgh skyline - geograph.org.uk - 7674988.jpg","nyc-44":"44th St 6th Av td 26 - 1133 Avenue of the Americas.jpg"}
rows = []
for k, f in L.items():
    p = {"action":"query","format":"json","titles":"File:"+f,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":2400}
    pg = list(get(API+urllib.parse.urlencode(p))["query"]["pages"].values())[0]
    ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
    art = re.sub(r"<[^>]+>", "", em.get("Artist",{}).get("value","")).strip()[:60]; lic = em.get("LicenseShortName",{}).get("value","")
    ext = ".png" if f.endswith((".webp",".png")) else ".jpg"
    open(k+ext, "wb").write(get(ii.get("thumburl") or ii["url"], raw=True))
    rows.append("\t".join([k, "File:"+f, art, lic, ii["descriptionurl"]])); print(k, lic, art)
open("bronnen.tsv","w",encoding="utf-8").write("\n".join(rows)+"\n")
