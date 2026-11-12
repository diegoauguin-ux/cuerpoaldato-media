"""Lluvia sobre una ventana + truenos lejanos. uso: gen_rain.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10
class F:
    def __init__(s,kind,f):
        s.sos=butter(2,f,btype=kind,fs=SR,output='sos'); s.z=np.zeros((s.sos.shape[0],2))
    def __call__(s,x):
        y,s.z=sosfilt(s.sos,x,zi=s.z); return y
ev=[];t=rng.uniform(90,180)
while t<mins*60-20: ev.append((t,rng.uniform(9,14),rng.uniform(.5,1))); t+=rng.uniform(200,420)
def env(tt):
    e=np.zeros_like(tt)
    for t0,d,a in ev:
        x=tt-t0; m=x>0
        e[m]+=a*np.minimum(x[m]/1.6,1)**2*np.exp(-x[m]/(d/3))
    return e
fb=[(F('band',[500,5500]),F('band',[120,900]),F('band',[2500,6500]),F('low',110),F('band',[200,1200])) for _ in range(2)]
G=None; wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); tt=(np.arange(n)+c*CH)/SR
    slow=1+0.10*np.sin(2*np.pi*tt/37+1)+0.06*np.sin(2*np.pi*tt/91)
    chs=[]
    for k in range(2):
        a,b,d,th,thump=fb[k]
        bed=a(rng.standard_normal(n))*0.9+b(rng.standard_normal(n))*0.7
        imp=(rng.random(n)<70/SR)*rng.random(n)*14
        dr=d(imp)*1.2
        imp2=(rng.random(n)<3/SR)*rng.random(n)*40
        tp=thump(imp2)*1.0
        thun=th(rng.standard_normal(n))*env(tt)*9
        chs.append((bed*slow+dr+tp,thun))
    x=np.stack([chs[0][0],chs[1][0]],1)
    if G is None: G=0.13/(np.sqrt((x**2).mean())+1e-9)
    y=np.tanh((x*G+np.stack([chs[0][1],chs[1][1]],1)*G*0.9))
    f=int(3*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.8*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
