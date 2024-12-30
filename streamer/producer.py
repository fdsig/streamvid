import cv2
import threading

class Gstreamer: 
    def __init__(self):
        self.set_params()

    def set_params(self,capture_width=1280,
                   capture_height=720,
                   display_width=1280,
                   display_height=720,
                   framerate=10,
                   flip_method=0):
        self.capture_width=capture_width
        self.capture_height=capture_height
        self.display_width=display_width
        self.display_height=display_height
        self.framerate=framerate
        self.flip_method=flip_method

    def gstreamer_pipeline(self):  
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
            self.capture_width,
            self.capture_height,
            self.framerate,
            self.flip_method,
            self.display_width,
            self.display_height,
        )
    )

class VideoStream:
    def __init__(self, camera):
        self.camera = camera
        self.video_frame = None
        self.thread_lock = threading.Lock()
        self.running = True
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.start()

    def capture_frames(self):
        while self.running:
            frame = self.camera.read()
            with self.thread_lock:
                self.video_frame = frame.copy()

    def get_frame(self):
        with self.thread_lock:
            if self.video_frame is None:
                return None
            return_key, encoded_image = cv2.imencode(".jpg", self.video_frame)
            if not return_key:
                return None
            return bytearray(encoded_image)

    def stop(self):
        self.running = False
        self.capture_thread.join()
