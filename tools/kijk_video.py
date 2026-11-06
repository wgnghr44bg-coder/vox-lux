#!/usr/bin/env python3
"""Watch and listen to a YouTube video (or a local file) so Claude can judge it.

Downloads the video small (yt-dlp), makes contact sheets of frames with timestamps,
writes what is said with timestamps (YouTube captions when there are any, otherwise
Whisper locally on the GPU) and measures the loudness. Free, nothing leaves the pc
except the download itself.

Run with the OmniVoice environment (it has torch + transformers + Whisper):
    C:/Users/rane/omnivoice-venv/Scripts/python.exe tools/kijk_video.py URL [--beelden 64] [--whisper]

Output in %TEMP%/kijk/<id>/: info.txt, tekst.txt, sheet-01.jpg ... (16 frames per sheet).
--whisper: always use Whisper (also when captions exist), e.g. to hear what is really said.
"""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

PY = r"C:\Users\rane\AppData\Local\Programs\Python\Python312\python.exe"   # has yt-dlp

ap = argparse.ArgumentParser()
ap.add_argument("bron", help="YouTube-link of een videobestand")
ap.add_argument("--beelden", type=int, default=64, help="aantal beeldjes over de hele video")
ap.add_argument("--whisper", action="store_true", help="altijd Whisper, ook als er ondertitels zijn")
a = ap.parse_args()


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8", errors="replace", **kw)


def tijd(s):
    s = int(s)
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


lokaal = Path(a.bron).exists()
if lokaal:
    vid = Path(a.bron).stem
    out = Path(os.environ["TEMP"]) / "kijk" / vid
    out.mkdir(parents=True, exist_ok=True)
    video = Path(a.bron)
    meta = {"title": vid}
else:
    meta = json.loads(run([PY, "-m", "yt_dlp", "-J", "--no-playlist", a.bron]).stdout)
    vid = meta["id"]
    out = Path(os.environ["TEMP"]) / "kijk" / vid
    out.mkdir(parents=True, exist_ok=True)
    print("downloaden:", meta["title"])
    run([PY, "-m", "yt_dlp", "--no-playlist", "-f", "bv*[height<=480]+ba/b[height<=480]/b", "--merge-output-format", "mp4",
         "--write-subs", "--write-auto-subs", "--sub-langs", ".*-orig,en", "--sub-format", "vtt", "--ignore-errors",   # vertaalde ondertitels geven 429
         "-o", str(out / "video.%(ext)s"), a.bron])
    video = out / "video.mp4"

duur = float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(video)]).stdout)

# ---------- info ----------
info = [f"titel     {meta.get('title')}", f"kanaal    {meta.get('channel', '')}", f"duur      {tijd(duur)}"]
for k, n in (("view_count", "weergaven"), ("like_count", "likes"), ("upload_date", "geplaatst"), ("channel_follower_count", "abonnees")):
    if meta.get(k) is not None:
        info.append(f"{n:<9} {meta[k]}")
for c in meta.get("chapters") or []:
    info.append(f"hoofdstuk {tijd(c['start_time'])} {c['title']}")
if meta.get("description"):
    info += ["", "beschrijving:", meta["description"]]
lufs = run(["ffmpeg", "-nostats", "-i", str(video), "-map", "0:a", "-af", "ebur128", "-f", "null", "-"]).stderr
m = re.findall(r"I:\s+(-?[\d.]+) LUFS", lufs)
info.insert(3, f"volume    {m[-1] if m else '?'} LUFS")
(out / "info.txt").write_text("\n".join(info) + "\n", encoding="utf-8")

# ---------- beelden: contactsheets van 4x4 met tijd erop ----------
for f in out.glob("sheet-*.jpg"):
    f.unlink()
from PIL import Image, ImageDraw, ImageFont   # per beeldje zoeken (-ss) is veel sneller dan de hele video decoderen
font = ImageFont.truetype(r"C:\Windows\Fonts\arial.ttf", 22)
stap = duur / a.beelden
beelden = []
for i in range(a.beelden):
    t = (i + 0.5) * stap
    f = out / "b.jpg"
    run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-vf", "scale=480:-2", str(f)])
    im = Image.open(f).convert("RGB")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 92, 30), fill=(0, 0, 0))
    d.text((6, 3), tijd(t), font=font, fill=(255, 255, 255))
    beelden.append(im)
(out / "b.jpg").unlink(missing_ok=True)
w, h = beelden[0].size
for n in range(0, len(beelden), 16):
    sheet = Image.new("RGB", (4 * w + 12, 4 * h + 12), (20, 20, 20))
    for j, im in enumerate(beelden[n:n + 16]):
        sheet.paste(im.resize((w, h)), ((j % 4) * (w + 4), (j // 4) * (h + 4)))
    sheet.save(out / f"sheet-{n // 16 + 1:02d}.jpg", quality=85)

# ---------- tekst: ondertitels of Whisper ----------
regels = []
subs = sorted(out.glob("video*.vtt"), key=lambda p: ("orig" not in p.name, p.name))
if subs and not a.whisper:
    laatste = ""
    for blok in subs[0].read_text(encoding="utf-8", errors="replace").split("\n\n"):
        mm = re.search(r"(\d+):(\d\d):(\d\d)\.\d+ -->", blok)
        if not mm:
            continue
        # automatische ondertitels rollen: elk blok herhaalt de vorige regel, dus alleen de laatste regel telt
        tekst = ([re.sub(r"<[^>]+>", "", l).strip() for l in blok.splitlines()[1:] if "-->" not in l and l.strip()] or [""])[-1]
        if tekst and tekst != laatste:
            regels.append(f"[{tijd(int(mm[1]) * 3600 + int(mm[2]) * 60 + int(mm[3]))}] {tekst}")
            laatste = tekst
    bron = f"ondertitels ({subs[0].name})"
else:
    import torch
    from transformers import pipeline
    wav = out / "geluid.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-ac", "1", "-ar", "16000", str(wav)])
    asr = pipeline("automatic-speech-recognition", "openai/whisper-large-v3-turbo", device="cuda:0", torch_dtype=torch.float16)
    r = asr(str(wav), chunk_length_s=30, batch_size=8, return_timestamps=True, generate_kwargs={"task": "transcribe"})
    for c in r["chunks"]:
        regels.append(f"[{tijd(c['timestamp'][0] or 0)}] {c['text'].strip()}")
    wav.unlink()
    bron = "Whisper (lokaal)"
(out / "tekst.txt").write_text(f"# tekst uit {bron}\n" + "\n".join(regels) + "\n", encoding="utf-8")

print(f"klaar: {out}")
print(f"  {len(list(out.glob('sheet-*.jpg')))} contactsheets, {len(regels)} tekstregels uit {bron}, duur {tijd(duur)}")
