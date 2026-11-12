"""Ruido marrón continuo. uso: gen_brown.py <min> <seed> <out.wav>"""
import sys,wave,numpy as np
from scipy.signal import lfilter,butter,sosfilt
mins,seed,out=float(sys.argv[1]),int(sys.argv[2]),sys.argv[3]
SR=32000; rng=np.random.default_rng(seed); total=int(mins*60*SR); CH=SR*10
a=[1,-0.9985]; zi=[np.zeros(1),np.zeros(1)]
sos=butter(1,18,btype='high',fs=SR,output='sos'); zh=[np.zeros((1,2)),np.zeros((1,2))]
def gen(k,n):
    y,zi[k]=lfilter([1],a,rng.standard_normal(n),zi=zi[k]); y,zh[k]=sosfilt(sos,y,zi=zh[k]); return y
gen(0,SR*8); gen(1,SR*8)
G=None; wv=wave.open(out,'wb'); wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR)
for c in range(int(np.ceil(total/CH))):
    n=min(CH,total-c*CH); x=np.stack([gen(0,n),gen(1,n)],1)
    if G is None: G=0.14/np.sqrt((x**2).mean())
    y=np.tanh(x*G)
    f=int(3*SR)
    if c==0: y[:f]*=np.linspace(0,1,f)[:,None]
    if (c+1)*CH>=total: y[-f:]*=np.linspace(1,0,f)[:,None]
    wv.writeframes((y*0.8*32767).astype(np.int16).tobytes())
wv.close(); print('ok',out)
