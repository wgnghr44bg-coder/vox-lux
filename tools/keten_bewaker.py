"""Keten-bewaker (eigenaar 13 nov 2026: "zorg ervoor dat hij niet meer vastloopt en gewoon aan de planning houdt").

Elk uur (Taakplanner "Sleep Archives bewaker") op de pc, kost niets:
  - draait er al een keten (tools/routine_lokaal.py)? dan niets doen, behalve als hij al 3 uur (bij uploaden 8 uur)
    niets meer wegschrijft: dan hangt hij en stopt de waakhond hem (15 nov);
  - anders: van de video's met een datum in de komende 14 dagen die nog gemaakt moeten worden, de eerste op datum
    in een nieuwe keten zetten (routine_lokaal.py --opnieuw "a!"). Na elke video roept de keten de bewaker meteen
    weer aan (--wacht-op <pid>), dus er gaat geen uur verloren en een vroegere datum gaat altijd voor (15 nov).
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


def pids(patroon):
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          # alleen python-processen: deze powershell-opdracht bevat zelf ook 'routine_lokaal' en zag
                          # zichzelf altijd als draaiende keten, waardoor de bewaker nooit iets startte (gevonden 15 nov)
                          f"Get-CimInstance Win32_Process | ? {{ $_.Name -match 'python' -and $_.CommandLine -match '{patroon}' }} "
                          "| % { $_.ProcessId }"],
                         capture_output=True, text=True, timeout=90).stdout
    return [int(x) for x in out.split() if x.strip().isdigit()]


def keten_draait():
    return bool(pids("routine_lokaal"))


# 15 nov 2026 (eigenaar: "zorg dat hij niet meer vastloopt"): waakhond. Een keten schrijft altijd ergens iets weg
# (beelden, stemclips, video's, logboek). Is er zo lang niets veranderd, dan hangt hij (ComfyUI, Ollama of ffmpeg die
# niet meer reageert): keten met alles eronder stoppen; daarna start de bewaker hem gewoon opnieuw.
STIL_UUR = 3          # tijdens uploaden (vervang_video.py) mag het langer stil zijn
STIL_UUR_UPLOAD = 8


def laatste_activiteit():
    nieuwst = 0.0
    for p in [LOG, KETENLOG] + list(Path.home().glob("*.log")):
        try:
            nieuwst = max(nieuwst, p.stat().st_mtime)
        except OSError:
            pass
    for wortel, mappen, bestanden in os.walk(STORIES):
        if wortel.count(os.sep) - str(STORIES).count(os.sep) >= 3:
            mappen[:] = []
        for b in bestanden:
            try:
                nieuwst = max(nieuwst, os.stat(os.path.join(wortel, b)).st_mtime)
            except OSError:
                pass
    return dt.datetime.fromtimestamp(nieuwst)


def waakhond(droog=False):
    stil = dt.datetime.now() - laatste_activiteit()
    grens = STIL_UUR_UPLOAD if pids("vervang_video") else STIL_UUR
    if stil < dt.timedelta(hours=grens):
        return False
    uren = stil.total_seconds() / 3600
    print(f"keten lijkt vast: al {uren:.1f} uur niets veranderd")
    if droog:
        return False
    for pid in pids("routine_lokaal"):
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)
    log(f"keten GESTOPT door de waakhond: al {uren:.1f} uur niets veranderd (vastgelopen); wordt opnieuw gestart")
    return True


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
        if status.startswith("compilatie"):                # 15 nov: compilaties gaan (nog) niet via de gewone keten
            continue
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
    if "--wacht-op" in sys.argv:                            # aangeroepen door een keten die net klaar is
        import time
        pid = sys.argv[sys.argv.index("--wacht-op") + 1]
        for _ in range(240):
            if pid not in subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout:
                break
            time.sleep(15)
        vandaag = dt.date.today()
    slot = Path.home() / "gpu-bezet.lock"                 # 19 nov 2026: andere kanalen (NOIRTRACES/BlackswanVault) gebruiken de videokaart
    if slot.exists() and dt.datetime.now().timestamp() - slot.stat().st_mtime < 12 * 3600:
        print("videokaart bezet door ander kanaal:", slot.read_text(errors="replace").strip()[:80])
        return
    swan = pids(r'(render\w*|[\\/ ]stem|maak_short|[\\/ ]mix)\.py')     # 21 nov 2026: BlackswanVault/Geldverhaal renderen gaat voor (weinig geheugen)
    if swan and not keten_draait():
        print("BlackswanVault/Geldverhaal is bezig (pid", swan, "), Sleep wacht")
        return
    if keten_draait():
        if not waakhond(droog):
            print("keten draait al")
            return
        import time
        time.sleep(20)
    sys.path.insert(0, str(HIER))
    from gitveilig import bewaar
    if not droog:
        bewaar([], "")                                      # veilig pull (wachtrij), niet meer rechtstreeks git pull
    lijst, seintjes = te_maken(vandaag)
    if not droog:                                           # 16 nov: beelden-wachter, ontbrekende kenmerken dagen vooruit
        try:
            import beelden_wachter
            beelden_wachter.alle()
        except Exception as e:
            print("beelden-wachter:", e)
    oud = LOG.read_text(encoding="utf-8", errors="replace")
    for s in seintjes:
        print("SEINTJE", s)
        if not droog and f"bewaker: SEINTJE {s}" not in oud:
            log(f"SEINTJE {s}")
    if not lijst:
        print("niets te maken")
        return
    print("te maken:", ", ".join(lijst))
    # 15 nov 2026: één video per keten. Na elke video kiest de bewaker opnieuw (de keten roept hem aan), zodat een video
    # met een vroegere datum nooit achter een lange keten hoeft te wachten en nieuwe fixes/scripts meteen meetellen.
    lijst = lijst[:1]
    if droog:
        return
    log(f"keten gestart voor {', '.join(lijst)}")
    with open(KETENLOG, "a", encoding="utf-8") as f:
        f.write(f"\n===== {dt.datetime.now():%Y-%m-%d %H:%M} {', '.join(lijst)}\n")
        f.flush()
        cmd = [sys.executable, "-u", str(HIER / "routine_lokaal.py"), "--opnieuw", ",".join(n + "!" for n in lijst)]
        vlag = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
        kw = dict(cwd=REPO, stdout=f, stderr=subprocess.STDOUT, env={**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"})
        try:                                                # los van de Taakplanner-taak, zodat de keten blijft lopen
            subprocess.Popen(cmd, creationflags=vlag | subprocess.CREATE_BREAKAWAY_FROM_JOB, **kw)
        except OSError:
            subprocess.Popen(cmd, creationflags=vlag, **kw)


if __name__ == "__main__":
    main()
