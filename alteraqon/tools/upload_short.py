"""Alteraqon: een goedgekeurde short op YouTube zetten (@alteraqon), met titel, beschrijving en tags uit upload.json.

ALLEEN draaien nadat de eigenaar uitdrukkelijk "zet online" heeft gezegd. Draait in de cloudsessie
(daar staat YT_REFRESH_TOKEN_ALTERAQON; nooit in git zetten).

Gebruik (vanuit de map vox-lux):
  python3 alteraqon/tools/upload_short.py alteraqon/<datum>-<slug> <pad/naar/slug.mp4> [--privacy public|unlisted|private]

- Controleert eerst de mp4 (1080x1920, video + audio, 15-180 s, geen decodeerfouten).
- Weigert als upload.json al een "youtube"-link heeft (nooit opnieuw uploaden: YouTube ziet het als kopie).
- Uploadt via tools/youtube_upload.py: categorie Wetenschap & technologie (28), Engels, niet voor kinderen,
  "gewijzigde of synthetische content" = ja.
- Schrijft de link terug in upload.json ("youtube", "uploaded").
"""
import argparse, datetime, json, os, re, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("mp4")
ap.add_argument("--privacy", choices=["public", "unlisted", "private"], default="public")
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
if (v["width"], v["height"]) != (1080, 1920): problems.append(f"formaat {v['width']}x{v['height']}")
if "audio" not in kinds: problems.append("geen geluid")
if not 15 <= dur <= 180: problems.append(f"duur {dur:.1f} s")
if errs.strip(): problems.append("decodeerfouten")
if problems:
    sys.exit("Controle mislukt: " + ", ".join(problems))
print(f"Controle goed: 1080x1920, {dur:.1f} s, met geluid.")

desc = meta["description"]
with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as f:
    f.write(desc); desc_file = f.name
env = dict(os.environ, YT_REFRESH_TOKEN=os.environ["YT_REFRESH_TOKEN_ALTERAQON"])
out = subprocess.run([sys.executable, str(ROOT / "tools" / "youtube_upload.py"), str(mp4),
                      "--title", meta["title"], "--description-file", desc_file,
                      "--tags", ",".join(meta.get("tags", [])), "--privacy", a.privacy,
                      "--category", "28", "--language", "en"],
                     env=env, capture_output=True, text=True)
os.unlink(desc_file)
print(out.stdout, out.stderr, sep="")
m = re.search(r"https://youtu\.be/[\w-]+", out.stdout)
if out.returncode or not m:
    sys.exit("Upload mislukt.")
meta["youtube"] = m.group(0)
meta["uploaded"] = f"{datetime.date.today().isoformat()} ({a.privacy})"
meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(f"Online: {m.group(0)} – opgeslagen in {meta_path}")
