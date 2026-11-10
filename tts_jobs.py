import os,glob,asyncio,subprocess,sys
subprocess.run([sys.executable,"-m","pip","install","-q","edge-tts"])
import edge_tts
async def m():
    for f in sorted(glob.glob("job_*.txt")):
        ep=f[4:-4]; d="voice/"+ep
        if os.path.isdir(d): continue
        os.makedirs(d)
        for i,l in enumerate([x.strip() for x in open(f,encoding="utf8") if x.strip()]):
            await edge_tts.Communicate(l,"es-CL-LorenzoNeural",rate="+12%",pitch="+2Hz").save("%s/%02d.mp3"%(d,i))
asyncio.run(m())
