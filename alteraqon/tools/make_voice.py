"""Stem maken (standaard Lux) voor een videomap: voice.mp3 + voice-times.tsv (tijden in s, stem start op 0,8 s).

Gebruik: python3 alteraqon/tools/make_voice.py alteraqon/<datum>-<slug> [cachemap]
(met een cachemap buiten de repo worden ongewijzigde zinnen niet opnieuw betaald)
Leest script-cues.txt ({img:Sxx} op een eigen regel, elke zin eindigt op [pause] of [long pause]).
Instellingen (eigenaar okt 2026): xAI Lux, tempo 0.9, pauzes 900/1700 ms, 600 ms na een zin.
Snelle Shorts-stem (eigenaar okt 2026, Venom): --voice atlas --speed 1.05 --pause-ms 300 --long-pause-ms 600 --sentence-pause-ms 200
"""
import argparse, csv, os, subprocess, sys
TOOL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "tools", "xai_voiceover.py")
LEAD = 0.8
ap = argparse.ArgumentParser()
ap.add_argument("map"); ap.add_argument("cache", nargs="?"); ap.add_argument("--voice", default="lux"); ap.add_argument("--speed", default="0.9")
ap.add_argument("--pause-ms", default="900"); ap.add_argument("--long-pause-ms", default="1700")
ap.add_argument("--sentence-pause-ms", default="600")
a = ap.parse_args()
CACHE = ["--cache-dir", os.path.abspath(a.cache)] if a.cache else []
os.chdir(a.map)
subprocess.run([sys.executable, TOOL, "script-cues.txt", "--proxy-auth", "--voice", a.voice, "--speed", a.speed,
                "--pause-ms", a.pause_ms, "--long-pause-ms", a.long_pause_ms, "--sentence-pause-ms", a.sentence_pause_ms,
                "--timeline", "voice-times-raw.tsv", "-o", "voice.mp3", *CACHE], check=True)
sec = lambda s: sum(float(p) * m for p, m in zip(s.split(":"), (3600, 60, 1)))
rows = [r for r in csv.reader(open("voice-times-raw.tsv"), delimiter="\t") if not r[0].startswith("#")]
with open("voice-times.tsv", "w") as f:
    f.write("#\tstart\tend\timage\ttext\n")
    for r in rows:
        f.write(f"{r[0]}\t{sec(r[1]) + LEAD:.2f}\t{sec(r[2]) + LEAD:.2f}\t{r[3]}\t{r[4]}\n")
print(f"voice-times.tsv: {len(rows)} regels, stem eindigt op {sec(rows[-1][2]) + LEAD:.1f} s")
