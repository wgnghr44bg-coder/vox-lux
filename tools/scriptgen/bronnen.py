"""Bronnen voor de feiten: Engelse Wikipedia (gratis, alleen lezen) en, bij ombouwen, het oude script.
Alles komt in <map>/bronnen/ zodat later na te gaan is waar elk feit vandaan komt."""
import re
from pathlib import Path

import requests

API = "https://en.wikipedia.org/w/api.php"
KOP = {"User-Agent": "SleepArchivesScriptgen/1.0 (local research tool)"}


def _get(params):
    """Rustig vragen (Wikipedia weigert te snelle vragen); bij een fout wachten en opnieuw, anders leeg."""
    import time
    for poging in range(5):
        time.sleep(1.5)
        try:
            r = requests.get(API, params=params, headers=KOP, timeout=60)
            if r.status_code == 200 and "json" in r.headers.get("content-type", ""):
                return r.json()
        except Exception:
            pass
        time.sleep(15 * (poging + 1))
    return {}


def zoek(term, n=3):
    r = _get({"action": "query", "list": "search", "srsearch": term, "srlimit": n, "format": "json"})
    return [x["title"] for x in r.get("query", {}).get("search", [])]


def artikel(titel):
    r = _get({"action": "query", "prop": "extracts", "explaintext": 1, "titles": titel, "redirects": 1, "format": "json"})
    for p in r.get("query", {}).get("pages", {}).values():
        t = p.get("extract", "")
        t = re.split(r"\n== (See also|References|Notes|Further reading|External links|Bibliography|Sources) ==", t)[0]
        return t.strip()
    return ""


def verzamel(map_, onderwerp, zoektermen, max_artikelen=14):
    """Zoek artikelen bij het onderwerp en de door het model voorgestelde zoektermen; bewaar ze."""
    d = Path(map_) / "bronnen"
    d.mkdir(exist_ok=True)
    titels = []
    for term in [onderwerp] + list(zoektermen):
        for t in zoek(term, 2):
            if t not in titels:
                titels.append(t)
        if len(titels) >= max_artikelen:
            break
    teksten = {}
    for t in titels[:max_artikelen]:
        tekst = artikel(t)
        if len(tekst.split()) > 300:
            teksten[t] = tekst
            (d / (re.sub(r"[^A-Za-z0-9]+", "_", t)[:60] + ".txt")).write_text(tekst, encoding="utf-8")
    return teksten


def stukken(teksten, woorden=900):
    """Knip bronnen in stukken van ± 900 woorden (past ruim in het model), elk met een id."""
    uit = []
    for titel, tekst in teksten.items():
        w = tekst.split()
        for i in range(0, len(w), woorden):
            uit.append({"id": len(uit), "bron": titel, "tekst": " ".join(w[i:i + woorden])})
    return uit
