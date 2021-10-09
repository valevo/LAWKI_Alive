#!/usr/bin/env bash


NPROCESSES=8

for i in $(seq 0 $(($NPROCESSES-1))); do
    python3 download_videos.py $NPROCESSES $i &
done
wait