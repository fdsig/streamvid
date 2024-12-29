import cv2
from flask import Flask, Response, render_template, request, jsonify
import os
from pathlib import Path
import time

app = Flask(__name__)

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

def get_video_capture():
    gst_str = gstreamer_pipeline()
    return cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

cap = get_video_capture()
start_time = time.time()

def generate():
    global start_time, cap
    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time > 3600:  # 3600 seconds = 1 hour
            cap.release()
            cap = get_video_capture()
            start_time = time.time()
            
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

@app.route('/save_image', methods=['POST'])
def save_image():
    print("Saving image...")
    ret, frame = cap.read()
    if not ret:
        return jsonify(status='error', message="Couldn't read frame.")
    filename = f"saved_frame_{time.time()}.jpg"
    print(f"frame {frame.shape} saved to {filename}")
    path = Path('.')
    print(path.absolute())
    cv2.imwrite(str(path/filename), frame)
    return jsonify(status='ok', message="Image saved successfully.")    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080)
