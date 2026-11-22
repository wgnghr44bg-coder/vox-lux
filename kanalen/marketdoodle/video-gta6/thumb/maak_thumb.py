"""Thumbnails Market Doodle video 1 (22 nov 2026): titel bovenaan, bon links, geschrokken figuur rechts. python thumb/maak_thumb.py"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W,H=1280,720
FH="C:/Windows/Fonts/segoeprb.ttf"; FX="C:/Windows/Fonts/impact.ttf"
RO=(214,32,39); GR=(30,150,70)
def bon(rows, w=430, rh=70):
    h=100+rh*len(rows)+100
    im=Image.new("RGBA",(w,h+30),(0,0,0,0)); d=ImageDraw.Draw(im)
    zig=[(x,h if (x//22)%2==0 else h+20) for x in range(0,w+1,22)]
    d.polygon([(0,0),(w,0)]+zig[::-1],fill=(255,255,255,255))
    d.line([(0,0),(w,0)]+[(w,h)]+zig[::-1]+[(0,0)],fill=(30,30,30),width=5)
    d.text((26,48),"MY GTA VI receipt",font=ImageFont.truetype(FH,36),fill=(30,30,30),anchor="lm")
    y=110
    for lab,bed,kl,groot in rows:
        if groot: d.rounded_rectangle((10,y-38,w-10,y+38),radius=14,fill=(255,236,140))
        d.text((26,y),lab,font=ImageFont.truetype(FH,44 if groot else 40),fill=(30,30,30),anchor="lm")
        d.text((w-26,y),bed,font=ImageFont.truetype(FH,64 if groot else 50),fill=kl,anchor="rm"); y+=rh
    d.line([(26,y-28),(w-26,y-28)],fill=(30,30,30),width=4)
    d.text((26,y+16),"Paid",font=ImageFont.truetype(FH,42),fill=(30,30,30),anchor="lm")
    d.text((w-26,y+16),"$79.99",font=ImageFont.truetype(FH,50),fill=(30,40,120),anchor="rm")
    return im
def maak(naam, regels, rows):
    c=Image.new("RGB",(W,H),(255,255,255)); d=ImageDraw.Draw(c)
    y=6; ends=[]
    for tekst,kl,maat in regels:
        f=ImageFont.truetype(FX,maat); d.text((30,y),tekst,font=f,fill=kl); ends.append(d.textbbox((30,y),tekst,font=f)[2]); y+=maat+4
    b=bon(rows).rotate(4,expand=True,resample=Image.BICUBIC); s=0.82; b=b.resize((int(b.width*s),int(b.height*s)),Image.LANCZOS)
    sh=Image.new("RGBA",b.size,(0,0,0,0)); sh.paste((0,0,0,60),mask=b.split()[3]); sh=sh.filter(ImageFilter.GaussianBlur(8))
    y0=max(y+10, H-b.height+4); bx=110; c.paste(sh,(bx+12,y0+10),sh); c.paste(b,(bx,y0),b)
    lg=Image.open("logos/rockstar.png").convert("RGBA"); lg.thumbnail((96,96)); c.paste(lg,(ends[0]+20,14),lg)
    p=Image.open("afbeeldingen/p_schrik.png").convert("RGB"); r=560/p.height; p=p.resize((int(p.width*r),560),Image.LANCZOS)
    px=W-p.width-40; c.paste(p,(px,H-p.height))
    h=Image.open("afbeeldingen/hoes.png").convert("RGBA").resize((165,220),Image.LANCZOS).rotate(-10,expand=True,resample=Image.BICUBIC)
    c.paste(h,(px-130,H-h.height-12),h)
    c.save(f"thumb/{naam}.png")
maak("thumb-c",[("WHAT DID ROCKSTAR",(20,20,20),100),("GET FROM ME?",RO,100)],[("Store","~$24",RO,False),("Sony","~$12",RO,False),("Disc","~$4",RO,False),("Rockstar","$??",GR,True)])
maak("thumb-d",[("ROCKSTAR ONLY",(20,20,20),100),("GOT $40?!",RO,110)],[("Store","~$24",RO,False),("Sony","~$12",RO,False),("Disc","~$4",RO,False),("Rockstar","~$40",GR,True)])
maak("thumb-e",[("HOW MUCH DID ROCKSTAR",(20,20,20),92),("EARN FROM ME?",RO,104)],[("Store","~$24",RO,False),("Sony","~$12",RO,False),("Disc","~$4",RO,False),("Rockstar","$??",GR,True)])
