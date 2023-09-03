#!/bin/bash

# Start capture
echo "Starting video capture..."
nvgstcapture-1.0 --mode=2 --video-enc=1 --file-type=0 --capture-time=10 --file-name="/tmp/test_output.mp4" &> capture_log.txt

# Convert captured video to HLS format
echo "Converting video to HLS format..."
ffmpeg -i /tmp/test_output.mp4 -c:v copy -f hls -hls_time 4 -hls_playlist_type event -hls_list_size 5 -hls_flags delete_segments /tmp/playlist.m3u8 &> ffmpeg_log.txt

# Start HTTP server
echo "Starting HTTP server on port 8080..."
python3 -m http.server 8080 --directory /tmp &> server_log.txt

