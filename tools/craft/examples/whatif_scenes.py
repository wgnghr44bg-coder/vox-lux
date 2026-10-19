import cv2,numpy as np,subprocess,math,random
from PIL import Image,ImageDraw,ImageFont
W,H,FPS=1080,1920,30
SP='/tmp/claude-0/-home-user/86e7f707-f363-5172-8e05-1d77434a04d3/scratchpad'
FONT='/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'
VO=[float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',f'vo/l{i}.mp3'])) for i in range(1,8)]
import json
DUR=[6,8.8,9.4,9,9.4,9,8.4]
LINES=json.load(open('lines.json'))
LABEL=[None,"DAG 1","WEEK 1","JAAR 1","JAAR 10","JAAR 50",None]
def cover(img,w=W,h=H):
    ih,iw=img.shape[:2];s=max(w/iw,h/ih);r=cv2.resize(img,(int(iw*s+.5),int(ih*s+.5)),interpolation=cv2.INTER_AREA if s<1 else cv2.INTER_CUBIC)
    y=(r.shape[0]-h)//2;x=(r.shape[1]-w)//2;return r[y:y+h,x:x+w].astype(np.float32)
def blurfill(img):
    bg=cv2.GaussianBlur(cover(img),(0,0),40)*0.45
    ih,iw=img.shape[:2];s=W/iw;fg=cv2.resize(img,(W,int(ih*s)),interpolation=cv2.INTER_CUBIC).astype(np.float32)
    y=(H-fg.shape[0])//2-120;bg[y:y+fg.shape[0]]=fg;return bg
def kb(img,z,ox=0,oy=0,rot=0):
    M=cv2.getRotationMatrix2D((W/2+ox,H/2+oy),rot,z);return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
ss=lambda x:min(1,max(0,x))**2*(3-2*min(1,max(0,x)))
def frames_of(path):
    p=subprocess.Popen(['ffmpeg','-v','error','-i',path,'-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
    while True:
        b=p.stdout.read(W*H*3)
        if len(b)<W*H*3: break
        yield np.frombuffer(b,np.uint8).reshape(H,W,3).astype(np.float32)
fcache={}
def font(sz):
    if sz not in fcache: fcache[sz]=ImageFont.truetype(FONT,sz)
    return fcache[sz]
def text(fr,txt,y,sz,alpha=1,color=(255,255,255),stroke=6,spacing=1.0):
    if alpha<=0: return fr
    im=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(im);f=font(sz)
    ls=txt.split('\n');yy=y
    for l in ls:
        while d.textlength(l,font=f)>W-110 and f.size>30: f=font(f.size-4)
        w=d.textlength(l,font=f);d.text(((W-w)/2,yy),l,font=f,fill=color+(255,),stroke_width=stroke,stroke_fill=(0,0,0,255));yy+=int(sz*1.18*spacing)
    a=np.asarray(im).astype(np.float32);al=a[...,3:]/255*alpha
    return fr*(1-al)+a[...,2::-1]*al
def chunks(line,dur,start=0.8):
    w=line.split();cs=[];i=0
    while i<len(w):
        n=3 if len(w)-i!=4 else 2;cs.append(' '.join(w[i:i+n]));i+=n
    tot=sum(len(c) for c in cs);t=start;out=[]
    for c in cs:
        d=dur*len(c)/tot;out.append((t,t+d,c));t+=d
    return out
def caption(fr,k,t):
    for a,b,c in chunks(LINES[k],VO[k]):
        if a<=t<b+(0.4 if c==chunks(LINES[k],VO[k])[-1][2] else 0):
            pop=min(1,(t-a)/0.08);return text(fr,c.upper(),1380,int(64+6*pop),1,(255,255,255),7)
    return fr
def label(fr,k,t):
    if LABEL[k] is None: return fr
    a=min(1,t/0.4)*min(1,(DUR[k]-t)/0.4)
    return text(fr,LABEL[k],230,54,a,(120,200,240),5)
def write(k,gen):
    p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',f'scene{k+1}.mp4'],stdin=subprocess.PIPE)
    n=int(round(DUR[k]*FPS))
    for f in range(n):
        t=f/FPS;fr=gen(t,f)
        fr=label(caption(fr,k,t),k,t)
        if f in (n//2,):cv2.imwrite(f'chk{k+1}.jpg',cv2.resize(np.clip(fr,0,255).astype(np.uint8),(270,480)))
        p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
    p.stdin.close();p.wait();print('scene',k+1,'ok',flush=True)

rng=np.random.default_rng(5)
DUST=rng.uniform(0,1,(140,4))
def fx(fr,t,f):
    for x,y,sp,sz in DUST:
        px=int((x*W+15*math.sin(t*0.5+y*9))%W);py=int((y*H-sp*40*t)%H)
        cv2.circle(fr,(px,py),int(1+sz*2.5),(200,220,235),-1,cv2.LINE_AA) if sz>0.6 else None
    fr+=rng.normal(0,5,(H//4,W//4,1)).repeat(4,0).repeat(4,1)
    return fr
def counter(fr,t,label,val,t0,t1):
    a=ss((t-t0)/0.4);v=int(val*ss((t-t0)/(t1-t0)))
    fr=text(fr,label,330,34,a,(200,200,200),3)
    return text(fr,"+"+f"{v:,}".replace(",","."),380,96,a,(255,255,255),6)

IMG=[cover(cv2.imread(f'img/{i}.jpg')) for i in range(1,8)]
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
blob=lambda x,y,r:np.exp(-((xx-x)**2+(yy-y)**2)/(2*r*r))
noise=cv2.GaussianBlur(rng.standard_normal((H*2,W)).astype(np.float32),(0,0),6)*8
crowd=np.clip((yy-950)/120,0,1)*np.clip((xx-200)/60,0,1)*np.clip((880-xx)/60,0,1)
LIGHTS=[(540,y,w) for y,w in [(497,420),(578,320),(632,250),(670,200),(698,160),(718,130)]]
def ecg(img,t):
    x0,x1,y0=175,485,1058
    head=x0+((t*110)%(x1-x0))
    pts=[]
    for x in range(x0,x1,2):
        age=(head-x)%(x1-x0)
        tt=t-age/110
        v=0
        if tt>1.8:
            ph=(tt*1.2)%1
            v=-60*math.exp(-((ph-0.3)/0.02)**2)+18*math.exp(-((ph-0.36)/0.02)**2)-10*math.exp(-((ph-0.6)/0.06)**2)
        pts.append((x,int(y0+v)))
    cv2.rectangle(img,(x0-8,y0-80),(x1+8,y0+70),(18,25,18),-1)
    cv2.polylines(img,[np.array(pts,np.int32)],False,(110,255,140),4,cv2.LINE_AA)
    cv2.circle(img,(int(head),y0),7,(200,255,210),-1,cv2.LINE_AA)
    return img
SAND=rng.uniform(0,1,(120,2))
def g(k):
    def gen(t,f):
        img=IMG[k].copy();d=DUR[k]
        shx=4*math.sin(t*1.7+k)+2*math.sin(t*3.1);shy=3*math.sin(t*1.3+2*k)
        z0=0.18*(1-ss(t/0.35)) if k>0 else 0
        if k==0:
            img=ecg(img,t)
            if t>1.8: img+=50*math.exp(-((t*1.2)%1)*7)*blob(330,1058,180)[...,None]*np.float32([0.3,1,0.4])
            fr=kb(img,1.0+0.045*t+z0,shx,60+shy)
            fr=text(fr,"WAT ALS...",260,130,ss((t-0.2)/0.5),(255,255,255),8)
        elif k==1:
            fl=1 if rng.random()>0.1 else 0.55
            img[:H//3]*=fl
            img+=(0.5+0.5*math.sin(t*6))*80*blob(540,800,60)[...,None]*np.float32([0.2,0.2,1])
            fr=kb(img,1.0+0.03*t+z0,shx,-40+8*t+shy)
        elif k==2:
            band=np.exp(-((xx-(-300+t*180)-0.4*(yy-1200))/160)**2)
            img+=band[...,None]*45*np.float32([0.6,0.85,1])
            fr=counter(kb(img,1.15-0.012*t+z0,-60+14*t+shx,shy),t,"GEBOORTES PER DAG",380000,1.0,6.0)
        elif k==3:
            nf=noise[int((H-t*60)%H):int((H-t*60)%H)+H]
            mx=xx+crowd*nf*0.6;my=yy+crowd*(np.roll(nf,37,1)*0.6)
            img=cv2.remap(img,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
            fr=counter(kb(img,1.0+0.05*t+z0,shx,120-10*t+shy),t,"MENSEN ERBIJ PER JAAR",130000000,1.0,7.0)
        elif k==4:
            dark=0.0
            for i,(x,y,w) in enumerate(LIGHTS):
                off=t>1.5+i*0.9
                if not off and rng.random()<0.06: off=True
                m=np.exp(-((yy-y)/40)**2)*np.clip(1-np.abs(xx-x)/(w+150),0,1)
                img*=1-(0.55*m[...,None] if off else 0)
                if off: dark+=0.07
            img*=1-min(0.45,dark)
            fr=kb(img,1.0+0.04*t+z0,shx,shy)
        elif k==5:
            gr=img.mean(axis=2,keepdims=True);m=0.5*ss(t/6);img=img*(1-m)+gr*m
            for j,bx in enumerate([760,880,1000]):
                ofs=bx+40*math.sin(t*0.6+j)
                beam=np.exp(-((xx-ofs+0.55*(yy-650))/55)**2)*np.clip((yy-600)/200,0,1)*np.clip((1700-yy)/400,0,1)
                img+=beam[...,None]*(28+14*math.sin(t*1.3+j))
            fr=kb(img,1.0+0.035*t+z0,shx,40+shy)
        else:
            speed=max(0,1-t/6.5)
            for x,y in SAND:
                py=1140+((y*340+t*420*speed)%340) if speed>0 else 1140+y*340
                if py<1450: cv2.circle(img,(int(535+(x-0.5)*6),int(py)),2,(110,190,235),-1,cv2.LINE_AA)
            img+=25*blob(535,1300,160)[...,None]*np.float32([0.2,0.6,1])*(0.6+0.4*math.sin(t*2))
            fr=kb(img,1.0+0.03*t+z0,40-6*t+shx,shy)
            fr=text(fr,"VOLG VOOR MEER\nWHAT IF'S",300,64,ss((t-5.0)/0.6),(232,196,120),6)
            fr=fr*min(1,(d-t)/1.0)
        if k>0: fr=fr*(1+0.6*(1-ss(t/0.25)))
        return fx(fr,t,f)*min(1,t/0.25 if k==0 else 1)
    return gen
for k in range(7): write(k,g(k))
