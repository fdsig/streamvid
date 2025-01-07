### This is a repository of scripts for capturing data from edge devices sensors intended as methods to capture data for inference of machine learning models and training data.

Using No-IP's DDNS service (or any other similar service) is a great way to expose a Flask app running on your local machine to the internet, especially when you have a dynamic IP address. Here's a step-by-step guide to set it up:

    Sign Up and Choose a Domain:
        Go to https://www.noip.com/ and sign up for an account.
        Once signed up, create a new DDNS hostname. This will be a subdomain under one of the domains they offer (e.g., myflaskapp.ddns.net).

    Install the No-IP Dynamic Update Client (DUC):
        Download and install the No-IP DUC on the computer where your Flask app is running.
        Log in to the client using your No-IP account. The DUC will ensure that the IP address for your chosen domain (e.g., myflaskapp.ddns.net) always points to the current public IP of your computer.


### data labelling

This id done on device -- by running streamer.py which used flask middle ware -- images are saved back on device.
This flask app has a backend that will run on device to caputure image from a pi-camera and serve it to the frontend.
fronend labeling is then saved straing to device.

to run this simply pip install 

```
pip install streamer
python streamer/stream.py
```


## Model training

Take labelled images and then fine tune for smaller number of specific categories -- i.e. from object detection genereic multiple classes to cat [a,b,c] 

Deplyment/ logic

measure proximit between both bounding boxes of feeder and cats


to do:

- [ ] source train object detection model
- [ ] set up tracking
- [ ] visualize inference live in video stream
- [ ] inferenct tab for app
- [ ] 



