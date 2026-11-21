"""Nederlandse hype-wachter voor BlackswanVault NL (eigenaar 21 nov 2026: "kun je als bron nu.nl, Financieel Dagblad gebruiken,
wat er in Nederland hype is, en zowel op YouTube checken met een wachter").

1. Nieuws (RSS, laatste 36 uur): nu.nl Economie, Financieel Dagblad, NOS Economie. Punten voor een grote naam (ASML, Shell,
   ING, kabinet, DNB, ...) en een gebeurtenis (ontslagen, overname, crash, faillissement, ...). Hoe meer bronnen, hoe hoger.
2. Koersen (Yahoo): AEX en de grootste Nederlandse bedrijven, bitcoin in euro's.
3. YouTube (Nederlands, regio NL, laatste 72 uur): welke geld-/beursvideo's krijgen nu het snelst views; onderwerpen die
   op YouTube én in het nieuws groot zijn heten STERK.
Alleen lezen, gratis (YouTube API-quota). Uitkomst: stories/nl-hype.json (voor de website).

  python tools/nl_wacht.py            # alles
  python tools/nl_wacht.py --zonder-youtube
"""
import datetime as dt, json, re, sys, time
from collections import defaultdict
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import nieuwswacht as nw

STORIES = HIER.parent / "stories"
UIT = STORIES / "nl-hype.json"

nw.FEEDS = {"nu.nl": "https://www.nu.nl/rss/Economie",
            "FD": "https://fd.nl/?rss",
            "NOS": "https://feeds.nos.nl/nosnieuwseconomie"}
nw.KOERS = {"^AEX": ("AEX", 2.5), "ASML.AS": ("ASML", 7), "SHELL.AS": ("Shell", 6), "INGA.AS": ("ING", 7),
            "ADYEN.AS": ("Adyen", 10), "PRX.AS": ("Prosus", 8), "UNA.AS": ("Unilever", 6), "AD.AS": ("Ahold Delhaize", 6),
            "HEIA.AS": ("Heineken", 7), "PHIA.AS": ("Philips", 8), "ABN.AS": ("ABN AMRO", 7), "BESI.AS": ("BESI", 10),
            "BTC-EUR": ("Bitcoin", 10)}
nw.NAMEN = {"asml": "ASML", " shell": "Shell", " ing ": "ING", "abn": "ABN AMRO", "rabobank": "Rabobank", "adyen": "Adyen",
            "prosus": "Prosus", "philips": "Philips", "heineken": "Heineken", "unilever": "Unilever", "ahold": "Ahold Delhaize",
            "albert heijn": "Ahold Delhaize", "besi": "BESI", "nexperia": "Nexperia", "booking": "Booking", "tata steel": "Tata Steel",
            "klm": "KLM", "schiphol": "Schiphol", " bol ": "Bol", "coolblue": "Coolblue", "postnl": "PostNL", " ns ": "NS",
            "kabinet": "Kabinet", "belasting": "Belastingen", "dnb": "DNB", "ecb": "ECB", "rente": "Rente", "hypothe": "Huizenmarkt",
            "huizen": "Huizenmarkt", "woning": "Huizenmarkt", "inflatie": "Inflatie", "pensioen": "Pensioenen", "energie": "Energie",
            "gasprijs": "Energie", "stroom": "Energie", "bitcoin": "Bitcoin", "crypto": "Bitcoin", "aex": "Beurs", "beurs": "Beurs",
            "nvidia": "Nvidia", "trump": "Trump", "heffing": "Importheffingen", "tarief": "Importheffingen", "china": "China",
            "chip": "Chips", " ai ": "AI", "kunstmatige intelligentie": "AI", "faillis": "Faillissementen", "boodschappen": "Boodschappen"}
