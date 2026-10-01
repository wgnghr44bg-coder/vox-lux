#!/usr/bin/env python3
"""Channel profile picture in the thumbnail logo style (crescent moon, night sky).

Run from the repo root: python3 tools/make_profile_picture.py
Writes branding/profielfoto-maan.png and branding/profielfoto-maan-tekst.png.
"""
import random
from PIL import Image, ImageDraw, ImageFilter, ImageFont
S=1024; MOON=(250,236,200); FONT="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def bg():
    im=Image.new("RGB",(S,S)); d=ImageDraw.Draw(im)
    for y in range(S):
        t=y/S; d.line([(0,y),(S,y)],fill=(int(14+30*t),int(16+14*t),int(44+30*t)))
    random.seed(4)
    for _ in range(140):
        x,y=random.randrange(S),random.randrange(S); r=random.choice([1,1,1,2,2,3]); a=random.randint(120,255)
        d.ellipse((x-r,y-r,x+r,y+r),fill=(a,a,min(255,a+10)))
    return im
def moon(im,cx,cy,r):
    glow=Image.new("L",im.size,0); ImageDraw.Draw(glow).ellipse((cx-r*1.35,cy-r*1.35,cx+r*1.35,cy+r*1.35),fill=80)
    im.paste(Image.new("RGB",im.size,(150,140,190)),(0,0),glow.filter(ImageFilter.GaussianBlur(r*0.45)))
    m=Image.new("L",im.size,0); md=ImageDraw.Draw(m)
    md.ellipse((cx-r,cy-r,cx+r,cy+r),fill=255)
    k=r/19; md.ellipse((cx-r+11*k,cy-r-5*k,cx+r+11*k,cy+r-5*k),fill=0)
    # sky behind the cut-out stays visible; paint moon
    im.paste(Image.new("RGB",im.size,MOON),(0,0),m.filter(ImageFilter.GaussianBlur(1.2)))
def text(im,y,size,s):
    d=ImageDraw.Draw(im); f=ImageFont.truetype(FONT,size); w=d.textlength(s,font=f)
    sh=Image.new("L",im.size,0); ImageDraw.Draw(sh).text(((S-w)/2,y),s,font=f,fill=255)
    im.paste(Image.new("RGB",im.size,(0,0,0)),(0,0),sh.filter(ImageFilter.GaussianBlur(8)).point(lambda v:int(v*.7)))
    d.text(((S-w)/2,y),s,font=f,fill=MOON)
a=bg(); moon(a,S//2+40,S//2,260); a.save("branding/profielfoto-maan.png")
b=bg(); moon(b,S//2+30,370,200); text(b,640,92,"SLEEP"); text(b,750,92,"ARCHIVES"); b.save("branding/profielfoto-maan-tekst.png")
# circle preview
prev=Image.new("RGB",(1100,560),(30,30,30))
for i,im in enumerate([a,b]):
    m=Image.new("L",(S,S),0); ImageDraw.Draw(m).ellipse((0,0,S,S),fill=255)
    c=im.copy(); prev.paste(c.resize((500,500)),(30+i*540,30),m.resize((500,500)))
prev.save("branding/profielfoto-maan-voorbeeld.jpg")
