#!/bin/bash
# primera línea de music_job.txt = "batch 0 0 x"; líneas siguientes: <nombre> <minutos> <seed> <tipo rain|pomo|brown|night|dawn>
set -e
mkdir -p out
FOC=${POMO_FOCUS:-1500}; CYC=${POMO_CYCLE:-1800}
stock(){ # $1=pexels id  $2=tipo (srain|spomo|sfire)
  curl -sL -A "Mozilla/5.0" -o /tmp/src.mp4 "https://www.pexels.com/download/video/$1/?w=1280&h=720" || true
  [ "$(stat -c%s /tmp/src.mp4 2>/dev/null || echo 0)" -gt 200000 ] || curl -sL -A "Mozilla/5.0" -o /tmp/src.mp4 "https://www.pexels.com/download/video/$1/"
  ls -la /tmp/src.mp4; ffprobe -v error -show_entries stream=width,height,duration -of csv=p=0 /tmp/src.mp4
  case $2 in
    srain) G="eq=brightness=-0.17:saturation=0.5:gamma=0.85,colorbalance=rs=-0.1:bs=0.14:bm=0.1,curves=all='0/0 0.5/0.38 1/0.85',gblur=sigma=1.2,drawbox=x=0:y=0:w=iw:h=ih:color=0x8fa0b5@0.10:t=fill,vignette=PI/4"; OV=1;;
    spomo) G="eq=brightness=-0.04:saturation=0.9"; OV=0;;
    sfire) G="eq=brightness=-0.02:saturation=1.0"; OV=0;;
  esac
  ffmpeg -nostdin -y -loglevel error -t 10 -i /tmp/src.mp4 -an -vf "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=12,$G" -c:v libx264 -preset veryfast -crf 18 /tmp/fwd.mp4
  ffmpeg -nostdin -y -loglevel error -i /tmp/fwd.mp4 -vf "reverse" -c:v libx264 -preset veryfast -crf 18 /tmp/rev.mp4
  printf "file '/tmp/fwd.mp4'\nfile '/tmp/rev.mp4'\n" > /tmp/l.txt
  ffmpeg -nostdin -y -loglevel error -f concat -safe 0 -i /tmp/l.txt -c copy /tmp/pp.mp4
  if [ $OV = 1 ]; then
    python3 gen_overlay_rain.py 10 /tmp/ov.mp4
    ffmpeg -nostdin -y -loglevel error -i /tmp/pp.mp4 -stream_loop -1 -i /tmp/ov.mp4 -filter_complex "[1:v]format=gbrp[o];[0:v]format=gbrp[b];[b][o]blend=all_mode=screen:all_opacity=0.55,format=yuv420p" -t $(ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/pp.mp4) -c:v libx264 -preset veryfast -crf 28 -maxrate 115k -bufsize 230k -g 48 /tmp/loop.mp4
  else
    ffmpeg -nostdin -y -loglevel error -i /tmp/pp.mp4 -c:v libx264 -preset veryfast -crf 28 -maxrate 115k -bufsize 230k -g 48 -pix_fmt yuv420p /tmp/loop.mp4
  fi
  ffmpeg -nostdin -y -loglevel error -i /tmp/loop.mp4 -frames:v 1 -ss 3 out/$N.jpg
}
build(){ N=$1; M=$2; S=$3; T=$4; ID=$5
  case $T in
    srain) python3 gen_rain.py $M $S /tmp/a.wav; stock $ID srain;;
    spomo) python3 gen_pomo.py $M $S /tmp/a.wav; stock $ID spomo;;
    sbrown) python3 gen_brown.py $M $S /tmp/a.wav; stock $ID sfire;;
    rain) python3 gen_rain.py $M $S /tmp/a.wav; VFPS=12 VCRF=30 VMAX=70k python3 gen_visual_rain.py 60 /tmp/loop.mp4;;
    brown) python3 gen_brown.py $M $S /tmp/a.wav; VFPS=12 VCRF=30 VMAX=50k python3 gen_visual_noise.py 60 /tmp/loop.mp4;;
    pomo) python3 gen_pomo.py $M $S /tmp/a.wav; VFPS=12 VW=1280 VH=720 DIM=0.5 VCRF=30 VMAX=90k python3 gen_visual2.py dawn 60 /tmp/loop.mp4;;
    *) python3 gen_sleep2.py $M $S /tmp/a.wav; VFPS=12 VW=1280 VH=720 DIM=0.55 VCRF=30 VMAX=120k python3 gen_visual2.py $T 60 /tmp/loop.mp4;;
  esac
  ffmpeg -nostdin -y -loglevel error -i /tmp/a.wav -c:a aac -b:a 64k /tmp/a.m4a
  LD=$(ffprobe -v error -show_entries format=duration -of csv=p=0 /tmp/loop.mp4); LOOPS=$(python3 -c "import math;print(int(math.ceil($M*60/float('$LD')))+1)")
  case $T in pomo|spomo) ISP=1;; *) ISP=0;; esac
  if [ $ISP = 1 ]; then
    FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
    R="ceil($FOC-mod(t\,$CYC))"; B="ceil($CYC-mod(t\,$CYC))"
    VF="drawbox=x=iw/2-230:y=40:w=460:h=190:color=black@0.45:t=fill,"
    VF+="drawtext=fontfile=$FONT:text='ENFOQUE':fontsize=40:fontcolor=0xffb84d:x=(w-tw)/2:y=58:enable='lt(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='DESCANSO':fontsize=40:fontcolor=0x2dd4bf:x=(w-tw)/2:y=58:enable='gte(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='%{eif\:floor($R/60)\:d\:2}\:%{eif\:mod($R\,60)\:d\:2}':fontsize=110:fontcolor=white:x=(w-tw)/2:y=105:enable='lt(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='%{eif\:floor($B/60)\:d\:2}\:%{eif\:mod($B\,60)\:d\:2}':fontsize=110:fontcolor=white:x=(w-tw)/2:y=105:enable='gte(mod(t\,$CYC)\,$FOC)'"
    ffmpeg -nostdin -y -loglevel error -stream_loop $LOOPS -i /tmp/loop.mp4 -i /tmp/a.m4a -map 0:v -map 1:a -vf "$VF" -c:v libx264 -preset veryfast -crf 30 -maxrate 110k -bufsize 220k -g 48 -pix_fmt yuv420p -c:a copy -shortest -movflags +faststart out/$N.mp4
  else
    ffmpeg -nostdin -y -loglevel error -stream_loop $LOOPS -i /tmp/loop.mp4 -i /tmp/a.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart out/$N.mp4
  fi
  ls -la out/$N.mp4; rm -f /tmp/a.wav /tmp/a.m4a /tmp/loop.mp4 /tmp/fwd.mp4 /tmp/rev.mp4 /tmp/pp.mp4 /tmp/src.mp4
}
if [ "$1" = batch ]; then
  tail -n +2 music_job.txt | while read n m s t id; do [ -n "$n" ] && build $n $m $s $t $id; done
else build $1 $2 $3 $4; fi
