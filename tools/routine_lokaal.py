"""De routine zonder Claude (eigenaar 8 nov 2026: "alles automatisch en via de pc", "zonder Claude", "extra controle op
verkeerde beelden"). Doet wat stories/PROMPT-ROUTINE-PC.md beschrijft, met gewone programma's en lokale modellen:

 1. git pull; een hangende video (status "bezig (... routine-lokaal)") eerst afmaken
 2. de eerstvolgende open plek kiezen (ma/wo/za 21:00, minstens 2 dagen vooruit): een script-klaar met die datum, anders
    (vrije plek) het eerste reservescript; nog niet omgebouwd -> tools/scriptgen/generator.py
 3. status "bezig", push
 4. ComfyUI starten indien nodig, beelden maken (comfy_batch), dubbele beeldcontrole (tools/beeldcheck.py)
 5. thumbnail (gekozen bestand, of 3 maken en de beste kiezen zonder uren)
 6. tools/b1_check.py en tools/check_afwisseling.py
 7. stem (engine_stem) + tekstcontrole met herstel, montage (montage_engine.sh), QC
 8. uploaden en controleren (tools/vervang_video.py), planning "klaar", opruimen
Bij elke fout: niets online, status terug naar script-klaar, melding in stories/ROUTINE-LOG.md.

  python tools/routine_lokaal.py            # één video
  python tools/routine_lokaal.py --plan     # alleen laten zien welke video en welke datum
"""
import datetime, json, re, subprocess, sys, time
from pathlib import Path

import requests

HIER = Path(__file__).resolve().parent
REPO = HIER.parent
STORIES = REPO / "stories"
OMNI = r"C:/Users/rane/omnivoice-venv/Scripts/python.exe"
BASH = r"C:\Program Files\Git\bin\bash.exe"
COMFY_BAT = r"C:\Users\rane\Downloads\ComfyUI_windows_portable_nvidia\ComfyUI_windows_portable\run_nvidia_gpu.bat"
sys.path.insert(0, str(HIER / "scriptgen"))


def log(t):
    r = f"- {datetime.datetime.now():%Y-%m-%d %H:%M} routine-lokaal: {t}\n"
    print(r, end="", flush=True)
    with open(STORIES / "ROUTINE-LOG.md", "a", encoding="utf-8") as f:
        f.write(r)


def run(cmd, **kw):
    print("$", " ".join(map(str, cmd))[:200], flush=True)
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def git_push(paden, boodschap):
    run(["git", "add"] + [str(p) for p in paden])
    run(["git", "commit", "-q", "-m", boodschap])
    run(["git", "pull", "-q", "--rebase", "--autostash"])
    run(["git", "push", "-q", "origin", "main"])


def planning(m):
    t = (m / "planning.txt").read_text(encoding="utf-8") if (m / "planning.txt").exists() else ""
    d = re.search(r"^datum\s+\S+\s+(\d{4}-\d{2}-\d{2})", t, re.M)
    s = (re.search(r"^status\s+(.+)$", t, re.M) or [None, ""])[1]
    return t, (d.group(1) if d else ""), s


def zet_status(m, status):
    t = (m / "planning.txt").read_text(encoding="utf-8")
    (m / "planning.txt").write_text(re.sub(r"^status .*$", f"status   {status}", t, count=1, flags=re.M), encoding="utf-8")


def kies(alleen_kijken=False):
    # hangende video eerst
    for m in STORIES.iterdir():
        if m.is_dir() and "routine-lokaal" in planning(m)[2] and planning(m)[2].startswith("bezig"):
            return m, planning(m)[1]
    bezet = {planning(m)[1] for m in STORIES.iterdir() if m.is_dir() and planning(m)[1]}
    dag = datetime.date.today() + datetime.timedelta(days=2)
    for _ in range(60):
        if dag.weekday() in (0, 2, 5):                      # ma, wo, za
            d = dag.isoformat()
            klaar = [m for m in STORIES.iterdir() if m.is_dir() and planning(m)[1] == d and planning(m)[2].startswith("script-klaar")]
            if klaar:
                return klaar[0], d
            if d not in bezet:                              # vrije plek: eerste reservescript
                res = sorted(m for m in STORIES.iterdir() if m.is_dir() and "reserve" in planning(m)[0]
                             and planning(m)[2].startswith("script-klaar"))
                if res and alleen_kijken:
                    return res[0], d
                if res:
                    t = planning(res[0])[0]
                    dagnaam = ["ma", "di", "wo", "do", "vr", "za", "zo"][dag.weekday()]
                    (res[0] / "planning.txt").write_text(re.sub(r"^datum .*$", f"datum    {dagnaam} {d} 21:00 NL", t, count=1,
                                                                flags=re.M), encoding="utf-8")
                    return res[0], d
        dag += datetime.timedelta(days=1)
    return None, None


