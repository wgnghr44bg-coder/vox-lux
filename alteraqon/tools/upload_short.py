"""Alteraqon: een goedgekeurde short op YouTube zetten (@alteraqon), met titel, beschrijving en tags uit upload.json.

ALLEEN draaien nadat de eigenaar uitdrukkelijk "zet online" heeft gezegd. Draait in de cloudsessie
(daar staat YT_REFRESH_TOKEN_ALTERAQON; nooit in git zetten).

Gebruik (vanuit de map vox-lux):
  python3 alteraqon/tools/upload_short.py alteraqon/<datum>-<slug> <pad/naar/slug.mp4> [--privacy public|unlisted|private] [--long] [--schedule]

- Controleert eerst de mp4 (1080x1920, video + audio, 15-180 s, geen decodeerfouten).
- Weigert als upload.json al een "youtube"-link heeft (nooit opnieuw uploaden: YouTube ziet het als kopie).
- Uploadt via tools/youtube_upload.py: categorie Wetenschap & technologie (28), Engels, niet voor kinderen,
  "gewijzigde of synthetische content" = ja.
- Schrijft de link terug in upload.json ("youtube", "uploaded") en toont daarna de TikTok-tekst ("tiktok").
"""
import argparse, datetime, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("mp4")
ap.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
ap.add_argument("--long", action="store_true", help="lange 16:9-video (1920x1080, tot 15 min) + thumbnail.jpg")
ap.add_argument("--schedule", action="store_true", help="niet meteen openbaar: inplannen op het eerstvolgende vrije tijdstip uit alteraqon/schedule.json")
a = ap.parse_args()

vid = Path(a.map); mp4 = Path(a.mp4)
meta_path = vid / "upload.json"
meta = json.loads(meta_path.read_text(encoding="utf-8"))
if meta.get("youtube"):
    sys.exit(f"Staat al online: {meta['youtube']} – niet opnieuw uploaden.")
if not os.environ.get("YT_REFRESH_TOKEN_ALTERAQON"):
    sys.exit("YT_REFRESH_TOKEN_ALTERAQON ontbreekt (alleen in de cloudsessie aanwezig).")

# controle van de mp4
probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height",
                        "-show_entries", "format=duration", "-of", "json", str(mp4)],
                       capture_output=True, text=True, check=True)
info = json.loads(probe.stdout)
kinds = {s["codec_type"] for s in info["streams"]}
v = next(s for s in info["streams"] if s["codec_type"] == "video")
dur = float(info["format"]["duration"])
errs = subprocess.run(["ffmpeg", "-v", "error", "-i", str(mp4), "-f", "null", "-"], capture_output=True, text=True).stderr
problems = []
want = (1920, 1080) if a.long else (1080, 1920)
if (v["width"], v["height"]) != want: problems.append(f"formaat {v['width']}x{v['height']}")
if "audio" not in kinds: problems.append("geen geluid")
if not (60 <= dur <= 900 if a.long else 15 <= dur <= 180): problems.append(f"duur {dur:.1f} s")
if errs.strip(): problems.append("decodeerfouten")
if problems:
    sys.exit("Controle mislukt: " + ", ".join(problems))
print(f"Controle goed: {want[0]}x{want[1]}, {dur:.1f} s, met geluid.")

publish_at = None
if a.schedule:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from next_slot import next_slot
    publish_at = next_slot("long" if a.long else "short")
    a.privacy = "private"
    print(f"Ingepland: wordt openbaar op {publish_at} (UTC).")

desc = meta["description"]
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write(desc); desc_file = f.name
env = dict(os.environ, YT_REFRESH_TOKEN=os.environ["YT_REFRESH_TOKEN_ALTERAQON"])
out = subprocess.run([sys.executable, str(ROOT / "tools" / "youtube_upload.py"), str(mp4),
                      "--title", meta["title"], "--description-file", desc_file,
                      "--tags", ",".join(meta.get("tags", [])), "--privacy", a.privacy,
                      "--category", "28", "--language", "en",
                      *(["--thumbnail", str(vid / "thumbnail.jpg")] if a.long and (vid / "thumbnail.jpg").exists() else []),
                      *(["--publish-at", publish_at] if publish_at else [])],
                     env=env, capture_output=True, text=True)
os.unlink(desc_file)
print(out.stdout, out.stderr, sep="")
m = re.search(r"https://youtu\.be/[\w-]+", out.stdout)
if not m:
    sys.exit("Upload mislukt.")
if out.returncode:
    print("LET OP: video staat online, maar de thumbnail kon niet automatisch gezet worden "
          "(kanaal niet geverifieerd?) – zet thumbnail.jpg zelf in YouTube Studio.")
meta["youtube"] = m.group(0)
meta["uploaded"] = f"{datetime.date.today().isoformat()} ({'ingepland' if publish_at else a.privacy})"
if publish_at: meta["publish_at"] = publish_at
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Online: {m.group(0)} – opgeslagen in {meta_path}" + (f" (openbaar vanaf {publish_at} UTC)" if publish_at else ""))
if meta.get("tiktok"):
    print("\n--- TikTok-tekst (kopiëren bij handmatig posten) ---\n" + meta["tiktok"])
