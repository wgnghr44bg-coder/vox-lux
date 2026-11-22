"""Niche-scanner (22 nov 2026, eigenaar: "echt scannen welke niche nu hot is").
Per onderwerp: video's van de laatste 30 dagen (Engels, VS), gesorteerd op weergaven. Meet:
  vraag     = mediaan weergaven per dag van de top-50 lange video's (>= 4 min)
  groot     = video's van kanalen met > 1 mln abonnees (concurrentie)
  kleine    = aantal lange video's van kanalen < 100k abonnees met meer weergaven dan abonnees (kleine kanalen die winnen)
  score     = vraag x (1 + kleine) / wortel(1 + groot)   -> hoog = veel kijkers, weinig grote makers, nieuwkomers maken kans
Kosten: ±102 punten YouTube-quota per onderwerp (dagquotum 10.000, gedeeld met uploads). Standaard 25 onderwerpen ≈ 2.600.
Gebruik: python tools/niche_scan.py [--dagen 30] [--uit kanalen/NICHE-SCAN.md] [--git] [onderwerpen.txt]
Elke maandag 08:00 via taak "Niche-scan" (tools/niche_scan_wekelijks.ps1), met --git: bewaart en pusht de uitslag."""
import json, math, urllib.error, os, re, statistics, sys, urllib.parse, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

# 22 nov: korte zoektermen + woorden waarvan er minstens één in de titel moet staan (anders telt de video niet mee)
ONDERWERPEN = {
    "Waar gaat je geld heen (bonnetje)": ("where does your money go", ["where", "goes", "go", "breakdown", "cost"]),
    "Hoe verdient bedrijf X geld": ("how does make money business model", ["make money", "makes money", "business model", "earn"]),
    "Kwartaalcijfers uitgelegd": ("earnings report stock", ["earnings", "quarter", "revenue", "results"]),
    "Rente / Fed": ("federal reserve interest rates", ["fed", "rate", "powell", "federal reserve"]),
    "Inflatie": ("inflation prices", ["inflation", "prices", "cpi"]),
    "Beurscrash": ("stock market crash", ["crash", "sell-off", "selloff", "collapse", "plunge"]),
    "AI-bubbel": ("AI bubble", ["ai", "bubble", "nvidia", "openai"]),
    "Beursgangen (IPO)": ("IPO stock", ["ipo", "going public", "public"]),
    "Bedrijf in problemen": ("company bankruptcy", ["bankrupt", "bankruptcy", "collapse", "failing", "dying", "closing"]),
    "Bedrijfsgeschiedenis": ("rise and fall of company", ["rise", "fall", "story", "history", "how"]),
    "Miljardairs (echte)": ("billionaire net worth richest", ["richest", "net worth", "fortune", "musk", "bezos", "buffett", "zuckerberg"]),
    "Huizenmarkt": ("housing market", ["housing", "home", "house", "real estate", "mortgage", "rent"]),
    "Crypto / bitcoin": ("bitcoin", ["bitcoin", "crypto", "btc"]),
    "Goud en zilver": ("gold price", ["gold", "silver"]),
    "Dividend beleggen": ("dividend stocks", ["dividend"]),
    "Beleggen voor beginners": ("investing for beginners", ["invest", "beginner", "stocks"]),
    "Persoonlijke financien": ("personal finance", ["money", "budget", "save", "saving", "finance"]),
    "Pensioen / 401k": ("retirement 401k", ["retire", "retirement", "401k", "ira", "social security"]),
    "Belastingen": ("taxes IRS", ["tax", "taxes", "irs"]),
    "Schulden / creditcard": ("credit card debt", ["debt", "credit"]),
    "Economie van landen": ("economy collapse country", ["economy", "economic", "gdp", "recession"]),
    "Tarieven / handelsoorlog": ("tariffs trade war", ["tariff", "tariffs", "trade"]),
    "Fraude en schandalen": ("financial fraud scandal", ["fraud", "scam", "scandal", "ponzi"]),
    "Alles wordt duurder": ("why is everything so expensive", ["expensive", "prices", "cost", "afford"]),
    "Geld in de gaming-industrie": ("video game industry money", ["game", "gaming", "gta", "nintendo", "playstation", "xbox"]),
}
ENGELSE_LANDEN = {"US", "GB", "CA", "AU", "IE", "NZ"}

