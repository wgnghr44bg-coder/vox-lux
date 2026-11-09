"""Git zonder botsingen (9 nov 2026): website-update, zelfcontrole, upload en generator pushen allemaal naar GitHub; als ze
tegelijk bezig waren gaf dat "index.lock exists" of een half afgemaakte rebase. Hier wachten ze op elkaar (één slot op
de pc) en wordt een achtergebleven slot of rebase veilig opgeruimd.

  from gitveilig import bewaar
  bewaar(["docs/status"], "dashboard 2026-11-09 09:33")      # add + commit (als er iets is) + pull --rebase --autostash + push
"""
import msvcrt, os, subprocess, time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SLOT = Path(r"C:\Users\rane\vox-lux-git.slot")


def _git(*a):
    return subprocess.run(["git", *a], cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")


def _opruimen():
    lock = REPO / ".git" / "index.lock"
    if lock.exists() and time.time() - lock.stat().st_mtime > 300:   # slot van een gecrasht proces (> 5 min oud)
        lock.unlink()
    rm = REPO / ".git" / "rebase-merge"
    if rm.exists() and time.time() - rm.stat().st_mtime > 300:
        auto = rm / "autostash"
        if auto.exists():
            _git("stash", "store", "-m", "autostash bewaard door gitveilig", auto.read_text().strip())
        _git("rebase", "--quit")


def bewaar(paden, boodschap, pushen=True, wacht=900):
    SLOT.touch(exist_ok=True)
    with open(SLOT, "r+") as f:
        begin = time.time()
        while True:
            try:
                msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
                break
            except OSError:
                if time.time() - begin > wacht:
                    return False
                time.sleep(3)
        try:
            _opruimen()
            for _ in range(5):
                if not (REPO / ".git" / "index.lock").exists():
                    break
                time.sleep(5)
            _git("add", *[str(p) for p in paden])
            if _git("diff", "--cached", "--quiet").returncode:
                _git("commit", "-q", "-m", boodschap + "\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
            if pushen:
                for poging in range(3):
                    _git("pull", "-q", "--rebase", "--autostash")
                    if _git("push", "-q", "origin", "main").returncode == 0:
                        return True
                    time.sleep(10 * (poging + 1))
            return not pushen
        finally:
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, 1)
