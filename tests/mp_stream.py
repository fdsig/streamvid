import cv2
import time
import multiprocessing as mp
from flask import Flask, Response, render_template, request, jsonify

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

def generate(q):
    cap = get_video_capture()
    start_time = time.time()

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

        if q.full():
            q.get()  # remove one item if the queue is full to avoid losing the new item

        q.put(jpeg.tobytes())  # put the jpeg bytes data into the queue

def video_capture(q):
    try:
        generate(q)
    except Exception as e:
        print(f"An error occurred: {e}")

@app.route('/')
def index():
    return render_template('mp_index.html')

@app.route('/video_feed')
def video_feed():
    if q.empty():
        return Response(status=204)
    jpg_bytes = q.get()
    return Response(jpg_bytes, mimetype='image/jpeg')

def video_from_process():
    q = mp.Queue(maxsize=10)  # Adjust the size based on your requirement
    p = mp.Process(target=video_capture, args=(q,))
    p.start()
    return q    # To be able to use q outside of this function
    

if __name__ == "__main__":
    global q
    q = video_from_process()
    while q.empty():
        time.sleep(0.1)
    
    print(q.get())
    app.run(host='0.0.0.0', port=9080, debug=True)
