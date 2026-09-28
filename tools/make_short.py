"""Maak verticale YouTube Shorts / TikToks (1080x1920) uit een stukje van een sleep documentary.

Het beeld is de 16:9-afbeelding die het hele scherm vult en langzaam van links naar rechts
(of andersom) schuift, met zachte overgangen en drijvende mist zoals in de lange video.
Grote ondertitels per zin (Pillow; de ffmpeg-build heeft geen drawtext), 432 Hz-muziek
op -17 dB. Met --eindtekst komt er in de laatste 3 seconden "Full sleep documentary on
the channel" (standaard uit: de eigenaar wil het simpel houden).

Gebruik:
  python3 tools/make_short.py stories/pompeii --van 509 --tot 516 --naam 1-wolk
  python3 tools/make_short.py stories/pompeii --lijst shorts.tsv [--alleen 1-wolk]
--van/--tot zijn zinsnummers (kolom # in tijdlijn-pauzes.tsv), allebei inclusief.
shorts.tsv (in de verhaalmap) heeft de kolommen naam, van, tot en weetje (plus eventueel meer).
Een weetje (--weetje) komt bovenin als "DID YOU KNOW?" + één zin die in het stukje verteld wordt.

Nodig: eerst `python3 tools/add_pauses.py stories/<verhaal>` (maakt video/stem-met-pauzes.wav,
tijdlijn-pauzes.tsv en afbeeldingen-tijden-pauzes.tsv) en <map>/afbeeldingen/NNN.jpg.
Uitvoer: <map>/video/shorts/<naam>.mp4
"""
import argparse, csv, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from make_video import make_fog  # noqa: E402

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1080, 1920, 25
XFADE = 1.5          # seconden overgang tussen afbeeldingen
PAN_SPEED = 28       # pixels per seconde dat het beeld opschuift
FOG_SPEED = 36       # pixels per seconde (mist, op 1920 hoog)
FOG_OPACITY = 0.4
LEAD = 0.4           # stilte voor de eerste zin
OUTRO = 3.0          # laatste seconden: verwijzing naar de lange video (--eindtekst)
TAIL = 0.8           # zonder eindtekst: zoveel rust na de laatste zin
OUTRO_GAP = 0.6      # stilte tussen de laatste zin en de eindtekst
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
SUB_FONT = FONT_DIR / "DejaVuSerif-Bold.ttf"
OUTRO_FONT = FONT_DIR / "DejaVuSerif.ttf"
LABEL_FONT = FONT_DIR / "DejaVuSans-Bold.ttf"
FACT_SIZE, FACT_Y = 56, 250                   # FACT_Y = bovenkant van het weetje-blok
LABEL_COLOR = (242, 204, 128, 255)            # warm goud
SUB_SIZE, SUB_MAX_W, SUB_Y = 68, 920, 1330   # SUB_Y = midden van het ondertitelblok
OUTRO_TEXT = "Full sleep documentary\non the channel"


def sec(x):
    h, m, s = x.split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        test = f"{cur} {word}".strip()
        if draw.textlength(test, font=font) <= max_w or not cur:
            cur = test
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


def text_layer(text, font_path, size, stroke, lines=None, fill=(255, 255, 255, 255)):
    """Witte tekst met donkere rand en zachte schaduw, als RGBA-plaatje (W breed)."""
    font = ImageFont.truetype(str(font_path), size)
    probe = ImageDraw.Draw(Image.new("L", (1, 1)))
    lines = lines or wrap(probe, text, font, SUB_MAX_W)
    lh = int(size * 1.28)
    h = lh * len(lines) + 2 * stroke + 40
    shadow = Image.new("L", (W, h), 0)
    sd, img = ImageDraw.Draw(shadow), Image.new("RGBA", (W, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for i, line in enumerate(lines):
        y = 20 + stroke + i * lh
        sd.text((W / 2, y + 4), line, font=font, anchor="ma", fill=200,
                stroke_width=stroke + 6, stroke_fill=200)
        d.text((W / 2, y), line, font=font, anchor="ma", fill=fill,
               stroke_width=stroke, stroke_fill=(18, 14, 12, 255))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10))
    out = Image.new("RGBA", (W, h), (0, 0, 0, 0))
    out.putalpha(shadow.point(lambda v: int(v * 0.55)))
    out = Image.alpha_composite(out, img)
    a = np.asarray(out).astype(np.float32) / 255
    return a[..., :3], a[..., 3:]


def ramp(t, a, b, fade):
    """0..1: fadet in vanaf a en uit tot b."""
    return float(np.clip(min(t - a, b - t) / fade, 0, 1))


