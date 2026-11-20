"""Staande Short (1080x1920) uit een lange BlackswanVault-video: stuk van zin A t/m B, de 16:9-video in het midden op een
wazige achtergrond, kop bovenin, grote ondertiteling (stukjes van max 4 woorden) onderin. Geen gesproken outro.
Gebruik: python maak_short.py <videomap> <video.mp4> <zin_a> <zin_b> "<KOP>" <uit.mp4> [--zonder-ondertitels]"""
import json, subprocess, sys
from pathlib import Path
ZONDER = "--zonder-ondertitels" in sys.argv   # 20 nov (eigenaar): Short zonder ondertiteling, alleen de kop
if ZONDER: sys.argv.remove("--zonder-ondertitels")
vm, src, a, b, kop, uit = Path(sys.argv[1]), sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5], sys.argv[6]
Z = json.load(open(vm / "zinnen.json", encoding="utf-8"))
t0 = max(0, Z[a][0] - 0.3); t1 = Z[b][1] + 0.9
if b + 1 < len(Z): t1 = min(t1, Z[b + 1][0] - 0.15)   # 20 nov: nooit het begin van de volgende zin meenemen
dur = t1 - t0
def ts(x):
    h, r = divmod(max(0, x), 3600); m, s = divmod(r, 60); return f"{int(h)}:{int(m):02d}:{s:05.2f}"
# 19 nov (eigenaar: "ondertiteling klopt niet helemaal", "je mag ook cijfers gebruiken"): woordtijden van Whisper op de stem
import os
wj = Path(uit).with_name(Path(uit).stem + "-woorden.json")
if not ZONDER and not wj.exists():
    subprocess.run([r"C:/Users/rane/omnivoice-venv/Scripts/python.exe", str(Path(__file__).with_name("woorden.py")), str(vm / "stem.wav"),
                    f"{t0:.2f}", f"{t1:.2f}", str(wj)], check=True)
GETAL = {"two": "2", "three": "3", "four": "4", "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9", "ten": "10"}
W = [] if ZONDER else json.load(open(wj, encoding="utf-8"))
vorige = "."
for w in W:
    k = w["w"].lower().strip(".,?!")
    if k in GETAL and vorige[-1:] not in ".?!": w["w"] = w["w"].lower().replace(k, GETAL[k])   # niet aan het begin van een zin
    w["w"] = w["w"].replace("NVIDIA", "Nvidia"); vorige = w["w"]
# 19 nov (eigenaar: "gaat van boven naar beneden en maakt geen complete zinnen"): hele zinsdelen (tot komma/punt, max 2 regels),
# en blokken sluiten precies op elkaar aan (overlap liet libass ze boven elkaar stapelen = springen)
groepen, groep = [], []
for w in W:
    groep.append(w)
    if w["w"][-1:] in ".,?!;:":
        groepen.append(groep); groep = []
if groep: groepen.append(groep)
import math
def verdeel(g, maxc=44):                                   # lange zin in gelijke delen (geen los staartje)
    n = math.ceil(len(" ".join(x["w"] for x in g)) / maxc)
    if n <= 1: return [g]
    doel = len(" ".join(x["w"] for x in g)) / n; uit, cur = [], []
    for x in g:
        cur.append(x)
        if len(uit) < n - 1 and len(" ".join(y["w"] for y in cur)) >= doel: uit.append(cur); cur = []
    if cur: uit.append(cur)
    return uit
groepen = [d for g in groepen for d in verdeel(g, 84)]   # 20 nov: stijl eigenaar (CapCut): hele zinsdelen, tot 4 regels
def regels(g):                                   # 20 nov: hoofdletters, regels van max ± 22 tekens (zoals eigenaar in CapCut)
    s = " ".join(x["w"] for x in g).upper(); r, cur = [], ""
    for w in s.split():
        if cur and len(cur) + 1 + len(w) > 22: r.append(cur); cur = w
        else: cur = (cur + " " + w).strip()
    return BREUK.join(r + [cur])
def regels_oud(g):
    s = " ".join(x["w"] for x in g)
    if len(s) <= 24: return s
    woorden = s.split(); beste = min(range(1, len(woorden)), key=lambda k: abs(len(" ".join(woorden[:k])) - len(" ".join(woorden[k:]))))
    return " ".join(woorden[:beste]) + BREUK + " ".join(woorden[beste:])
BREUK = chr(92) + 'N'
reg = []
for k, g in enumerate(groepen):
    s = g[0]["s"]; e = (g[-1]["e"] or g[-1]["s"] + 0.3) + 0.35
    if k + 1 < len(groepen): e = min(e, groepen[k + 1][0]["s"])
    reg.append(f"Dialogue: 0,{ts(s)},{ts(e)},Sub,,0,0,0,,{{\pos(540,1490)}}{regels(g)}")
kop_r = f"Dialogue: 1,{ts(0)},{ts(dur)},Kop,,0,0,0,,{kop}"
ass = f"""[Script Info]
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Sub,Segoe UI,68,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,0,3,5,60,60,0,1
Style: Kop,Segoe UI Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H64000000,1,0,0,0,100,100,0,0,1,5,0,8,60,60,250,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
{kop_r}
""" + "\n".join(reg) + "\n"
Path("ondertitels.ass").write_text(ass, encoding="utf-8")
fc = ("[0:v]split[a][b];[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.42[bg];"
      r"[b]scale=1080:-2[fg];[bg][fg]overlay=0:(H-h)/2,subtitles=ondertitels.ass:fontsdir='C\:/Windows/Fonts',"
      f"fade=t=out:st={dur - 0.6:.2f}:d=0.6[v];[0:a]afade=t=out:st={dur - 0.8:.2f}:d=0.8[au]")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t0:.2f}", "-t", f"{dur:.2f}", "-i", src, "-filter_complex", fc, "-map", "[v]", "-map", "[au]",
                "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", uit], check=True)
print("KLAAR", uit, round(dur, 1), "s")
