"""What if the asteroid that killed the dinosaurs had missed? Lange video, 1920x1080 (16:9), ca. 3 min.

Lux-stem (voice.mp3, start op LEAD s), één beeld per zin, tijdstempels als lower-third, een klein
label linksboven dat feiten ("REAL HISTORY") en speculatie ("ALTERNATE TIMELINE") scheidt,
witte flits + inslag bij "Then.", drone + lage klap bij elke tijdstempel.

Gebruik (vanuit deze map): python3 make.py <tmpmap>   -> <tmpmap>/what-if-asteroid-missed.mp4
"""
import csv, subprocess, sys
S=sys.argv[1]; FPS=30; A="afbeeldingen"; LEAD=0.8; W,H=1920,1080
rows=[r for r in csv.reader(open("voice-times.tsv"),delimiter="\t") if not r[0].startswith("#")]
END=float(rows[-1][2])+2.5
start=lambda n: float(rows[n-1][1])          # n = regelnummer in voice-times.tsv

# Shots: elk beeld begint op de eerste regel waar het in de kolom 'image' staat (eerste beeld op 0 s).
SH=[(int(r[0]),r[3]) for r in rows if r[3]]
FLASH="fade=t=in:st=0:d=0.8:color=white"
IMPACT=14                                     # regel "Then." -> flits + inslag
MOVE={"S01":"out","S08":"in","S11":"in","S12":"shake","S13":"punch","S21":"left","S22":"right","S38":"out"}
CYCLE=["in","left","out","right"]
# (label, groot getal) per regel in voice-times.tsv
STAMPS={3:("LATE CRETACEOUS","66 MILLION YEARS AGO"),4:("AGE OF DINOSAURS","160+ MILLION YEARS"),
 11:("ASTEROID DIAMETER","~10 KM"),12:("IMPACT SPEED","~20 KM/S"),13:("IMPACT SITE · CHICXULUB","21.4° N  89.5° W"),
 15:("ENERGY · HIROSHIMA BOMBS",">1 BILLION ×"),16:("CRATER WIDTH","~180 KM"),20:("SPECIES LOST","~75%"),
 23:("SURFACE THAT COULD DO THIS","~13% OF EARTH"),33:("HOMO SAPIENS","~300,000 YEARS"),
 35:("THE DINOSAUROID","1982"),46:("BIRD SPECIES TODAY","10,000+")}
RED={20}
# label linksboven: (vanaf regel, tot regel (exclusief), tekst)
CHIPS=[(3,25,"REAL HISTORY"),(25,43,"ALTERNATE TIMELINE  ·  SPECULATION"),(43,49,"REAL SCIENCE")]

starts=[0.0]+[start(r) for r,_ in SH[1:]]

# --- beeld ---
segs=[]
for i,(r,img) in enumerate(SH):
    d=(starts[i+1] if i+1<len(SH) else END)-starts[i]; n=round(d*FPS)
    mv=MOVE.get(img,CYCLE[i%4])
    cx,cy="iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"
    z={"in":f"1+0.12*on/{n}","out":f"1.12-0.12*on/{n}","left":"1.12","right":"1.12",
       "shake":f"1.12+0.05*on/{n}","punch":f"1.25-0.18*min(on/8,1)"}[mv]
    if mv=="left": cx=f"(iw-iw/zoom)*(1-on/{n})"
    if mv=="right": cx=f"(iw-iw/zoom)*on/{n}"
    if mv=="shake": cx+="+14*sin(on*2.1)"; cy+="+14*cos(on*1.7)"
    vf=f"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,setsar=1,zoompan=z='{z}':x='{cx}':y='{cy}':d={n}:s={W}x{H}:fps={FPS}"
    if r==IMPACT: vf+=","+FLASH
    vf+=",eq=contrast=1.08:saturation=0.75,colorbalance=bs=0.06:bh=-0.03,noise=alls=4:allf=t,vignette=PI/4.5"
    out=f"{S}/seg{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"{A}/{img}.jpg","-vf",vf,"-frames:v",str(n),
      "-c:v","libx264","-preset","fast","-pix_fmt","yuv420p","-crf","17",out],check=True)
    segs.append(out); print(img, mv, f"{d:.1f}s", flush=True)
open(f"{S}/list.txt","w").write("".join(f"file '{s}'\n" for s in segs))

