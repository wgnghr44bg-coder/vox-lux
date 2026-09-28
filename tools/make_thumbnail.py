#!/usr/bin/env python3
"""Make a YouTube thumbnail in the channel's fixed sleep-documentary style.

Every video gets the same layout so viewers recognise the series:
a vivid scene image, the series label "SLEEP DOCUMENTARY" big across the top,
and bottom-left a small line (the part after ":" in the topic) above the topic
itself in huge extra-bold white letters with a moonlight glow.

Usage:
    python3 tools/make_thumbnail.py scene.jpg thumb.jpg --title "POMPEII" --subtitle "The Last Day"

Requires Pillow. Uses DejaVu Serif/Sans (installed on the cloud image).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
TITLE_COLOR = (255, 255, 255)
OUTLINE = (18, 12, 8)  # dark rim around all text
NIGHT_GLOW = (190, 215, 255)  # pale moonlight halo around the title
LABEL = "SLEEP DOCUMENTARY"  # fixed series label at the bottom of every thumbnail
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


def heavy_text(base: Image.Image, xy: tuple[int, int], text: str,
               font: ImageFont.FreeTypeFont, night_glow: bool = False) -> None:
    """Big, extra-bold white text with a dark outline and glow (reads on any image).

    The white stroke thickens the letters; night_glow adds a pale moonlight halo.
    """
    weight = max(2, font.size // 28)
    outline = weight + max(3, font.size // 30)
    shadow = Image.new("L", base.size, 0)
    ImageDraw.Draw(shadow).text(xy, text, font=font, fill=255,
                                stroke_width=outline + 8, stroke_fill=255)
    shadow = shadow.filter(ImageFilter.GaussianBlur(16))
    base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0),
               shadow.point(lambda v: int(v * 0.85)))
    if night_glow:
        halo = Image.new("L", base.size, 0)
        ImageDraw.Draw(halo).text(xy, text, font=font, fill=255,
                                  stroke_width=outline, stroke_fill=255)
        for radius, strength in ((34, 0.5), (12, 0.45)):
            soft = halo.filter(ImageFilter.GaussianBlur(radius))
            base.paste(Image.new("RGB", base.size, NIGHT_GLOW), (0, 0),
                       soft.point(lambda v, k=strength: int(v * k)))
    d = ImageDraw.Draw(base)
    d.text(xy, text, font=font, fill=OUTLINE, stroke_width=outline, stroke_fill=OUTLINE)
    d.text(xy, text, font=font, fill=TITLE_COLOR, stroke_width=weight, stroke_fill=TITLE_COLOR)


def split_title(title: str) -> tuple[str, str]:
    """'Pompeii: The Last Day' -> ('Pompeii', 'The Last Day'); no colon -> (title, '')."""
    if ":" in title:
        main, sub = title.split(":", 1)
        return main.strip(), sub.strip()
    return title.strip(), ""


def make(scene: Path, out: Path, title: str, subtitle: str) -> None:
    base = cover(Image.open(scene).convert("RGB"))
    base = ImageEnhance.Color(base).enhance(1.25)
    base = ImageEnhance.Contrast(base).enhance(1.08)

    # Gently darken the top band and the bottom-left corner where the text sits.
    shade = Image.new("L", (W, H))
    px = shade.load()
    for y in range(H):
        top = max(0.0, 1 - y / (H * 0.30))
        for x in range(W):
            bottom = max(0.0, 1 - ((W - x) / W * 0.4 + (H - y) / (H * 0.45)))
            px[x, y] = int(150 * max(top, bottom) ** 1.2)
    base = Image.composite(Image.new("RGB", (W, H), (5, 5, 10)), base, shade)

    d = ImageDraw.Draw(base)
    main, sub = split_title(title)
    if subtitle:
        sub = subtitle

    # Top: fixed series label, same on every thumbnail.
    label_font = fit_font(d, LABEL, TITLE_FONT, int(W * 0.86), 112)
    lx = (W - d.textlength(LABEL, font=label_font)) // 2
    heavy_text(base, (int(lx), 18), LABEL, label_font)

    # Bottom-left: small line, then the topic very big with the night glow.
    x = 40
    main_font = fit_font(d, main, TITLE_FONT, int(W * 0.9), 200)
    main_top = H - main_font.getbbox(main)[3] - 34
    if sub:
        sub_font = fit_font(d, sub, TITLE_FONT, int(W * 0.75), 70)
        heavy_text(base, (x + 8, main_top - sub_font.getbbox(sub)[3] + 2), sub, sub_font)
    heavy_text(base, (x, main_top), main, main_font, night_glow=True)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("scene", type=Path, help="calm scene image from the video")
    parser.add_argument("out", type=Path)
    parser.add_argument("--title", required=True, help="the topic, e.g. 'Pompeii: The Last Day'")
    parser.add_argument("--subtitle", default="", help="optional, appended to the title")
    args = parser.parse_args()
    make(args.scene, args.out, args.title, args.subtitle)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
