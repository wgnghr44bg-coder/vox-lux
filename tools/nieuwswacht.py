"""Nieuwswacht voor BlackswanVault (eigenaar 19 nov 2026: "als er economisch echt iets groots is dan moet wel video maken").

Elke ochtend (Taakplanner "BlackswanVault nieuwswacht", 08:00, 12:00, 15:45 en 20:00) op de pc. Alleen lezen, gratis:
  1. koersen (Yahoo chart API): S&P 500, Nasdaq, Dow, de grootste bedrijven, bitcoin, olie, goud.
     GROOT bij: index >= 2,5 % op een dag, groot bedrijf >= 8 %, bitcoin >= 10 %, olie >= 7 %.
  2. koppen (RSS van CNBC, MarketWatch, BBC Business, NYT Business, laatste 36 uur): punten voor een grote naam
     (Nvidia, Apple, Fed, ...) en een grote gebeurtenis (CEO weg, faillissement, overname, crash, ontslagen, ...).
     Hoe meer bronnen hetzelfde melden, hoe hoger. GROOT vanaf 7 punten.
Uitkomst: stories/nieuws.json (website, paneel "Nieuwswacht") en een seintje in stories/ROUTINE-LOG.md (één keer per
onderwerp per dag). Wat ermee gebeurt, beslist de eigenaar: een video maken of niet (zie kanalen/PLANNING.md).

  python tools/nieuwswacht.py
"""
import datetime as dt, email.utils, json, re, sys
from pathlib import Path
import xml.etree.ElementTree as ET

import requests

HIER = Path(__file__).resolve().parent
STORIES = HIER.parent / "stories"
UIT = STORIES / "nieuws.json"
UA = {"User-Agent": "BlackSwanVault-research/1.0 (https://www.youtube.com/@blackswanvault)"}
FEEDS = {"CNBC": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
         "CNBC business": "https://www.cnbc.com/id/10001147/device/rss/rss.html",
         "MarketWatch": "https://feeds.content.dowjones.io/public/rss/mw_topstories",
         "BBC": "https://feeds.bbci.co.uk/news/business/rss.xml",
         "NYT": "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"}
KOERS = {"^GSPC": ("S&P 500", 2.5), "^IXIC": ("Nasdaq", 2.5), "^DJI": ("Dow Jones", 2.5),
         "NVDA": ("Nvidia", 8), "AAPL": ("Apple", 8), "MSFT": ("Microsoft", 8), "GOOGL": ("Alphabet", 8),
         "AMZN": ("Amazon", 8), "META": ("Meta", 8), "TSLA": ("Tesla", 8), "AVGO": ("Broadcom", 8),
         "BRK-B": ("Berkshire", 6), "JPM": ("JPMorgan", 7), "WMT": ("Walmart", 7), "BTC-USD": ("Bitcoin", 10),
         "CL=F": ("Olie", 7), "GC=F": ("Goud", 4)}
NAMEN = {"nvidia": "Nvidia", "apple": "Apple", "microsoft": "Microsoft", "google": "Alphabet", "alphabet": "Alphabet",
         "amazon": "Amazon", "meta ": "Meta", "facebook": "Meta", "tesla": "Tesla", "musk": "Musk", "openai": "OpenAI",
         "berkshire": "Berkshire", "buffett": "Buffett", "jpmorgan": "JPMorgan", "walmart": "Walmart", "intel": "Intel",
         "boeing": "Boeing", "disney": "Disney", "netflix": "Netflix", "federal reserve": "Fed", "the fed": "Fed",
         "powell": "Fed", "bitcoin": "Bitcoin", "crypto": "Bitcoin", "tariff": "Tarieven", "recession": "Recessie",
         "wall street": "Wall Street", "stock market": "Beurs", "s&p 500": "Beurs", "dow ": "Beurs", "nasdaq": "Beurs",
         "anthropic": "Anthropic", "broadcom": "Broadcom", "amd": "AMD", "tsmc": "TSMC", "starbucks": "Starbucks",
         "nike": "Nike", "black friday": "Black Friday", "oil": "Olie", "gold": "Goud", "inflation": "Inflatie"}
