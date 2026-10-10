"""V2: één beeld per gesproken zin/zinsdeel, cuts precies op de stem."""
import subprocess, sys
S=sys.argv[1]; FPS=30; END=34.4
# (start in s, afbeelding, beweging, extra filter)
SCENES=[(0.00,"101","in",""),(2.22,"001","out",""),
 (3.25,"002","in","eq=brightness='-0.35*between(t,1.1,9)*min((t-1.1)/0.6,1)'"),
 (5.50,"102","rot",""),(6.83,"103","in",""),(9.49,"104","out",""),
 (11.07,"004","in",""),(12.81,"105","up",""),(14.99,"106","in",""),
 (16.70,"107","up",""),(20.75,"005","shake",""),(21.83,"006","out",""),
 (26.56,"108","in",""),(29.88,"007","punch",""),(31.69,"109","out","")]
segs=[]
for i,(st,img,mv,extra) in enumerate(SCENES):
    d=(SCENES[i+1][0] if i+1<len(SCENES) else END)-st; n=round(d*FPS)
    cx,cy="iw/2-(iw/zoom/2)","ih/2-(ih/zoom/2)"
    z={"in":f"1+0.18*on/{n}","out":f"1.18-0.18*on/{n}","rot":f"1.05+0.10*on/{n}",
       "up":"1.15","shake":f"1.12+0.05*on/{n}","punch":f"1.25-0.2*min(on/8,1)"}[mv]
    if mv=="up": cy=f"(ih-ih/zoom)*(1-on/{n})"
    if mv=="shake": cx+="+12*sin(on*2.1)"; cy+="+12*cos(on*1.7)"
    if mv=="rot": cx=f"(iw-iw/zoom)*on/{n}"
    vf=f"scale=2160:3840,zoompan=z='{z}':x='{cx}':y='{cy}':d={n}:s=1080x1920:fps={FPS}"
    if extra: vf+=","+extra
    vf+=",eq=contrast=1.06:saturation=0.92,noise=alls=7:allf=t,vignette=PI/5"
    out=f"{S}/v2seg{i:02d}.mp4"
    subprocess.run(["ffmpeg","-v","error","-y","-loop","1","-i",f"afbeeldingen/{img}.jpg","-vf",vf,
      "-frames:v",str(n),"-c:v","libx264","-pix_fmt","yuv420p","-crf","18",out],check=True)
    segs.append(out)
open(f"{S}/v2list.txt","w").write("".join(f"file '{s}'\n" for s in segs))
