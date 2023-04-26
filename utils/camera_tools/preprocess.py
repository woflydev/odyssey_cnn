import cv2
import numpy as np
from os import getcwd
import sys
sys.path.insert(0, getcwd())
from utils.webpanel.telementry import show_image

BLUR = 10
FLOOR_TOLERANCE = (60, 15, 15)
LINE_WIDTH = 15
erosion_size = round(LINE_WIDTH / 3)
element = cv2.getStructuringElement(cv2.MORPH_RECT, (2 * erosion_size + 1, 2 * erosion_size + 1),
                                       (erosion_size, erosion_size))
def preprocess(image, lane_colors_only=False):
    bgr = image[round(image.shape[0] / 3):, :]
    bgr = cv2.blur(bgr, (BLUR,BLUR))
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    lab = cv2.cvtColor(bgr, cv2.COLOR_BGR2LAB)
    # lab[..., 1] = 255
    avg = np.average(lab,(0,1))
    #floor filter
    mask1 = cv2.bitwise_not(cv2.inRange(lab, avg - FLOOR_TOLERANCE, avg + FLOOR_TOLERANCE))

    # average filter
    blur = cv2.blur(lab, (LINE_WIDTH * 3, LINE_WIDTH * 3))
    diff = lab - blur
    mask2 = cv2.bitwise_not(cv2.inRange(diff, (-256, -60, -60), (256, 60, 60)))

    mask = cv2.bitwise_and(mask1, mask2)
    
    mask = cv2.erode(mask, element)
    return cv2.bitwise_and(hsv, hsv, mask=mask), mask
if __name__ == "__main__":
    image = cv2.imread("data/img/stolen2.png")
    image = preprocess(image, True)
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    show_image("test",image)