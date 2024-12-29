import cv2
import os

# Directory to save the jpg images
img_directory = "captured_images"
os.makedirs(img_directory, exist_ok=True)

gst_pipeline = (
    "shmsrc socket-path=/tmp/video_stream ! "
    "video/x-raw, format=I420, width=1280, height=720, framerate=10/1 ! "
    "videoconvert ! appsink"
)

# Create VideoCapture object
cap = cv2.VideoCapture(gst_pipeline, cv2.CAP_GSTREAMER)

if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# Define the codec using VideoWriter_fourcc and create a VideoWriter object
# Save the video as an MP4 file
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or use 'x264'
out = cv2.VideoWriter('output.mp4', fourcc, 10, (1280, 720))

frame_count = 0
max_frames = 100  # Save 100 frames

while frame_count < max_frames:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break

    # Save frame as JPG image
    img_path = os.path.join(img_directory, f"frame_{frame_count:03d}.jpg")
    cv2.imwrite(img_path, frame)

    # Write the frame to the output MP4 file
    out.write(frame)

    frame_count += 1

# Release everything
cap.release()
out.release()
