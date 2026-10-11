"""What if the sky displayed a countdown? Lange video, 1920x1080 (16:9), ca. 3 min.

Atlas-stem (voice.mp3, start op LEAD s; snelle stijl van de shorts: tempo 1.0, pauzes 300/600 ms + 200 ms),
harde opening zonder fade-in en zonder titeltekst, één beeld per zin, tijdstempels als lower-third,
een klein label linksboven dat feiten ("REAL SCIENCE"/"REAL HISTORY") en speculatie ("ALTERNATE TIMELINE")
scheidt, en gloeiende cijfers in de lucht die echt aftellen (ASS, elk cijfer op een vaste plek, dus geen
verspringen). Laatste tien seconden groot in beeld met tikken, rode flits + dreun bij "Zero.",
lage klap bij elke tijdstempel, eigen score (music.mp3 uit make_music.py) die onder de stem zachter gaat.

Gebruik (vanuit deze map): python3 make.py <tmpmap>   -> <tmpmap>/what-if-sky-countdown.mp4
"""
import csv, os, subprocess, sys
S=os.path.abspath(sys.argv[1]); os.makedirs(S,exist_ok=True)
os.chdir(os.path.dirname(os.path.abspath(__file__)))
FPS=30; A="afbeeldingen"; LEAD=0.8; W,H=1920,1080
rows=[r for r in csv.reader(open("voice-times.tsv"),delimiter="\t") if not r[0].startswith("#")]
END=float(rows[-1][2])+2.5
start=lambda n: float(rows[n-1][1])          # n = regelnummer in voice-times.tsv

# Shots: elk beeld begint op de eerste regel waar het in de kolom 'image' staat (eerste beeld op 0 s).
SH=[(int(r[0]),r[3]) for r in rows if r[3]]
ZERO=63                                       # regel "Zero." -> rode flits + dreun
FLASH="fade=t=in:st=0:d=0.9:color=0xff3020"
MOVE={"S01":"out","S08":"in","S09":"in","S35":"in","S36":"in","S37":"punch","S39":"out","S43":"out"}
CYCLE=["in","left","out","right"]
# (label, groot getal) per regel in voice-times.tsv
STAMPS={6:("TIME REMAINING","365 DAYS"),7:("TOKYO · LOCAL TIME","9:00 PM"),9:("NEW YORK · LOCAL TIME","8:00 AM"),
 14:("VISIBLE AT ONCE","≤ HALF OF EARTH"),15:("FULL MOON · APPARENT SIZE","~0.5°"),17:("MOON DIAMETER","3,474 KM"),
 19:("TIMELINE","DAY 2 OF 365"),28:("Y2K PREPARATIONS · ESTIMATE","~$300 BILLION"),35:("TIMELINE","DAY 100 OF 365"),
 42:("DOOMSDAY CLOCK · CREATED","1947"),43:("DOOMSDAY CLOCK · 1947","7 MINUTES TO MIDNIGHT"),
 44:("DOOMSDAY CLOCK · 2026","85 SECONDS TO MIDNIGHT"),47:("TIME REMAINING","30 DAYS"),
 56:("TIME REMAINING","24 HOURS"),60:("TIME REMAINING","1 HOUR"),74:("AN 80-YEAR LIFE","≈ 4,170 WEEKS")}
RED={44,60}
# label linksboven: (vanaf regel, tot regel (exclusief, None = einde), tekst)
SPEC="ALTERNATE TIMELINE  ·  SPECULATION"
CHIPS=[(1,12,SPEC),(12,19,"REAL SCIENCE"),(19,27,SPEC),(27,29,"REAL HISTORY"),(29,39,SPEC),(39,41,"REAL SCIENCE"),
 (41,46,"REAL HISTORY"),(46,54,SPEC),(54,56,"REAL HISTORY"),(56,71,SPEC),(71,None,"REAL MATH")]

# Aftellen in de lucht: (van s, tot s, stand bij begin in seconden, tempo); tot = None -> tot volgende shot.
D=86400
COUNT=[(0.0,start(12),365*D,1),(start(19),start(25),363*D+14*3600+27*60+12,1),(start(35),start(37),265*D+9*3600+12*60+40,1),
 (start(47),start(49),30*D-1,1),(start(56),start(60),24*3600-2,1),(start(60),start(62),3599,1)]
T10,T0=start(62)+0.2,start(ZERO)               # laatste tien seconden: 10 -> 0 precies op "Zero."

starts=[0.0]+[start(r) for r,_ in SH[1:]]