def token():
    d = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_WHATIF_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    return json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", d))["access_token"]

T = None
CACHE = Path.home() / ".niche-scan-cache" / datetime.now().strftime("%Y-%m-%d")   # 22 nov: zelfde dag opnieuw = geen quota
def g(pad, **q):
    import hashlib
    u = "https://www.googleapis.com/youtube/v3/" + pad + "?" + urllib.parse.urlencode(q)
    f = CACHE / (hashlib.md5(u.encode()).hexdigest() + ".json")
    if f.exists(): return json.loads(f.read_text(encoding="utf-8"))
    d = json.load(urllib.request.urlopen(urllib.request.Request(u, headers={"Authorization": "Bearer " + T})))
    CACHE.mkdir(parents=True, exist_ok=True); f.write_text(json.dumps(d), encoding="utf-8")
    return d

def sec(iso):
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return sum(int(x or 0) * f for x, f in zip(m.groups(), (3600, 60, 1))) if m else 0

def zoek_web(zoek):
    import subprocess
    u = "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(zoek) + "&sp=CAMSBAgEEAE%253D"   # meest bekeken, deze maand
    out = subprocess.run([sys.executable, "-m", "yt_dlp", "--flat-playlist", "--playlist-end", "50", "-J", u],
                         capture_output=True, text=True, encoding="utf-8", timeout=180).stdout
    return [e["id"] for e in json.loads(out).get("entries", []) if e.get("id")][:50]