GEBEURT = [(r"\b(steps? down|resign|ousted|fired|departs?|retire[sd]?|succession|new ceo)\b", 3, "CEO/top weg"),
           (r"\b(bankrupt|chapter 11|insolven|collapse[sd]?|default)", 4, "faillissement"),
           (r"\b(acqui|merger|to buy|buyout|takeover|deal worth|\$\d+(\.\d+)? ?(billion|trillion|bn))", 3, "overname/deal"),
           (r"\b(crash|plunge|tumble|sell-?off|rout|wipes? out|biggest drop|worst day)", 4, "crash"),
           (r"\b(soar|surge|record high|all-time high|biggest gain|trillion)", 2, "record"),
           (r"\b(layoffs?|job cuts|cut .{0,15}jobs)", 2, "ontslagen"),
           (r"\b(antitrust|break ?up|lawsuit|fine[ds]? \$|probe|indict)", 2, "rechtszaak"),
           (r"\b(ipo|going public)\b", 2, "beursgang"),
           (r"\b(rate cut|rate hike|raises rates|cuts rates|recession|stagflation)", 3, "rente/recessie"),
           (r"\b(earnings|quarter|revenue|guidance)\b", 1, "cijfers")]
GROOT = 7          # Short waard; ntfy "Grote hype: BlackswanVault - Short"
KOERS_WOORD = {"S&P 500": ["s&p", "stock market", "stocks", "wall street"], "Nasdaq": ["nasdaq", "tech stocks"],
               "Dow Jones": ["dow", "stock market", "wall street"], "Olie": ["oil", "crude", "opec"],
               "Goud": ["gold", "bullion"], "Bitcoin": ["bitcoin", "crypto"], "Berkshire": ["berkshire", "buffett"]}
LANG = 10         # 26 nov (eigenaar): Short + lange video waard (veel bronnen tegelijk, of een koerssprong)


def koersen():
    uit = []
    for sym, (naam, grens) in KOERS.items():
        try:
            r = requests.get(f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}", headers=UA, timeout=20,
                             params={"range": "5d", "interval": "1d"}).json()["chart"]["result"][0]
            c = [x for x in r["indicators"]["quote"][0]["close"] if x]
            if len(c) < 2:
                continue
            pct = 100 * (c[-1] - c[-2]) / c[-2]
            uit.append({"naam": naam, "pct": round(pct, 1), "groot": abs(pct) >= grens, "grens": grens})
        except Exception:
            pass
    return uit


def koppen():
    grens = dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=36)
    uit = []
    for bron, url in FEEDS.items():
        try:
            root = ET.fromstring(requests.get(url, headers=UA, timeout=20).content)
        except Exception:
            continue
        for it in root.iter("item"):
            titel = (it.findtext("title") or "").strip()
            try:
                t = email.utils.parsedate_to_datetime(it.findtext("pubDate"))
            except Exception:
                t = None
            if titel and (t is None or t >= grens):
                uit.append({"bron": bron, "titel": titel, "link": (it.findtext("link") or "").strip(),
                            "tijd": t.isoformat() if t else ""})
    return uit


def score(kop):
    k = " " + kop["titel"].lower() + " "
    namen = sorted({v for n, v in NAMEN.items() if n in k})
    ev = [(p, w) for rx, p, w in GEBEURT if re.search(rx, k)]
    return namen, sum(p for p, _ in ev), [w for _, w in ev]


