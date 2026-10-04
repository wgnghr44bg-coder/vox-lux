#!/usr/bin/env python3
"""Publish a finished 'What if' video (after make_whatif.py).

    python3 whatif-demo/publish_whatif.py 1            # check, upload (if the token exists), TikTok folder, list
    python3 whatif-demo/publish_whatif.py 1 --dry-run  # only the check and the TikTok folder

1. tools/check_video.py must say "CONTROLE GOED", otherwise nothing is uploaded (exit 1).
2. YouTube, channel "whatif" (YT_WHATIF_REFRESH_TOKEN): private, --publish-at the next day 18:00
   Europe/Amsterdam, AI label on, thumbnail. Without the token the upload is skipped (and said so).
3. TikTok: mp4 + thumbnail + tiktok.txt in whatif-demo/tiktok/<date>-<slug>/ (the session copies
   that folder to Google Drive "TikTok klaar", see AUTOMATISCH.md).
4. onderwerpen.md: status -> "geüpload <date> <link>" (or "klaar <date>, niet geüpload: ...").
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
REPO = HERE.parent
sys.path.insert(0, str(HERE))
from make_whatif import find_topic  # noqa: E402


def publish_at(now: dt.datetime | None = None) -> str:
    ams = ZoneInfo("Europe/Amsterdam")
    now = now or dt.datetime.now(ams)
    t = dt.datetime.combine(now.date() + dt.timedelta(days=1), dt.time(18, 0), ams)
    return t.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def set_status(num: int, status: str):
    p = HERE / "onderwerpen.md"
    out = []
    for line in p.read_text(encoding="utf-8").splitlines():
        cells = line.split("|")
        if len(cells) > 6 and cells[1].strip() == str(num):
            cells[5] = f" {status} "
            line = "|".join(cells)
        out.append(line)
    p.write_text("\n".join(out) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("number", type=int)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    d = find_topic(a.number); slug = d.name
    video, thumb = d / f"{slug}.mp4", d / "thumbnail.jpg"
    up = json.loads((d / "upload.json").read_text(encoding="utf-8"))
    today = dt.datetime.now(ZoneInfo("Europe/Amsterdam")).date().isoformat()

    chk = subprocess.run([sys.executable, REPO / "tools" / "check_video.py", d, video.name, "--stem", "voice.mp3", "--bron", (d / "check-bron.txt").read_text().strip() if (d / "check-bron.txt").exists() else "mix.wav"],
                         capture_output=True, text=True)
    print(chk.stdout.strip())
    if "CONTROLE GOED" not in chk.stdout:
        print("NOT uploading: check failed.", chk.stderr[-500:])
        sys.exit(1)

    # TikTok folder
    tk = HERE / "tiktok" / f"{today}-{slug}"
    tk.mkdir(parents=True, exist_ok=True)
    shutil.copy2(video, tk / video.name); shutil.copy2(thumb, tk / "thumbnail.jpg")
    (tk / "tiktok.txt").write_text(up["tiktok"] + "\n", encoding="utf-8")
    print("TikTok folder:", tk)

    if a.dry_run:
        return
    if not all(os.environ.get(k) for k in ("YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_WHATIF_REFRESH_TOKEN")):
        print("YouTube upload SKIPPED: YT_WHATIF_REFRESH_TOKEN (or client id/secret) is not set.")
        set_status(a.number, f"klaar {today}, niet geüpload (geen YT_WHATIF_REFRESH_TOKEN)")
        return
    desc = d / "description.txt"; desc.write_text(up["description"], encoding="utf-8")
    when = publish_at()
    res = subprocess.run([sys.executable, REPO / "tools" / "youtube_upload.py", video, "--channel", "whatif",
                          "--title", up["title"], "--description-file", desc, "--tags", ",".join(up["tags"]),
                          "--privacy", "private", "--publish-at", when, "--thumbnail", thumb],
                         capture_output=True, text=True)
    print(res.stdout.strip(), res.stderr.strip()[-500:])
    m = re.search(r"https://youtu\.be/[\w-]+", res.stdout)
    if res.returncode or not m:
        set_status(a.number, f"klaar {today}, upload mislukt")
        sys.exit(1)
    set_status(a.number, f"geüpload {today} {m.group(0)} (openbaar {when})")
    print("uploaded:", m.group(0), "public at", when)


if __name__ == "__main__":
    main()
