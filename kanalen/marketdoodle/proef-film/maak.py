"""Proef film-camera + levendiger bewegen (27 nov 2026). Eerst 'BEFORE' (zoals nu: vaste push-in, armen springen, mond op volume),
daarna 'AFTER' (tools/filmcamera.py: wijd shot, shot/tegenshot close-ups met wazige achtergrond, punch-in bij uitroep, handheld;
ps.BEWEGEN: veren, hupje, wiegen, knikken; lip sync).  -> film-proef.mp4"""
import json, os, subprocess, sys
from pathlib import Path
import numpy as np, soundfile as sf
from PIL import Image, ImageDraw, ImageFilter
HIER = Path(__file__).parent; BRON = HIER.parent / "video-gta-echt"
_c = os.getcwd(); os.chdir(HIER.parent / "proef-pop-short"); sys.path.insert(0, os.getcwd()); import pop_short as ps; os.chdir(_c)
sys.path.insert(0, str(HIER.parents[2] / "tools")); from lipsync import Lipsync; from filmcamera import FilmCamera
W, H, FPS, SS = 1920, 1080, 30, ps.SS
Zb = json.load(open(BRON / "zinnen.json", encoding="utf-8")); WOb = json.load(open(BRON / "woorden.json", encoding="utf-8"))
A0, sr = sf.read(BRON / "stem.wav", dtype="float32"); A0 = A0.mean(axis=1) if A0.ndim > 1 else A0
REGELS = [5, 6, 16, 18]                                       # papa / mama / papa / mama
GEB = {5: None, 6: "armen-open", 16: "armen-open", 18: "wijslinks"}
stukken, Z, WO, t = [np.zeros(int(1.2 * sr), np.float32)], [], [], 1.2
for i in REGELS:
    z = Zb[i]; seg = A0[int(z[0] * sr):int(z[1] * sr)]; d0 = z[0]
    Z.append([t, t + len(seg) / sr, z[2], "keuken", z[4], GEB[i]]); WO += [[len(Z) - 1, w[1], w[2] - d0 + t, w[3] - d0 + t] for w in WOb if w[0] == i]
    stukken += [seg, np.zeros(int(0.35 * sr), np.float32)]; t += len(seg) / sr + 0.35
A = np.concatenate(stukken + [np.zeros(int(0.8 * sr), np.float32)]); EIND = len(A) / sr
sf.write(HIER / "stem.wav", np.concatenate([A, A]), sr)                          # BEFORE + AFTER
LS = Lipsync(WO)
def luid(t, wie):
    if not any(z[0] <= t <= z[1] and z[4] == wie for z in Z): return 0.0
    s = A[int(t * sr):int((t + 1 / FPS) * sr)]; return float(min(1.0, np.sqrt((s ** 2).mean()) * 9)) if len(s) else 0.0
FIG = {"DAD": ("dad", 700), "MOM": ("mom", 1250)}
cam = FilmCamera(W, H, Z, WO, posities={"DAD": (700, 560), "MOM": (1250, 580)})
bg = Image.open(BRON.parent / "video-swap" / "afbeeldingen" / "keuken.png").convert("RGB").resize((W, H))
def frame(t, nieuw):
    nu = next((z for z in Z if z[0] - 0.05 <= t <= z[1] + 0.3), None)
    if nieuw: box, waas = cam.uitsnede(t)
    else: f = 1 + 0.06 * min(1, t / EIND); box, waas = ((W - W / f) / 2, (H - H / f) * 0.45, (W + W / f) / 2, (H - H / f) * 0.45 + H / f), 0.0
    img = bg.filter(ImageFilter.GaussianBlur(9 * waas)) if waas > 0.05 else bg.copy()
    laag = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0)); d = ImageDraw.Draw(laag); ps.LIPSYNC = LS if nieuw else None
    for wie, (n, x) in FIG.items():
        ander = 1250 if wie == "DAD" else 700; kijk = 0.9 if ander > x else -0.9
        g = nu[5] if nu and nu[4] == wie else None
        ps.poppetje(d, n, x, 1000, 1.7, t, kijk=kijk, mond=luid(t, wie), gebaar=g, sleutel=n + str(nieuw), bewegen=nieuw,
                    verbaasd=bool(nu and nu[4] == wie and "!" in nu[2]))
    ps.LIPSYNC = None
    laag = laag.resize((W, H), Image.LANCZOS); img.paste(laag, (0, 0), laag)
    x0, y0, x1, y1 = box; img = img.crop((int(x0), int(y0), int(x1), int(y1))).resize((W, H), Image.LANCZOS); d = ImageDraw.Draw(img)
    s_ = "AFTER: FILM CAMERA + LIP SYNC" if nieuw else "BEFORE"; f = ps.font(ps.FB, 56)
    d.text((40, 30), s_, font=f, fill=(255, 214, 64) if nieuw else (255, 255, 255), stroke_width=6, stroke_fill=(20, 20, 30))
    if nu:
        ww = [w for w in WO if w[0] == Z.index(nu)]; f = ps.font(ps.FS, 54); stukken_, cur = [], []
        for w in ww:
            cur.append(w)
            if len(cur) >= 6 or w[1][-1:] in ".?!,": stukken_.append(cur); cur = []
        if cur: stukken_.append(cur)
        tekst = " ".join(w[1] for w in next((s2 for s2 in stukken_ if t <= s2[-1][3] + 0.1), stukken_[-1]))
        d.text((W / 2 - d.textlength(tekst, font=f) / 2, 985), tekst, font=f, fill=(255, 255, 255), stroke_width=6, stroke_fill=(0, 0, 0))
    return img
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(HIER / "stem.wav"),
                      "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-shortest", str(HIER / "film-proef.mp4")], stdin=subprocess.PIPE)
for nieuw in (False, True):
    for i in range(int(EIND * FPS)): p.stdin.write(frame(i / FPS, nieuw).tobytes())
p.stdin.close(); p.wait(); print("KLAAR film-proef.mp4", round(2 * EIND, 1), "s")
