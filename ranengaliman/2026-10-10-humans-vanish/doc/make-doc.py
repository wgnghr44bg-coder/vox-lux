"""Documentaireversie: stem (ElevenLabs Daniel), tijdstempels, tijdsprong-klappen."""
import csv, subprocess, sys
S=sys.argv[1]; FPS=30; A="../afbeeldingen"
LEAD, GAP_AT, GAP = 0.5, 0.45, 0.7          # stilte vooraf + extra pauze na "Earth."
T=lambda x: x+LEAD if x<GAP_AT else x+LEAD+GAP
rows=[r for r in csv.reader(open("voice-times.tsv"),delimiter="\t") if not r[0].startswith("#")]
sec=lambda s: sum(float(p)*m for p,m in zip(s.split(":"),(3600,60,1)))
END=T(sec(rows[-1][2]))+2.0
# (spreker-regel waar de shot begint, afbeelding, beweging, extra, tijdstempel)
SH=[(1,"109","in","",None),(2,"101","out","",None),(3,"001","in","",None),
 (4,"110","in","","HOUR 1"),(6,"002","out","eq=brightness='-0.4*min(max((t-1.3)/0.8,0),1)'",None),
 (7,"104","in","","HOUR 36"),(9,"103","in","",None),(10,"105","up","","YEAR 20"),(12,"106","in","",None),
 (13,"107","up","","YEAR 300"),(15,"005","shake","",None),(16,"006","out","","YEAR 500"),
 (18,"108","in","",None),(19,"007","punch","",None),(21,"111","in","",None)]
starts=[0.0]+[T(sec(rows[r-1][1])) for r,*_ in SH[1:]]
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
    out=f"{S}/docseg{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"{A}/{img}.jpg","-vf",vf,"-frames:v",str(n),
      "-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out],check=True)
    segs.append(out)
open(f"{S}/doclist.txt","w").write("".join(f"file '{s}'\n" for s in segs))
# ondertitels + tijdstempels
ts=lambda s: f"{int(s//3600)}:{int(s%3600//60):02d}:{s%60:05.2f}"
ass=["[Script Info]","PlayResX: 1080","PlayResY: 1920","","[V4+ Styles]",
"Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
"Style: Sub,DejaVu Serif,62,&H00F0F0F0,&H00FFFFFF,&H00000000,&H96000000,1,0,0,0,100,100,0,0,1,5,3,2,110,110,430,1",
"Style: Stamp,DejaVu Sans Mono,96,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,6,0,1,4,0,7,80,80,300,1",
"Style: Small,DejaVu Sans Mono,40,&H0080C8F2,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,4,0,1,3,0,7,84,80,250,1",
"Style: Pop,DejaVu Sans Mono,66,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,3,0,1,4,0,8,60,60,330,1",
"","[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
for i,r in enumerate(rows):
    st=T(sec(r[1])); en=T(sec(rows[i+1][1])) if i+1<len(rows) else END-0.8
    ass.append(f"Dialogue: 0,{ts(st)},{ts(en)},Sub,,0,0,0,,{{\\fad(120,120)}}{r[4]}")
for i,(r,img,mv,extra,stamp) in enumerate(SH):
    if stamp:
        st=starts[i]; en=starts[i+1]
        ass.append(f"Dialogue: 1,{ts(st)},{ts(en)},Small,,0,0,0,,{{\\fad(80,200)}}AFTER HUMANS")
        ass.append(f"Dialogue: 1,{ts(st)},{ts(en)},Stamp,,0,0,0,,{{\\fad(80,200)}}{stamp}")
ass.append(f"Dialogue: 1,{ts(starts[1])},{ts(starts[2])},Pop,,0,0,0,,{{\\fad(150,0)}}POPULATION\\N8,000,000,000")
ass.append(f"Dialogue: 1,{ts(starts[2])},{ts(starts[3])},Pop,,0,0,0,,{{\\c&H3030E0&\\fad(0,200)}}POPULATION\\N0")
open("subs.ass","w").write("\n".join(ass)+"\n")
hits=[starts[i] for i,s in enumerate(SH) if s[4]]+[starts[2],starts[13]]
open(f"{S}/docmeta.txt","w").write(f"{END:.2f}\n"+" ".join(f"{h:.2f}" for h in hits)+"\n")
