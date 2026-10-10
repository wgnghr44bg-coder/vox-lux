import subprocess, csv, sys
S=sys.argv[1]
starts=[0,3.2,6.8,11.1,16.7,21.8,26.6]; END=34.4; FPS=30
# per image: alternate zoom in / zoom out, slight drift
segs=[]
for i,st in enumerate(starts):
    d=(starts[i+1] if i+1<len(starts) else END)-st
    n=round(d*FPS)
    z = f"1+0.12*on/{n}" if i%2==0 else f"1.12-0.12*on/{n}"
    out=f"{S}/seg{i}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"afbeeldingen/{i+1:03d}.jpg","-vf",
      f"scale=2160:3840,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps={FPS},eq=contrast=1.06:saturation=0.9,vignette=PI/5",
      "-frames:v",str(n),"-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out],check=True)
    segs.append(out)
open(f"{S}/list.txt","w").write("".join(f"file '{s}'\n" for s in segs))
# subtitles (ASS)
def t(x):
    h,m,s=x.split(":"); s=float(s)+int(m)*60+int(h)*3600
    return f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
rows=[r for r in csv.reader(open("voice-times.tsv"),delimiter="\t") if not r[0].startswith("#")]
ass=["[Script Info]","PlayResX: 1080","PlayResY: 1920","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,DejaVu Sans,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,6,3,2,90,90,560,1",
"Style: Big,DejaVu Sans,110,&H0000D7FF,&H0000D7FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,8,4,5,60,60,0,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,r in enumerate(rows):
    end = rows[i+1][1] if i+1<len(rows) else "0:00:34.4"
    style="Big" if r[4].strip()=="Our plastic." else "Sub"
    txt=r[4].replace("…","...").upper() if style=="Big" else r[4]
    ass.append(f"Dialogue: 0,{t(r[1])},{t(end)},{style},,0,0,0,{{\\fad(150,100)}},{txt}".replace(",{\\fad",",,{\\fad").replace(",,,{\\fad",",,{\\fad"))
open(f"{S}/subs.ass","w").write("\n".join(ass)+"\n")