class Pan:
    """Een 16:9-afbeelding, schermvullend (1920 hoog), die langzaam opzij schuift."""

    def __init__(self, path, t_in, t_out, direction):
        img = Image.open(path).convert("RGB")
        scale = H / img.height
        self.img = img.resize((max(W, round(img.width * scale)), H), Image.LANCZOS)
        span = self.img.width - W
        travel = min(span, PAN_SPEED * (t_out - t_in))
        x0 = (span - travel) / 2
        self.x_from, self.x_to = (x0, x0 + travel) if direction > 0 else (x0 + travel, x0)
        self.t_in, self.t_out = t_in, t_out

    def frame(self, t):
        p = np.clip((t - self.t_in) / max(self.t_out - self.t_in, 1e-6), 0, 1)
        p = p * p * (3 - 2 * p) * 0.3 + p * 0.7   # heel licht afgeronde start en eind
        x = self.x_from + (self.x_to - self.x_from) * p
        f = self.img.transform((W, H), Image.AFFINE, (1, 0, x, 0, 1, 0), Image.BILINEAR)
        return np.asarray(f).astype(np.float32) / 255


def make_short(story, van, tot, naam, seed, weetje="", eindtekst=False):
    tl = {int(r[0]): r for r in (l.split("\t") for l in
          open(story / "tijdlijn-pauzes.tsv").read().splitlines()[1:] if l.strip())}
    sents = [(sec(tl[i][1]), sec(tl[i][2]), tl[i][4].strip()) for i in range(van, tot + 1)]
    t0 = sents[0][0] - LEAD
    speech_end = sents[-1][1] - t0
    outro_at = speech_end + OUTRO_GAP
    total = outro_at + (OUTRO if eindtekst else TAIL)
    print(f"{naam}: zinnen {van}-{tot}, {total:.1f} s", flush=True)
    if not 40 <= total <= 62:
        print(f"  let op: {total:.1f} s valt buiten 45-60 s")

    # afbeeldingen die in dit stuk vallen (tijden relatief aan t0)
    imgs = list(csv.DictReader(open(story / "afbeeldingen-tijden-pauzes.tsv"), delimiter="\t"))
    pans = []
    for i, r in enumerate(imgs):
        s, e = float(r["start"]) - t0, float(r["end"]) - t0
        if e + XFADE <= 0 or s >= total:
            continue
        t_in, t_out = max(s, 0), min(e + XFADE, total)
        direction = 1 if (int(Path(r["file"]).stem) + len(pans)) % 2 else -1
        pans.append((max(s, 0), Pan(story / "afbeeldingen" / r["file"], t_in, t_out, direction)))

    # mist (zelfde textuur als de lange video), geschaald naar 1920 hoog
    fog_png = story / "video" / "mist.png"
    if not fog_png.exists():
        make_fog(fog_png)
    fog_img = Image.open(fog_png).convert("L")
    fog_img = fog_img.resize((round(fog_img.width * H / fog_img.height), H), Image.BILINEAR)
    fog = np.asarray(fog_img).astype(np.float32)[..., None] / 255 * np.array([1, 0.97, 0.92], np.float32)
    fog_period = 7680 * H / 1080

    subs = []
    for k, (s, e, text) in enumerate(sents):
        a = s - t0 - 0.1
        b = min(e - t0 + 0.5, (sents[k + 1][0] - t0 - 0.15) if k + 1 < len(sents) else outro_at)
        rgb, alpha = text_layer(text, SUB_FONT, SUB_SIZE, 6)
        subs.append((a, b, rgb, alpha, SUB_Y - rgb.shape[0] // 2))
    o_rgb, o_alpha = text_layer("", OUTRO_FONT, 62, 5, lines=OUTRO_TEXT.split("\n"))
    o_y = H // 2 - o_rgb.shape[0] // 2
    facts = []
    if weetje:
        l_rgb, l_alpha = text_layer("", LABEL_FONT, 44, 5, lines=["DID YOU KNOW?"], fill=LABEL_COLOR)
        f_rgb, f_alpha = text_layer(weetje, SUB_FONT, FACT_SIZE, 6)
        facts = [(l_rgb, l_alpha, FACT_Y), (f_rgb, f_alpha, FACT_Y + l_rgb.shape[0] - 30)]

    # audio: stem-stuk + muziek
    out_dir = story / "video" / "shorts"
    out_dir.mkdir(parents=True, exist_ok=True)
    music = out_dir / f"{naam}-muziek.wav"
    subprocess.run([sys.executable, str(Path(__file__).parent / "ambient_432.py"), str(music),
                    "--duur", f"{total + 2:.1f}", "--seed", str(seed)], check=True)
    voice_len = speech_end + 0.3
    final = out_dir / f"{naam}.mp4"
    graph = (f"[1:a]atrim=start={t0:.3f}:duration={voice_len:.3f},asetpts=PTS-STARTPTS,"
             f"afade=t=in:d=0.05,afade=t=out:st={voice_len - 0.3:.3f}:d=0.3,"
             f"aformat=channel_layouts=stereo,apad[v];"
             f"[2:a]volume=-17dB[m];[v][m]amix=inputs=2:duration=shortest:normalize=0,"
             f"alimiter=limit=0.9,afade=t=out:st={total - 1.5:.3f}:d=1.5[a]")
    enc = subprocess.Popen(
        [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
         "-i", str(story / "video" / "stem-met-pauzes.wav"), "-i", str(music),
         "-filter_complex", graph, "-map", "0:v", "-map", "[a]", "-t", f"{total:.3f}",
         "-c:v", "libx264", "-preset", "medium", "-crf", "21", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(final)],
        stdin=subprocess.PIPE)

    n_frames = int(round(total * FPS))
    for f in range(n_frames):
        t = f / FPS
        # beeld: nieuwste afbeelding fadet over de vorige heen
        active = [(s, p) for s, p in pans if p.t_in <= t < p.t_out + 1e-6] or [pans[-1]]
        frame = active[0][1].frame(t)
        for s, p in active[1:]:
            w = np.clip((t - s) / XFADE, 0, 1) if s > 0 else 1.0
            frame = frame * (1 - w) + p.frame(t) * w if w < 1 else p.frame(t)
        # mist (screen-blend)
        x = int(t * FOG_SPEED) % int(fog_period)
        fg = fog[:, x:x + W]
        frame = frame + ((1 - (1 - frame) * (1 - fg)) - frame) * FOG_OPACITY
        # eindtekst: beeld iets donkerder, tekst fadet in
        if eindtekst and t >= outro_at:
            k = ramp(t, outro_at, total + 10, 0.8)
            frame *= 1 - 0.35 * k
            region = frame[o_y:o_y + o_rgb.shape[0]]
            region += (o_rgb - region) * o_alpha * k
        # weetje bovenin, tot de eindtekst
        if facts:
            k = ramp(t, 0.2, outro_at if eindtekst else total + 10, 0.6)
            for rgb, alpha, y in facts:
                region = frame[y:y + rgb.shape[0]]
                region += (rgb - region) * alpha * k
        # ondertitels
        for a, b, rgb, alpha, y in subs:
            if a <= t <= b:
                k = ramp(t, a, b, 0.2)
                region = frame[y:y + rgb.shape[0]]
                region += (rgb - region) * alpha * k
        if t < 0.3:
            frame *= t / 0.3
        enc.stdin.write((np.clip(frame, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
        if f % (FPS * 10) == 0:
            print(f"  {t:.0f}/{total:.0f} s", flush=True)
    enc.stdin.close()
    if enc.wait():
        sys.exit("ffmpeg gaf een fout")
    music.unlink()
    print(f"klaar: {final} ({final.stat().st_size / 1e6:.1f} MB)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("--van", type=int)
    ap.add_argument("--tot", type=int)
    ap.add_argument("--naam")
    ap.add_argument("--weetje", default="", help='zin bovenin onder "DID YOU KNOW?"')
    ap.add_argument("--lijst", help="tsv in de verhaalmap met kolommen naam, van, tot")
    ap.add_argument("--alleen", help="alleen deze naam uit de lijst")
    ap.add_argument("--eindtekst", action="store_true", help='"Full sleep documentary on the channel" aan het eind')
    ap.add_argument("--seed", type=int, default=7, help="muziek-zaadje")
    a = ap.parse_args()
    if a.lijst:
        rows = list(csv.DictReader(open(a.story / a.lijst), delimiter="\t"))
        for r in rows:
            if not a.alleen or r["naam"] == a.alleen:
                make_short(a.story, int(r["van"]), int(r["tot"]), r["naam"], a.seed,
                           r.get("weetje") or "", a.eindtekst)
    elif a.van and a.tot:
        make_short(a.story, a.van, a.tot, a.naam or f"short-{a.van}", a.seed, a.weetje, a.eindtekst)
    else:
        ap.error("geef --van en --tot, of --lijst")


if __name__ == "__main__":
    main()
