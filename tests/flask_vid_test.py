import cv2
from flask import Flask, Response, render_template
import os


app = Flask(__name__)

# Capture video
def gstreamer_pipeline(
    capture_width=1280,
    capture_height=720,
    display_width=1280,
    display_height=720,
    framerate=10,
    flip_method=0,
):
    return (
        "nvarguscamerasrc ! "
        "video/x-raw(memory:NVMM), "
        "width=(int)%d, height=(int)%d, "
        "format=(string)NV12, framerate=(fraction)%d/1 ! "
        "nvvidconv flip-method=%d ! "
        "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
        "videoconvert ! "
        "video/x-raw, format=(string)BGR ! appsink"
        % (
            capture_width,
            capture_height,
            framerate,
            flip_method,
            display_width,
            display_height,
        )
    )

gst_str = gstreamer_pipeline()

# Open capture
cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

def generate():
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't read frame.")
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Couldn't encode frame.")
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        
@app.route('/')
def index():
    #pid = os.getpid()  # Get the PID of the current process
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    print("video_feed() called")
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080)
