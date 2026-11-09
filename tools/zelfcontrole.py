"""Zelfcontrole van de pc (eigenaar 9 nov 2026: "hij moet dat zelf doen vanuit de pc controleren of alles goed werkt").
Wordt elk half uur aangeroepen door tools/dashboard_bijwerken.py; de uitslag staat op de website (paneel Zelfcontrole).

Licht (elke keer):
  - programma's: Ollama, ComfyUI, ffmpeg, OmniVoice-omgeving, YouTube-koppeling
  - Taakplanner: laatste uitslag van routine / scriptgenerator / dashboard
  - schijfruimte (C:)
  - git: vastgelopen rebase (zoals 9 nov 06:03) wordt veilig opgelost: autostash bewaard als stash, rebase gestopt
  - planning: staat de eerstvolgende video (binnen 2 dagen) op tijd op YouTube?
Zwaar (één keer per nacht tussen 01:00 en 05:00, alleen als de videokaart vrij is):
  - tools/b1_check.py (stem en muziek nog precies B1 + W3?)
  - tools/script_check.py op scripts in de nieuwe opbouw die nog niet (of niet na de laatste wijziging) zijn gecontroleerd
    (max 3 per nacht). Afgekeurd -> status terug naar "script-klaar (oude opbouw; scriptcheck FOUT ...)", zodat de
    scriptgenerator het opnieuw ombouwt en de routine het niet zo gebruikt.
"""
import datetime, json, re, shutil, subprocess, sys
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
STAAT = Path(r"C:\Users\rane\zelfcontrole-staat.json")
OMNI = r"C:\Users\rane\omnivoice-venv\Scripts\python.exe"
NU = datetime.datetime.now()


def punt(naam, ok, tekst):
    return {"naam": naam, "ok": bool(ok), "tekst": tekst}


def http(url):
    try:
        return requests.get(url, timeout=5).status_code == 200
    except Exception:
        return False


def git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")


def gpu_vrij():
    try:
        r = subprocess.run(["nvidia-smi", "--query-compute-apps=process_name", "--format=csv,noheader"],
                           capture_output=True, text=True, timeout=20).stdout
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "Get-CimInstance Win32_Process | ? { $_.CommandLine } | % { $_.CommandLine }"],
                             capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=90).stdout
        bezig = any(k in out for k in ("engine_stem.py", "comfy_batch.py", "beeldcheck.py", "herstel_zinnen.py",
                                       "check_stem_tekst.py", "scriptgen", "PROMPT-ROUTINE-PC", "routine_lokaal.py"))
        return not bezig
    except Exception:
        return False


def licht():
    p = []
    p.append(punt("Ollama (lokale modellen)", http("http://127.0.0.1:11434/api/tags"), "draait" if http("http://127.0.0.1:11434/api/tags") else "staat uit"))
    comfy = http("http://127.0.0.1:8188/system_stats")
    p.append(punt("ComfyUI (beelden)", comfy, "draait" if comfy else "staat uit (de routine start hem zelf)"))
    p.append(punt("ffmpeg", shutil.which("ffmpeg") is not None, "gevonden" if shutil.which("ffmpeg") else "niet gevonden"))
    p.append(punt("OmniVoice-omgeving", Path(OMNI).exists(), "gevonden" if Path(OMNI).exists() else "ontbreekt"))
    vrij = shutil.disk_usage("C:\\").free / 1e9
    p.append(punt("Schijfruimte C:", vrij > 30, f"{vrij:.0f} GB vrij" + ("" if vrij > 30 else " (te weinig voor een video, ± 30 GB nodig)")))
    for naam in ("Sleep Archives routine", "Sleep Archives scriptgenerator", "Sleep Archives dashboard"):
        try:
            r = subprocess.run(["powershell", "-NoProfile", "-Command",
                                f"$i = Get-ScheduledTask -TaskName '{naam}' | Get-ScheduledTaskInfo; \"$($i.LastTaskResult)|$($i.LastRunTime.ToString('yyyy-MM-dd HH:mm'))\""],
                               capture_output=True, text=True, timeout=60).stdout.strip()
            res, wanneer = r.split("|")
            ok = res in ("0", "267011", "267009")           # 267011 = nog nooit gedraaid, 267009 = draait nu
            p.append(punt(f"Taak '{naam.replace('Sleep Archives ', '')}'", ok,
                          {"0": "laatste keer goed", "267011": "nog niet gedraaid", "267009": "draait nu"}.get(res, f"foutcode {res}")
                          + (f" ({wanneer})" if not wanneer.startswith("1999") else "")))
        except Exception:
            p.append(punt(f"Taak '{naam.replace('Sleep Archives ', '')}'", False, "niet gevonden"))
    # git: vastgelopen rebase veilig oplossen
    rm = REPO / ".git" / "rebase-merge"
    import time as _t
    if rm.exists() and _t.time() - rm.stat().st_mtime > 300 and (not (rm / "git-rebase-todo").exists() or (rm / "git-rebase-todo").read_text().strip() == ""):
        auto = rm / "autostash"
        if auto.exists():
            git("stash", "store", "-m", f"autostash bewaard door zelfcontrole {NU:%Y-%m-%d %H:%M}", auto.read_text().strip())
        git("rebase", "--quit")
        p.append(punt("Git", True, "vastgelopen rebase gevonden en veilig opgelost (wijzigingen bewaard als stash)"))
    else:
        achter = git("log", "origin/main..main", "--oneline").stdout.strip()
        p.append(punt("Git", not achter, "alles gepusht" if not achter else f"{len(achter.splitlines())} commit(s) nog niet gepusht"))
    # planning: eerstvolgende video op tijd op YouTube?
    morgen = (NU + datetime.timedelta(days=2)).date().isoformat()
    for m in sorted(STORIES.iterdir()):
        pt = m / "planning.txt"
        if not pt.exists():
            continue
        t = pt.read_text(encoding="utf-8", errors="replace")
        d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
        if d and NU.date().isoformat() <= d.group(1) <= morgen:
            link = re.search(r"youtu\.be/", t) and re.search(r"^status\s+klaar", t, re.M)
            p.append(punt(f"Video {d.group(1)} ({m.name})", bool(link), "staat op YouTube ingepland" if link
                          else "nog NIET op YouTube (minder dan 2 dagen tot publicatie)"))
    return p


