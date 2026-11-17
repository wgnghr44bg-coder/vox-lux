"""Monteert een bodycam-video in de EWU-vorm, in ÉÉN ffmpeg-keer (geen losse stukken plakken = geen naden).

  python kanalen/bodycam/monteer.py kanalen/bodycam/videos/<map> [--uit proef.mp4]

plan.json = lijst van stukken op volgorde:
  {"soort": "origineel", "bron": [612.0, 628.5], "beeld": "bodycam"}
        echt geluid van de bron, met ondertitels (uit Whisper: <map>/bron/whisper.json), GEEN verteller
  {"soort": "stem", "blok": 1, "bron": [[230, 252]], "beeld": "bodycam"}
        onze verteller (stem/blokNN.wav), bron-geluid UIT; bronbeeld loopt zo lang als de stem (+0,5 s), is het te kort
        dan loopt het laatste bronstuk door. Nooit vertragen of stilzetten.
beeld: "bodycam" (4:3 in zwarte randen -> wazige vulling), "vol" (zoals het is), "kaart" (onderste ondertitels weg).
Regels eigenaar 17 nov: nooit stem en echt geluid tegelijk; niet haperen; 29,97 fps zoals de bodycams.
"""
import json, re, subprocess, sys
from pathlib import Path

W, H, FPS = 1920, 1080, "30000/1001"
FONT = "arial.ttf"


def duur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def esc(t):
    return (t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace(",", "\\,")
            .replace("%", "\\%").replace("[", "(").replace("]", ")"))


