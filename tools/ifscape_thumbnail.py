#!/usr/bin/env python3
"""IfScape3D-thumbnail (16:9, 1280x720) in de vaste stijl van het kanaal (eigenaar, okt 2026).

Stijl: een echt beeld uit de eigen 3D-video (geen AI-beeld), links een donker verloop met
"WHAT IF" klein in oranje, daaronder de vraag groot in crème (Playfair Display Black), en de
"hook" (bv. een getal) groot in oranje cursief. Rechtsboven het logo (wereldbol met ring),
rechtsonder leeg (daar zet YouTube de videolengte).

Gebruik:
    python3 tools/ifscape_thumbnail.py video.mp4 thumb.jpg --tijd 239 \
        --vraag "THE WIND|NEVER|STOPPED?" --hook "1,000 km/h" --logo whatif-demo/branding/logo-cut.png

    --tijd   seconde in de video met het spannendste moment (bij voorkeur zonder tekst/HUD in beeld)
    --vraag  regels gescheiden door |, hoofdletters, max. ± 3 regels van ± 10 tekens
    --zoom   1.0 = heel beeld; 0.94 = iets ingezoomd (standaard). Het beeld wordt naar rechts
             uitgelijnd, zodat het belangrijke stuk rechts van de tekst valt.

Lettertype: Playfair Display uit npm (@fontsource/playfair-display); het script haalt het zelf
op met `npm pack` als het nog niet in ~/.cache/ifscape-fonts staat (vereist fonttools + brotli).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H = 1280, 720
CREAM = (246, 238, 224)
AMBER = (232, 166, 84)
FONTS = Path.home() / ".cache" / "ifscape-fonts"


def fonts() -> Path:
    """Playfair Display (Black, Bold, Bold Italic) als .ttf; eenmalig ophalen via npm."""
    need = ["900-normal", "700-normal", "700-italic"]
    if all((FONTS / f"pf-{n}.ttf").exists() for n in need):
        return FONTS
    FONTS.mkdir(parents=True, exist_ok=True)
    from fontTools.ttLib import TTFont  # pip install fonttools brotli
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["npm", "pack", "@fontsource/playfair-display@5", "--silent"], cwd=tmp, check=True,
                       stdout=subprocess.DEVNULL)
        tgz = next(Path(tmp).glob("*.tgz"))
        subprocess.run(["tar", "xzf", tgz.name], cwd=tmp, check=True)
        for n in need:
            f = TTFont(Path(tmp) / "package" / "files" / f"playfair-display-latin-{n}.woff2")
            f.flavor = None
            f.save(FONTS / f"pf-{n}.ttf")
    return FONTS


def frame(video: str, t: float) -> Image.Image:
    import imageio_ffmpeg
    raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-v", "error", "-ss", str(t), "-i", video,
                          "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True, check=True).stdout
    from io import BytesIO
    return Image.open(BytesIO(raw)).convert("RGB")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video"); ap.add_argument("out")
    ap.add_argument("--tijd", type=float, required=True)
    ap.add_argument("--vraag", required=True, help='regels gescheiden door |, bv. "THE WIND|NEVER|STOPPED?"')
    ap.add_argument("--hook", required=True, help='bv. "1,000 km/h"')
    ap.add_argument("--boven", default="WHAT IF")
    ap.add_argument("--logo", default="whatif-demo/branding/logo-cut.png")
    ap.add_argument("--zoom", type=float, default=0.94)
    a = ap.parse_args()

    fd = fonts()
    f = lambda n, s: ImageFont.truetype(str(fd / f"pf-{n}.ttf"), s)

    im = frame(a.video, a.tijd)
    w, h = im.size
    cw = int(w * a.zoom); ch = int(cw * 9 / 16)
    im = im.crop((w - cw, h - ch, w, h)).resize((W, H), Image.LANCZOS)
    im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.18)).enhance(1.25)

    g = Image.new("L", (W, H)); gd = ImageDraw.Draw(g)
    for x in range(W):
        gd.line([(x, 0), (x, H)], fill=int(max(0, 1 - x / (W * 0.55)) ** 1.4 * 200))
    im = Image.composite(Image.new("RGB", (W, H), (10, 14, 22)), im, g)

    def txt(xy, t, font, fill, blur=8):
        lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(lay).text((xy[0] + 3, xy[1] + 5), t, font=font, fill=(0, 0, 0, 210))
        lay = lay.filter(ImageFilter.GaussianBlur(blur)); im.paste(lay, (0, 0), lay)
        ImageDraw.Draw(im).text(xy, t, font=font, fill=fill)

    lines = [s.strip() for s in a.vraag.split("|") if s.strip()]
    big = 98 if len(lines) <= 3 else 80
    # te brede regels kleiner maken, zodat de tekst in de linker ± 45% blijft
    meet = ImageDraw.Draw(im)
    while big > 60 and max(meet.textlength(s, font=f("900-normal", big)) for s in lines) > W * 0.46:
        big -= 4
    txt((52, 46), a.boven, f("700-normal", 44), AMBER, 4)
    y = 98
    for s in lines:
        txt((48, y), s, f("900-normal", big), CREAM)
        y += int(big * 1.10)
    txt((52, y + 20), a.hook, f("700-italic", 92), AMBER)

    if Path(a.logo).exists():
        lg = Image.open(a.logo).convert("RGBA"); lg = lg.crop(lg.getbbox())
        lw = 250; lg = lg.resize((lw, int(lg.height * lw / lg.width)), Image.LANCZOS)
        px, py = W - lw - 26, 18
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        sh.paste(Image.new("RGBA", lg.size, (0, 0, 0, 255)), (px + 4, py + 8), lg.split()[3].point(lambda v: int(v * 0.75)))
        sh = sh.filter(ImageFilter.GaussianBlur(10))
        im.paste(sh, (0, 0), sh); im.paste(lg, (px, py), lg)
    else:
        print("let op: logo niet gevonden:", a.logo, file=sys.stderr)

    im.save(a.out, quality=92)
    print("Saved", a.out)


if __name__ == "__main__":
    main()
