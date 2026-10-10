"""Documentaireversie met Lux-stem (voice-lux.mp3, start op LEAD s) en strakke tijdstempels.

Gebruik: python3 make-doc-lux.py <tmpdir>   -> <tmpdir>/what-if-humans-vanished-lux.mp4
"""
import csv, subprocess, sys
S=sys.argv[1]; FPS=30; A="../afbeeldingen"; LEAD=0.8
rows=[r for r in csv.reader(open("voice-times-lux.tsv"),delimiter="\t") if not r[0].startswith("#")]
END=float(rows[-1][2])+2.5
# (spreker-regel waar de shot begint, afbeelding, beweging, extra filter, tijdstempel)
SH=[(1,"109","in","",None),(2,"101","out","",None),(3,"001","in","",None),
 (4,"110","in","","HOUR 1"),(6,"002","out","eq=brightness='-0.4*min(max((t-1.3)/0.8,0),1)'",None),
 (7,"104","in","","HOUR 36"),(9,"103","in","",None),(10,"105","up","","YEAR 20"),(12,"106","in","",None),
 (13,"107","up","","YEAR 300"),(15,"005","shake","",None),(16,"006","out","","YEAR 500"),
 (18,"108","in","",None),(19,"007","punch","",None),(21,"111","in","",None)]
starts=[0.0]+[float(rows[r-1][1]) for r,*_ in SH[1:]]

# --- beeld ---
segs=[]
for i,(r,img,mv,extra,stamp) in enumerate(SH):
    d=(starts[i+1] if i+1<len(SH) else END)-starts[i]; n=round(d*FPS)
    cx,cy="iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"
    z={"in":f"1+0.15*on/{n}","out":f"1.15-0.15*on/{n}","up":"1.15","shake":f"1.12+0.05*on/{n}","punch":f"1.25-0.2*min(on/8,1)"}[mv]
    if mv=="up": cy=f"(ih-ih/zoom)*(1-on/{n})"
    if mv=="shake": cx+="+12*sin(on*2.1)"; cy+="+12*cos(on*1.7)"
    vf=f"scale=2160:3840,zoompan=z='{z}':x='{cx}':y='{cy}':d={n}:s=1080x1920:fps={FPS}"
    if extra: vf+=","+extra
    vf+=",eq=contrast=1.08:saturation=0.75,colorbalance=bs=0.06:bh=-0.03,noise=alls=4:allf=t,vignette=PI/4.5"
    out=f"{S}/luxseg{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"{A}/{img}.jpg","-vf",vf,"-frames:v",str(n),
      "-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out],check=True)
    segs.append(out)
open(f"{S}/luxlist.txt","w").write("".join(f"file '{s}'\n" for s in segs))

# --- tekst (ASS) ---
ts=lambda s: f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
GOLD="&H0080C8F2&"; X, Y = 84, 300          # linkerbovenhoek van het tijdstempel-blok
ass=["[Script Info]","PlayResX: 1080","PlayResY: 1920","WrapStyle: 0","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,Inter SemiBold,56,&H00F2F2F2,&H00FFFFFF,&H00000000,&H90000000,0,0,0,0,100,100,0.5,0,1,3.5,2.5,2,110,110,430,1",
"Style: Label,Inter SemiBold,32,&H0080C8F2,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,9,0,1,0,2,7,0,0,0,1",
"Style: Big,Inter Display Light,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,4,0,1,0,3,7,0,0,0,1",
"Style: Bar,Inter,10,&H0080C8F2,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def ev(layer,st,en,style,text): ass.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")
def stamp(st, label, big, hold=2.6, color=None):
    """Kort lower-third: lijntje schuift in, label + groot tijdstip glijden mee, alles fadet weg."""
    en=st+hold; c=f"\\c{color}" if color else ""
    ev(2,st,en,"Bar",f"{{\\pos({X},{Y})\\fad(0,350)\\clip({X},{Y},{X},{Y+4})\\t(0,450,\\clip({X},{Y},{X+260},{Y+4}))\\p1}}m 0 0 l 260 0 260 4 0 4{{\\p0}}")
    ev(2,st+0.12,en,"Label",f"{{\\move({X-30},{Y+22},{X},{Y+22},0,400)\\fad(250,350)}}{label}")
    ev(2,st+0.22,en,"Big",f"{{\\move({X-40},{Y+62},{X},{Y+62},0,450)\\fad(300,350){c}}}{big}")
for i,r in enumerate(rows):
    st=float(r[1]); en=min(float(rows[i+1][1]) if i+1<len(rows) else END-0.8, float(r[2])+0.9)
    ev(0,st,en,"Sub",f"{{\\fad(150,150)}}{r[4]}")
for i,s in enumerate(SH):
    if s[4]: stamp(starts[i], "AFTER HUMANS", s[4])
stamp(starts[1], "WORLD POPULATION", "8,000,000,000", hold=starts[2]-starts[1]-0.05)
stamp(starts[2], "WORLD POPULATION", "0", color="&H4040E8&")
open("subs-lux.ass","w").write("\n".join(ass)+"\n")

# --- geluid + eindmix ---
hits=[starts[i] for i,s in enumerate(SH) if s[4]]+[starts[2],starts[13]]
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","sine=f=48:d=2.2","-f","lavfi","-i","anoisesrc=color=brown:d=2.2:amplitude=0.8",
  "-filter_complex","[0]volume=1.2[s];[1]lowpass=f=180,volume=0.8[n];[s][n]amix=2:normalize=0,afade=t=out:st=0.05:d=2.1:curve=exp,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/boom.wav"],check=True)
ins=[]; fc=""; L=""
for k,h in enumerate(hits):
    ins+=["-i",f"{S}/boom.wav"]; ms=int(h*1000); fc+=f"[{k+4}:a]adelay={ms}|{ms},volume=0.75[h{k}];"; L+=f"[h{k}]"
fc+=(f"[1:a]aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={int(LEAD*1000)}|{int(LEAD*1000)}[vo];"
     "[2:a]volume=0.2,tremolo=f=0.12:d=0.6[s];[3:a]lowpass=f=240,volume=0.28[n];"
     f"[s][n]amix=inputs=2:normalize=0,afade=t=in:d=3,afade=t=out:st={END-4}:d=4,pan=stereo|c0=c0|c1=c0[bg];"
     f"[vo][bg]{L}amix=inputs={len(hits)+2}:duration=longest:normalize=0,alimiter=limit=0.95[a];"
     f"[0:v]ass=subs-lux.ass,fade=t=in:st=0:d=0.8,fade=t=out:st={END-1.8}:d=1.8[v]")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{S}/luxlist.txt","-i","voice-lux.mp3",
  "-f","lavfi","-t",str(END),"-i","sine=f=55:sample_rate=44100","-f","lavfi","-t",str(END),"-i","anoisesrc=color=brown:sample_rate=44100:amplitude=0.5",
  *ins,"-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(END),"-c:v","libx264","-preset","slow","-b:v","2.9M","-maxrate","3.5M","-bufsize","6M",
  "-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-movflags","+faststart",f"{S}/what-if-humans-vanished-lux.mp4"],check=True)
print(f"klaar: {END:.1f}s")