def main():
    nu = dt.datetime.now()
    markt = koersen()
    kp = koppen()
    onderwerpen = {}
    for kop in kp:
        namen, pt, wat = score(kop)
        if not namen or pt == 0:
            continue
        for n in namen:
            o = onderwerpen.setdefault(n, {"onderwerp": n, "punten": 0, "bronnen": set(), "wat": set(), "koppen": []})
            o["punten"] = max(o["punten"], pt + 1)
            o["bronnen"].add(kop["bron"].split()[0])
            o["wat"].update(wat)
            if len(o["koppen"]) < 4:
                o["koppen"].append({"titel": kop["titel"], "bron": kop["bron"], "link": kop["link"]})
    lijst = []
    for o in onderwerpen.values():
        o["punten"] += 2 * (len(o["bronnen"]) - 1)
        lijst.append({**o, "bronnen": sorted(o["bronnen"]), "wat": sorted(o["wat"]), "groot": o["punten"] >= GROOT})
    lijst.sort(key=lambda o: -o["punten"])
    # 27 nov: goud +4,4% (Thanksgiving, dunne handel) gaf vals alarm zonder één nieuwskop. Een koerssprong is pas hype als
    # het nieuws er ook over schrijft: met koppen 10 punten (Short + lang), zonder koppen 5 (alleen op het paneel, geen seintje).
    for m in markt:
        if m["groot"]:
            woorden = KOERS_WOORD.get(m["naam"], [m["naam"].lower()])
            hits = [k for k in kp if any(w in k["titel"].lower() for w in woorden)]
            pt = 10 if hits else 5
            lijst.insert(0, {"onderwerp": m["naam"], "punten": pt, "bronnen": sorted({"koers"} | {k["bron"].split()[0] for k in hits}),
                             "wat": [f"{m['pct']:+.1f}% op één dag" + ("" if hits else " (geen nieuws erover)")],
                             "koppen": [{"titel": k["titel"], "bron": k["bron"], "link": k["link"]} for k in hits[:4]],
                             "groot": pt >= GROOT})
    data = {"bijgewerkt": nu.strftime("%Y-%m-%d %H:%M"), "markt": markt, "onderwerpen": lijst[:12],
            "groot": [o["onderwerp"] for o in lijst if o["groot"]], "aantal_koppen": len(kp)}
    UIT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    log = STORIES / "ROUTINE-LOG.md"
    oud = log.read_text(encoding="utf-8", errors="replace") if log.exists() else ""
    seintjes = []
    with open(log, "a", encoding="utf-8") as f:
        for o in lijst:
            if o["groot"]:
                soort = "Short + lange video" if o["punten"] >= LANG else "Short"
                sleutel = f"nieuwswacht: GROOT {o['onderwerp']} ({nu:%Y-%m-%d})" + (" LANG" if soort != "Short" else "")
                if sleutel not in oud:
                    kop = o["koppen"][0]["titel"] if o["koppen"] else ", ".join(o["wat"])
                    f.write(f"- {nu:%Y-%m-%d %H:%M} {sleutel}: {kop[:140]} -> BlackswanVault: {soort}? (eigenaar beslist)\n")
                    seintjes.append((soort, o, kop))
    # 26 nov (eigenaar): "bericht sturen zodra er hype is voor een short of een short+long" -> ntfy op de telefoon
    if seintjes:
        try:
            sys.path.insert(0, str(HIER))
            from swan_yt_wacht import seintje
            for soort, o, kop in seintjes[:3]:
                seintje(f"Grote hype: BlackswanVault - {soort}",
                        f"{o['onderwerp']}: {kop[:160]}\n({o['punten']} punten, bronnen: {', '.join(o['bronnen'])})")
        except Exception as e:
            print("seintje mislukt:", e)
    print(f"nieuwswacht {data['bijgewerkt']}: {len(kp)} koppen, groot: {', '.join(data['groot']) or 'niets'}")
    for o in lijst[:8]:
        print(f"  {o['punten']:2d} {'GROOT ' if o['groot'] else '      '}{o['onderwerp']:12s} {', '.join(o['wat'])[:40]:40s} | {(o['koppen'][0]['titel'] if o['koppen'] else '')[:70]}")


if __name__ == "__main__":
    main()
