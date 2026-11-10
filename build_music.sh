#!/bin/bash
# uso: build_music.sh <nombre> <minutos> <seed> <tema night|dawn|rain>
set -e
N=$1; M=$2; S=$3; T=$4
mkdir -p out
python3 gen_sleep2.py $M $S /tmp/a.wav
VFPS=12 VW=1280 VH=720 DIM=0.55 VCRF=30 VMAX=120k python3 gen_visual2.py $T 60 /tmp/loop.mp4
ffmpeg -y -loglevel error -i /tmp/a.wav -c:a aac -b:a 80k /tmp/a.m4a
LOOPS=$(( (M*60)/60 + 1 ))
ffmpeg -y -loglevel error -stream_loop $LOOPS -i /tmp/loop.mp4 -i /tmp/a.m4a -map 0:v -map 1:a -c copy -shortest -movflags +faststart out/$N.mp4
ls -la out/$N.mp4
