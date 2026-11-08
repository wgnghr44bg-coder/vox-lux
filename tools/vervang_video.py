"""Nieuwe versie van een video uploaden en de oude pas daarna verwijderen (eigenaar 6-8 nov 2026), helemaal zonder
tussenkomst, voor de keten op de pc.

  python tools/vervang_video.py stories/<map> --video <map>/video/<naam>-16mm.mp4 --publish-at 2026-11-11T20:00:00Z
         --thumbnail <bestand> --soort mysterie [--oud 4RjjJh-j5a0] [--tags "a, b, c"]

Stappen: titel uit planning.txt (regel "titel", zonder het commentaar tussen haakjes), beschrijving uit
youtube-beschrijving.txt, privé met publishAt, thumbnail, kanaal "Sleep Archives" controleren (anders meteen
verwijderen en stoppen), afspeellijsten, wachten tot YouTube klaar is (tools/wacht_verwerkt.py, max 12 uur), dan de
oude video verwijderen (alleen als die op Sleep Archives staat, privé is en een andere id heeft), grote bestanden op
de pc opruimen en planning.txt bijwerken + commit/push. Bij een fout: niets verwijderen, melding in ROUTINE-LOG.md.
"""
import argparse, datetime, re, subprocess, sys
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import youtube_upload as yu

TAGS = ("history for sleep, boring history for sleep, sleep documentary, bedtime story, relaxing history, sleep story, "
        "432hz, 432 hz sleep music, sleep sounds")
API = "https://www.googleapis.com/youtube/v3/videos"


def log(m, tekst):
    regel = f"- {datetime.datetime.now():%Y-%m-%d %H:%M} {m.name}: {tekst}\n"
    print(regel, end="", flush=True)
    with open(HIER.parent / "stories" / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(regel)


def info(vid):
    h = {"Authorization": "Bearer " + yu.access_token()}
    r = requests.get(API, params={"part": "snippet,status", "id": vid}, headers=h, timeout=60).json().get("items", [])
    return r[0] if r else None


def verwijder(vid):
    h = {"Authorization": "Bearer " + yu.access_token()}
    return requests.delete(API, params={"id": vid}, headers=h, timeout=60).status_code == 204


ap = argparse.ArgumentParser()
ap.add_argument("map", type=Path)
ap.add_argument("--video", type=Path, required=True)
ap.add_argument("--publish-at", required=True)
ap.add_argument("--thumbnail", type=Path, required=True)
ap.add_argument("--soort", required=True)
ap.add_argument("--oud", default="")
ap.add_argument("--tags", default="")
a = ap.parse_args()
m = a.map
plan = (m / "planning.txt").read_text(encoding="utf-8")
titel = re.search(r"^titel\s+(.+?\| History for Sleep)", plan, re.M).group(1).strip()
assert a.video.exists() and a.thumbnail.exists(), "video of thumbnail ontbreekt"
assert "hour" not in titel.lower(), "titel met uren"

uit = subprocess.run([sys.executable, str(HIER / "youtube_upload.py"), str(a.video), "--title", titel,
                      "--description-file", str(m / "youtube-beschrijving.txt"), "--tags", TAGS + (", " + a.tags if a.tags else ""),
                      "--privacy", "private", "--publish-at", a.publish_at, "--thumbnail", str(a.thumbnail)],
                     capture_output=True, text=True, encoding="utf-8", errors="replace")
print(uit.stdout[-600:], uit.stderr[-600:])
gevonden = re.search(r"youtu\.be/([A-Za-z0-9_-]{11})", uit.stdout)
if not gevonden:
    log(m, "UPLOAD MISLUKT, niets verwijderd")
    sys.exit(1)
nieuw = gevonden.group(1)
i = info(nieuw)
if not i or i["snippet"]["channelTitle"] != "Sleep Archives":
    verwijder(nieuw)
    log(m, f"VERKEERD KANAAL ({i and i['snippet']['channelTitle']}), nieuwe upload {nieuw} verwijderd, gestopt")
    sys.exit(1)
log(m, f"geüpload https://youtu.be/{nieuw} (privé, publiek {a.publish_at}), kanaal Sleep Archives gecontroleerd")
subprocess.run([sys.executable, str(HIER / "youtube_playlist.py"), "--soort", a.soort, nieuw])

w = subprocess.run([sys.executable, str(HIER / "wacht_verwerkt.py"), nieuw, "--uren", "12"], capture_output=True, text=True)
print(w.stdout)
if w.returncode != 0:
    log(m, f"verwerking {nieuw} niet klaar of mislukt ({w.stdout.strip()[:80]}): oude versie NIET verwijderd, bestanden blijven")
    sys.exit(1)

if a.oud and a.oud != nieuw:
    o = info(a.oud)
    if o and o["snippet"]["channelTitle"] == "Sleep Archives" and o["status"]["privacyStatus"] == "private":
        log(m, f"oude versie {a.oud} ('{o['snippet']['title']}') " + ("verwijderd" if verwijder(a.oud) else "NIET verwijderd (fout)"))
    else:
        log(m, f"oude versie {a.oud} niet verwijderd: niet gevonden, niet privé of ander kanaal")

v = m / "video"
for f in list(v.rglob("*.mp4")) + list(v.rglob("*.wav")):
    f.unlink()
regel = (f"link https://youtu.be/{nieuw} ({datetime.date.today()}: B1 + W3, nieuwe opbouw, 16mm; privé met publishAt "
         f"{a.publish_at}; Sleep Archives gecontroleerd; verwerkt; "
         + (f"oude {a.oud} verwijderd met OK van de eigenaar; " if a.oud else "") + "bestanden opgeruimd)\nkosten  EUR 0")
plan = re.sub(r"^link .*$", regel.replace("\\", "/"), plan, count=1, flags=re.M) if re.search(r"^link ", plan, re.M) \
    else plan.rstrip() + "\n" + regel + "\n"
plan = re.sub(r"^status .*$", "status   klaar", plan, count=1, flags=re.M)
(m / "planning.txt").write_text(plan, encoding="utf-8")
subprocess.run(["git", "add", str(m / "planning.txt"), str(m / "youtube-beschrijving.txt"), "stories/ROUTINE-LOG.md"],
               cwd=HIER.parent)
subprocess.run(["git", "commit", "-q", "-m", f"{m.name}: nieuwe versie {nieuw} geüpload, oude verwijderd\n\n"
                "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"], cwd=HIER.parent)
subprocess.run(["git", "pull", "-q", "--rebase"], cwd=HIER.parent)
subprocess.run(["git", "push", "-q", "origin", "main"], cwd=HIER.parent)
log(m, "KLAAR")
