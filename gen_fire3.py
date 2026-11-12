"""Fogata/chimenea profunda. uso: gen_fire3.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10; ML=SR  # 1 s events
def bp(lo,hi,x): return sosfilt(butter(2,[lo,hi],btype='band',fs=SR,output='sos'),x)
def pad(w): o=np.zeros(ML); o[:min(len(w),ML)]=w[:ML]; return o
def env(L,t): return np.exp(-np.arange(L)/(t*SR))*np.minimum(np.arange(L)/(0.0008*SR),1)
def tick():
    L=int(0.03*SR); return pad(bp(rng.uniform(500,1200),rng.uniform(2200,4200),rng.standard_normal(L))*env(L,rng.uniform(.002,.006)))
def crackle():
    o=np.zeros(ML); p=0; a=1.
    for _ in range(int(rng.integers(4,14))):
        L=int(0.04*SR); w=bp(rng.uniform(350,900),rng.uniform(1800,3500),rng.standard_normal(L))*env(L,rng.uniform(.003,.012))
        o[p:p+L]+=w*a; p+=int(rng.integers(.004*SR,.03*SR)); a*=rng.uniform(.7,1.0)
    return o
def snap():
    L=int(.12*SR); w=bp(150,1500,rng.standard_normal(L))*env(L,rng.uniform(.01,.03))*3
    t=np.arange(ML)/SR; th=np.sin(2*np.pi*rng.uniform(110,240)*t)*np.exp(-t/rng.uniform(.04,.09))*1.2
    return th+pad(w)
def thud():
    t=np.arange(ML)/SR; f=rng.uniform(55,95)
    return np.sin(2*np.pi*f*t*(1-0.15*t))*np.exp(-t/rng.uniform(.12,.25))*np.minimum(t/.004,1)*2
LIB={'tick':[tick() for _ in range(150)],'crk':[crackle() for _ in range(80)],'snap':[snap() for _ in range(40)],'thud':[thud() for _ in range(15)]}
AMP={'tick':(-1.3,.7,60.),'crk':(-.9,.6,4.),'snap':(-.5,.5,.5),'thud':(-.6,.4,.08)}
lo=[butter(4,200,btype='low',fs=SR,output='sos') for _ in range(2)]; lz=[np.zeros((2,2)) for _ in range(2)]
sg=butter(2,.3,btype='low',fs=SR,output='sos'); sz=np.zeros((1,2))
carry=[np.zeros(ML),np.zeros(ML)]; act=0.
wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); G=None
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); act=0.85*act+rng.normal(0,.4); m=float(np.exp(np.clip(act,-1,.8)))
    chs=[]
    for k in range(2):
        s=sosfilt(lo[k],rng.standard_normal(n)); 
        g,sz_=sosfilt(sg,rng.standard_normal(n),zi=np.zeros((1,2))) if False else (None,None)
        body=s*0.0035*m   # rumble grave muy suave
        buf=np.zeros(n+ML); buf[:ML]+=carry[k]
        for kind,(mu,sd,rate) in AMP.items():
            for _ in range(rng.poisson(rate*m*n/SR)):
                p=int(rng.integers(0,n)); buf[p:p+ML]+=LIB[kind][int(rng.integers(0,len(LIB[kind])))]*rng.lognormal(mu,sd)*0.2
        carry[k]=buf[n:n+ML].copy(); chs.append(body+buf[:n])
    x=np.stack(chs,1)
    if G is None: G=0.45/(np.percentile(np.abs(x),99.7)+1e-9)
    y=np.tanh(x*G)
    f=int(4*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.9*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
