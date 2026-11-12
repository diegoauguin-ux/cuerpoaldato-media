"""Campo soleado: pajaros, insectos, abejas (sin viento). uso: gen_meadow.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import butter,sosfilt,fftconvolve
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10; ML=SR*5
def lp(f): return butter(2,f,btype='low',fs=SR,output='sos')
LPS={0:lp(9500),1:lp(6500),2:lp(4200)}
def synth(f,amps=(1,.28,.08)):
    ph=2*np.pi*np.cumsum(f)/SR; y=np.zeros_like(f)
    for h,a in enumerate(amps,1): y+=a*np.sin(h*ph)*(h*f<14500)
    return y
def env(n,att=.15,rel=.5):
    e=np.sin(np.linspace(0,np.pi,n))**2; return e
def note(f0,f1,dur,curve=1.0,amps=(1,.28,.08)):
    n=int(dur*SR); x=np.linspace(0,1,n)**curve; f=f0+(f1-f0)*x
    f=f*(1+0.012*np.sin(2*np.pi*np.linspace(0,dur,n)*rng.uniform(20,40))); return synth(f,amps)*env(n)
def silence(d): return np.zeros(int(d*SR))
def tweet():
    f0=rng.uniform(2300,5200); parts=[]
    for _ in range(int(rng.integers(2,7))):
        d=rng.uniform(.06,.16); up=rng.random()<.5; f1=f0*(rng.uniform(1.15,1.5) if up else rng.uniform(.65,.9))
        parts+= [note(f0,f1,d,rng.uniform(.7,1.4))*rng.uniform(.6,1), silence(rng.uniform(.05,.2))]
        f0=float(np.clip(f0*rng.uniform(.9,1.1),2000,5600))
    return np.concatenate(parts)
def trill():
    f=rng.uniform(3000,5000); parts=[]; n=int(rng.integers(8,24)); d=rng.uniform(.022,.04)
    for i in range(n): parts+=[note(f*(1+.012*i),f*(1+.012*i)*rng.uniform(.9,1.1),d)*(1-.3*i/n), silence(d*rng.uniform(.3,.7))]
    return np.concatenate(parts)
def warble():
    dur=rng.uniform(1.0,2.6); n=int(dur*SR); t=np.arange(n)/SR; fc=rng.uniform(2400,4300)
    fm=rng.uniform(5,12)+3*np.sin(2*np.pi*t*rng.uniform(.4,1.2)); dev=rng.uniform(600,1400)
    f=fc+dev*np.sin(2*np.pi*np.cumsum(fm)/SR)+300*np.sin(2*np.pi*t*rng.uniform(1,2.5))
    a=(np.sin(np.pi*t/dur)**1.5)*(0.55+0.45*np.sin(2*np.pi*t*rng.uniform(2.5,5))**2)
    a*=(np.sin(2*np.pi*t*rng.uniform(2,4)+rng.uniform(0,6))>-0.55)
    a=np.convolve(a,np.ones(160)/160,'same'); return synth(f,(1,.18,.05))*a
def cuckoo():
    f=rng.uniform(560,720); return np.concatenate([note(f*1.19,f*1.17,.2,1,(1,.5,.15,.05)),silence(.07),note(f,f*.98,.3,1,(1,.5,.15,.05))])
def coo():
    parts=[]; f=rng.uniform(430,560)
    for d in (.35,.28,.28,.5): parts+=[note(f*1.05,f*.95,d,.8,(1,.35,.1))*.7,silence(.14)]
    return np.concatenate(parts)
EV=[(tweet,1.0,.8),(trill,.45,.6),(warble,.5,1.0),(cuckoo,.025,.7),(coo,.03,.5)]
IR=[rng.standard_normal(int(.9*SR))*np.exp(-np.arange(int(.9*SR))/(.22*SR)) for _ in range(2)]; IR=[i/np.sqrt((i**2).sum()) for i in IR]
bus_carry=[np.zeros(ML),np.zeros(ML)]
def place(buf,w,pos,pan):
    L=min(len(w),buf.shape[1]-pos)
    if L<=0: return
    buf[0,pos:pos+L]+=w[:L]*np.cos((pan+1)*np.pi/4); buf[1,pos:pos+L]+=w[:L]*np.sin((pan+1)*np.pi/4)
def insects(n,t0):
    tt=(np.arange(n)+t0)/SR; o=np.zeros((2,n))
    for k in range(2):
        for j,(fc,pr,ph) in enumerate(((rng.uniform(4300,4800),rng.uniform(42,58),0),(rng.uniform(5200,5900),rng.uniform(30,44),1.3))):
            pulse=np.clip(np.sin(2*np.pi*pr*tt+ph+k),0,1)**1.5
            sw=0.5+0.5*np.sin(2*np.pi*tt/rng.uniform(25,55)+k*2+j)
            o[k]+=np.sin(2*np.pi*fc*tt+0.5*np.sin(2*np.pi*3*tt))*pulse*sw**2*0.008
    return o
bpf=[butter(2,[600,3200],btype='band',fs=SR,output='sos') for _ in range(2)]
wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); G=None; act=0.
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); act=0.92*act+rng.normal(0,.35); m=float(np.exp(np.clip(act,-1.6,0.3)))*0.5
    buf=np.zeros((2,n+ML)); buf[:,:ML]+=np.array(bus_carry)
    for fn,rate,lvl in EV:
        for _ in range(rng.poisson(rate*m*n/SR)):
            w=fn(); dist=int(rng.choice([0,1,2],p=[.25,.45,.3])); w=sosfilt(LPS[dist],w)*lvl*(1,.6,.35)[dist]*rng.uniform(.6,1)
            place(buf,w,int(rng.integers(0,n)),rng.uniform(-.9,.9))
    # abejas
    for _ in range(rng.poisson(.05*n/SR)):
        d=rng.uniform(3,6); k=int(d*SR); tt=np.arange(k)/SR; f=rng.uniform(170,250)*(1+.04*np.sin(2*np.pi*rng.uniform(.5,2)*tt))
        w=synth(f,(1,.6,.35,.2,.1))*np.exp(-((tt-d/2)/(d/4.5))**2)*0.05
        p0,p1=rng.uniform(-.9,.9),rng.uniform(-.9,.9); pos=int(rng.integers(0,n)); L=min(k,buf.shape[1]-pos)
        pan=np.linspace(p0,p1,k)[:L]; buf[0,pos:pos+L]+=w[:L]*np.cos((pan+1)*np.pi/4); buf[1,pos:pos+L]+=w[:L]*np.sin((pan+1)*np.pi/4)
    wet=[fftconvolve(buf[k],IR[k])[:n+ML] for k in range(2)]
    mix=[buf[k]+0.22*wet[k] for k in range(2)]
    bus_carry=[mix[k][n:n+ML].copy() for k in range(2)]
    ins=insects(n,c*CH); air=[sosfilt(bpf[k],rng.standard_normal(n))*0.004 for k in range(2)]
    x=np.stack([mix[0][:n]+ins[0]+air[0],mix[1][:n]+ins[1]+air[1]],1)
    if G is None: G=0.42/(np.percentile(np.abs(x),99.7)+1e-9)
    y=np.tanh(x*G*1.1)/1.1; f=int(4*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.9*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