def comfy_aan():
    try:
        requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
        return True
    except Exception:
        subprocess.Popen(["cmd", "/c", COMFY_BAT], cwd=str(Path(COMFY_BAT).parent), creationflags=0x08000000)
        for _ in range(60):
            time.sleep(10)
            try:
                requests.get("http://127.0.0.1:8188/system_stats", timeout=5)
                return True
            except Exception:
                pass
    return False


def thumbnail(m, plan_t):
    g = re.search(r"thumbnail gekozen[^\n]*?([\w/.-]+\.jpg)", plan_t)
    if g:
        p = REPO / g.group(1) if "/" in g.group(1) else m / g.group(1)
        if p.exists() and not toont_uren(p):              # door de eigenaar gekozen: houden, behalve met uren erop
            return p
    import beeldcheck as bc
    regel = (re.search(r"^thumbnail (.+)$", plan_t, re.M) or [None, ""])[1]
    amber = (re.search(r'amberregel "([^"]+)"', regel) or [None, ""])[1]
    beeld = (re.search(r"beeld:\s*(.+)$", regel) or [None, regel])[1]
    titel = (re.search(r"^titel\s+(.+?)\s*\|", plan_t, re.M) or [None, m.name])[1]
    import llm
    eng = llm.vraag(f"Translate to one English image prompt sentence (only the sentence): {beeld}", temp=0.2, max_tokens=120)
    hook = llm.vraag(f"From the video title '{titel}', give 2-4 big thumbnail words (no question mark, no hours). Only the words.",
                     temp=0.3, max_tokens=15).strip().strip('"')
    if not amber:
        amber = llm.vraag(f"Give a short line 'PLACE · YEAR' in capitals for a thumbnail of: {titel}. Only the line.",
                          temp=0.2, max_tokens=15).strip()
    stijl = bc.stijl(m)
    (m / "thumb").mkdir(exist_ok=True)
    (m / "thumb" / "prompts.txt").write_text("".join(
        f"t{i}|{' '.join(eng.split())}, the main subject large on the right, the lower left calmer and darker, "
        f"{stijl}\n" for i in (1, 2, 3)), encoding="utf-8")
    bc.vlm_vrij()
    run([sys.executable, str(HIER / "comfy" / "comfy_batch.py"), str(HIER / "comfy" / "zimage_api.json"), str(m / "thumb")])
    bc.comfy_vrij()
    beste, score = None, -1
    for i in (1, 2, 3):
        p = m / "thumb" / "afbeeldingen" / f"t{i}.png"
        if not p.exists() or bc.vlm(p, eng, f"the time of the video '{titel}'") or bc.clip_fout(bc.clip_scores([p], bc.jaar(m))[0]):
            continue
        uit = m / "thumb" / f"thumbnail-{i}.jpg"
        run([sys.executable, str(HIER / "make_thumbnail.py"), str(p), str(uit), "--hook", hook, "--title", amber])
        s = vlm_cijfer(uit)
        if uit.exists() and s > score:
            beste, score = uit, s
    bc.vlm_vrij()
    if beste:
        doel = m / "thumbnail-gekozen.jpg"
        doel.write_bytes(beste.read_bytes())
        return doel
    return None


def toont_uren(p):
    """Staat er een aantal uren op de thumbnail (bv. "2+ HOURS")? Dan een nieuwe maken (eigenaar: nooit uren)."""
    import base64
    vraag = ('Read all text on this thumbnail. Does it mention a number of hours (like "2 HOURS" or "3+ HOURS")? '
             'JSON: {"text": "...", "hours": true or false}')
    try:
        r = requests.post("http://127.0.0.1:11434/api/chat", json={"model": "qwen2.5vl:7b", "stream": False, "format": "json",
            "options": {"temperature": 0}, "messages": [{"role": "user", "content": vraag,
            "images": [base64.b64encode(p.read_bytes()).decode()]}]}, timeout=600)
        a = json.loads(r.json()["message"]["content"])
        return bool(a.get("hours")) or bool(re.search(r"\bhours?\b", str(a.get("text", "")), re.I))
    except Exception:
        return True


def vlm_cijfer(p):
    import base64
    try:
        r = requests.post("http://127.0.0.1:11434/api/chat", json={"model": "qwen2.5vl:7b", "stream": False, "format": "json",
            "options": {"temperature": 0}, "messages": [{"role": "user", "images": [base64.b64encode(p.read_bytes()).decode()],
            "content": 'Rate this YouTube thumbnail 1-10: is the main subject clear and striking, is the text fully readable '
                       'and not over a face, no strange letters or shapes? JSON: {"score": n}'}]}, timeout=600)
        return int(json.loads(r.json()["message"]["content"]).get("score", 0))
    except Exception:
        return 0


