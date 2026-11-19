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
        datum = d.group(1) if d and "reserve" not in g("datum") else ""      # "reserve (... was ma 2026-11-16)"
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


RUW = []                                                    # (starttijd, opdrachtregel) van alle processen


def processen():
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CreationDate.ToString('s') + '|' + $_.CommandLine }"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
    except Exception:
        out = ""
    gevonden, stap, mapnaam = [], -1, ""
    for regel in out.splitlines():
        start, _, regel = regel.partition("|")
        RUW.append((start, regel))
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


# ---------- wanneer klaar ----------
# Duur per stap in minuten per uur video, gemeten bij Babylon (12 nov, 2u05: montage 3u06, motion 3u54, 16mm 50 min,
# de controles samen ± 20 min), daarna uploaden en wachten op YouTube (14 min). Volgorde zoals routine_lokaal.py en
# montage_engine.sh.
NA_STEM = [("prep_engine.sh", 10), ("engine_muziek.py", 4), ("make_video.py", 90), ("motion.py", 113),
           ("stil_tikjes.py", 1), ("check_video.py", 2), ("check_stem_tekst.py", 3), ("eind_volume.py", 2),
           ("film16.py", 24), ("qc_video.py", 4), ("vergelijk_bron.py", 1)]
UPLOAD_MIN = 20


