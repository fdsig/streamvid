import cv2
import threading
from camera import Camera, JetsonCSI
import logging
from logger_config import setup_logging
from args import args

setup_logging()
class VideoStream:
    def __init__(self,
                 camera=JetsonCSI(flip=args.flip, 
                 width=args.width, 
                 height=args.height, 
                 fps=args.fps,
                 camera_id=args.camera_id)):
        camera: JetsonCSI
        self.camera = camera
        self.video_frame = None
        self.video_frame_id = None
        self.running = True
        self.thread_lock = threading.Lock()
        self.capture_thread = threading.Thread(target=self.__capture_frames__)
        #start the video capture thread
        self.capture_thread.start()
        print(f"Capture thread ID: {self.capture_thread.ident}")

    def __capture_frames__(self):
        while self.running:
            frame = self.camera.capture()
            print(f"Frame: {frame}")
            with self.thread_lock:
                try:
                    self.video_frame = frame
                except Exception as e:
                    logging.error(f"Error capturing frame: {e}")

    def __get_frame__(self):
        print(f"Getting frame: {self.video_frame}")
        print('going into __get_frame__')
        with self.thread_lock:
            if self.video_frame is None:
                return None
            if args.image_format == "jpg":
                print(self.video_frame)
                return_key, encoded_image = cv2.imencode(f".{args.image_format}", self.video_frame, [cv2.IMWRITE_JPEG_QUALITY, args.image_quality])
                print(f"Encoded image: {encoded_image}")
            elif args.image_format == "png":
                return_key, encoded_image = cv2.imencode(f".{args.image_format}", self.video_frame)
            if not return_key:
                return None
            return bytearray(encoded_image)
   
    def streamFrames(self):
        while True:
            encoded_image = self.__get_frame__()
            print(f"Encoded image: {encoded_image}")
            if encoded_image is None:
                continue
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n')

    def stop(self):
        self.running = False
        self.capture_thread.join()


