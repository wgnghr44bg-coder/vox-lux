import cv2,numpy as np,subprocess,math
src=cv2.imread('/root/.claude/uploads/86e7f707-f363-5172-8e05-1d77434a04d3/068c3508-image.png')
im=src[380:2083,110:1068].astype(np.float32);H,W=im.shape[:2]
D=lambda x,y:(x*1.2774-110,y*1.2774-380)
tx0,ty0=map(int,D(290,713));tx1,ty1=map(int,D(658,946))
TV=im[ty0:ty1,tx0:tx1].copy();th,tw=TV.shape[:2]
cx,cy=D(463,833);cx-=tx0;cy-=ty0
mx,my=D(552,893);mx-=tx0;my-=ty0
ax0,ay0=map(int,D(538,719));ax1,ay1=map(int,D(652,741));ax0-=tx0;ax1-=tx0;ay0-=ty0;ay1-=ty0
amBG=TV[ay0:ay1,ax0:ax0+6].mean(axis=(0,1))
# LED mask
hsv=cv2.cvtColor(im.astype(np.uint8),cv2.COLOR_BGR2HSV)
led=((hsv[...,1]>110)&(hsv[...,2]>150)&(((hsv[...,0]>125)&(hsv[...,0]<170))|((hsv[...,0]>80)&(hsv[...,0]<105)))).astype(np.float32)
led=cv2.GaussianBlur(led,(0,0),6)[...,None]
yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
_,hy=D(0,1150);_,hy2=D(0,1260)
wh=np.clip((yy-hy)/(hy2-hy),0,1)  # hands weight
t1=D(372,1258);t2=D(605,1250)
def blob(p,r): return np.exp(-((xx-p[0])**2+(yy-p[1])**2)/(2*r*r))
b1,b2=blob(t1,28),blob(t2,28)
fps=30;N=8*fps
shots=[0.9,1.15,1.4,2.6,2.8,3.9,4.1,4.3,5.6,5.85,6.9,7.2]
def pulse(t,ts,d):
    v=0
    for s in ts:
        if 0<=t-s<d: v=max(v,1-(t-s)/d)
    return v
out='game.mp4'
p=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{1080}x{1920}','-r',str(fps),'-i','-','-c:v','libx264','-pix_fmt','yuv420p','-crf','18',out],stdin=subprocess.PIPE)
for f in range(N):
    t=f/fps;fr=im.copy()
    sh=pulse(t,shots,0.12);rec=pulse(t,shots,0.2)
    # --- TV: walking forward, head bob, recoil
    z=1+0.12*t/8+0.015*rec
    bx=3*math.sin(t*2*math.pi*0.9)+2*rec;by=2.5*abs(math.sin(t*2*math.pi*0.9))+5*rec
    M=np.float32([[z,0,(1-z)*cx+bx],[0,z,(1-z)*cy-by]])
    tv=cv2.warpAffine(TV,M,(tw,th),borderMode=cv2.BORDER_REFLECT)
    # hit flash on zombie near crosshair
    hit=pulse(t,[s+0.05 for s in shots],0.25)
    zb=np.exp(-((np.arange(tw)[None,:]-cx)**2/(2*40**2)+(np.arange(th)[:,None]-cy)**2/(2*60**2)))[...,None]
    tv=tv+hit*zb*np.float32([0,0,120])
    # muzzle flash
    if sh>0:
        fl=np.exp(-((np.arange(tw)[None,:]-mx)**2+(np.arange(th)[:,None]-my)**2)/(2*(14+10*sh)**2))[...,None]
        tv=tv+fl*sh*np.float32([120,220,255])*1.4+sh*18
    # ammo counter
    ammo=30-sum(1 for s in shots if s<=t)
    tv[ay0:ay1,ax0:ax1]=amBG;tv=np.clip(tv,0,255).astype(np.uint8)
    cv2.putText(tv,f'AMMO: {ammo}/30',(ax0+2,ay1-5),cv2.FONT_HERSHEY_DUPLEX,0.62,(240,240,240),1,cv2.LINE_AA)
    tv=tv.astype(np.float32)
    fr[ty0:ty1,tx0:tx1]=tv
    # TV glow onto room
    glow=blob(((tx0+tx1)/2,(ty0+ty1)/2),330)[...,None]
    fr=fr*(1+0.10*sh*glow)+glow*sh*np.float32([10,25,30])
    # LEDs pulse
    fr=fr+led*fr*0.18*math.sin(t*2*math.pi*0.5)
    # --- hands/controller: breathing + recoil shake + tilt
    dx=1.5*math.sin(t*2*math.pi*0.25)+4*rec*math.sin(f*2.3)+3*math.sin(t*1.3)
    dy=2*math.sin(t*2*math.pi*0.3)+5*rec
    ang=0.6*math.sin(t*0.9)*math.pi/180
    ccx,ccy=W/2,H*0.85
    mapx=xx-wh*(dx+(-(yy-ccy)*ang))
    mapy=yy-wh*(dy+((xx-ccx)*ang))
    # thumbs: right presses on shots, left circles the stick
    press=pulse(t,shots,0.15)
    mapy=mapy-b2*6*press
    mapx=mapx-b1*3*math.cos(t*4);mapy=mapy-b1*3*math.sin(t*4)
    fr=cv2.remap(np.clip(fr,0,255).astype(np.float32),mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    o=cv2.resize(fr,(1080,1920),interpolation=cv2.INTER_CUBIC)
    p.stdin.write(np.clip(o,0,255).astype(np.uint8).tobytes())
    if f in (30,33,120): cv2.imwrite(f'chk{f}.png',cv2.resize(o,(360,640)))
p.stdin.close();p.wait();print('done')
