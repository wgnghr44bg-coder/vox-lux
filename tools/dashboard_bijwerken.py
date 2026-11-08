"""Werkt het statusdashboard bij: https://wgnghr44bg-coder.github.io/vox-lux/status/ (eigenaar 8 nov 2026: "een website
via GitHub zodat ik alles kan zien wat er loopt: script, video, planning, alles via de pc").

Verzamelt op de pc: planning van alle video's (stories/*/planning.txt), wat er nu draait (processen, logs), het
logboek (stories/ROUTINE-LOG.md) en de videokaart; schrijft docs/status/data.json en pusht ALLEEN dat bestand.
Geen geheimen: geen sleutels, tokens of wachtwoorden, alleen wat al in de (openbare) repo staat plus de stand van de pc.

  python tools/dashboard_bijwerken.py            # bijwerken en pushen
  python tools/dashboard_bijwerken.py --niet-pushen
"""
import datetime, json, re, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
UIT = REPO / "docs" / "status" / "data.json"
LOGS = {"testvolgorde": Path(r"C:\Users\rane\testvolgorde.log"),
        "scriptgenerator": Path(r"C:\Users\rane\sleep-archives-scripts-log.txt"),
        "routine": Path(r"C:\Users\rane\sleep-archives-routine-log.txt")}


def lees(p, n=None):
    try:
        t = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        try:
            t = p.read_text(encoding="utf-16", errors="replace")
        except Exception:
            return []
    regels = [r.rstrip() for r in t.splitlines() if r.strip()]
    return regels[-n:] if n else regels


def planning():
    uit = []
    for m in sorted(STORIES.iterdir()):
        p = m / "planning.txt"
        if not m.is_dir() or not p.exists() or m.name.startswith("_"):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        g = lambda k: (re.search(rf"^{k}\s+(.+)$", t, re.M) or [None, ""])[1].strip()
        d = re.search(r"(\d{4}-\d{2}-\d{2})", g("datum"))
        link = re.search(r"https://youtu\.be/[A-Za-z0-9_-]{11}", t)
        status = g("status") or ("klaar" if link else "")
        titel = re.sub(r"\s*\(.*$", "", g("titel")) or g("onderwerp")
        vandaag = datetime.date.today().isoformat()
        soort = ("gepland" if link and status.startswith("klaar") and d and d.group(1) > vandaag else
                 "online" if link and status.startswith("klaar") else
                 "bezig" if status.startswith(("bezig", "in-wording")) else
                 "script nieuw" if "nieuwe opbouw" in status else
                 "script oud" if status.startswith("script-klaar") else status.split(" ")[0] or "?")
        uit.append({"map": m.name, "datum": d.group(1) if d else "", "reserve": "reserve" in g("datum"),
                    "titel": titel[:110], "onderwerp": g("onderwerp")[:90], "status": status[:140], "soort": soort,
                    "link": link.group(0) if link else "", "afspeellijst": g("soort").split(" ")[0],
                    "opening": g("opening").split(" ")[0], "beelden": len(list((m / "afbeeldingen").glob("*.png")))
                    if (m / "afbeeldingen").is_dir() else 0})
    return uit


def processen():
    """Wat draait er nu op de pc (alleen herkende onderdelen, geen paden of argumenten)."""
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CommandLine }"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60).stdout
    except Exception:
        out = ""
    namen = {"engine_stem.py": "stem inspreken", "prep_engine.sh": "tekstcontrole", "make_video.py": "montage: beelden",
             "motion.py": "montage: beweging", "film16.py": "montage: 16mm-look", "qc_video.py": "kwaliteitscontrole",
             "engine_muziek.py": "muziek maken", "comfy_batch.py": "beelden maken (ComfyUI)", "beeldcheck.py": "beeldcontrole",
             "vervang_video.py": "uploaden / verwerking", "wacht_verwerkt.py": "wachten op YouTube",
             "scriptgen\\generator.py": "script schrijven (lokaal)", "scriptgen/generator.py": "script schrijven (lokaal)",
             "routine_lokaal.py": "routine zonder Claude", "PROMPT-ROUTINE-PC": "routine (met Claude)",
             "PROMPT-SCRIPT-PC": "scriptgenerator (met Claude)", "testvolgorde.ps1": "testvolgorde",
             "herstel_zinnen.py": "zinnen herstellen", "check_stem_tekst.py": "tekstcontrole (Whisper)"}
    gevonden = []
    for regel in out.splitlines():
        for k, v in namen.items():
            if k in regel and v not in gevonden:
                gevonden.append(v)
    return gevonden


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
    for naam in ("Sleep Archives routine", "Sleep Archives scriptgenerator"):
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                                f"$i = Get-ScheduledTask -TaskName '{naam}' | Get-ScheduledTaskInfo; "
                                "\"$($i.LastRunTime.ToString('yyyy-MM-dd HH:mm'))|$($i.NextRunTime.ToString('yyyy-MM-dd HH:mm'))|$($i.LastTaskResult)\""],
                               capture_output=True, text=True, timeout=60).stdout.strip()
            laatst, volgend, res = r.split("|")
            laatst = "nog niet" if laatst.startswith("1999") else laatst
            uit[naam] = {"laatst": laatst, "volgende": volgend, "resultaat": res}
        except Exception:
            uit[naam] = None
    return uit


def schoon(regels):
    """Logregels zonder paden naar de pc."""
    return [re.sub(r"[A-Z]:\\[^\s'\"]+", "…", r)[:220] for r in regels]


data = {
    "bijgewerkt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
    "nu_bezig": processen(),
    "videokaart": gpu(),
    "taken": taken(),
    "video": planning(),
    "logboek": schoon(lees(STORIES / "ROUTINE-LOG.md", 40)),
    "logs": {k: schoon([r for r in lees(p, 400) if r.startswith("===") or "GOED" in r or "FOUT" in r
                        or "KLAAR" in r or "MISLUKT" in r or "GESTOPT" in r][-14:]) for k, p in LOGS.items()},
    "vast": {"stem": "B1: narrator-e (OmniVoice), speed 0.54, pauzes ×1,4, warme klank",
             "muziek": "W3: diep en donker-warm, 432 Hz, elke 6 s een ander akkoord, 11 LUFS onder de stem",
             "opbouw": "begin ± 2 min (zonder Tonight), 8-13 onderwerpen met feitjes, slot dat uitdooft",
             "planning": "ma, wo en za 21:00 (NL)"},
}
UIT.parent.mkdir(parents=True, exist_ok=True)
UIT.write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
print("dashboard bijgewerkt:", data["bijgewerkt"], "| nu:", ", ".join(data["nu_bezig"]) or "niets")
if "--niet-pushen" not in sys.argv:
    g = lambda *a: subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True)
    g("add", str(UIT))
    if g("diff", "--cached", "--quiet").returncode:
        g("commit", "-q", "-m", f"dashboard {data['bijgewerkt']}")
        g("pull", "-q", "--rebase")
        g("push", "-q", "origin", "main")
