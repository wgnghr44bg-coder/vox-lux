"""Thumbnail Market Doodle video 2 (Claude-abonnement, 22 nov 2026). python thumb/maak_thumb.py"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1280,720
FH="C:/Windows/Fonts/segoeprb.ttf"; FX="C:/Windows/Fonts/impact.ttf"
RO=(214,32,39); GR=(30,150,70)
def bon(rows, w=440, rh=58):
    h=100+rh*len(rows)+100
    im=Image.new("RGBA",(w,h+30),(0,0,0,0)); d=ImageDraw.Draw(im)
    zig=[(x,h if (x//22)%2==0 else h+20) for x in range(0,w+1,22)]
    d.polygon([(0,0),(w,0)]+zig[::-1],fill=(255,255,255,255))
    d.line([(0,0),(w,0)]+[(w,h)]+zig[::-1]+[(0,0)],fill=(30,30,30),width=5)
    d.text((26,48),"MY CLAUDE receipt",font=ImageFont.truetype(FH,36),fill=(30,30,30),anchor="lm")
    y=110
    for lab,bed,kl,groot in rows:
        if groot: d.rounded_rectangle((10,y-34,w-10,y+34),radius=14,fill=(255,236,140))
        d.text((26,y),lab,font=ImageFont.truetype(FH,40 if groot else 34),fill=(30,30,30),anchor="lm")
        d.text((w-26,y),bed,font=ImageFont.truetype(FH,58 if groot else 42),fill=kl,anchor="rm"); y+=rh
    d.line([(26,y-24),(w-26,y-24)],fill=(30,30,30),width=4)
    d.text((26,y+16),"Paid",font=ImageFont.truetype(FH,40),fill=(30,30,30),anchor="lm")
    d.text((w-26,y+16),"$20.00",font=ImageFont.truetype(FH,48),fill=(30,40,120),anchor="rm")
    return im
def maak(naam, regels, rows):
    c=Image.new("RGB",(W,H),(255,255,255)); d=ImageDraw.Draw(c)
    y=6; ends=[]
    for tekst,kl,maat in regels:
        f=ImageFont.truetype(FX,maat); d.text((30,y),tekst,font=f,fill=kl); ends.append(d.textbbox((30,y),tekst,font=f)[2]); y+=maat+4
    b=bon(rows).rotate(4,expand=True,resample=Image.BICUBIC); s=0.8; b=b.resize((int(b.width*s),int(b.height*s)),Image.LANCZOS)
    sh=Image.new("RGBA",b.size,(0,0,0,0)); sh.paste((0,0,0,60),mask=b.split()[3]); sh=sh.filter(ImageFilter.GaussianBlur(8))
    y0=max(y+6, H-b.height+4); bx=110; c.paste(sh,(bx+12,y0+10),sh); c.paste(b,(bx,y0),b)
    lg=Image.open("logos/anthropic.png").convert("RGBA"); lg.thumbnail((330,60)); c.paste(lg,(min(ends[1]+30,W-lg.width-20),y-78),lg)
    p=Image.open("afbeeldingen/p_schrik.png").convert("RGB"); r=490/p.height; p=p.resize((int(p.width*r),490),Image.LANCZOS)
    px=W-p.width-40; c.paste(p,(px,H-p.height))
    c.save(f"thumb/{naam}.png"); c.save(f"thumb/thumbnail.jpg",quality=92)
maak("thumb-a",[("HOW MUCH DOES ANTHROPIC",(20,20,20),90),("MAKE FROM ME?",RO,104)],
     [("Computers","~$11.63",RO,False),("People","~$2.02",RO,False),("Sales","~$2.78",RO,False),("Charity","~$2.36",RO,False),("Anthropic","$??",GR,True)])
