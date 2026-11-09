import json, math, random, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
import numpy as np
W,H,FPS=1080,1920,30
TIM,AUD,OUT=sys.argv[1],sys.argv[2],sys.argv[3]
BEATS=json.load(open(sys.argv[4]))
T=json.load(open(TIM)); DUR=T[-1]["end"]+0.4
F=lambda n,s: ImageFont.truetype(f"/usr/share/fonts/opentype/inter/Inter-{n}.otf",s)
f_sub=F("Black",80); f_m=F("Bold",46); f_s=F("Bold",36)
OL=(40,24,64); WH=(255,255,255); YL=(255,214,10); PK=(255,105,150); CY=(0,229,255); GR=(70,220,130); RD=(255,82,104); SK=(255,205,170)
def ease(x): x=max(0,min(1,x)); return 1-(1-x)**3
def back(x):
    x=max(0,min(1,x)); c=1.7; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def pop(sp,dl=0,du=0.45): return back((sp-dl)/du)
def ctext(d,x,y,s,font,fill=WH,st=0,sf=OL): d.text((x,y),s,font=font,fill=fill,anchor="mm",stroke_width=st,stroke_fill=sf)
def E(d,x,y,rx,ry,fill=None,ol=OL,w=6):
    rx=max(0.5,rx); ry=max(0.5,ry); d.ellipse((x-rx,y-ry,x+rx,y+ry),fill=fill,outline=ol,width=w)
def R(d,x0,y0,x1,y1,r=20,fill=None,ol=OL,w=6): d.rounded_rectangle((x0,y0,x1,y1),r,fill=fill,outline=ol,width=w)
# ---------- background ----------
yy=np.linspace(0,1,H,dtype=np.float32)[:,None,None]
def bg(top,bot):
    a=np.array(top,dtype=np.float32); b=np.array(bot,dtype=np.float32)
    return Image.fromarray(np.broadcast_to(a*(1-yy)+b*yy,(H,W,3)).astype(np.uint8))
BGS={}
def getbg(k,top,bot):
    if k not in BGS: BGS[k]=bg(top,bot)
    return BGS[k].copy()
rnd=random.Random(5); STARS=[(rnd.random()*W,rnd.random()*1500,rnd.random()*2+1.5,rnd.random()*6) for _ in range(46)]
def stars(d,t,col=(200,205,255)):
    for x,y,r,ph in STARS:
        a=0.5+0.5*math.sin(t*2+ph); rr=r*(0.6+0.6*a); d.ellipse((x-rr,y-rr,x+rr,y+rr),fill=col)
