"""Niche-scanner (22 nov 2026, eigenaar: "echt scannen welke niche nu hot is").
Per onderwerp: video's van de laatste 30 dagen (Engels, VS), gesorteerd op weergaven. Meet:
  vraag     = mediaan weergaven per dag van de top-50 lange video's (>= 4 min)
  aanbod    = hoeveel video's YouTube ongeveer vindt in 30 dagen (ruwe schatting)
  kleine    = aantal lange video's van kanalen < 100k abonnees met meer weergaven dan abonnees (kleine kanalen die winnen)
  score     = vraag x (1 + kleine) / wortel(aanbod)   -> hoog = veel kijkers, weinig makers, nieuwkomers maken kans
Kosten: ±102 punten YouTube-quota per onderwerp (dagquotum 10.000, gedeeld met uploads). Standaard 25 onderwerpen ≈ 2.600.
Gebruik: python tools/niche_scan.py [--dagen 30] [--uit kanalen/NICHE-SCAN.md] [onderwerpen.txt]"""
import json, math, os, re, statistics, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ONDERWERPEN = {
    "Waar gaat je geld heen (bonnetje)": "where does your money go when you buy",
    "Hoe verdient bedrijf X geld": "how does company make money explained",
    "Kwartaalcijfers uitgelegd": "earnings explained stock",
    "Rente / Fed uitgelegd": "fed interest rate cut explained",
    "Inflatie uitgelegd": "inflation explained why prices",
    "Beurscrash / bubbel": "stock market crash bubble explained",
    "AI-bubbel": "AI bubble stocks explained",
    "Beursgangen (IPO)": "IPO explained company going public",
    "Bedrijf in problemen": "why company is failing collapse",
    "Bedrijfsgeschiedenis": "rise and fall of company documentary",
    "Miljardairs / rijkste mensen": "billionaire net worth how he made money",
    "Huizenmarkt": "housing market crash explained",
    "Crypto / bitcoin nieuws": "bitcoin crash explained why",
    "Goud en zilver": "gold price why rising explained",
    "Dividend beleggen": "dividend investing explained",
    "Beleggen voor beginners": "how to invest for beginners",
    "Persoonlijke financien": "personal finance tips money",
    "Pensioen / 401k": "retirement 401k explained",
    "Belastingen uitgelegd": "taxes explained how",
    "Schulden / creditcard": "credit card debt explained",
    "Economie van landen": "why country economy collapsing explained",
    "Tarieven / handelsoorlog": "tariffs trade war explained",
    "Oplichting / fraude bedrijven": "biggest financial fraud scandal explained",
    "Prijzen van alledaagse dingen": "why is it so expensive now explained",
    "Gaming-industrie geld": "video game industry money explained",
}

def token():
    d = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_WHATIF_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d))["access_token"]

T = None
def g(pad, **q):
    u = "https://www.googleapis.com/youtube/v3/" + pad + "?" + urllib.parse.urlencode(q)
    return json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"Authorization": "Bearer " + T})))

def sec(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * f for x, f in zip(m.groups(), (3600, 60, 1))) if m else 0