def maak_video(m, datum, test=False):
    plan_t = planning(m)[0]
    if "nieuwe opbouw" not in planning(m)[2] and not (m / "src-feiten" / "begin.txt").exists():
        import generator
        if not generator.maak(m, test=True):
            raise RuntimeError("script ombouwen mislukt")
        plan_t = planning(m)[0]
    if not test:
        zet_status(m, f"bezig ({datetime.date.today()}, routine-lokaal)")
        git_push([m], f"{m.name}: bezig (routine-lokaal) voor {datum}")

    if not comfy_aan():
        raise RuntimeError("ComfyUI start niet")
    r = run([sys.executable, str(HIER / "comfy" / "comfy_batch.py"), str(HIER / "comfy" / "zimage_api.json"), str(m)])
    print(r.stdout[-500:])
    r = run([OMNI, str(HIER / "beeldcheck.py"), str(m)])
    print(r.stdout[-1500:])
    if "BEELDEN GOED" not in r.stdout:
        raise RuntimeError("beeldcontrole: " + r.stdout.strip().splitlines()[-1][:200])
    thumb = thumbnail(m, plan_t)
    if not thumb:
        raise RuntimeError("geen goede thumbnail")
    if test:                                                # --test-tot-beelden: hier stoppen, niets online
        log(f"{m.name}: TEST tot en met beelden en thumbnail GOED ({thumb.name})")
        return

    for cmd, goed in (([OMNI, str(HIER / "b1_check.py")], "B1 GOED"),
                      ([sys.executable, str(HIER / "check_afwisseling.py"), str(m)], "AFWISSELING GOED")):
        r = run(cmd)
        if goed not in r.stdout:
            raise RuntimeError(r.stdout.strip().splitlines()[-1][:200] if r.stdout.strip() else goed + " ontbreekt")

    print(run([OMNI, str(HIER / "engine_stem.py"), str(m)]).stdout[-400:])
    for ronde in range(1, 5):
        r = run([BASH, "tools/prep_engine.sh", m.name], env={**__import__("os").environ, "REPO": str(REPO).replace("\\", "/")})
        fout = re.search(r"TEKST FOUT.*?" + re.escape(m.name) + r"\s+([\d ]+)$", r.stdout, re.M)
        if not fout:
            break
        if ronde == 4:
            raise RuntimeError("tekstfouten na 3 herstelrondes")
        run([OMNI, str(HIER / "engine_stem.py"), str(m), "--hergebruik", "--opnieuw", ",".join(fout.group(1).split()),
             "--seed-extra", str(3000 * ronde)])
    titel = (re.search(r"^titel\s+(.+?\| History for Sleep)", planning(m)[0], re.M) or [None, ""])[1]
    r = run([BASH, "tools/montage_engine.sh", m.name, titel, thumb.relative_to(m).as_posix()],
            env={**__import__("os").environ, "REPO": str(REPO).replace("\\", "/")})
    print(r.stdout[-3000:])
    if not ("CONTROLE GOED" in r.stdout and "TEKST GOED" in r.stdout and "APPROVED" in r.stdout):
        raise RuntimeError("montage-controles niet goed")
    soort = (re.search(r"^soort\s+(\S+)", planning(m)[0], re.M) or [None, "mysterie"])[1]
    r = run([sys.executable, str(HIER / "vervang_video.py"), str(m), "--video", str(m / "video" / f"{m.name}-16mm.mp4"),
             "--publish-at", f"{datum}T20:00:00Z", "--thumbnail", str(thumb), "--soort", soort])
    print(r.stdout[-1500:])
    if "KLAAR" not in r.stdout:
        raise RuntimeError("upload/verwerking niet klaar (zie ROUTINE-LOG)")


if __name__ == "__main__":
    if "--test-tot-beelden" in sys.argv:                    # proef: één map, alleen beelden + controle + thumbnail
        m = Path(sys.argv[sys.argv.index("--test-tot-beelden") + 1]).resolve()
        try:
            maak_video(m, planning(m)[1], test=True)
        except Exception as e:
            log(f"{m.name}: TEST GESTOPT ({e})")
            sys.exit(1)
        sys.exit(0)
    run(["git", "checkout", "-q", "main"])
    run(["git", "pull", "-q"])
    m, datum = kies(alleen_kijken="--plan" in sys.argv)
    if "--plan" in sys.argv:
        print("volgende video:", m and m.name, "op", datum)
        sys.exit(0)
    if not m:
        log("geen script en geen vrije plek gevonden")
        sys.exit(0)
    log(f"{m.name}: start voor {datum} 21:00")
    try:
        maak_video(m, datum)
        log(f"{m.name}: KLAAR, gepland op {datum} 21:00")
    except Exception as e:
        log(f"{m.name}: GESTOPT ({e}); niets online gezet")
        try:
            zet_status(m, "script-klaar (nieuwe opbouw, terug na fout in routine-lokaal)")
            git_push([m / "planning.txt", STORIES / "ROUTINE-LOG.md"], f"{m.name}: routine-lokaal gestopt ({e})"[:120])
        except Exception:
            pass
        sys.exit(1)
