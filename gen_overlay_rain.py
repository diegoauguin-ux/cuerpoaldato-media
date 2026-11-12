"""overlay de lluvia en bucle (negro + rayas). uso: gen_overlay_rain.py <seg> <out.mp4>"""
import sys,os,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFilter
SEC,OUT=int(sys.argv[1]),sys.argv[2]
W,H,FPS=1280,720,12; NF=SEC*FPS; rng=np.random.default_rng(5)
def layer(n,k,L,br,wd):
    return [(rng.uniform(0,W),rng.uniform(0,H),k,L,br,wd) for _ in range(n)]
P=layer(260,6,34,150,1)+layer(120,12,60,215,1)+layer(30,17,90,255,2)
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','gray','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p',OUT],stdin=subprocess.PIPE)
for f in range(NF):
    ph=f/NF; im=Image.new('L',(W,H),0); dr=ImageDraw.Draw(im)
    for x,y0,k,L,br,wd in P:
        y=(y0+H*k*ph)%H; xx=x-0.25*(y-y0)*0+ (y*0.18)
        xx=(x+y*0.18)%W
        dr.line([(xx,y),(xx-L*0.18,y-L)],fill=int(br),width=wd)
    p.stdin.write(im.filter(ImageFilter.GaussianBlur(0.7)).tobytes())
p.stdin.close(); p.wait()