# --- beeld ---
segs=[]
for i,(r,img) in enumerate(SH):
    d=(starts[i+1] if i+1<len(SH) else END)-starts[i]; n=round(d*FPS)
    mv=MOVE.get(img,CYCLE[i%4])
    cx,cy="iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"
    z={"in":f"1+0.12*on/{n}","out":f"1.12-0.12*on/{n}","left":"1.12","right":"1.12",
       "punch":f"1.25-0.18*min(on/8,1)"}[mv]
    if mv=="left": cx=f"(iw-iw/zoom)*(1-on/{n})"
    if mv=="right": cx=f"(iw-iw/zoom)*on/{n}"
    vf=f"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,setsar=1,zoompan=z='{z}':x='{cx}':y='{cy}':d={n}:s={W}x{H}:fps={FPS}"
    if r==ZERO: vf+=","+FLASH
    vf+=",eq=contrast=1.08:saturation=0.78,colorbalance=bs=0.06:bh=-0.03,noise=alls=4:allf=t,vignette=PI/4.5"
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
# gloeiende cijfers in de lucht: kern (bijna wit-rood) + rode gloed eronder
"Style: Num,Inter Display Light,150,&H00C8D8FF,&H00FFFFFF,&H002A2AFF,&H00000000,0,0,0,0,100,100,0,0,1,1.5,0,8,0,0,0,1",
"Style: Glow,Inter Display Light,150,&H602020FF,&H00FFFFFF,&H602020FF,&H00000000,0,0,0,0,100,100,0,0,1,9,0,8,0,0,0,1",
"Style: Unit,Inter SemiBold,22,&H00A0B8FF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,10,0,1,0,1.5,8,0,0,0,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
def ev(layer,st,en,style,text): ass.append(f"Dialogue: {layer},{ts(st)},{ts(en)},{style},,0,0,0,,{text}")
def stamp(st, label, big, hold=2.8, color=None):
    """Kort lower-third: lijntje schuift in, label + groot getal glijden mee, alles fadet weg."""
    en=st+hold; c=f"\\c{color}" if color else ""
    ev(2,st,en,"Bar",f"{{\\pos({X},{Y})\\fad(0,350)\\clip({X},{Y},{X},{Y+4})\\t(0,450,\\clip({X},{Y},{X+300},{Y+4}))\\p1}}m 0 0 l 300 0 300 4 0 4{{\\p0}}")
    ev(2,st+0.12,en,"Label",f"{{\\move({X-30},{Y+20},{X},{Y+20},0,400)\\fad(250,350)}}{label}")
    ev(2,st+0.22,en,"Big",f"{{\\move({X-40},{Y+58},{X},{Y+58},0,450)\\fad(300,350){c}}}{big}")

def fmt(v):
    v=max(0,int(v)); return f"{v//D:03d}:{v%D//3600:02d}:{v%3600//60:02d}:{v%60:02d}"
def sky_count(t0, t1, v0, rate, scale=100, y=96, fin=0.6, fout=0.5):
    """Aftellende cijfers bovenin beeld; elk teken op een vaste plek (Inter heeft geen vaste cijferbreedte)."""
    k=scale/100; cw,colw=92*k,40*k
    widths=[colw if c==":" else cw for c in "000:00:00:00"]; x=W/2-sum(widths)/2; xs=[]
    for w_ in widths: xs.append(x+w_/2); x+=w_
    ticks=[t0]; t=t0
    while True:
        t=t0+len(ticks)/rate
        if t>=t1: break
        ticks.append(t)
    vals=[fmt(v0-j) for j in range(len(ticks))]
    fade=lambda a,b: f"\\fad({int(fin*1000) if a==t0 else 0},{int(fout*1000) if b>=t1-1e-6 else 0})"
    for ci in range(12):
        j=0
        while j<len(ticks):
            ch=vals[j][ci]; k2=j
            while k2+1<len(ticks) and vals[k2+1][ci]==ch: k2+=1
            a,b=ticks[j],(ticks[k2+1] if k2+1<len(ticks) else t1)
            tag=f"{{\\an8\\pos({xs[ci]:.1f},{y})\\fscx{scale}\\fscy{scale}{fade(a,b)}"
            ev(3,a,b,"Glow",tag+"\\blur18}"+ch)
            ev(4,a,b,"Num",tag+"\\blur1.2}"+ch)
            j=k2+1
    uy=y+int(168*k)
    for txt,ci in (("DAYS",1),("HRS",4.5),("MIN",7.5),("SEC",10.5)):
        cx=(xs[int(ci)]+xs[int(ci)+1])/2 if ci%1 else xs[int(ci)]
        ev(4,t0,t1,"Unit",f"{{\\an8\\pos({cx:.1f},{uy})\\fscx{scale}\\fscy{scale}\\fad({int(fin*1000)},{int(fout*1000)})}}{txt}")

for i,r in enumerate(rows):
    st=float(r[1]); en=min(float(rows[i+1][1]) if i+1<len(rows) else END-0.8, float(r[2])+0.9)
    ev(0,st,en,"Sub",f"{{\\fad(150,150)}}{r[4]}")
for n,(label,big) in STAMPS.items():
    stamp(start(n), label, big, color="&H4040E8&" if n in RED else None)
for a,b,text in CHIPS:
    st=start(a); en=(start(b) if b else END)-0.3
    ev(1,st,en,"Bar",f"{{\\pos(72,62)\\fad(400,400)\\p1}}m 0 0 l 10 0 10 10 0 10{{\\p0}}")
    ev(1,st,en,"Chip",f"{{\\pos(94,52)\\fad(400,400)}}{text}")
