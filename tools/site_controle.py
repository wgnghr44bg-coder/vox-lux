"""Sitecontrole (eigenaar 15 nov 2026: "zorg dat er altijd iemand is die de site controleert of alles klopt").

Elk half uur (Taakplanner "Sleep Archives sitecontrole", om :18 en :48, tussen de dashboard-updates in), op de pc,
kost niets. Haalt de echte website op (https://wgnghr44bg-coder.github.io/vox-lux/status/data.json) en vergelijkt die
met wat er werkelijk op de pc gebeurt:

  1. site bereikbaar en bijgewerkt (niet ouder dan 50 min), en de laatste update is ook echt online gekomen (push)
  2. per video: datum en status op de site = planning.txt
  3. "nu bezig" op de site = de keten die echt draait (tools/routine_lokaal.py); staat iets op bezig terwijl er al
     ruim een uur geen keten draait, dan is dat ook een fout
  4. "daarna" op de site = de volgorde van de bewaker (tools/keten_bewaker.py)
  5. YouTube: een geplande video staat privé met de juiste publicatiedatum (21:00 NL)
  6. een video die binnen 36 uur online moet en nog niet klaar is

Een probleem moet 2 rondes achter elkaar bestaan voordat het gemeld wordt (een update kan net tussendoor komen).
Melding: één regel "sitecontrole: NIET GOED: ..." in stories/ROUTINE-LOG.md (komt als fout op de site); is het weg,
dan "sitecontrole: opgelost: ...". Stand tussen rondes in C:\\Users\\rane\\site-controle.json.

  python tools/site_controle.py           # controleren en melden
  python tools/site_controle.py --droog   # alleen laten zien
"""
import datetime as dt, json, re, subprocess, sys, time
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
LOG = STORIES / "ROUTINE-LOG.md"
LOKAAL = REPO / "docs" / "status" / "data.json"
URL = "https://wgnghr44bg-coder.github.io/vox-lux/status/data.json"
STAND = Path.home() / "site-controle.json"
NL = ZoneInfo("Europe/Amsterdam")
sys.path.insert(0, str(HIER))


def log(t):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} sitecontrole: {t}\n")


def tijd(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M")


def ketens():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'routine_lokaal' -and $_.Name -match 'python' } "
                          "| % { $_.CommandLine }"], capture_output=True, text=True, timeout=90).stdout
    return [r for r in out.splitlines() if r.strip()]


