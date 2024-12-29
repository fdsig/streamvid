import subprocess
import time
import os
import signal

def start_ffserver():
    cmd = ["ffserver", "-f", "ffserver.conf"]
    return subprocess.Popen(cmd)

def capture_and_stream_video():
    # Define the command and its parameters as a list
    cmd = [
        "nvgstcapture-1.0",
        "--mode=2",
        "--video-enc=1",
        "--file-type=0",
        "--capture-time=5",
        "--file-name=-"  # Use '-' to write to stdout
    ]
    
    # ffmpeg command to receive input from stdin and send to ffserver
    ffmpeg_cmd = [
        "ffmpeg",
        "-i", "-",
        "http://localhost:8080/feed1.ffm"
    ]
    
    # Use Popen to start the nvgstcapture process
    nvgst_process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Use Popen to start the ffmpeg process and link the stdout of nvgstcapture to its stdin
    ffmpeg_process = subprocess.Popen(ffmpeg_cmd, stdin=nvgst_process.stdout, stderr=subprocess.PIPE)

    # Wait a bit to ensure nvgstcapture is ready to accept input
    time.sleep(1)
    
    # Send '1' as an input to nvgstcapture
    nvgst_process.communicate(input=b'1')
    
    # Wait for ffmpeg to finish (you can also handle its output or errors if needed)
    ffmpeg_process.communicate()

try:
    ffserver_process = start_ffserver()
    time.sleep(2)  # Give ffserver a moment to start up
    capture_and_stream_video()  # This will capture and stream the video
except KeyboardInterrupt:
    print("Gracefully shutting down...")
    ffserver_process.terminate()
    print("ffserver terminated.")

