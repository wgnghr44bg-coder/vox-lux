import json, re, urllib.parse
from wm import get
API = "https://commons.wikimedia.org/w/api.php?"
L = {"dario-a":"Dario Amodei at TechCrunch Disrupt 2023 01.jpg","dario-b":"Dario Amodei at TechCrunch Disrupt 2023 03.jpg",
"dario-c":"Dario Amodei at TechCrunch Disrupt 2023 05.jpg","dario-d":"Dario Amodei at TechCrunch Disrupt 2023 07.jpg",
"dario-e":"Dario Amodei at TechCrunch Disrupt 2023 04.jpg","dario-f":"Dario Amodei at TechCrunch Disrupt 2023 06.jpg","dario-g":"Dario Amodei at TechCrunch Disrupt 2023 08.jpg",
"logo":"Anthropic Logo 2.webp","nasdaq-a":"NASDAQ Market Site 201506.jpg","nasdaq-b":"Nasdaq Tower May 2026.jpg",
"nasdaq-c":"Nasdaq MarketSite (51494550508).jpg","nasdaq-bel":"Times Square Nasdaq Closing Bell Ceremony 2013 Berenberg.JPG",
"starship":"SpaceX Starship before IFT-5.jpg","pentagon":"Aerial Closeup of the Pentagon, May 11, 2021.jpg",
"trump":"Official Presidential Portrait of President Donald J. Trump (2025).jpg",
"prettyman":"Washington D.C. Federal Courthouse - E. Barrett Prettyman (54271895303).jpg",
"burton":"Phillip Burton Federal Building & United States Courthouse.jpg","supreme":"Exterior of Supreme Court Building 20240601.jpg",
"amazon":"Amazon Spheres 00.jpg","google":"Googleplex HQ (cropped).jpg","code":"Code on computer monitor (Unsplash).jpg",
"boeken":"Library Books Bookshelves (Unsplash).jpg","sf":"San Francisco skyline from Marin Headlands.jpg",
"sf-b":"San Francisco Financial District at dusk (8542633876).jpg","dc-us":"Data center infrastructure in the United States.jpg",
"dc-baltic":"BalticServers data center.jpg"}
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
