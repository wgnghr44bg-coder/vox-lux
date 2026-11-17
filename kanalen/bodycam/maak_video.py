"""Monteert een bodycam-video uit bron.mp4 + de voice-over-blokken (stem/blokken.json) volgens plan.json.

  python kanalen/bodycam/maak_video.py kanalen/bodycam/videos/<map> [--uit proef.mp4]

plan.json = lijst van stukken, op volgorde:
  {"blok": 1, "bron": [[212, 227], [227, 240]], "soort": "bodycam", "tekst": "optionele onderschrift-regel"}
  {"blok": null, "bron": [[402, 424]], "soort": "vol", "geluid": "origineel"}     # stuk zonder stem, echt geluid
soort: "bodycam" (4:3 in zwarte randen -> wazige achtergrond), "kaart" (onderste ondertitels van de bron wegsnijden),
       "vol" (beeld zoals het is).
geluid: "origineel" (STANDAARD: echt geluid, zakt automatisch weg onder onze stem) / "uit" (STANDAARD bij "kaart":
       de korps-verteller wordt vervangen door onze stem) / "onder" (vast -18 dB). Eigenaar 17 nov: origineel geluid
       behouden, alleen de verteller vervangen. Spraak van een verteller in een bronstuk: controleer met Whisper.
Met stem: het bronbeeld loopt zo lang als het stemblok (+0,6 s); te kort -> iets vertraagd (max 1,35x), daarna
stilstaand laatste beeld. Eindvolume -14 LUFS (zoals tools/eind_volume.py).
Rechtsonder klein "Footage: <bron>" (uit bronvermelding.txt, eerste woorden tot " – ").
"""
import json, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
FONT = "arial.ttf"  # wordt naast de tijdelijke bestanden gezet (ffmpeg op Windows kan slecht met C:-paden in filters)
W, H, FPS = 1920, 1080, 30


CWD = None


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, a)], check=True, cwd=CWD)


def duur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True, check=True).stdout)


def esc(t):
    return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\u2019").replace(",", "\\,")


