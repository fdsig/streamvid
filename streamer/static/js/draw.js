let imageObj; // Declare imageObj at the top level
let images; // Declare images at the top level
let currentIndex = 0; // Declare currentIndex at the top level

function resizeCanvas() {
    const canvas = document.getElementById('canvas');
    canvas.width = window.innerWidth * 0.9;
    canvas.height = window.innerHeight * 0.9;
}

window.addEventListener('resize', resizeCanvas);
resizeCanvas(); // Initial resize

let drawMode = false;
let rect = {};
let drag = false;
let boundingBoxCoordinates = null;

function toggleDrawMode() {
    drawMode = !drawMode;
}

document.getElementById('toggleDrawButton').addEventListener('click', toggleDrawMode);

function mouseDown(e) {
    if (!drawMode) return;
    const canvas = document.getElementById('canvas');
    rect.startX = e.pageX - canvas.offsetLeft;
    rect.startY = e.pageY - canvas.offsetTop;
    drag = true;
}

function mouseUp() {
    if (!drawMode) return;
    drag = false;
    boundingBoxCoordinates = [
        { xa: rect.startX, ya: rect.startY },
        { xb: rect.startX, yb: rect.startY + rect.h },
        { xc: rect.startX + rect.w, yc: rect.startY + rect.h },
        { xd: rect.startX + rect.w, yd: rect.startY }
    ];
    console.log('Bounding Box Coordinates:', boundingBoxCoordinates);
}

function mouseMove(e) {
    if (!drag || !drawMode) return;
    const canvas = document.getElementById('canvas');
    const context = canvas.getContext('2d');
    context.clearRect(0, 0, canvas.width, canvas.height);
    if (imageObj) { // Check if imageObj is defined
        context.drawImage(imageObj, 0, 0, canvas.width, canvas.height);
    }
    rect.w = (e.pageX - canvas.offsetLeft) - rect.startX;
    rect.h = (e.pageY - canvas.offsetTop) - rect.startY;
    context.strokeStyle = 'red';
    context.strokeRect(rect.startX, rect.startY, rect.w, rect.h);
}

function initDrawing() {
    const canvas = document.getElementById('canvas');
    canvas.addEventListener('mousedown', mouseDown, false);
    canvas.addEventListener('mouseup', mouseUp, false);
    canvas.addEventListener('mousemove', mouseMove, false);
}

document.getElementById('loadImagesButton').addEventListener('click', function() {
    fetch('/list_images')
        .then(response => response.json())
        .then(data => {
            images = data.real_images_base64; // Assign to the top-level images variable
            const imageNames = data.image_names; // Capture image names here
            console.log('metadata', imageNames);
            currentIndex = 0; // Reset currentIndex

            imageObj = new Image(); // Initialize imageObj here
            imageData = new String(); // this should an instance of the image data

            function showImage() {
                const canvas = document.getElementById('canvas'); // Ensure canvas is defined
                const context = canvas.getContext('2d'); // Get the 2D context here

                imageObj.onload = function() {
                    context.clearRect(0, 0, canvas.width, canvas.height);
                    context.drawImage(imageObj, 0, 0, canvas.width, canvas.height);
                };
                imageObj.src = 'data:image/jpeg;base64,' + images[currentIndex];
            }

            // Populate the sidebar with image thumbnails
            const imageList = document.getElementById('imageList');
            imageList.innerHTML = ''; // Clear previous images
            images.forEach((image, index) => {
                const container = document.createElement('div');
                container.style.textAlign = 'center'; // Center the caption

                const imgElement = document.createElement('img');
                imgElement.src = 'data:image/jpeg;base64,' + image;
                imgElement.style.width = '100%';
                imgElement.style.height = 'auto'; // Maintain aspect ratio
                imgElement.style.objectFit = 'contain'; // Ensure the image fits within the container
                imgElement.style.cursor = 'pointer';
                imgElement.addEventListener('click', function() {
                    currentIndex = index;
                    showImage();
                });

                const caption = document.createElement('div');
                caption.textContent = imageNames[index]; // Use image names for captions
                caption.style.fontSize = '12px';
                caption.style.color = '#555';

                container.appendChild(imgElement);
                container.appendChild(caption);
                imageList.appendChild(container);
            });

            document.getElementById('prevImageButton').addEventListener('click', function() {
                currentIndex = (currentIndex - 1 + images.length) % images.length;
                showImage();
            });

            document.getElementById('nextImageButton').addEventListener('click', function() {
                currentIndex = (currentIndex + 1) % images.length;
                showImage();
            });

            showImage(); // Show the first image initially
            initDrawing();
        });
});

document.getElementById('captureButton').addEventListener('click', function() {
    window.location.href = '/';
});

document.getElementById('saveBoundingBoxButton').addEventListener('click', function() {
    if (!boundingBoxCoordinates) {
        console.log('No bounding box to save.');
        return;
    }

    // Retrieve the session_id from cookies
    const session_id = getCookie('session_id');
    const imageData = images[currentIndex]; // Use the top-level images variable
    const label = document.getElementById('imageLabelInput').value; // Get the label from the input field

    fetch('/save_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            session_id: session_id,
            image_data: imageData,
            image_label: label, // Include the label in the request
            bboxes: boundingBoxCoordinates
        })
    })
    .then(response => response.json())
    .then(data => {
        console.log('Bounding box and image saved:', data);
        
        // Clear the bounding box, label input, and rect object
        boundingBoxCoordinates = null;
        rect = {}; // Reset the rect object
        document.getElementById('imageLabelInput').value = '';

        // Clear the canvas
        const canvas = document.getElementById('canvas');
        const context = canvas.getContext('2d');
        context.clearRect(0, 0, canvas.width, canvas.height);

        // Redraw the current image without the bounding box
        imageObj.onload = function() {
            context.drawImage(imageObj, 0, 0, canvas.width, canvas.height);
        };
        imageObj.src = 'data:image/jpeg;base64,' + images[currentIndex];
    })
    .catch(error => {
        console.error('Error saving bounding box and image:', error);
    });
});
