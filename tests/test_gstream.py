from streamer.flask_file_streamer import gstreamer_pipeline


def test_gstreamer_pipeline():
    assert gstreamer_pipeline() == (
        "shmsrc socket-path=/tmp/video_stream ! "
        "video/x-raw, format=I420, width=1280, height=720, framerate=10/1 ! "
        "videoconvert ! "
        "appsink")
    print("test_gstreamer_pipeline() passed.")
    print(gstreamer_pipeline())
    return gstreamer_pipeline()

test_gstreamer_pipeline()