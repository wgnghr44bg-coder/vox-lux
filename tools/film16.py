"""16mm-documentairelook (jaren 60/70) over een hele video, snel via ffmpeg (eigenaar 3 nov 2026: "die proef
video wel heel mooi en past ook echt erbij", zonder de rode lichtvlek; op tv, iPhone en tablet vloeiend).

Warme vale kleuren, zacht contrast (zwart iets opgetild), fijne zachte korrel, donkere randen met ronde hoeken,
en af en toe een stofje. Geen flikkeren. Geen krassen, geen lichtvlek, geen trillen: de beweging blijft gelijk.
Geluid wordt ongewijzigd gekopieerd.
Vuur (eigenaar 12 nov 2026: "vonken veel" over de hele video, bij alle video's): een naadloze lus van 40 s met een warme
flakkerende gloed van onderen en zwevende vonkjes (tools/effects.py: vonken 1.6 + vuur 0.8, op halve snelheid: eigenaar 12 nov "vlammen iets minder
 en minder snel"), één keer gemaakt en
bewaard in ~/vox-lux-cache, en hier snel door ffmpeg erbij opgeteld. Zonder: --zonder-vuur.

Gebruik: python tools/film16.py in.mp4 uit.mp4 [--zonder-vuur]
In de montage: na tools/eind_volume.py (<map>-14.mp4 -> <map>-16mm.mp4), daarna qc_video.py op het 16mm-bestand.
"""
import subprocess, sys, tempfile
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

FF = imageio_ffmpeg.get_ffmpeg_exe()
W, H, FPS = 1920, 1080, 25   # zelfde als make_video


def masker(pad):
    """Vignet met ronde, donkere filmhoeken (zoals een projectievenster)."""
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    v = np.clip(1.05 - 0.38 * (nx ** 2 + ny ** 2) ** 1.3, 0.3, 1)
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).rounded_rectangle([10, 8, W - 10, H - 8], radius=70, fill=255)
    m = np.asarray(m.filter(ImageFilter.GaussianBlur(14)), np.float32) / 255
    Image.fromarray((np.clip(v * (0.08 + 0.92 * m), 0, 1) * 255).astype(np.uint8)).convert("RGB").save(pad)


def stof(pad, sec=12):
    """Lus van een paar seconden met af en toe een klein licht stofje op zwart (wordt er 'opgeteld')."""
    rng = np.random.default_rng(16)
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "12", "-pix_fmt", "yuv420p", str(pad)],
                         stdin=subprocess.PIPE)
    for _ in range(sec * FPS):
        f = np.zeros((H, W), np.uint8)
        for _ in range(rng.poisson(1.2)):
            x, y, s = int(rng.uniform(0, W)), int(rng.uniform(0, H)), int(rng.integers(1, 3))
            f[max(0, y - s):y + s + 1, max(0, x - s):x + s + 1] = int(rng.uniform(40, 90))
        p.stdin.write(f.tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("stof-lus mislukt")


VUUR_LUS = Path.home() / "vox-lux-cache" / "vuurlus-v3.mp4"
VUUR_SEC, VUUR_FADE, VUUR_LICHT = 40, 3, 1.3     # lengte, overvloeien naar het begin (naadloos), extra gloed
VUUR, VONKEN, VUUR_TEMPO = 0.8, 1.6, 0.5          # sterkte gloed, aantal vonken, snelheid flakkeren en zweven


def vuurlus(pad=VUUR_LUS):
    """Gloed + vonken op zwart, naadloos rond (± 10 min, één keer)."""
    if pad.exists():
        return pad
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from effects import make_effect
    w, h, n, f = W, H, VUUR_SEC * FPS, VUUR_FADE * FPS

    def frames():
        rng = np.random.default_rng(12)
        eff = [make_effect("vuur", w, h, rng, VUUR), make_effect("vonken", w, h, rng, VONKEN)]
        zwart = np.zeros((h, w, 3), np.float32)
        for i in range(n + f):
            x = zwart
            for e in eff:
                x = e.apply(x, i / FPS * VUUR_TEMPO, VUUR_TEMPO / FPS, 1.0)
            yield x
    staart = [x for i, x in enumerate(frames()) if i >= n]          # ronde 1: alleen het stuk ná het einde
    pad.parent.mkdir(parents=True, exist_ok=True)
    tmp = pad.with_suffix(".tmp.mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv444p", str(tmp)],
                         stdin=subprocess.PIPE)
    for i, x in enumerate(frames()):                                 # ronde 2: zelfde zaad, begin vloeit over
        if i >= n:
            break
        if i < f:
            x = x * (i / f) + staart[i] * (1 - i / f)
        p.stdin.write((np.clip(x * VUUR_LICHT, 0, 1) * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    if p.wait():
        raise RuntimeError("vuur-lus mislukt")
    tmp.replace(pad)
    return pad


def main():
    inp, out = Path(sys.argv[1]), Path(sys.argv[2])
    vuur = "--zonder-vuur" not in sys.argv
    # kleur: 22 % grijs erdoor (vaal), dan warm (r 1.06, g 0.99, b 0.84)
    a, g = 0.78, 0.22 * np.array([0.30, 0.59, 0.11])
    rij = lambda i, k: " ".join(f"{k * ((a if j == i else 0) + g[j]):.4f}" for j in range(3))
    r, gg, b = rij(0, 1.06).split(), rij(1, 0.99).split(), rij(2, 0.84).split()
    mixer = (f"colorchannelmixer=rr={r[0]}:rg={r[1]}:rb={r[2]}:gr={gg[0]}:gg={gg[1]}:gb={gg[2]}"
             f":br={b[0]}:bg={b[1]}:bb={b[2]}")
    with tempfile.TemporaryDirectory() as tmp:
        mpad, spad = Path(tmp) / "masker.png", Path(tmp) / "stof.mp4"
        masker(mpad); stof(spad)
        fc = (f"[0:v]format=rgb24,{mixer},lutrgb=r='val*0.88+18':g='val*0.88+18':b='val*0.88+18',"
              # geen flikkeren (eigenaar 3 nov 2026: "ik zie een flikker door het beeld")
              "format=yuv444p,noise=c0s=6:c0f=t+u[k];"                   # fijne korrel, alleen in de helderheid
              "[k]format=gbrp[k1];"
              + ("[3:v]format=gbrp[f];[k1][f]blend=all_mode=addition[k2];" if vuur else "[k1]null[k2];")
              + "[1:v]format=gbrp[m];[k2][m]blend=all_mode=multiply[v];"
              "[2:v]format=gbrp[s];[v][s]blend=all_mode=addition,format=yuv420p[uit]")
        cmd = [FF, "-v", "error", "-y", "-i", str(inp), "-loop", "1", "-framerate", str(FPS), "-i", str(mpad),
               "-stream_loop", "-1", "-i", str(spad)] + (["-stream_loop", "-1", "-i", str(vuurlus())] if vuur else []) + [
               "-filter_complex", fc, "-map", "[uit]", "-map", "0:a?",
               "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-c:a", "copy",
               "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)
    print(f"16mm-look -> {out}")


if __name__ == "__main__":
    main()
