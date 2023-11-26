import cv2
from pathlib import Path
from flask import Flask, Response, render_template, request, jsonify, send_from_directory
import multiprocessing
import threading
from collections import deque
from pathlib import Path
import time
import os
import subprocess


global frame_buffer, buffer_lock
frame_buffer = deque(maxlen=10)  # Buffer up to 10 frames
buffer_lock = threading.Lock()
app = Flask(__name__)
camera_lock = threading.Lock()

global temp_flag
temp_flag = Path('output.log')
if temp_flag.exists():
    temp_flag.unlink()
temp_flag.touch()


def start_producer(script_name='producer.sh'):
    with open('output.log', 'w') as f:
        try:

            process = subprocess.Popen(['bash', script_name],stdout=f,stderr=f, start_new_session=True,env=os.environ.copy())
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while running the script: {e}")
        



def wait_for_producer():
   with open('output.log', 'r') as f:
       while True:
           line = f.readline()
           if not line:
               time.sleep(0.1)
               continue
           if 'Producer has connected; continuing.' in line:
               print("Producer is ready.")
               break
           else:
               print(line)
               continue


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
    "queue max-size-buffers=10, max-size-bytes=0, max-size-time=0 ! "
    "video/x-raw, format=I420, width=1280, height=720, framerate=10/1 ! "
    "videoconvert ! appsink"
    )
    return cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)


def generate():
    global frame_buffer, buffer_lock
    while True:  # Acquiring the lock before accessing the camera
        ret, frame = cap.read()
        with buffer_lock:
            frame_buffer.append(frame)
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
    global frame_buffer, buffer_lock
    path = Path('saved_images')
    path.mkdir( exist_ok=True)

    with buffer_lock:
        if not frame_buffer:
            return jsonify(status='error', message="No frames in buffer.")
    # Acquiring the lock before accessing the camera
        frame = frame_buffer[-1]
    filename = f"{path.name}/saved_frame_{time.time()}.jpg"
    cv2.imwrite(filename, frame)
    print(f"Image saved as {filename}")
    return jsonify(status='ok', message=f"Image saved as {filename}")


@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory('saved_images', filename)


@app.route('/images/list')
def list_images():
    files = os.listdir('saved_images')
    return jsonify(files)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/via')
def via():
    return render_template('annotate.html')


@app.route('/get_image_files_json', methods=['GET'])
def get_image_file_json():
    path = Path('saved_images')
    try:
        # Assuming images are stored directly under the 'saved_images' directory
        image_filenames = [str(filename) for filename in path.iterdir()]
        print(f"Found {len(image_filenames)} images.")
        # Filter out any non-image files if necessary
        image_filenames = [filename for filename in image_filenames if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        
        return jsonify(image_filenames)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify(error=str(e)), 500


@app.route('/ims/<path:path>')
def send_report(path,methods=['GET']):
    print(path)
    path = Path(path)
    print(path.exists())
    return send_from_directory('ims', path)



@app.route('/get_image_filenames', methods=['GET'])
def get_image_filenames():
    path = Path('saved_images')
    try:
        # Assuming images are stored directly under the 'saved_images' directory
        image_filenames = [str(filename.name) for filename in path.iterdir()]
        print(f"Found {len(image_filenames)} images.")
        # Filter out any non-image files if necessary
        images = 'http://192.168.1.200:9080/images/'
        image_filenames = [f'{images}{filename}' for filename in image_filenames if filename.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        print(image_filenames)
        return jsonify(image_filenames)
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify(error=str(e)), 500


if __name__ == '__main__':
    # Start the producer process wiith multiprocessing
    time.sleep(5)
    with camera_lock:
    #     start_producer('producer.sh')
    #wait_for_producer()
        cap = get_video_capture()
    #cap = get_video_capture()
    app.run(host='0.0.0.0', port=9080)