# --- tekst (ASS) ---
ts=lambda s: f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
X, Y = 110, 630          # linkerbovenhoek van het lower-third-blok
ass=["[Script Info]",f"PlayResX: {W}",f"PlayResY: {H}","WrapStyle: 0","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,Inter SemiBold,52,&H00F2F2F2,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0.5,0,1,3.2,2.2,2,300,300,64,1",
"Style: Label,Inter SemiBold,30,&H0080C8F2,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,8,0,1,0,2,7,0,0,0,1",
"Style: Big,Inter Display Light,104,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,3,0,1,0,3,7,0,0,0,1",
"Style: Chip,Inter SemiBold,24,&H00D8D8D8,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,6,0,1,0,1.5,7,0,0,0,1",
"Style: Bar,Inter,10,&H0080C8F2,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def ev(layer,st,en,style,text): ass.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")
def stamp(st, label, big, hold=2.8, color=None):
    """Kort lower-third: lijntje schuift in, label + groot getal glijden mee, alles fadet weg."""
    en=st+hold; c=f"\\c{color}" if color else ""
    ev(2,st,en,"Bar",f"{{\\pos({X},{Y})\\fad(0,350)\\clip({X},{Y},{X},{Y+4})\\t(0,450,\\clip({X},{Y},{X+300},{Y+4}))\\p1}}m 0 0 l 300 0 300 4 0 4{{\\p0}}")
    ev(2,st+0.12,en,"Label",f"{{\\move({X-30},{Y+20},{X},{Y+20},0,400)\\fad(250,350)}}{label}")
    ev(2,st+0.22,en,"Big",f"{{\\move({X-40},{Y+58},{X},{Y+58},0,450)\\fad(300,350){c}}}{big}")
for i,r in enumerate(rows):
    st=float(r[1]); en=min(float(rows[i+1][1]) if i+1<len(rows) else END-0.8, float(r[2])+0.9)
    ev(0,st,en,"Sub",f"{{\\fad(150,150)}}{r[4]}")
for n,(label,big) in STAMPS.items():
    stamp(start(n), label, big, color="&H4040E8&" if n in RED else None)
for a,b,text in CHIPS:
    st=start(a); en=start(b)-0.3
    ev(1,st,en,"Bar",f"{{\\pos(72,62)\\fad(400,400)\\p1}}m 0 0 l 10 0 10 10 0 10{{\\p0}}")
    ev(1,st,en,"Chip",f"{{\\pos(94,52)\\fad(400,400)}}{text}")
open(f"{S}/subs.ass","w").write("\n".join(ass)+"\n")

# --- geluid + eindmix ---
hits=[start(n) for n in STAMPS]
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","sine=f=48:d=2.2","-f","lavfi","-i","anoisesrc=color=brown:d=2.2:amplitude=0.8",
  "-filter_complex","[0]volume=1.2[s];[1]lowpass=f=180,volume=0.8[n];[s][n]amix=2:normalize=0,afade=t=out:st=0.05:d=2.1:curve=exp,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/boom.wav"],check=True)
# inslag: korte knal + lange lage rommel (langer en dieper dan de donder in de lightning-video)
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anoisesrc=color=white:d=0.3:amplitude=1","-f","lavfi","-i","anoisesrc=color=brown:d=7:amplitude=1",
  "-f","lavfi","-i","sine=f=36:d=7",
  "-filter_complex","[0]highpass=f=600,afade=t=out:d=0.3,volume=1.2[c];[1]lowpass=f=120,volume=2.4,afade=t=in:d=0.1,afade=t=out:st=0.5:d=6.5:curve=exp,tremolo=f=5:d=0.4[r];"
  "[2]volume=0.9,afade=t=out:st=0.3:d=6.7:curve=exp[s];[c][r][s]amix=3:normalize=0,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/impact.wav"],check=True)
ins=["-i",f"{S}/impact.wav"]; ms=int(start(IMPACT)*1000)
fc=f"[4:a]adelay={ms}|{ms},volume=1.0[im];"; L="[im]"
for k,h in enumerate(hits):
    ins+=["-i",f"{S}/boom.wav"]; ms=int(h*1000); fc+=f"[{k+5}:a]adelay={ms}|{ms},volume=0.55[h{k}];"; L+=f"[h{k}]"
fc+=(f"[1:a]aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={int(LEAD*1000)}|{int(LEAD*1000)}[vo];"
     "[2:a]volume=0.2,tremolo=f=0.12:d=0.6[s];[3:a]lowpass=f=240,volume=0.28[n];"
     f"[s][n]amix=inputs=2:normalize=0,afade=t=in:d=3,afade=t=out:st={END-4}:d=4,pan=stereo|c0=c0|c1=c0[bg];"
     f"[vo][bg]{L}amix=inputs={len(hits)+3}:duration=longest:normalize=0,alimiter=limit=0.89:level=0[a];"
     f"[0:v]ass={S}/subs.ass,fade=t=in:st=0:d=0.8,fade=t=out:st={END-1.8}:d=1.8[v]")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{S}/list.txt","-i","voice.mp3",
  "-f","lavfi","-t",str(END),"-i","sine=f=55:sample_rate=44100","-f","lavfi","-t",str(END),"-i","anoisesrc=color=brown:sample_rate=44100:amplitude=0.5",
  *ins,"-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(END),"-c:v","libx264","-preset","slow","-b:v","8M","-maxrate","10M","-bufsize","16M",
  "-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-b:a","192k","-movflags","+faststart",f"{S}/what-if-asteroid-missed.mp4"],check=True)
print(f"klaar: {END:.1f}s")
