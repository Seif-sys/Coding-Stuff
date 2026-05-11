#!/bin/bash

input="input.mp4"  
segment_duration=7
overlap=1
index=0
start_time=0
output_dir="output_chunks"

duration=$(ffmpeg -i "$input" 2>&1 | grep "Duration" | awk '{print $2}' | tr -d , | awk -F: '{ print ($1 * 3600) + ($2 * 60) + $3 }')

while (( $(echo "$start_time < $duration" | bc -l) )); do
    filename=$(printf "$output_dir/out%03d.ogv" $index)
    echo "Creating $filename from $start_time seconds..."

    ffmpeg -ss "$start_time" -i "$input" -t "$segment_duration" \
        -c:v libtheora -q:v 7 \
        -c:a libvorbis -q:a 5 \
        "$filename"

    start_time=$(echo "$start_time + $segment_duration - $overlap" | bc)
    ((index++))
done
