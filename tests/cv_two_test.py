import cv2

def test_video_capture(output_file='output.avi', duration=10):
    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Check if the camera opened successfully
    if not cap.isOpened():
        print("Error: Could not open video device.")
        return

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (640, 480))

    print("Recording video...")

    # Capture video for the specified duration
    for _ in range(int(20 * duration)):  # 20 frames per second
        ret, frame = cap.read()
        if not ret:
            print("Error: Couldn't read frame.")
            break

        # Write the frame to the output file
        out.write(frame)

    # Release everything if job is finished
    cap.release()
    out.release()
    print(f"Video saved to {output_file}")

if __name__ == "__main__":
    #capture video for 10 seconds
    test_video_capture(output_file='output.mp4', duration=1)
    
