document.addEventListener('DOMContentLoaded', function() {
    // Function to get a cookie by name
    // Retrieve the session_id from cookies
    let session_id = getCookie('session_id');

    let selectedImage = null;

    document.getElementById('capturecurrentframe').addEventListener('click', function() {
        let image = document.getElementById('videoStream'); // Assuming this is the still image
        let canvas = document.getElementById('canvas');
        let context = canvas.getContext('2d');

        // Set canvas dimensions to match the image
        canvas.width = image.naturalWidth;
        canvas.height = image.naturalHeight;

        // Draw the image onto the canvas
        context.drawImage(image, 0, 0, canvas.width, canvas.height);

        // Convert the canvas to an image in JPEG format 
        let img = new Image();
        img.src = canvas.toDataURL('image/jpeg');

        // Create a span element for the default label
        let labelElement = document.createElement('span');
        labelElement.textContent = 'no_label';

        // Append the image and the label to the sidebar
        let savedImagesContainer = document.getElementById('savedImagesContainer');
        savedImagesContainer.appendChild(img);
        savedImagesContainer.appendChild(labelElement);
    });

    // Function to handle image selection
    function selectImage(event) {
        // Deselect previously selected image
        if (selectedImage) {
            selectedImage.style.border = 'none';
        }

        // Select the new image
        selectedImage = event.target;
        selectedImage.style.border = '2px solid gray';

        // Enable the save, label, and delete buttons               
        document.getElementById('saveSelectedButton').disabled = false;
        document.getElementById('labelInput').disabled = false;
        document.getElementById('labelButton').disabled = false;
        document.getElementById('deleteButton').disabled = false; // Enable delete button
    }

    // Add event listener to the saved images container
    document.getElementById('savedImagesContainer').addEventListener('click', function(event) {
        if (event.target.tagName === 'IMG') {
            selectImage(event);
        }
    });

    // Function to apply label to the selected image
    document.getElementById('labelButton').addEventListener('click', function() {
        if (selectedImage) {
            let label = document.getElementById('labelInput').value;
            let labelElement = selectedImage.nextElementSibling;

            if (!labelElement || labelElement.tagName !== 'SPAN') {
                labelElement = document.createElement('span');
                selectedImage.parentNode.insertBefore(labelElement, selectedImage.nextSibling);
            }

            labelElement.textContent = label;
        }
    });

    // Function to save the selected image
    document.getElementById('saveSelectedButton').addEventListener('click', function() {
        console.log('saveSelectedButton clicked');
        console.log('session_id', session_id);
        if (selectedImage) {
            let imageData = selectedImage.src;
            let label = selectedImage.nextElementSibling ? selectedImage.nextElementSibling.textContent : '';

            // Check if imageData is a data URL and extract the base64 part
            if (imageData.startsWith('data:image')) {
                imageData = imageData.split(',')[1];
            }

            fetch('/save_image', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: session_id,
                    image_data: imageData,
                    image_label: label
                })
            })
            .then(response => response.json())
            .then(data => {
                console.log('Image saved:', data);
                // Display success message in the UI
                let messageElement = document.createElement('div');
                messageElement.textContent = 'Image successfully saved!';
                messageElement.style.color = 'green';
                document.body.appendChild(messageElement);

                // Optionally, remove the message after a few seconds
                setTimeout(() => {
                    document.body.removeChild(messageElement);
                }, 3000);
            })
            .catch(error => {
                console.error('Error saving image:', error);
            });
        }
    });

    // Add event listener to the delete button
    document.getElementById('deleteButton').addEventListener('click', function() {
        if (selectedImage) {
            // Remove the selected image and its label
            let labelElement = selectedImage.nextElementSibling;
            if (labelElement && labelElement.tagName === 'SPAN') {
                labelElement.remove();
            }
            selectedImage.remove();

            // Reset selectedImage and disable buttons
            selectedImage = null;
            document.getElementById('saveSelectedButton').disabled = true;
            document.getElementById('labelInput').disabled = true;
            document.getElementById('labelButton').disabled = true;
            document.getElementById('deleteButton').disabled = true;
        }
    });

    // Add event listener to the Annotate Saved Image button
    document.getElementById('Annotate_saved_image').addEventListener('click', function() {
        window.location.href = '/draw';
    });
}); 
