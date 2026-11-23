"""Weekplanning als seintje op de telefoon (ntfy), elke maandag 08:45; met --vandaag elke dag 09:00 alleen wat er vandaag gemaakt moet worden (eigenaar 23 nov: "stuur mij een bericht wanneer er
iets gemaakt moet worden en wat de planning is van deze week"). Bronnen: kanalen/PLANNING-KANALEN.json (BlackswanVault),
YouTube-inplanning van Sleep Archives, vast ritme Market Doodle (ma/wo/vr). Geen privégegevens in het bericht."""
import datetime as dt, json, os, sys
from pathlib import Path
import requests
ROOT = Path(__file__).resolve().parent.parent
DAG = ["ma", "di", "wo", "do", "vr", "za", "zo"]
vandaag = dt.date.today(); maandag = vandaag - dt.timedelta(days=vandaag.weekday()); zondag = maandag + dt.timedelta(days=6)
regels = {}
def zet(d, tekst):
    regels.setdefault(d, []).append(tekst)
# Market Doodle: ma/wo/vr maken (al online op die dag = klaar)
online = set()
try:
    import urllib.parse, urllib.request
    q = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_REFRESH_TOKEN_ALTERAQON"], "grant_type": "refresh_token"}).encode()
    t = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", q))["access_token"]; H2 = {"Authorization": "Bearer " + t}
    def g2(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/" + p, headers=H2)))
    up = g2("channels?part=contentDetails&mine=true")["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = ",".join(i["contentDetails"]["videoId"] for i in g2(f"playlistItems?part=contentDetails&maxResults=20&playlistId={up}")["items"])
    for v in g2(f"videos?part=snippet,contentDetails&id={ids}")["items"]:
        dur = v["contentDetails"]["duration"]
        if "M" in dur and not dur.startswith("PT0M"):   # lange video (minuten in de duur)
            online.add(dt.datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")).astimezone().date())
except Exception as e: print("Doodle niet gelezen:", e)
for k in (0, 2, 4):
    d = maandag + dt.timedelta(days=k)
    if d in online: zet(d, "Doodle: What If-video online")
    elif d >= vandaag: zet(d, "Doodle: What If-video MAKEN (17:00)")
# BlackswanVault uit de planning
try:
    data = json.load(open(ROOT / "kanalen/PLANNING-KANALEN.json", encoding="utf-8"))
    items = data if isinstance(data, list) else data.get("videos", data.get("items", []))
    for x in items:
        if x.get("kanaal") != "BlackswanVault": continue
        try: d = dt.date.fromisoformat(x.get("datum", ""))
        except ValueError: continue
        stand = x.get("stand", "")
        if not (vandaag <= d <= zondag) or stand.startswith("vervalt"): continue
        soort = "Short" if x.get("titel", "").startswith("Short") else "video"
        actie = "MAKEN/bijwerken" if stand.startswith("maken") else "staat klaar"
        zet(d, f"Swan {soort} {x.get('tijd','')}: {actie}")
except Exception as e: print("planning niet gelezen:", e)
# Sleep Archives: wat staat er ingepland op YouTube
try:
    import urllib.parse, urllib.request
    q = urllib.parse.urlencode({"client_id": os.environ["YT_CLIENT_ID"], "client_secret": os.environ["YT_CLIENT_SECRET"],
                                "refresh_token": os.environ["YT_REFRESH_TOKEN"], "grant_type": "refresh_token"}).encode()
    t = json.load(urllib.request.urlopen("https://oauth2.googleapis.com/token", q))["access_token"]; H = {"Authorization": "Bearer " + t}
    def g(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://www.googleapis.com/youtube/v3/" + p, headers=H)))
    up = g("channels?part=contentDetails&mine=true")["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    ids = ",".join(i["contentDetails"]["videoId"] for i in g(f"playlistItems?part=contentDetails&maxResults=20&playlistId={up}")["items"])
    sleep_week = False
    for v in g(f"videos?part=status&id={ids}")["items"]:
        pa = v["status"].get("publishAt")
        if pa:
            d = dt.datetime.fromisoformat(pa.replace("Z", "+00:00")).astimezone().date()
            if vandaag <= d <= zondag: zet(d, "Sleep 21:00: staat klaar"); sleep_week = True
    later = [v["status"].get("publishAt") for v in g(f"videos?part=status&id={ids}")["items"] if v["status"].get("publishAt")]
    if not any(pa[:10] > zondag.isoformat() for pa in later): zet(zondag, "Sleep: na deze week niets meer ingepland (routine staat stil)")
except Exception as e: print("Sleep niet gelezen:", e)
if "--vandaag" in sys.argv:                       # dagelijks 09:00: alleen een seintje als er vandaag iets GEMAAKT moet worden
    maak = [r for r in regels.get(vandaag, []) if "MAKEN" in r]
    if not maak: print("vandaag niets te maken"); sys.exit()
    regels = {vandaag: maak}
tekst = "\n".join(f"{DAG[d.weekday()]} {d.day}/{d.month}: " + "; ".join(r) for d, r in sorted(regels.items())) or "Niets gepland."
print(tekst)
if "--droog" not in sys.argv:
    topic = json.loads((Path.home() / ".swan-ntfy.json").read_text())["topic"]
    requests.post(f"https://ntfy.sh/{topic}", data=tekst.encode("utf-8"), headers={"Title": (("Vandaag maken" if "--vandaag" in sys.argv else f"Planning week {maandag.day}/{maandag.month}")).encode("utf-8"), "Tags": "calendar"}, timeout=20)
    print("seintje verstuurd")
