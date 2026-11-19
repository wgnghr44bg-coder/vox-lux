import json, re, urllib.parse
from wm import get
API = "https://commons.wikimedia.org/w/api.php?"
L = {"kantoor-a":"Secretary of State Peter Kyle visits Anthropic in San Francisco. (54098999333).jpg",
"kantoor-b":"Secretary of State Peter Kyle visits Anthropic in San Francisco. (54099081629).jpg",
"jack-clark":"Jack Clark, co-founder of Anthropic, giving a talk on AI at the Schwarzman Centre in Oxford.jpg",
"claude-site":"Claude AI website screenshot.webp","dario-japan":"Sanae Takaichi and Dario Amodei in 2025 (1).jpg"}
rows = []
for k, f in L.items():
    p = {"action":"query","format":"json","titles":"File:"+f,"prop":"imageinfo","iiprop":"url|extmetadata","iiurlwidth":2400}
    pg = list(get(API+urllib.parse.urlencode(p))["query"]["pages"].values())[0]
    ii = pg["imageinfo"][0]; em = ii.get("extmetadata", {})
    art = re.sub(r"<[^>]+>", "", em.get("Artist",{}).get("value","")).strip()[:60]; lic = em.get("LicenseShortName",{}).get("value","")
    ext = ".png" if f.endswith((".webp",".png")) else ".jpg"
    open(k+ext, "wb").write(get(ii.get("thumburl") or ii["url"], raw=True))
    rows.append("\t".join([k, "File:"+f, art, lic, ii["descriptionurl"]])); print(k, lic, art)
open("bronnen.tsv","a",encoding="utf-8").write("\n".join(rows)+"\n")
