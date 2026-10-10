"""Alteraqon kanaalbranding: profielfoto's (800x800) en banner (2560x1440, tekst in de veilige zone).

Gebruik (vanuit deze map): python3 make_branding.py   -> profielfoto-*.png, banner.png, banner-preview-*.png
Bronbeelden (xAI grok-imagine-image, prompts.txt) staan in bron/.
"""
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance
import numpy as np
GOLD=(242,200,128); FD="/usr/share/fonts/truetype/"
def font(name,size):
    import subprocess
    path=subprocess.run(["fc-match","-f","%{file}",name],capture_output=True,text=True).stdout
    return ImageFont.truetype(path,size)

def profile(src,out,margin=1.55):
    im=Image.open(src).convert("RGB"); a=np.asarray(im).astype(int).sum(2)
    ys,xs=np.where(a>90); cx,cy=(xs.min()+xs.max())/2,(ys.min()+ys.max())/2
    half=max(xs.max()-xs.min(),ys.max()-ys.min())/2*margin
    im=im.crop((int(cx-half),int(cy-half),int(cx+half),int(cy+half))).resize((800,800),Image.LANCZOS)
    im=ImageEnhance.Contrast(im).enhance(1.05); im.save(out)
    # voorbeeld zoals YouTube hem toont (rond)
    m=Image.new("L",(800,800),0); ImageDraw.Draw(m).ellipse((0,0,799,799),fill=255)
    prev=Image.new("RGB",(800,800),(255,255,255)); prev.paste(im,(0,0),m); return prev

def spaced(d,xy,text,f,fill,track):
    x,y=xy
    for ch in text:
        d.text((x,y),ch,font=f,fill=fill); x+=d.textlength(ch,font=f)+track
def spaced_w(d,text,f,track): return sum(d.textlength(c,font=f) for c in text)+track*(len(text)-1)

def banner():
    W,H=2560,1440
    im=Image.open("bron/banner.jpg").convert("RGB").resize((W,H),Image.LANCZOS)
    im=ImageEnhance.Color(im).enhance(0.8)
    # donkere band door het midden (veilige zone 1546x423) zodat de tekst leesbaar is
    sh=Image.new("L",(W,H),0); ImageDraw.Draw(sh).rectangle((0,H//2-260,W,H//2+260),fill=165)
    im.paste((8,10,14),(0,0),sh.filter(ImageFilter.GaussianBlur(120)))
    d=ImageDraw.Draw(im)
    big=font("Inter Display:light",150); tr=38; t="ALTERAQON"
    w=spaced_w(d,t,big,tr); spaced(d,((W-w)/2,H//2-120),t,big,(245,245,245),tr)
    small=font("Inter:semibold",38); tr2=14; t2="WHAT IF  ·  DOCUMENTARY SHORTS"
    w2=spaced_w(d,t2,small,tr2); spaced(d,((W-w2)/2,H//2+70),t2,small,GOLD,tr2)
    d.rectangle((W/2-130,H//2+48,W/2+130,H//2+52),fill=GOLD)
    im.save("banner.png")
    # previews: desktop (1546x423 midden) en mobiel (1546x423 is ook de mobiele zone)
    im.crop(((W-1546)//2,(H-423)//2,(W+1546)//2,(H+423)//2)).save("banner-preview-desktop.png")

for i in (1,2):
    profile(f"bron/icon{i}.jpg",f"profielfoto-{i}.png").save(f"profielfoto-{i}-rond.png")
banner()
