import cv2

from flask import Flask, Response, render_template, request, jsonify, send_from_directory
import threading
from pathlib import Path
import time

app = Flask(__name__)

# Defining a threading lock for synchronizing camera access
camera_lock = threading.Lock()

def gstreamer_pipeline(format='I420', 
                       capture_width=1280, 
                       capture_height=720, 
                       framerate=10):
    return ("shmsrc socket-path=/tmp/video_stream ! "
            f"video/x-raw, format={format}, width={capture_width}, height={capture_height}, framerate={framerate}/1 ! "
            "videoconvert ! "
            "appsink"
            )

# GStreamer Pipeline to read from shared memory
def get_video_capture():
    gst_pipeline = (
        "shmsrc socket-path=/tmp/video_stream ! "
        "video/x-raw, format=I420, width=1280, height=720, framerate=10/1 ! "
        "videoconvert ! appsink"
    )
    return cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

cap = get_video_capture()

def generate():
    while True:
        with camera_lock:  # Acquiring the lock before accessing the camera
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
    path = Path('saved_images')
    path.mkdir( exist_ok=True)

    with camera_lock:  # Acquiring the lock before accessing the camera
        ret, frame = cap.read()
    if not ret:
        return jsonify(status='error', message="Couldn't read frame.")
    
    filename = f"{path.name}/saved_frame_{time.time()}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    return jsonify(status='ok', message=f"Image saved as {filename}")

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/via')
def via():
    return render_template('via.html')


@app.route('/get_image_filenames', methods=['GET'])
def get_image_filenames():
    image_folder = 'saved_images'
    images = [f for f in os.listdir(image_folder) if os.path.isfile(os.path.join(image_folder, f))]
    return jsonify(images)


@app.route('/saved_images/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory('saved_images', filename)



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9080)
