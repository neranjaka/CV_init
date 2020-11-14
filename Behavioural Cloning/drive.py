import socketio
import eventlet
import base64
import numpy as np
import cv2
from flask import Flask
#import tensorflow as tf
#import keras
from tensorflow.keras.models import load_model
from io import BytesIO
from PIL import Image

sio = socketio.Server()

app = Flask(__name__) #'__main__'

#@app.route('/home')
#def greeting():
#    return 'Welcome!'

#print(tf.__version__)
#print(keras.__version__)

speed_limit = 10 # this is to limit the speed to 10
def img_preprocess(img):
  img = img[60:135,:,:]
  img = cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
  img = cv2.GaussianBlur(img, (3,3), 0)
  img = cv2.resize(img, (200,66))
  img = img/255
  return img

@sio.on('telemetry')
def telemetry(sid,data):
    speed = float(data['speed']) #gets the speed out of data
    image = Image.open(BytesIO(base64.b64decode(data['image'])))
    image = np.asarray(image)
    image = img_preprocess(image)
    image = np.array([image])
    steering_angle = float(model.predict(image))

    throttle = 1.0 - speed/speed_limit #this limits the speed to 10
    send_control(steering_angle,throttle)

@sio.on('connect')
def connect(sid,environ):
    print('Connected')
    send_control(0,0)

def send_control(steering_angle,throttle):
    sio.emit('steer',data={'steering_angle': steering_angle.__str__(),'throttle':throttle.__str__()})

if __name__ == '__main__':
    model = load_model('model.h5')
    app = socketio.Middleware(sio,app)
    eventlet.wsgi.server(eventlet.listen(('',4567)),app)
