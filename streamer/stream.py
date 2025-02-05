import cv2
from flask import (Response, Flask, render_template, 
                   jsonify, request,
                   make_response, url_for)
import json
from utils import (cleanup, generate_metadata, update_metadata)
import atexit
from pathlib import Path
from camera import JetsonCSI
from producer import YieldFrames
import base64
from base64 import b64encode
import numpy as np
from uuid import uuid4
from logger import logger
# Image frame sent to the Flask object
video_frame = None
save_frame_flag = False
# Use locks for thread-safe viewing of frames in multiple browsers

# Create the Flask object for the application

app = Flask(__name__, template_folder='templates')
app.config['TEMPLATES_AUTO_RELOAD'] = True

@app.route("/")
def index():
    print(url_for('static', filename='js/utils.js'))
    print(url_for('static', filename='js/main.js'))
    session_id = str(uuid4())
    response = make_response(render_template("index.html"))
    response.set_cookie('session_id', session_id, samesite='Lax')
    return response

# this should be a
@app.route("/video_feed")
def video_feed():
    print('going into video_feed')
    return Response(YieldFrames(camera), mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route('/draw')
def draw():
    try:
        session_id = request.cookies.get('session_id')
    except TypeError:
        logger.error(f"session_id not found in cookies")
        session_id = str(uuid4())
    except Exception as e:
        logger.error(f"Error getting session_id: {e}")
        session_id = str(uuid4())

    print('draw session_id from draw', session_id)
    response = make_response(render_template('draw.html'))
    response.set_cookie('session_id', session_id, samesite='Lax')
    return response
    
@app.route('/list_images')
def list_images():
    """ this should only list image saved in a particlular brouser session
    by checking the browser session id"""
    session_id = request.cookies.get('session_id')
    print('session_id', session_id)
    all_images_path = Path(f'./saved_images/')
    #create list scanning subdirectories
    images = []
    for subdir in all_images_path.iterdir():
        if subdir.is_dir():
            images.extend([im for im in subdir.iterdir() if im.is_file()])
    for im_path in images:
        assert im_path.exists(), f"Session ID {session_id} does not exist"
    image_names = [f'{img_path.parent}/{img_path.name}' for img_path in images]
    image_file_names = [f'{img_path.name}' for img_path in images]
    real_images = [cv2.imread(im_path) for im_path in image_names]
    real_images = [cv2.cvtColor(im, cv2.COLOR_BGR2RGB) for im in real_images if im is not None]
    real_images = [cv2.imencode('.jpg', im)[1].tobytes() for im in real_images]
    # Encode image bytes to base64
    real_images_base64 = [b64encode(im).decode('utf-8') for im in real_images]
    #replace with a generator
    print('sending images')
    metadata_path=Path('./metadata/metadata.json')
    if not metadata_path.exists():
        generate_metadata(metadata_path)
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    updated = False
    for path in images:
        if not path.name in metadata:
            update_metadata(path, 
                            metadata_path=metadata_path,
                            bbox_coords=[{'xa': 0, 'ya': 0}, 
                                         {'xb': 0, 'yb': 0}, 
                                         {'xc': 0, 'yc': 0}, 
                                         {'xd': 0, 'yd': 0}],
                            label='label')
            updated = True
    # load updated metadata
    if updated:
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
    # each image needs metadata as this is shown for each image
    # in the draw.html template.
    return jsonify(image_file_names=image_file_names, 
                   image_names=image_names,
                   real_images_base64=real_images_base64,
                   metadata=metadata)



@app.route('/save_image', methods=['POST'])
def save_image():
    ''' this should receive
     body: JSON.stringify({ session_id: session_id, image_data: imageDataURL })
     from the frontend and save the image to the server'''
    print("Saving image")
    session_id = request.json.get('session_id')
    image_data = request.json.get('image_data')
    image_label = request.json.get('image_label')
    image_file_path = request.json.get('image_file_path')
    bbox_coords = request.json.get('bbox_coords')
    print(f'bboxes: {bbox_coords}')
    if not bbox_coords:
        bbox_coords = [{'xa': 0, 'ya': 0}, 
                      {'xb': 0, 'yb': 0}, 
                      {'xc': 0, 'yc': 0}, 
                      {'xd': 0, 'yd': 0}]
    print(f"session_id: {session_id}")
    print(f"image_label: {image_label}")
    # Decode the base64 image data
    try:
        image_data = base64.b64decode(image_data)
        image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
        
        # Check if the image was decoded successfully
        if image is None:
            raise ValueError("Image decoding failed. The image data might be corrupted or improperly formatted.")
        
        # Ensure the directory exists
        if not image_file_path:
            print('image_file_path not provided')
            save_path = Path(f'saved_images/{session_id}')
            save_path.mkdir(parents=True, exist_ok=True)
            # crate unique id from datetime
            save_path = save_path / f'{uuid4()}.jpg'
            print('save_path', save_path)
        else:
            print('image_file_path provided')
            print('image_file_path', image_file_path)
            save_path = Path(image_file_path)
            print('save_path', save_path)
        
        
        # Save the image
        print('saving image', save_path,type(save_path))
        cv2.imwrite(save_path.as_posix(), image)
        # update metadata
        print('updating metadata')
        update_metadata(save_path, 
                        metadata_path=Path('./metadata/metadata.json'), 
                        label=image_label, 
                        bbox_coords=bbox_coords)

        return jsonify({'message': 'Image saved successfully'})
    
    except Exception as e:
        print(f"Error decoding or saving image: {e}")
        return jsonify({'error': 'Failed to save image'}), 500

# @app.route('/favicon.ico')
# def favicon():
#     return send_from_directory(os.path.join(app.root_path, 'static'),
#                                'favicon.ico', mimetype='image/vnd.microsoft.icon')

# check to see if this is the main thread of execution
if __name__ == '__main__':
    generate_metadata(Path('./metadata/metadata.json'))
    atexit.register(cleanup)
    # Create a thread and attach the method that captures the image frames, to it
    # process_thread = threading.Thread(target=captureFrames)
    # process_thread.daemon = True
    # # Start the thread
    # process_thread.start()
    camera = JetsonCSI(flip=0, width=640, height=480, fps=16)
    # For multiple CSI camera
    # camera_2 = nano.Camera(device_id=1, flip=0, width=1280, height=800, fps=30)
    print('CSI Camera is now ready')
    # start the Flask Web Application
    # While it can be run on any feasible IP, IP = 0.0.0.0 renders the web app on
    # the host machine's localhost and is discoverable by other machines on the same network 
    app.run("0.0.0.0", port="8000")
