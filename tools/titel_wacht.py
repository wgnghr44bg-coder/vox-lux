"""Titelwachter, onderdeel van de hype-wachter (eigenaar 15 nov 2026: "hype wachter zorgt dat elke titel goed gekozen
is"; "je mag de hype wachter altijd verbeteren").

Elke 2 uur (Taakplanner "Sleep Archives titels") op de pc, kost niets (lokaal model, geen extra YouTube-quota):
  1. regels (stories/AFSPRAKEN.md, "Titel"): elke video met een datum in de komende 6 weken. Fout = meteen melden,
     niet pas als de keten eraan begint (die stopt dan op afspraken_check).
  2. vergelijken met wat nu werkt: titels van de grote slaapkanalen over hetzelfde onderwerp (stories/concurrent.json,
     elke ochtend door tools/hype_wacht.py opgehaald) + onze eigen cijfers (views na een week, stories/titel-cijfers.json;
     CTR geeft de YouTube-API niet). Het lokale model stelt een betere titel voor als die er is; elke titel hooguit één
     keer per week, en niet als de grafische kaart bezet is (beelden, stem, beeldcontrole).
  3. YouTube: staat een geplande/online video met een andere titel op YouTube dan in planning.txt, of breekt die titel
     de regels (bv. een vraag), dan een seintje (titel aanpassen in Studio kost geen views).
Uitkomst: stories/titels.json (website, kaart "Titels") en seintjes in stories/ROUTINE-LOG.md (één keer per voorstel).
Titels aanpassen doet de eigenaar of Claude op zijn verzoek; dit programma verandert zelf niets aan planning.txt.

  python tools/titel_wacht.py                 # bijwerken
  python tools/titel_wacht.py --zonder-model  # alleen regels en YouTube
  python tools/titel_wacht.py --opnieuw       # model ook voor titels die deze week al bekeken zijn
"""
import datetime as dt, json, re, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
UIT = STORIES / "titels.json"
CONC = STORIES / "concurrent.json"
CIJFERS = STORIES / "titel-cijfers.json"
DATA = REPO / "docs" / "status" / "data.json"
VOORUIT = 42
STAART = " | History for Sleep"
sys.path.insert(0, str(HIER))
sys.path.insert(0, str(HIER / "scriptgen"))
from hype_wacht import woorden  # noqa: E402

GOEDE_VOORBEELDEN = ["Life Aboard the Mayflower, 1620", "Life on the Oregon Trail, 1846", "How Vikings Survived the Long Dark Winter",
                     "Life Aboard the Titanic, April 1912", "Life in Gettysburg, July 1863"]


def log(t):
    with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} hype-wachter: {t}\n")


def regels(titel):
    """Fouten (afspraak gebroken) en let-op-punten van een volledige titel."""
    fout, let = [], []
    if not titel.endswith(STAART):
        fout.append("eindigt niet op '| History for Sleep'")
    kern = titel.split(" | ")[0].strip()
    if "?" in kern:
        fout.append("is een vraag")
    if re.search(r"<N>|\bhours?\b", kern, re.I):
        fout.append("noemt uren of <N>")
    namen = [w for w in re.findall(r"\b[A-Z][a-z'’]+\b", kern)[1:] if w not in ("The", "A", "An", "Of", "In", "On", "And")]
    if not re.search(r"\d|\bBC\b|\bAD\b", kern) and not namen:
        fout.append("niet concreet (geen plaats, naam of jaartal)")
    if len(titel) > 80:
        let.append(f"lang ({len(titel)} tekens; op de telefoon valt het eind weg)")
    return fout, let


def planning():
    uit = []
    for p in STORIES.glob("*/planning.txt"):
        if p.parent.name.startswith("_"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        g = lambda k: (re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1].strip()
        d = re.search(r"(\d{4}-\d{2}-\d{2})", g("datum"))
        if not d or "reserve" in g("datum"):
            continue
        titel = re.sub(r"\s*\((eigenaar|was|hype|\d{1,2} nov).*$", "", g("titel")).strip()
        link = re.search(r"https://youtu\.be/([A-Za-z0-9_-]{11})", t)
        uit.append({"map": p.parent.name, "datum": d.group(1), "titel": titel, "status": g("status"),
                    "onderwerp": g("onderwerp"), "id": link.group(1) if link else ""})
    return sorted(uit, key=lambda v: v["datum"])


def cijfers_bijwerken():
    """Views van onze video's na ± een week (de API geeft geen CTR; views in week 1 zijn de beste vervanging)."""
    oud = json.loads(CIJFERS.read_text(encoding="utf-8")) if CIJFERS.exists() else {}
    try:
        recent = json.loads(DATA.read_text(encoding="utf-8"))["kanaal"]["recent"]
    except Exception:
        return oud
    nu = dt.datetime.now(dt.timezone.utc)
    for r in recent:
        pub = r.get("publiceer") or ""
        if not pub or r.get("privacy") == "private" or r["id"] in oud:
            continue
        dagen = (nu - dt.datetime.fromisoformat(pub.replace("Z", "+00:00"))).total_seconds() / 86400
        if 7 <= dagen <= 10:
            oud[r["id"]] = {"titel": r["titel"], "publiceer": pub[:10], "views_week1": r["views"]}
    CIJFERS.write_text(json.dumps(oud, indent=1, ensure_ascii=False), encoding="utf-8")
    return oud


def verwant(v, conc):
    w = woorden(" ".join([v["titel"].split(" | ")[0], v["onderwerp"], v["map"].replace("-", " ")]))
    w -= {"christmas"} if "christmas" not in v["titel"].lower() else set()
    rij = [c for c in conc if w & woorden(c["titel"])]
    return sorted(rij, key=lambda c: -c["per_dag"])[:6]


def gpu_bezet():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.Name -match 'python' -and $_.CommandLine -match "
                          "'comfy_batch|engine_stem|beeldcheck|thumbnail_v3|check_stem_tekst' } | % { $_.ProcessId }"],
                         capture_output=True, text=True, timeout=90).stdout
    return bool(out.strip())