# ---------- people & objects ----------
def person(d,cx,cy,s=1.0,mood="normal",t=0,hood=(255,120,90),tilt=0,arms=None):
    ox=math.sin(tilt)*40*s
    R(d,cx-120*s+ox,cy+90*s,cx+120*s+ox,cy+400*s,int(50*s),hood)
    if arms=="wave":
        a=math.sin(t*9)*0.4; R(d,cx+110*s,cy+120*s,cx+170*s,cy+300*s,25,hood)
        x0,y0=cx-110*s,cy+140*s; d.line((x0,y0,x0-90*s,y0-110*s-math.sin(t*9)*40*s),fill=hood,width=int(52*s)); E(d,x0-95*s,y0-120*s-math.sin(t*9)*40*s,34*s,34*s,SK)
    elif arms=="hold": pass
    else:
        R(d,cx-175*s+ox,cy+120*s,cx-105*s+ox,cy+330*s,int(30*s),hood); R(d,cx+105*s+ox,cy+120*s,cx+175*s+ox,cy+330*s,int(30*s),hood)
    hx,hy=cx+ox*0.6,cy
    E(d,hx,hy,125*s,135*s,SK)
    d.pieslice((hx-135*s,hy-150*s,hx+135*s,hy+60*s),180,360,fill=(60,40,50),outline=OL,width=6)
    for sg in(-1,1):
        x=hx+sg*52*s; y=hy+12*s
        if mood in("tired","sleep"):
            if mood=="sleep": d.arc((x-30*s,y-10*s,x+30*s,y+30*s),0,180,fill=OL,width=7)
            else:
                E(d,x,y,30*s,26*s,WH,OL,5); E(d,x+3*s,y+4*s,13*s,13*s,OL,OL,1)
                d.pieslice((x-31*s,y-27*s,x+31*s,y+27*s),180,360,fill=(245,185,150),outline=OL,width=5)
                d.arc((x-34*s,y+10*s,x+34*s,y+55*s),20,160,fill=(120,80,150),width=int(9*s))
        elif mood=="swirl":
            E(d,x,y,34*s,34*s,WH,OL,5)
            pts=[(x+math.cos(a*3+t*8)*a*3.2*s,y+math.sin(a*3+t*8)*a*3.2*s) for a in [i/10 for i in range(0,50)]]
            d.line(pts,fill=OL,width=4)
        elif mood=="happy":
            d.arc((x-30*s,y-20*s,x+30*s,y+30*s),200,340,fill=OL,width=8)
        else:
            E(d,x,y,30*s,34*s,WH,OL,5); E(d,x+3*s,y+2*s,14*s,16*s,OL,OL,1)
    # cheeks + mouth
    for sg in(-1,1): E(d,hx+sg*85*s,hy+62*s,22*s,13*s,(255,150,150),None,0)
    my=hy+80*s
    if mood in("tired","swirl"): d.arc((hx-35*s,my-5*s,hx+35*s,my+35*s),200,340,fill=OL,width=7)
    elif mood=="sleep": E(d,hx,my+8*s,15*s,12*s,(120,40,70),OL,4)
    elif mood=="shock": E(d,hx,my+10*s,24*s,32*s,(120,40,70),OL,5)
    else: d.arc((hx-40*s,my-30*s,hx+40*s,my+30*s),20,160,fill=OL,width=8)
def brain(d,cx,cy,s=1.0,t=0,mood="happy",tint=(255,160,200)):
    for x,y,r in((-70,20,88),(70,20,88),(0,-50,92),(0,60,86)): E(d,cx+x*s,cy+y*s,r*s,r*s,tint,OL,7)
    for x,y,r in((-70,20,81),(70,20,81),(0,-50,85),(0,60,79)): E(d,cx+x*s,cy+y*s,r*s,r*s,tint,None,0)
    d.arc((cx-110*s,cy-90*s,cx-5*s,cy-5*s),200,320,fill=(210,110,160),width=int(7*s)); d.arc((cx+5*s,cy-90*s,cx+110*s,cy-5*s),220,340,fill=(210,110,160),width=int(7*s))
    for sg in(-1,1):
        x=cx+sg*38*s; E(d,x,cy+10*s,22*s,26*s,WH,OL,4); E(d,x+2*s,cy+13*s,10*s,12*s,OL,OL,1)
    if mood=="sad": d.arc((cx-28*s,cy+55*s,cx+28*s,cy+95*s),200,340,fill=OL,width=6)
    else: d.arc((cx-30*s,cy+35*s,cx+30*s,cy+80*s),20,160,fill=OL,width=6)
def clock(d,cx,cy,r,hours,t=0,col=WH):
    E(d,cx,cy,r,r,col,OL,8)
    for k in range(12):
        a=k*math.tau/12; d.line((cx+math.sin(a)*r*0.82,cy-math.cos(a)*r*0.82,cx+math.sin(a)*r*0.92,cy-math.cos(a)*r*0.92),fill=OL,width=5)
    a=hours/12*math.tau; d.line((cx,cy,cx+math.sin(a)*r*0.5,cy-math.cos(a)*r*0.5),fill=OL,width=10)
    b=hours*math.tau; d.line((cx,cy,cx+math.sin(b)*r*0.75,cy-math.cos(b)*r*0.75),fill=RD,width=6)
def moon(d,cx,cy,r,col=(255,236,150)):
    E(d,cx,cy,r,r,col,OL,7); E(d,cx+r*0.45,cy-r*0.2,r*0.85,r*0.85,(22,26,80),None,0)
    d.arc((cx-r,cy-r,cx+r,cy+r),90,270,fill=OL,width=7)
