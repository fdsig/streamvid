# Import the needed libraries
import time
from threading import Thread, Lock, current_thread
from queue import Queue
import cv2
import logging
logger = logging.getLogger(__name__)



''' credit to 
https://github.com/thehapyone/NanoCamera/blob/master/nanocamera/NanoCam.py
from where this code was adapted
this solves the threading issue with the camera with one thread = one class instance
'''

class VideoCaptureCM:
    def __init__(self, pipeline, backend):
        self.cap = cv2.VideoCapture(pipeline, backend)

    def __enter__(self):
        return self.cap

    def __exit__(self, exc_type, exc_value, traceback):
        self.cap.release()


# def captureFrames():
#     global video_frame, thread_lock, save_frame_flag
#     gstream_parms = Gstreamer()
#     gst_str = gstream_parms.gstreamer_pipeline()
#     # Video capturing from OpenCV
#     with VideoCaptureCM(gst_str, cv2.CAP_GSTREAMER) as video_capture:
#         while True and video_capture.isOpened():
#             return_key, frame = video_capture.read()
#             if not return_key:
#                 break
#         # Create a copy of the frame and store it in the global variable,
#         # with thread safe access
#             with thread_lock:
#                 video_frame = frame.copy()
#         video_capture.release()


class JetsonCSI:
    def __init__(self, flip=0, width=640, height=480, fps=30, camera_id=0):
        # Initialize camera parameters
        self.flip = flip
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_id = camera_id
        self.backend = cv2.CAP_GSTREAMER
        self.cap = None
        self.lock = Lock()
        self.running = True
        # Start the camera thread
        self.start()

    def __pipeline__(self):
        return (f'nvarguscamerasrc sensor-id={self.camera_id} ! '
                'video/x-raw(memory:NVMM), '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'format=(string)NV12, framerate=(fraction){self.fps}/1 ! '
                f'nvvidconv flip-method={self.flip} ! '
                f'video/x-raw, width=(int){self.width}, height=(int){self.height}, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink')
    
    def start(self):
        self.cam_thread = Thread(target=self.__read)
        self.cam_thread.daemon = True
        self.cam_thread.start()
        print(f"Camera thread ID: {self.cam_thread.ident}")
    
    def __read(self):
        # Read a frame from the camera
        self.__camera_open()
        while self.running:
            if not self.cap.isOpened():
                logger.error("Camera is not opened successfully")
                time.sleep(1)
                continue
            return_key, image = self.cap.read()
            if return_key:
                with self.lock:
                    self.video_frame = image.copy()
            else:
                logger.error("Error: Could not read image from camera")
                return None
        
    def __camera_open(self):
        self.cap = cv2.VideoCapture(self.__pipeline__(), self.backend)

    def read(self):
        #read the camera stream
        with self.lock:
            return self.video_frame
    
    def queueFrames(self):
        print(f"going into queueFrames")
        while self.running:
            try:
                self.video_frame = self.__read()
                if self.video_frame is None:
                    logger.error("No frame captured")
                    continue
                print(f"frame captured of shape: {self.video_frame.shape}")
                return_key, encoded_image = cv2.imencode(".jpg", self.video_frame)
                if not return_key:
                    logger.error("Failed to encode image")
                    continue
                if encoded_image is None:
                    logger.error("Encoded image is None")
                    continue
                encoded_image = bytearray(encoded_image)
                print('putting frame into queue')
                if not self.frame_queue.full():
                    self.frame_queue.put(encoded_image)
                else:
                    logger.warning("Frame queue is full, skipping frame")
            except Exception as e:
                logger.error(f"Exception in queueFrames: {e}")



