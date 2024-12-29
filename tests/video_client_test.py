import socket
import struct
import pickle

def test_video_capture_client(host='localhost', port=5006):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    print("Connected to the server")

    data = b""
    payload_size = struct.calcsize("L")
    print(f"Payload size: {payload_size}")
    while True:
        # Retrieve message size
        while len(data) < payload_size:
            packet = client_socket.recv(4096)
            print(f"Received packet: {len(packet)}")
            if not packet:
                break
            data += packet

        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack("L", packed_msg_size)[0]

        # Retrieve all data based on message size
        while len(data) < msg_size:
            data += client_socket.recv(4096)

        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Deserialize the frame
        frame = pickle.loads(frame_data)
        print(f"Received frame of size: {frame.shape}")

    client_socket.close()

if __name__ == '__main__':
    test_video_capture_client()
