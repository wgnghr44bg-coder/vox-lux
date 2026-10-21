"""Zet elke zin van een stemopname precies op de tijd van zijn ondertitel.

Leest <map>/voice.mp3 + <map>/voice-times.tsv (van tools/comfy/make_voice_local.py)
en <map>/cues.tsv (id, start, end, tekst: dezelfde tijden als de ondertitels in de HTML).
Schrijft <map>/voice-placed.mp3: elke cue begint op zijn ondertitel-start (+ --offset).
Past een zin niet in zijn tijdvak, dan wordt hij iets versneld (max --max-tempo) en volgt een waarschuwing.

Gebruik (vanuit de map vox-lux, alleen standaard-Python + ffmpeg nodig):
  python tools/threejs/place_voice.py tools/threejs/never-stopped-raining
"""
import argparse, os, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("map")
ap.add_argument("--offset", type=float, default=0.15, help="seconden na de ondertitel-start")
ap.add_argument("--max-tempo", type=float, default=1.15)
ap.add_argument("--length", type=float, default=None, help="totale lengte (standaard: einde laatste cue + 1 s)")
a = ap.parse_args()

def rows(path):
    with open(path, encoding="utf-8") as f:
        return [l.rstrip("\n").split("\t") for l in f if l.strip() and not l.startswith("#")]

cues = {r[0]: (float(r[1]), float(r[2]), r[3]) for r in rows(os.path.join(a.map, "cues.tsv"))}
groups = []                                   # [cue, start, end] in voice.mp3
for r in rows(os.path.join(a.map, "voice-times.tsv")):
    start, end, cue = float(r[1]), float(r[2]), r[3].strip()
    if cue:
        groups.append([cue, start, end])
    elif groups:
        groups[-1][2] = end
missing = [g[0] for g in groups if g[0] not in cues]
if missing:
    sys.exit(f"Deze cues staan niet in cues.tsv: {', '.join(missing)}")

filters, labels, problems = [], [], []
for i, (cue, gs, ge) in enumerate(groups):
    c0, c1, text = cues[cue]
    slot = c1 - c0 - a.offset - 0.1
    dur = ge - gs
    tempo = 1.0 if dur <= slot else min(a.max_tempo, dur / slot)
    if dur / tempo > slot:
        problems.append(f"{cue}: {dur:.1f} s stem, tijdvak {slot:.1f} s ({text[:50]})")
    delay = int(round((c0 + a.offset) * 1000))
    filters.append(f"[0:a]atrim=start={gs:.3f}:end={ge:.3f},asetpts=PTS-STARTPTS,"
                   f"atempo={tempo:.3f},adelay={delay}|{delay}[v{i}]")
    labels.append(f"[v{i}]")
    print(f"{cue}  {c0:6.2f}s  {dur:4.1f}s{'' if tempo == 1 else f'  x{tempo:.2f}'}  {text[:60]}")

length = a.length or max(c[1] for c in cues.values()) + 1
filters.append(f"{''.join(labels)}amix=inputs={len(labels)}:normalize=0:duration=longest,apad=whole_dur={length:.2f}[out]")
out = os.path.join(a.map, "voice-placed.mp3")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(a.map, "voice.mp3"),
                "-filter_complex", ";".join(filters), "-map", "[out]", "-t", f"{length:.2f}", "-b:a", "192k", out], check=True)
print(f"\nKlaar: {out}")
if problems:
    print("Let op, deze zinnen passen niet helemaal (de volgende zin begint eroverheen):")
    for p in problems:
        print("  " + p)