for t0,t1,v0,rate in COUNT:
    sky_count(t0,t1,v0,rate,fin=0 if t0==0 else 0.6)
# laatste tien seconden: groter en lager in beeld, 10 -> 0 precies op "Zero."; daarna nullen tot de lucht leeg is
sky_count(T10,T0,10,10/(T0-T10),scale=140,y=150,fin=0.3,fout=0)
sky_count(T0,start(68)+2.2,0,1e-9,scale=140,y=150,fin=0,fout=2.0)
open(f"{S}/subs.ass","w").write("\n".join(ass)+"\n")

# --- geluid + eindmix ---
hits=[start(n) for n in STAMPS]
ticks=[T10+j*(T0-T10)/10 for j in range(10)]
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","sine=f=48:d=2.2","-f","lavfi","-i","anoisesrc=color=brown:d=2.2:amplitude=0.8",
  "-filter_complex","[0]volume=1.2[s];[1]lowpass=f=180,volume=0.8[n];[s][n]amix=2:normalize=0,afade=t=out:st=0.05:d=2.1:curve=exp,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/boom.wav"],check=True)
# tik van de klok: korte hoge klik + lage hartslag-dreun
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anoisesrc=color=white:d=0.05:amplitude=1","-f","lavfi","-i","sine=f=55:d=0.5",
  "-filter_complex","[0]highpass=f=2500,afade=t=out:d=0.05,volume=0.5[c];[1]afade=t=out:st=0.02:d=0.48:curve=exp,volume=1.1[b];[c][b]amix=2:normalize=0,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/tick.wav"],check=True)
# nul: korte knal + lange lage rommel
subprocess.run(["ffmpeg","-v","error","-y","-f","lavfi","-i","anoisesrc=color=white:d=0.3:amplitude=1","-f","lavfi","-i","anoisesrc=color=brown:d=6:amplitude=1",
  "-f","lavfi","-i","sine=f=36:d=6",
  "-filter_complex","[0]highpass=f=600,afade=t=out:d=0.3,volume=0.5[c];[1]lowpass=f=120,volume=2.2,afade=t=in:d=0.1,afade=t=out:st=0.5:d=5.5:curve=exp,tremolo=f=5:d=0.4[r];"
  "[2]volume=0.9,afade=t=out:st=0.3:d=5.7:curve=exp[s];[c][r][s]amix=3:normalize=0,aresample=44100,pan=stereo|c0=c0|c1=c0",
  f"{S}/impact.wav"],check=True)
ins=["-i",f"{S}/impact.wav"]; ms=int(T0*1000)
fc=f"[4:a]adelay={ms}|{ms},volume=1.0[im];"; L="[im]"; k=5
for h in hits:
    ins+=["-i",f"{S}/boom.wav"]; ms=int(h*1000); fc+=f"[{k}:a]adelay={ms}|{ms},volume=0.55[x{k}];"; L+=f"[x{k}]"; k+=1
for j,h in enumerate(ticks):
    ins+=["-i",f"{S}/tick.wav"]; ms=int(h*1000); fc+=f"[{k}:a]adelay={ms}|{ms},volume={0.45+0.05*j:.2f}[x{k}];"; L+=f"[x{k}]"; k+=1
fc+=(f"[1:a]aresample=44100,pan=stereo|c0=c0|c1=c0,adelay={int(LEAD*1000)}|{int(LEAD*1000)}[vo];"
     # muziek (make_music.py) gaat zachter zodra de stem klinkt; heel zacht wat lage ruis als 'lucht'
     "[vo]asplit[vo][sc];[2:a]aresample=44100,highpass=f=40,volume=0.5[mu];"
     "[mu][sc]sidechaincompress=threshold=0.02:ratio=5:attack=60:release=700:makeup=1[md];[3:a]lowpass=f=240,volume=0.12,pan=stereo|c0=c0|c1=c0[n];"
     f"[md][n]amix=inputs=2:normalize=0,afade=t=in:d=0.05,afade=t=out:st={END-4}:d=4[bg];"
     f"[vo][bg]{L}amix=inputs={k-2}:duration=longest:normalize=0,alimiter=limit=0.84:level=0[a];"
     f"[0:v]ass={S}/subs.ass,fade=t=out:st={END-1.8}:d=1.8[v]")
subprocess.run(["ffmpeg","-v","error","-y","-f","concat","-safe","0","-i",f"{S}/list.txt","-i","voice.mp3",
  "-i","music.mp3","-f","lavfi","-t",str(END),"-i","anoisesrc=color=brown:sample_rate=44100:amplitude=0.5",
  *ins,"-filter_complex",fc,"-map","[v]","-map","[a]","-t",str(END),"-c:v","libx264","-preset","slow","-b:v","8M","-maxrate","10M","-bufsize","16M",
  "-pix_fmt","yuv420p","-r",str(FPS),"-c:a","aac","-b:a","192k","-movflags","+faststart",f"{S}/what-if-sky-countdown.mp4"],check=True)
print(f"klaar: {END:.1f}s")
