# Hyperspace + fly-through demo, fully procedural (free)
import numpy as np,cv2,subprocess,math,wave
W,H,FPS=1080,1920,30;T=12;N=T*FPS;rng=np.random.default_rng(2)
BPM=128;beat=60/BPM
# ---------- procedural space images ----------
def fbm(h,w,oct=6,seed=0):
    r=np.random.default_rng(seed);acc=np.zeros((h,w),np.float32);amp=1
    for o in range(oct):
        s=2**o*3;n=r.standard_normal((s,s)).astype(np.float32)
        acc+=amp*cv2.resize(n,(w,h),interpolation=cv2.INTER_CUBIC);amp*=0.55
    acc-=acc.min();return acc/acc.max()
def stars(img,n,seed):
    r=np.random.default_rng(seed)
    for _ in range(n):
        x,y=r.integers(0,img.shape[1]),r.integers(0,img.shape[0]);b=r.uniform(.4,1)**3
        cv2.circle(img,(int(x),int(y)),int(r.uniform(0.5,2.2)),(255*b,240*b,230*b),-1,cv2.LINE_AA)
    return img
def nebula(seed,c1,c2,c3):
    S=1400;f=fbm(S,S,7,seed);g=fbm(S,S,6,seed+9)
    yy,xx=np.mgrid[0:S,0:S]/S;core=np.exp(-((xx-.5)**2+(yy-.5)**2)/0.08)
    d=np.clip(f*1.3*core+0.15*g-0.25,0,1)**1.6
    img=(np.float32(c1)*d[...,None]+np.float32(c2)*(d*g)[...,None]*1.5+np.float32(c3)*(d**3)[...,None]*2.5)
    img=img*0.55+cv2.GaussianBlur(img,(0,0),25)*0.35
    img=255*(1-np.exp(-img/150))
    return np.clip(stars(img,1400,seed),0,255)
def planet(seed):
    S=1400;img=stars(np.zeros((S,S,3),np.float32),900,seed);R=430
    yy,xx=np.mgrid[0:S,0:S].astype(np.float32);dx,dy=(xx-S/2)/R,(yy-S/2)/R;r2=dx*dx+dy*dy;m=r2<1
    z=np.sqrt(np.clip(1-r2,0,1));t=fbm(S,S,6,seed)
    col=np.float32([150,120,40])*(1-t[...,None])+np.float32([220,200,90])*t[...,None]
    light=np.clip(dx*-0.5+dy*-0.4+z*0.8,0,1)[...,None]
    img[m]=(col*light)[m]
    atm=np.exp(-((np.sqrt(r2)-1)/0.04)**2)[...,None]*np.float32([255,200,120])*0.8;img+=atm
    return np.clip(img,0,255)
IM=[nebula(1,(60,40,200),(30,120,255),(200,230,255)),   # orange/red
    nebula(5,(180,60,120),(90,200,60),(220,180,255)),    # magenta/green
    planet(7)]
IM=[cv2.resize(i,(int(W*1.5),int(W*1.5*1)),interpolation=cv2.INTER_AREA) for i in IM]
def place(img,z):
    h,w=img.shape[:2];s=z*H/h*1.0;M=np.float32([[s,0,W/2-s*w/2],[0,s,H/2-s*h/2]])
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderValue=(0,0,0))
def radial_blur(img,amt):
    if amt<0.01: return img
    acc=img.copy();n=6
    for i in range(1,n):
        z=1+amt*i/n;M=cv2.getRotationMatrix2D((W/2,H/2),0,z);acc+=cv2.warpAffine(img,M,(W,H))
    return acc/n
