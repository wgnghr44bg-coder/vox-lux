"""Proef van een stuk van de short (eigenaar 26 nov: "stuur eerst proef"). Gebruik: python scene_proef.py <van_s> <tot_s> <uit.mp4>"""
import subprocess, sys
import maak_short as M
T0, T1, UIT = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{M.W}x{M.H}", "-r", str(M.FPS), "-i", "-",
                      "-ss", f"{T0:.2f}", "-i", str(M.HIER / "stem.wav"), "-af", "loudnorm=I=-14:TP=-1.5", "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", "24",
                      "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-t", f"{T1 - T0:.2f}", str(M.HIER / UIT)], stdin=subprocess.PIPE)
for i in range(int((T1 - T0) * M.FPS)): p.stdin.write(M.frame(T0 + i / M.FPS).tobytes())
p.stdin.close(); p.wait(); print(UIT, round(T1 - T0, 1), "s")
