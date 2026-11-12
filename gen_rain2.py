"""Lluvia natural y relajante (sin truenos). uso: gen_rain2.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10; ML=2400
class F:
    def __init__(s,kind,f,o=2):
        s.sos=butter(o,f,btype=kind,fs=SR,output='sos'); s.z=np.zeros((s.sos.shape[0],2))
    def __call__(s,x):
        y,s.z=sosfilt(s.sos,x,zi=s.z); return y
t=np.arange(ML)/SR
def drop(f,tau):
    w=np.sin(2*np.pi*f*t)*np.exp(-t/tau); w[:12]*=np.linspace(0,1,12); return w
DR=[drop(rng.uniform(1400,5200),rng.uniform(.0018,.007)) for _ in range(96)]
def bloop(f,tau):
    ff=f*(1+0.22*(1-np.exp(-t/0.012))); ph=2*np.pi*np.cumsum(ff)/SR
    w=np.sin(ph)*np.exp(-t/tau); w[:20]*=np.linspace(0,1,20); return w
BL=[bloop(rng.uniform(320,900),rng.uniform(.015,.035)) for _ in range(40)]
bands=[[F('low',320),F('band',[320,1600]),F('band',[1600,5200]),F('band',[5200,9500]),F('low',0.12)] for _ in range(2)]
gs=[F('low',0.09) for _ in range(2)]
carry=[np.zeros(ML),np.zeros(ML)]
wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
lam=70.; G=None
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); tt=(np.arange(n)+c*CH)/SR
    lam=float(np.clip(lam*np.exp(rng.normal(0,.25))+(70-lam)*.1,25,140))
    chs=[]
    for k in range(2):
        a,b,d,e,g=bands[k]; w=rng.standard_normal
        gust=1+0.22*np.tanh(g(w(n))*330)
        gust2=1+0.35*np.tanh(gs[k](w(n))*420)
        bed=a(w(n))*0.55*gust+b(w(n))*0.50*gust+d(w(n))*0.26*gust2+e(w(n))*0.045*gust2
        buf=np.zeros(n+ML); buf[:ML]+=carry[k]
        for _ in range(rng.poisson(lam*n/SR)):
            p=int(rng.integers(0,n)); buf[p:p+ML]+=DR[int(rng.integers(0,len(DR)))]*rng.lognormal(-2.0,0.7)
        for _ in range(rng.poisson(1.6*n/SR)):
            p=int(rng.integers(0,n)); buf[p:p+ML]+=BL[int(rng.integers(0,len(BL)))]*rng.lognormal(-2.3,0.5)
        carry[k]=buf[n:n+ML].copy(); chs.append(bed+buf[:n])
    x=np.stack(chs,1)
    if G is None: G=0.11/(np.sqrt((x**2).mean())+1e-9)
    y=np.tanh(x*G*1.2)/1.2
    f=int(4*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.9*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
