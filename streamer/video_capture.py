import cv2
import socket
import struct
import pickle
import threading
global thread_lock 
import atexit
import subprocess
global video_frame
video_frame = None
thread_lock = threading.Lock()


class VideoCaptureCM:
    def __init__(self,backend):
        self.pipeline = (
            "nvarguscamerasrc ! video/x-raw(memory:NVMM), width=3280, height=2464, "
            "format=(string)NV12, framerate=21/1 ! nvvidconv flip-method=0 ! "
            "video/x-raw, width=960, height=616, format=(string)BGRx ! videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink wait-on-eos=false max-buffers=1 drop=True"
        )
        self.cap = cv2.VideoCapture(self.pipeline, backend)

    def __enter__(self):
        return self.cap

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()


def video_capture_server(host='localhost', port=5006):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print("Video capture server started, waiting for connection...")

    # Accept multiple connections
    while True:
        conn, addr = server_socket.accept()
        print(f"Connection from: {addr}")
        client_thread = threading.Thread(target=handle_client, args=(conn,))
        client_thread.start()

def handle_client(conn):
    print(f"Sending frame: {video_frame.shape}")
    # Use encoded frame generator to stream at socket
    cap = encodeFrame()
    print("Starting to send frames")
    while True:
        frame = next(cap)
        print(f'Frame: {frame.shape}')
        print(f"Sending frame: {frame.shape}")
        data = pickle.dumps(frame)
        # Send message length first
        print(f"Sending message size: {len(data)}")
        message_size = struct.pack("L", len(data))
        # Then data
        try:
            conn.sendall(message_size + data)
        except (BrokenPipeError, ConnectionResetError):
            # Handle disconnection
            print("Connection lost, closing client thread...")
            break
    conn.close()

def captureFrames():
    global video_frame, thread_lock
    print("Starting to capture frames")
    # Video capturing from OpenCV
    with VideoCaptureCM(cv2.CAP_GSTREAMER) as video_capture:
        print("Video capture started")
        while True and video_capture.isOpened():
            return_key, frame = video_capture.read()
            if not return_key:
                break
        # Create a copy of the frame and store it in the global variable,
        # with thread safe access
            with thread_lock:
                 video_frame = frame.copy()
                 print(f"Frame captured: {video_frame.shape}")
        video_capture.release()

def encodeFrame():
    global thread_lock
    while True:
        # Acquire thread_lock to access the global video_frame object
        with thread_lock:
            global video_frame
            if video_frame is None:
                continue
            return_key, encoded_image = cv2.imencode(".jpg", video_frame)
            if not return_key:
                continue

        # Output image as a byte array
        print(f"Sending frame: {encoded_image.shape}")
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encoded_image) + b'\r\n')

def cleanup():
    subprocess.run(["sudo", "systemctl", "restart", "nvargus-daemon"])
    server_socket.close()
    

if __name__ == '__main__':
    atexit.register(cleanup)
    thread_lock = threading.Lock()
    # Create a thread and attach the method that captures the image frames, to it
    process_thread = threading.Thread(target=captureFrames)
    process_thread.daemon = True
    # Start the thread
    process_thread.start()
    print("Starting video capture server"*10)
    video_capture_server()
