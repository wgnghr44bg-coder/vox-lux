"""MP3-site (eigenaar 27 nov 2026): plak een TikTok- of YouTube-link op je iPhone, krijg een mp3 die je in Bestanden bewaart.

Draait op de pc van de eigenaar (yt-dlp + ffmpeg), alleen in het eigen thuisnetwerk: http://<pc-ip>:8780
  python server.py
Bestanden staan maar 1 uur op de pc en worden daarna vanzelf opgeruimd.
"""
import json, re, shutil, subprocess, sys, threading, time, uuid
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote, urlparse

HIER = Path(__file__).resolve().parent
MAP = HIER / "mp3"
MAP.mkdir(exist_ok=True)
POORT = 8780
FFMPEG = shutil.which("ffmpeg") or r"C:\Users\rane\AppData\Roaming\Python\Python312\site-packages\imageio_ffmpeg\binaries\ffmpeg-win-x86_64-v7.1.exe"
TOEGESTAAN = ("youtube.com", "youtu.be", "tiktok.com")
BEWAAR = 3600
klussen = {}                     # id -> {"stand": "bezig"|"klaar"|"fout", "titel", "bestand", "fout"}


def toegestaan(url):
    try:
        h = (urlparse(url).hostname or "").lower()
    except ValueError:
        return False
    return urlparse(url).scheme in ("http", "https") and any(h == d or h.endswith("." + d) for d in TOEGESTAAN)


def opruimen():
    while True:
        for p in MAP.iterdir():
            if time.time() - p.stat().st_mtime > BEWAAR:
                shutil.rmtree(p, ignore_errors=True) if p.is_dir() else p.unlink(missing_ok=True)
        time.sleep(300)


def maak(kid, url):
    doel = MAP / kid
    doel.mkdir()
    r = subprocess.run([sys.executable, "-m", "yt_dlp", "--no-playlist", "-x", "--audio-format", "mp3", "--audio-quality", "0",
                        "--embed-metadata", "--embed-thumbnail", "--convert-thumbnails", "jpg",
                        "--ffmpeg-location", FFMPEG, "--restrict-filenames", "--no-progress",
                        "-o", str(doel / "%(title).80s.%(ext)s"), "--print", "after_move:title", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
    mp3 = next(doel.glob("*.mp3"), None)
    if r.returncode == 0 and mp3:
        titel = (r.stdout.strip().splitlines() or [mp3.stem])[-1]
        klussen[kid] = {"stand": "klaar", "titel": titel, "bestand": mp3.name}
    else:
        fout = (r.stderr.strip().splitlines() or ["onbekende fout"])[-1]
        klussen[kid] = {"stand": "fout", "fout": re.sub(r"^ERROR:\s*", "", fout)[:300]}


class H(BaseHTTPRequestHandler):
    def stuur(self, code, data, soort="application/json; charset=utf-8", extra=None):
        b = data if isinstance(data, bytes) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", soort)
        self.send_header("Content-Length", str(len(b)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        p = urlparse(self.path).path
        if p in ("/", "/index.html"):
            return self.stuur(200, (HIER / "index.html").read_bytes(), "text/html; charset=utf-8")
        if p == "/icoon.png" and (HIER / "icoon.png").exists():
            return self.stuur(200, (HIER / "icoon.png").read_bytes(), "image/png")
        m = re.fullmatch(r"/stand/([0-9a-f]{32})", p)
        if m:
            return self.stuur(200, klussen.get(m.group(1), {"stand": "fout", "fout": "niet gevonden (verlopen?)"}))
        m = re.fullmatch(r"/bestand/([0-9a-f]{32})", p)
        if m and klussen.get(m.group(1), {}).get("stand") == "klaar":
            k = klussen[m.group(1)]
            f = MAP / m.group(1) / k["bestand"]
            if f.exists():
                naam = re.sub(r'[\\/:*?"<>|]', "", k["titel"]).strip()[:80] or "audio"
                return self.stuur(200, f.read_bytes(), "audio/mpeg",
                                  {"Content-Disposition": f"attachment; filename=\"audio.mp3\"; filename*=UTF-8''{quote(naam)}.mp3"})
        self.stuur(404, {"fout": "niet gevonden"})

    def do_POST(self):
        if urlparse(self.path).path != "/maak":
            return self.stuur(404, {"fout": "niet gevonden"})
        try:
            url = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0)) or 0) or b"{}").get("url", "").strip()
        except (ValueError, AttributeError):
            url = ""
        if not toegestaan(url):
            return self.stuur(400, {"fout": "Alleen links van YouTube of TikTok."})
        kid = uuid.uuid4().hex
        klussen[kid] = {"stand": "bezig"}
        threading.Thread(target=maak, args=(kid, url), daemon=True).start()
        self.stuur(200, {"id": kid})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    threading.Thread(target=opruimen, daemon=True).start()
    print(f"MP3-site op http://0.0.0.0:{POORT}")
    ThreadingHTTPServer(("0.0.0.0", POORT), H).serve_forever()
