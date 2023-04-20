import cv2
import numpy as np

def preprocess(image):
    bgr = image[round(image.shape[0] / 2):image.shape[0], 0:image.shape[1]]
    hsv = cv2.cvtColor(bgr, cv2.COLOR_BGR2HSV)
    hsv[..., 1] = 255
    hsv = cv2.medianBlur(hsv, 15)
    avg = np.average(hsv,(0,1))
    #floor filter
    mask1 = cv2.bitwise_not(cv2.inRange(hsv, (avg[0] - 20, 0, avg[2]-20), (avg[0] + 20, 255, avg[2] + 20)))
    #ghost detection
    mask2 = cv2.inRange(hsv, (0, 0, 200), (255,255,256))
    mask = cv2.bitwise_and(mask1, mask2)
    hsv = cv2.bitwise_and(hsv,hsv, mask=mask)
    return hsv
def yellowOnly(hsv):
    mask = cv2.inRange(hsv, (20, 0, 0), (65,255,256))
    return cv2.bitwise_and(hsv,hsv, mask=mask)

def blueOnly(hsv):
    mask4 = cv2.inRange(hsv, (90, 0, 0), (150,255,256))
    return cv2.bitwise_and(hsv,hsv, mask=mask4)

if __name__ == "__main__":
    image = cv2.imread("data/img/school_tape3.jpg")
    image = preprocess(image)
    image = cv2.cvtColor(image, cv2.COLOR_HSV2BGR)
    cv2.imwrite("preprocess.test.png",image)