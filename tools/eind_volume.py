"""Laatste stap vóór upload: zet het volume van de video op -14 LUFS (eigenaar, 31 okt 2026: "net zo hard als
de meeste sleep history video's"). YouTube speelt alles wat harder is af op -14, dus zo klinkt hij even hard
als de rest. Pieken worden met een limiter op -1 dB gehouden; het beeld wordt alleen gekopieerd (snel).

Gebruik: python tools/eind_volume.py in.mp4 uit.mp4 [--lufs -14]
"""
import argparse, re, subprocess

import imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()


def meet(pad):
    uit = subprocess.run([FF, "-hide_banner", "-nostats", "-i", pad, "-vn", "-af", "ebur128=peak=true", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", uit)[-1]), float(re.findall(r"Peak:\s+(-?[\d.]+) dBFS", uit)[-1])


ap = argparse.ArgumentParser()
ap.add_argument("invoer"); ap.add_argument("uitvoer"); ap.add_argument("--lufs", type=float, default=-14)
a = ap.parse_args()
lufs, piek = meet(a.invoer)
gain = a.lufs - lufs
for _ in range(3):                                           # limiter maakt het iets zachter: bijstellen
    subprocess.run([FF, "-v", "error", "-y", "-i", a.invoer, "-c:v", "copy", "-af",
                    f"volume={gain:.2f}dB,alimiter=limit=0.89:level=false", "-c:a", "aac", "-b:a", "192k",
                    "-movflags", "+faststart", a.uitvoer], check=True)
    nu, piek_nu = meet(a.uitvoer)
    print(f"was {lufs:.1f} LUFS -> {nu:.1f} LUFS, piek {piek_nu:.1f} dB")
    if abs(nu - a.lufs) <= 0.5:
        break
    gain += a.lufs - nu
