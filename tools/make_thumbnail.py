#!/usr/bin/env python3
"""Make a YouTube thumbnail in the channel's fixed sleep-documentary style.

Style v2 (default, since Oct 2026): a warm scene with people, a small
"SLEEP ARCHIVES" moon logo top-left, and bottom-left a small amber topic line
above a short hook (2-4 words, one or two lines) in huge white letters.

Style v1 (old): "SLEEP DOCUMENTARY" big across the top, the topic huge
bottom-left.

Usage:
    python3 tools/make_thumbnail.py scene.jpg thumb.jpg --hook "Before the Ash" --title "Pompeii  ·  79 AD"
    python3 tools/make_thumbnail.py scene.jpg thumb.jpg --stijl v1 --title "Pompeii: The Last Day"

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
AMBER = (246, 178, 92)
MOON = (250, 236, 200)
# v2 text stays in the left two thirds: YouTube puts the duration label bottom-right.
HOOK_W = int(1280 * 0.64)
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


def make(scene: Path, out: Path, title: str, subtitle: str, glow: bool = True) -> None:
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
    heavy_text(base, (x, main_top), main, main_font, night_glow=glow)

    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, quality=92)


def moon_logo(base: Image.Image, x: int, y: int) -> None:
    """Small crescent moon + 'SLEEP ARCHIVES', the same on every thumbnail."""
    font = ImageFont.truetype(str(LABEL_FONT), 34)
    text = "S L E E P   A R C H I V E S"
    r = 19
    cx, cy = x + r, y + 21
    glow = Image.new("L", base.size, 0)
    gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    gd.text((x + 2 * r + 16, y), text, font=font, fill=255)
    base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0),
               glow.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.8)))
    moon = Image.new("L", base.size, 0)
    md = ImageDraw.Draw(moon)
    md.ellipse((cx - r, cy - r, cx + r, cy + r), fill=255)
    md.ellipse((cx - r + 11, cy - r - 5, cx + r + 11, cy + r - 5), fill=0)
    base.paste(Image.new("RGB", base.size, MOON), (0, 0), moon)
    ImageDraw.Draw(base).text((x + 2 * r + 16, y), text, font=font, fill=MOON)


def split_hook(d: ImageDraw.ImageDraw, hook: str, max_w: int) -> list[str]:
    """One line if it fits big enough, otherwise two balanced lines."""
    words = hook.split()
    font = ImageFont.truetype(str(TITLE_FONT), 150)
    if len(words) < 3 or d.textlength(hook, font=font) <= max_w:
        return [hook]
    best = min(range(1, len(words)),
               key=lambda i: abs(d.textlength(" ".join(words[:i]), font=font)
                                 - d.textlength(" ".join(words[i:]), font=font)))
    return [" ".join(words[:best]), " ".join(words[best:])]


def make_v2(scene: Path, out: Path, hook: str, topic: str, glow: bool = True) -> None:
    base = cover(Image.open(scene).convert("RGB"))
    base = ImageEnhance.Color(base).enhance(1.3)
    base = ImageEnhance.Contrast(base).enhance(1.1)
    # A touch warmer: lamplight should feel cosy.
    r, g, b = base.split()
    base = Image.merge("RGB", (r.point(lambda v: min(255, int(v * 1.06))), g,
                               b.point(lambda v: int(v * 0.95))))

    # Darken only the bottom-left (text) and a little of the top-left (logo).
    shade = Image.new("L", (W, H))
    px = shade.load()
    for y in range(H):
        for x in range(W):
            bottom = max(0.0, 1 - ((x / W) * 0.9 + (H - y) / (H * 0.62)))
            top = max(0.0, 1 - (x / (W * 0.45) + y / (H * 0.16)))
            px[x, y] = int(190 * max(bottom, top * 0.8) ** 1.1)
    base = Image.composite(Image.new("RGB", (W, H), (6, 5, 10)), base, shade)

    d = ImageDraw.Draw(base)
    moon_logo(base, 34, 26)

    lines = split_hook(d, hook.upper(), HOOK_W)
    size = 170 if len(lines) == 1 else 116
    font = min((fit_font(d, ln, TITLE_FONT, HOOK_W, size) for ln in lines),
               key=lambda f: f.size)
    line_h = font.getbbox("HG")[3] + 6
    y = H - 36 - line_h * len(lines)
    if topic:
        tf = fit_font(d, topic.upper(), LABEL_FONT, HOOK_W, 50)
        ty = y - tf.getbbox("HG")[3] - 4
        shadow = Image.new("L", base.size, 0)
        ImageDraw.Draw(shadow).text((50, ty), topic.upper(), font=tf, fill=255,
                                    stroke_width=8, stroke_fill=255)
        base.paste(Image.new("RGB", base.size, (0, 0, 0)), (0, 0),
                   shadow.filter(ImageFilter.GaussianBlur(10)).point(lambda v: int(v * 0.85)))
        ImageDraw.Draw(base).text((50, ty), topic.upper(), font=tf, fill=AMBER,
                                  stroke_width=3, stroke_fill=OUTLINE)
    for ln in lines:
        heavy_text(base, (40, y), ln, font, night_glow=glow)
        y += line_h

    out.parent.mkdir(parents=True, exist_ok=True)
    base.save(out, quality=92)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("scene", type=Path, help="calm scene image from the video")
    parser.add_argument("out", type=Path)
    parser.add_argument("--stijl", choices=["v1", "v2"], default="v2")
    parser.add_argument("--hook", default="", help="v2: the big words, 2-4 words, e.g. 'Before the Ash'")
    parser.add_argument("--title", required=True,
                        help="v2: small amber topic line, e.g. 'Pompeii  ·  79 AD'; v1: the topic")
    parser.add_argument("--subtitle", default="", help="v1 only: optional, appended to the title")
    parser.add_argument("--no-glow", action="store_true", help="leave out the moonlight glow")
    args = parser.parse_args()
    if args.stijl == "v2":
        if not args.hook:
            parser.error("--hook is required for style v2")
        make_v2(args.scene, args.out, args.hook, args.title, glow=not args.no_glow)
    else:
        make(args.scene, args.out, args.title, args.subtitle, glow=not args.no_glow)
    print(f"Saved {args.out}")


if __name__ == "__main__":
    main()
