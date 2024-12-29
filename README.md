### This is a repository of scripts for capturing data from edge devices sensors intended as methods to capture data for inference of machine learning models and training data.

Using No-IP's DDNS service (or any other similar service) is a great way to expose a Flask app running on your local machine to the internet, especially when you have a dynamic IP address. Here's a step-by-step guide to set it up:

    Sign Up and Choose a Domain:
        Go to https://www.noip.com/ and sign up for an account.
        Once signed up, create a new DDNS hostname. This will be a subdomain under one of the domains they offer (e.g., myflaskapp.ddns.net).

    Install the No-IP Dynamic Update Client (DUC):
        Download and install the No-IP DUC on the computer where your Flask app is running.
        Log in to the client using your No-IP account. The DUC will ensure that the IP address for your chosen domain (e.g., myflaskapp.ddns.net) always points to the current public IP of your computer.


### data labelling

data is labelled using a modified version of  [VIA](https://www.robots.ox.ac.uk/~vgg/software/via/) which is integrated into this project and can take camera stills that are captured on edge device and served from the same edge device and label these either for semantic segmentation or bounding box task.

to do:

- [ ] get image stills to show in VIA
- [ ] source train object detection model
- [ ] set up tracking
- [ ] visualize inference live in video stream



