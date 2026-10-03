"""Zet extra stilte achter elke zin van een bestaande voice-over (geen nieuwe audio nodig).

Na een zin komt  PAUZE_BASIS + PAUZE_PER_SEC * (zinslengte in s)  seconden extra stilte,
zodat lange zinnen meer ademruimte krijgen. De stilte gaat midden in de bestaande pauze.
Alle tijden (tijdlijn en afbeeldingen) worden mee verschoven.

Gebruik: python3 tools/add_pauses.py stories/pompeii [--welkom]
Met --welkom begint de stem met branding/welkom.mp3 ("Welcome back to Sleep Archives.",
één keer ingesproken, voor elke video hetzelfde); alle tijden schuiven dan mee.
Uitvoer: <map>/video/stem-met-pauzes.wav, <map>/tijdlijn-pauzes.tsv,
         <map>/afbeeldingen-tijden-pauzes.tsv
"""
import argparse, bisect, csv, subprocess, wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np

SR = 44100
PAUZE_BASIS = 0.6     # eigenaar, okt 2026: iets kortere pauzes dan eerst (0.7 / 0.1 / 2.2)
PAUZE_PER_SEC = 0.08
PAUZE_MAX = 1.8
KOMMA_PAUZE = 0.25    # kleine extra pauze bij elke adempauze binnen een zin (komma's)
KOMMA_MIN = 0.22      # zo lang moet zo'n stilte binnen een zin al zijn (s)
WELKOM = Path(__file__).resolve().parent.parent / "branding" / "welkom.mp3"
WELKOM_VOOR, WELKOM_NA = 0.8, 1.5     # stilte voor en na de welkomst (s)
# Stem net iets zwaarder en warmer (eigenaar, okt 2026): ± 0,4 halve toon lager,
# zelfde lengte (atempo maakt het tempo weer gelijk), iets meer laag, iets minder scherp.
ZWAARDER = ("asetrate=44100*0.975,aresample=44100,atempo=1.0256410,"
            "lowshelf=g=2:f=190,highshelf=g=-1:f=7500,deesser=i=0.3,volume=-1.5dB")


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def hms_precies(x):
    h, rest = divmod(max(x, 0), 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:06.3f}"


