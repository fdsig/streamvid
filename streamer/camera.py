# Import the needed libraries
import time
from threading import Thread
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

CSI: int = 0
USB: int = 1
RTSP: int = 2
MJPEG: int = 3 

class Camera:
   
    def __init__(self, 
                 camera_type=0, 
                 device_id=0, 
                 flip=0, 
                 width=640, 
                 height=480, 
                 fps=30,
                 enforce_fps=False, 
                 debug=False):
        # initialize all variables
        self.fps = fps
        self.camera_type = camera_type
        self.camera_id = device_id
        # for streaming camera only
        self.flip_method = flip
        self.width = width
        self.height = height
        self.enforce_fps = enforce_fps

        self.debug_mode = debug
        # track error value
        '''
        -1 = Unknown error
        0 = No error
        1 = Error: Could not initialize camera.
        2 = Thread Error: Could not read image from camera
        3 = Error: Could not read image from camera
        4 = Error: Could not release camera
        '''
        #Need to keep an history of the error values
        self.__error_value = [0]
        #created a thread for enforcing FPS camera read and write
        self.cam_thread = None
        # holds the frame data
        self.frame = None
        #tracks if a CAM opened was succesful or not
        self.__cam_opened = False
        #create the OpenCV camera inteface
        self.cap = None
        #open the camera interface
        self.open()
        # enable a threaded read if enforce_fps is active
        if self.enforce_fps:
            self.start()

    def __csi_pipeline(self, sensor_id=0):
        return (f'nvarguscamerasrc sensor-id={sensor_id} ! '
                'video/x-raw(memory:NVMM), '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'format=(string)NV12, framerate=(fraction){self.fps}/1 ! '
                f'nvvidconv flip-method={self.flip_method} ! '
                f'video/x-raw, width=(int){self.width}, height=(int){self.height}, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink')

    def __usb_pipeline(self, device_name="/dev/video1"):
        return (f'v4l2src device={device_name} ! '
                'video/x-raw, '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'format=(string)YUY2, framerate=(fraction){self.fps}/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink')

    def __rtsp_pipeline(self, location="localhost:8080"):
        return (f'rtspsrc location=rtsp://{location} ! '
                'rtph264depay ! h264parse ! omxh264dec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'framerate=(fraction){self.fps}/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink')

    def __mjpeg_pipeline(self, location="localhost:8080"):
        return ('souphttpsrc location=%s do-timestamp=true is_live=true ! '
                'multipartdemux ! jpegdec ! '
                'videorate ! videoscale ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % ("http://" + location, self.width, self.height, self.fps))

    def __usb_pipeline_enforce_fps(self, device_name="/dev/video1"):
        return ('v4l2src device=%s ! '
                'video/x-raw, '
                'width=(int)%d, height=(int)%d, '
                'format=(string)YUY2, framerate=(fraction)%d/1 ! '
                'videorate ! '
                'video/x-raw, framerate=(fraction)%d/1 ! '
                'videoconvert ! '
                'video/x-raw, format=BGR ! '
                'appsink' % (device_name, self.width, self.height, self.fps, self.fps))

    def open(self):
        # open the camera inteface
        # determine what type of camera to open
        if self.camera_type == CSI:
            # then CSI camera
            self.__open_csi()
        elif self.camera_type == USB:
            # it is USB camera
            self.__open_usb()
        elif self.camera_type == RTSP:
            # rtsp camera
            self.__open_rtsp()
        elif self.camera_type == MJPEG:
            # http camera
            self.__open_mjpeg()
        else:
            raise Exception("Not Support Camera Type %d", self.camera_type)
        return self

    def start(self):
        print(f"Starting camera thread"*10)
        self.cam_thread = Thread(target=self.__thread_read)
        self.cam_thread.daemon = True
        self.cam_thread.start()
        print(f"Camera thread ID: {self.cam_thread.ident}")
        return self

    # Tracks if camera is ready or not(maybe something went wrong)
    def isReady(self):
        return self.__cam_opened

    # Tracks the camera error state.
    def hasError(self):
        # check the current state of the error history
        latest_error = self.__error_value[-1]
        if latest_error == 0:
            # means no error has occured yet.
            return self.__error_value, False
        else:
            return self.__error_value, True

    def __open_csi(self):
        # opens an inteface to the CSI camera
        try:
            # initialize the first CSI camera
            self.cap = cv2.VideoCapture(self.__csi_pipeline(self.camera_id), cv2.CAP_GSTREAMER)
            if not self.cap.isOpened():
                # raise an error here
                # update the error value parameter
                self.__error_value.append(1)
                raise RuntimeError()
            self.__cam_opened = True
        except RuntimeError as e:
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError('Error: Could not initialize CSI camera.')
        except Exception as e:
            # some unknown error occurred
            logger.error("Unknown Error has occurred")
            self.__cam_opened = False
            if self.debug_mode:
                raise RuntimeError("Unknown Error has occurred")


    def __thread_read(self):
        # uses thread to read
        time.sleep(1.5)
        while self.__cam_opened:
            try:
                self.frame = self.__read()

            except Exception:
                # update the error value parameter
                self.__error_value.append(2)
                self.__cam_opened = False
                if self.debug_mode:
                    raise RuntimeError('Thread Error: Could not read image from camera')
                break
        # reset the thread object:
        self.cam_thread = None

    def __read(self):
        # reading images
        ret, image = self.cap.read()
        if ret:
            return image
        else:
            # update the error value parameter
            self.__error_value.append(3)

    def read(self):
        # read the camera stream
        try:
            # check if debugging is activated
            if self.debug_mode:
                # check the error value
                if self.__error_value[-1] != 0:
                    raise RuntimeError("An error as occurred. Error Value:", self.__error_value)
            if self.enforce_fps:
                # if threaded read is enabled, it is possible the thread hasn't run yet
                if self.frame is not None:
                    return self.frame
                else:
                    # we need to wait for the thread to be ready.
                    return self.__read()
            else:
                return self.__read()
        except Exception as ee:
            if self.debug_mode:
                raise RuntimeError(ee.args)

    def release(self):
        # destroy the opencv camera object
        try:
            # update the cam opened variable
            self.__cam_opened = False
            # ensure the camera thread stops running
            if self.enforce_fps:
                if self.cam_thread is not None:
                    self.cam_thread.join()
            if self.cap is not None:
                self.cap.release()
            # update the cam opened variable
            self.__cam_opened = False
        except RuntimeError:
            # update the error value parameter
            self.__error_value.append(4)
            if self.debug_mode:
                raise RuntimeError('Error: Could not release camera')


class JetsonCSI:
    def __init__(self, flip=0, width=640, height=480, fps=30, camera_id=0):
        flip : int
        width : int
        height : int
        fps : int
        camera_id : int

        self.flip = flip
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_id = camera_id
        self.__pipeline = self.__pipeline__()
        self.backend = cv2.CAP_GSTREAMER
        self.cap = cv2.VideoCapture(self.__pipeline, self.backend)
        self.cam_thread = Thread(target=self.__read)
        self.cam_thread.daemon = True
        self.cam_thread.start()
        print(f"Camera thread ID: {self.cam_thread.ident}")
    
    def __enter__(self):
        print(f"Camera thread ID: {self.cam_thread.ident}")
        return self.__read()
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            logger.error(f"Exception occurred: {exc_value} {traceback}")
            #this event only happens when camera streaming is shut down
            return True
        self.cap.release()
        self.cam_thread.join()
        return False

    def __dict__(self):
        return {
            'flip': self.flip,
            'width': self.width,
            'height': self.height,
            'fps': self.fps
        }
    
    def __pipeline__(self):
        return (f'nvarguscamerasrc sensor-id={self.camera_id} ! '
                'video/x-raw(memory:NVMM), '
                f'width=(int){self.width}, height=(int){self.height}, '
                f'format=(string)NV12, framerate=(fraction){self.fps}/1 ! '
                f'nvvidconv flip-method={self.flip} ! '
                f'video/x-raw, width=(int){self.width}, height=(int){self.height}, format=(string)BGRx ! '
                'videoconvert ! '
                'video/x-raw, format=(string)BGR ! appsink')
    
    def camera_open(self):
        ''' returns the camera object'''
        return self.__read()
    def camera_close(self):
        ''' releases the camera object'''
        self.cap.release()
    
    def __read(self):
        # reading images
        with self.thread_lock:
            ret, image = self.cap.read()
            print(f"Frame in __read: {image}")
            if ret:
                return image
            else:
                # update the error value parameter
                logger.error("Error: Could not read image from camera")

    def read(self):
        #read the camera stream
        return self.__read()

