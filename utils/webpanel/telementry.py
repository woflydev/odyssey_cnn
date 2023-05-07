import cv2
import time
import os
PATH = '/dev/shm/odyssey_tmp'
if not os.path.exists(PATH):
    os.makedirs(PATH)
import urllib.request as req

def show_image(name,image):
    w_start = time.process_time_ns()
    if(image.size > 90000):
        w = image.shape[1]
        h = image.shape[0]
        dest_w = 300
        image = cv2.resize(image, (dest_w, int(dest_w/w * h)))
    cv2.imwrite(f"{PATH}/{name}.bmp", image)
    req.urlopen(f"http://localhost:8000/forceFrameUpdate/{name}")
    print(f"Writing image took {(time.process_time_ns() - w_start) / 1e6}ms")
    return True
