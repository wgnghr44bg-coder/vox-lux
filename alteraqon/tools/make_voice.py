"""Lux-stem maken voor een videomap: voice.mp3 + voice-times.tsv (tijden in s, stem start op 0,8 s).

Gebruik: python3 alteraqon/tools/make_voice.py alteraqon/<datum>-<slug>
Leest script-cues.txt ({img:Sxx} op een eigen regel, elke zin eindigt op [pause] of [long pause]).
Instellingen (eigenaar okt 2026): xAI Lux, tempo 0.9, pauzes 900/1700 ms, 600 ms na een zin.
"""
import csv, os, subprocess, sys
TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "xai_voiceover.py")
LEAD = 0.8
os.chdir(sys.argv[1])
subprocess.run([sys.executable, TOOL, "script-cues.txt", "--proxy-auth", "--speed", "0.9",
                "--pause-ms", "900", "--long-pause-ms", "1700", "--sentence-pause-ms", "600",
                "--timeline", "voice-times-raw.tsv", "-o", "voice.mp3"], check=True)
sec = lambda s: sum(float(p) * m for p, m in zip(s.split(":"), (3600, 60, 1)))
rows = [r for r in csv.reader(open("voice-times-raw.tsv"), delimiter="\t") if not r[0].startswith("#")]
with open("voice-times.tsv", "w") as f:
    f.write("#\tstart\tend\timage\ttext\n")
    for r in rows:
        f.write(f"{r[0]}\t{sec(r[1]) + LEAD:.2f}\t{sec(r[2]) + LEAD:.2f}\t{r[3]}\t{r[4]}\n")
print(f"voice-times.tsv: {len(rows)} regels, stem eindigt op {sec(rows[-1][2]) + LEAD:.1f} s")
