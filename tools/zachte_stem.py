"""Zachte klank voor de standaardstem Slaap 3 (eigenaar, 30 okt 2026): na tools/add_pauses.py, vóór make_video.py.

Haalt het scherpe randje van <map>/video/stem-met-pauzes.wav (warm, rond) en bewaart het origineel als
stem-met-pauzes-ruw.wav. Monteer daarna met `make_video.py ... --muziek-db -26`: dan staat de muziek
heel zacht onder de stem (eigenaar 31 okt: "zachter 4 is perfect"). Zet de video daarna met tools/eind_volume.py op -14 LUFS (net zo hard als andere sleep history video's).
Zacht komt van de klank en de rust, niet van een laag volume.

Gebruik: python tools/zachte_stem.py stories/<map>

Staat er <map>/stem.json (Audio Engine-stem, eigenaar 6 nov 2026), dan komt de klank daaruit ("klank"), bv. alleen
een highpass, of de stem iets lager en helderder zoals het voorbeeld van de eigenaar.
"""
import json, subprocess, sys
from pathlib import Path

import imageio_ffmpeg

KLANK = "lowpass=f=3800,highshelf=f=2200:g=-6,volume=0.4dB"


def klank_voor(story):
    sj = Path(story) / "stem.json"
    return json.loads(sj.read_text(encoding="utf-8")).get("klank", KLANK) if sj.exists() else KLANK


if __name__ == "__main__":
    v = Path(sys.argv[1]) / "video"
    ruw, stem = v / "stem-met-pauzes-ruw.wav", v / "stem-met-pauzes.wav"
    if not ruw.exists():
        stem.rename(ruw)
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-y", "-i", str(ruw), "-af", klank_voor(sys.argv[1]), str(stem)],
                   check=True)
    print(f"zachte klank -> {stem}")
