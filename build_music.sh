#!/bin/bash
# primera línea de music_job.txt = "batch 0 0 x"; líneas siguientes: <nombre> <minutos> <seed> <tipo rain|pomo|brown|night|dawn>
set -e
mkdir -p out
FOC=${POMO_FOCUS:-1500}; CYC=${POMO_CYCLE:-1800}
build(){ N=$1; M=$2; S=$3; T=$4
  case $T in
    rain) python3 gen_rain.py $M $S /tmp/a.wav; VFPS=12 VCRF=30 VMAX=70k python3 gen_visual_rain.py 60 /tmp/loop.mp4;;
    brown) python3 gen_brown.py $M $S /tmp/a.wav; VFPS=12 VCRF=30 VMAX=50k python3 gen_visual_noise.py 60 /tmp/loop.mp4;;
    pomo) python3 gen_pomo.py $M $S /tmp/a.wav; VFPS=12 VW=1280 VH=720 DIM=0.5 VCRF=30 VMAX=90k python3 gen_visual2.py dawn 60 /tmp/loop.mp4;;
    *) python3 gen_sleep2.py $M $S /tmp/a.wav; VFPS=12 VW=1280 VH=720 DIM=0.55 VCRF=30 VMAX=120k python3 gen_visual2.py $T 60 /tmp/loop.mp4;;
  esac
  ffmpeg -y -loglevel error -i /tmp/a.wav -c:a aac -b:a 64k /tmp/a.m4a
  LOOPS=$(( (M*60)/60 + 1 ))
  if [ "$T" = pomo ]; then
    FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
    R="ceil($FOC-mod(t\,$CYC))"; B="ceil($CYC-mod(t\,$CYC))"
    VF="drawbox=x=iw/2-230:y=40:w=460:h=190:color=black@0.45:t=fill,"
    VF+="drawtext=fontfile=$FONT:text='ENFOQUE':fontsize=40:fontcolor=0xffb84d:x=(w-tw)/2:y=58:enable='lt(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='DESCANSO':fontsize=40:fontcolor=0x2dd4bf:x=(w-tw)/2:y=58:enable='gte(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='%{eif\:floor($R/60)\:d\:2}\:%{eif\:mod($R\,60)\:d\:2}':fontsize=110:fontcolor=white:x=(w-tw)/2:y=105:enable='lt(mod(t\,$CYC)\,$FOC)',"
    VF+="drawtext=fontfile=$FONT:text='%{eif\:floor($B/60)\:d\:2}\:%{eif\:mod($B\,60)\:d\:2}':fontsize=110:fontcolor=white:x=(w-tw)/2:y=105:enable='gte(mod(t\,$CYC)\,$FOC)'"
    ffmpeg -y -loglevel error -stream_loop $LOOPS -i /tmp/loop.mp4 -i /tmp/a.m4a -map 0:v -map 1:a -vf "$VF" -c:v libx264 -preset veryfast -crf 30 -maxrate 90k -bufsize 180k -g 48 -pix_fmt yuv420p -c:a copy -shortest -movflags +faststart out/$N.mp4
  else
    ffmpeg -y -loglevel error -stream_loop $LOOPS -i /tmp/loop.mp4 -i /tmp/a.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart out/$N.mp4
  fi
  ls -la out/$N.mp4; rm -f /tmp/a.wav /tmp/a.m4a /tmp/loop.mp4
}
if [ "$1" = batch ]; then
  tail -n +2 music_job.txt | while read n m s t; do [ -n "$n" ] && build $n $m $s $t; done
else build $1 $2 $3 $4; fi
