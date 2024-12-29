import cv2
import threading
from flask import Response, Flask, render_template

# Image frame sent to the Flask object
global video_frame
video_frame = None

# Use a lock for thread-safe viewing of frames in multiple browsers
global thread_lock
thread_lock = threading.Lock()

# GStreamer Pipeline for the Jetson camera
GSTREAMER_PIPELINE = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM), width=3280, height=2464, format=(string)NV12, framerate=21/1 ! "
    "nvvidconv flip-method=0 ! "
    "video/x-raw, width=960, height=616, format=(string)BGRx ! "
    "videoconvert ! video/x-raw, format=(string)BGR ! "
    "appsink wait-on-eos=false max-buffers=1 drop=True"
)

# Create the Flask object
app = Flask(__name__, template_folder='templates')

def captureFrames():
    """
    Continuously capture frames from the Jetson camera (via GStreamer) 
    and store them in a global variable for streaming.
    """
    global video_frame, thread_lock
    video_capture = cv2.VideoCapture(GSTREAMER_PIPELINE, cv2.CAP_GSTREAMER)

    while True and video_capture.isOpened():
        return_key, frame = video_capture.read()
        if not return_key:
            # If we fail to read a frame, just break out
            break

        # Lock the global variable and store a copy of the frame
        with thread_lock:
            video_frame = frame.copy()

    video_capture.release()

def encodeFrame():
    """
    Generator function to encode the current frame as JPEG,
    and yield it to be served as a streaming response.
    """
    global thread_lock
    while True:
        with thread_lock:
            global video_frame
            if video_frame is None:
                # If no frame is ready, skip and keep trying
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Output the encoded image in multipart/x-mixed-replace format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n'
               + bytearray(encoded_image)
               + b'\r\n')

@app.route("/")
def index():
    """
    Render the main HTML page (index.html).
    """
    return render_template('index.html')

@app.route("/video_feed")
def video_feed():
    """
    Return the streaming response (mjpeg stream) with the generate function.
    """
    return Response(encodeFrame(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':
    # Create a thread to capture frames in the background
    process_thread = threading.Thread(target=captureFrames)
    process_thread.daemon = True
    process_thread.start()

    # Start the Flask app
    # Access at http://<jetson-ip>:8000/
    app.run(host="0.0.0.0", port=8000, debug=True)
