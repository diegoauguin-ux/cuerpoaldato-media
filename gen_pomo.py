"""Lofi suave para estudiar con ciclos Pomodoro. uso: gen_pomo.py <min> <seed> <out.wav>  (env POMO_FOCUS, POMO_CYCLE en s)"""
import sys,os,wave,numpy as np
from scipy.signal import butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
FOC=int(os.environ.get('POMO_FOCUS',1500)); CYC=int(os.environ.get('POMO_CYCLE',1800))
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); BPM=72; beat=60/BPM; bar=4*beat
buf=np.zeros(total+SR*8,np.float32)
def add(s,t,g=1.0):
    i=int(t*SR)
    if i<0 or i>=total: return
    j=min(len(buf),i+len(s)); buf[i:j]+=s[:j-i]*g
mid=lambda m:440*2**((m-69)/12)
def rhodes(f,dur,decay=2.2):
    n=int(dur*SR); t=np.arange(n)/SR; s=0
    for dt in (-3,3):
        ff=f*2**(dt/1200); s=s+np.sin(2*np.pi*ff*t+1.1*np.exp(-t*6)*np.sin(2*np.pi*ff*t))+0.2*np.sin(2*np.pi*2*ff*t)*np.exp(-t*4)
    return (s*np.exp(-t*decay)*(1-np.exp(-t*90))*0.5).astype(np.float32)
def bell(f,dur=3.5):
    t=np.arange(int(dur*SR))/SR; s=0
    for r,a,d in ((1,1,1.2),(2.76,.5,2),(5.4,.25,3.2)): s=s+a*np.sin(2*np.pi*f*r*t)*np.exp(-t*d)
    return (s*0.25*(1-np.exp(-t*200))).astype(np.float32)
def kick():
    t=np.arange(int(.35*SR))/SR; ph=2*np.pi*(45*t+75*(1-np.exp(-t*22))/22); return (np.sin(ph)*np.exp(-t*9)).astype(np.float32)
bpS=butter(2,[1500,5500],btype='band',fs=SR,output='sos'); hpS=butter(2,7000,btype='high',fs=SR,output='sos')
def snare():
    n=int(.25*SR); t=np.arange(n)/SR; return (sosfilt(bpS,rng.standard_normal(n))*np.exp(-t*20)*.9+np.sin(2*np.pi*190*t)*np.exp(-t*25)*.4).astype(np.float32)
def hat():
    n=int(.06*SR); t=np.arange(n)/SR; return (sosfilt(hpS,rng.standard_normal(n))*np.exp(-t*70)).astype(np.float32)
KS,SS=kick(),snare()
Q={'M7':[0,4,7,11],'m7':[0,3,7,10],'d7':[0,4,7,10],'m9':[0,3,7,10,14]}
PR=[[(5,'M7'),(4,'m7'),(2,'m7'),(0,'M7')],[(9,'m9'),(2,'m7'),(7,'d7'),(0,'M7')],[(0,'M7'),(9,'m7'),(2,'m9'),(7,'d7')],[(2,'m7'),(7,'d7'),(0,'M7'),(9,'m7')]]
TR=[0,-2,3,5]
def chord(root,q,t,vel,dur,decay):
    base=root+48
    for k,iv in enumerate(Q[q]):
        add(rhodes(mid(base+iv),dur,decay),t+k*0.018+rng.uniform(0,.008),vel*(0.9 if k==0 else 1))
    add(rhodes(mid(base-12),dur,1.3)*1.4,t,vel*.9)
nbar=int(total/SR/bar)+1; cyc_prev=-1
for b in range(nbar):
    t=b*bar; p=t%CYC; ci=int(t//CYC); focus=p<FOC
    if ci!=cyc_prev:
        cyc_prev=ci
        add(bell(mid(84)),t+0.2,0.9)
    if abs(t-(ci*CYC+FOC))<bar/2+0.01 or (b>0 and (t-bar)%CYC<FOC<=p): pass
    prog=PR[(b//16+ci)%4]; sh=TR[ci%4]; root,q=prog[b%4]; root=(root+sh)%12
    if focus:
        vel=0.16*(0.85+0.15*np.sin(b/5.0))
        chord(root,q,t,vel,bar*1.1,2.0)
        if rng.random()<0.8: chord(root,q,t+beat*1.5+0.04,vel*.55,bar*.6,3.0)
        if rng.random()<0.35: chord(root,q,t+beat*3,vel*.4,bar*.5,3.0)
        if p>bar*6:
            add(KS,t,0.55); add(KS,t+beat*2.5+0.02,0.45)
            add(SS,t+beat,0.30); add(SS,t+beat*3,0.30)
            for h in range(8):
                off=h*beat/2+(0.07*beat if h%2 else 0)
                add(hat(),t+off+rng.uniform(-.004,.004),0.10*rng.uniform(.5,1.2))
    elif b%2==0:
        chord(root,q,t,0.14,bar*2.2,0.9)
    if focus and p+bar>=FOC: add(bell(mid(72)),t+bar-0.3,0.9)
# post: calidez, crepitar, reverb suave, estéreo
buf=buf[:total]
lp=butter(2,4200,btype='low',fs=SR,output='sos'); x=sosfilt(lp,buf).astype(np.float32); del buf
for dly,g in ((0.09,.22),(0.17,.16),(0.31,.1)):
    k=int(dly*SR); x[k:]+=x[:-k].copy()*g
x/=np.abs(x).max()+1e-9; x*=0.7
d=int(0.009*SR); wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
CH=SR*20; ck=butter(2,[1500,9000],btype='band',fs=SR,output='sos')
for c in range(int(np.ceil(total/CH))):
    a,bb=c*CH,min(total,(c+1)*CH); n=bb-a
    L=x[a:bb].copy(); R=np.zeros(n,np.float32); s=max(0,a-d); R[(a-s) if a<d else 0:]=0
    R=np.roll(x[a:bb],d)*0.95
    cr=(rng.random(n)<6/SR)*rng.random(n)*0.5; cr=sosfilt(ck,cr).astype(np.float32)
    hs=sosfilt(ck,rng.standard_normal(n)).astype(np.float32)*0.004
    y=np.stack([L+cr+hs,R+np.roll(cr,7)+hs],1)
    f=int(3*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if bb>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((np.clip(y,-1,1)*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
