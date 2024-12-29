from flask import Flask, render_template, Response, jsonify, request
import cv2
import time

app = Flask(__name__)

# Video state management class
class VideoState:
    def __init__(self):
        self.is_streaming = True
        self.is_paused = False
        self.save_image = False

video_state = VideoState()

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
        if video_state.is_streaming:
            ret, frame = cap.read()
            if not ret:
                print("Error: Couldn't read frame.")
                continue

            if video_state.save_image:
                cv2.imwrite("saved_image.jpg", frame)
                video_state.save_image = False

            if not video_state.is_paused:
                ret, jpeg = cv2.imencode('.jpg', frame)
                if not ret:
                    print("Error: Couldn't encode frame.")
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
            else:
                time.sleep(0.1)  # Sleep for a bit when paused
        else:
            time.sleep(0.1)  # Sleep for a bit when streaming is stopped

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/action', methods=['POST'])
def action():
    action_type = request.json['action']

    if action_type == "start":
        video_state.is_streaming = True
    elif action_type == "stop":
        video_state.is_streaming = False
    elif action_type == "pause":
        video_state.is_paused = True
    elif action_type == "resume":
        video_state.is_paused = False
    elif action_type == "save_image":
        video_state.save_image = True

    return jsonify(status="success")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080)