def planningen():
    uit = {}
    for p in STORIES.glob("*/planning.txt"):
        if p.parent.name.startswith("_"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        g = lambda k: (re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1].strip()
        d = re.search(r"(\d{4}-\d{2}-\d{2})", g("datum"))
        link = re.search(r"https://youtu\.be/([A-Za-z0-9_-]{11})", t)
        uit[p.parent.name] = {"datum": d.group(1) if d and "reserve" not in g("datum") else "",
                              "status": g("status") or ("klaar" if link else ""), "id": link.group(1) if link else "",
                              "gewijzigd": dt.datetime.fromtimestamp(p.stat().st_mtime)}
    return uit


def controleer():
    nu = dt.datetime.now()
    p = []                                                           # (sleutel, tekst)
    try:
        r = requests.get(URL, params={"t": int(time.time())}, timeout=30)
        r.raise_for_status()
        site = r.json()
    except Exception as e:
        return [("onbereikbaar", f"website niet bereikbaar of kapot ({type(e).__name__})")]

    bij = tijd(site["bijgewerkt"])
    if nu - bij > dt.timedelta(minutes=50):
        p.append(("oud", f"website is sinds {site['bijgewerkt']} niet bijgewerkt (taak 'Sleep Archives dashboard' kijken)"))
    try:
        lok = json.loads(LOKAAL.read_text(encoding="utf-8"))["bijgewerkt"]
        if tijd(lok) - bij > dt.timedelta(minutes=40):
            p.append(("push", f"update van {lok} staat niet online (site toont {site['bijgewerkt']}); pushen naar GitHub lukt niet"))
    except Exception:
        pass

    # 2. video's: datum en status
    plan = planningen()
    opsite = {v["map"]: v for v in site.get("video", [])}
    vandaag = nu.date().isoformat()
    for m, pl in plan.items():
        if pl["gewijzigd"] > bij:                                    # na de laatste update veranderd: volgende ronde
            continue
        v = opsite.get(m)
        if not v:
            if pl["datum"] and pl["datum"] >= vandaag:
                p.append((f"mist:{m}", f"{m} ({pl['datum']}) staat niet op de site"))
            continue
        if v["datum"] != pl["datum"]:
            p.append((f"datum:{m}", f"{m}: site zegt datum {v['datum'] or 'geen'}, planning zegt {pl['datum'] or 'geen'}"))
        if pl["status"][:140] != v["status"]:
            p.append((f"status:{m}", f"{m}: site zegt '{v['status'][:50]}', planning zegt '{pl['status'][:50]}'"))

    # 3. nu bezig
    draait = ketens()
    huidig = (site.get("huidig") or {}).get("map", "")
    st = laad()
    if draait:
        st.pop("geen_keten_sinds", None)
        if huidig and not plan.get(huidig, {}).get("status", "").startswith("bezig"):
            p.append((f"huidig:{huidig}", f"site zegt dat {huidig} nu gemaakt wordt, maar die staat niet op bezig"))
        if not huidig and nu - bij < dt.timedelta(minutes=50):
            p.append(("huidig:leeg", "er draait een keten, maar de site zegt dat er niets gemaakt wordt"))
    else:
        st.setdefault("geen_keten_sinds", nu.strftime("%Y-%m-%d %H:%M"))
        if huidig and bij > tijd(st["geen_keten_sinds"]):
            p.append((f"huidig:{huidig}", f"site zegt dat {huidig} nu gemaakt wordt, maar er draait geen keten"))
        if nu - tijd(st["geen_keten_sinds"]) > dt.timedelta(minutes=75):
            bezig = [m for m, pl in plan.items() if pl["status"].startswith("bezig") and pl["datum"] >= vandaag]
            if bezig:
                p.append(("stil", f"al ruim een uur draait er geen keten, terwijl {', '.join(sorted(bezig))} op bezig staat "
                                  "(taak 'Sleep Archives bewaker' kijken)"))
    bewaar_stand(st)

    # 4. daarna = volgorde van de bewaker
    try:
        from keten_bewaker import te_maken
        lijst, _ = te_maken(nu.date())
        wp = site.get("werkplanning") or {}
        getoond = [x.get("map") for x in wp.get("nu", []) + wp.get("daarna", [])]
        weg = [m for m in lijst if m not in getoond and plan.get(m, {}).get("gewijzigd", nu) <= bij]
        if weg:
            p.append(("daarna", f"de keten maakt nog {', '.join(weg)}, maar dat staat niet bij 'daarna' op de site"))
    except Exception as e:
        p.append(("daarna-kapot", f"volgorde van de bewaker niet te lezen ({type(e).__name__})"))

    # 5. YouTube
    recent = {r["id"]: r for r in (site.get("kanaal") or {}).get("recent", [])}
    for m, pl in plan.items():
        if not (pl["id"] and pl["datum"] and pl["status"].startswith("klaar") and pl["datum"] >= vandaag):
            continue
        r = recent.get(pl["id"])
        if not r:
            continue                                                 # niet in de lijst van recente video's: niet te zien
        if r.get("publiceer"):
            pub = dt.datetime.fromisoformat(r["publiceer"].replace("Z", "+00:00")).astimezone(NL)
            if pub.date().isoformat() != pl["datum"] or pub.hour != 21:
                p.append((f"yt:{m}", f"{m}: YouTube publiceert op {pub:%Y-%m-%d %H:%M}, planning zegt {pl['datum']} 21:00"))
        elif r.get("privacy") != "public":
            p.append((f"yt:{m}", f"{m}: staat op YouTube zonder publicatiedatum ({r.get('privacy')})"))

    # 6. bijna online maar niet klaar
    for m, pl in plan.items():
        if pl["datum"] and not pl["status"].startswith("klaar"):
            uur = (dt.datetime.fromisoformat(pl["datum"] + " 21:00") - nu).total_seconds() / 3600
            if 0 < uur < 36:
                p.append((f"laat:{m}", f"{m} moet over {uur:.0f} uur online, maar is nog niet klaar ({pl['status'][:40]})"))
    return p


def laad():
    try:
        return json.loads(STAND.read_text(encoding="utf-8"))
    except Exception:
        return {}


def bewaar_stand(st):
    oud = laad()
    oud.update(st)
    if "geen_keten_sinds" not in st:
        oud.pop("geen_keten_sinds", None)
    STAND.write_text(json.dumps(oud, indent=1, ensure_ascii=False), encoding="utf-8")


def main():
    droog = "--droog" in sys.argv
    problemen = dict(controleer())
    st = laad()
    vorige = st.get("vorige", {})                                    # sleutel -> tekst, gezien in de vorige ronde
    gemeld = st.get("gemeld", {})                                    # sleutel -> tekst, al in het logboek
    for k, t in problemen.items():
        print("NIET GOED:" if k in vorige else "verdacht: ", t)
    if not problemen:
        print("alles klopt")
    if droog:
        return
    for k, t in problemen.items():
        if k in vorige and k not in gemeld:
            log(f"NIET GOED: {t}")
            gemeld[k] = t
    for k in [k for k in gemeld if k not in problemen]:
        log(f"opgelost: {gemeld.pop(k)}")
    st = laad()
    st.update({"vorige": problemen, "gemeld": gemeld, "laatste": dt.datetime.now().strftime("%Y-%m-%d %H:%M")})
    STAND.write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