nw.GEBEURT = [(r"(vertrekt|stapt op|treedt af|ontslagen als|nieuwe ceo|nieuwe topman|topvrouw)", 3, "top weg"),
              (r"(faillie|failliet|bankroet|surseance|omgevallen)", 4, "faillissement"),
              (r"(overname|neemt .{0,30} over|fusie|koopt|miljard)", 3, "overname/deal"),
              (r"(crash|keldert|zakt|daalt fors|kelderde|onderuit|ingestort|beurskrach|rood)", 4, "daling"),
              (r"(record|stijgt fors|schiet omhoog|hoogste|knalt)", 2, "record"),
              (r"(banen|ontslagen|reorganisatie|schrapt)", 2, "ontslagen"),
              (r"(rechtszaak|boete|onderzoek naar|toezichthouder|acm|afm)", 2, "rechtszaak"),
              (r"(beursgang|naar de beurs)", 2, "beursgang"),
              (r"(rente|recessie|inflatie|krimp)", 3, "rente/economie"),
              (r"(duurder|prijsstijging|prijzen stijgen|tekort)", 2, "prijzen"),
              (r"(winst|omzet|kwartaal|resultaten)", 1, "cijfers")]

ZOEK = ["beurs nieuws", "aandelen", "economie nieuws", "beleggen", "bitcoin nieuws", "ASML aandeel", "huizenmarkt", "inflatie Nederland"]
STOP = set("""de het een en of van in op voor met aan bij uit om te is zijn was waren wordt worden dit dat die deze er niet geen
wel ook nog maar dan als hoe wat wie waarom waar wanneer je jij jouw we wij ons onze ze zij hun hij zijn haar ik mijn me nu
nieuws nieuw nieuwe live vandaag gaat gaan komt komen kan kun moet moeten wil willen heeft hebben had over naar tot meer meest
minder veel alle alles echt zo heel grote groot beste nooit altijd jaar maand week dag deel video shorts aandeel aandelen beurs
beleggen geld economie euro doen daalt dalen stijgt stijgen kopen verkopen moet moeten jouw podcast afl procent miljard miljoen 2025 2026 the and you this how why what""".split())


def youtube(uren=72):
    import requests
    from swan_yt_wacht import token, get
    tok = token()
    nu = dt.datetime.now(dt.timezone.utc)
    sinds = (nu - dt.timedelta(hours=uren)).strftime("%Y-%m-%dT%H:%M:%SZ")
    ids = set()
    for q in ZOEK:
        time.sleep(2)
        try:
            r = get(tok, "search", part="id", q=q, type="video", order="viewCount", publishedAfter=sinds,
                    regionCode="NL", relevanceLanguage="nl", maxResults=25)
            ids |= {i["id"]["videoId"] for i in r.get("items", [])}
        except requests.HTTPError as e:
            code = e.response.status_code if e.response is not None else 0
            print("zoeken mislukt:", q, code)
            if code == 403:
                break
    vids = []
    lijst = list(ids)
    for k in range(0, len(lijst), 50):
        r = get(tok, "videos", part="snippet,statistics", id=",".join(lijst[k:k + 50]))
        for v in r.get("items", []):
            s = v["snippet"]
            taal = (s.get("defaultAudioLanguage") or s.get("defaultLanguage") or "nl")[:2]
            if taal not in ("nl", ""):
                continue
            u = max(1.0, (nu - dt.datetime.fromisoformat(s["publishedAt"].replace("Z", "+00:00"))).total_seconds() / 3600)
            views = int(v["statistics"].get("viewCount", 0))
            vids.append({"id": v["id"], "titel": s["title"], "kanaal": s["channelTitle"], "views": views,
                         "per_uur": round(views / u), "uren_oud": round(u)})
    vids.sort(key=lambda x: -x["per_uur"])
    return vids


