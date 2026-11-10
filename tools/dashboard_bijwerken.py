"""Werkt het statusdashboard bij: https://wgnghr44bg-coder.github.io/vox-lux/status/ (eigenaar 8 nov 2026: "een website
via GitHub zodat ik alles kan zien", "pas dit aan zoals deze afbeelding met de gegevens die wij gebruiken").

Verzamelt op de pc: kanaalcijfers (YouTube Data + Analytics API, alleen lezen), laatste uploads, de stap van de
videostraat die nu loopt met voortgang, huidige taak, weekplanning, logboek, fouten en de stand van onze programma's
(Ollama/Qwen3, ComfyUI, OmniVoice B1, Audio Engine W3, ffmpeg, YouTube API, Taakplanner). Schrijft
docs/status/data.json (+ thumbnail van de huidige taak) en pusht ALLEEN docs/status. Geen sleutels of tokens.

  python tools/dashboard_bijwerken.py            # bijwerken en pushen
  python tools/dashboard_bijwerken.py --niet-pushen
"""
import datetime, json, re, shutil, subprocess, sys
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
# Eigenaar 9 nov 2026: "kun je de website offline halen". ONLINE = True   # eigenaar 10 nov: website weer aan ("wat er in de planning staat, waar we mee bezig zijn en wat er fout ging"): alles blijft lokaal op de pc (de zelfcontrole draait
# gewoon door), niets naar GitHub. Weer online: ONLINE = True en docs/status terugzetten uit git (commit vóór 9 nov avond).
ONLINE = True   # eigenaar 10 nov: website weer aan ("wat er in de planning staat, waar we mee bezig zijn en wat er fout ging")
DOCS = REPO / "docs" / "status" if ONLINE else Path(r"C:\Users\rane\sleep-archives-status")
UIT = DOCS / "data.json"
NU = datetime.datetime.now()
VANDAAG = datetime.date.today()
LOGS = {"testvolgorde": Path(r"C:\Users\rane\testvolgorde.log"),
        "scriptgenerator": Path(r"C:\Users\rane\sleep-archives-scripts-log.txt"),
        "routine": Path(r"C:\Users\rane\sleep-archives-routine-log.txt"),
        "nachttest": Path(r"C:\Users\rane\nachttest.log"), "tombstone": Path(r"C:\Users\rane\tombstone-herstel.log"),
        "testvervolg": Path(r"C:\Users\rane\testvervolg.log"),
        "hervat": Path(r"C:\Users\rane\hervat.log")}
FOUTWOORDEN = r"FOUT|GESTOPT|MISLUKT|NIET GOED|REJECTED|AFWIJKING|Traceback|Error"


def lees(p, n=None):
    """Leest ook logs die PowerShell 5 als UTF-16 schrijft (met '*>')."""
    try:
        b = Path(p).read_bytes()
    except Exception:
        return []
    if b[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(b) > 1 and b[1:2] == b"\x00"):
        t = b.decode("utf-16", errors="replace")
    else:
        t = b.decode("utf-8", errors="replace")
    regels = [r.rstrip() for r in t.splitlines() if r.strip()]
    return regels[-n:] if n else regels


def schoon(r):
    return re.sub(r"[A-Z]:\\[^\s'\"]+", "…", r.replace("Ã¨", "è").replace("Ã¼", "ü"))[:200]


