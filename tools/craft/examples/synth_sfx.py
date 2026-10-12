import numpy as np,wave
sr=48000;T=8;n=sr*T;rng=np.random.default_rng(1)
L=np.zeros(n);R=np.zeros(n)
shots=[0.9,1.15,1.4,2.6,2.8,3.9,4.1,4.3,5.6,5.85,6.9,7.2]
def lp(x,a):  # one-pole lowpass
    y=np.empty_like(x);s=0.
    for i,v in enumerate(x): s+=a*(v-s);y[i]=s
    return y
def add(sig,t,gain=1,pan=0):
    i=int(t*sr);j=min(n,i+len(sig));s=sig[:j-i]*gain
    L[i:j]+=s*(1-max(0,pan));R[i:j]+=s*(1+min(0,pan))
# gunshot: crack + boom + room tail
d=int(0.6*sr);tt=np.arange(d)/sr
crack=rng.standard_normal(d)*np.exp(-tt*60)
boom=np.sin(2*np.pi*(70*np.exp(-tt*8)+45)*tt)*np.exp(-tt*9)
tail=lp(rng.standard_normal(d),0.08)*np.exp(-tt*7)*0.8
gun=0.55*crack+0.9*boom+tail
# trigger click (controller)
c=int(0.03*sr);ct=np.arange(c)/sr
click=(rng.standard_normal(c)*0.6+np.sin(2*np.pi*2400*ct))*np.exp(-ct*400)
for s in shots:
    add(gun,s,0.7); add(click,s-0.03,0.25,pan=0.3)
    # shell casing tinkle
    k=int(0.25*sr);kt=np.arange(k)/sr
    add(np.sin(2*np.pi*rng.uniform(3800,4600)*kt)*np.exp(-kt*25)*0.12,s+0.35,1,pan=0.4)
# footsteps in game
st=int(0.18*sr);stt=np.arange(st)/sr
step=lp(rng.standard_normal(st),0.05)*np.exp(-stt*30)*1.5+np.sin(2*np.pi*90*stt)*np.exp(-stt*35)*0.4
for k,t in enumerate(np.arange(0.2,T,1/1.8)): add(step,t,0.35,pan=0.15 if k%2 else -0.15)
# zombie groans: glottal pulses through formant-ish filtering
def groan(dur,f0):
    m=int(dur*sr);gt=np.arange(m)/sr
    f=f0*(1+0.08*np.sin(2*np.pi*3*gt))+rng.standard_normal(m).cumsum()*0.0005
    ph=2*np.pi*np.cumsum(f)/sr
    src=np.sign(np.sin(ph))*0.5+np.sin(ph*2)*0.3+rng.standard_normal(m)*0.25
    v=lp(src,0.06)-lp(src,0.01)
    env=np.sin(np.pi*gt/dur)**0.7
    return v*env*3
for t,dur,f0,pan in [(0.3,1.6,85,-0.3),(2.0,1.3,72,0.4),(3.3,1.8,95,-0.1),(5.0,1.4,78,0.3),(6.3,1.7,88,-0.4)]:
    add(groan(dur,f0),t,0.5,pan)
# room ambience: hum + soft hiss
tn=np.arange(n)/sr
amb=0.02*np.sin(2*np.pi*50*tn)+0.01*np.sin(2*np.pi*100*tn)+lp(rng.standard_normal(n),0.02)*0.15
L+=amb;R+=amb
# fades + normalize
fade=np.minimum(1,np.minimum(tn/0.3,(T-tn)/0.5))
st=np.stack([L,R],1)*fade[:,None];st/=np.abs(st).max()*1.12
with wave.open('sound.wav','wb') as w:
    w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
