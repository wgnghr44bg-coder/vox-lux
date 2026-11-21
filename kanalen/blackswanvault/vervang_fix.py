"""Vervang video8 (Bitcoin), video9 (SpaceX) en de SpaceX-Short door de versies met de juiste slotcijfers (eigenaar OK 21 nov).
Neemt titel, beschrijving, tags, taal en publishAt over van de oude video, uploadt privé, controleert het kanaal,
AI-label aan, thumbnail, wacht tot YouTube klaar is en verwijdert pas dan de oude. Links in de Shorts worden bijgewerkt.
Draaien met YT_REFRESH_TOKEN=$YT_WHATIF_REFRESH_TOKEN."""
import json, re, sys, time
from pathlib import Path
import requests
HIER = Path(__file__).parent
sys.path.insert(0, str(HIER.parents[1] / "tools"))
from youtube_upload import access_token, upload, set_thumbnail

API = "https://www.googleapis.com/youtube/v3/videos"
TOKEN = access_token(); H = {"Authorization": f"Bearer {TOKEN}"}
BITCOIN_SHORT = "gtqCj_lhfm4"

def haal(vid):
    for i in range(6):
        try:
            r = requests.get(API, params={"part": "snippet,status", "id": vid}, headers=H, timeout=60); break
        except requests.RequestException:
            time.sleep(20 * (i + 1))
    r.raise_for_status()
    it = r.json()["items"]; return it[0] if it else None

def zet(item, parts):
    r = requests.put(API, params={"part": parts}, headers={**H, "Content-Type": "application/json"}, data=json.dumps(item), timeout=60)
    if not r.ok: print("PUT fout", r.status_code, r.text[:300])
    return r.ok

def nieuwe_hoofdstukken(tekst, map_):
    a = json.loads((map_ / "oud-voor-fix-zinnen.json").read_text(encoding="utf-8"))
    b = json.loads((map_ / "zinnen.json").read_text(encoding="utf-8"))
    def schuif(m):
        t = int(m.group(1)) * 60 + int(m.group(2))
        if t == 0: return m.group(0)
        verschil = next((y[0] - x[0] for x, y in zip(a, b) if x[0] >= t - 1.5), 0)
        n = max(0, round(t + verschil)); return f"{n // 60:02d}:{n % 60:02d}"
    return re.sub(r"^(\d\d):(\d\d)(?= )", schuif, tekst, flags=re.M)

def vervang(oud, bestand, map_, thumb=None, beschr=None):
    o = haal(oud); assert o, f"oude {oud} niet gevonden"
    sn, st = o["snippet"], o["status"]
    print(f"== {oud} '{sn['title']}' publishAt={st.get('publishAt')}", flush=True)
    desc = beschr(sn["description"]) if beschr else sn["description"]
    meta = {"snippet": {k: v for k, v in {"title": sn["title"], "description": desc, "tags": sn.get("tags", []),
                        "categoryId": sn.get("categoryId", "27"), "defaultLanguage": sn.get("defaultLanguage", "en"),
                        "defaultAudioLanguage": sn.get("defaultAudioLanguage", "en")}.items()},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
    if st.get("publishAt"): meta["status"]["publishAt"] = st["publishAt"]
    nieuw = upload(bestand, meta, TOKEN)
    n = haal(nieuw)
    print(f"   nieuw {nieuw} kanaal={n['snippet']['channelTitle']} privacy={n['status']['privacyStatus']} publishAt={n['status'].get('publishAt')}", flush=True)
    if n["snippet"]["channelTitle"].lower() != "blackswanvault":
        sys.exit("VERKEERD KANAAL, gestopt")
    if n["status"].get("publishAt") != st.get("publishAt"):
        n["status"]["publishAt"] = st.get("publishAt"); n["status"]["containsSyntheticMedia"] = True; zet({"id": nieuw, "status": n["status"]}, "status")
    if thumb and thumb.exists(): set_thumbnail(nieuw, thumb, TOKEN)
    if map_: (map_ / "youtube-id.txt").write_text(nieuw + "\n", encoding="utf-8")
    return nieuw

def wacht(vid):
    for _ in range(240):
        r = requests.get(API, params={"part": "processingDetails,status", "id": vid}, headers=H, timeout=60).json()["items"][0]
        s = r.get("processingDetails", {}).get("processingStatus"); u = r["status"].get("uploadStatus")
        if s == "succeeded" or u == "processed": return True
        if s == "failed" or u in ("failed", "rejected"): return False
        time.sleep(30)
    return False

def link_bij(vid, oud, nieuw):
    s = haal(vid)
    if not s or oud not in s["snippet"]["description"]: return
    sn = {k: s["snippet"][k] for k in ("title", "description", "categoryId", "tags", "defaultLanguage", "defaultAudioLanguage") if k in s["snippet"]}
    sn["description"] = sn["description"].replace(oud, nieuw)
    print(f"   link in {vid}: {oud} -> {nieuw}", zet({"id": vid, "snippet": sn}, "snippet"), flush=True)

v8, v9 = HIER / "video8", HIER / "video9"
import os
b8 = os.environ.get("B8") or vervang("JW4e9rWlukk", v8 / "blackswanvault-bitcoin.mp4", v8, v8 / "thumbnail-definitief.jpg", lambda d: nieuwe_hoofdstukken(d, v8))
b9 = os.environ.get("B9") or vervang("uLoUpPHRz9g", v9 / "blackswanvault-spacex.mp4", v9, v9 / "thumbnail-definitief.jpg", lambda d: nieuwe_hoofdstukken(d, v9))
s9 = vervang("ZdwE2HdjVJg", HIER / "shorts" / "spacex-short-1.mp4", None, None, lambda d: d.replace("uLoUpPHRz9g", b9))
link_bij(BITCOIN_SHORT, "JW4e9rWlukk", b8)
for f, o, n in [("bitcoin-short-1-beschrijving-def.txt", "JW4e9rWlukk", b8), ("spacex-short-1-beschrijving-def.txt", "uLoUpPHRz9g", b9)]:
    p = HIER / "shorts" / f
    if p.exists(): p.write_text(p.read_text(encoding="utf-8").replace(o, n), encoding="utf-8")
(HIER / "shorts" / "spacex-short-1-id.txt").write_text(s9 + "\n", encoding="utf-8")
for oud, nieuw in [("JW4e9rWlukk", b8), ("uLoUpPHRz9g", b9), ("ZdwE2HdjVJg", s9)]:
    ok = wacht(nieuw); print(f"== verwerkt {nieuw}: {ok}", flush=True)
    if ok:
        r = requests.delete(API, params={"id": oud}, headers=H, timeout=60); print(f"   oude {oud} verwijderd: {r.status_code}", flush=True)
    else:
        print(f"   oude {oud} BLIJFT staan (nieuwe niet verwerkt)", flush=True)
print(f"VERVANG-KLAAR bitcoin={b8} spacex={b9} short={s9}", flush=True)