# ---------- planning ----------
def planning():
    uit = []
    for m in sorted(STORIES.iterdir()):
        p = m / "planning.txt"
        if not m.is_dir() or not p.exists() or m.name.startswith("_"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        g = lambda k: (re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1].strip()
        d = re.search(r"(\d{4}-\d{2}-\d{2})", g("datum"))
        link = re.search(r"https://youtu\.be/([A-Za-z0-9_-]{11})", t)
        status = g("status") or ("klaar" if link else "")
        datum = d.group(1) if d else ""
        soort = ("gepland" if link and status.startswith("klaar") and datum > VANDAAG.isoformat() else
                 "online" if link and status.startswith("klaar") else
                 "bezig" if status.startswith(("bezig", "in-wording")) else
                 "script nieuw" if "nieuwe opbouw" in status else
                 "script oud" if status.startswith("script-klaar") else status.split(" ")[0] or "?")
        uit.append({"map": m.name, "datum": datum, "reserve": "reserve" in g("datum"),
                    "titel": re.sub(r"\s*\(.*$", "", g("titel"))[:110] or g("onderwerp")[:110],
                    "status": status[:140], "soort": soort, "id": link.group(1) if link else "",
                    "afspeellijst": g("soort").split(" ")[0], "opening": g("opening").split(" ")[0]})
    return uit


# ---------- wat draait er ----------
STAPPEN = ["Onderwerp & planning", "Script schrijven", "Beelden maken", "Stem (B1)", "Video bouwen", "Controles", "YouTube upload"]
HERKEN = [("scriptgen", 1, "script schrijven (Qwen3 lokaal)"), ("PROMPT-SCRIPT-PC", 1, "script schrijven (Claude)"),
          ("comfy_batch.py", 2, "beelden maken (ComfyUI)"), ("beeldcheck.py", 2, "beeldcontrole (Qwen2.5-VL + CLIP)"),
          ("engine_stem.py", 3, "stem inspreken (OmniVoice B1)"), ("prep_engine.sh", 3, "tekstcontrole"),
          ("check_stem_tekst.py", 3, "tekstcontrole (Whisper)"), ("herstel_zinnen.py", 3, "zinnen herstellen"),
          ("engine_muziek.py", 4, "muziek maken (Audio Engine W3)"), ("make_video.py", 4, "beelden en geluid samenvoegen"),
          ("motion.py", 4, "beweging en hoofdstuktitels"), ("stil_tikjes.py", 4, "tikjes weghalen"),
          ("eind_volume.py", 4, "eindvolume -14 LUFS"), ("film16.py", 4, "16mm-look"),
          ("check_video.py", 5, "videocontrole"), ("qc_video.py", 5, "kwaliteitscontrole"),
          ("vervang_video.py", 6, "uploaden en controleren"), ("youtube_upload.py", 6, "uploaden"),
          ("wacht_verwerkt.py", 6, "wachten op verwerking YouTube"),
          ("PROMPT-ROUTINE-PC", 0, "routine (Claude) stuurt aan"), ("routine_lokaal.py", 0, "routine zonder Claude")]


def processen():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CommandLine }"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
    except Exception:
        out = ""
    gevonden, stap, mapnaam = [], -1, ""
    for regel in out.splitlines():
        for k, s, naam in HERKEN:
            if k in regel:
                if naam not in [g["naam"] for g in gevonden]:
                    gevonden.append({"naam": naam, "stap": s})
                if s > stap:
                    stap = s
                    mm = re.search(r"stories[\\/]([a-z0-9-]+)", regel) or re.search(r"\b([a-z0-9]+-[0-9]{3,4}|[a-z]+-[a-z]+)\b\s", regel)
                    mapnaam = mm.group(1) if mm and (STORIES / mm.group(1)).is_dir() else mapnaam
    return gevonden, stap, mapnaam


def voortgang(stap, m):
    """Ruwe voortgang (0-100) van de stap die nu loopt, uit bestanden en logs."""
    if not m:
        return None, ""
    d = STORIES / m
    try:
        if stap == 1:
            # alleen de log die nu loopt (de nieuwste), en alleen na de laatste start van de generator
            nieuwste = max((LOGS[k] for k in ("testvolgorde", "nachttest", "testvervolg") if Path(LOGS[k]).exists()),
                           key=lambda p: Path(p).stat().st_mtime)
            tekst = "\n".join(lees(nieuwste, 2000))
            tekst = tekst[tekst.rfind(": start ("):] if ": start (" in tekst else tekst
            n = max([int(x) for x in re.findall(r"feitje (\d+):", tekst)] or [0])
            return min(99, round(100 * n / 90)), f"{n} van ± 90 feitjes"
        if stap == 2:
            totaal = sum(1 for r in (d / "prompts.txt").read_text(encoding="utf-8").splitlines() if "|" in r and not r.startswith("#"))
            klaar = len(list((d / "afbeeldingen").glob("*.png")))
            return min(99, round(100 * klaar / max(totaal, 1))), f"{klaar} van {totaal} beelden"
        if stap == 3:
            alles = "\n".join(lees(LOGS["testvolgorde"], 300))
            k = re.findall(r"klaar (\d+)/(\d+)", alles)
            if k:
                a, b = map(int, k[-1])
                return min(99, round(100 * a / b)), f"{a} van {b} zinnen"
            return None, "bezig"
        if stap == 4:
            v = d / "video"
            basis = (v / f"{m}.mp4").stat().st_size if (v / f"{m}.mp4").exists() else 0
            for naam, doel, factor, label in (("-16mm.mp4", "-14.mp4", 4.0, "16mm-look"), ("-motion.mp4", ".mp4", 1.0, "beweging")):
                f, g = v / f"{m}{naam}", v / f"{m}{doel}"
                if f.exists() and g.exists() and f.stat().st_mtime > NU.timestamp() - 3 * 3600:
                    return min(99, round(100 * f.stat().st_size / (g.stat().st_size * factor))), label
            return None, "bezig"
    except Exception:
        pass
    return None, ""


