#bin/bash
stdbuf -oL -eL gst-launch-1.0 nvarguscamerasrc ! 'video/x-raw(memory:NVMM), \
width=1280, height=720, format=NV12, framerate=10/1' ! \
nvvidconv flip-method=0 ! 'video/x-raw, format=I420' ! \
queue ! shmsink socket-path=/tmp/video_stream \
& python3 flask_file_streamer.py

