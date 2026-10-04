#!/usr/bin/env python3
"""Eindcontrole van een lange video vóór de upload (eigenaar, okt 2026: "alles moet vloeiend
lopen, geen haperende of vastlopende stem; eerst controleren, dan pas plaatsen").

Controleert:
1. stem (video/stem-met-pauzes.wav): geen losse korte geluidjes tussen twee stiltes
   (= pauze midden in een woord, de stem "blijft hangen");
2. stem en eindvideo: geen decodeerfouten ("Header missing" gaf gekraak bij San Francisco);
3. geluid van de eindvideo per halve seconde vergeleken met de bron (stem + muziek op
   dezelfde sterkte): haperingen, gaten of herhalingen in de render vallen dan op;
4. beeld: nergens langer dan 8 s precies stilstaand;
5. lengte van beeld en geluid gelijk.

Gebruik:
    python3 tools/check_video.py stories/<map> video/<naam>-motion.mp4 [--muziek-db -20]
    python3 tools/check_video.py whatif-demo/topics/<slug> <slug>.mp4 --stem voice.mp3 --bron mix.wav
        (What if-video's: stem = losse voice-over, bron = de eindmix zelf als referentie)
Exitcode 0 en "CONTROLE GOED" = mag geüpload worden; anders NIET uploaden.
"""
import argparse, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np

FF = imageio_ffmpeg.get_ffmpeg_exe()


def pcm(args, sr):
    r = subprocess.run([FF, "-v", "error", *args, "-ac", "1", "-ar", str(sr), "-f", "s16le", "-"],
                       capture_output=True)
    return np.frombuffer(r.stdout, "<i2").astype(np.float32)


def hang_plekken(stem):
    """Korte geluidjes (≤ 0,2 s) met aan beide kanten ≥ 0,35 s stilte."""
    x = pcm(["-i", str(stem)], 16000)
    hop = 160
    n = len(x) // hop
    e = np.abs(x[:n * hop]).reshape(n, hop).mean(1)
    s = e > 0.03 * np.percentile(e, 90)
    segs, k = [], 0
    while k < n:
        if s[k]:
            m = k
            while m < n and s[m]:
                m += 1
            segs.append((k, m))
            k = m
        else:
            k += 1
    return [segs[i][0] / 100 for i in range(1, len(segs) - 1)
            if segs[i][1] - segs[i][0] <= 20 and segs[i][0] - segs[i - 1][1] >= 35
            and segs[i + 1][0] - segs[i][1] >= 35]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("video", help="eindvideo, relatief aan de verhaalmap of een pad")
    ap.add_argument("--muziek-db", type=float, default=-20)
    ap.add_argument("--stem", help="voice-over (default video/stem-met-pauzes.wav)")
    ap.add_argument("--bron", help="reference audio for the whole video (default: stem + muziek)")
    a = ap.parse_args()
    st = a.story
    f = Path(a.video) if Path(a.video).exists() else st / a.video
    stem, muziek = st / "video" / "stem-met-pauzes.wav", st / "video" / "muziek432.wav"
    if a.stem:
        stem = st / a.stem
    fout = []

    # 1. stem blijft hangen (meer dan een paar = gewone korte woordjes tussen komma's)
    h = hang_plekken(stem)
    print(f"stem: {len(h)} losse korte geluidjes", [f"{int(t // 60)}:{t % 60:04.1f}" for t in h[:8]])
    if len(h) > 2:   # streng (eigenaar: "geen haper, stotter of kraak, alles vloeiend")
        fout.append(f"stem blijft op {len(h)} plekken hangen")

    # 2. decodeerfouten
    for p in (stem, f):
        err = subprocess.run([FF, "-v", "error", "-i", str(p), "-f", "null", "-"],
                             capture_output=True, text=True).stderr.strip()
        if err:
            fout.append(f"decodeerfouten in {p.name}: {err.splitlines()[0]}")

    # 2b. vervorming/kraak: stem of video mag nergens tegen het maximum aan zitten
    for p in (stem, f):
        y = pcm(["-i", str(p)], 22050)
        clip = int((np.abs(y) >= 32000).sum())
        if clip > 10:
            fout.append(f"vervorming (kraak) in {p.name}: {clip} samples op het maximum")

    # 3. geluid van de video tegen de bron
    got = pcm(["-i", str(f)], 8000)
    ref_args = ["-i", str(stem)]
    if a.bron:
        ref_args = ["-i", str(st / a.bron)]
    elif muziek.exists():
        ref_args = ["-i", str(stem), "-i", str(muziek), "-filter_complex",
                    f"[1]volume={a.muziek_db}dB[m];[0][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9"]
    ref = pcm(ref_args, 8000)
    best = max(range(-400, 400), key=lambda k: float(np.dot(got[8000 + k:248000 + k], ref[8000:248000])))
    got = got[best:] if best >= 0 else np.concatenate([np.zeros(-best, np.float32), got])
    n = min(len(got), len(ref))
    bad = []
    for i in range(0, n - 4000, 4000):
        x, y = got[i:i + 4000], ref[i:i + 4000]
        if np.sqrt((y ** 2).mean()) < 300:
            continue
        c = float(np.dot(x, y) / (np.linalg.norm(x) * np.linalg.norm(y) + 1e-9))
        if c < 0.8:
            bad.append((i / 8000, round(c, 2)))
    print(f"geluid video vs bron: {len(bad)} afwijkende halve seconden",
          [f"{int(t // 60)}:{t % 60:04.1f}" for t, _ in bad[:8]])
    if len(bad) > 2:
        fout.append(f"geluid wijkt op {len(bad)} plekken af van de bron (hapering in de render)")
    if abs(len(got) - len(ref)) / 8000 > 3:
        fout.append(f"lengte video {len(got) / 8000:.0f} s, bron {len(ref) / 8000:.0f} s")

    # 4. stilstaand beeld
    raw = subprocess.run([FF, "-v", "error", "-i", str(f), "-vf", "fps=0.5,scale=64:36,format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    fr = np.frombuffer(raw, np.uint8).reshape(-1, 64 * 36).astype(np.float32)
    d = np.abs(np.diff(fr, axis=0)).mean(1)
    vast, run = [], 0
    for i, x in enumerate(d):
        run = run + 1 if x < 0.05 else 0
        if run == 4:
            vast.append(i * 2)
    print(f"beeld: {len(vast)} keer langer dan 8 s stilstaand", vast[:5])
    if vast:
        fout.append(f"beeld staat stil rond {vast[:3]} s")

    if fout:
        print("CONTROLE FOUT: " + "; ".join(fout))
        sys.exit(1)
    print("CONTROLE GOED")


if __name__ == "__main__":
    main()
