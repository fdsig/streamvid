from argparse import ArgumentParser

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('--camera_id', type=int, default=0)
    parser.add_argument('--debug_mode', type=bool, default=False)
    parser.add_argument('--width', type=int, default=640)
    parser.add_argument('--height', type=int, default=480)
    parser.add_argument('--fps', type=int, default=30)
    return parser.parse_args()
