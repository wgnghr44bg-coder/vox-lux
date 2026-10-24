"""Spoort knipperen/flikkeren op: beelden die heen en weer springen in helderheid (A-B-A), in het hele beeld
of in een deel ervan (bijvoorbeeld een zonnevlek die aan/uit gaat, schaduwstrepen, glinsterend water).
Een harde cut is één sprong en telt niet; knipperen is een sprong die het volgende beeld weer terugspringt.

Gebruik (vanuit de map vox-lux; nodig: ffmpeg en numpy):
  python tools/threejs/check_flicker.py <video.mp4>                  # de echte MP4 (alle beelden, 30 fps)
  python tools/threejs/check_flicker.py <map-met-jpgs>               # beelden van check_frames.mjs --times a,a+1/30,...
  opties: --from 0 --to 10 (alleen dat stuk), --cell 6 (drempel per vak), --whole 2 (drempel hele beeld)
Drie of meer terugspringende sprongen binnen een halve seconde = knipperen (code 1); losse sprongen worden apart
genoemd om even te bekijken (een sputterende kraan, een ondertitel die invloeit).
"""
import argparse, os, subprocess, sys
import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("--from", dest="t0", type=float, default=0)
ap.add_argument("--to", dest="t1", type=float, default=None)
ap.add_argument("--fps", type=float, default=30)
ap.add_argument("--cell", type=float, default=6, help="sprong in een vak (0-255) die als knipperen telt")
ap.add_argument("--whole", type=float, default=2, help="sprong in het hele beeld die als knipperen telt")
a = ap.parse_args()

W, H, GX, GY = 36, 64, 6, 8
if os.path.isdir(a.src):
    inp = ["-pattern_type", "glob", "-i", os.path.join(a.src, "*.jpg")]
    t_of = lambda i: i
else:
    inp = ["-ss", str(a.t0), "-i", a.src] + (["-t", str(a.t1 - a.t0)] if a.t1 else [])
    t_of = lambda i: a.t0 + i / a.fps
raw = subprocess.run(["ffmpeg", "-v", "error", *inp, "-vf", f"scale={W}:{H}:flags=area,format=gray", "-f", "rawvideo", "-"],
                     capture_output=True, check=True).stdout
f = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
cells = f.reshape(len(f), GY, H // GY, GX, W // GX).mean(axis=(2, 4)).reshape(len(f), -1)
whole = f.mean(axis=(1, 2))

def alternating(v, thr):
    # a jump that comes straight back: frame i differs from both neighbours, while the neighbours are alike
    d = np.diff(v, axis=0)
    back = np.abs(v[2:] - v[:-2])
    return (np.abs(d[:-1]) > thr) & (np.abs(d[1:]) > thr) & (np.sign(d[:-1]) != np.sign(d[1:])) & (back < 0.5 * np.minimum(np.abs(d[:-1]), np.abs(d[1:])))

hits = alternating(cells, a.cell).sum(axis=1) + alternating(whole[:, None], a.whole)[:, 0] * GX * GY
bad = [i + 1 for i in np.nonzero(hits)[0]]
if not bad:
    print(f"geen knipperen gevonden in {len(f)} beelden")
    sys.exit(0)
# group hits that are less than half a second apart; three or more in a row is flicker, a single one is usually motion
gap = int(a.fps * 0.5) if not os.path.isdir(a.src) else 3
groups, cur = [], [bad[0]]
for i in bad[1:]:
    if i - cur[-1] <= gap: cur.append(i)
    else: groups.append(cur); cur = [i]
groups.append(cur)
unit = " s" if not os.path.isdir(a.src) else " (beeldnummer)"
span = lambda g: f"{t_of(g[0]):.2f}" + (f"–{t_of(g[-1]):.2f}" if len(g) > 1 else "") + unit
flick = [g for g in groups if len(g) >= 3]
single = [g for g in groups if len(g) < 3]
if single:
    print("losse sprongen (meestal gewone beweging of een ondertitel, even bekijken): " + ", ".join(span(g) for g in single))
if not flick:
    print(f"geen knipperen gevonden in {len(f)} beelden")
    sys.exit(0)
print(f"KNIPPEREN in {len(f)} beelden:")
for g in flick:
    print(f"  {span(g)}  ({len(g)} sprongen)")
sys.exit(1)
