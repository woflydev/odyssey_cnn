import cv2
import sys
import numpy as np
import argparse

def nothing(x):
    pass

parser = argparse.ArgumentParser(description='Uses flags to either use a photo or a video.')
parser.add_argument('--video')
parser.add_argument('path', nargs=1)

argsParsed = parser.parse_args()
USE_VIDEO = argsParsed.video
print(USE_VIDEO)

cap = cv2.VideoCapture(USE_VIDEO, cv2.CAP_DSHOW) if USE_VIDEO else None
img = cv2.imread(str(argsParsed.path)) if argsParsed.path != '' else None

# Load frames (for image it's a path, but for a video get the current capture)
def returnFrame(videoBool=USE_VIDEO):
    if videoBool:
        return cap.read()[1]
    else:
        return img

# Create a window
slider_window = cv2.namedWindow('image', cv2.WINDOW_NORMAL)

# Create trackbars for color change
# Hue is from 0-179 for Opencv
cv2.createTrackbar('HMin', 'image', 0, 179, nothing)
cv2.createTrackbar('SMin', 'image', 0, 255, nothing)
cv2.createTrackbar('VMin', 'image', 0, 255, nothing)
cv2.createTrackbar('HMax', 'image', 0, 179, nothing)
cv2.createTrackbar('SMax', 'image', 0, 255, nothing)
cv2.createTrackbar('VMax', 'image', 0, 255, nothing)

# Set default value for Max HSV trackbars
cv2.setTrackbarPos('HMax', 'image', 179)
cv2.setTrackbarPos('SMax', 'image', 255)
cv2.setTrackbarPos('VMax', 'image', 255)

# Initialize HSV min/max values
hMin = sMin = vMin = hMax = sMax = vMax = 0
phMin = psMin = pvMin = phMax = psMax = pvMax = 0

while(True):
    image = returnFrame()
    if image is not None:
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
        hMin = cv2.getTrackbarPos('HMin', 'image')
        sMin = cv2.getTrackbarPos('SMin', 'image')
        vMin = cv2.getTrackbarPos('VMin', 'image')
        hMax = cv2.getTrackbarPos('HMax', 'image')
        sMax = cv2.getTrackbarPos('SMax', 'image')
        vMax = cv2.getTrackbarPos('VMax', 'image')

        # Set minimum and maximum HSV values to displayx
        lower = np.array([hMin, sMin, vMin])
        upper = np.array([hMax, sMax, vMax])

        # Convert to HSV format and color threshold
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(image, image, mask=mask)
        resultS = cv2.resize(result, (960, 540))

        # Print if there is a change in HSV value
        if((phMin != hMin) | (psMin != sMin) | (pvMin != vMin) | (phMax != hMax) | (psMax != sMax) | (pvMax != vMax) ):
            print("(hMin = %d , sMin = %d, vMin = %d), (hMax = %d , sMax = %d, vMax = %d)" % (hMin , sMin , vMin, hMax, sMax , vMax))
            phMin = hMin
            psMin = sMin
            pvMin = vMin
            phMax = hMax
            psMax = sMax
            pvMax = vMax

        # Display result image
        cv2.imshow('image', resultS)