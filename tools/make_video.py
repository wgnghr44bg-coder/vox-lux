"""Maak de slaapvideo: rustig bewegend beeld (zoom + schuiven), zachte overgangen, drijvende mist.

Gebruik: python3 tools/make_video.py stories/pompeii [--tot SECONDEN]
Nodig: <map>/afbeeldingen/NNN.jpg, <map>/afbeeldingen-tijden.tsv, <map>/audio/*-deel*.mp3.
Uitvoer: <map>/video/clips/NNN.mp4 (tussenstap) en <map>/video/<map>.mp4.
--tot rendert alleen de eerste SECONDEN (om te testen).
"""
import argparse, csv, subprocess, sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image
from concurrent.futures import ThreadPoolExecutor

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
FPS = 25
XFADE = 1.5      # seconden overgang tussen afbeeldingen
FOG_SPEED = 25   # pixels per seconde; = 1 pixel per beeldje, anders schokt de mist (0-1-1-1-0)
FOG_OPACITY = 0.4
# Avondeffect v2 (eigenaar, 30 okt 2026): iets donkerder, kleuren gewoon (geen gele "ansichtkaart"-lucht),
# randen zacht donker. Alleen het beeld; titels/kaarten van motion.py en de thumbnail blijven zoals ze zijn.
AVOND = ("format=yuv444p,eq=brightness=-0.02:gamma=0.85:contrast=1.02,format=gbrp,"
         "colorbalance=rs=0.04:bs=-0.03:rm=0.03:bm=-0.03,vignette=angle=PI/5,")


