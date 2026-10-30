"""Zachte klank voor de standaardstem Slaap 3 (eigenaar, 30 okt 2026): na tools/add_pauses.py, vóór make_video.py.

Haalt het scherpe randje van <map>/video/stem-met-pauzes.wav (warm, rond) en bewaart het origineel als
stem-met-pauzes-ruw.wav. Monteer daarna met `make_video.py ... --muziek-db -24.6`: dan staat de muziek
± 25 dB onder de stem (eigenaar 31 okt: "veel zachter") en is het geheel ± -23 LUFS, dus ook hoorbaar als iemand zijn telefoon zacht heeft.
Zacht komt van de klank en de rust, niet van een laag volume.

Gebruik: python tools/zachte_stem.py stories/<map>
"""
import subprocess, sys
from pathlib import Path

import imageio_ffmpeg

KLANK = "lowpass=f=3800,highshelf=f=2200:g=-6,volume=0.4dB"

v = Path(sys.argv[1]) / "video"
ruw, stem = v / "stem-met-pauzes-ruw.wav", v / "stem-met-pauzes.wav"
if not ruw.exists():
    stem.rename(ruw)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(ruw), "-af", KLANK, str(stem)], check=True)
print(f"zachte klank -> {stem}")
