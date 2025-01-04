import cv2
import logging

def YieldFrames(camera):
    while camera.running:
        frame = camera.read()
        encoded_image = cv2.imencode('.jpg', frame)[1].tobytes()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n')


