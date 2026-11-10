"""Loop visual sin costuras (paisaje nocturno animado). uso: gen_visual.py <tema> <seg> <out.mp4>
temas: night | dawn | rain"""
import sys, math, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
theme,SEC,OUT=sys.argv[1],int(sys.argv[2]),sys.argv[3]
import os
W,H,FPS=1920,1080,int(os.environ.get("VFPS",24)); NF=SEC*FPS
DIM=float(os.environ.get("DIM",1)); SC=W/1920
rng=np.random.default_rng(7)
PAL={"night":((8,10,38),(40,32,90),(255,236,170)),"dawn":((30,24,70),(240,140,120),(255,220,160)),"rain":((12,18,30),(40,60,80),(200,220,255))}[theme]
top,bot,moonc=PAL
y=np.linspace(0,1,H,dtype=np.float32)[:,None,None]
sky=(np.array(top,np.float32)*(1-y)+np.array(bot,np.float32)*y)
sky=np.broadcast_to(sky,(H,W,3)).copy()
def ridge(base,amp,seed,col,n=6):
    r=np.random.default_rng(seed); x=np.arange(W)/W; h=np.zeros(W)
    for k in range(1,n+1): h+=r.uniform(0.3,1)/k*np.sin(2*np.pi*k*x*r.uniform(0.6,1.6)+r.uniform(0,6))
    h=base+amp*h/ n*2
    im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.polygon([(0,H)]+[(i,int(h[i])) for i in range(W)]+[(W,H)],fill=col+(255,))
    return im
bgim=Image.fromarray(sky.astype(np.uint8)).convert("RGBA")
cols=[(26,28,70),(18,20,52),(10,12,34)] if theme!="dawn" else [(110,70,120),(70,45,90),(30,22,50)]
for i,(b,a,s) in enumerate([(640,110,3),(740,90,9),(840,70,21)]):
    bgim=Image.alpha_composite(bgim,ridge(b,a,s,cols[i]))
base=np.array(bgim.convert("RGB"),np.float32)
# lago (reflejo suave abajo)
base[900:]=base[900:]*0.55+np.array(bot,np.float32)*0.25
STARS=[(rng.random()*W,rng.random()*560,rng.random()*1.6+0.6,rng.random()*6.28,int(rng.integers(1,4))) for _ in range(160)]
FF=[(rng.random()*W,600+rng.random()*380,rng.random()*6.28,int(rng.integers(1,3)),rng.random()*30+10) for _ in range(26)]
# niebla periódica
fog=np.array(Image.fromarray((rng.random((18,64))*255).astype(np.uint8)).resize((W*2,260),Image.BICUBIC).filter(ImageFilter.GaussianBlur(30)),np.float32)/255
mx,my=1500,170
yy_,xx_=np.mgrid[0:H,0:W]
glow=np.exp(-(((xx_-mx)**2+(yy_-my)**2)/(2*180**2))).astype(np.float32)
p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf",os.environ.get("VCRF","21"),"-maxrate",os.environ.get("VMAX","50000k"),"-bufsize",os.environ.get("VMAX","50000k"),"-g",str(FPS*4),"-pix_fmt","yuv420p","-movflags","+faststart","-vf",f"scale={os.environ.get('VW',1920)}:{os.environ.get('VH',1080)}",OUT],stdin=subprocess.PIPE)
for f in range(NF):
    ph=2*math.pi*f/NF
    fr=base.copy()
    fr+=glow[...,None]*np.array(moonc,np.float32)*(0.28+0.06*math.sin(ph*2))
    im=Image.fromarray(np.clip(fr,0,255).astype(np.uint8)); d=ImageDraw.Draw(im,"RGBA")
    d.ellipse((mx-48,my-48,mx+48,my+48),fill=moonc+(255,))
    for x,yv,r,pp,k in STARS:
        a=0.45+0.55*math.sin(ph*k+pp); rr=r*(0.7+0.5*a)
        d.ellipse((x-rr,yv-rr,x+rr,yv+rr),fill=(255,255,255,int(150+100*a)))
    for x,yv,pp,k,rad in FF:
        fx=x+rad*math.sin(ph*k+pp); fy=yv+rad*0.6*math.cos(ph*k*2+pp); a=0.5+0.5*math.sin(ph*3*k+pp)
        for rr,al in ((9,int(40*a)),(4,int(200*a))): d.ellipse((fx-rr,fy-rr,fx+rr,fy+rr),fill=(255,240,150,al))
    arr=np.asarray(im,np.float32)
    off=int(W*f/NF)  # una vuelta completa => bucle perfecto
    fg=np.roll(fog,-off,axis=1)[:, :W]
    win=np.sin(np.linspace(0,np.pi,260))[:,None]
    arr[560:820]+=(fg*win)[...,None]*np.array([40,44,70],np.float32)*0.55
    if theme=="rain":
        for _ in range(60):
            x=int(rng.integers(0,W)); y0=int(rng.integers(0,H-60)); arr[y0:y0+40,x:x+1]+=40
    p.stdin.write(np.clip(arr*DIM,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print("ok",OUT)
