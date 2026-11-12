"""Fondo marrón cálido con polvo suspendido (bucle). uso: gen_visual_noise.py <seg> <out.mp4>"""
import sys,os,math,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFilter
SEC,OUT=int(sys.argv[1]),sys.argv[2]
W,H,FPS=1280,720,int(os.environ.get('VFPS',12)); NF=SEC*FPS; rng=np.random.default_rng(5)
yy,xx=np.mgrid[0:H,0:W].astype(np.float32); r=np.sqrt(((xx-W/2)/W*1.3)**2+((yy-H/2)/H)**2)
P=[(rng.uniform(0,W),rng.uniform(0,H),rng.uniform(1.2,3.6),int(rng.integers(1,3)),rng.uniform(0,6.28),rng.uniform(25,70)) for _ in range(110)]
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf',os.environ.get('VCRF','30'),'-maxrate',os.environ.get('VMAX','50k'),'-bufsize','100k','-g',str(FPS*4),'-pix_fmt','yuv420p','-movflags','+faststart',OUT],stdin=subprocess.PIPE)
for f in range(NF):
    ph=f/NF; glow=np.exp(-(r**2)/0.13)*(0.8+0.2*math.sin(2*math.pi*ph*2))
    a=np.stack([20+75*glow,11+42*glow,7+22*glow],-1)*(1-0.55*np.clip(r,0,1)[...,None])
    im=Image.fromarray(np.clip(a,0,255).astype(np.uint8)); dr=ImageDraw.Draw(im,'RGBA')
    for x,y0,s,k,pp,dev in P:
        y=(y0-H*k*ph)%H; x2=x+dev*math.sin(2*math.pi*ph*k+pp)
        al=int(70+60*math.sin(2*math.pi*ph*2*k+pp))
        dr.ellipse((x2-s,y-s,x2+s,y+s),fill=(255,205,150,al))
    p.stdin.write(np.asarray(im.filter(ImageFilter.GaussianBlur(.6))).tobytes())
p.stdin.close(); p.wait(); print('ok',OUT)
