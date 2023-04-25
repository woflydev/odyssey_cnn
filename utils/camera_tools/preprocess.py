import cv2
import numpy as np
from os import getcwd
import sys
sys.path.insert(0, getcwd())
from utils.webpanel.telementry import show_image

BLUR = 10
FLOOR_TOLERANCE = (60, 15, 15)

def preprocess(image, lane_colors_only=False):
    bgr = image[round(image.shape[0] / 3):, :]
    bgr = cv2.blur(bgr, (BLUR,BLUR))
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    # lab[..., 1] = 255
    avg = np.average(lab,(0,1))
    #floor filter
    mask = cv2.bitwise_not(cv2.inRange(lab, avg - FLOOR_TOLERANCE, avg + FLOOR_TOLERANCE))

    if(lane_colors_only):
        white = cv2.inRange(hsv, (230, 108, 108), (256, 148, 148))
        yellow = cv2.inRange(hsv, (20, 0, 0), (65,256,256))
        #yellow = cv2.inRange(lab, YELLOW_LAB - LAB_TOLERANCE, YELLOW_LAB + LAB_TOLERANCE)
        blue = cv2.inRange(hsv, (80, 0, 0), (160,256,256))
        #blue = cv2.inRange(lab, BLUE_LAB - LAB_TOLERANCE, BLUE_LAB + LAB_TOLERANCE)
        m = cv2.bitwise_or(yellow, blue)
        m = cv2.bitwise_or(m, white)
        mask = cv2.bitwise_and(mask, m)
    hsv = cv2.bitwise_and(hsv,hsv, mask=mask)
    return hsv
if __name__ == "__main__":
    image = cv2.imread("data/img/stolen2.png")
    image = preprocess(image, True)
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    show_image(image)