def woorden(t):
    t = re.sub(r"[^a-z0-9à-ü€$&' ]", " ", t.lower())
    return [w for w in t.split() if len(w) > 2 and w not in STOP and not w.isdigit()]


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    nu = dt.datetime.now()
    markt = nw.koersen()
    kp = nw.koppen()
    onderwerpen = {}
    for kop in kp:
        namen, pt, wat = nw.score(kop)
        if not namen or pt == 0:
            continue
        for n in namen:
            o = onderwerpen.setdefault(n, {"onderwerp": n, "punten": 0, "bronnen": set(), "wat": set(), "koppen": []})
            o["punten"] = max(o["punten"], pt + 1)
            o["bronnen"].add(kop["bron"])
            o["wat"].update(wat)
            if len(o["koppen"]) < 4:
                o["koppen"].append({"titel": kop["titel"], "bron": kop["bron"], "link": kop["link"]})
    nieuws = []
    for o in onderwerpen.values():
        o["punten"] += 2 * (len(o["bronnen"]) - 1)
        nieuws.append({**o, "bronnen": sorted(o["bronnen"]), "wat": sorted(o["wat"]), "groot": o["punten"] >= nw.GROOT})
    nieuws.sort(key=lambda o: -o["punten"])
    for m in markt:
        if m["groot"]:
            nieuws.insert(0, {"onderwerp": m["naam"], "punten": 10, "bronnen": ["koers"], "wat": [f"{m['pct']:+.1f}% op één dag"],
                              "koppen": [], "groot": True})

    vids, yt = [], []
    if "--zonder-youtube" not in sys.argv:
        try:
            vids = youtube()
        except Exception as e:
            print("YouTube mislukt:", e)
        gewicht, kanalen, voorbeeld = defaultdict(float), defaultdict(set), defaultdict(list)
        for v in vids[:120]:
            w = woorden(v["titel"])
            for t in set(w) | {f"{x} {y}" for x, y in zip(w, w[1:])}:
                gewicht[t] += v["per_uur"]; kanalen[t].add(v["kanaal"])
                if len(voorbeeld[t]) < 3:
                    voorbeeld[t].append(f'{v["titel"]} ({v["kanaal"]}, {v["views"]:,} views)')
        namen_nieuws = {o["onderwerp"].lower(): o for o in nieuws}
        for t, g in sorted(gewicht.items(), key=lambda x: -x[1]):
            if len(kanalen[t]) < 2 or any(t in o["onderwerp"].split() for o in yt):
                continue
            in_nieuws = any(n in t or t in n for n in namen_nieuws)
            yt.append({"onderwerp": t, "views_per_uur": round(g), "kanalen": len(kanalen[t]), "in_nieuws": in_nieuws,
                       "sterk": in_nieuws and len(kanalen[t]) >= 3, "voorbeelden": voorbeeld[t]})
            if len(yt) >= 15:
                break

    data = {"bijgewerkt": nu.strftime("%Y-%m-%d %H:%M"), "markt": markt, "nieuws": nieuws[:12],
            "groot": [o["onderwerp"] for o in nieuws if o["groot"]], "aantal_koppen": len(kp),
            "youtube": yt, "top_videos": vids[:15]}
    UIT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")

    print(f"nl-wacht {data['bijgewerkt']}: {len(kp)} koppen (nu.nl, FD, NOS), {len(vids)} NL-video's")
    for o in nieuws[:10]:
        k = o["koppen"][0]["titel"] if o["koppen"] else ", ".join(o["wat"])
        print(f'{o["punten"]:>3} {"GROOT" if o["groot"] else "     "} {o["onderwerp"]:16} [{", ".join(o["bronnen"])}] {k[:80]}')
    if yt:
        print("\nYouTube NL:")
        for o in yt[:10]:
            print(f'{o["views_per_uur"]:>7} v/u {o["kanalen"]:>2} kan. {"STERK" if o["sterk"] else ("nieuws" if o["in_nieuws"] else ""):6} {o["onderwerp"]}')
        print("\nSnelste NL-video's:")
        for v in vids[:8]:
            print(f'{v["per_uur"]:>7} v/u  {v["titel"][:75]}  [{v["kanaal"]}]')


if __name__ == "__main__":
    main()
