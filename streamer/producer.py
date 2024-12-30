import cv2
import threading
from camera import Camera
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
    def __init__(self, camera_type=0, 
                 device_id=0, 
                 flip=0, 
                 width=640, 
                 height=480, 
                 fps=30):
        camera_type: int
        device_id: int
        flip: int
        width: int
        height: int
        fps: int
    
        self.flip = flip
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_type = camera_type
        self.device_id = device_id

        self.camera = Camera(flip=self.flip, 
                             width=self.width, 
                             height=self.height, 
                             fps=self.fps)
        self.video_frame = None
        self.running = True
        self.thread_lock = threading.Lock()
        self.capture_thread = threading.Thread(target=self.capture_frames)
        self.capture_thread.start()
        print(f"Capture thread ID: {self.capture_thread.ident}")

    def capture_frames(self):
        while self.running:
            frame = self.camera.read()
            with self.thread_lock:
                self.video_frame = frame.copy()

    def __get_frame__(self):
        with self.thread_lock:
            if self.video_frame is None:
                return None
            return_key, encoded_image = cv2.imencode(".jpg", self.video_frame)
            if not return_key:
                return None
            return bytearray(encoded_image)
   
    def streamFrames(self):
        while True:
            encoded_image = self.__get_frame__()
            if encoded_image is None:
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n')

    def stop(self):
        self.running = False
        self.capture_thread.join()


