import cv2

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

def generate(cap):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't read frame.")
            continue
        ret, jpeg = cv2.imencode('.jpg', frame)
        if not ret:
            print("Error: Couldn't encode frame.")
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        

