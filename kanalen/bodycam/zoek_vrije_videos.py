#!/usr/bin/env python3
"""Zoekt online naar de nieuwste video's die je op YouTube mag gebruiken (public domain / vrije licentie).

Gebruik:
  python kanalen/bodycam/zoek_vrije_videos.py                      # standaard bodycam-termen, alle bronnen
  python kanalen/bodycam/zoek_vrije_videos.py --zoek "police chase,pursuit" --aantal 30
  python kanalen/bodycam/zoek_vrije_videos.py --bronnen commons,cbp

Bronnen zonder sleutel: overheid (BREED: alle Commons-video's van overheden zonder auteursrecht – LAPD, Californië,
Florida, federaal – gefilterd op incidenten), commons, archive, cbp, dhs, mixkit
Kolom "verhaal" (0-5 sterren): grove kans op een goed verhaal (standoff/achtervolging/gijzeling, 3-45 min, jaartal of
naam in de titel, maker is een korps). --sorteer verhaal zet de beste kandidaten bovenaan.
Met gratis API-sleutel (omgevingsvariabele): dvids (DVIDS_API_KEY), pexels (PEXELS_API_KEY), pixabay (PIXABAY_API_KEY)
Niet automatisch (blokkeren scripts / geen video): loc.gov, fbi.gov, bjs.ojp.gov -> zie de tips onderaan het verslag.

Uitvoer: kanalen/bodycam/nieuwe-videos.md (NIEUW = nog niet eerder gezien, bijgehouden in gezien.json).
Alles is gratis; er wordt niets gedownload, alleen gezocht.

LET OP: "mag" betekent alleen dat de licentie het toestaat. Controleer altijd zelf de bronpagina, maak een screenshot
van de licentie, en laat stukken van derden (winkelcamera's, nieuwszenders, muziek) weg.
"""
import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

MAP = Path(__file__).resolve().parent
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) vrije-videos-zoeker/1.0"
TIMEOUT = 30


def haal(url, headers=None, als_json=True):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        for wacht in (10, 30, 60, None):  # bij "te veel verzoeken" (429) even wachten en opnieuw
            try:
                with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                    data = r.read().decode("utf-8", "replace")
                break
            except urllib.error.HTTPError as e:
                if e.code != 429 or wacht is None:
                    raise
                print(f"  te veel verzoeken, {wacht} s wachten ...", file=sys.stderr)
                time.sleep(wacht)
    except urllib.error.HTTPError as e:
        if e.code != 403 or not shutil.which("curl"):
            raise
        # sommige overheidssites (cbp.gov, dhs.gov) weigeren Python maar niet curl
        cmd = ["curl", "-sfL", "--max-time", str(TIMEOUT), "-A", UA]
        for k, v in (headers or {}).items():
            cmd += ["-H", f"{k}: {v}"]
        data = subprocess.run(cmd + [url], capture_output=True, check=True).stdout.decode("utf-8", "replace")
    return json.loads(data) if als_json else data


def schoon(t):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", t or ""))).strip()


def oordeel_licentie(lic):
    """Geeft (status, uitleg). status: MAG / LET OP / NIET."""
    l = (lic or "").lower()
    if not l:
        return "NIET", "geen licentie vermeld"
    if any(k in l for k in ["-nc", " nc", "noncommercial", "non-commercial", "-nd", " nd", "noderiv"]):
        return "NIET", "niet-commercieel of geen bewerking toegestaan"
    if any(k in l for k in ["public domain", "publicdomain", "pd-", "cc0", "pdm", "zero"]):
        return "MAG", "public domain"
    if "by-sa" in l or "by sa" in l:
        return "LET OP", "CC BY-SA: bronvermelding + je video onder dezelfde licentie"
    if re.search(r"\bby\b|cc by|/by/", l):
        return "MAG", "CC BY: met bronvermelding"
    if any(k in l for k in ["pexels", "pixabay", "mixkit"]):
        return "MAG", "gratis stock-licentie (geen bronvermelding nodig; kan Content ID-claims geven)"
    return "LET OP", f"onbekende licentie: {lic}"


