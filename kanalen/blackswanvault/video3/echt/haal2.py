import json, re, urllib.parse
from wm import get
API = "https://commons.wikimedia.org/w/api.php?"
L = {"dundee":"Dundee Waterfront Redevelopment Jun 2017 a.jpg","zynga":"Zynga building.JPG","ps2":"Sony-PlayStation-2-70001-Console-FL.jpg",
"neon":"Boulevard Hotel (Neon sign), Miami Beach.jpg","lifeguard":"Lifeguard stand, Miami Beach.jpg","artdeco":"Miami Beach - Art Deco Building.jpg"}
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
