#!/usr/bin/env python3
"""Make a YouTube thumbnail in the channel's fixed sleep-documentary style.

Every video gets the same layout so viewers recognise the series:
a calm scene image, a dark gradient on the left, a large cream title,
an amber subtitle, an amber rule and the label "SLEEP DOCUMENTARY".

Usage:
    python3 tools/make_thumbnail.py scene.jpg thumb.jpg --title "POMPEII" --subtitle "The Last Day"

Requires Pillow. Uses DejaVu Serif/Sans (installed on the cloud image).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
CREAM = (243, 230, 200)
AMBER = (224, 164, 88)
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
TITLE_FONT = FONT_DIR / "DejaVuSerif-Bold.ttf"
SUB_FONT = FONT_DIR / "DejaVuSerif.ttf"
LABEL_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"


def cover(img: Image.Image) -> Image.Image:
    """Scale and centre-crop to 1280x720."""
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left, top = (img.width - W) // 2, (img.height - H) // 2
    return img.crop((left, top, left + W, top + H))


def fit_font(draw: ImageDraw.ImageDraw, text: str, path: Path, max_w: int, start: int) -> ImageFont.FreeTypeFont:
    size = start
    while size > 40:
        font = ImageFont.truetype(str(path), size)
        if draw.textlength(text, font=font) <= max_w:
            return font
        size -= 4
    return ImageFont.truetype(str(path), size)


def make(scene: Path, out: Path, title: str, subtitle: str) -> None:
    base = cover(Image.open(scene).convert("RGB"))

    # Dark gradient from the left so the text always reads, same on every video.
    shade = Image.new("L", (W, H))
    px = shade.load()
    for x in range(W):
        a = int(215 * max(0.0, 1 - x / (W * 0.62)) ** 1.4)
        for y in range(H):
            px[x, y] = a
    base = Image.composite(Image.new("RGB", (W, H), (8, 8, 14)), base, shade)
    # Soft vignette.
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.25, -H * 0.35, W * 1.25, H * 1.35), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(120))
    base = Image.composite(base, Image.new("RGB", (W, H), (0, 0, 0)), vig)

    d = ImageDraw.Draw(base)
    x = 70
    label_font = ImageFont.truetype(str(LABEL_FONT), 30)
    title_font = fit_font(d, title, TITLE_FONT, int(W * 0.52), 150)
    sub_font = fit_font(d, subtitle, SUB_FONT, int(W * 0.50), 58) if subtitle else None

    title_h = title_font.getbbox(title)[3]
    sub_h = sub_font.getbbox(subtitle)[3] if sub_font else 0
    block = 30 + 26 + title_h + (18 + sub_h if sub_font else 0)
    y = (H - block) // 2

    d.text((x, y), "SLEEP DOCUMENTARY", font=label_font, fill=AMBER)
    y += 30 + 26
    for dx, dy in ((3, 3), (0, 0)):  # subtle shadow, then text
        d.text((x + dx, y + dy), title, font=title_font,
               fill=(0, 0, 0) if dx else CREAM)
    y += title_h + 22
    d.rectangle((x, y, x + 120, y + 4), fill=AMBER)
    if sub_font:
        d.text((x, y + 18), subtitle, font=sub_font, fill=AMBER)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("scene", type=Path, help="calm scene image from the video")
    parser.add_argument("out", type=Path)
    parser.add_argument("--title", required=True, help="1-2 words, e.g. POMPEII")
    parser.add_argument("--subtitle", default="", help="short line, e.g. The Last Day")
    args = parser.parse_args()
    make(args.scene, args.out, args.title.upper(), args.subtitle)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
