import subprocess
import os

def check_producer_ready():
    return os.path.exists('/tmp/producer_ready.flag')

def run_producer():
    try:
        command = [
            'gst-launch-1.0',
            'nvarguscamerasrc',
            '!', 
            "'video/x-raw(memory:NVMM), width=1280, height=720, format=NV12, framerate=10/1'",
            '!',
            'nvvidconv flip-method=0',
            '!',
            "'video/x-raw, format=I420'",
            '!',
            'shmsink socket-path=/tmp/video_stream'
        ]
        with open('output.log', 'w') as f:
            print("Producer script started successfully.")
            process = subprocess.Popen(' '.join(command), stdout=f, stderr=f, shell=True,env=os.environ.copy())
            #process.wait()

        # Wait for the process to start and create a flag file
    except Exception as e:
        print(f"An error occurred: {e}")

run_producer()

# Now you can start the Flask application