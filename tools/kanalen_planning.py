"""Planning van alle drie kanalen voor de website (eigenaar 19 nov 2026: "ik wil duidelijk zien wat elke week nu en
week later de planning is").

Bronnen:
  - Sleep Archives: stories/*/planning.txt (de lijst `video` uit dashboard_bijwerken.planning()).
  - NOIRTRACES en BlackswanVault: kanalen/PLANNING-KANALEN.json (met de hand of door Claude bijgehouden).
  - YouTube (alleen lezen) van NOIRTRACES en BlackswanVault: wat al online of gepland staat, ook als het niet in de json staat.

  python tools/kanalen_planning.py        # laat de twee weken zien (zonder Sleep-planning uit het dashboard)
"""
import datetime as dt, json, os, re
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

REPO = Path(__file__).resolve().parent.parent
BESTAND = REPO / "kanalen" / "PLANNING-KANALEN.json"
NL = ZoneInfo("Europe/Amsterdam")
SLEEP_STAND = {"online": "online", "gepland": "gepland", "bezig": "wordt gemaakt",
               "script nieuw": "script klaar", "script oud": "script moet om"}


def _token(refresh):
    r = requests.post("https://oauth2.googleapis.com/token", timeout=60, data={
        "client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
        "refresh_token": refresh, "grant_type": "refresh_token"})
    r.raise_for_status()
    return r.json()["access_token"]


def _youtube(kanaal):
    """Video's van een kanaal: id, titel, stand (online/gepland/prive), NL-datum en tijd."""
    if kanaal == "BlackswanVault":
        refresh = os.environ.get("YT_WHATIF_REFRESH_TOKEN")
    else:
        p = Path.home() / ".yt-altena.json"
        refresh = json.loads(p.read_text())["refresh_token"] if p.exists() else None
    if not refresh:
        return []
    h = {"Authorization": "Bearer " + _token(refresh)}
    api = "https://www.googleapis.com/youtube/v3/"
    up = requests.get(api + "channels", headers=h, timeout=60,
                      params={"part": "contentDetails", "mine": "true"}).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = [i["contentDetails"]["videoId"] for i in requests.get(api + "playlistItems", headers=h, timeout=60, params={
        "part": "contentDetails", "playlistId": up, "maxResults": 50}).json().get("items", [])]
    if not ids:
        return []
    uit = []
    for v in requests.get(api + "videos", headers=h, timeout=60, params={"part": "snippet,status", "id": ",".join(ids)}).json()["items"]:
        st = v["status"]
        wanneer = st.get("publishAt") if st["privacyStatus"] != "public" else v["snippet"]["publishedAt"]
        if not wanneer:
            continue
        t = dt.datetime.fromisoformat(wanneer.replace("Z", "+00:00")).astimezone(NL)
        uit.append({"id": v["id"], "titel": v["snippet"]["title"], "datum": t.date().isoformat(), "tijd": t.strftime("%H:%M"),
                    "stand": "online" if st["privacyStatus"] == "public" else "gepland" if st.get("publishAt") else "privé"})
    return uit


def maak(sleep_video=(), vandaag=None):
    vandaag = vandaag or dt.date.today()
    maandag = vandaag - dt.timedelta(days=vandaag.weekday())
    eind = maandag + dt.timedelta(days=13)
    try:
        cfg = json.loads(BESTAND.read_text(encoding="utf-8"))
    except Exception as e:
        cfg = {"regels": {}, "items": [], "fout": str(e)[:100]}
    items = []
    for v in sleep_video:
        if v.get("datum") and maandag.isoformat() <= v["datum"] <= eind.isoformat():
            items.append({"kanaal": "Sleep Archives", "datum": v["datum"], "tijd": "21:00",
                          "titel": re.sub(r"\s*\|.*$", "", v["titel"]), "stand": SLEEP_STAND.get(v["soort"], v["soort"]),
                          "youtube": v.get("id", "")})
    items += [dict(i) for i in cfg.get("items", [])]
    fouten = []
    for kanaal in ("BlackswanVault", "NOIRTRACES"):
        try:
            yt = _youtube(kanaal)
        except Exception as e:
            fouten.append(f"{kanaal}: YouTube niet te lezen ({str(e)[:60]})")
            continue
        bekend = {i.get("youtube") for i in items if i.get("youtube")}
        for y in yt:
            eigen = next((i for i in items if i.get("youtube") == y["id"]), None)
            if eigen:                                         # YouTube is de waarheid voor datum en stand
                eigen.update(datum=y["datum"], tijd=y["tijd"], stand=y["stand"])
            elif y["id"] not in bekend:
                items.append({"kanaal": kanaal, **{k: y[k] for k in ("datum", "tijd", "titel", "stand")}, "youtube": y["id"]})
    weken = []
    for w in range(2):
        start = maandag + dt.timedelta(weeks=w)
        dagen = []
        for d in range(7):
            dag = (start + dt.timedelta(days=d)).isoformat()
            dagen.append({"datum": dag, "items": sorted([i for i in items if i["datum"] == dag], key=lambda i: i.get("tijd", ""))})
        weken.append({"label": "Deze week" if w == 0 else "Volgende week", "van": start.isoformat(),
                      "tot": (start + dt.timedelta(days=6)).isoformat(), "week": start.isocalendar()[1], "dagen": dagen})
    return {"weken": weken, "regels": cfg.get("regels", {}), "fouten": fouten + ([cfg["fout"]] if cfg.get("fout") else [])}


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    for w in maak()["weken"]:
        print(f"== {w['label']} (week {w['week']}, {w['van']} t/m {w['tot']})")
        for d in w["dagen"]:
            for i in d["items"]:
                print(f"  {d['datum']} {i.get('tijd', '')}  {i['kanaal']:15s} {i['stand']:16s} {i['titel'][:60]}")
