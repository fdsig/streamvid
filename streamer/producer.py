import cv2
import threading
from camera import Camera, JetsonCSI
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
        print(f"going into capture_frames")
        

    def __get_frame__(self):
        print(f"going into __get_frame__")
        
   
    def streamFrames(self):
        while self.running:
            self.video_frame = self.camera.capture()
            print(f"frame captured of shape: {self.video_frame.shape}")
            return_key, encoded_image = cv2.imencode(".jpg", self.video_frame)
            print(f"return_key: {return_key}")
            print(f"encoded_image: {encoded_image}")
            encoded_image = bytearray(encoded_image)
            if not return_key:
                return None
            if encoded_image is None:
                continue
            print('yielding encoded image')
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n')

    def stop(self):
        self.running = False
        self.capture_thread.join()


