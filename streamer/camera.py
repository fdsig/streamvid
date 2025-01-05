# Import the needed libraries
import time
from threading import Thread, Lock
from utils import cleanup
import cv2
from logger import logger



''' credit to 
https://github.com/thehapyone/NanoCamera/blob/master/nanocamera/NanoCam.py
which informed the approach to the camera capture.
This solves the threading issue with the camera with one thread = one class instance
'''

class VideoCaptureCM:
    '''
    This class is a wrapper around the cv2.VideoCapture class.
    It is used to capture frames from the camera.
    Designed to be used with context manager.
    example:
    with VideoCaptureCM(pipeline, backend) as cap:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            # process the frame
    '''
    def __init__(self, pipeline, backend):
        self.cap = cv2.VideoCapture(pipeline, backend)

    def __enter__(self):
        return self.cap

    def __exit__(self, exc_type, exc_value, traceback):
        print(f"releasing camera")
        print(f"exc_type: {exc_type}")
        print(f"exc_value: {exc_value}")
        print(f"traceback: {traceback}")
        self.cap.release()
        cleanup()



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
    '''
    This class a python camera capture class that uses the Jetson CSI camera.
    It useses a threadsafe approach to capture frames from the camera.

    example:
    camera = JetsonCSI(flip=0, width=640, height=480, fps=30, camera_id=0)
    while camera.running:
        frame = camera.read()
        # process the frame
    camera.stop()
    -- or --
    frame_gen = YieldFrames(camera)
    for frame in frame_gen:
        # process the frame
    '''
    def __init__(self, flip=0, width=640, height=480, fps=30, camera_id=0,
                 capture_handler=VideoCaptureCM):
        # Initialize camera parameters
        self.flip = flip
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_id = camera_id
        # set the backend to gstreamer -- this might change as camera driver changes
        self.backend = cv2.CAP_GSTREAMER
        # set the capture handler to the VideoCaptureCM class   
        self.capture_handler = capture_handler
        # set the lock to a lock object
        self.lock = Lock()
        # set the running flag to True
        self.running = True
        # Start the camera thread
        self.start()

    def __pipeline(self):
        '''
        This function returns the gstreamer pipeline string for the camera.
        '''
        return (f'nvarguscamerasrc sensor-id={self.camera_id} ! '
                'video/x-raw(memory:NVMM), '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'format=(string)NV12, framerate=(fraction){self.fps}/1 ! '
                f'nvvidconv flip-method={self.flip} ! '
                f'video/x-raw, width=(int){self.width}, height=(int){self.height}, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink')
    
    def start(self):
        '''
        This function starts the camera thread.
        '''
        self.cam_thread = Thread(target=self.__read)
        self.cam_thread.daemon = True
        self.cam_thread.start()
        print(f"Camera thread ID: {self.cam_thread.ident}")
    
    def __read(self):
        '''
        This function reads a frame from the camera.
        '''
        # Read a frame from the camera
        with self.capture_handler(self.__pipeline(), self.backend) as cap:
            while self.running:
                if not cap.isOpened():
                    logger.error("Camera is not opened successfully")
                    time.sleep(1)
                    continue
                return_key, image = cap.read()
                if return_key:
                    with self.lock:
                        self.video_frame = image
                else:
                    logger.error("Error: Could not read image from camera")
                    self.video_frame = None
        
    def read(self) -> np.ndarray:
        '''
        This function reads a frame from the camera.
        '''
        #read the camera stream
        with self.lock:
            if self.video_frame:
                return self.video_frame
            else:
                return None
    
    def stop(self):
        '''
        This function stops the camera thread.
        '''
        self.running = False
        self.cam_thread.join()
