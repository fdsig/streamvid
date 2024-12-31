from queue import Queue
import time
from threading import Thread, current_thread, Barrier, Lock
from streamer.camera import JetsonCSI

def read_camera(camera, frame_queue, lock):
    while True:
        result = camera.read()
        if result is not None:
            frame_hash, frame = result
            with lock:
                frame_queue.put((frame_hash, frame))
        else:
            print("Error: Could not read image from camera")
        time.sleep(1 / camera.fps)  # Sleep to match the camera's FPS

def process_frame(frame_queue, barrier, lock):
    while True:
        with lock:
            if not frame_queue.empty():
                frame_hash, frame = frame_queue.queue[0]  # Peek at the first item
            else:
                frame_hash, frame = None, None

        if frame is not None:
            # Process the frame (e.g., display it, save it, etc.)
            print(f"Frame captured")
            print(f'frame hash: {frame_hash}')
            print(f'thread id: {current_thread().ident}')

        barrier.wait()  # Wait for all threads to finish processing the current frame

        with lock:
            if not frame_queue.empty():
                frame_queue.get()  # Remove the frame after all threads have processed it

        time.sleep(0.01)  # Sleep briefly to avoid busy-waiting

def main():
    # Instantiate the camera
    camera = JetsonCSI(flip=0, width=640, height=480, fps=30, camera_id=0)
    frame_queue = Queue()
    lock = Lock()
    num_threads = 2
    barrier = Barrier(num_threads)

    # Start a separate thread to read from the camera
    camera_thread = Thread(target=read_camera, args=(camera, frame_queue, lock))
    camera_thread.daemon = True
    camera_thread.start()

    # Start threads for data processing
    data_thread_1 = Thread(target=process_frame, args=(frame_queue, barrier, lock))
    data_thread_1.daemon = True
    data_thread_1.start()

    data_thread_2 = Thread(target=process_frame, args=(frame_queue, barrier, lock))
    data_thread_2.daemon = True
    data_thread_2.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        camera.close()
        camera_thread.join()
        data_thread_1.join()
        data_thread_2.join()

if __name__ == "__main__":
    main()
