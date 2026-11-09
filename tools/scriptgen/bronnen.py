"""Bronnen voor de scriptgenerator zonder Claude (eigenaar 9 nov 2026: "kun je geen andere bronnen gebruiken", "je kan
toch de tekst van YouTube gebruiken als informatie en dan je eigen versie maken").

- ombouwen: ALLEEN het oude script (al door Claude geschreven en gecontroleerd); vrij zoeken gaf Soedan/Maersk bij Gettysburg
- nieuw: gerichte Wikipedia (hoofdartikel + artikelen waar het zelf naar linkt, gefilterd), rechtenvrije boeken
  (Internet Archive, Project Gutenberg) en YouTube-transcripties van grote video's over het onderwerp
- YouTube: alleen als bron van FEITEN; een feit uit YouTube telt pas als een tweede bron het bevestigt (generator.py),
  en het script wordt vergeleken met de transcripties (kopieercontrole), zodat er niets letterlijk wordt overgenomen
Alles komt in <map>/bronnen/ zodat na te gaan is waar elk feit vandaan komt. Elk stuk bron wordt eerst gekeurd:
gaat het over deze plaats en deze tijd?
"""
import json, re, subprocess, sys, time
from pathlib import Path

import requests

API = "https://en.wikipedia.org/w/api.php"
KOP = {"User-Agent": "SleepArchivesScriptgen/2.0 (local research tool)"}
HIER = Path(__file__).resolve().parent


def _get(url, params=None, json_ok=True, timeout=60):
    for poging in range(4):
        time.sleep(1.2)
        try:
            r = requests.get(url, params=params, headers=KOP, timeout=timeout)
            if r.status_code == 200:
                return r.json() if json_ok else r.text
        except Exception:
            pass
        time.sleep(10 * (poging + 1))
    return {} if json_ok else ""


# ---------- Wikipedia, gericht ----------
def wiki_zoek(term, n=3):
    r = _get(API, {"action": "query", "list": "search", "srsearch": term, "srlimit": n, "format": "json"})
    return [x["title"] for x in r.get("query", {}).get("search", [])]


def wiki_tekst(titel):
    r = _get(API, {"action": "query", "prop": "extracts", "explaintext": 1, "titles": titel, "redirects": 1, "format": "json"})
    for p in r.get("query", {}).get("pages", {}).values():
        t = p.get("extract", "")
        return re.split(r"\n== (See also|References|Notes|Further reading|External links|Bibliography|Sources) ==", t)[0].strip()
    return ""


def wiki_links(titel, n=200):
    r = _get(API, {"action": "query", "prop": "links", "titles": titel, "pllimit": n, "plnamespace": 0, "redirects": 1, "format": "json"})
    uit = []
    for p in r.get("query", {}).get("pages", {}).values():
        uit += [l["title"] for l in p.get("links", [])]
    return uit


# ---------- rechtenvrije boeken ----------
def archive_boeken(term, jaar_tot=1925, n=3):
    q = f'title:({term}) AND mediatype:texts AND date:[1700-01-01 TO {jaar_tot}-12-31] AND NOT title:(times OR compiler OR star OR gazette)'
    r = _get("https://archive.org/advancedsearch.php", {"q": q, "fl[]": ["identifier", "title"], "rows": n * 3,
                                                          "sort[]": "downloads desc", "output": "json"})
    uit = []
    for d in r.get("response", {}).get("docs", [])[:n * 3]:
        t = _get(f"https://archive.org/download/{d['identifier']}/{d['identifier']}_djvu.txt", json_ok=False, timeout=120)
        if t and len(t) > 20000:
            uit.append((f"Boek: {d.get('title', d['identifier'])[:80]}", t[:400000]))
        if len(uit) >= n:
            break
    return uit


def gutenberg_boeken(term, n=2):
    r = _get("https://gutendex.com/books", {"search": term}, timeout=90)
    uit = []
    for b in r.get("results", [])[:n * 2]:
        url = next((v for k, v in b.get("formats", {}).items() if k.startswith("text/plain")), None)
        if url:
            t = _get(url, json_ok=False, timeout=120)
            if t and len(t) > 20000:
                uit.append((f"Boek: {b['title'][:80]}", t[:400000]))
        if len(uit) >= n:
            break
    return uit


