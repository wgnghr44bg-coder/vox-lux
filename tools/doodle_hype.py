"""Hype-wachter Market Doodle (eigenaar 23 nov 2026: "en of er grote hype is op 1 van de kanalen wil ik dan ook weten").
Elke dag 08:40 (Taakplanner "Market Doodle hype"): zoekt What If-video's van de laatste 2 dagen die heel hard gaan
(views per uur). Bij GROTE hype (>= GRENS views/uur) één seintje per onderwerp: "Grote hype: Market Doodle".
Kost alleen YouTube-quota (zoeken = 100 eenheden per zoekterm). Uitkomst ook in stories/doodle-hype.json.
  python tools/doodle_hype.py [--droog]"""
import datetime as dt, json, os, sys, urllib.parse, urllib.request
from pathlib import Path
HIER = Path(__file__).resolve().parent; STORIES = HIER.parent / "stories"; sys.path.insert(0, str(HIER))
GRENS = 50000                    # views per uur = grote hype (20.000 gaf te veel ruis, 23 nov)
ZOEK = ["what if", "what if you could"]

def token():
    q = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_REFRESH_TOKEN_ALTERAQON"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", q))["access_token"]

def main():
    H = {"Authorization": "Bearer " + token()}
    def g(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/" + p, headers=H)))
    na = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=48)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = set()
    for z in ZOEK:
        r = g("search?" + urllib.parse.urlencode({"part": "id", "q": z, "type": "video", "order": "viewCount", "publishedAfter": na, "maxResults": 25, "relevanceLanguage": "en"}))
        ids |= {i["id"]["videoId"] for i in r.get("items", [])}
    rij = []
    for v in g("videos?part=snippet,statistics&id=" + ",".join(ids)).get("items", []) if ids else []:
        uren = max(1.0, (dt.datetime.now(dt.timezone.utc) - dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 3600)
        rij.append({"titel": v["snippet"]["title"], "kanaal": v["snippet"]["channelTitle"], "per_uur": int(int(v["statistics"].get("viewCount", 0)) / uren)})
    rij.sort(key=lambda x: -x["per_uur"])
    (STORIES / "doodle-hype.json").write_text(json.dumps({"bijgewerkt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "videos": rij[:20]}, indent=1, ensure_ascii=False), encoding="utf-8")
    for x in rij[:10]: print(f'{x["per_uur"]:>8} v/u  {x["titel"][:80]}  [{x["kanaal"]}]')
    groot = [x for x in rij if x["per_uur"] >= GRENS and "what if you" in x["titel"].lower()]   # verhaal-stijl zoals wij
    logp = STORIES / "ROUTINE-LOG.md"; oud = logp.read_text(encoding="utf-8", errors="replace")
    vandaag = dt.date.today().isoformat()
    nieuw = [x for x in groot if f"Doodle-hype: {x['titel']}" not in oud]
    if nieuw and "--droog" not in sys.argv:
        with logp.open("a", encoding="utf-8") as f:
            for x in nieuw[:3]: f.write(f"\n- {vandaag} Doodle-hype: {x['titel']} ({x['per_uur']} views/uur)\n")
        from swan_yt_wacht import seintje
        seintje("Grote hype: Market Doodle", "\n".join(f"{x['titel']} ({x['per_uur']:,} views/uur)" for x in nieuw[:3])
                + "\nEigen What If-versie maken voor Market Doodle?")

if __name__ == "__main__":
    main()
