import cv2
from time import time
#global last_wrote_image
#last_wrote_image = 0
def show_image(image):
    #debounce frequenct writes
    #global last_wrote_image
    #if(time() < last_wrote_image + 1):
    #    return False
    # last_wrote_image = time()
    cv2.imwrite("/dev/shm/frame.png", image)
    return True
