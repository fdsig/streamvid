### This is a repository of scripts for capturing data from edge devices sensors intended as methods to capture data for inference of machine learning models and training data.

Using No-IP's DDNS service (or any other similar service) is a great way to expose a Flask app running on your local machine to the internet, especially when you have a dynamic IP address. Here's a step-by-step guide to set it up:

    Sign Up and Choose a Domain:
        Go to https://www.noip.com/ and sign up for an account.
        Once signed up, create a new DDNS hostname. This will be a subdomain under one of the domains they offer (e.g., myflaskapp.ddns.net).

    Install the No-IP Dynamic Update Client (DUC):
        Download and install the No-IP DUC on the computer where your Flask app is running.
        Log in to the client using your No-IP account. The DUC will ensure that the IP address for your chosen domain (e.g., myflaskapp.ddns.net) always points to the current public IP of your computer.


### data labelling

This is done on the device -- by running streamer.py which uses Flask middleware -- images are saved back on the device.
This flask app has a backend that will run on a device to capture ian mage from a pi-camera and serve it to the frontend.
frontend labelling is then saved streaming to the device.

to run this simply pip install 

```
pip install streamer
python streamer/stream.py
```


## Model training

Take labelled images and then fine-tune for a smaller number of specific categories -- i.e. from object detection generic multiple classes to cat [a,b,c] 

Deployment/ logic

measure the proximity between both bounding boxes of feeder and cats


## LLM 

LLM call application that describes based on classified data as a second check 

## LLM Call QA

example questions might include

how was my cat today  
how often did my cat move today
has my cat eaten today



to do:

- [ ] source train object detection model
- [ ] set up tracking
- [ ] visualize inference live in the video stream
- [ ] inference tab for app
- [ ] LLM check of inference
- [ ] LLM rag approach 
- [ ] test the Vanialla model on the device




