import cv2
import time
from flask import Flask, Response

app = Flask(__name__)

###############################################################################
# 1) GStreamer Pipeline
###############################################################################
# By default, Jetson might automatically pick a "mode=4" at 1280x720 @ 120 fps,
# which can cause "Failed to create CaptureSession" on some sensor setups.
# Let's force a more stable mode (e.g. 1920x1080 @ 30 fps) by specifying sensor-mode=2
# (or whichever mode matches your camera’s capabilities). 
#
# The sensor-mode values depend on your camera and driver. From your logs:
#   Mode 0: 3264x2464 @ 21 fps
#   Mode 1: 3264x1848 @ 28 fps
#   Mode 2: 1920x1080 @ ~30 fps
#   Mode 3: 1280x720  @ ~60 fps
#   Mode 4: 1280x720  @ ~120 fps
#
# We'll pick sensor-mode=2 to get 1920x1080 @ 30 fps (which is usually stable).
###############################################################################
GST_PIPELINE = (
    "nvarguscamerasrc sensor-mode=2 ! "  # Force mode=2 for 1920x1080 @ 30 fps
    "video/x-raw(memory:NVMM), width=(int)1920, height=(int)1080, framerate=(fraction)30/1 ! "
    "nvvidconv ! video/x-raw, format=(string)BGRx ! "
    "videoconvert ! video/x-raw, format=(string)BGR ! appsink"
)

cap = cv2.VideoCapture(GST_PIPELINE, cv2.CAP_GSTREAMER)


###############################################################################
# 2) Generator for Streaming
###############################################################################
# Reads from the camera in a loop, encodes to JPG, and yields frames as a
# multipart/x-mixed-replace stream.
###############################################################################
def generate_frames():
    while True:
        ret, frame = cap.read()
        if not ret:
            # If a frame can’t be read, wait briefly then retry.
            print("Error: Couldn't read frame.")
            time.sleep(0.1)
            continue

        success, encoded_image = cv2.imencode('.jpg', frame)
        if not success:
            print("Error: Couldn't encode frame.")
            time.sleep(0.1)
            continue

        # Yield the current frame in multipart/x-mixed-replace format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               encoded_image.tobytes() +
               b'\r\n\r\n')


###############################################################################
# 3) Flask Routes
###############################################################################
@app.route('/')
def index():
    """
    Inline HTML (no external template). Shows the video stream at /video_feed.
    """
    # Simple HTML that references the /video_feed route for the <img> source.
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Jetson Nano CSI Camera</title>
        <style>
            body {
                background: #f0f0f0;
                font-family: sans-serif;
                text-align: center;
            }
            .video-container {
                margin-top: 40px;
            }
            img {
                border: 2px solid #333;
                max-width: 90%;
                height: auto;
            }
        </style>
    </head>
    <body>
        <h1>Jetson Nano Live Stream</h1>
        <div class="video-container">
            <!-- The video stream is displayed here -->
            <img src="/video_feed" alt="Live Stream" />
        </div>
    </body>
    </html>
    """
    return html_content


@app.route('/video_feed')
def video_feed():
    """
    Returns a streaming response using the generate_frames() generator.
    """
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


###############################################################################
# 4) Main Entry
###############################################################################
if __name__ == '__main__':
    # For a simple test environment:
    # - Runs on 0.0.0.0 so you can access from other devices on the network.
    # - Debug mode prints extra logs. Remove debug=True in production.
    app.run(host='0.0.0.0', port=9080, debug=True)