def gpu():
    try:
        r = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total",
                            "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=20).stdout.strip()
        b, g, t = [int(x) for x in r.split(",")]
        return {"bezig_procent": b, "geheugen_mb": g, "totaal_mb": t}
    except Exception:
        return None


def taken():
    uit = {}
    for naam in ("Sleep Archives routine", "Sleep Archives scriptgenerator", "Sleep Archives dashboard"):
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                                f"$t = Get-ScheduledTask -TaskName '{naam}'; $i = $t | Get-ScheduledTaskInfo; "
                                "\"$($t.State)|$($i.LastRunTime.ToString('yyyy-MM-dd HH:mm'))|$($i.NextRunTime.ToString('yyyy-MM-dd HH:mm'))\""],
                               capture_output=True, text=True, timeout=60).stdout.strip()
            st, laatst, volgend = r.split("|")
            uit[naam.replace("Sleep Archives ", "")] = {"aan": st != "Disabled", "laatst": "nog niet" if laatst.startswith("1999") else laatst,
                                                         "volgende": volgend or "—"}
        except Exception:
            uit[naam.replace("Sleep Archives ", "")] = None
    return uit


def programmas(yt_ok):
    def http(url):
        try:
            return requests.get(url, timeout=5).status_code == 200
        except Exception:
            return False
    ollama = http("http://127.0.0.1:11434/api/tags")
    return [
        {"naam": "Script", "wat": "Qwen3 14B (Ollama)" if ollama else "Ollama staat uit", "ok": ollama},
        {"naam": "Beelden", "wat": "ComfyUI Z-Image", "ok": http("http://127.0.0.1:8188/system_stats")},
        {"naam": "Beeldcontrole", "wat": "Qwen2.5-VL + CLIP", "ok": ollama and (HIER / "beeldcheck_clip.npz").exists()},
        {"naam": "Stem", "wat": "OmniVoice B1", "ok": Path(r"C:\Users\rane\omnivoice-venv\Scripts\python.exe").exists()
                                                       and (REPO / "audio_engine" / "B1-referentie" / "maten.json").exists()},
        {"naam": "Muziek", "wat": "Audio Engine W3", "ok": (REPO / "audio_engine" / "B1.json").exists()},
        {"naam": "Video", "wat": "ffmpeg", "ok": shutil.which("ffmpeg") is not None},
        {"naam": "YouTube", "wat": "API", "ok": yt_ok}]


