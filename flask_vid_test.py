import cv2
from flask import Flask, Response, render_template

app = Flask(__name__)

# Capture video
gst_str = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM),format=(string)NV12,width=1920,height=1080,framerate=30/1 ! "
    "nvvidconv ! videoconvert ! "
    "appsink"
)

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
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)