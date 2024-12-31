import cv2
import threading
from camera import JetsonCSI
import logging
from logger_config import setup_logging

setup_logging()
class VideoStream:
    def __init__(self,
                 flip=0, 
                 width=640, 
                 height=480, 
                 fps=30,
                 camera_id=0):
        flip: int
        width: int
        height: int
        fps: int
    
        self.flip = flip
        self.width = width
        self.height = height
        self.fps = fps
        self.camera_id = camera_id

        self.camera = JetsonCSI(flip=self.flip, 
                             width=self.width, 
                             height=self.height, 
                             fps=self.fps,
                             camera_id=self.camera_id)
        self.video_frame = None
        self.running = True
        # self.thread_lock = threading.Lock()
        # self.capture_thread = threading.Thread(target=self.capture_frames)
        # #start the video capture thread
        # self.capture_thread.start()
        # print(f"Capture thread ID: {self.capture_thread.ident}")

    def capture_frames(self):
        while self.running:
            frame = self.camera.camera_open()
            print(f"Frame in capture_frames: {frame}")
            #with self.thread_lock:
            try:
                self.video_frame = frame.copy()
            except Exception as e:
                logging.error(f"Error capturing frame: {e}")

    def __get_frame__(self):
        # with self.thread_lock:
        print(f"Video frame: {self.video_frame}")
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