# Media-kanalen die korpsbeelden bewerken en op YouTube zetten: hun versie kan Content ID-claims geven.
MEDIAKANALEN = ["policeactivity", "law&crime", "law & crime", "lawandcrime", "code blue cam", "midwest safety",
                "real world police", "bodycam watch", "police state", "court tv", "inside edition", "abc", "nbc",
                "cbs", "fox", "cnn", "ktla", "wfla", "news", "audit the audit", "the voice of reason",
                "police watch", "response files", "copcam", "bodycam files", "jim the lawyer"]
# Woorden die op een overheid/korps wijzen (alleen dan is "public domain" voor bodycam aannemelijk).
OVERHEID = ["police department", "police dept", "sheriff", "county", "city of", "state patrol", "highway patrol",
            "state police", "prosecutor", "attorney", "department", "government", "lapd", "nypd", "cbp", "dhs",
            "customs", "border", "fbi", "u.s.", "us army", "marshals"]


def verhaal_score(r):
    """0-5: hoe waarschijnlijk er een goed verhaal van te maken is (grove schatting op titel, duur en maker)."""
    t, sc = r["titel"].lower(), 0
    if any(k in t for k in STERK):
        sc += 2
    elif any(k in t for k in INCIDENT):
        sc += 1
    sec = r.get("sec") or 0
    if 180 <= sec <= 2700:          # 3-45 min: genoeg beeld voor 10-15 min video
        sc += 1
    if re.search(r"\b(19|20)\d\d\b", t) or re.search(r"\b[A-Z][a-z]+ [A-Z][a-z]+'s\b", r["titel"]):
        sc += 1                     # jaartal of naam ("Ryan Routh's Arrest"): bekend incident, nieuws te vinden
    if any(k in schoon(r.get("maker", "")).lower() for k in OVERHEID):
        sc += 1
    return min(sc, 5)


# ---------------------------------------------------------------- bronnen

def termen(q):
    return [t.strip() for t in q.split(",") if t.strip()]