def zwaar(p):
    staat = json.loads(STAAT.read_text(encoding="utf-8")) if STAAT.exists() else {}
    vandaag = NU.date().isoformat()
    if staat.get("laatst") == vandaag or not (1 <= NU.hour < 5) or not gpu_vrij():
        if staat.get("uitslag"):
            p += [punt(x["naam"], x["ok"], x["tekst"] + f" (nacht {staat.get('laatst')})") for x in staat["uitslag"]]
        return
    uit = []
    r = subprocess.run([OMNI, str(HIER / "b1_check.py")], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    uit.append(punt("Stem en muziek (B1 + W3)", "B1 GOED" in r.stdout, r.stdout.strip().splitlines()[-1][:150] if r.stdout.strip() else "geen uitslag"))
    gecontroleerd = 0
    for m in sorted(STORIES.iterdir()):
        pt = m / "planning.txt"
        sf = m / "src-feiten"
        if gecontroleerd >= 3 or not pt.exists() or not sf.exists():
            continue
        t = pt.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"^status\s+script-klaar \(nieuwe opbouw", t, re.M):
            continue
        sc = m / "scriptcheck.json"
        nieuwste = max(f.stat().st_mtime for f in sf.glob("*.txt"))
        if sc.exists() and sc.stat().st_mtime > nieuwste:
            continue
        gecontroleerd += 1
        r = subprocess.run([sys.executable, str(HIER / "script_check.py"), str(m)], cwd=REPO, capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        goed = "SCRIPT GOED" in r.stdout
        uit.append(punt(f"Script {m.name}", goed, "SCRIPT GOED" if goed else r.stdout.strip().splitlines()[-1]))
        if not goed:                                        # niet gebruiken, opnieuw laten ombouwen
            t = re.sub(r"^status .*$", f"status   script-klaar (oude opbouw; scriptcheck FOUT {vandaag}: opnieuw ombouwen, zie scriptcheck.json)",
                       t, count=1, flags=re.M)
            pt.write_text(t, encoding="utf-8")
            with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
                f.write(f"- {NU:%Y-%m-%d %H:%M} zelfcontrole: {m.name}: SCRIPT FOUT, terug naar ombouwen (zie scriptcheck.json)\n")
        from gitveilig import bewaar
        bewaar([pt, m / "scriptcheck.json", STORIES / "ROUTINE-LOG.md"], f"zelfcontrole: {m.name} {'SCRIPT GOED' if goed else 'SCRIPT FOUT, terug naar ombouwen'}")
    STAAT.write_text(json.dumps({"laatst": vandaag, "uitslag": uit}, indent=1, ensure_ascii=False), encoding="utf-8")
    p += uit


def alles():
    p = licht()
    try:
        zwaar(p)
    except Exception as e:
        p.append(punt("Nachtcontrole", False, f"fout: {str(e)[:100]}"))
    return p


if __name__ == "__main__":
    for x in alles():
        print(("OK  " if x["ok"] else "FOUT"), x["naam"], "-", x["tekst"])