def run(args):
    subprocess.run([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", *args], check=True)


def make_fog(path):
    """Zachte mist-textuur (grijs), onderin dichter; naadloos herhaalbaar door spiegeling."""
    def octave(size, seed, sigma):
        return (f"color=c=gray:s={size},format=gray,noise=alls=100:allf=u:all_seed={seed},"
                f"scale=3840:1080:flags=bicubic,gblur=sigma={sigma},format=gray")
    run(["-f", "lavfi", "-i", octave("32x9", 11, 70), "-f", "lavfi", "-i", octave("128x36", 22, 25),
         "-filter_complex",
         "[0][1]blend=all_expr='A*0.7+B*0.3',format=gray,"
         "curves=all='0/0 0.4/0.08 0.7/0.8 1/1',geq=lum='lum(X,Y)*(0.35+0.65*Y/H)',format=gray,"
         "split[a][b];[b]hflip[f];[a][f]hstack,split[s][t];[t]crop=1920:1080:0:0[head];[s][head]hstack",
         "-frames:v", "1", str(path)])


# Beweging: elke BEWEGING seconden schuift het beeld rustig naar de volgende stand
# (inzoomen, opzij, uitzoomen, andere kant op), met zachte start en stop. Zo staat het
# beeld nooit stil, ook niet bij afbeeldingen van 1,5 minuut. (zoom, x, y); x/y = 0..1 van de marge.
BEWEGING = 18
STANDEN = [(1.04, 0.50, 0.50), (1.18, 0.50, 0.38), (1.18, 0.12, 0.45), (1.10, 0.88, 0.58)]


def make_clip(img, out, dur, n):
    """Een afbeelding met langzame, steeds wisselende zoom- en schuifbewegingen."""
    # Elk beeldje wordt zelf berekend met fracties van een pixel (Pillow, bicubisch). zoompan schoof in
    # hele pixels: bij deze trage beweging stond het beeld dan even stil en sprong het, en dat zag je op
    # een groot tv-scherm als trillen (eigenaar, 2 nov 2026). Gemeten: zoompan 59% stilstaande beeldjes.
    frames = round(dur * FPS)
    segf = BEWEGING * FPS
    zmax = max(s[0] for s in STANDEN)
    im = Image.open(img).convert("RGB")
    s = max(1920 * zmax / im.width, 1080 * zmax / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    W, H = round(1920 * zmax), round(1080 * zmax)      # midden 16:9, zoals vroeger; bij zoom zmax 1 op 1
    l, t = (im.width - W) // 2, (im.height - H) // 2
    im = im.crop((l, t, l + W, t + H))
    proc = subprocess.Popen([FFMPEG, "-hide_banner", "-loglevel", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
                             "-s", "1920x1080", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast",
                             "-crf", "16", "-pix_fmt", "yuv420p", str(out)], stdin=subprocess.PIPE)
    for on in range(frames):
        k, p = divmod(on, segf)
        a, b = STANDEN[(k + n) % len(STANDEN)], STANDEN[(k + n + 1) % len(STANDEN)]
        p /= segf
        e = p * p * (3 - 2 * p)
        z, fx, fy = (a[i] + (b[i] - a[i]) * e for i in range(3))
        cw, ch = W / z, H / z                       # zichtbaar stuk van de bron
        x0, y0 = (W - cw) * fx, (H - ch) * fy
        sc = cw / 1920
        fr = im.transform((1920, 1080), Image.AFFINE, (sc, 0, x0, 0, sc, y0), Image.BICUBIC)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    if proc.wait():
        raise RuntimeError(f"ffmpeg faalde voor {out}")


GROEP = 20      # max. aantal clips per ffmpeg-stap (geheugen)


def chain_inputs(rows):
    return [x for r in rows for x in ("-i", str(r["clip"]))]


def chain_graph(rows):
    """xfade-keten; een overgang begint op het moment dat de volgende afbeelding start."""
    graph, last = [], "[0:v]"
    for i in range(1, len(rows)):
        offset = float(rows[i]["start"]) - float(rows[0]["start"])
        graph.append(f"{last}[{i}:v]xfade=transition=fade:duration={XFADE}:offset={offset:.3f}[x{i}]")
        last = f"[x{i}]"
    if not graph:  # een enkele clip
        graph.append("[0:v]null[x0]")
        last = "[x0]"
    return graph, last


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("story", type=Path)
    ap.add_argument("--tot", type=float, help="alleen de eerste zoveel seconden")
    ap.add_argument("--tijden", default="afbeeldingen-tijden.tsv", help="bestand in de verhaalmap")
    ap.add_argument("--audio", type=Path, help="stem-bestand (standaard: audio/*-deel*.mp3 aan elkaar)")
    ap.add_argument("--muziek", type=Path, help="achtergrondmuziek (bv. van tools/ambient_432.py)")
    ap.add_argument("--muziek-db", type=float, default=-20, help="volume van de muziek in dB")
    ap.add_argument("--geluid", type=Path,
                    help="natuurgeluiden per scène (van tools/ambient_sfx.py, al op het goede niveau)")
    ap.add_argument("--geen-avond", action="store_true", help="zonder avondeffect (oude video's)")
    ap.add_argument("--naam", help="naam van de eindvideo (zonder .mp4)")
    ap.add_argument("--preset", default="medium",
                    help="x264-preset van de eindvideo (veryfast: ± 3x sneller, iets groter bestand)")
    a = ap.parse_args()
    story = a.story
    rows = list(csv.DictReader(open(story / a.tijden), delimiter="\t"))
    if a.tot:
        rows = [r for r in rows if float(r["start"]) < a.tot]
        rows[-1]["end"] = str(min(float(rows[-1]["end"]), a.tot))
    total = float(rows[-1]["end"])

    out_dir = story / "video"
    clips = out_dir / "clips"
    clips.mkdir(parents=True, exist_ok=True)
    fog = out_dir / "mist.png"
    if not fog.exists():
        make_fog(fog)

    # 1. Clips per afbeelding. Elke clip (behalve de laatste) is XFADE langer, voor de overgang.
    #    4 tegelijk (4 cores). Eerst naar een tijdelijke naam, zodat een afgebroken clip
    #    de volgende keer opnieuw gemaakt wordt.
    todo = []
    for i, r in enumerate(rows):
        dur = float(r["end"]) - float(r["start"]) + (XFADE if i < len(rows) - 1 else 0)
        out = clips / f"{Path(r['file']).stem}-{dur:.2f}-b2.mp4"   # b2 = nieuwe beweging
        if not out.exists():
            todo.append((story / "afbeeldingen" / r["file"], out, dur, i))
        r["clip"] = out

    def one(job):
        img, out, dur, i = job
        print(f"clip {img.name} ({dur:.0f} s)", flush=True)
        tmp = out.with_name("tmp-" + out.name)
        make_clip(img, tmp, dur, i)
        tmp.replace(out)
    with ThreadPoolExecutor(8) as ex:   # Pillow rekent buiten de GIL, 8 tegelijk is ± 3x zo snel
        list(ex.map(one, todo))

    # 1b. Veel afbeeldingen tegelijk openen kost te veel geheugen (75 clips: ffmpeg gestopt
    #     door geheugentekort). Daarom eerst groepjes van GROEP clips aan elkaar zetten.
    #     Elk groepje is net als een clip XFADE langer, zodat de overgangen gelijk blijven.
    if len(rows) > GROEP:
        groups = []
        for g in range(0, len(rows), GROEP):
            part = rows[g:g + GROEP]
            out = clips / f"groep-{part[0]['clip'].stem}-{part[-1]['clip'].stem}.mp4"
            if not out.exists():
                print(f"groep {part[0]['file']} t/m {part[-1]['file']}", flush=True)
                run([*chain_inputs(part), "-filter_complex", ";".join(chain_graph(part)[0]),
                     "-map", chain_graph(part)[1], "-c:v", "libx264", "-preset", "veryfast",
                     "-crf", "16", "-pix_fmt", "yuv420p", str(out)])
            groups.append({"start": part[0]["start"], "clip": out})
        rows_final = groups
    else:
        rows_final = rows

    # 2. Alles samen: overgangen, mist, audio.
    inputs, (graph, last) = chain_inputs(rows_final), chain_graph(rows_final)
    n = len(rows_final)
    inputs += ["-loop", "1", "-framerate", str(FPS), "-i", str(fog)]
    graph.append(f"[{n}:v]format=gray,crop=1920:1080:x='mod(t*{FOG_SPEED},7680)':y=0,"
                 f"format=gbrp,colorchannelmixer=rr=1:gg=0.97:bb=0.92[fog]")
    graph.append(f"{last}format=gbrp[img]")
    graph.append(f"[img][fog]blend=all_mode=screen:all_opacity={FOG_OPACITY},"
                 f"{'' if a.geen_avond else AVOND}format=yuv420p[v]")

    if a.audio:
        inputs += ["-i", str(a.audio)]
    else:
        parts = sorted((story / "audio").glob("*-deel*.mp3"))
        concat = out_dir / "audio.txt"
        concat.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        inputs += ["-f", "concat", "-safe", "0", "-i", str(concat)]
    audio_out = f"{n + 1}:a"
    beds = []
    if a.muziek:
        inputs += ["-i", str(a.muziek)]
        graph.append(f"[{n + 1 + len(beds) + 1}:a]volume={a.muziek_db}dB[m]")
        beds.append("[m]")
    if a.geluid:
        inputs += ["-i", str(a.geluid)]
        graph.append(f"[{n + 1 + len(beds) + 1}:a]anull[g]")
        beds.append("[g]")
    if beds:
        graph.append(f"[{n + 1}:a]{''.join(beds)}amix=inputs={len(beds) + 1}:duration=first:"
                     f"normalize=0,alimiter=limit=0.9[a]")
        audio_out = "[a]"

    name = a.naam or story.name
    final = out_dir / f"{name}{'-test' if a.tot else ''}.mp4"
    print(f"eindvideo {final} ({total / 60:.1f} min)", flush=True)
    run([*inputs, "-filter_complex", ";".join(graph), "-map", "[v]", "-map", audio_out,
         "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", a.preset, "-crf", "26",
         "-tune", "stillimage", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
         str(final)])
    print("klaar:", final)


if __name__ == "__main__":
    sys.exit(main())
