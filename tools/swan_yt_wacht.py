"""YouTube-wachter voor BlackswanVault (eigenaar 21 nov 2026: "heb je ook een wachter die kijkt naar YouTube en nieuws
wat nu echt heel groot is").

Zoekt op YouTube welke geld-/bedrijfs-/beursvideo's van de laatste 48 uur nu het snelst views krijgen (views per uur),
haalt de onderwerpen eruit en legt ze naast de nieuwswachter (stories/nieuws.json). Een onderwerp dat op YouTube EN in
het nieuws groot is, heet STERK. Ook: hebben wij er al een video over (kanalen/PLANNING-KANALEN.json)?
Alleen lezen, kost geen geld (alleen YouTube API-quota: ± 100 per zoekterm, ± 1.000 per keer).

  YT_REFRESH_TOKEN="$YT_WHATIF_REFRESH_TOKEN" python tools/swan_yt_wacht.py          # bijwerken
  python tools/swan_yt_wacht.py --uren 72 --top 25

Uitkomst: stories/yt-hype-swan.json en een seintje in stories/ROUTINE-LOG.md (één keer per onderwerp per dag).
"""
import argparse, datetime as dt, json, os, re, sys, time
from collections import defaultdict
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
ROOT = HIER.parent
STORIES = ROOT / "stories"
UIT = STORIES / "yt-hype-swan.json"
LOG = STORIES / "ROUTINE-LOG.md"
API = "https://www.googleapis.com/youtube/v3/"

ZOEK = ["stock market news", "stock market crash", "economy news", "business news", "nvidia stock",
        "bitcoin crash", "tech stocks", "IPO", "layoffs", "recession", "federal reserve interest rates",
        "billionaire"]
# geen nieuwszenders als hype-bron weglaten; wel meetellen, maar kanaal wordt getoond
STOP = set("""the a an and or of to in on for is are was were be been it its this that these those with as at by from
how why what who when will can could would should not no yes you your we our they their he his she her i my me just
now new news live today stock stocks market markets price prices video full update breaking 2025 2026 vs after before
about into over under more most less than then here there all every one two three big huge biggest major top is
says said get got has have had do does did up down out off amid week day year years month time watch must shorts
dont don't isn't it's what's here's crash crashing falling fell drop drops dropped plunge plunges surge soars rally
billion trillion million percent next coming really real truth explained everything nobody someone happening happen
investors investor investing invest money economy economic business sell selling sold buy buying dump loss lose losing
target warning collapse trillions laid off fears fear wrong ever worse bad good finally officially shocking breaking
""".split())


def token():
    if os.environ.get("YT_WHATIF_REFRESH_TOKEN") and not os.environ.get("YT_KANAAL"):
        os.environ["YT_REFRESH_TOKEN"] = os.environ["YT_WHATIF_REFRESH_TOKEN"]
    from youtube_upload import access_token
    return access_token()


def get(tok, pad, **p):
    r = requests.get(API + pad, headers={"Authorization": f"Bearer {tok}"}, params=p, timeout=60)
    r.raise_for_status()
    return r.json()


def woorden(t):
    t = re.sub(r"[^a-z0-9$&' ]", " ", t.lower())
    return [w for w in t.split() if len(w) > 2 and w not in STOP and not w.isdigit()]


def onze_titels():
    try:
        d = json.loads((ROOT / "kanalen/PLANNING-KANALEN.json").read_text(encoding="utf-8"))
        return [(i["datum"], i["titel"]) for i in d["items"] if i.get("kanaal") == "BlackswanVault"]
    except Exception:
        return []


