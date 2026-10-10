#!/usr/bin/env python3
"""Save the source files of a finished video in the archive repo (ifscape3d-videos), so it can be made again later.

    python whatif-demo/archive_whatif.py 45                 # Short: <archive>/<date>-<slug>/
    python whatif-demo/archive_whatif.py 40 --chapters aliens-1-street aliens-2-news --name aliens-landed
    python whatif-demo/archive_whatif.py 45 --push          # also git push the archive (sources only, never a video)

Copies scenario.js, script.txt, voice.mp3, voice-times.tsv, timing.json, upload.json and thumbnail.jpg (when present),
writes ENGINE.txt (vox-lux branch + commit) and commits in the archive repo. Never copies mp4, stills or wav's,
and never uploads a video anywhere. Existing files in the archive are not overwritten without --force.
"""
from __future__ import annotations

import argparse
import datetime as dt
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from make_whatif import find_topic, TOPICS  # noqa: E402

FILES = ["scenario.js", "script.txt", "voice.mp3", "voice-times.tsv", "timing.json", "upload.json", "thumbnail.jpg"]


def git(*args, cwd: Path) -> str:
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


def copy_topic(src: Path, dst: Path, force: bool) -> list[str]:
    dst.mkdir(parents=True, exist_ok=True); done = []
    for name in FILES:
        f = src / name
        if not f.exists(): continue
        if (dst / name).exists() and not force:
            sys.exit(f"{dst / name} already exists (use --force to replace it)")
        shutil.copy2(f, dst / name); done.append(name)
    return done


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("number", type=int)
    ap.add_argument("--chapters", nargs="*", help="long video: topic folders (slugs) of all chapters, in order")
    ap.add_argument("--name", help="folder name after the date (default: the slug)")
    ap.add_argument("--date", default=dt.date.today().isoformat())
    ap.add_argument("--archive", type=Path, default=REPO.parent / "ifscape3d-videos")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()

    if not (a.archive / ".git").exists():
        sys.exit(f"Archive repo not found: {a.archive} (clone https://github.com/wgnghr44bg-coder/ifscape3d-videos.git there)")
    d = find_topic(a.number)
    folder = a.archive / f"{a.date}-{a.name or d.name}"
    if a.chapters:
        for slug in a.chapters:
            print(slug, copy_topic(TOPICS / slug, folder / slug, a.force))
        if (d / "thumbnail.jpg").exists(): shutil.copy2(d / "thumbnail.jpg", folder / "thumbnail.jpg")
    else:
        print(d.name, copy_topic(d, folder, a.force))
    if not (folder / "upload.json").exists() and not a.chapters:
        print("WARNING: no upload.json (render the video first with make_whatif.py)")

    branch, commit = git("rev-parse", "--abbrev-ref", "HEAD", cwd=REPO), git("rev-parse", "HEAD", cwd=REPO)
    if git("status", "--porcelain", "whatif-demo/engine", cwd=REPO):
        print("WARNING: whatif-demo/engine has uncommitted changes; commit them so ENGINE.txt points at the real engine")
    (folder / "ENGINE.txt").write_text(f"vox-lux {branch} {commit} - python whatif-demo/make_whatif.py {a.number}\n", encoding="utf-8")

    git("add", folder.name, cwd=a.archive)
    subprocess.run(["git", "commit", "-q", "-m", f"{folder.name}: bronbestanden"], cwd=a.archive, check=False)
    print("saved:", folder)
    if a.push:
        subprocess.run(["git", "push", "origin", "HEAD"], cwd=a.archive, check=True)
    else:
        print(f"push later:  git -C \"{a.archive}\" push")


if __name__ == "__main__":
    main()
