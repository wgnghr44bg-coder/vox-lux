"""Video-geluid tegen de bron (stem + muziek), per 0,5 s, ook zachte stukjes. Lijst van afwijkende plekken."""
import subprocess, sys
from pathlib import Path
import numpy as np

m, video = Path(sys.argv[1]), Path(sys.argv[2])
v = m / "video"
mdb = (v / "muziek-db.txt").read_text().strip()
stem = v / "stem-met-pauzes.wav"
muziek = v / "muziek432.wav"


def pcm(args):
    return np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", *args, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                                        capture_output=True).stdout, np.int16).astype(np.float32)


got = pcm(["-i", str(video)])
ref = pcm(["-i", str(stem), "-i", str(muziek), "-filter_complex",
           f"[1]volume={mdb}dB[m];[0][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9"])
best = max(range(-400, 400), key=lambda k: float(np.dot(got[8000 + k:248000 + k], ref[8000:248000])))
got = got[best:] if best >= 0 else np.concatenate([np.zeros(-best, np.float32), got])
n = min(len(got), len(ref))
rij = []
for i in range(0, n - 4000, 4000):
    u, w = got[i:i + 4000], ref[i:i + 4000]
    rw = float(np.sqrt((w ** 2).mean()))
    if rw < 60:
        continue
    cc = float(np.dot(u, w) / (np.linalg.norm(u) * np.linalg.norm(w) + 1e-9))
    gu = float(np.sqrt((u ** 2).mean()))
    rij.append((i / 8000, cc, rw, gu))
cc = np.array([r[1] for r in rij])
print(f"blokken {len(rij)}, cc mediaan {np.median(cc):.3f}, <0.8: {(cc < 0.8).sum()}, <0.6: {(cc < 0.6).sum()}, <0.4: {(cc < 0.4).sum()}")
for t, c, rw, gu in sorted(rij, key=lambda r: r[1])[:25]:
    print(f"{int(t // 60)}:{t % 60:05.2f}  cc {c:.2f}  bron {rw:.0f}  video {gu:.0f}")
