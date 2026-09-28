"""Zet extra stilte achter elke zin van een bestaande voice-over (geen nieuwe audio nodig).

Na een zin komt  PAUZE_BASIS + PAUZE_PER_SEC * (zinslengte in s)  seconden extra stilte,
zodat lange zinnen meer ademruimte krijgen. De stilte gaat midden in de bestaande pauze.
Alle tijden (tijdlijn en afbeeldingen) worden mee verschoven.

Gebruik: python3 tools/add_pauses.py stories/pompeii
Uitvoer: <map>/video/stem-met-pauzes.wav, <map>/tijdlijn-pauzes.tsv,
         <map>/afbeeldingen-tijden-pauzes.tsv
"""
import argparse, bisect, csv, subprocess, wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np

SR = 44100
PAUZE_BASIS = 0.7
PAUZE_PER_SEC = 0.1
PAUZE_MAX = 2.2


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def hms(x):
    h, rest = divmod(x, 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    story = ap.parse_args().story

    lines = open(story / "tijdlijn.tsv").read().splitlines()
    header, rows = lines[0], [l.split("\t") for l in lines[1:] if l.strip()]

    # waar komt stilte bij (midden van de pauze na elke zin) en hoeveel
    cuts = []  # (tijd, extra)
    for i in range(len(rows) - 1):
        start, end, nxt = sec(rows[i][1]), sec(rows[i][2]), sec(rows[i + 1][1])
        extra = min(PAUZE_MAX, PAUZE_BASIS + PAUZE_PER_SEC * (end - start))
        cuts.append(((end + nxt) / 2, extra))
    cut_t = [c[0] for c in cuts]
    cum = np.concatenate([[0], np.cumsum([c[1] for c in cuts])])

    def shift(t):
        return t + cum[bisect.bisect_right(cut_t, t)]

    # 1. audio: delen aan elkaar, stilte invoegen
    parts = sorted((story / "audio").glob("*-deel*.mp3"))
    concat = "|".join(str(p) for p in parts)
    pcm = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                          "-i", f"concat:{concat}", "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype="<i2")
    pieces, prev = [], 0
    for t, extra in cuts:
        k = int(round(t * SR))
        pieces += [audio[prev:k], np.zeros(int(round(extra * SR)), dtype="<i2")]
        prev = k
    pieces.append(audio[prev:])
    out = np.concatenate(pieces)
    (story / "video").mkdir(exist_ok=True)
    with wave.open(str(story / "video" / "stem-met-pauzes.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(out.tobytes())

    # 2. tijdlijn
    with open(story / "tijdlijn-pauzes.tsv", "w") as f:
        f.write(header + "\n")
        for r in rows:
            f.write("\t".join([r[0], hms(shift(sec(r[1]))), hms(shift(sec(r[2])))] + r[3:]) + "\n")

    # 3. afbeeldingen: grenzen mee verschuiven, laatste loopt door tot het eind
    imgs = list(csv.DictReader(open(story / "afbeeldingen-tijden.tsv"), delimiter="\t"))
    total = len(out) / SR
    with open(story / "afbeeldingen-tijden-pauzes.tsv", "w") as f:
        f.write("file\tstart\tend\tslug\n")
        for i, r in enumerate(imgs):
            s = shift(float(r["start"]))
            e = total if i == len(imgs) - 1 else shift(float(imgs[i + 1]["start"]))
            f.write(f"{r['file']}\t{s:.2f}\t{e:.2f}\t{r['slug']}\n")

    print(f"oud {len(audio) / SR / 60:.1f} min -> nieuw {total / 60:.1f} min "
          f"(+{cum[-1] / 60:.1f} min stilte)")


if __name__ == "__main__":
    main()
