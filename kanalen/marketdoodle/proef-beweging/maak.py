"""Proef bewegingen (27 nov 2026): links zoals het was, rechts met ps.BEWEGEN (armen veren soepel naar een nieuwe houding,
ademen bij stilstaan, hoofd beweegt mee met praten, naar voren leunen bij lopen) + lip sync.  -> beweging-proef.mp4"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw
HIER = Path(__file__).parent; LS_MAP = HIER.parent / "proef-lipsync"; BRON = HIER.parent / "video-gta-echt"
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools")); from lipsync import Lipsync
W, H, FPS, SS = 1920, 1080, 30, ps.SS
A, sr = sf.read(LS_MAP / "stem.wav", dtype="float32"); A = A.mean(axis=1) if A.ndim > 1 else A
EIND = 11.0; A = np.concatenate([np.zeros(int(0.8 * sr), np.float32), A, np.zeros(int(max(0, EIND * sr - len(A) - 0.8 * sr)), np.float32)])
sf.write(HIER / "stem.wav", A, sr)
Z = json.load(open(BRON / "zinnen.json", encoding="utf-8")); WO = json.load(open(BRON / "woorden.json", encoding="utf-8"))
woorden, t_ = [], 0.8
for i in (5, 16):
    z = Z[i]; d0 = z[0] - 0.2; woorden += [[0, w[1], w[2] - d0 + t_, w[3] - d0 + t_] for w in WO if w[0] == i]; t_ += (z[1] + 0.4) - d0
LS = Lipsync(woorden)
def luid(t):
    s = A[int(t * sr):int((t + 1 / FPS) * sr)]; return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
PLAN = [(0.0, None), (1.6, "armen-open"), (3.0, None), (4.2, "juich"), (5.4, "wijs"), (6.6, "hoofdhanden"), (8.0, None)]
def gebaar(t): return [g for t0, g in PLAN if t >= t0][-1]
LOOP = (8.6, 10.2)
bg = Image.open(BRON.parent / "video-swap" / "afbeeldingen" / "keuken.png").convert("RGB").resize((W, H))
def frame(t):
    img = bg.copy(); laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag)
    m = luid(t); loop = (t - LOOP[0]) * 2.2 if LOOP[0] <= t < LOOP[1] else None
    dx = 0 if t < LOOP[0] else min(1, (t - LOOP[0]) / (LOOP[1] - LOOP[0])) * 160
    g = gebaar(t) if loop is None else None
    for x0, beweeg, key in ((420, False, "oud"), (1300, True, "nieuw")):
        ps.LIPSYNC = LS if beweeg else None
        ps.poppetje(d, "dad", x0 + dx, 1000, 2.1, t, loop=loop, kijk=0.9 if loop is not None else 0.2, mond=m, gebaar=g, sleutel=key, bewegen=beweeg)
    ps.LIPSYNC = None
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag); d = ImageDraw.Draw(img)
    d.line([(960, 0), (960, H)], fill=(255, 255, 255), width=8)
    for x, s_, kl in ((480, "NOW", (255, 255, 255)), (1440, "NEW: MOVEMENT + LIP SYNC", (255, 214, 64))):
        f = ps.font(ps.FB, 60); tw = d.textlength(s_, font=f); d.text((x - tw / 2, 40), s_, font=f, fill=kl, stroke_width=7, stroke_fill=(20, 20, 30))
    f = ps.font(ps.FS, 46); s_ = {None: "standing / talking", "armen-open": "arms open", "juich": "cheer", "wijs": "point", "hoofdhanden": "hands on head"}.get(g, "")
    if loop is not None: s_ = "walking"
    d.text((W / 2 - d.textlength(s_, font=f) / 2, 1000), s_, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return img
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(HIER / "stem.wav"),
                      "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-t", f"{EIND}", str(HIER / "beweging-proef.mp4")], stdin=subprocess.PIPE)
for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS).tobytes())
p.stdin.close(); p.wait(); print("KLAAR beweging-proef.mp4")