def regels_ondertitel(chunks, a, b, max_tekens=60):
    """Whisper-stukjes binnen [a, b] -> [(start, eind, tekst)] relatief aan a, lange zinnen in 2 regels."""
    uit = []
    for c in chunks:
        s, e = c["timestamp"]
        e = e if e is not None else s + 3
        if e <= a or s >= b:
            continue
        t = c["text"].strip()
        if len(t) > max_tekens:                       # in twee regels knippen op een spatie bij het midden
            k = t.rfind(" ", 0, len(t) // 2 + 10)
            t = t[:k] + "\n" + t[k + 1:] if k > 0 else t
        uit.append((max(0, s - a), min(b, e) - a, t))
    return uit


def main():
    map_ = Path(sys.argv[1]).resolve()
    uit = map_ / (sys.argv[sys.argv.index("--uit") + 1] if "--uit" in sys.argv else "proef.mp4")
    plan = json.loads((map_ / "plan.json").read_text(encoding="utf-8"))
    bron = map_ / "bron" / "bron.mp4"
    whisper = json.loads((map_ / "bron" / "whisper.json").read_text(encoding="utf-8"))
    blokken = {b["blok"]: b for b in json.loads((map_ / "stem" / "blokken.json").read_text(encoding="utf-8"))}
    credit = (map_ / "bronvermelding.txt").read_text(encoding="utf-8").splitlines()[0].split(" – ")[0].strip()
    tmp = map_ / "build"
    tmp.mkdir(exist_ok=True)
    (tmp / FONT).write_bytes(Path("C:/Windows/Fonts/arial.ttf").read_bytes())

    inputs, fc, labels, n_in = [], [], [], 0
    for i, st in enumerate(plan):
        if st["soort"] == "origineel":
            a, b = st["bron"]
            stukken, lengte = [[a, b]], b - a
        else:
            blok = blokken[st["blok"]]
            lengte = blok["duur"] + 0.5
            stukken = [list(x) for x in st["bron"]]
            heb = sum(e - s for s, e in stukken)
            if lengte > heb:
                stukken[-1][1] += lengte - heb + 0.1
        # video: elk bronstuk een eigen input met nauwkeurig zoeken (-ss voor -i), dan aan elkaar binnen dit stuk
        vlabels = []
        for s, e in stukken:
            inputs += ["-ss", f"{s:.3f}", "-t", f"{e - s:.3f}", "-i", str(bron)]
            vlabels.append(f"[{n_in}:v]")
            bron_audio = n_in
            n_in += 1
        vin = "".join(vlabels)
        v = f"{vin}concat=n={len(vlabels)}:v=1:a=0," if len(vlabels) > 1 else f"{vin}"
        v += "setpts=PTS-STARTPTS,"
        beeld = st.get("beeld", "bodycam")
        if beeld == "bodycam":
            v += (f"crop=1440:1080:240:0,split[a{i}][b{i}];[a{i}]scale={W}:-2,crop={W}:{H},boxblur=30:2,"
                  f"eq=brightness=-0.15[bg{i}];[b{i}]scale=-2:{H}[fg{i}];[bg{i}][fg{i}]overlay=(W-w)/2:0,")
        elif beeld == "kaart":
            v += f"crop=iw*0.86:ih*0.86:(iw-ow)/2:0,scale={W}:{H},"
        else:
            v += f"scale={W}:{H},"
        if st["soort"] == "stem" and st.get("verberg_ondertitels", True):
            # ondertitels die het korps in het beeld heeft gezet horen bij geluid dat je nu niet hoort -> onderste strook
            # vervagen (anders lees je zinnen die niemand zegt)
            v += (f"split[o{i}][p{i}];[p{i}]crop=iw:ih*0.2:0:ih*0.8,boxblur=25:3[q{i}];"
                  f"[o{i}][q{i}]overlay=0:H*0.8,")
        v += f"fps={FPS},trim=0:{lengte:.3f},setpts=PTS-STARTPTS"
        tekst = [f"drawtext=fontfile={FONT}:text='{esc(credit)}':x=w-tw-28:y=h-th-24:fontsize=24:"
                 "fontcolor=white@0.75:box=1:boxcolor=black@0.35:boxborderw=8"]
        if st["soort"] == "origineel" and st.get("ondertitels", True):   # eigen ondertitels (niet als de bron ze al heeft)
            for s, e, t in regels_ondertitel(whisper, *st["bron"]):
                tekst.append(f"drawtext=fontfile={FONT}:text='{esc(t)}':x=(w-tw)/2:y=h-200:fontsize=44:"
                             f"fontcolor=white:borderw=3:bordercolor=black:line_spacing=10:"
                             f"enable='between(t,{s:.2f},{e:.2f})'")
        if st.get("tekst"):
            tekst.append(f"drawtext=fontfile={FONT}:text='{esc(st['tekst'])}':x=60:y=60:fontsize=42:fontcolor=white:"
                         "box=1:boxcolor=black@0.55:boxborderw=16:enable='between(t,0.3,6)'")
        fc.append(v + "," + ",".join(tekst) + f",format=yuv420p[v{i}]")
        # audio: óf echt geluid, óf onze stem — nooit allebei
        if st["soort"] == "origineel":
            fc.append(f"[{bron_audio}:a]aformat=sample_rates=48000:channel_layouts=stereo,"
                      # bodycam-geluid is vaak zacht en ongelijk: op hetzelfde volume brengen als de stem
                      f"highpass=f=80,dynaudnorm=f=250:g=15:m=12,loudnorm=I=-16:TP=-2:LRA=9,aresample=48000,"
                      f"atrim=0:{lengte:.3f},apad=whole_dur={lengte:.3f},asetpts=PTS-STARTPTS[a{i}]")
        else:
            inputs += ["-i", str(map_ / "stem" / blokken[st["blok"]]["bestand"])]
            fc.append(f"[{n_in}:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=250|250,"
                      f"loudnorm=I=-16:TP=-2:LRA=9,aresample=48000,apad=whole_dur={lengte:.3f},atrim=0:{lengte:.3f},asetpts=PTS-STARTPTS[a{i}]")
            n_in += 1
        labels.append(f"[v{i}][a{i}]")
    totaal = len(plan)
    fc.append("".join(labels) + f"concat=n={totaal}:v=1:a=1[vc][ac]")
    fc.append("[ac]loudnorm=I=-14:TP=-1:LRA=11,aresample=48000[af]")
    (tmp / "filter.txt").write_text(";\n".join(fc), encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *inputs, "-/filter_complex", "filter.txt",
                    "-map", "[vc]", "-map", "[af]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-r", FPS, "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(uit)],
                   check=True, cwd=tmp)
    print(f"klaar: {uit} ({duur(uit):.1f} s)")


if __name__ == "__main__":
    main()
