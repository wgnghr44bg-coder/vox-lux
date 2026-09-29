"""Maak afbeeldingen-tijden.tsv en afbeeldingen-prompts.md uit de tijdlijn van de stem.

Nodig in de verhaalmap:
  tijdlijn.tsv                 (van tools/xai_voiceover.py --timeline; kolom 'image' = {img:...})
  afbeeldingen-onderwerpen.tsv (kolommen slug, onderwerp: wat er op het beeld staat)
  audio/*-deel*.mp3            (voor de eindtijd van het laatste beeld)

Gebruik: python3 tools/make_image_prompts.py stories/titanic --stijl "cinematic realistic photograph, ..."
Daarna: python3 tools/xai_images.py stories/titanic 1 2 3   (of: all)
"""
import argparse, csv, re, subprocess
from pathlib import Path

import imageio_ffmpeg


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def hms(x):
    h, rest = divmod(int(x), 3600)
    m, s = divmod(rest, 60)
    return f"{h}:{m:02d}:{s:02d}"


def audio_len(story):
    parts = sorted((story / "audio").glob("*-deel*.mp3"))
    total = 0.0
    for p in parts:
        info = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-hide_banner", "-i", str(p)],
                              capture_output=True, text=True).stderr
        h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", info).groups()
        total += int(h) * 3600 + int(m) * 60 + float(s)
    return total


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("--stijl", required=True, help="stijltekst achter elke prompt")
    ap.add_argument("--titel", default="", help="kop van afbeeldingen-prompts.md")
    a = ap.parse_args()
    story = a.story

    rows = list(csv.DictReader(open(story / "tijdlijn.tsv"), delimiter="\t"))
    cues = [(sec(r["start"]), r["image"], r["text"]) for r in rows if r["image"]]
    cues[0] = (0.0, *cues[0][1:])
    subjects = {r["slug"]: r["onderwerp"] for r in
                csv.DictReader(open(story / "afbeeldingen-onderwerpen.tsv"), delimiter="\t")}
    missing = [slug for _, slug, _ in cues if slug not in subjects]
    if missing:
        raise SystemExit(f"Geen onderwerp voor: {', '.join(missing)}")
    end = audio_len(story)

    tsv = ["file\tstart\tend\tslug"]
    md = [f"# {a.titel} — afbeeldingen (xAI Grok Imagine)".strip(), "",
          "Eén afbeelding per nummer, opgeslagen als `001.jpg`, `002.jpg`, enz. "
          "(`tools/xai_images.py`).", ""]
    for i, (start, slug, text) in enumerate(cues):
        stop = cues[i + 1][0] if i + 1 < len(cues) else end
        tsv.append(f"{i + 1:03d}.jpg\t{start:.2f}\t{stop:.2f}\t{slug}")
        md += [f"## {i + 1:03d}  ·  {hms(start)} – {hms(stop)}  ({(stop - start) / 60:.1f} min)",
               f'*Verteller:* "{text}"', "", "```", f"{subjects[slug]}, {a.stijl}", "```", ""]
    (story / "afbeeldingen-tijden.tsv").write_text("\n".join(tsv) + "\n")
    (story / "afbeeldingen-prompts.md").write_text("\n".join(md))
    print(f"{len(cues)} afbeeldingen, laatste eindigt op {hms(end)}")


if __name__ == "__main__":
    main()
