"""Rustigere stem zonder nieuwe TTS: langere pauzes tussen de zinnen + iets trager (atempo)."""
import csv, subprocess
TEMPO = 0.93            # 7% trager
LEAD = 0.8              # stilte voor "Earth."
PAUSE = {"short": 0.6, "long": 1.4}   # extra stilte na een zin / na een [long pause]
sec=lambda s: sum(float(p)*m for p,m in zip(s.split(":"),(3600,60,1)))
rows=[r for r in csv.reader(open("voice-times.tsv"),delimiter="\t") if not r[0].startswith("#")]
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","voice.mp3"],capture_output=True,text=True).stdout)
parts=[]; out=[]; t=LEAD
for i,r in enumerate(rows):
    a=sec(r[1]); b=sec(rows[i+1][1]) if i+1<len(rows) else dur
    gap=(sec(rows[i+1][1])-sec(r[2])) if i+1<len(rows) else 0
    extra=0 if i+1==len(rows) else PAUSE["long"] if gap>0.8 or i==0 else PAUSE["short"] if gap>0.2 else 0.15
    out.append([r[0], f"{t:.2f}", f"{t+(sec(r[2])-a)/TEMPO:.2f}", r[3], r[4]])
    parts.append((a,b,extra)); t+=(b-a)/TEMPO+extra
fc=f"aevalsrc=0:d={LEAD}:s=44100[l];"; L="[l]"
for i,(a,b,e) in enumerate(parts):
    fc+=f"[0:a]atrim={a}:{b},asetpts=N/SR/TB,aresample=44100,pan=mono|c0=c0,atempo={TEMPO}[p{i}];aevalsrc=0:d={e+0.001}:s=44100[g{i}];"
    L+=f"[p{i}][g{i}]"
fc+=f"{L}concat=n={2*len(parts)+1}:v=0:a=1[a]"
subprocess.run(["ffmpeg","-v","error","-y","-i","voice.mp3","-filter_complex",fc,"-map","[a]","-b:a","192k","voice-calm.mp3"],check=True)
with open("voice-times-calm.tsv","w") as f:
    f.write("#\tstart\tend\timage\ttext\n"+"".join("\t".join(r)+"\n" for r in out))
print(f"duur {t:.1f}s")
