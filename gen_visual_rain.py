"""Ventana con lluvia sobre ciudad nocturna (bucle). uso: gen_visual_rain.py <seg> <out.mp4>"""
import sys,os,math,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFilter
SEC,OUT=int(sys.argv[1]),sys.argv[2]
W,H,FPS=1280,720,int(os.environ.get('VFPS',12)); NF=SEC*FPS; rng=np.random.default_rng(11)
bg=Image.new('RGB',(W,H),(9,13,26)); d=ImageDraw.Draw(bg)
for i in range(H): d.line([(0,i),(W,i)],fill=(int(9+14*i/H),int(13+16*i/H),int(26+30*i/H)))
cols=[(255,190,90),(255,140,80),(120,190,255),(255,230,170),(255,120,140),(150,255,200)]
lights=Image.new('RGB',(W,H),(0,0,0)); ld=ImageDraw.Draw(lights)
for _ in range(120):
    x,y=rng.integers(0,W),rng.integers(250,H); r=int(rng.integers(8,34)); c=cols[int(rng.integers(0,len(cols)))]
    k=float(rng.uniform(.25,.8)); ld.ellipse((x-r,y-r,x+r,y+r),fill=tuple(int(v*k) for v in c))
lights=lights.filter(ImageFilter.GaussianBlur(9))
base=np.clip(np.asarray(bg,np.float32)+np.asarray(lights,np.float32),0,255)
fogl=np.asarray(Image.fromarray((np.linspace(0,1,H)[:,None]*np.ones((H,W))*40).astype(np.uint8)),np.float32)[...,None]*np.array([.3,.4,.6])
base=np.clip(base+fogl,0,255)
nd=46; D=[(rng.uniform(20,W-20),rng.uniform(0,H),rng.uniform(4,8),int(rng.integers(1,3))) for _ in range(nd)]
ST=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(40,110),rng.uniform(180,420)) for _ in range(90)]
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf',os.environ.get('VCRF','30'),'-maxrate',os.environ.get('VMAX','70k'),'-bufsize','140k','-g',str(FPS*4),'-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for f in range(NF):
    ph=f/NF; fl=1+0.04*math.sin(2*math.pi*ph*3)
    im=Image.fromarray(np.clip(base*fl,0,255).astype(np.uint8)); dr=ImageDraw.Draw(im,'RGBA')
    for x,y0,l,sp in ST:
        yy=(y0+sp*SEC*ph*(FPS/FPS))%H; 
        dr.line([(x,yy),(x-l*.08,yy+l*.5)],fill=(190,210,240,50),width=1)
    for x,y0,r,k in D:
        y=(y0+H*k*ph)%H; w=math.sin(ph*2*math.pi*(k+1)+x)*3
        for t in range(1,18,3): dr.ellipse((x+w*0.3-r*.35,y-t*4-r*.35,x+w*0.3+r*.35,y-t*4+r*.35),fill=(200,220,245,22))
        dr.ellipse((x+w-r,y-r*1.3,x+w+r,y+r*1.3),fill=(215,230,250,70),outline=(255,255,255,110))
        dr.ellipse((x+w-r*.35,y-r*.8,x+w+r*.05,y-r*.3),fill=(255,255,255,170))
    p.stdin.write(np.asarray(im).tobytes())
p.stdin.close(); p.wait(); print('ok',OUT)
