import cv2
import numpy as np

def detect_edges(frame):
    # filter for blue lane lines
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    #cv2.imshow("hsv", hsv)
    lower_blue = np.array([60, 40, 40])
    upper_blue = np.array([150, 255, 255])
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    cv2.imshow("blue mask", mask)

    # detect edges
    edges = cv2.Canny(mask, 200, 400)

    return edges

#cap.dshow only on windows
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
camera.set(3, 640)
camera.set(4, 480)

while(camera.isOpened()):
		_, image = camera.read()
		
		edges = detect_edges(image)       
		cv2.imshow('Original', edges)

		if cv2.waitKey(1) & 0xFF == ord('q') :
				break
				
cv2.destroyAllWindows()
