import cv2,numpy as np,subprocess,math
W,H,fps=1080,1920,30;N=8*fps
shots=[0.9,1.15,1.4,2.6,2.8,3.9,4.1,4.3,5.6,5.85,6.9,7.2]
def pulse(t,d):
    return max([1-(t-s)/d for s in shots if 0<=t-s<d]+[0])
ss=lambda x:x*x*(3-2*x)
rd=subprocess.Popen(['ffmpeg','-v','error','-i','game.mp4','-f','rawvideo','-pix_fmt','bgr24','-'],stdout=subprocess.PIPE)
wr=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i','sound.wav','-c:v','libx264','-pix_fmt','yuv420p','-crf','18','-c:a','aac','-b:a','192k','-shortest','game_pov.mp4'],stdin=subprocess.PIPE)
for f in range(N):
    fr=np.frombuffer(rd.stdout.read(W*H*3),np.uint8).reshape(H,W,3);t=f/fps
    # look-around intro: start looking left/up at the room, settle on the TV
    a=ss(min(1,max(0,(t-0.1)/1.0)))
    px=(1-a)*-60; py=(1-a)*-70; roll=(1-a)*-3
    # lean in toward the TV mid-video, back a bit at the end
    lean=ss(min(1,max(0,(t-3.2)/1.2)))-0.5*ss(min(1,max(0,(t-6.6)/1.0)))
    z=1.22+0.16*lean
    # handheld / breathing sway + walk-like head bob
    px+=10*math.sin(t*1.1)+5*math.sin(t*2.7+1)
    py+=8*math.sin(t*1.6+0.5)+4*abs(math.sin(t*math.pi*1.8))
    roll+=1.2*math.sin(t*0.8)+0.5*math.sin(t*2.1)
    # recoil kick on shots
    k=pulse(t,0.18)
    py+=-14*k; roll+=1.5*k*math.sin(f*1.7); z+=0.02*k
    cx,cy=W/2+px,H*0.42+py
    M=cv2.getRotationMatrix2D((cx,cy),roll,z)
    M[0,2]+=W/2-cx; M[1,2]+=H/2-cy
    o=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    # subtle vignette for POV feel
    if f==0:
        yy,xx=np.mgrid[0:H,0:W];v=1-0.35*(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/2;v=np.clip(v,0,1)[...,None]
    wr.stdin.write((o*v).astype(np.uint8).tobytes())
wr.stdin.close();wr.wait();print('ok')
