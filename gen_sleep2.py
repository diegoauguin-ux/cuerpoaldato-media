"""Música de sueño v2: drones graves de sinusoides, sin ataques, respiración 6/min, ruido marrón suave, apagado progresivo.
uso: python3 gen_sleep2.py <minutos> <seed> <salida.wav>"""
import sys,numpy as np,wave
from scipy.signal import lfilter
SR=32000
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
rng=np.random.default_rng(seed); N=int(mins*60*SR)
mid=lambda m:440*2**((m-69)/12)
SC=[0,2,4,7,9]; ROOT=38  # D2, pentatónica mayor (sin disonancias)
L=np.zeros(N,np.float32); R=np.zeros(N,np.float32)
def tone(f,dur):
    n=int(dur*SR); t=np.arange(n,dtype=np.float32)/SR; s=0
    for dt in (-1.2,0,1.0):
        ff=f*2**(dt/1200); s=s+np.sin(2*np.pi*ff*t+rng.random()*6)+0.18*np.sin(2*np.pi*2*ff*t+rng.random()*6)
    a=int(min(dur*0.4,12)*SR); r=int(min(dur*0.4,14)*SR)
    e=np.ones(n,np.float32); e[:a]=np.sin(np.linspace(0,np.pi/2,a))**2; e[-r:]*=np.cos(np.linspace(0,np.pi/2,r))**2
    return (s*e/3).astype(np.float32)
def add(b,s,i):
    j=min(N,i+len(s))
    if j>i: b[i:j]+=s[:j-i]
t=0.0; prev=None
while t<mins*60:
    d=rng.uniform(24,36)
    deg=rng.choice(len(SC),2,replace=False)
    notes=[ROOT+SC[deg[0]], ROOT+12+SC[deg[0]], ROOT+12+SC[deg[1]]]  # solo graves-medios (D2–A3)
    for k,m in enumerate(notes):
        pan=0.5+rng.uniform(-0.15,0.15)
        s=tone(mid(m),d+16)*(0.30 if k==0 else 0.18); i=int(t*SR)
        add(L,s*(1-pan)*2,i); add(R,s*pan*2,i)
    t+=d
# respiración: 6 ciclos/min (0,1 Hz), profundidad pequeña
tt=np.arange(N,dtype=np.float32)/SR
br=(0.88+0.12*np.sin(2*np.pi*0.1*tt)).astype(np.float32)
L*=br; R*=br
# ruido marrón muy suave
def brown(n):
    w=rng.standard_normal(n).astype(np.float32)
    y=lfilter([1],[1,-0.995],w).astype(np.float32); y-=lfilter([1],[1,-0.9995],y).astype(np.float32)*0+0
    return y/ (np.abs(y).max()+1e-9)
for ch in (L,R):
    nz=lfilter([0.02],[1,-0.98],rng.standard_normal(N).astype(np.float32)).astype(np.float32)
    nz/=np.abs(nz).max()+1e-9
    ch+=nz*0.05*(0.7+0.3*np.sin(2*np.pi*0.03*tt+rng.random()*6))
# apagado progresivo del brillo: mezcla de dos pasabajos
def lp(x,fc):
    a=np.exp(-2*np.pi*fc/SR); return lfilter([1-a],[1,-a],x).astype(np.float32)
w=np.linspace(0,1,N,dtype=np.float32)
for ch in (L,R):
    ch[:]=(1-w)*lp(lp(ch,900),900)+w*lp(lp(ch,350),350)*1.6
# reverb larga y suave
def rev(x):
    y=x.copy()
    for dly,g in [(0.11,0.35),(0.23,0.3),(0.41,0.25),(0.73,0.2),(1.3,0.15)]:
        k=int(dly*SR); y[k:]+=x[:-k]*g
    return y
L=rev(L); R=rev(R)
fi=int(45*SR); f=np.linspace(0,1,fi)**2
for ch in (L,R): ch[:fi]*=f; ch[-fi:]*=f[::-1]
pk=max(np.abs(L).max(),np.abs(R).max()); L=L/pk*0.55; R=R/pk*0.55
st=(np.stack([L,R],1)*32767).astype(np.int16)
with wave.open(out,"wb") as wv:
    wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(st.tobytes())
print("ok",out)