def main():
    map_ = Path(sys.argv[1]).resolve()
    uit = map_ / (sys.argv[sys.argv.index("--uit") + 1] if "--uit" in sys.argv else "proef.mp4")
    plan = json.loads((map_ / "plan.json").read_text(encoding="utf-8"))
    blokken = {b["blok"]: b for b in json.loads((map_ / "stem" / "blokken.json").read_text(encoding="utf-8"))}
    bron = map_ / "bron" / "bron.mp4"
    credit = (map_ / "bronvermelding.txt").read_text(encoding="utf-8").split(" – ")[0].strip()
    tmp = map_ / "build"
    tmp.mkdir(exist_ok=True)
    global CWD
    CWD = tmp
    (tmp / FONT).write_bytes(Path("C:/Windows/Fonts/arial.ttf").read_bytes())
    delen = []
    for n, st in enumerate(plan, 1):
        blok = blokken.get(st.get("blok"))
        stem_duur = blok["duur"] + 0.6 if blok else None
        stukken = st["bron"]
        bron_duur = sum(b - a for a, b in stukken)
        doel = stem_duur or bron_duur
        tempo = min(1.35, max(1.0, doel / bron_duur))            # >1 = langzamer afspelen
        # 1) bronstukken knippen en aan elkaar
        off = max(0, min(a for a, _ in stukken) - 1)            # snel zoeken: alleen vanaf het eerste stuk inlezen
        sel = "+".join(f"between(t,{a - off},{b - off})" for a, b in stukken)
        v = f"select='{sel}',setpts=N/FRAME_RATE/TB"
        a_ = f"aselect='{sel}',asetpts=N/SR/TB"
        soort = st.get("soort", "vol")
        if soort == "bodycam":   # 4:3-beeld uit de zwarte randen halen, wazige vulling erachter
            v += (f",crop=1440:1080:240:0,split[a][b];[a]scale={W}:-2,crop={W}:{H},boxblur=30:2,eq=brightness=-0.15[bg];"
                  f"[b]scale=-2:{H}[fg];[bg][fg]overlay=(W-w)/2:0")
        elif soort == "kaart":   # ondertitels onderin de bron wegsnijden
            v += f",crop=iw*0.86:ih*0.86:(iw-ow)/2:0,scale={W}:{H}"
        else:
            v += f",scale={W}:{H}"
        v += f",fps={FPS},setpts={tempo:.4f}*PTS,tpad=stop_mode=clone:stop_duration=30,trim=0:{doel:.3f},setpts=PTS-STARTPTS"
        tekst = [f"drawtext=fontfile={FONT}:text='{esc(credit)}':x=w-tw-28:y=h-th-24:fontsize=24:"
                 "fontcolor=white@0.75:box=1:boxcolor=black@0.35:boxborderw=8"]
        if st.get("tekst"):
            tekst.append(f"drawtext=fontfile={FONT}:text='{esc(st['tekst'])}':x=60:y=h-150:fontsize=46:fontcolor=white:"
                         "box=1:boxcolor=black@0.55:boxborderw=18:enable='between(t,0.5,7)'")
        v += "," + ",".join(tekst) + ",format=yuv420p[v]"
        # Eigenaar 17 nov: "het geluid van de originele video wel behouden, alleen het commentaar of de verteller door de stem".
        # geluid: "origineel" (STANDAARD: echt bodycam-geluid; zakt vanzelf weg zodra onze stem praat, komt tussen de zinnen
        #          weer omhoog) / "uit" (STANDAARD bij "kaart": daar praat de korps-verteller -> vervangen door onze stem;
        #          ook voor tekstschermen met verteller) / "onder" (vast -18 dB).
        geluid = st.get("geluid") or ("uit" if soort == "kaart" else "origineel")
        bron_vol = {"origineel": 1.0, "onder": 0.126, "uit": 0.0}[geluid]
        a_ += (f",atempo={1 / tempo:.4f},volume={bron_vol},aformat=sample_rates=48000:channel_layouts=stereo,"
               f"apad,atrim=0:{doel:.3f}[ba]")
        deel = tmp / f"deel{n:02d}.mp4"
        if blok:
            # ducking: het bron-geluid gaat ± 20 dB omlaag zolang onze stem klinkt (sidechain), zachte overgangen
            fc = (f"[0:v]{v};[0:a]{a_};[1:a]aformat=sample_rates=48000:channel_layouts=stereo,adelay=300|300,"
                  f"apad,atrim=0:{doel:.3f},asplit[s][sc];"
                  f"[ba][sc]sidechaincompress=threshold=0.01:ratio=20:attack=30:release=600:makeup=1[bd];"
                  f"[bd][s]amix=inputs=2:normalize=0:duration=first[a]")
            ff("-ss", off, "-i", bron, "-i", map_ / "stem" / blok["bestand"], "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-r", FPS, deel)
        else:
            fc = f"[0:v]{v};[0:a]{a_.replace('[ba]', '[a]')}"
            ff("-ss", off, "-i", bron, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
               "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-r", FPS, deel)
        delen.append(deel)
        print(f"stuk {n}: {doel:5.1f} s ({soort}, tempo {tempo:.2f}) {'stem blok ' + str(st['blok']) if blok else 'origineel geluid'}",
              flush=True)
    lijst = tmp / "lijst.txt"
    lijst.write_text("".join(f"file '{d.name}'\n" for d in delen), encoding="utf-8")
    samen = tmp / "samen.mp4"
    ff("-f", "concat", "-safe", "0", "-i", lijst, "-c", "copy", samen)
    # eindvolume -14 LUFS, korte fade in/uit
    t = duur(samen)
    ff("-i", samen, "-af", f"loudnorm=I=-14:TP=-1:LRA=11,afade=t=in:d=0.4,afade=t=out:st={t - 1.2:.2f}:d=1.2",
       "-vf", f"fade=t=in:d=0.5,fade=t=out:st={t - 1.2:.2f}:d=1.2", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
       "-c:a", "aac", "-b:a", "192k", uit)
    print(f"klaar: {uit} ({duur(uit):.0f} s)")


if __name__ == "__main__":
    main()
