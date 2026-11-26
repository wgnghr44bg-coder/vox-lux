"""Alleen de Denny's-scène (1993) uit maak_short.py v3 renderen, ter goedkeuring (eigenaar 26 nov: "nee eerst de scène")."""
import subprocess
import maak_short as M
EIND = M.SC[1]["t"]
p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{M.W}x{M.H}", "-r", str(M.FPS), "-i", "-",
                      "-i", str(M.HIER / "stem.wav"), "-af", "loudnorm=I=-14:TP=-1.5", "-c:v", "libx264", "-crf", "21", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "128k", "-t", f"{EIND:.2f}", str(M.HIER / "scene-denny.mp4")], stdin=subprocess.PIPE)
for i in range(int(EIND * M.FPS)): p.stdin.write(M.frame(i / M.FPS).tobytes())
p.stdin.close(); p.wait(); print("scene-denny.mp4", round(EIND, 1), "s")