# ---------- YouTube (alleen feiten, met dubbele controle in generator.py) ----------
def youtube_teksten(onderwerp, map_, n=4):
    """Transcripties van de meest bekeken slaap-/geschiedenisvideo's over het onderwerp (YouTube Data API, alleen lezen)."""
    try:
        sys.path.insert(0, str(HIER.parent))
        import youtube_upload as yu
        h = {"Authorization": "Bearer " + yu.access_token()}
        r = requests.get("https://www.googleapis.com/youtube/v3/search", headers=h, timeout=30, params={
            "part": "snippet", "q": f"{onderwerp} history for sleep", "type": "video", "order": "viewCount",
            "videoDuration": "long", "maxResults": n * 2, "relevanceLanguage": "en"}).json()
        ids = [i["id"]["videoId"] for i in r.get("items", [])]
    except Exception as e:
        print("  YouTube zoeken lukte niet:", e, flush=True)
        return []
    uit, d = [], Path(map_) / "bronnen" / "youtube"
    d.mkdir(parents=True, exist_ok=True)
    for vid in ids:
        if len(uit) >= n:
            break
        subprocess.run([sys.executable, "-m", "yt_dlp", "--skip-download", "--write-auto-subs", "--write-subs",
                        "--sub-langs", "en.*", "--sub-format", "vtt", "-o", str(d / f"{vid}.%(ext)s"),
                        f"https://www.youtube.com/watch?v={vid}"], capture_output=True, timeout=300)
        vtt = next(iter(sorted(d.glob(f"{vid}*.vtt"))), None)
        if not vtt:
            continue
        regels, vorige = [], ""
        for r_ in vtt.read_text(encoding="utf-8", errors="replace").splitlines():
            r_ = re.sub(r"<[^>]+>", "", r_).strip()
            if not r_ or "-->" in r_ or r_.startswith(("WEBVTT", "Kind:", "Language:")) or r_ == vorige:
                continue
            regels.append(r_)
            vorige = r_
        tekst = " ".join(regels)
        if len(tekst.split()) > 3000:
            (d / f"{vid}.txt").write_text(tekst, encoding="utf-8")
            uit.append((f"YouTube {vid}", tekst))
    return uit


# ---------- alles samen ----------
def stukken(teksten, woorden=900):
    uit = []
    for titel, tekst in teksten.items():
        w = tekst.split()
        for i in range(0, len(w), woorden):
            uit.append({"id": len(uit), "bron": titel, "youtube": titel.startswith("YouTube"), "tekst": " ".join(w[i:i + woorden])})
    return uit


def relevant(stukjes, onderwerp, llm):
    """Laat alleen stukken door die over deze plaats en tijd gaan (oude script en hoofdartikel altijd)."""
    uit = []
    for s in stukjes:
        if s["bron"] == "Old script":
            uit.append(s)
            continue
        r = llm.json_vraag(f"Video topic: {onderwerp}.\nText:\n{s['tekst'][:3500]}\n\nIs this text mainly about this topic "
                           "(the same place and the same period, its people, daily life and events)? Answer false for other "
                           "countries, other wars, other centuries, adverts, indexes or garbled OCR.\n"
                           'JSON: {"relevant": true or false}', temp=0.0, max_tokens=30)
        if isinstance(r, dict) and r.get("relevant") is True:
            uit.append(s)
    return uit


def verzamel(map_, onderwerp, llm, oud=""):
    d = Path(map_) / "bronnen"
    d.mkdir(exist_ok=True)
    if oud:                                                  # ombouwen: alleen het oude script
        return {"Old script": oud}
    teksten = {}
    plek = re.split(r"[,:(]", onderwerp)[0].replace("Life in", "").replace("Life on", "").replace("Life Aboard", "").strip()
    hoofd = (wiki_zoek(onderwerp, 1) or wiki_zoek(plek, 1) or [None])[0]
    if hoofd:
        teksten[f"Wikipedia: {hoofd}"] = wiki_tekst(hoofd)
        links = wiki_links(hoofd)
        kies = llm.json_vraag(f"Video topic: {onderwerp}.\nWikipedia articles linked from '{hoofd}':\n{links[:200]}\n\nChoose "
                              "up to 8 titles that are directly about this place and period (daily life, key people, events, "
                              "buildings, what remains today). No other wars, countries or modern topics.\n"
                              'JSON: ["...", ...]', temp=0.1, max_tokens=300)
        for t in [x for x in kies if isinstance(x, str) and x in links][:8]:
            tekst = wiki_tekst(t)
            if len(tekst.split()) > 300:
                teksten[f"Wikipedia: {t}"] = tekst
    for titel, tekst in archive_boeken(plek) + gutenberg_boeken(plek):
        teksten[titel] = tekst
    for titel, tekst in youtube_teksten(onderwerp, map_):
        teksten[titel] = tekst
    for t, tekst in teksten.items():
        (d / (re.sub(r"[^A-Za-z0-9]+", "_", t)[:70] + ".txt")).write_text(tekst, encoding="utf-8")
    return teksten


def kopieer_overlap(tekst, bronteksten, n=8):
    """Stukken van n woorden die letterlijk in een YouTube-transcriptie staan (kopieercontrole)."""
    norm = lambda s: re.sub(r"[^a-z0-9 ]", "", s.lower()).split()
    grams = set()
    for b in bronteksten:
        w = norm(b)
        grams |= {" ".join(w[i:i + n]) for i in range(len(w) - n + 1)}
    w = norm(tekst)
    return [" ".join(w[i:i + n]) for i in range(len(w) - n + 1) if " ".join(w[i:i + n]) in grams]
