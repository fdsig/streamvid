from streamer.camera import JetsonCSI
from streamer.utils import cleanup
import time
from streamer.producer import YieldFrames

cleanup()

def test_camera():
    camera = JetsonCSI(width=1920, height=1080, fps=30, camera_id=0)
    camera.start()
    print(f"Camera thread ID: {camera.cam_thread.ident}")
    time.sleep(2)
    for i in range(5):
        frame = camera.read()
        print(f"frame shape from read: {frame.shape}")
    camera.stop()

def test_pipeline():
    camera = JetsonCSI(width=1920, height=1080, fps=30, camera_id=0)
    assert camera.pipeline == "nvgstcapture-1.0 --mode=2 --video-enc=1 --file-type=0 --capture-time=5 --file-name=-"

def test_producer():
    camera = JetsonCSI(width=1920, height=1080, fps=30, camera_id=0)
    camera.start()
    time.sleep(2)
    for i in range(5):
        frame = next(YieldFrames(camera))
        print(f"frame shape from producer: {type(frame)}")
    camera.stop()

if __name__ == "__main__":
    test_camera()
    test_producer()
