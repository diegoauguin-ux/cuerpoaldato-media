import sys,json,subprocess,os,glob
d=sys.argv[1]; ep=sys.argv[2]
L=[l.strip() for l in open(f'{ep}.txt') if l.strip()]
fs=sorted(glob.glob(f'{d}/{ep}/*.mp3')); assert len(fs)==len(L),(len(fs),len(L))
lst=[];tim=[];t=0.0
sil=f'{d}/sil.wav'; subprocess.run(f'ffmpeg -v error -y -f lavfi -i anullsrc=r=24000:cl=mono -t 0.3 {sil}',shell=True)
for f,l in zip(fs,L):
    w=f[:-4]+'.wav'; subprocess.run(f'ffmpeg -v error -y -i {f} -ar 24000 -ac 1 {w}',shell=True)
    dur=float(subprocess.check_output(f'ffprobe -v error -show_entries format=duration -of csv=p=0 {w}',shell=True))
    tim.append({"text":l,"start":round(t,3),"end":round(t+dur,3)}); t+=dur+0.3; lst+=[w,sil]
open(f'{d}/{ep}.lst','w').write("".join(f"file '{os.path.abspath(x)}'\n" for x in lst))
subprocess.run(f'ffmpeg -v error -y -f concat -safe 0 -i {d}/{ep}.lst -af loudnorm=I=-14:TP=-1.5 -ar 44100 {d}/{ep}.wav',shell=True)
json.dump(tim,open(f'{d}/{ep}.json','w'),ensure_ascii=False); print(ep,round(t,1),'s')