def voorstel(v, rij, cijfers):
    import llm
    eigen = sorted(cijfers.values(), key=lambda c: -c["views_week1"])
    eigen_t = "\n".join(f"- {c['titel']} ({c['views_week1']} views in week 1)" for c in eigen[:4] + eigen[-2:]) or "- (nog geen)"
    conc_t = "\n".join(f"- {c['titel']} ({c['kanaal']}, {c['per_dag']:,} views/day)" for c in rij) or "- (none on this topic right now)"
    vraag = f"""You choose YouTube titles for "Sleep Archives", a calm history channel for falling asleep.
Our video: {v['onderwerp'] or v['titel']}
Current title: {v['titel']}

Our rules (from real click-through data: concrete titles 4.8-7.4%, question titles 0.7-2.5%):
- concrete, with a place and/or a year; never a question; no hours; always ends with "{STAART.strip()}"
- forms that work for us: "Life in <place>, <year>", "Life Aboard <ship>, <year>", "How <people> Survived <thing>", "<Event>, <year>"
- the title must promise what the video is about (the first chapter delivers it); max 80 characters in total
- good examples: {"; ".join(GOEDE_VOORBEELDEN)}

Our own videos, views in the first week:
{eigen_t}

Titles on this topic that grow fast at big sleep channels right now:
{conc_t}

Is there a clearly better title that follows ALL our rules and uses the words people click on now (a famous name,
a place, a year)? Only propose one if it is clearly better; otherwise keep the current one.
JSON: {{"beter": true/false, "titel": "<full title ending with {STAART.strip()}>", "waarom": "<max 15 words, in Dutch>"}}"""
    a = llm.json_vraag(vraag, temp=0.3, max_tokens=300, ctx=4096)
    t = " ".join(str(a.get("titel", "")).split())
    if t and not t.endswith(STAART):
        t = t.split(" | ")[0].rstrip() + STAART
    if not a.get("beter") or not t or t.lower() == v["titel"].lower() or regels(t)[0] or regels(t)[1]:
        return "", ""
    # lidwoord vergeten ("Life in Ice Age Cave"): het model keurde dat zelf goed, dus een vaste regel
    if re.search(r"\b(in|on|at|inside|aboard|from)\s+(?!The\b|A\b|An\b)[A-Z]\w+\s+[A-Z]\w+\s+[A-Z]\w+\b", t.split(" | ")[0]):
        return "", ""
    # 15 nov, eerste ronde: het model stelde vaak slechtere titels voor ("Life in America, 1933" zonder Great
    # Depression; Thanksgiving zonder het woord Thanksgiving vlak voor Thanksgiving). Daarom een tweede, strenge
    # beoordeling: beide titels naast elkaar, twee keer met de volgorde omgedraaid; alleen als het voorstel beide keren wint.
    taal = llm.json_vraag(f"""Is this a natural, grammatically correct English YouTube title, the way a native speaker
would write it (articles like "a"/"an"/"the" where needed)? Title: {t.split(' | ')[0]}
JSON: {{"correct": true or false}}""", temp=0.0, max_tokens=30, ctx=1024)
    if taal.get("correct") is not True:
        return "", ""
    for eerst, dan in ((v["titel"], t), (t, v["titel"])):
        oordeel = llm.json_vraag(
            f"""Two YouTube titles for the same calm history video for falling asleep ({v['onderwerp'] or v['titel']}).
A: {eerst}
B: {dan}
Which one would more people click on? Judge strictly: the best title keeps the most famous, searched-for words
(names like Thanksgiving, Great Depression, Blackbeard, Pirate, Titanic), is natural correct English, concrete
(place and/or year), and promises exactly what the video is about. If they are about equally good, answer "gelijk".
JSON: {{"beste": "A" or "B" or "gelijk"}}""", temp=0.0, max_tokens=40, ctx=2048)
        winnaar = str(oordeel.get("beste", "")).strip().upper()[:1]
        if (winnaar == "A" and eerst != t) or (winnaar == "B" and dan != t) or winnaar not in "AB":
            return "", ""
    return t, str(a.get("waarom", ""))[:120]