def hms(x):
    h, rest = divmod(x, 3600)
    m, s = divmod(rest, 60)
    return f"{int(h)}:{int(m):02d}:{s:04.1f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("--welkom", action="store_true", help="begin met branding/welkom.mp3")
    ap.add_argument("--niet-zwaarder", action="store_true", help="stem niet zwaarder maken")
    a = ap.parse_args()
    story = a.story

    lines = open(story / "tijdlijn.tsv").read().splitlines()
    header, rows = lines[0], [l.split("\t") for l in lines[1:] if l.strip()]

    # de stem inlezen (nodig om de pauzes precies in echte stiltes te zetten)
    parts = sorted((story / "audio").glob("*-deel*.mp3"))
    pcm = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                          "-i", "concat:" + "|".join(str(p) for p in parts), "-ac", "1", "-ar", str(SR),
                          "-f", "s16le", "-"], capture_output=True, check=True).stdout
    audio = np.frombuffer(pcm, dtype="<i2")
    hop = SR // 100
    env = np.abs(audio[:len(audio) // hop * hop].astype(np.float32)).reshape(-1, hop).mean(1)
    stil = env < 0.03 * np.percentile(env, 90)

    def stilte_bij(t, zoek=2.5, min_len=0.15):
        """Midden van de echte stilte die het dichtst bij t ligt. De tijden in tijdlijn.tsv lopen
        bij lange opnames tot een paar seconden uit de pas met het geluid (eigenaar, okt 2026:
        "de stem blijft hangen" = pauze midden in een woord); daarom altijd op de stilte zetten."""
        a, b = max(int((t - zoek) * 100), 0), min(int((t + zoek) * 100), len(stil))
        best, k = None, a
        while k < b:
            if stil[k]:
                m = k
                while m < len(stil) and stil[m]:
                    m += 1
                if (m - k) / 100 >= min_len:
                    mid = (k + m) / 200
                    if best is None or abs(mid - t) < abs(best - t):
                        best = mid
                k = m
            else:
                k += 1
        return best

    # waar komt stilte bij (in de echte pauze na elke zin) en hoeveel
    cuts, drift_t, drift = [], [], []  # (tijd, extra); hoeveel de tijdlijn afwijkt van het geluid
    for i in range(len(rows) - 1):
        start, end, nxt = sec(rows[i][1]), sec(rows[i][2]), sec(rows[i + 1][1])
        extra = min(PAUZE_MAX, PAUZE_BASIS + PAUZE_PER_SEC * (end - start))
        t = stilte_bij((end + nxt) / 2)
        if t is None:
            print(f"let op: geen stilte gevonden na zin {rows[i][0]}, geen extra pauze")
            continue
        cuts.append((t, extra))
        drift_t.append((end + nxt) / 2)
        drift.append(t - (end + nxt) / 2)
    print(f"tijdlijn wijkt tot {max(map(abs, drift), default=0):.2f} s af van het geluid (gecorrigeerd)")

    def echt(t):
        """Tijd uit tijdlijn.tsv -> tijd in het echte geluid."""
        return t + float(np.interp(t, drift_t, drift)) if drift_t else t
    for r in rows:
        r[1], r[2] = hms_precies(echt(sec(r[1]))), hms_precies(echt(sec(r[2])))

    # kleine pauze bij elke adempauze binnen een zin (komma's): stiltes in de stem zelf
    for r in rows:
        a0, a1 = int(sec(r[1]) * 100) + 5, int(sec(r[2]) * 100) - 5
        seg = env[a0:a1]
        if len(seg) < 20:
            continue
        quiet = seg < 0.08 * np.percentile(seg, 90)
        k = 0
        while k < len(seg):
            if quiet[k]:
                m = k
                while m < len(seg) and quiet[m]:
                    m += 1
                if k > 0 and m < len(seg) and (m - k) / 100 >= KOMMA_MIN:
                    cuts.append(((a0 + (k + m) / 2) / 100, KOMMA_PAUZE))
                k = m
            else:
                k += 1
    cuts.sort()
    cut_t = [c[0] for c in cuts]
    cum = np.concatenate([[0], np.cumsum([c[1] for c in cuts])])

    lead = np.zeros(0, dtype="<i2")
    if a.welkom:
        w = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                            "-i", str(WELKOM), "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                           capture_output=True, check=True).stdout
        lead = np.concatenate([np.zeros(int(WELKOM_VOOR * SR), dtype="<i2"), np.frombuffer(w, dtype="<i2"),
                               np.zeros(int(WELKOM_NA * SR), dtype="<i2")])
    offset = len(lead) / SR

    def shift(t):
        return t + cum[bisect.bisect_right(cut_t, t)] + offset

    # 1. audio (hierboven al ingelezen): stilte invoegen
    pieces, prev = [lead], 0
    for t, extra in cuts:
        k = int(round(t * SR))
        pieces += [audio[prev:k], np.zeros(int(round(extra * SR)), dtype="<i2")]
        prev = k
    pieces.append(audio[prev:])
    out = np.concatenate(pieces)
    if not a.niet_zwaarder:
        z = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-loglevel", "error",
                            "-f", "s16le", "-ar", str(SR), "-ac", "1", "-i", "-", "-af", ZWAARDER,
                            "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                           input=out.tobytes(), capture_output=True, check=True).stdout
        z = np.frombuffer(z, dtype="<i2")
        out = np.pad(z, (0, max(0, len(out) - len(z))))[:len(out)]   # exact even lang houden
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
            s = 0.0 if i == 0 else shift(echt(float(r["start"])))
            e = total if i == len(imgs) - 1 else shift(echt(float(imgs[i + 1]["start"])))
            f.write(f"{r['file']}\t{s:.2f}\t{e:.2f}\t{r['slug']}\n")

    print(f"oud {len(audio) / SR / 60:.1f} min -> nieuw {total / 60:.1f} min "
          f"(+{cum[-1] / 60:.1f} min stilte)")


if __name__ == "__main__":
    main()