def scan(zoek, dagen):
    na = (datetime.now(timezone.utc) - timedelta(days=dagen)).strftime("%Y-%m-%dT%H:%M:%SZ")
    s = g("search", part="id", type="video", maxResults=50, order="viewCount", publishedAfter=na,
          q=zoek, relevanceLanguage="en", regionCode="US")
    aanbod = s.get("pageInfo", {}).get("totalResults", 0)
    ids = [x["id"]["videoId"] for x in s.get("items", [])]
    if not ids: return None
    v = g("videos", part="snippet,statistics,contentDetails", id=",".join(ids))["items"]
    kan = {x["snippet"]["channelId"] for x in v}
    ab = {c["id"]: int(c["statistics"].get("subscriberCount", 0)) for c in g("channels", part="statistics", id=",".join(kan))["items"]}
    nu = datetime.now(timezone.utc); lang = []
    for x in v:
        dur = sec(x["contentDetails"].get("duration"))
        views = int(x["statistics"].get("viewCount", 0))
        oud = max(1.0, (nu - datetime.fromisoformat(x["snippet"]["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 86400)
        r = dict(titel=x["snippet"]["title"], kanaal=x["snippet"]["channelTitle"], abo=ab.get(x["snippet"]["channelId"], 0),
                 views=views, per_dag=views / oud, id=x["id"])
        if dur >= 240: lang.append(r)
    if not lang: return None
    vraag = statistics.median(r["per_dag"] for r in lang)
    kleine = [r for r in lang if r["abo"] < 100_000 and r["views"] > max(r["abo"], 1)]
    score = vraag * (1 + len(kleine)) / math.sqrt(max(aanbod, 1))
    return dict(aanbod=aanbod, n_lang=len(lang), vraag=vraag, kleine=kleine, score=score,
                top=sorted(lang, key=lambda r: -r["views"])[:3])

def main():
    global T
    a = sys.argv[1:]; dagen = 30; uit = Path("kanalen/NICHE-SCAN.md"); onderwerpen = ONDERWERPEN
    if "--dagen" in a: i = a.index("--dagen"); dagen = int(a[i + 1]); del a[i:i + 2]
    if "--uit" in a: i = a.index("--uit"); uit = Path(a[i + 1]); del a[i:i + 2]
    if a:   # eigen lijst: regels "naam | zoekterm"
        onderwerpen = dict(l.split("|", 1) for l in Path(a[0]).read_text(encoding="utf-8").splitlines() if "|" in l)
        onderwerpen = {k.strip(): z.strip() for k, z in onderwerpen.items()}
    T = token(); res = {}
    for naam, zoek in onderwerpen.items():
        try: res[naam] = scan(zoek, dagen); print("ok", naam, flush=True)
        except Exception as e: print("fout", naam, e, flush=True)
    res = {k: r for k, r in res.items() if r}
    rij = sorted(res.items(), key=lambda kv: -kv[1]["score"])
    hoog = max(r["score"] for r in res.values()) or 1
    L = [f"# Niche-scan geld/financiën (Engels, VS)", "",
         f"Gemaakt: {datetime.now():%d-%m-%Y %H:%M}, video's van de laatste {dagen} dagen, alleen lange video's (4 min of langer).", "",
         "- **Vraag** = mediaan weergaven per dag van de best bekeken video's",
         "- **Aanbod** = hoeveel video's YouTube ongeveer vindt (ruwe schatting)",
         "- **Kleine winnaars** = video's van kanalen onder 100k abonnees met meer weergaven dan abonnees",
         "- **Score** (0-100) = veel vraag, weinig aanbod, en kleine kanalen maken kans", "",
         "| # | Onderwerp | Score | Vraag (views/dag) | Aanbod | Kleine winnaars |", "|---|---|---|---|---|---|"]
    for n, (k, r) in enumerate(rij, 1):
        L.append(f"| {n} | {k} | {100 * r['score'] / hoog:.0f} | {r['vraag']:,.0f} | {r['aanbod']:,} | {len(r['kleine'])} |")
    L += ["", "## Top 5 in detail", ""]
    for k, r in rij[:5]:
        L += [f"### {k}", "", "Best bekeken:"]
        L += [f"- {t['titel']} ({t['kanaal']}, {t['abo']:,} abo) - {t['views']:,} views" for t in r["top"]]
        if r["kleine"]:
            L += ["", "Kleine kanalen die het goed doen:"]
            L += [f"- {t['titel']} ({t['kanaal']}, {t['abo']:,} abo) - {t['views']:,} views"
                  for t in sorted(r["kleine"], key=lambda t: -t["views"])[:3]]
        L.append("")
    uit.write_text("\n".join(L), encoding="utf-8")
    json.dump(res, open(uit.with_suffix(".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("KLAAR", uit)

if __name__ == "__main__":
    main()
