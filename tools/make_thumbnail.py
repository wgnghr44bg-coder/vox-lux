#!/usr/bin/env python3
"""Make a YouTube thumbnail in the channel's fixed sleep-documentary style.

Every video gets the same layout so viewers recognise the series:
a scene image, a big white serif title centred at the top with a dark glow,
and the series label "SLEEP DOCUMENTARY" centred at the bottom.

Usage:
    python3 tools/make_thumbnail.py scene.jpg thumb.jpg --title "POMPEII" --subtitle "The Last Day"

Requires Pillow. Uses DejaVu Serif/Sans (installed on the cloud image).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W, H = 1280, 720
TITLE_COLOR = (255, 255, 255)
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


def glow_text(base: Image.Image, xy: tuple[int, int], text: str,
              font: ImageFont.FreeTypeFont, fill: tuple[int, int, int],
              night_glow: bool = False) -> None:
    """Draw text with a soft dark glow behind it, so it reads on any image.

    night_glow adds a pale, moonlight-like halo so the title stands out.
    """
    layer = Image.new("L", base.size, 0)
    ImageDraw.Draw(layer).text(xy, text, font=font, fill=255,
                               stroke_width=10, stroke_fill=255)
    layer = layer.filter(ImageFilter.GaussianBlur(14))
    base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0),
               layer.point(lambda v: int(v * 0.9)))
    if night_glow:
        halo = Image.new("L", base.size, 0)
        ImageDraw.Draw(halo).text(xy, text, font=font, fill=255,
                                  stroke_width=6, stroke_fill=255)
        for radius, strength in ((28, 0.55), (10, 0.6)):
            soft = halo.filter(ImageFilter.GaussianBlur(radius))
            glow = Image.new("RGB", base.size, NIGHT_GLOW)
            base.paste(Image.blend(base, glow, 1.0), (0, 0),
                       soft.point(lambda v, k=strength: int(v * k)))
    ImageDraw.Draw(base).text(xy, text, font=font, fill=fill,
                              stroke_width=3, stroke_fill=(20, 12, 6))


def wrap(draw: ImageDraw.ImageDraw, text: str, path: Path, max_w: int) -> tuple[list[str], ImageFont.FreeTypeFont]:
    """One line if it fits at a big size, otherwise two balanced lines."""
    font = fit_font(draw, text, path, max_w, 150)
    if font.size >= 104 or " " not in text:
        return [text], font
    words = text.split()
    best = min(range(1, len(words)), key=lambda i: abs(
        draw.textlength(" ".join(words[:i]), font=font) - draw.textlength(" ".join(words[i:]), font=font)))
    lines = [" ".join(words[:best]), " ".join(words[best:])]
    longest = max(lines, key=lambda l: draw.textlength(l, font=font))
    return lines, fit_font(draw, longest, path, int(max_w * 0.85), 104)


def make(scene: Path, out: Path, title: str, subtitle: str) -> None:
    base = cover(Image.open(scene).convert("RGB"))

    # Darken the top and bottom bands where the text sits, plus a soft vignette.
    shade = Image.new("L", (W, H))
    px = shade.load()
    for y in range(H):
        t = min(y, H - y) / (H * 0.5)
        a = int(170 * max(0.0, 1 - t / 0.55) ** 1.3)
        for x in range(W):
            px[x, y] = a
    base = Image.composite(Image.new("RGB", (W, H), (6, 6, 10)), base, shade)
    vig = Image.new("L", (W, H), 0)
    ImageDraw.Draw(vig).ellipse((-W * 0.2, -H * 0.3, W * 1.2, H * 1.3), fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(110))
    base = Image.composite(base, Image.new("RGB", (W, H), (0, 0, 0)), vig)

    d = ImageDraw.Draw(base)
    text = f"{title} {subtitle}".strip() if subtitle else title
    lines, font = wrap(d, text, TITLE_FONT, int(W * 0.9))
    line_h = font.getbbox("Hg")[3] + 6
    y = 30
    for line in lines:
        x = (W - d.textlength(line, font=font)) // 2
        glow_text(base, (int(x), y), line, font, TITLE_COLOR, night_glow=True)
        y += line_h

    label_font = fit_font(d, LABEL, TITLE_FONT, int(W * 0.72), 100)
    lx = (W - d.textlength(LABEL, font=label_font)) // 2
    ly = H - label_font.getbbox(LABEL)[3] - 40
    glow_text(base, (int(lx), ly), LABEL, label_font, TITLE_COLOR)

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
