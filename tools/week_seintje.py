"""Seintje op de telefoon (ntfy) ALLEEN als er een video of Short gemaakt moet worden, van tevoren.
Eigenaar 23 nov 2026 (avond): "kun je bericht sturen van tevoren als er nog video of short gemaakt moet worden,
de rest van de berichten kunnen weg op ntfy". Alle andere seintjes staan uit (zie swan_yt_wacht.seintje + ~/.swan-ntfy.json "alleen_maken").

Vaste dagen (kanalen/PLANNING-KANALEN.json "regels"):
  BlackswanVault ma/wo/za: lang 15:00 + Short 17:00 | Market Doodle ma/wo/za: lang 17:00 + Short 19:00 | Sleep Archives za 21:00.
Kijkt op YouTube wat er die dag al ingepland of online staat; wat ontbreekt = MAKEN. Geen bericht als alles klaar staat.

  python week_seintje.py --morgen     # 19:00 de avond ervoor: wat moet er morgen nog gemaakt worden
  python week_seintje.py --vandaag    # 09:00: wat moet er vandaag nog gemaakt worden (alleen als het er nog niet staat)
  python week_seintje.py --droog ...  # alleen laten zien
Geen privégegevens in het bericht."""
import datetime as dt, json, os, sys, urllib.parse, urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo
import requests

NL = ZoneInfo("Europe/Amsterdam")
DAG = ["ma", "di", "wo", "do", "vr", "za", "zo"]
VAST = {  # kanaal: (token-env of None voor ~/.yt-..., dagen, [(soort, tijd)])
    "BlackswanVault": ("YT_WHATIF_REFRESH_TOKEN", (0, 2, 5), [("lange video", "15:00"), ("Short", "17:00")]),
    "Market Doodle": ("YT_REFRESH_TOKEN_ALTERAQON", (0, 2, 5), [("lange video", "17:00"), ("Short", "19:00")]),
    "Sleep Archives": ("YT_REFRESH_TOKEN", (5,), [("slaapvideo", "21:00")]),
}

def dur_s(iso):                                             # PT1M8S -> 68
    n, t = 0, iso.replace("PT", "")
    for eenheid, f in (("H", 3600), ("M", 60), ("S", 1)):
        if eenheid in t:
            a, t = t.split(eenheid, 1); n += int(float(a)) * f
    return n

def wat_staat(env, dag):
    """lijst van ('lang'|'short') die op deze dag (NL) online staan of ingepland zijn"""
    q = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ[env], "grant_type": "refresh_token"}).encode()
    t = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", q))["access_token"]; H = {"Authorization": "Bearer " + t}
    def g(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/" + p, headers=H)))
    up = g("channels?part=contentDetails&mine=true")["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = ",".join(i["contentDetails"]["videoId"] for i in g(f"playlistItems?part=contentDetails&maxResults=30&playlistId={up}")["items"])
    uit = []
    for v in g(f"videos?part=snippet,status,contentDetails&id={ids}")["items"]:
        tijd = v["status"].get("publishAt") or (v["snippet"]["publishedAt"] if v["status"]["privacyStatus"] == "public" else None)
        if not tijd: continue
        d = dt.datetime.fromisoformat(tijd.replace("Z", "+00:00")).astimezone(NL).date()
        if d == dag: uit.append("short" if dur_s(v["contentDetails"]["duration"]) <= 100 else "lang")
    return uit

def te_maken(dag):
    regels = []
    for kanaal, (env, dagen, wat) in VAST.items():
        if dag.weekday() not in dagen: continue
        try: staat = wat_staat(env, dag)
        except Exception as e: print(kanaal, "niet gelezen:", e); continue
        for soort, tijd in wat:
            nodig = "short" if soort == "Short" else "lang"
            if nodig in staat: staat.remove(nodig); continue
            extra = " (eigen onderwerp)" if soort == "Short" and kanaal != "Sleep Archives" else ""
            regels.append(f"{kanaal}: {soort} {tijd}{extra}")
    return regels

if __name__ == "__main__":
    morgen = "--morgen" in sys.argv
    dag = dt.datetime.now(NL).date() + dt.timedelta(days=1 if morgen else 0)
    regels = te_maken(dag)
    if not regels: print("niets te maken op", dag); sys.exit()
    kop = ("Morgen maken" if morgen else "Vandaag nog maken") + f" ({DAG[dag.weekday()]} {dag.day}/{dag.month})"
    tekst = "\n".join(regels) + "\nOpen Claude en zeg wat je wilt maken."
    print(kop); print(tekst)
    if "--droog" not in sys.argv:
        topic = json.loads((Path.home() / ".swan-ntfy.json").read_text())["topic"]
        requests.post(f"https://ntfy.sh/{topic}", data=tekst.encode("utf-8"), headers={"Title": kop.encode("utf-8"), "Tags": "clapper"}, timeout=20)
        print("seintje verstuurd")
