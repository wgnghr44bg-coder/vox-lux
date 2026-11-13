"""Keten-bewaker (eigenaar 13 nov 2026: "zorg ervoor dat hij niet meer vastloopt en gewoon aan de planning houdt").

Elk uur (Taakplanner "Sleep Archives bewaker") op de pc, kost niets:
  - draait er al een keten (tools/routine_lokaal.py)? dan niets doen;
  - anders: alle video's met een datum in de komende 14 dagen die nog gemaakt moeten worden, op volgorde van datum,
    in één nieuwe keten zetten (routine_lokaal.py --opnieuw "a!,b!,...").
Nog te maken = status "script-klaar"/"bezig", of "klaar" maar het script is daarna nog veranderd (bv. omgebouwd naar
de nieuwe opbouw, Egypte 13 nov). Een video die vandaag al 2 keer GESTOPT is, wordt tot morgen overgeslagen, zodat
één kapotte video de rest niet ophoudt. Video's zonder script ("script nodig") komen als SEINTJE in het logboek.

  python tools/keten_bewaker.py            # kijken en zo nodig starten
  python tools/keten_bewaker.py --droog    # alleen laten zien wat hij zou doen
"""
import datetime as dt, os, re, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
LOG = STORIES / "ROUTINE-LOG.md"
VOORUIT = 14
KETENLOG = Path.home() / "keten-bewaker.log"


def log(t):
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"- {dt.datetime.now():%Y-%m-%d %H:%M} bewaker: {t}\n")


def keten_draait():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "Get-CimInstance Win32_Process | ? { $_.CommandLine -match 'routine_lokaal' } | % { $_.ProcessId }"],
                         capture_output=True, text=True, timeout=90).stdout
    return bool(out.strip())


def script_datum(m):
    """Laatste commitdatum van het script (src-feiten of src)."""
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", f"stories/{m.name}/src-feiten", f"stories/{m.name}/src"],
                       cwd=REPO, capture_output=True, text=True).stdout.strip()
    return r or "0000-00-00"


def te_maken(vandaag):
    logtekst = LOG.read_text(encoding="utf-8", errors="replace")
    uit, seintjes = [], []
    for p in STORIES.glob("*/planning.txt"):
        t = p.read_text(encoding="utf-8", errors="replace")
        d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
        if not d or "reserve" in d.group(0):
            continue
        datum = dt.date.fromisoformat(d.group(1))
        if not vandaag <= datum <= vandaag + dt.timedelta(days=VOORUIT):
            continue
        m = p.parent
        status = (re.search(r"^status\s+(.+)$", t, re.M) or [None, ""])[1].strip()
        if status.startswith("script nodig") or not ((m / "src-feiten").exists() or (m / "src").exists()):
            seintjes.append(f"{m.name} ({datum}) heeft nog geen script")
            continue
        if status.startswith("klaar"):
            link = re.search(r"^link https://youtu\.be/\S+ \((\d{4}-\d{2}-\d{2})", t, re.M)
            if link and link.group(1) >= script_datum(m):
                continue                                    # gemaakt met het huidige script
        if datum == vandaag and dt.datetime.now().hour >= 9:
            seintjes.append(f"{m.name} ({datum}) is niet op tijd klaar te krijgen")
            continue
        gestopt = len(re.findall(rf"^- {vandaag} \d\d:\d\d .*{re.escape(m.name)}: opnieuw maken GESTOPT", logtekst, re.M))
        if gestopt >= 2:
            seintjes.append(f"{m.name} ({datum}) is vandaag {gestopt}x gestopt, morgen opnieuw")
            continue
        uit.append((datum, m.name))
    return [n for _, n in sorted(uit)], seintjes


def main():
    vandaag = dt.date.today()
    droog = "--droog" in sys.argv
    if keten_draait():
        print("keten draait al")
        return
    subprocess.run(["git", "pull", "-q", "--rebase", "--autostash"], cwd=REPO)
    lijst, seintjes = te_maken(vandaag)
    oud = LOG.read_text(encoding="utf-8", errors="replace")
    for s in seintjes:
        print("SEINTJE", s)
        if not droog and f"bewaker: SEINTJE {s}" not in oud:
            log(f"SEINTJE {s}")
    if not lijst:
        print("niets te maken")
        return
    print("te maken:", ", ".join(lijst))
    if droog:
        return
    log(f"keten gestart voor {', '.join(lijst)}")
    with open(KETENLOG, "a", encoding="utf-8") as f:
        f.write(f"\n===== {dt.datetime.now():%Y-%m-%d %H:%M} {', '.join(lijst)}\n")
        f.flush()
        subprocess.Popen([sys.executable, "-u", str(HIER / "routine_lokaal.py"), "--opnieuw", ",".join(n + "!" for n in lijst)],
                         cwd=REPO, stdout=f, stderr=subprocess.STDOUT,
                         env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"},
                         creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP)


if __name__ == "__main__":
    main()