def nieuws_onderwerpen():
    try:
        d = json.loads((STORIES / "nieuws.json").read_text(encoding="utf-8"))
        return {o["onderwerp"].lower(): o for o in d.get("onderwerpen", [])}
    except Exception:
        return {}


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--uren", type=int, default=48)
    ap.add_argument("--top", type=int, default=20)
    a = ap.parse_args()
    nu = dt.datetime.now(dt.timezone.utc)
    sinds = (nu - dt.timedelta(hours=a.uren)).strftime("%Y-%m-%dT%H:%M:%SZ")
    tok = token()

    ids = set()
    for q in ZOEK:
        time.sleep(2)
        try:
            r = get(tok, "search", part="id", q=q, type="video", order="viewCount", publishedAfter=sinds,
                    regionCode="US", relevanceLanguage="en", maxResults=25)
            ids |= {i["id"]["videoId"] for i in r.get("items", [])}
        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            print("zoeken mislukt:", q, code)
            if code == 403:  # quota op
                break
            if code == 429:
                time.sleep(20)
                try:
                    r = get(tok, "search", part="id", q=q, type="video", order="viewCount", publishedAfter=sinds,
                            regionCode="US", relevanceLanguage="en", maxResults=25)
                    ids |= {i["id"]["videoId"] for i in r.get("items", [])}
                except requests.HTTPError:
                    pass
    vids = []
    lijst = list(ids)
    for k in range(0, len(lijst), 50):
        r = get(tok, "videos", part="snippet,statistics,contentDetails", id=",".join(lijst[k:k + 50]))
        for v in r.get("items", []):
            s = v["snippet"]
            if s.get("channelTitle", "").lower() == "blackswanvault":
                continue
            uren = max(1.0, (nu - dt.datetime.fromisoformat(s["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 3600)
            views = int(v["statistics"].get("viewCount", 0))
            dur = v["contentDetails"].get("duration", "")
            vids.append({"id": v["id"], "titel": s["title"], "kanaal": s["channelTitle"], "views": views,
                         "per_uur": round(views / uren), "uren_oud": round(uren),
                         "short": bool(re.fullmatch(r"PT(\d+S|[0-2]M(\d+S)?)", dur))})
    vids.sort(key=lambda x: -x["per_uur"])

    # onderwerpen: woorden (en tweetallen) gewogen met views per uur, minstens 2 kanalen
    gewicht, kanalen, voorbeeld = defaultdict(float), defaultdict(set), defaultdict(list)
    for v in vids[:150]:
        w = woorden(v["titel"])
        termen = set(w) | {f"{x} {y}" for x, y in zip(w, w[1:])}
        for t in termen:
            gewicht[t] += v["per_uur"]
            kanalen[t].add(v["kanaal"])
            if len(voorbeeld[t]) < 3:
                voorbeeld[t].append(f'{v["titel"]} ({v["kanaal"]}, {v["views"]:,} views in {v["uren_oud"]} u)')
    nieuws = nieuws_onderwerpen()
    ons = onze_titels()
    onderwerpen = []
    for t, g in sorted(gewicht.items(), key=lambda x: -x[1]):
        if len(kanalen[t]) < 2:
            continue
        # tweetal wint van losse woorden die erin zitten
        if any(t in o["onderwerp"].split() for o in onderwerpen):
            continue
        in_nieuws = [n for n in nieuws if n in t or t in n]
        gedaan = [f"{d}: {ti}" for d, ti in ons if all(x in ti.lower() for x in t.split())]
        onderwerpen.append({"onderwerp": t, "views_per_uur": round(g), "kanalen": len(kanalen[t]),
                            "in_nieuws": bool(in_nieuws), "sterk": bool(in_nieuws) and len(kanalen[t]) >= 3,
                            "al_gedaan": gedaan, "voorbeelden": voorbeeld[t]})
        if len(onderwerpen) >= a.top:
            break

    uit = {"bijgewerkt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "uren": a.uren, "aantal_videos": len(vids),
           "onderwerpen": onderwerpen, "top_videos": vids[:25]}
    UIT.write_text(json.dumps(uit, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"swan-yt-wacht {uit['bijgewerkt']}: {len(vids)} video's van de laatste {a.uren} uur")
    for o in onderwerpen:
        merk = "STERK" if o["sterk"] else ("nieuws" if o["in_nieuws"] else "")
        gd = " | AL GEDAAN: " + o["al_gedaan"][0] if o["al_gedaan"] else ""
        print(f'{o["views_per_uur"]:>8} v/u {o["kanalen"]:>2} kan. {merk:6} {o["onderwerp"]}{gd}')
    print("\nSnelste video's:")
    for v in vids[:12]:
        print(f'{v["per_uur"]:>8} v/u  {v["titel"][:80]}  [{v["kanaal"]}]')

    # seintje, één keer per onderwerp per dag
    vandaag = dt.date.today().isoformat()
    try:
        oud = LOG.read_text(encoding="utf-8")
    except Exception:
        oud = ""
    nieuwe = [o for o in onderwerpen if o["sterk"] and not o["al_gedaan"]
              and f"{vandaag} YouTube-hype: {o['onderwerp']}" not in oud]
    if nieuwe:
        with LOG.open("a", encoding="utf-8") as f:
            for o in nieuwe:
                f.write(f"\n- {vandaag} YouTube-hype: {o['onderwerp']} (STERK: YouTube + nieuws, "
                        f"{o['kanalen']} kanalen, {o['views_per_uur']} views/uur). BlackswanVault: video waard?\n")


if __name__ == "__main__":
    main()
