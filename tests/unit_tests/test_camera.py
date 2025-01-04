from streamer.camera import JetsonCSI
import time
def test_camera():
    camera = JetsonCSI(width=1920, height=1080, fps=30, camera_id=0)
    camera.start()
    print(f"Camera thread ID: {camera.cam_thread.ident}")
    time.sleep(10)
    camera.stop()

def test_pipeline():
    camera = JetsonCSI(width=1920, height=1080, fps=30, camera_id=0)
    assert camera.pipeline == "nvgstcapture-1.0 --mode=2 --video-enc=1 --file-type=0 --capture-time=5 --file-name=-"

if __name__ == "__main__":
    test_camera()