def main():
    import msvcrt                                           # 15 nov: nooit twee rondes tegelijk (dubbele seintjes)
    slot = open(Path.home() / "titel-wacht.slot", "a+")
    try:
        msvcrt.locking(slot.fileno(), msvcrt.LK_NBLCK, 1)
    except OSError:
        print("titelwachter draait al")
        return
    vandaag = dt.date.today()
    zonder = "--zonder-model" in sys.argv
    oud = {x["map"]: x for x in json.loads(UIT.read_text(encoding="utf-8")).get("titels", [])} if UIT.exists() else {}
    conc = json.loads(CONC.read_text(encoding="utf-8")).get("videos", []) if CONC.exists() else []
    cijfers = cijfers_bijwerken()
    yt = {}
    try:
        yt = {r["id"]: r for r in json.loads(DATA.read_text(encoding="utf-8"))["kanaal"]["recent"]}
    except Exception:
        pass
    log_t = (STORIES / "ROUTINE-LOG.md").read_text(encoding="utf-8", errors="replace")
    model_mag = not zonder and not gpu_bezet()
    gevraagd = 0
    rijen = []
    for v in planning():
        d = dt.date.fromisoformat(v["datum"])
        if d < vandaag - dt.timedelta(days=14) or d > vandaag + dt.timedelta(days=VOORUIT):
            continue
        fout, let = regels(v["titel"])
        r = {"map": v["map"], "datum": v["datum"], "titel": v["titel"], "fouten": fout, "let_op": let,
             "voorstel": "", "waarom": "", "youtube": "", "concurrent": [], "bekeken": ""}
        # YouTube: geplande of online video met een andere of foute titel
        if v["id"] and v["id"] in yt:
            ytt = yt[v["id"]]["titel"]
            if ytt.strip() != v["titel"].strip():
                r["youtube"] = f"op YouTube staat '{ytt}'"
            yfout = regels(ytt)[0]
            if yfout:
                r["youtube"] = (r["youtube"] + "; " if r["youtube"] else f"op YouTube: '{ytt}' ") + ", ".join(yfout)
        # voorstel van het model (alleen voor video's die nog niet klaar/geüpload zijn; daarvoor is het seintje
        # hierboven over YouTube genoeg)
        if d >= vandaag and not v["status"].startswith("klaar"):
            rij = verwant(v, conc)
            r["concurrent"] = [{"titel": c["titel"], "kanaal": c["kanaal"], "per_dag": c["per_dag"]} for c in rij[:3]]
            o = oud.get(v["map"], {})
            vers = (o.get("titel") == v["titel"] and o.get("bekeken", "") >= (vandaag - dt.timedelta(days=7)).isoformat()
                    and "--opnieuw" not in sys.argv)
            if vers:
                r.update({k: o.get(k, "") for k in ("voorstel", "waarom", "bekeken")})
            elif model_mag and gevraagd < 8:
                try:
                    r["voorstel"], r["waarom"] = voorstel(v, rij, cijfers)
                    r["bekeken"] = vandaag.isoformat()
                    gevraagd += 1
                except Exception as e:
                    print("model:", e)
        rijen.append(r)
        # seintjes, elk één keer
        for f in r["fouten"]:
            s = f"TITEL FOUT {v['map']} ({v['datum']}): '{v['titel']}' {f}"
            if s not in log_t:
                log(s)
        if r["youtube"]:
            s = f"SEINTJE TITEL YouTube {v['map']}: {r['youtube']}"
            if s not in log_t:
                log(s + " (aanpassen in Studio kost geen views)")
        if r["voorstel"]:
            s = f"SEINTJE TITEL {v['map']} ({v['datum']}): '{v['titel']}' -> voorstel '{r['voorstel']}'"
            if s not in log_t:
                log(s + f" ({r['waarom']})")
    if gevraagd:
        try:                                                # model meteen uit het geheugen (de keten heeft de kaart nodig)
            import llm, requests
            requests.post("http://127.0.0.1:11434/api/generate", json={"model": llm.MODEL, "keep_alive": 0}, timeout=30)
        except Exception:
            pass
    UIT.write_text(json.dumps({"bijgewerkt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "titels": rijen,
                               "model": "gebruikt" if gevraagd else ("overgeslagen: kaart bezet" if not zonder and not model_mag else "niet nodig")},
                              indent=1, ensure_ascii=False), encoding="utf-8")
    for r in rijen:
        st = "FOUT " + ", ".join(r["fouten"]) if r["fouten"] else ("voorstel: " + r["voorstel"] if r["voorstel"] else "goed")
        print(f"{r['datum']} {r['map']}: {r['titel']} -> {st}" + (f" | YT: {r['youtube']}" if r["youtube"] else ""))


if __name__ == "__main__":
    main()
