import logging
import cv2
import io
from PIL import Image
import numpy as np
import pickle

from classes.pyDrivingMatter import pyDrivingMatter
from classes.Car import Car
from classes.KBhit import KBHit
from classes.Misc import RPSCounter

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#pydm = pyDrivingMatter()
#car_data, car_link = pydm.get_car()

car_link = "ws://{}:{}".format("192.168.8.103", "8000")

action_link = "{}/action".format(car_link)
state_link = "{}/state".format(car_link)

logging.debug("Action Link: " + action_link)
logging.debug("State Link: " + state_link)

car = Car(action_link, url_state=state_link)

rps_counter = RPSCounter()

def handle_state(data, ws):
    global rps_counter
    current_datavector = pickle.loads(data)
    pc_rps = rps_counter.get()

    #logger.debug("PC RPS: " + str(pc_rps) + "\n\nCar RPS: " + str(car_rps) + "\n\nTotal: " + str(total_requests))

    sensors = current_datavector['sensors']
    logger.debug(sensors)
    camera_names = [key for key in current_datavector if key.startswith('camera')]
    for name in camera_names:
        frame = current_datavector[name]
        if frame != None:
            img = Image.open(io.BytesIO(frame))
            current_datavector[name] = img
            cv2.imshow(name, np.asarray(img))
            cv2.waitKey(1) # CV2 Devil - Don't dare to remove
        else:
            logger.debug("None frame received. Camera: " + name)

car.set_state_callback(handle_state)

try:
    kb = KBHit()
    while True:
        if kb.kbhit():
            c = kb.carkey()
            if c == 0:   # Up
                car.forward()            
            elif c == 1: # Right
                car.forwardRight() 
            elif c == 2: # Down
                car.backward()              
            elif c == 3: # Left
                car.forwardLeft()              
            elif c == 4: # Space
                car.stop()              
finally:
    kb.set_normal_term()    
    cv2.destroyAllWindows()