def eindtijd(m, proc):
    """Verwachte tijd waarop de video klaar is en op YouTube staat (gepland), uit de stap die nu draait."""
    if not m:
        return None
    try:
        regels = (STORIES / m / "voice-times.tsv").read_text(encoding="utf-8").strip().splitlines()
        uren = float(regels[-1].split("\t")[1]) / 3600 + 0.05
    except Exception:
        uren = 2.5
    actief = [(s, c) for s, c in RUW if m in c or "montage_engine" in c or "vervang_video" in c]
    if any("vervang_video.py" in c or "wacht_verwerkt.py" in c for _, c in actief):
        start = min(datetime.datetime.fromisoformat(s) for s, c in actief if "vervang_video.py" in c)
        return {"klaar": start.strftime("%Y-%m-%d %H:%M"),
                "youtube": max(start + datetime.timedelta(minutes=UPLOAD_MIN), NU + datetime.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M")}
    montage = any("montage_engine" in c for _, c in actief)
    idx, start = -1, None
    for i, (k, _) in enumerate(NA_STEM):
        for s, c in actief:
            # check_stem_tekst.py draait ook vóór de montage (tekstcontrole van de stem)
            if k in c and (k != "check_stem_tekst.py" or montage) and i > idx:
                idx, start = i, datetime.datetime.fromisoformat(s)
    if idx < 0:
        stem = [s for s, c in actief if "engine_stem.py" in c]
        if not stem:
            return None
        rest = 60 * uren * (1 - (proc or 0) / 100)                     # stem: ± 60 min per uur video
        idx, eind = -1, NU + datetime.timedelta(minutes=rest)
    else:
        duur = NA_STEM[idx][1] * uren
        bezig = (NU - start).total_seconds() / 60
        if proc and proc > 3 and bezig > 5:                            # echte voortgang van deze stap (motion, 16mm)
            duur = bezig * 100 / proc
        eind = NU + datetime.timedelta(minutes=max(duur - bezig, 0.1 * duur))
    for _, per_uur in NA_STEM[idx + 1:]:
        eind += datetime.timedelta(minutes=per_uur * uren)
    return {"klaar": eind.strftime("%Y-%m-%d %H:%M"),
            "youtube": (eind + datetime.timedelta(minutes=UPLOAD_MIN)).strftime("%Y-%m-%d %H:%M")}


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
    for naam in ("Sleep Archives routine", "Sleep Archives scriptgenerator", "Sleep Archives dashboard", "Sleep Archives hype",
                 "Sleep Archives bewaker", "Sleep Archives sitecontrole", "Sleep Archives titels"):
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

        # voor het nieuwe dashboard (eigenaar 12 nov 2026, ontwerp "Studio"): 28 dagen per dag, 28 dagen tegen de 28
        # dagen ervoor, een jaar (doel YouTube-partnerprogramma: 1.000 abonnees en 4.000 kijkuren) en de top 3
        def rapport(b, e, **extra):
            r = requests.get("https://youtubeanalytics.googleapis.com/v2/reports", headers=h, timeout=30, params={
                "ids": "channel==MINE", "startDate": str(b), "endDate": str(e), **extra}).json()
            namen = [k["name"] for k in r.get("columnHeaders", [])]
            return [dict(zip(namen, rij)) for rij in r.get("rows", [])]
        try:
            dagen = [{"dag": x["day"], "views": x["views"], "abonnees": x["subscribersGained"] - x["subscribersLost"]}
                     for x in rapport(VANDAAG - datetime.timedelta(days=28), VANDAAG, dimensions="day", sort="day",
                                      metrics="views,subscribersGained,subscribersLost")]
            maand = periode(VANDAAG - datetime.timedelta(days=28), VANDAAG)
            vorige_maand = periode(VANDAAG - datetime.timedelta(days=56), VANDAAG - datetime.timedelta(days=28))
            jaar = periode(VANDAAG - datetime.timedelta(days=365), VANDAAG)
            top_r = rapport(VANDAAG - datetime.timedelta(days=28), VANDAAG, dimensions="video", sort="-views",
                            maxResults=3, metrics="views,estimatedMinutesWatched")
            namen = {}
            if top_r:
                for v in requests.get("https://www.googleapis.com/youtube/v3/videos", headers=h, timeout=30,
                                      params={"part": "snippet,contentDetails", "id": ",".join(x["video"] for x in top_r)}).json().get("items", []):
                    u, mi, s = [int(x or 0) for x in re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", v["contentDetails"]["duration"]).groups()]
                    namen[v["id"]] = (v["snippet"]["title"], f"{u}:{mi:02d}:{s:02d}")
            top = [{"id": x["video"], "titel": namen.get(x["video"], ("?", ""))[0], "duur": namen.get(x["video"], ("", ""))[1],
                    "views": x["views"], "uren": round(x["estimatedMinutesWatched"] / 60)} for x in top_r]
        except Exception:
            dagen, maand, vorige_maand, jaar, top = [], None, None, None, []
        # 16 nov 2026 (eigenaar: "hoeveel dagen ik nog heb tot de 365 dagen van de 4000 uur"): partnerprogramma.
        # Kijkuren per dag over 365 dagen: hoeveel tellen nu mee, wanneer vallen de oudste eruit, wanneer haal je
        # 4.000 uur en 1.000 abonnees in het huidige tempo (laatste 28 dagen).
        partner = None
        try:
            per_dag = [(datetime.date.fromisoformat(x["day"]), x["estimatedMinutesWatched"] / 60)
                       for x in rapport(VANDAAG - datetime.timedelta(days=364), VANDAAG, dimensions="day", sort="day",
                                        metrics="estimatedMinutesWatched")]
            uren = sum(u for _, u in per_dag)
            eerste = next((d for d, u in per_dag if u > 0), None)
            tempo_uren = sum(u for d, u in per_dag if d > VANDAAG - datetime.timedelta(days=28)) / 28
            abo = int(c["statistics"]["subscriberCount"])
            tempo_abo = sum(x["abonnees"] for x in dagen) / 28 if dagen else 0
            # wanneer 4.000 uur: dag voor dag vooruit, met het huidige tempo erbij en de uren van 365 dagen eerder eraf
            oud = {d: u for d, u in per_dag}
            stand, datum_uren = uren, None
            for i in range(1, 3 * 365):
                dag = VANDAAG + datetime.timedelta(days=i)
                stand += tempo_uren - oud.get(dag - datetime.timedelta(days=365), 0)
                if stand >= 4000:
                    datum_uren = dag.isoformat()
                    break
            partner = {"uren": round(uren), "uren_doel": 4000, "abonnees": abo, "abonnees_doel": 1000,
                       "eerste_uren": eerste.isoformat() if eerste else None,
                       "valt_eruit_vanaf": (eerste + datetime.timedelta(days=365)).isoformat() if eerste else None,
                       "tempo_uren_per_dag": round(tempo_uren, 1), "tempo_abonnees_per_dag": round(tempo_abo, 2),
                       "datum_uren": datum_uren,
                       "datum_abonnees": ((VANDAAG + datetime.timedelta(days=int((1000 - abo) / tempo_abo) + 1)).isoformat()
                                          if tempo_abo > 0 and abo < 1000 else None)}
        except Exception:
            pass
        return {"naam": c["snippet"]["title"], "abonnees": int(c["statistics"]["subscriberCount"]),
                "views_totaal": int(c["statistics"]["viewCount"]), "video_aantal": int(c["statistics"]["videoCount"]),
                "week": nu, "vorige_week": voor, "recent": recent, "dagen": dagen, "maand": maand,
                "vorige_maand": vorige_maand, "jaar": jaar, "top": top, "partner": partner}, True
    except Exception as e:
        return {"fout": str(e)[:120]}, False


# ---------- logboek en fouten ----------
def logboek():
    uit = []
    for r in lees(STORIES / "ROUTINE-LOG.md", 60):
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (.+)$", r)
        if m:
            uit.append({"tijd": m.group(1), "tekst": schoon(m.group(2))})
    for r in lees(LOGS["testvolgorde"], 400) + lees(Path(r"C:\Users\rane\tombstone-opnieuw.log"), 200) + lees(LOGS["nachttest"], 200) + lees(LOGS["tombstone"], 100) + lees(LOGS["testvervolg"], 200) + lees(LOGS["hervat"], 300) + lees(Path(r"C:\Users\rane\opnieuw-keten.log"), 200):
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


def productie(v):
    """Stappen script, stem, beelden, edit, upload van één video (uit de bestanden op de pc), voor de productietabel
    (eigenaar 16 nov 2026: website simpel, zoals het voorbeeld met per video de stappen en hoeveel procent klaar)."""
    d = STORIES / v["map"]
    if v["soort"] in ("gepland", "online"):
        return [True] * 5
    cues = d / "script-cues.txt"
    script = cues.exists() and ((d / "src-feiten" / "deel1.txt").exists() or (d / "src").exists())
    voice = d / "voice.mp3"
    stem = script and voice.exists() and voice.stat().st_mtime >= cues.stat().st_mtime - 60
    try:
        nodig = sum(1 for r in (d / "prompts.txt").read_text(encoding="utf-8").splitlines() if "|" in r and not r.startswith("#"))
    except Exception:
        nodig = 0
    beelden = nodig > 0 and len(list((d / "afbeeldingen").glob("[0-9]*.png"))) >= nodig
    film = d / "video" / f"{v['map']}-16mm.mp4"
    edit = stem and film.exists() and film.stat().st_mtime >= voice.stat().st_mtime
    return [bool(script), bool(stem), bool(beelden), bool(edit), False]


def kleine_thumb(m):
    """thumbs/<map>.jpg uit de eigen thumbnail (v3 eerst), zodat de tabel een plaatje heeft, ook vóór de upload."""
    bron = next((STORIES / m / n for n in ("thumbnail-v3.jpg", "thumbnail-gekozen.jpg") if (STORIES / m / n).exists()), None)
    if not bron:
        return ""
    doel = DOCS / "thumbs" / f"{m}.jpg"
    try:
        if not doel.exists() or doel.stat().st_mtime < bron.stat().st_mtime:
            from PIL import Image
            doel.parent.mkdir(parents=True, exist_ok=True)
            Image.open(bron).convert("RGB").resize((320, 180)).save(doel, quality=72)
        return f"thumbs/{m}.jpg"
    except Exception:
        return ""


# ---------- alles samen ----------
video = planning()
for v in [x for x in video if x["datum"] >= VANDAAG.isoformat()]:
    v["stappen"] = productie(v)
    v["gereed"] = round(100 * sum(v["stappen"]) / 5)
    v["thumb"] = kleine_thumb(v["map"]) if v["datum"] <= (VANDAAG + datetime.timedelta(days=45)).isoformat() else ""
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
    bron = next((STORIES / actief / n for n in ("thumbnail-v3.jpg", "thumbnail-gekozen.jpg") if (STORIES / actief / n).exists()),
                STORIES / actief / "thumbnail-gekozen.jpg")
    # eigen thumbnail eerst: van een privévideo laat YouTube alleen een grijs plaatje zien
    if bron.exists():
        (DOCS / "thumbs").mkdir(parents=True, exist_ok=True)
        try:
            from PIL import Image
            Image.open(bron).convert("RGB").resize((480, 270)).save(DOCS / "thumbs" / f"{actief}.jpg", quality=75)
            thumb = f"thumbs/{actief}.jpg"
        except Exception:
            pass
    if not thumb and v.get("id"):
        thumb = f"https://i.ytimg.com/vi/{v['id']}/mqdefault.jpg"
    huidig = {"map": actief, "titel": v["titel"], "datum": v["datum"], "thumb": thumb, "stap": stap,
              "stapnaam": STAPPEN[stap] if 0 <= stap < len(STAPPEN) else "", "voortgang": proc, "detail": proc_tekst,
              "taken": [d["naam"] for d in draait], "eind": eindtijd(actief, proc)}
week = []
for i in range(7):
    dag = VANDAAG + datetime.timedelta(days=i)
    plek = dag.weekday() in (2, 5)
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
try:                                                        # 15 nov: de sitecontrole (elk half uur) moet zelf ook lopen
    sc = json.loads((Path.home() / "site-controle.json").read_text(encoding="utf-8"))
    oud = (NU - datetime.datetime.strptime(sc["laatste"], "%Y-%m-%d %H:%M")).total_seconds() / 60
    n = len(sc.get("gemeld", {}))
    zc.append({"naam": "Sitecontrole", "ok": oud < 70 and n == 0,
               "tekst": (f"laatste ronde {sc['laatste'][11:]}: " + ("alles klopt" if n == 0 else f"{n} ding(en) klopt niet, zie meldingen"))
                        if oud < 70 else f"draait niet meer (laatste ronde {sc['laatste']})"})
except Exception:
    zc.append({"naam": "Sitecontrole", "ok": False, "tekst": "nog nooit gedraaid (taak 'Sleep Archives sitecontrole')"})
for x in zc:                                              # fouten uit de zelfcontrole ook bij de meldingen
    if not x["ok"]:
        fouten.append({"tijd": NU.strftime("%Y-%m-%d %H:%M"), "tekst": f"Zelfcontrole: {x['naam']}: {x['tekst']}", "fout": True})
# ---------- duidelijke planning (eigenaar 10 nov 2026: "ik wil duidelijk de planning zien, wat er nu gebeurt en wat erna") ----------
def werkplanning():
    alle_cmd = subprocess.run(["powershell", "-NoProfile", "-Command",
                               "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CreationDate.ToString('s') + '|' + $_.CommandLine }"],
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
    for i in range(1, 29):                                   # vrije plekken (wo/za) in de komende 4 weken
        dag = VANDAAG + datetime.timedelta(days=i)
        if dag.weekday() in (2, 5) and dag.isoformat() not in bezet:
            todo.append({"map": "", "datum": dag.isoformat(), "titel": "Vrije plek: de routine kiest een populair onderwerp",
                         "soort": "vrij"})
    todo.sort(key=lambda v: v["datum"])
    bewaker_aan = bool(tk.get("bewaker") and tk["bewaker"]["aan"])
    if bewaker_aan and not routine_aan:      # 15 nov: de bewaker (elk uur) zet de video's van de komende 14 dagen op
        DG = ["ma", "di", "wo", "do", "vr", "za", "zo"]     # datumvolgorde in één keten; dat is de echte volgorde
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from keten_bewaker import te_maken
            lijst, _ = te_maken(VANDAAG)
        except Exception:
            lijst = []
        per_map = {v["map"]: v for v in video}
        for n in [n for n in lijst if not (huidig and n == huidig["map"])]:
            v = per_map.get(n, {"titel": n, "datum": ""})
            d = v.get("datum") or ""
            daarna.append({"wanneer": f"na {wacht_op[:40]}" if huidig else "bij de volgende bewakerronde (elk uur)",
                           "wat": v["titel"], "map": n,
                           "detail": (f"keten maakt de video voor {DG[datetime.date.fromisoformat(d).weekday()]} "
                                      f"{int(d[8:])}-{int(d[5:7])} 21:00") if d else "keten"})
            wacht_op = n.split("-")[0].capitalize()
        todo = []                            # de oude routine-planning (zo/di/do 09:00) geldt dan niet
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
        if not vs and dag.weekday() not in (2, 5):
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
        # 14 nov 2026: een script in de oude toon (niet TOON GOED) is nog niet klaar; het moet naar de Sleepy-opbouw
        oude_toon = nieuw and tn and tn.get("toon") != "TOON GOED" and v["soort"] not in ("gepland", "online", "bezig")
        if oude_toon:
            nieuw = False
        if v["soort"] in ("gepland", "online"):
            stand = "video staat klaar"
        elif v["soort"] == "bezig":
            stand = "video wordt gemaakt"
        elif oude_toon:
            stand = "moet nog naar de Sleepy-opbouw (zie PROMPT-SCRIPTS-DEC.md)"
        elif nieuw:
            stand = "script klaar" + (" en 's nachts goedgekeurd" if check == "GOED" else
                                      ", nachtcontrole vond iets" if check == "FOUT" else ", nachtcontrole volgt")
        elif "scriptcheck FOUT" in v["status"]:
            stand = "script afgekeurd, moet opnieuw"
        else:
            stand = "nog in de oude opbouw, moet omgebouwd"
        # 16 nov 2026 (eigenaar: "zorg dat alles op de website ook geüpdatet wordt"): per komende video de vaste afspraken
        # (stories/AFSPRAKEN.md, tools/afspraken_check.py), niet voor wat al gemaakt is of een compilatie
        afspraken = None
        if v["soort"] not in ("gepland", "online") and not v["status"].startswith("compilatie"):
            try:
                import afspraken_check
                afspraken = afspraken_check.controleer(d)
            except Exception as e:
                afspraken = [f"controle kon niet draaien: {str(e)[:80]}"]
        rij.append({"datum": v["datum"], "titel": v["titel"], "map": v["map"], "klaar": nieuw, "stand": stand,
                    "controle": check, "flesch": lb["flesch"] if lb else None, "niveau": lb["niveau"] if lb else None,
                    "leesbaar": lb["oordeel"] if lb else None, "toon": tn["toon"] if tn else None,
                    "afspraken": afspraken})
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

try:                                                         # eigenaar 19 nov 2026: planning van alle drie kanalen, deze en volgende week
    import kanalen_planning
    kp = kanalen_planning.maak(video)
except Exception as e:
    kp = {"weken": [], "regels": {}, "fouten": [str(e)[:120]]}

data = {
    "bijgewerkt": NU.strftime("%Y-%m-%d %H:%M"),
    "kanalen": kp,
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
    # hype-wachter (eigenaar 12 nov 2026: "die je dan een seintje geeft op tijd"): tools/hype_wacht.py, elke dag 08:30
    "hype": json.loads((STORIES / "hype.json").read_text(encoding="utf-8")) if (STORIES / "hype.json").exists() else None,
    # titelwachter (eigenaar 15 nov 2026: "hype wachter zorgt dat elke titel goed gekozen is"): tools/titel_wacht.py
    "titels": json.loads((STORIES / "titels.json").read_text(encoding="utf-8")) if (STORIES / "titels.json").exists() else None,
    # Claude-gebruik (eigenaar 15 nov 2026): tools/claude_gebruik.py, alleen tellen, geen sleutels
    "claude": (lambda r: json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip().startswith("{") else None)(
        subprocess.run([sys.executable, str(HIER / "claude_gebruik.py"), "--json"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=240)),
    "vast": {"Stem": "eigen stem 'Yesss' (OmniVoice), snelheid 0.9, pauzes max 2 s",
             "Achtergrond": "open haard + B-effect (432 Hz), 10 LUFS onder de stem",
             "Beeld": "16mm-look met warme vuurgloed en zwevende vonken over de hele video",
             "Beelden": "historisch juist (kenmerkenlijst per video voor bekende schepen en gebouwen), geen beelden die op elkaar lijken en geen kopieën; beeldenwachter elk uur",
             "Opbouw": "zoals Sleepy History: kort begin, ± 90 blokken (feit, uitleg, bewijs, nuance, slotgedachte), kort slot",
             "Planning": "wo en za 21:00 (NL), 2x per week (eigenaar 19 nov); zo dat het beste is voor het kanaal en mee met de hype (hype-wachter, elke dag 08:30)",
             "Thumbnail": "stijl zoals Babylon (maanlogo, groot wit onderwerp, geel jaartal); rechts het kenmerkende beeld met mensen van toen die doen wat er gebeurde, nooit een losse vrouw",
             "Scripts": "stories/PROMPT-SCRIPTS-DEC.md: hoofdsessie ijstijd, blackbeard, alchemie (klaar); ander account rome, zwarte-dood, scott, londen, bethlehem, japan"},
}
DOCS.mkdir(parents=True, exist_ok=True)
UIT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print("dashboard bijgewerkt:", data["bijgewerkt"], "| stap:", stap, actief, proc, "| nu:", ", ".join(d["naam"] for d in draait) or "niets")
if ONLINE and "--niet-pushen" not in sys.argv:                          # via de wachtrij (tools/gitveilig.py), geen botsingen
    from gitveilig import bewaar
    bewaar([DOCS], f"dashboard {data['bijgewerkt']}")