def bed(d,cx,cy,s=1.0):
    R(d,cx-330*s,cy,cx+330*s,cy+120*s,30,(110,90,200)); R(d,cx-330*s,cy-40*s,cx-290*s,cy+210*s,10,(90,70,160)); R(d,cx+290*s,cy+60*s,cx+330*s,cy+210*s,10,(90,70,160))
    R(d,cx-300*s,cy-30*s,cx-150*s,cy+30*s,25,(235,235,255))
def label(d,cx,cy,txt,col=YL,font=None,bgc=(20,22,60),w=None):
    font=font or f_m; tw=d.textlength(txt,font=font)+60
    R(d,cx-tw/2,cy-44,cx+tw/2,cy+44,30,bgc,col,6); ctext(d,cx,cy,txt,font,col)
def bar(d,x,y,w,h,v,col,txt):
    R(d,x,y,x+w,y+h,h//2,(30,32,80),WH,4)
    if v>0.02: R(d,x,y,x+max(h,w*v),y+h,h//2,col,OL,4)
    d.text((x,y-26),txt,font=f_s,fill=WH,anchor="ls")
def donut(d,cx,cy,r):
    E(d,cx,cy,r,r,(230,160,90),OL,6); E(d,cx,cy,r*0.35,r*0.35,(40,24,64),OL,5)
    for a in range(0,360,60):
        x=cx+math.cos(math.radians(a))*r*0.68; y=cy+math.sin(math.radians(a))*r*0.68; d.rectangle((x-9,y-3,x+9,y+3),fill=[PK,CY,YL][a//60%3])
def pizza(d,cx,cy,r):
    d.polygon([(cx-r,cy-r*0.8),(cx+r,cy-r*0.8),(cx,cy+r)],fill=(255,200,70),outline=OL,width=6)
    for x,y in((-r*0.4,-r*0.4),(r*0.3,-r*0.5),(0,r*0.1)): E(d,cx+x,cy+y,r*0.16,r*0.16,RD,OL,3)
def virus(d,cx,cy,r,t=0):
    for k in range(10):
        a=k*math.tau/10+t; d.line((cx+math.cos(a)*r*0.8,cy+math.sin(a)*r*0.8,cx+math.cos(a)*r*1.3,cy+math.sin(a)*r*1.3),fill=OL,width=6); E(d,cx+math.cos(a)*r*1.3,cy+math.sin(a)*r*1.3,r*0.17,r*0.17,GR,OL,4)
    E(d,cx,cy,r,r,(120,230,120),OL,6)
    for sg in(-1,1): E(d,cx+sg*r*0.35,cy-r*0.1,r*0.22,r*0.26,WH,OL,3); E(d,cx+sg*r*0.35,cy-r*0.05,r*0.1,r*0.12,OL,OL,1)
    d.arc((cx-r*0.4,cy+r*0.1,cx+r*0.4,cy+r*0.6),200,340,fill=OL,width=5)
def shield(d,cx,cy,s,crack=0):
    pts=[(cx-110*s,cy-120*s),(cx+110*s,cy-120*s),(cx+110*s,cy+20*s),(cx,cy+140*s),(cx-110*s,cy+20*s)]
    d.polygon(pts,fill=CY,outline=OL,width=8); d.line((cx,cy-90*s,cx,cy+90*s),fill=WH,width=8); d.line((cx-70*s,cy-20*s,cx+70*s,cy-20*s),fill=WH,width=8)
    if crack>0:
        c=[(cx+30*s,cy-120*s),(cx+5*s,cy-50*s),(cx+50*s,cy),(cx-10*s,cy+60*s)]; d.line(c[:1+int(crack*3)+1],fill=OL,width=9)
def phone(d,cx,cy,s,on=True,text=None):
    R(d,cx-80*s,cy-150*s,cx+80*s,cy+150*s,int(26*s),(30,30,50) if not on else (40,40,70),WH,6)
    R(d,cx-68*s,cy-130*s,cx+68*s,cy+120*s,int(14*s),(100,200,255) if on else (15,15,25),None,0)
def book(d,cx,cy,s):
    R(d,cx-110*s,cy-80*s,cx+110*s,cy+80*s,10,(255,120,90),OL,7); d.line((cx,cy-80*s,cx,cy+80*s),fill=OL,width=6)
    for k in range(3): d.line((cx-90*s,cy-40*s+k*30*s,cx-20*s,cy-40*s+k*30*s),fill=WH,width=5); d.line((cx+20*s,cy-40*s+k*30*s,cx+90*s,cy-40*s+k*30*s),fill=WH,width=5)
def car(d,cx,cy,s,t):
    R(d,cx-200*s,cy-40*s,cx+200*s,cy+60*s,30,(255,90,90)); R(d,cx-110*s,cy-120*s,cx+110*s,cy-30*s,30,(255,90,90))
    R(d,cx-90*s,cy-105*s,cx+90*s,cy-40*s,15,(170,230,255),OL,5)
    for sx in(-110,110): E(d,cx+sx*s,cy+65*s,42*s,42*s,(40,40,60),OL,6); E(d,cx+sx*s,cy+65*s,16*s,16*s,(190,190,210),OL,3)
def zzz(d,x,y,t,s=1.0):
    for k in range(3):
        u=(t*0.5+k/3)%1; ctext(d,x+k*40*s+u*30,y-u*140-k*30,"Z",F("Black",int((50+k*16)*s)),CY,4)
def cloudfog(d,cx,cy,w,a=1.0):
    for k in range(7):
        x=cx-w/2+k*w/6; y=cy+math.sin(k*1.7)*20; E(d,x,y,w*0.14,w*0.09,(210,215,235),None,0)
# ---------- new props ----------
COL={"RD":RD,"GR":GR,"YL":YL,"CY":CY,"PK":PK}
def stomach_p(d,cx,cy,s):
    R(d,cx+10*s,cy-130*s,cx+60*s,cy-30*s,int(20*s),(70,205,205)); E(d,cx,cy+20*s,120*s,105*s,(70,205,205),OL,7)
    for sg in(-1,1): E(d,cx+sg*38*s,cy+5*s,16*s,20*s,WH,OL,4); E(d,cx+sg*38*s+2,cy+8*s,7*s,9*s,OL,OL,1)
    d.arc((cx-30*s,cy+35*s,cx+30*s,cy+80*s),20,160,fill=OL,width=6)
def glass_p(d,cx,cy,s,t=0):
    d.polygon([(cx-70*s,cy-110*s),(cx+70*s,cy-110*s),(cx+52*s,cy+110*s),(cx-52*s,cy+110*s)],fill=(190,235,255),outline=OL,width=7)
    wy=cy-40*s+math.sin(t*3)*4; d.polygon([(cx-62*s,wy),(cx+62*s,wy),(cx+52*s,cy+104*s),(cx-52*s,cy+104*s)],fill=(70,170,255))
def bulb_p(d,cx,cy,s,t=0):
    for k in range(10):
        a=k*math.tau/10; d.line((cx+math.cos(a)*105*s,cy-20*s+math.sin(a)*105*s,cx+math.cos(a)*(140+8*math.sin(t*5+k))*s,cy-20*s+math.sin(a)*(140+8*math.sin(t*5+k))*s),fill=YL,width=6)
    E(d,cx,cy-20*s,85*s,85*s,(255,236,120),OL,7); R(d,cx-40*s,cy+55*s,cx+40*s,cy+110*s,10,(160,160,190))
def cell_p(d,cx,cy,s):
    E(d,cx,cy,105*s,105*s,(90,235,155),OL,7); E(d,cx+40*s,cy+40*s,32*s,32*s,(255,205,60),OL,5)
    for sg in(-1,1): E(d,cx+sg*34*s-10*s,cy-15*s,16*s,20*s,WH,OL,4); E(d,cx+sg*34*s-8*s,cy-12*s,7*s,9*s,OL,OL,1)
    d.arc((cx-36*s,cy+5*s,cx+14*s,cy+45*s),20,160,fill=OL,width=6)
def drop_p(d,cx,cy,s):
    d.polygon([(cx,cy-110*s),(cx+75*s,cy+30*s),(cx-75*s,cy+30*s)],fill=(70,170,255),outline=OL,width=7); E(d,cx,cy+35*s,75*s,70*s,(70,170,255),OL,7)
    d.polygon([(cx-5*s,cy-100*s),(cx+68*s,cy+28*s),(cx-68*s,cy+28*s)],fill=(70,170,255))
    for sg in(-1,1): E(d,cx+sg*28*s,cy+25*s,11*s,14*s,WH,OL,3)
def prop(d,nm,x,y,s,t=0):
    if s<=0.02: return
    if nm=="stomach": stomach_p(d,x,y,s)
    elif nm=="glass": glass_p(d,x,y,s,t)
    elif nm=="bulb": bulb_p(d,x,y,s,t)
    elif nm=="cell": cell_p(d,x,y,s)
    elif nm=="drop": drop_p(d,x,y,s)
    elif nm=="shield": shield(d,x,y,1.0*s)
    elif nm=="virus": virus(d,x,y,80*s,t)
    elif nm=="brain": brain(d,x,y,0.9*s,t)
    elif nm=="phone": phone(d,x,y,1.0*s,True)
    elif nm=="clock": clock(d,x,y,100*s,5,t)
    elif nm=="moon": moon(d,x,y,100*s)
def wrapw(d,txt,font,maxw):
    out=[];cur=""
    for w in txt.split():
        n=(cur+" "+w).strip()
        if d.textlength(n,font=font)>maxw and cur: out.append(cur);cur=w
        else: cur=n
    return out+[cur]
def scene(im,d,si,sp,t,dur):
    b=BEATS[min(si,len(BEATS)-1)]; cx=540; ty=b["t"]
    stars(d,t)
    if ty=="hook":
        pop_=pop(sp,0.1); prop(d,b["prop"],cx,1000,1.6*pop_ if False else 1.5*pop_,t)
        person(d,cx,560,0.8,b.get("mood","shock"),t) if False else None
        label(d,cx,330,b["label"],YL,f_m)
        # person peeking
        person(d,cx+300,640,0.7,b.get("mood","shock"),t)
    elif ty=="stat":
        P_=pop(sp,0.05)
        for k in range(8):
            a=sp*0.8+k*math.tau/8; prop(d,b["prop"],cx+math.cos(a)*400,820+math.sin(a)*330,0.35,t)
        prop(d,b["prop"],cx,820,1.35*P_,t)
        ctext(d,cx,1250,b["big"],F("Black",b.get("size",150)),YL,8)
        label(d,cx,330,b["label"],CY,f_m)
    elif ty=="bars":
        a=ease(sp/1.8); y=640
        for i,(lab,v,c) in enumerate(b["bars"]):
            bar(d,140,y+i*300,800,80,v*a,COL[c],lab)
        label(d,cx,330,b["label"],YL,f_m)
        person(d,cx,1250,0.5,"happy",t)
    elif ty=="stamp":
        R(d,110,560,970,980,40,(30,34,100),WH,7)
        ls=wrapw(d,b["claim"],F("Black",64),740)
        for i,l in enumerate(ls): ctext(d,cx,690+i*84,l,F("Black",64),WH,3)
        p=pop(sp,1.4,0.35)
        if p>0.02:
            col=COL[b["vcol"]]; w=int(300*p)
            R(d,cx-w,830-int(60*p),cx+w,830+int(60*p),12,None,col,12) if False else None
            im2=Image.new("RGBA",(900,220),(0,0,0,0)); dd=ImageDraw.Draw(im2); dd.rounded_rectangle((10,10,890,210),24,outline=col,width=14); dd.text((450,110),b["verdict"],font=F("Black",92),fill=col,anchor="mm")
            im2=im2.rotate(-8,expand=True,resample=Image.BICUBIC); sc=max(0.05,p); im2=im2.resize((int(im2.width*sc),int(im2.height*sc)))
            im.paste(im2,(int(cx-im2.width/2),int(1130-im2.height/2)),im2)
        label(d,cx,330,"¿MITO O REALIDAD?",YL,f_m)
    elif ty=="cards":
        for k,(txt,pr) in enumerate(b["cards"]):
            p=pop(sp,0.2+k*0.9); y=560+k*320
            if p>0.05:
                x0=540-440*min(1,p); R(d,x0,y-120,1080-x0,y+120,40,(30,34,100),[CY,YL,PK][k],7)
                prop(d,pr,230,y,0.55,t)
                if p>0.8:
                    for i,l in enumerate(wrapw(d,txt,f_s,520)): ctext(d,650,y-(len(wrapw(d,txt,f_s,520))-1)*22+i*44,l,f_s,WH,2)
        label(d,cx,330,b["label"],YL,F("Black",60))
    else:
        person(d,cx,700,1.15,"happy",t,arms="wave")
        label(d,cx,330,b["label"],YL,f_m)
        R(d,140,1230,940,1380,50,(30,34,100),CY,6); ctext(d,cx,1305,"SÍGUEME  @cuerpoaldato",f_m,CY)
# ---------- subtitles ----------
words=[]
for i,s in enumerate(T):
    ws=s["text"].split(); wt=[len(w)+1 for w in ws]; tot=sum(wt); t0=s["start"]
    for w,x in zip(ws,wt):
        dd=(s["end"]-s["start"])*x/tot; words.append((w,t0,t0+dd,i)); t0+=dd
chunks=[]; i=0
while i<len(words):
    j=i
    while j+1<len(words) and words[j+1][3]==words[i][3] and j-i<3 and not words[j][0].endswith((".","?",":")): j+=1
    chunks.append((i,j)); i=j+1
frames=int(min(DUR,float(os.environ.get("LIMIT","999")))*FPS)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",AUD,"-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p","-c:a","aac","-b:a","160k","-shortest","-movflags","+faststart",OUT],stdin=subprocess.PIPE)
THEMES=[((34,28,110),(12,10,44))]*11+[((60,30,120),(14,10,50))]
for fr in range(frames):
    t=fr/FPS
    si=next((k for k,s in enumerate(T) if t<s["end"]+0.18),len(T)-1); sp=t-T[si]["start"]; dur=T[si]["end"]-T[si]["start"]
    top,bot=THEMES[min(si,len(THEMES)-1)]
    im=getbg(si%2,top,bot) if False else getbg(("b",si),top,bot)
    d=ImageDraw.Draw(im)
    scene(im,d,si,max(0,sp),t,dur)
    # zoom (push-in) on scene area
    z=1+0.06*min(1,max(0,sp)/max(dur,1))
    cw,ch=W/z,H/z; box=(int((W-cw)/2),int((H-ch)/2),int((W+cw)/2),int((H+ch)/2))
    im=im.crop(box).resize((W,H),Image.BILINEAR); d=ImageDraw.Draw(im)
    if sp<0.18: im=Image.blend(Image.new("RGB",(W,H),(10,8,30)),im,ease(sp/0.18)); d=ImageDraw.Draw(im)
    ctext(d,540,150,"CUERPO AL DATO",f_m,YL)
    d.rectangle((60,200,60+960*min(1,t/DUR),210),fill=YL)
    wi=next((k for k,w in enumerate(words) if t<w[2]),len(words)-1)
    a,b=next(c for c in chunks if c[0]<=wi<=c[1])
    cw_=[words[k][0].upper() for k in range(a,b+1)]; tw=[d.textlength(w+" ",font=f_sub) for w in cw_]
    rows=[(cw_[:len(cw_)//2],tw[:len(cw_)//2]),(cw_[len(cw_)//2:],tw[len(cw_)//2:])] if sum(tw)>980 else [(cw_,tw)]
    idx=a
    for r,(rw,rt) in enumerate(rows):
        x=540-sum(rt)/2
        for w,wd in zip(rw,rt):
            d.text((x,1560+r*100),w,font=f_sub,fill=YL if idx==wi else WH,anchor="lm",stroke_width=9,stroke_fill=(0,0,0)); x+=wd; idx+=1
    p.stdin.write(im.tobytes())
p.stdin.close(); p.wait(); print("done",OUT,round(DUR,1))
