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
FOG_SPEED = 20   # pixels per seconde
FOG_OPACITY = 0.4


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
    frames = round(dur * FPS)
    segf = BEWEGING * FPS
    k = f"mod(floor(on/{segf})+{n},{len(STANDEN)})"
    k1 = f"mod(floor(on/{segf})+{n + 1},{len(STANDEN)})"
    p = f"((on-floor(on/{segf})*{segf})/{segf})"
    e = f"({p}*{p}*(3-2*{p}))"

    def sel(idx, i):
        v = [s[i] for s in STANDEN]
        expr = str(v[-1])
        for j in range(len(v) - 2, -1, -1):
            expr = f"if(eq({idx},{j}),{v[j]},{expr})"
        return expr

    def lerp(i):
        return f"({sel(k, i)}+({sel(k1, i)}-{sel(k, i)})*{e})"
    zoom, x, y = lerp(0), f"(iw-iw/zoom)*{lerp(1)}", f"(ih-ih/zoom)*{lerp(2)}"
    # Groot (4K) en in RGB, anders verspringt het beeld zichtbaar (zoompan schuift in hele
    # pixels, in YUV zelfs per 2). Het vergroten gebeurt één keer met Pillow, niet per beeldje.
    big = Path(out).with_suffix(".png")
    im = Image.open(img).convert("RGB")
    s = max(3840 / im.width, 2160 / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    l, t = (im.width - 3840) // 2, (im.height - 2160) // 2
    im.crop((l, t, l + 3840, t + 2160)).save(big)
    run(["-loop", "1", "-framerate", str(FPS), "-i", str(big), "-filter_complex",
         f"[0]format=rgb24,zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s=1920x1080:fps={FPS},format=yuv420p",
         "-frames:v", str(frames), "-c:v", "libx264", "-preset", "veryfast", "-crf", "16",
         str(out)])
    big.unlink()


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
    ap.add_argument("--muziek-db", type=float, default=-17, help="volume van de muziek in dB")
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
    with ThreadPoolExecutor(4) as ex:
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
    graph.append(f"[img][fog]blend=all_mode=screen:all_opacity={FOG_OPACITY},format=yuv420p[v]")

    if a.audio:
        inputs += ["-i", str(a.audio)]
    else:
        parts = sorted((story / "audio").glob("*-deel*.mp3"))
        concat = out_dir / "audio.txt"
        concat.write_text("".join(f"file '{p.resolve()}'\n" for p in parts))
        inputs += ["-f", "concat", "-safe", "0", "-i", str(concat)]
    audio_out = f"{n + 1}:a"
    if a.muziek:
        inputs += ["-i", str(a.muziek)]
        graph.append(f"[{n + 2}:a]volume={a.muziek_db}dB[m];"
                     f"[{n + 1}:a][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.9[a]")
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
