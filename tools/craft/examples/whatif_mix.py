import numpy as np,subprocess,wave
sr=48000;DUR=[6,8.8,9.4,9,9.4,9,8.4];ST=np.cumsum([0]+DUR[:-1]);T=sum(DUR);n=int(T*sr)
rng=np.random.default_rng(7);tn=np.arange(n)/sr;L=np.zeros(n);R=np.zeros(n)
def lp(x,a):
    y=np.empty_like(x);s=0.
    for i,v in enumerate(x): s+=a*(v-s);y[i]=s
    return y
def add(sig,t,g=1,pan=0):
    i=int(t*sr);j=min(n,i+len(sig));s=sig[:j-i]*g;L[i:j]+=s*(1-max(0,pan));R[i:j]+=s*(1+min(0,pan))
env=lambda t0,t1,a=0.5:np.clip((tn-t0)/a,0,1)*np.clip((t1-tn)/a,0,1)
# flatline tone then heartbeat beeps (scene 1), fainter in scene 2
fl=np.sin(2*np.pi*1000*tn)*env(0.1,1.8,0.05)*0.06;L+=fl;R+=fl
b=int(0.12*sr);bt=np.arange(b)/sr;beep=np.sin(2*np.pi*1000*bt)*np.minimum(1,(0.12-bt)/0.02)*0.12
for t in np.arange(1.8+0.3/1.2,ST[2],1/1.2): add(beep,t,1 if t<ST[1] else 0.35)
d=sum(g*np.sin(2*np.pi*f*tn+np.sin(tn*0.2*f/55)) for f,g in [(49,1),(49.3,.8),(73.4,.5),(98,.3),(58.3,.35)])
d*=0.6+0.4*np.sin(tn*0.13-1.5);m=env(0.5,T,3)*(0.05+0.05*np.clip((tn-ST[3])/20,0,1));L+=d*m;R+=d*m
for k in range(5):
    m_=int(0.6*sr);mt=np.arange(m_)/sr;f=420+80*np.sin(2*np.pi*3*mt)
    add(np.sin(2*np.pi*np.cumsum(f)/sr)*np.sin(np.pi*mt/0.6)**2*0.03,ST[2]+1+k*1.5+rng.uniform(0,.5),1,rng.uniform(-.6,.6))
cr=lp(rng.standard_normal(n),0.06)*(1+0.3*np.sin(tn*2.3))*1.2;w=env(ST[3],ST[4]+1,0.8)*0.35;L+=cr*w;R+=np.roll(cr,999)*w
bz=(np.sin(2*np.pi*100*tn)+0.5*np.sin(2*np.pi*200*tn)+0.3*np.sign(np.sin(2*np.pi*100*tn)))*env(ST[4],ST[5],0.3)*0.03;L+=bz;R+=bz
c=int(0.15*sr);ct=np.arange(c)/sr;clunk=(lp(rng.standard_normal(c),0.3)*np.exp(-ct*40)+np.sin(2*np.pi*120*ct)*np.exp(-ct*30))*0.25
for i in range(6): add(clunk,ST[4]+1.5+i*0.9)
wd=lp(rng.standard_normal(n),0.01)*3*env(ST[5],ST[6]+2,1.5)*0.2;L+=wd;R+=np.roll(wd,4000)
c=int(0.02*sr);ct=np.arange(c)/sr;tick=rng.standard_normal(c)*np.exp(-ct*300)*0.15
for t in np.arange(ST[6],ST[6]+6.5,0.5): add(tick,t)
for s in ST[1:]:
    q=int(0.8*sr);qt=np.arange(q)/sr;add(lp(rng.standard_normal(q),0.05)*np.sin(np.pi*qt/0.8)**2*1.2,s-0.4,0.5)
    h=int(1.2*sr);ht=np.arange(h)/sr;add(np.sin(2*np.pi*(55*np.exp(-ht*3)+30)*ht)*np.exp(-ht*4)*0.5,s)
for i in range(7):
    v=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',f'vo/l{i+1}.mp3','-f','f32le','-ac','1','-ar',str(sr),'-']),np.float32).astype(float);v/=np.abs(v).max()
    add(v,ST[i]+0.8)
fade=np.clip(tn/0.2,0,1)*np.clip((T-tn)/1.0,0,1);st=np.stack([L,R],1)*fade[:,None];st/=np.abs(st).max()*1.1
with wave.open('mix.wav','wb') as w: w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype('<i2').tobytes())
print('mix ok',T)
