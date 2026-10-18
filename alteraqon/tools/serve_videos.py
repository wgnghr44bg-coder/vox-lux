"""Alteraqon: video's tonen én downloaden op de iPhone via Tailscale.

Gebruik (op de pc, alleen op het Tailscale-IP):
  python alteraqon/tools/serve_videos.py <tailscale-ip> [poort=8765] [map=C:\\Users\\rane\\Videos\\alteraqon]

  http://<ip>:8765/            -> lijst van alle video's met een "Bekijk"- en "Download"-knop
  http://<ip>:8765/<slug>.mp4  -> bekijken in Safari
  http://<ip>:8765/<slug>.mp4?download=1 -> Safari downloadt het bestand (komt in Bestanden > Downloads)
"""
import html, os, sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, urlsplit

IP = sys.argv[1]
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 8765
DIR = sys.argv[3] if len(sys.argv) > 3 else r"C:\Users\rane\Videos\alteraqon"


class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        url = urlsplit(self.path)
        if url.path in ("/", "/index.html"):
            files = sorted((f for f in os.listdir(DIR) if f.lower().endswith(".mp4")),
                           key=lambda f: os.path.getmtime(os.path.join(DIR, f)), reverse=True)
            rows = "".join(
                f'<li><b>{html.escape(f)}</b><br><a href="/{quote(f)}">Bekijk</a> · '
                f'<a href="/{quote(f)}?download=1">Download</a></li>' for f in files)
            body = (f'<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                    f'<title>Alteraqon</title><style>body{{font:18px system-ui;margin:20px}}li{{margin:14px 0}}'
                    f'a{{display:inline-block;padding:8px 14px;margin-top:6px;background:#222;color:#fff;'
                    f'border-radius:8px;text-decoration:none}}</style><h2>Alteraqon-video\'s</h2><ul>{rows}</ul>').encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        self._download = "download=1" in (url.query or "")
        self.path = url.path
        super().do_GET()

    def do_HEAD(self):
        url = urlsplit(self.path)
        self._download = "download=1" in (url.query or "")
        self.path = url.path
        super().do_HEAD()

    def end_headers(self):
        if getattr(self, "_download", False):
            name = os.path.basename(self.path)
            self.send_header("Content-Disposition", f'attachment; filename="{name}"')
        super().end_headers()


ThreadingHTTPServer((IP, PORT), partial(Handler, directory=DIR)).serve_forever()
