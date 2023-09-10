import cv2

# IP and port of the machine you want to send the stream to
destination_ip = "192.168.1.100"  # Replace with the receiver's IP
destination_port = "5000"         # Replace with the desired port

# Define the GStreamer pipeline
gst_out = (
    "appsrc ! videoconvert ! "
    "x264enc speed-preset=ultrafast tune=zerolatency ! "
    "rtph264pay ! udpsink host=" + destination_ip + " port=" + destination_port
)

# Define the GStreamer pipeline for capturing video
gst_str = (
    "nvarguscamerasrc ! "
    "video/x-raw(memory:NVMM),format=(string)NV12,width=1920,height=1080,framerate=30/1 ! "
    "nvvidconv ! videoconvert ! "
    "appsink"
)

# Open capture
cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)

# Check if camera opened successfully
if not cap.isOpened():
    print("Error: Couldn't open camera.")
    exit()

# Create videowriter as a shmsink
out = cv2.VideoWriter(gst_out, cv2.CAP_GSTREAMER, 0, 30, (1920, 1080), True)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Couldn't read frame.")
        break

    # Process the frame here (e.g., display it)
    #Cv2.imshow('Camera', frame)
    out.write(frame)  # Send frame
    print(frame)