# ---------- YouTube (alleen lezen) ----------
def youtube():
    try:
        sys.path.insert(0, str(HIER))
        import youtube_upload as yu
        h = {"Authorization": "Bearer " + yu.access_token()}
        c = requests.get("https://www.googleapis.com/youtube/v3/channels", headers=h,
                         params={"part": "snippet,statistics,contentDetails", "mine": "true"}, timeout=30).json()["items"][0]

        def periode(b, e):
            r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", headers=h, timeout=30, params={
                "ids": "channel==MINE", "startDate": str(b), "endDate": str(e),
                "metrics": "views,estimatedMinutesWatched,subscribersGained,subscribersLost"}).json()
            rij = (r.get("rows") or [[0, 0, 0, 0]])[0]
            return {"views": rij[0], "uren": round(rij[1] / 60), "abonnees": rij[2] - rij[3]}
        nu = periode(VANDAAG - datetime.timedelta(days=7), VANDAAG)
        voor = periode(VANDAAG - datetime.timedelta(days=14), VANDAAG - datetime.timedelta(days=7))
        uploads = c["contentDetails"]["relatedPlaylists"]["uploads"]
        items = requests.get("https://www.googleapis.com/youtube/v3/playlistItems", headers=h, timeout=30,
                             params={"part": "contentDetails", "playlistId": uploads, "maxResults": 10}).json().get("items", [])
        ids = ",".join(i["contentDetails"]["videoId"] for i in items)
        vids = requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, timeout=30,
                            params={"part": "snippet,status,contentDetails,statistics", "id": ids}).json().get("items", [])
        recent = []
        for v in vids:
            dur = v["contentDetails"]["duration"]
            u, mi, s = [int(x or 0) for x in re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", dur).groups()]
            st = v["status"]
            recent.append({"id": v["id"], "titel": v["snippet"]["title"], "duur": f"{u}:{mi:02d}:{s:02d}",
                           "privacy": st["privacyStatus"], "publiceer": st.get("publishAt") or v["snippet"]["publishedAt"],
                           "views": int(v.get("statistics", {}).get("viewCount", 0)), "verwerkt": st.get("uploadStatus")})
        recent.sort(key=lambda x: x["publiceer"], reverse=True)
        return {"naam": c["snippet"]["title"], "abonnees": int(c["statistics"]["subscriberCount"]),
                "views_totaal": int(c["statistics"]["viewCount"]), "video_aantal": int(c["statistics"]["videoCount"]),
                "week": nu, "vorige_week": voor, "recent": recent}, True
    except Exception as e:
        return {"fout": str(e)[:120]}, False


# ---------- logboek en fouten ----------
def logboek():
    uit = []
    for r in lees(STORIES / "ROUTINE-LOG.md", 60):
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (.+)$", r)
        if m:
            uit.append({"tijd": m.group(1), "tekst": schoon(m.group(2))})
    for r in lees(LOGS["testvolgorde"], 400) + lees(Path(r"C:\Users\rane\tombstone-opnieuw.log"), 200) + lees(LOGS["nachttest"], 200) + lees(LOGS["tombstone"], 100) + lees(LOGS["testvervolg"], 200) + lees(LOGS["hervat"], 300):
        m = re.match(r"=== (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (.+)$", r)
        if m:
            uit.append({"tijd": m.group(1), "tekst": schoon(m.group(2))})
    uit.sort(key=lambda x: x["tijd"])
    for x in uit:
        x["fout"] = bool(re.search(FOUTWOORDEN, x["tekst"]))
        x["klaar"] = bool(re.search(r"KLAAR|GOED|geüpload|online", x["tekst"])) and not x["fout"]
    return uit[-250:]


def runs(log):
    grens = (NU - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    r = [x for x in log if x["tijd"] >= grens and (x["fout"] or "KLAAR" in x["tekst"])]
    goed = sum(1 for x in r if not x["fout"])
    return {"goed": goed, "totaal": len(r), "procent": round(100 * goed / len(r)) if r else None}


# ---------- alles samen ----------
video = planning()
draait, stap, actief = processen()
if not actief:                                              # anders: de video die "bezig" is
    b = [v for v in video if v["soort"] == "bezig"]
    actief = b[0]["map"] if b else ""
proc, proc_tekst = voortgang(stap, actief)
yt, yt_ok = youtube()
log = logboek()
huidig = None
if actief:
    v = next((x for x in video if x["map"] == actief), {"titel": actief, "datum": "", "id": ""})
    thumb = ""
    bron = STORIES / actief / "thumbnail-gekozen.jpg"
    if v.get("id"):
        thumb = f"https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg"
    elif bron.exists():
        (DOCS / "thumbs").mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image
            Image.open(bron).convert("RGB").resize((480, 270)).save(DOCS / "thumbs" / f"{actief}.jpg", quality=75)
            thumb = f"thumbs/{actief}.jpg"
        except Exception:
            pass
    huidig = {"map": actief, "titel": v["titel"], "datum": v["datum"], "thumb": thumb, "stap": stap,
              "stapnaam": STAPPEN[stap] if 0 <= stap < len(STAPPEN) else "", "voortgang": proc, "detail": proc_tekst,
              "taken": [d["naam"] for d in draait]}
week = []
for i in range(7):
    dag = VANDAAG + datetime.timedelta(days=i)
    plek = dag.weekday() in (0, 2, 5)
    vs = [v for v in video if v["datum"] == dag.isoformat()]
    week.append({"datum": dag.isoformat(), "plek": plek, "video": vs[0]["titel"] if vs else "",
                 "soort": vs[0]["soort"] if vs else ("vrij" if plek else "")})
grens48 = (NU - datetime.timedelta(hours=72)).strftime("%Y-%m-%d %H:%M")
SLEUTELS = {d.name.split("-")[0].lower() for d in STORIES.iterdir() if d.is_dir() and not d.name.startswith("_")}


def opgelost(x):
    """Een fout is niet meer actueel als er daarna iets nieuws over dezelfde video in het logboek staat
    (opnieuw gestart, gepauzeerd, uitgesteld, gelukt)."""
    tekst = x["tekst"].lower()
    for s in SLEUTELS:
        if s in tekst and any(y["tijd"] > x["tijd"] and s in y["tekst"].lower() for y in log):
            return True
    return False


fouten = [x for x in log if x["fout"] and x["tijd"] >= grens48 and not opgelost(x)][-6:]
opgeloste = [x for x in log if x["fout"] and x["tijd"] >= grens48 and opgelost(x)][-8:]   # eigenaar 10 nov: "wat er fout ging"
geplande = [r for r in yt.get("recent", []) if r["privacy"] == "private" and r["publiceer"] > NU.isoformat()]

try:                                                        # zelfcontrole (licht elke keer, zwaar één keer per nacht)
    import zelfcontrole
    zc = zelfcontrole.alles()
except Exception as e:
    zc = [{"naam": "Zelfcontrole", "ok": False, "tekst": f"kon niet draaien: {str(e)[:100]}"}]
for x in zc:                                               # fouten uit de zelfcontrole ook bij de meldingen
    if not x["ok"]:
        fouten.append({"tijd": NU.strftime("%Y-%m-%d %H:%M"), "tekst": f"Zelfcontrole: {x['naam']}: {x['tekst']}", "fout": True})
# ---------- duidelijke planning (eigenaar 10 nov 2026: "ik wil duidelijk de planning zien, wat er nu gebeurt en wat erna") ----------
def werkplanning():
    alle_cmd = subprocess.run(["powershell", "-NoProfile", "-Command",
                               "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CommandLine }"],
                              capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
    tk = taken()
    routine_aan = bool(tk.get("routine") and tk["routine"]["aan"])
    nu = []
    if huidig:
        nu.append({"wat": f"{huidig['titel']}", "map": huidig["map"], "detail": f"{huidig['stapnaam']}"
                   + (f" · {huidig['voortgang']}%" if huidig.get("voortgang") is not None else ""), "soort": "nu"})
    daarna = []
    wacht_op = huidig["map"].split("-")[0].capitalize() if huidig else "de huidige taak"
    if "tombstone_opnieuw.ps1" in alle_cmd and not (huidig and huidig["map"] == "tombstone-1881"):
        daarna.append({"wanneer": f"zodra {wacht_op[:40]} klaar is", "wat": "Tombstone opnieuw maken",
                       "detail": "nieuw begin en slot, strenge haperingcontrole, dan de privéversie vervangen", "map": "tombstone-1881"})
    # routine: zo/di/do 09:00, elke keer de eerstvolgende video die nog gemaakt moet worden (of een vrije plek)
    vandaag = VANDAAG.isoformat()
    klaar = {"gepland", "online"}
    todo = sorted([v for v in video if v["datum"] and v["datum"] >= vandaag and v["soort"] not in klaar
                   and v["soort"] != "bezig" and v["map"] != "tombstone-1881"], key=lambda v: v["datum"])
    bezet = {v["datum"] for v in video if v["datum"]}
    for i in range(1, 29):                                   # vrije plekken (ma/wo/za) in de komende 4 weken
        dag = VANDAAG + datetime.timedelta(days=i)
        if dag.weekday() in (0, 2, 5) and dag.isoformat() not in bezet:
            todo.append({"map": "", "datum": dag.isoformat(), "titel": "Vrije plek: de routine kiest een populair onderwerp",
                         "soort": "vrij"})
    todo.sort(key=lambda v: v["datum"])
    runs = []
    for i in range(0, 21):                                   # routine: zondag, dinsdag en donderdag 09:00
        dag = VANDAAG + datetime.timedelta(days=i)
        t = datetime.datetime.combine(dag, datetime.time(9, 0))
        if dag.weekday() in (6, 1, 3) and t > NU and len(runs) < 6:
            runs.append(t)
    DAGEN = ["ma", "di", "wo", "do", "vr", "za", "zo"]
    for r in runs:
        kand = [v for v in todo if v["datum"] >= (r.date() + datetime.timedelta(days=1)).isoformat()]
        if not kand:
            break
        v = kand[0]
        todo.remove(v)
        daarna.append({"wanneer": f"{DAGEN[r.weekday()]} {r.day}-{r.month} 09:00" + ("" if routine_aan else " (routine staat UIT)"),
                       "wat": v["titel"], "map": v["map"],
                       "detail": f"routine maakt de video voor {DAGEN[datetime.date.fromisoformat(v['datum']).weekday()]} "
                                 f"{int(v['datum'][8:])}-{int(v['datum'][5:7])} 21:00"
                                 + (" (script moet eerst nog goedgekeurd)" if v["soort"] == "script oud" else "")})
    # publicaties: komende 3 weken
    pub = []
    for i in range(0, 22):
        dag = VANDAAG + datetime.timedelta(days=i)
        vs = [v for v in video if v["datum"] == dag.isoformat()]
        if not vs and dag.weekday() not in (0, 2, 5):
            continue
        v = vs[0] if vs else None
        if v and v["map"] == "tombstone-1881" and "tombstone_opnieuw.ps1" in alle_cmd:
            stand, kleur = "wordt opnieuw gemaakt (foute versie tegengehouden)", "let"
        elif not v:
            stand, kleur = ("geen video (te weinig tijd om er nog een te maken)", "zacht") if i <= 1 else ("vrije plek: de routine kiest een onderwerp", "zacht")
        elif v["soort"] == "gepland":
            stand, kleur = "staat klaar op YouTube", "goed"
        elif v["soort"] == "online":
            stand, kleur = "online", "goed"
        elif v["soort"] == "bezig":
            stand, kleur = "wordt nu gemaakt", "nu"
        elif v["soort"] == "script nieuw":
            stand, kleur = "script klaar, video volgt", "zacht"
        elif v["soort"] == "script oud":
            stand, kleur = "script moet nog (opnieuw) gemaakt worden", "fout"
        else:
            stand, kleur = v["status"][:60], "zacht"
        pub.append({"datum": dag.isoformat(), "dag": DAGEN[dag.weekday()], "titel": v["titel"] if v else "—",
                    "map": v["map"] if v else "", "stand": stand, "kleur": kleur})
    return {"nu": nu, "daarna": daarna, "publicaties": pub, "routine_aan": routine_aan}


def scripts_overzicht():
    """Eigenaar 10 nov 2026: "tot hoe ver zijn de scripts klaar, en is het makkelijk Engels". Komende 10 weken."""
    import script_leesbaar
    grens = (VANDAAG + datetime.timedelta(days=70)).isoformat()
    rij = []
    for v in sorted([v for v in video if v["datum"] and VANDAAG.isoformat() <= v["datum"] <= grens], key=lambda v: v["datum"]):
        d = STORIES / v["map"]
        nieuw = "nieuwe opbouw" in v["status"] or v["soort"] in ("gepland", "online", "bezig")
        sc, check = d / "scriptcheck.json", "nog niet"
        sf = list((d / "src-feiten").glob("*.txt")) if (d / "src-feiten").exists() else []
        if sc.exists() and sf and sc.stat().st_mtime >= max(f.stat().st_mtime for f in sf):
            try:
                check = "GOED" if not json.loads(sc.read_text(encoding="utf-8")).get("fouten") else "FOUT"
            except Exception:
                check = "?"
        try:
            lb = script_leesbaar.meet(d) if nieuw else None
            tn = script_leesbaar.toon(d) if nieuw else None
        except Exception:
            lb = None
        if v["soort"] in ("gepland", "online"):
            stand = "video staat klaar"
        elif v["soort"] == "bezig":
            stand = "video wordt gemaakt"
        elif nieuw:
            stand = "script klaar" + (" en 's nachts goedgekeurd" if check == "GOED" else
                                      ", nachtcontrole vond iets" if check == "FOUT" else ", nachtcontrole volgt")
        elif "scriptcheck FOUT" in v["status"]:
            stand = "script afgekeurd, moet opnieuw"
        else:
            stand = "nog in de oude opbouw, moet omgebouwd"
        rij.append({"datum": v["datum"], "titel": v["titel"], "map": v["map"], "klaar": nieuw, "stand": stand,
                    "controle": check, "flesch": lb["flesch"] if lb else None, "niveau": lb["niveau"] if lb else None,
                    "leesbaar": lb["oordeel"] if lb else None, "toon": tn["toon"] if tn else None})
    tot = ""
    for r in rij:                                            # aaneengesloten klaar vanaf vandaag
        if not r["klaar"]:
            break
        tot = r["datum"]
    return {"klaar_tot": tot, "rij": rij}


try:
    sc_overzicht = scripts_overzicht()
except Exception as e:
    sc_overzicht = {"klaar_tot": "", "rij": [], "fout": str(e)[:120]}

try:
    wp = werkplanning()
    for w in week:                                          # week gelijk aan de planning (bv. Tombstone tegengehouden)
        p = next((x for x in wp["publicaties"] if x["datum"] == w["datum"]), None)
        if p and p["kleur"] == "let":
            w["soort"] = p["stand"]
except Exception as e:
    wp = {"nu": [], "daarna": [], "publicaties": [], "fout": str(e)[:120]}

data = {
    "bijgewerkt": NU.strftime("%Y-%m-%d %H:%M"),
    "werkplanning": wp,
    "scripts": sc_overzicht,
    "zelfcontrole": zc,
    "automatisering": bool(taken().get("routine") and taken()["routine"]["aan"]),   # scriptgenerator staat bewust uit (scripts via Claude)
    "taken": taken(),
    "kanaal": yt,
    "kpi": {"geplande": len(geplande), "runs": runs(log), "fouten": len(fouten),
            "zelfcontrole": {"goed": sum(1 for x in zc if x["ok"]), "totaal": len(zc)}},
    "stappen": STAPPEN, "stap": stap, "huidig": huidig,
    "nu_bezig": draait, "videokaart": gpu(), "programmas": programmas(yt_ok),
    "week": week, "logboek": log[-14:], "fouten": fouten, "opgelost": opgeloste,
    "video": video,
    "vast": {"Stem": "B1: narrator-e (OmniVoice), speed 0.54, pauzes ×1,4, warme klank",
             "Muziek": "W3: diep en donker-warm, 432 Hz, elke 6 s een ander akkoord, 11 LUFS onder de stem",
             "Opbouw": "begin ± 2 min (zonder Tonight), 8-13 onderwerpen met feitjes, slot dat uitdooft",
             "Planning": "ma, wo en za 21:00 (NL)"},
}
DOCS.mkdir(parents=True, exist_ok=True)
UIT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print("dashboard bijgewerkt:", data["bijgewerkt"], "| stap:", stap, actief, proc, "| nu:", ", ".join(d["naam"] for d in draait) or "niets")
if ONLINE and "--niet-pushen" not in sys.argv:                          # via de wachtrij (tools/gitveilig.py), geen botsingen
    from gitveilig import bewaar
    bewaar([DOCS], f"dashboard {data['bijgewerkt']}")