def zoek_commons(q, n):
    titels = []
    for t in termen(q):  # alleen video's met de zoekterm in de TITEL (anders komt er veel onzin mee)
        p = {"action": "query", "format": "json", "list": "search", "srnamespace": 6, "srlimit": n,
             "srsearch": f'intitle:"{t}" filetype:video', "srsort": "create_timestamp_desc"}
        zoek = haal("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
        time.sleep(1)  # Wikimedia vraagt om rustig aan te doen
        titels += [r["title"] for r in zoek.get("query", {}).get("search", [])]
    return commons_details(list(dict.fromkeys(titels)), "Wikimedia Commons")


# Licentiesjablonen op Commons voor werk van overheden zonder auteursrecht (bodycam, dashcam, persvideo's).
OVERHEID_SJABLONEN = ["PD-CAGov-LAPD", "PD-CAGov", "PD-FLGov", "PD-USGov-DHS-CBP", "PD-USGov-DHS", "PD-USGov-FBI",
                      "PD-USGov-DOJ", "PD-USGov-Military", "PD-USGov", "PD-USGov-NTSB", "PD-USGov-FAA",
                      "PD-USGov-NPS", "PD-USGov-USCG", "PD-AZGov", "PD-WAGov", "PD-MNGov", "PD-OHGov"]
# Woorden in de titel die op een incident met een verhaal wijzen (geen persconferentie of opsporingsbericht).
INCIDENT = ["bodycam", "body cam", "body camera", "body-worn", "body worn", "dashcam", "dash cam", "shooting",
            "shootout", "shots", "standoff", "hostage", "pursuit", "chase", "arrest", "ois", "officer-involved",
            "officer involved", "critical incident", "use of force", "carjack", "robbery", "stabbing", "rescue",
            "barricade", "swat", "ambush", "crash", "fire", "drown", "kidnap", "riot", "manhunt", "escape",
            "standoff", "taser", "k9", "k-9", "traffic stop", "dui", "overdose", "911", "raid", "intercept"]
STERK = ["shootout", "standoff", "hostage", "pursuit", "manhunt", "ambush", "kidnap", "barricade", "rescue",
         "carjack", "escape", "critical incident", "officer-involved", "officer involved"]


def zoek_overheid(q, n):
    """Breed: alle video's met een overheids-PD-sjabloon, nieuwste eerst, gefilterd op incident-woorden."""
    titels = []
    for sj in OVERHEID_SJABLONEN:
        p = {"action": "query", "format": "json", "list": "search", "srnamespace": 6, "srlimit": min(500, n * 8),
             "srsearch": f'hastemplate:"{sj}" filetype:video', "srsort": "create_timestamp_desc"}
        try:
            zoek = haal("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
        except Exception as e:
            print(f"  {sj}: overgeslagen ({e})", file=sys.stderr)
            continue
        time.sleep(1.5)
        gevonden = [r["title"] for r in zoek.get("query", {}).get("search", [])
                    if any(k in r["title"].lower() for k in INCIDENT)]
        print(f"  {sj}: {len(gevonden)} incident-video's", file=sys.stderr)
        titels += gevonden
    return commons_details(list(dict.fromkeys(titels)), "Commons (overheid)")


def commons_details(titels, bronnaam):
    uit = []
    for i in range(0, len(titels), 20):
        time.sleep(1)
        p = {"action": "query", "format": "json", "prop": "imageinfo|templates", "titles": "|".join(titels[i:i + 20]),
             "iiprop": "extmetadata|size|timestamp", "tllimit": 500,
             "iiextmetadatafilter": "LicenseShortName|Artist|DateTimeOriginal"}
        d = haal("https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode(p))
        for pg in d.get("query", {}).get("pages", {}).values():
            ii = (pg.get("imageinfo") or [{}])[0]
            m = ii.get("extmetadata", {})
            dur = ii.get("duration")
            sj = {t["title"] for t in pg.get("templates", [])}
            waarsch = ""
            if any(x in sj for x in ["Template:Delete", "Template:Deletion request", "Template:Copyvio",
                                     "Template:No permission since", "Template:No license since"]):
                waarsch = "verwijderverzoek op Commons"
            elif "Template:LicenseReview/layout-reviewme" in sj:
                waarsch = "licentie nog niet gecontroleerd door Commons"
            uit.append({"waarschuwing": waarsch,
                "bron": bronnaam, "titel": pg["title"].removeprefix("File:"), "sec": dur or 0,
                "datum": (ii.get("timestamp") or "")[:10],
                "duur": f"{int(dur // 60)}:{int(dur % 60):02d}" if dur else "",
                "licentie": schoon(m.get("LicenseShortName", {}).get("value")),
                "maker": schoon(m.get("Artist", {}).get("value"))[:60],
                "url": "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(pg["title"].replace(" ", "_")),
            })
    return uit


def zoek_archive(q, n):
    # alleen items MET licentie (de meeste bodycam-items op archive.org zijn YouTube-kopieën zonder licentie)
    zoekterm = " OR ".join(f'"{t}"' for t in termen(q))
    p = [("q", f"title:({zoekterm}) AND mediatype:movies AND licenseurl:*"), ("rows", n), ("output", "json"),
         ("sort[]", "addeddate desc")] + [("fl[]", f) for f in ["identifier", "title", "licenseurl", "addeddate", "creator"]]
    d = haal("https://archive.org/advancedsearch.php?" + urllib.parse.urlencode(p))
    uit = []
    for r in d.get("response", {}).get("docs", []):
        lic = r.get("licenseurl", "")
        if "publicdomain" in lic:
            lic = "Public domain (" + lic + ")"
        elif "creativecommons.org/licenses/" in lic:
            lic = "CC " + lic.split("/licenses/")[1].strip("/").upper().replace("/", " ")
        c = r.get("creator", "")
        uit.append({"bron": "Archive.org", "titel": schoon(r.get("title")), "datum": (r.get("addeddate") or "")[:10],
                    "duur": "", "licentie": lic, "maker": (c[0] if isinstance(c, list) else c)[:60],
                    "url": "https://archive.org/details/" + r["identifier"],
                    "waarschuwing": "licentie door de uploader zelf ingevuld: check of die de maker is"})
    return uit


def zoek_cbp(q, n):
    h = haal("https://www.cbp.gov/newsroom/accountability-and-transparency/body-worn-camera-video-releases",
             als_json=False)
    uit = []
    for rij in re.findall(r"<tr>(.*?)</tr>", h, re.S):
        m = re.search(r'<th scope="row">([^<]+)</th>\s*<td>([^<]*)</td>\s*<td><a href="([^"]+)">([^<]+)</a>', rij)
        v = re.search(r"dvidshub\.net/video/embed/(\d+)", rij)
        if not m:
            continue
        try:
            datum = datetime.strptime(m.group(1).strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
        except ValueError:
            datum = m.group(1).strip()
        uit.append({"bron": "CBP (grenspolitie)", "titel": f"{schoon(m.group(4))} ({m.group(2).strip()})",
                    "datum": datum, "duur": "", "licentie": "Public domain (US federal government)",
                    "maker": "U.S. Customs and Border Protection",
                    "url": f"https://www.dvidshub.net/video/{v.group(1)}" if v else "https://www.cbp.gov" + m.group(3),
                    "extra": "persbericht: https://www.cbp.gov" + m.group(3)})
    uit.sort(key=lambda r: r["datum"], reverse=True)
    return uit[:n]  # CBP-lijst is klein: altijd alles tonen, zoekterm niet nodig


def zoek_dhs(q, n):
    alle = [t.lower() for t in termen(q)]
    q = alle[0]
    h = haal("https://www.dhs.gov/medialibrary/assets/videos?" + urllib.parse.urlencode({"search_api_fulltext": q}),
             als_json=False)
    uit, gezien = [], set()
    for m in re.finditer(r'href="(/medialibrary/assets/video/(\d+))"', h):
        if m.group(2) in gezien:
            continue
        gezien.add(m.group(2))
        t = schoon(h[m.end():m.end() + 600]).split(" - Video by")[0]
        duur = re.search(r"\((\d+:\d+(?::\d+)?)\)\s*$", t)
        uit.append({"bron": "DHS", "titel": re.sub(r"\s*\(\d+:\d+(?::\d+)?\)\s*$", "", t)[:150], "datum": "",
                    "duur": duur.group(1) if duur else "", "licentie": "Public domain (US federal government)",
                    "maker": "DHS", "url": "https://www.dhs.gov" + m.group(1)})
    # de DHS-zoekfunctie negeert de zoekterm soms: alleen titels met een zoekterm houden
    return [r for r in uit if any(t in r["titel"].lower() for t in alle)][:n]


def zoek_mixkit(q, n):
    q = termen(q)[0]
    slug = re.sub(r"[^a-z0-9]+", "-", q.lower()).strip("-")
    h = haal(f"https://mixkit.co/free-stock-video/{slug}/", als_json=False)
    uit = []
    for pad in dict.fromkeys(re.findall(r'href="(/free-stock-video/[a-z0-9-]+-\d+/)"', h)):
        naam = pad.split("/")[2].rsplit("-", 1)[0].replace("-", " ")
        uit.append({"bron": "Mixkit (stock)", "titel": naam, "datum": "", "duur": "",
                    "licentie": "Mixkit stock licence", "maker": "", "url": "https://mixkit.co" + pad})
    return uit[:n]


def zoek_dvids(q, n):
    q = termen(q)[0]
    key = os.environ.get("DVIDS_API_KEY")
    if not key:
        raise RuntimeError("geen DVIDS_API_KEY (gratis aanvragen: https://api.dvidshub.net/)")
    p = {"api_key": key, "type": "video", "q": q, "max_results": min(n, 50), "sort": "date", "sortdir": "desc"}
    d = haal("https://api.dvidshub.net/search?" + urllib.parse.urlencode(p))
    return [{"bron": "DVIDS", "titel": schoon(r.get("title")), "datum": (r.get("date_published") or r.get("date") or "")[:10],
             "duur": "", "licentie": "Public domain (US federal government, tenzij anders vermeld)",
             "maker": schoon(r.get("unit_name") or r.get("branch") or "")[:60], "url": r.get("url", "")}
            for r in d.get("results", [])]


def zoek_pexels(q, n):
    q = termen(q)[0]
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        raise RuntimeError("geen PEXELS_API_KEY (gratis: https://www.pexels.com/api/)")
    d = haal("https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": q, "per_page": min(n, 80)}),
             headers={"Authorization": key})
    return [{"bron": "Pexels (stock)", "titel": v["url"].rstrip("/").split("/")[-1].rsplit("-", 1)[0].replace("-", " "),
             "datum": "", "duur": f"{v['duration'] // 60}:{v['duration'] % 60:02d}", "licentie": "Pexels licence",
             "maker": v.get("user", {}).get("name", ""), "url": v["url"]} for v in d.get("videos", [])]


def zoek_pixabay(q, n):
    q = termen(q)[0]
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        raise RuntimeError("geen PIXABAY_API_KEY (gratis: https://pixabay.com/api/docs/)")
    p = {"key": key, "q": q, "order": "latest", "per_page": max(3, min(n, 200))}
    d = haal("https://pixabay.com/api/videos/?" + urllib.parse.urlencode(p))
    return [{"bron": "Pixabay (stock)", "titel": v.get("tags", ""), "datum": "",
             "duur": f"{v['duration'] // 60}:{v['duration'] % 60:02d}", "licentie": "Pixabay licence",
             "maker": v.get("user", ""), "url": v["pageURL"]} for v in d.get("hits", [])]


BRONNEN = {"overheid": zoek_overheid, "commons": zoek_commons, "archive": zoek_archive, "cbp": zoek_cbp, "dhs": zoek_dhs,
           "mixkit": zoek_mixkit, "dvids": zoek_dvids, "pexels": zoek_pexels, "pixabay": zoek_pixabay}

TIPS = """## Handmatig (scripts worden geblokkeerd of het zijn geen video's)
- **loc.gov/free-to-use** – vooral oude films en foto's (geschiedenis). Blokkeert scripts; zoek in de browser.
- **fbi.gov/news/videos** – FBI-video's zijn federaal (meestal public domain), maar soms zit er materiaal van derden in.
  De pagina werkt alleen in een browser.
- **bjs.ojp.gov/reuse-policy** – geen video's: cijfers en grafieken over misdaad en politie, vrij te gebruiken met
  bronvermelding. Handig voor uitleg in je video's.
- **DVIDS** zonder sleutel: dvidshub.net, zoek "body worn camera", filter Video.
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zoek", default="bodycam,body camera,body cam,body-worn,body worn,dashcam",
                    help="zoektermen, komma-gescheiden (standaard bodycam-termen)")
    ap.add_argument("--aantal", type=int, default=25, help="max. resultaten per bron")
    ap.add_argument("--bronnen", default=",".join(BRONNEN), help="komma-lijst: " + ",".join(BRONNEN))
    ap.add_argument("--sorteer", choices=["nieuw", "verhaal"], default="nieuw",
                    help="nieuw = nieuwste eerst; verhaal = beste kans op een goed verhaal eerst")
    ap.add_argument("--alles", action="store_true", help="ook video's tonen die je NIET mag gebruiken")
    ap.add_argument("--uit", default=str(MAP / "nieuwe-videos.md"))
    a = ap.parse_args()

    gezien_pad = MAP / "gezien.json"
    try:
        gezien = set(json.loads(gezien_pad.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        gezien = set()

    resultaten, meldingen = [], []
    for naam in [b.strip() for b in a.bronnen.split(",") if b.strip()]:
        f = BRONNEN.get(naam)
        if not f:
            meldingen.append(f"{naam}: onbekende bron")
            continue
        try:
            r = f(a.zoek, a.aantal)
            meldingen.append(f"{naam}: {len(r)} gevonden")
            resultaten += r
        except Exception as e:  # één kapotte bron mag de rest niet tegenhouden
            meldingen.append(f"{naam}: OVERGESLAGEN – {e}")
        print(meldingen[-1], file=sys.stderr)

    uniek = {}
    for r in resultaten:              # zelfde video uit twee Commons-zoekacties maar één keer
        uniek.setdefault(r["url"], r)
    resultaten = list(uniek.values())
    for r in resultaten:
        r["verhaal"] = verhaal_score(r)
        r["status"], r["uitleg"] = oordeel_licentie(r["licentie"])
        maker = schoon(r.get("maker", "")).lower()
        if ("Commons" in r["bron"] and r["status"] == "MAG" and "public domain" in r["uitleg"]
                and not any(k in maker for k in OVERHEID) and not any(k in maker for k in MEDIAKANALEN)):
            r["waarschuwing"] = ((r.get("waarschuwing") or "") + " maker lijkt geen overheid: check de bron").strip()
        if any(k in maker for k in MEDIAKANALEN):
            r["waarschuwing"] = ((r.get("waarschuwing") or "") + " bewerkt door mediakanaal (kans op Content ID-claim):"
                                 " zoek het origineel van het korps").strip()
        if r.get("waarschuwing"):
            r["uitleg"] += " – " + r["waarschuwing"]
            if r["status"] == "MAG":
                r["status"] = "LET OP"
        r["nieuw"] = r["url"] not in gezien
    if not a.alles:
        resultaten = [r for r in resultaten if r["status"] != "NIET"]
    resultaten.sort(key=lambda r: (r["nieuw"], r["datum"]), reverse=True)
    if a.sorteer == "verhaal":
        resultaten.sort(key=lambda r: (r["status"] == "MAG", r["verhaal"], r["datum"]), reverse=True)

    nu = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    regels = [f"# Vrije video's – zoekterm \"{a.zoek}\" ({nu})", "",
              f"{sum(r['nieuw'] for r in resultaten)} nieuw, {len(resultaten)} totaal. "
              "Altijd zelf de licentie op de bronpagina nakijken en een screenshot bewaren.", "",
              "Bronnen: " + "; ".join(meldingen), "",
              "| nieuw | mag? | verhaal | datum | duur | bron | titel | maker | licentie | link |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in resultaten:
        t = r["titel"].replace("|", "/")[:110]
        regels.append(f"| {'NIEUW' if r['nieuw'] else ''} | {r['status']} | {'*' * r['verhaal']} | {r['datum']} | {r['duur']} | {r['bron']} | "
                      f"{t} | {schoon(r.get('maker', '')).replace('|', '/')[:40]} | {r['uitleg']} | {r['url']} |")
    regels += ["", TIPS]
    Path(a.uit).write_text("\n".join(regels), encoding="utf-8")

    gezien_pad.write_text(json.dumps(sorted(gezien | {r["url"] for r in resultaten}), indent=0), encoding="utf-8")
    print(f"\n{sum(r['nieuw'] for r in resultaten)} nieuw / {len(resultaten)} bruikbaar -> {a.uit}")
    for r in [r for r in resultaten if r["nieuw"]][:15]:
        print(f"  [{r['status']}] {'*' * r['verhaal']:5} {r['datum'] or '----------'} {r['bron']}: {r['titel'][:80]}")


if __name__ == "__main__":
    main()
