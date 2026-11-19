"""Staande Short (1080x1920) uit een lange BlackswanVault-video: stuk van zin A t/m B, de 16:9-video in het midden op een
wazige achtergrond, kop bovenin, grote ondertiteling (stukjes van max 4 woorden) onderin. Geen gesproken outro.
Gebruik: python maak_short.py <videomap> <video.mp4> <zin_a> <zin_b> "<KOP>" <uit.mp4>"""
import json, subprocess, sys
from pathlib import Path
vm, src, a, b, kop, uit = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
Z = json.load(open(vm / "zinnen.json", encoding="utf-8"))
t0 = max(0, Z[a][0] - 0.3); t1 = Z[b][1] + 0.9; dur = t1 - t0
def ts(x):
    h, r = divmod(max(0, x), 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"
reg = []
for s, e, z, _ in Z[a:b + 1]:
    w = z.split(); stukken = [w[i:i + 4] for i in range(0, len(w), 4)]
    tot = sum(len(" ".join(x)) for x in stukken); t = s
    for x in stukken:
        d = (e - s) * len(" ".join(x)) / tot
        reg.append(f"Dialogue: 0,{ts(t - t0)},{ts(t + d - t0)},Sub,,0,0,0,,{' '.join(x)}"); t += d
kop_r = f"Dialogue: 1,{ts(0)},{ts(dur)},Kop,,0,0,0,,{kop}"
ass = f"""[Script Info]
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Segoe UI Black,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,6,2,2,60,60,430,1
Style: Kop,Segoe UI Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,5,0,8,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{kop_r}
""" + "\n".join(reg) + "\n"
Path("ondertitels.ass").write_text(ass, encoding="utf-8")
fc = ("[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.25[bg];"
      r"[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2,subtitles=ondertitels.ass:fontsdir='C\:/Windows/Fonts',"
      f"fade=t=out:st={dur - 0.6:.2f}:d=0.6[v];[0:a]afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-t", f"{dur:.2f}", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", uit], check=True)
print("KLAAR", uit, round(dur, 1), "s")
