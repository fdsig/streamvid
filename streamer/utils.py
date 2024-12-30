import cv2
import time
import subprocess
import numpy as np
import json
from pathlib import Path
from hashlib import md5
from typing import List, Tuple, Dict

class FrameSaver:
    def __init__(self):
        self.save_frame_flag = False
    
    def set_session_id(self, session_id):
        self.session_id = session_id

    def set_save_flag(self, save:bool):
        self.save_frame_flag = save

    def get_save_flag(self):
        return self.save_frame_flag
    
    def save_image(self, frame:np.ndarray):
        cv2.imwrite(f'saved_images/{self.session_id}/{time.time()}.jpg', frame)
        self.save_frame_flag = False

def cleanup():
    subprocess.run(["sudo", "systemctl", "restart", "nvargus-daemon"])

def generate_metadata(metadata_path: Path = Path('./metadata/metadata.json')) -> bool:
    ''''
    this careates metadata driectory
    if not already created
    checks if metadata.json exists
    if not, creates it
    '''
    metadata_path = Path(f'./metadata/')
    metadata_path.mkdir(parents=True, exist_ok=True)
    metadata_path = metadata_path / 'metadata.json'
    if not metadata_path.exists():
        # keys are file name
        data_structure = {'image_file_name': {
        'file_path': '',
        'bbox_labels': [],
        'bbox_coords': []}
        }
        with open(metadata_path, 'w') as f:
            json.dump(data_structure, f)
            return True
    else:
        return False

def update_metadata(image_file: Path,
                    metadata_path: Path = Path('./metadata/metadata.json'),
                    label: str = 'label',
                    bbox_coords: List[Dict[str, int]] = 
                    [{'xa': 0, 'ya': 0}, 
                     {'xb': 0, 'yb': 0}, 
                     {'xc': 0, 'yc': 0}, 
                     {'xd': 0, 'yd': 0}]):
   
    assert type(bbox_coords) == list, 'coords must be list'
    assert type(bbox_coords[0]) == dict, 'coords[0] must be dict'
    assert type(bbox_coords[0]['xa']) == int, 'xa must be int' 
    assert type(bbox_coords[0]['ya']) == int, 'ya must be int'
    
    print('opening metadata_path', metadata_path)
    with open(metadata_path, 'r') as f:

        '''add entry if not already present to metadata
        '''
        metadata = json.load(f)
    #check if image_file_name is in metadata
    print('image_file', image_file)
    if image_file.name not in metadata:
        metadata[image_file.name] = {'file_path': str(image_file),
                                        'bboxes': {label: bbox_coords}}

    if label not in metadata[image_file.name]['bboxes']:
        metadata[image_file.name]['bboxes'][label] = bbox_coords

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f)
    
    return True

# GStreamer Pipeline to access the Raspberry Pi camera
class VideoCaptureCM:
    def __init__(self, pipeline, backend):
        self.cap = cv2.VideoCapture(pipeline, backend)

    def __enter__(self):
        return self.cap

    def __exit__(self):
        self.cap.release()