# ---------- starfield ----------
NS=2500;P=np.column_stack([rng.uniform(-1,1,NS),rng.uniform(-1,1,NS),rng.uniform(0.05,1,NS)])
def starfield(t,speed):
    img=np.zeros((H,W,3),np.float32);f=700
    z0=P[:,2].copy();P[:,2]-=speed/FPS;dead=P[:,2]<0.02;P[dead,2]+=1;P[dead,0:2]=rng.uniform(-1,1,(dead.sum(),2))
    for (x,y,z),zp,d in zip(P,z0,dead):
        if d: continue
        x1,y1=W/2+x*f/z,H/2+y*f/z;x0,y0=W/2+x*f/zp,H/2+y*f/zp
        if -50<x1<W+50 and -50<y1<H+50:
            b=min(255,90/z);cv2.line(img,(int(x0),int(y0)),(int(x1),int(y1)),(b,b,b*1.05),max(1,int(1.5/z**0.5)),cv2.LINE_AA)
    return img
# ---------- timeline ----------
WARP=4.5;cuts=[WARP+beat*k*2 for k in range(int((T-WARP)/(beat*2))+1)]   # fly into a new image every 2 beats
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-i','beat.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','-c:a','aac','-shortest','warp_demo.mp4'],stdin=subprocess.PIPE)
# simple synth beat (free): kick on every beat, hat on offbeats, bass drone, whoosh at transitions
sr=48000;n=int(T*sr);tn=np.arange(n)/sr;au=np.zeros(n)
def add(s,t,g=1):
    i=int(t*sr);j=min(n,i+len(s));au[i:j]+=s[:j-i]*g
k=int(.4*sr);kt=np.arange(k)/sr;kick=np.sin(2*np.pi*(50+120*np.exp(-kt*30))*kt)*np.exp(-kt*7)
h=int(.05*sr);hat=rng.standard_normal(h)*np.exp(-np.arange(h)/sr*90)*0.25
for b in np.arange(0,T,beat):
    if b>=WARP-beat*2: add(kick,b,0.9)
    add(hat,b+beat/2,0.6 if b>=WARP else 0.25)
au+=0.12*np.sin(2*np.pi*55*tn)*np.clip((tn-WARP+2)/2,0,1)+0.05*np.sin(2*np.pi*110*tn+np.sin(tn))
riser=rng.standard_normal(n)*np.clip(tn/WARP,0,1)**3*(tn<WARP)*0.25;au+=cv2.GaussianBlur(riser.reshape(-1,1),(1,0),3).ravel() if False else riser*0.6
for c in cuts:
    q=int(.6*sr);qt=np.arange(q)/sr;add(rng.standard_normal(q)*np.sin(np.pi*qt/.6)**2*0.3,c-0.3)
au=np.clip(au/np.abs(au).max()*0.9,-1,1)
with wave.open('beat.wav','wb') as w: w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((au*32767).astype('<i2').tobytes())
for f in range(N):
    t=f/FPS
    if t<WARP:
        sp=0.15+2.6*(t/WARP)**2
        fr=starfield(t,sp)
        fl=max(0,(t-(WARP-0.25))/0.25);fr=fr*(1-fl)+255*fl
    else:
        i=max(k for k,c in enumerate(cuts) if t>=c);c=cuts[i];u=(t-c)/(beat*2)
        cur=IM[i%3];nxt=IM[(i+1)%3]
        if (i//3)%2: cur=cv2.flip(cur,1)
        if ((i+1)//3)%2: nxt=cv2.flip(nxt,1)
        z=1.0+0.6*u**3                         # slow drift, then accelerate into image
        fr=place(cur,z)
        if u>0.75:                            # next image grows from the centre = flying through
            v=(u-0.75)/0.25;fr=fr*(1-v)+place(nxt,0.15+0.85*v**2)*v
            fr=radial_blur(fr,0.25*v)
        ph=(t-WARP)%beat/beat;pulse=math.exp(-ph*6)
        fr=fr*(1+0.15*pulse);M=cv2.getRotationMatrix2D((W/2,H/2),0,1+0.03*pulse);fr=cv2.warpAffine(fr,M,(W,H))
        if u<0.08: fr=fr+(1-u/0.08)*110
    p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
p.stdin.close();p.wait();print('ok')
