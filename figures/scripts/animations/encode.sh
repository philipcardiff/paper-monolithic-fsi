#!/bin/bash
# encode.sh FRAMESDIR NAME FPS LOOPS WIDTH_WEB POSTER_FRAME [FIRST LAST]
# MP4 (H.264, yuv420p, crf 18, max 1920 wide) + WebM (VP9) looped LOOPS times,
# a looping GIF (<= 5 MB, else animated WebP) at WIDTH_WEB, and a poster PNG.
set -e
F=$1; N=$2; FPS=$3; LOOPS=$4; WW=$5; PF=$6; FIRST=${7:-0}; LAST=${8:-}
O=/Volumes/OpenFOAM/philipc-v2512/claude-runs/animations/out; mkdir -p $O
FF=/opt/homebrew/bin/ffmpeg
T=$(mktemp -d)
n=0; for f in $(ls $F/f*.png | sort); do i=$((10#$(basename $f .png | tr -d f))); if [ $i -ge $FIRST ] && { [ -z "$LAST" ] || [ $i -le $LAST ]; }; then ln -s $f $T/g$(printf %04d $n).png; n=$((n+1)); fi; done
echo "$N: $n frames"
SC="scale='min(1920,iw)':-2:flags=lanczos"
$FF -y -loglevel error -framerate $FPS -i $T/g%04d.png -vf "loop=loop=$((LOOPS-1)):size=$n:start=0,$SC,format=yuv420p" -c:v libx264 -crf 18 -preset slow -r 30 -movflags +faststart $O/$N.mp4
$FF -y -loglevel error -framerate $FPS -i $T/g%04d.png -vf "loop=loop=$((LOOPS-1)):size=$n:start=0,$SC,format=yuv420p" -c:v libvpx-vp9 -crf 32 -b:v 0 -r 30 $O/$N.webm
$FF -y -loglevel error -framerate $FPS -i $T/g%04d.png -vf "scale=$WW:-2:flags=lanczos,palettegen=max_colors=128:stats_mode=diff" $T/pal.png
$FF -y -loglevel error -framerate $FPS -i $T/g%04d.png -i $T/pal.png -lavfi "scale=$WW:-2:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4" -loop 0 $O/$N.gif
s=$(stat -f %z $O/$N.gif)
if [ $s -gt 5000000 ]; then rm -f $O/$N.gif; $FF -y -loglevel error -framerate $FPS -i $T/g%04d.png -vf "scale=$WW:-2:flags=lanczos" -c:v libwebp_anim -quality 70 -loop 0 $O/$N.webp; echo "$N: GIF too large ($s), wrote animated WebP"; fi
cp $(ls $F/f*.png | sort | sed -n "$((PF+1))p") $O/$N-poster.png
rm -rf $T
ls -la $O/$N.*  $O/$N-poster.png | awk '{print $5, $NF}'
