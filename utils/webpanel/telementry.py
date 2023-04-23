import cv2
from time import time
import os
PATH = '/dev/shm/odyssey_tmp'
if not os.path.exists(PATH):
    os.makedirs(PATH)

def show_image(name,image):
    #debounce frequenct writes
    #global last_wrote_image
    #if(time() < last_wrote_image + 1):
    #    return False
    # last_wrote_image = time()
    cv2.imwrite(f"{PATH}/{name}.png", image)
    return True