def scan(zoek, woorden, dagen):
    na = (datetime.now(timezone.utc) - timedelta(days=dagen)).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        s = g("search", part="id", type="video", maxResults=50, order="viewCount", publishedAfter=na,
              q=zoek, relevanceLanguage="en", regionCode="US")
        ids = [x["id"]["videoId"] for x in s.get("items", [])]
    except urllib.error.HTTPError as e:      # 22 nov: zoek-quota op -> zelfde zoekopdracht via de website (yt-dlp), kost geen quota
        if e.code not in (403, 429): raise
        ids = zoek_web(zoek)
    if not ids: return None
    v = g("videos", part="snippet,statistics,contentDetails", id=",".join(ids))["items"]
    kan = {x["snippet"]["channelId"] for x in v}
    cs = g("channels", part="statistics,snippet", id=",".join(kan))["items"]
    ab = {c["id"]: int(c["statistics"].get("subscriberCount", 0)) for c in cs}
    land = {c["id"]: c["snippet"].get("country") for c in cs}
    nu = datetime.now(timezone.utc); lang = []
    for x in v:
        sn = x["snippet"]; titel = sn["title"]
        taal = (sn.get("defaultAudioLanguage") or sn.get("defaultLanguage") or "").lower()
        if taal and not taal.startswith("en"): continue                       # 22 nov: alleen Engelstalig
        if not taal and land.get(sn["channelId"]) not in ENGELSE_LANDEN | {None}: continue
        if not titel.isascii() and sum(not c.isascii() for c in titel) > 3: continue   # Hindi, Arabisch enz.
        if re.search(r"\b(hindi|urdu|tagalog|ang |ng |ni )\b", titel.lower() + " " + sn["channelTitle"].lower()): continue
        if not any(re.search(r"\b" + re.escape(w) + r"\b", titel.lower()) for w in woorden): continue            # 22 nov: moet echt over het onderwerp gaan
        dur = sec(x["contentDetails"].get("duration"))
        views = int(x["statistics"].get("viewCount", 0))
        oud = max(1.0, (nu - datetime.fromisoformat(x["snippet"]["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 86400)
        r = dict(titel=x["snippet"]["title"], kanaal=x["snippet"]["channelTitle"], abo=ab.get(x["snippet"]["channelId"], 0),
                 views=views, per_dag=views / oud, id=x["id"])
        if dur >= 240: lang.append(r)
    if not lang: return None
    vraag = statistics.median(r["per_dag"] for r in lang)
    kleine = [r for r in lang if r["abo"] < 100_000 and r["views"] > max(r["abo"], 1)]
    groot = sum(1 for r in lang if r["abo"] >= 1_000_000)
    score = vraag * (1 + len(kleine)) / math.sqrt(1 + groot)
    return dict(groot=groot, n_lang=len(lang), vraag=vraag, kleine=kleine, score=score,
                top=sorted(lang, key=lambda r: -r["views"])[:3])

def main():
    global T
    a = sys.argv[1:]; dagen = 30; uit = Path("kanalen/NICHE-SCAN.md"); onderwerpen = ONDERWERPEN
    if "--dagen" in a: i = a.index("--dagen"); dagen = int(a[i + 1]); del a[i:i + 2]
    if "--uit" in a: i = a.index("--uit"); uit = Path(a[i + 1]); del a[i:i + 2]
    git = "--git" in a
    if git: a.remove("--git")
    if a:   # eigen lijst: regels "naam | zoekterm"
        onderwerpen = {}
        for l in Path(a[0]).read_text(encoding="utf-8").splitlines():   # regels "naam | zoekterm | woord1,woord2"
            d = [x.strip() for x in l.split("|")]
            if len(d) == 3: onderwerpen[d[0]] = (d[1], [w.strip().lower() for w in d[2].split(",")])
    T = token(); res = {}
    for naam, (zoek, woorden) in onderwerpen.items():
        try: res[naam] = scan(zoek, woorden, dagen); print("ok", naam, flush=True)
        except Exception as e: print("fout", naam, e, flush=True)
    res = {k: r for k, r in res.items() if r}
    try: vorig = json.load(open(uit.with_suffix(".json"), encoding="utf-8"))   # 22 nov: vergelijken met vorige week
    except Exception: vorig = {}
    if not res: sys.exit("GEEN UITSLAG (quota op of alles gefilterd); oude scan blijft staan")
    rij = sorted(res.items(), key=lambda kv: -kv[1]["score"])
    hoog = max(r["score"] for r in res.values()) or 1
    L = [f"# Niche-scan geld/financiën (Engels, VS)", "",
         f"Gemaakt: {datetime.now():%d-%m-%Y %H:%M}, video's van de laatste {dagen} dagen, alleen lange video's (4 min of langer).", "",
         "- **Vraag** = mediaan weergaven per dag van de best bekeken video's",
         "- **Grote kanalen** = hoeveel van de best bekeken video's van kanalen met meer dan 1 miljoen abonnees komen (concurrentie)",
         "- **Kleine winnaars** = video's van kanalen onder 100k abonnees met meer weergaven dan abonnees",
         "- **Score** (0-100) = veel vraag, weinig grote concurrenten, en kleine kanalen maken kans", "",
         "- **Trend** = vraag vergeleken met de vorige scan", "",
         "| # | Onderwerp | Score | Vraag (views/dag) | Trend | Grote kanalen | Kleine winnaars |", "|---|---|---|---|---|---|---|"]
    for n, (k, r) in enumerate(rij, 1):
        v0 = (vorig.get(k) or {}).get("vraag")
        trend = "nieuw" if not v0 else f"{100 * (r['vraag'] / v0 - 1):+.0f}%"
        L.append(f"| {n} | {k} | {100 * r['score'] / hoog:.0f} | {r['vraag']:,.0f} | {trend} | {r['groot']} | {len(r['kleine'])} |")
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
    if git:
        sys.path.insert(0, str(Path(__file__).parent)); from gitveilig import bewaar
        bewaar([str(uit), str(uit.with_suffix(".json"))], f"Niche-scan {datetime.now():%d-%m-%Y}")
    print("KLAAR", uit)

if __name__ == "__main__":
    main()
