"""Maakt de losse korte geluidjes stil die tools/check_video.py als "stem blijft hangen" meldt, en zet het geluid
opnieuw onder de video. Bij OmniVoice (Slaap 3) zijn dat piepkleine adem- of tikgeluidjes ± 0,5 s vóór een zin
(31 okt 2026, Oregon: 52 stuks, met Whisper nagekeken: geen woorden).

Werkwijze: in <map>/video/stem-met-pauzes.wav wordt elk geluidje (≤ 0,2 s, aan beide kanten stilte) stil gemaakt,
het origineel blijft als stem-met-pauzes-voor-tikjes.wav. Daarna stem + muziek (zelfde mix als make_video.py)
opnieuw onder het beeld van <video> (beeld wordt gekopieerd). Draai daarna tools/check_video.py en tools/eind_volume.py.

Gebruik: python tools/stil_tikjes.py stories/<map> <video>-motion.mp4 <uit>.mp4 [--muziek-db -24.6] [--max-piek 0.3]
"""
import argparse, shutil, subprocess, sys, wave
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
import check_video as cv

ap = argparse.ArgumentParser()
ap.add_argument("story", type=Path); ap.add_argument("video"); ap.add_argument("uit")
ap.add_argument("--muziek-db", type=float, default=-24.6)
ap.add_argument("--max-piek", type=float, default=0.3, help="hardere geluidjes niet aanraken (kan een woord zijn)")
a = ap.parse_args()
v = a.story / "video"
stem, orig, muziek = v / "stem-met-pauzes.wav", v / "stem-met-pauzes-voor-tikjes.wav", v / "muziek432.wav"
if not orig.exists():
    shutil.copy(stem, orig)

plekken = cv.hang_plekken(orig)
with wave.open(str(orig)) as w:
    sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth()
    x = np.frombuffer(w.readframes(w.getnframes()), f"<i{sw}").reshape(-1, ch).copy()
stil = 0
for t in plekken:                                   # geluidje loopt van t tot hooguit t + 0,2 s; ruim stil maken
    s, e = int((t - 0.05) * sr), int((t + 0.3) * sr)
    if np.abs(x[s:e]).max() / 2 ** (8 * sw - 1) > a.max_piek:
        print(f"  {t:.1f} s overgeslagen (te hard, misschien een woord)")
        continue
    f = int(0.01 * sr)
    x[s:s + f] = (x[s:s + f] * np.linspace(1, 0, f)[:, None]).astype(x.dtype)
    x[s + f:e] = 0
    stil += 1
with wave.open(str(stem), "wb") as w:
    w.setnchannels(ch); w.setsampwidth(sw); w.setframerate(sr); w.writeframes(x.tobytes())
print(f"{stil} van {len(plekken)} geluidjes stil gemaakt -> {stem}")

subprocess.run([cv.FF, "-v", "error", "-y", "-i", a.video, "-i", str(stem), "-i", str(muziek), "-filter_complex",
                f"[2:a]volume={a.muziek_db}dB[m];[1:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]",
                "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                "-movflags", "+faststart", a.uit], check=True)
print("klaar:", a.uit)
