"""Chimenea con leña crepitando. uso: gen_fire.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10; ML=3600
class F:
    def __init__(s,kind,f,o=2):
        s.sos=butter(o,f,btype=kind,fs=SR,output='sos'); s.z=np.zeros((s.sos.shape[0],2))
    def __call__(s,x):
        y,s.z=sosfilt(s.sos,x,zi=s.z); return y
hp=butter(2,1800,btype='high',fs=SR,output='sos')
def pad(w): o=np.zeros(ML); o[:len(w)]=w[:ML]; return o
def tick():
    L=int(rng.integers(30,110)); w=rng.standard_normal(L)*np.exp(-np.arange(L)/rng.uniform(6,28)); return pad(sosfilt(hp,w))
def crackle():
    o=np.zeros(ML); p=0; a=1.0
    for _ in range(int(rng.integers(3,11))):
        L=int(rng.integers(25,90)); w=sosfilt(hp,rng.standard_normal(L)*np.exp(-np.arange(L)/rng.uniform(5,20)))
        o[p:p+L]+=w*a; p+=int(rng.integers(40,260)); a*=rng.uniform(.6,1.0)
    return o
def pop():
    L=int(rng.uniform(.006,.014)*SR); w=sosfilt(hp,rng.standard_normal(L)*np.exp(-np.arange(L)/(L/4)))*1.4
    tt=np.arange(ML)/SR; th=np.sin(2*np.pi*rng.uniform(140,330)*tt)*np.exp(-tt/rng.uniform(.02,.05))*0.9
    o=th.copy(); o[:L]+=w; return o
def sizz():
    L=int(rng.uniform(.12,.35)*SR); tt=np.arange(L)/SR
    b=butter(2,[rng.uniform(2800,4500),rng.uniform(7000,10500)],btype='band',fs=SR,output='sos')
    w=sosfilt(b,rng.standard_normal(L))*np.minimum(tt/.01,1)*np.exp(-tt/rng.uniform(.04,.1)); return pad(w)
LIB={'tick':[tick() for _ in range(120)],'crk':[crackle() for _ in range(60)],'pop':[pop() for _ in range(30)]}
AMP={'tick':(-1.1,.6,10.),'crk':(-0.8,.6,2.6),'pop':(-.2,.5,.30)}
bands=[(F('low',110,4),None,F('low',0.15),None) for _ in range(2)]
carry=[np.zeros(ML),np.zeros(ML)]; act=0.
wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); G=None
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); act=0.85*act+rng.normal(0,.45); m=float(np.exp(np.clip(act,-1.2,1.2)))
    chs=[]
    for k in range(2):
        lo,mid,g1,g2=bands[k]; w=rng.standard_normal
        fl=1+0.4*np.tanh(g1(w(n))*260)
        bed=lo(w(n))*0.05*fl
        buf=np.zeros(n+ML); buf[:ML]+=carry[k]
        for kind,(mu,sg,rate) in AMP.items():
            for _ in range(rng.poisson(rate*m*n/SR/(1 if kind=='tick' else 1))):
                p=int(rng.integers(0,n)); wv_=LIB[kind][int(rng.integers(0,len(LIB[kind])))]
                buf[p:p+ML]+=wv_*rng.lognormal(mu,sg)*0.25
        carry[k]=buf[n:n+ML].copy(); chs.append(bed+buf[:n])
    x=np.stack(chs,1)
    if G is None: G=0.5/(np.percentile(np.abs(x),99.5)+1e-9)
    y=np.tanh(x*G*1.1)/1.1
    f=int(4*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.9*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
