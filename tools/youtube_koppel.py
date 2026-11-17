"""Een extra YouTube-kanaal koppelen (eigenaar 17 nov 2026: kanaal op een ander e-mailadres).

Gebruikt dezelfde Google-app (YT_CLIENT_ID / YT_CLIENT_SECRET) als Sleep Archives. Opent de browser: log daar in met
het ANDERE e-mailadres, kies het kanaal en klik op Toestaan. De sleutel (refresh token) komt in ~/.yt-<naam>.json,
buiten git. Er wordt niets geüpload of veranderd: alleen lezen (kanaal, video's, statistieken).

  python tools/youtube_koppel.py altena
  python tools/youtube_koppel.py altena --test        # laat zien welk kanaal gekoppeld is
"""
import http.server, json, os, sys, threading, urllib.parse, webbrowser
from pathlib import Path
import requests

SCOPES = "https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly"
if "--schrijf" in sys.argv:   # alles wat Sleep Archives kan: uploaden, titels/thumbnails/afspeellijsten/kanaal aanpassen
    SCOPES = ("https://www.googleapis.com/auth/youtube https://www.googleapis.com/auth/youtube.upload "
              "https://www.googleapis.com/auth/youtube.force-ssl https://www.googleapis.com/auth/yt-analytics.readonly")
POORT = 8765
naam = sys.argv[1] if len(sys.argv) > 1 else "extra"
BESTAND = Path.home() / f".yt-{naam}.json"
cid, geheim = os.environ.get("YT_CLIENT_ID"), os.environ.get("YT_CLIENT_SECRET")
if not cid or not geheim:
    sys.exit("YT_CLIENT_ID / YT_CLIENT_SECRET ontbreken (dezelfde als voor Sleep Archives)")


def token():
    d = json.loads(BESTAND.read_text())
    r = requests.post("https://oauth2.googleapis.com/token", data={"client_id": cid, "client_secret": geheim,
                      "refresh_token": d["refresh_token"], "grant_type": "refresh_token"}, timeout=30)
    r.raise_for_status()
    return r.json()["access_token"]


if "--test" in sys.argv:
    t = token()
    c = requests.get("https://www.googleapis.com/youtube/v3/channels", headers={"Authorization": f"Bearer {t}"},
                     params={"part": "snippet,statistics", "mine": "true"}, timeout=30).json()["items"][0]
    print(f"gekoppeld: {c['snippet']['title']} ({c['id']}), {c['statistics'].get('subscriberCount')} abonnees, "
          f"{c['statistics'].get('videoCount')} video's")
    sys.exit()

code = {}


class Ontvanger(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code.update({k: v[0] for k, v in q.items()})
        self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers()
        self.wfile.write("Gekoppeld. Je kunt dit venster sluiten.".encode() if "code" in q else
                         f"Niet gelukt: {q.get('error', ['?'])[0]}".encode())

    def log_message(self, *a):
        pass


server = http.server.HTTPServer(("127.0.0.1", POORT), Ontvanger)
threading.Thread(target=server.handle_request, daemon=True).start()
url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode({
    "client_id": cid, "redirect_uri": f"http://127.0.0.1:{POORT}", "response_type": "code", "scope": SCOPES,
    "access_type": "offline", "prompt": "consent select_account"})
print("Log in de browser in met het ANDERE e-mailadres en klik op Toestaan.\n", url)
webbrowser.open(url)
server.timeout = 300
while "code" not in code and "error" not in code:
    server.handle_request()
if "error" in code:
    sys.exit(f"Niet gelukt: {code['error']}")
r = requests.post("https://oauth2.googleapis.com/token", data={"code": code["code"], "client_id": cid,
                  "client_secret": geheim, "redirect_uri": f"http://127.0.0.1:{POORT}",
                  "grant_type": "authorization_code"}, timeout=30)
r.raise_for_status()
d = r.json()
if "refresh_token" not in d:
    sys.exit("Geen refresh token ontvangen; probeer opnieuw.")
BESTAND.write_text(json.dumps({"refresh_token": d["refresh_token"]}))
print(f"opgeslagen in {BESTAND} (buiten git). Test: python tools/youtube_koppel.py {naam} --test")
