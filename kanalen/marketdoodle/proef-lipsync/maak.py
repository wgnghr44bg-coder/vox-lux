"""Proef lip sync (27 nov 2026): papa's zin uit de GTA-video twee keer naast elkaar. Links de oude mond (open/dicht op volume),
rechts de nieuwe lip sync (mondvorm per klank, tools/lipsync.py).  -> lipsync-proef.mp4"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent; BRON = HIER.parent / "video-gta-echt"
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools")); from lipsync import Lipsync
W, H, FPS, SS = 1920, 1080, 30, ps.SS
Z = json.load(open(BRON / "zinnen.json", encoding="utf-8")); WO = json.load(open(BRON / "woorden.json", encoding="utf-8"))
ZINNEN = [5, 16]                                            # papa: "It says I have $312..." en "What? It was an accident!"
A, sr = sf.read(BRON / "stem.wav", dtype="float32"); A = A.mean(axis=1) if A.ndim > 1 else A
stukken, woorden, t = [], [], 0.0
for i in ZINNEN:
    z = Z[i]; seg = A[int((z[0] - 0.2) * sr):int((z[1] + 0.4) * sr)]; d0 = z[0] - 0.2
    woorden += [[0, w[1], w[2] - d0 + t, w[3] - d0 + t] for w in WO if w[0] == i]; stukken.append(seg); t += len(seg) / sr
AUD = np.concatenate(stukken); sf.write(HIER / "stem.wav", AUD, sr); EIND = len(AUD) / sr
LS = Lipsync(woorden)
def luid(t):
    s = AUD[int(t * sr):int((t + 1 / FPS) * sr)]; return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
bg = Image.open(BRON.parent / "video-swap" / "afbeeldingen" / "keuken.png").convert("RGB").resize((W, H))
def frame(t):
    img = bg.copy(); laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    m = luid(t); v = LS.viseem(t) if m > 0.05 else None
    ps.poppetje(d, "dad", 520, 1700, 3.2, t, kijk=0.3, mond=m)                    # oud
    ps.poppetje(d, "dad", 1400, 1700, 3.2, t, kijk=-0.3, mond=m, viseem=v)        # nieuw
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); d = ImageDraw.Draw(img)
    d.line([(960, 0), (960, H)], fill=(255, 255, 255), width=8)
    for x, s_, kl in ((520, "NOW", (255, 255, 255)), (1400, "NEW: LIP SYNC", (255, 214, 64))):
        f = ps.font(ps.FB, 70); tw = d.textlength(s_, font=f); d.text((x - tw / 2, 40), s_, font=f, fill=kl, stroke_width=7, stroke_fill=(20, 20, 30))
    if v: f = ps.font(ps.FB, 60); d.text((1400 - d.textlength(v, font=f) / 2, 140), v, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(20, 20, 30))
    nu = [w for w in woorden if w[2] - 0.05 <= t <= w[3] + 0.3]
    if nu:
        s_ = " ".join(w[1] for w in woorden if abs(w[2] - nu[-1][2]) < 1.2)
        f = ps.font(ps.FS, 56); tw = d.textlength(s_, font=f); d.text((W / 2 - tw / 2, 985), s_, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return img
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(HIER / "stem.wav"),
                      "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "lipsync-proef.mp4")], stdin=subprocess.PIPE)
for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("KLAAR lipsync-proef.mp4", round(EIND, 1), "s")
