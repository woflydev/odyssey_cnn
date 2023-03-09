import cv2
import numpy as np
import time

# Changes source and destination points according to mode and cursor
def modifyPoints(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global srcPoints, destPoints, mode
        print(param)

        match param:
            case 'src':
                srcPoints[mode] = [x, y]
            case 'dest':
                destPoints[mode] = [x, y]
            case _:
                raise ValueError

        print(f"Source points: {srcPoints}")
        print(f"Destination points: {destPoints}")

    
frameDelay = 0.02
    

srcPoints = np.array([[0, 0], [0, 0], [0, 0], [0, 0]], dtype=np.float32)
destPoints = np.array([[0, 0], [0, 0], [0, 0], [0, 0]], dtype=np.float32)

srcColour = (255, 0, 0)
destColour = (0, 255, 0)

mode = 0
modes = [ord('1'), ord('2'), ord('3'), ord('4')]

imageScale = 1

circleRadius = 10
circleThickness = 1
textOffset = np.array([20, 20])
scale = 2
fontColour = (0, 0, 0)
fontThickness = 2

onStart = True

"""path = '.\data\img\self_car_data_hsv.png'

image = cv2.imread(path)"""

path = '.\data\\test_lane_video.mp4'
cap = cv2.VideoCapture(path)

cv2.namedWindow('source')
cv2.namedWindow('destination')
cv2.setMouseCallback('source', modifyPoints, 'src')
cv2.setMouseCallback('destination', modifyPoints, 'dest')


while True:
    ret, image = cap.read()
    if ret:
        # Scales the dimensions by 0.5.
        image = cv2.resize(image, (0, 0), fx=imageScale, fy=imageScale)


        #cv2.imshow('original', image)

        if not onStart:
            mtx = cv2.getPerspectiveTransform(srcPoints, destPoints)
        else:
            mtx = np.identity(3)

        #destSize = (np.amax(destPoints, 0) - np.amin(destPoints, 0)).astype(np.int32)
        destSize = (image.shape[1], image.shape[0])

        srcImage = np.copy(image)
        destImage = cv2.warpPerspective(srcImage, mtx, destSize)
        
        for pointIndex in range(len(srcPoints)):
            cv2.circle(srcImage, srcPoints[pointIndex].astype(np.int32), circleRadius, srcColour, circleThickness)
            cv2.putText(srcImage, str(pointIndex + 1), (srcPoints[pointIndex] + textOffset).astype(np.int32), cv2.FONT_HERSHEY_PLAIN, scale, fontColour, fontThickness)
        
        for pointIndex in range(len(destPoints)):
            cv2.circle(destImage, destPoints[pointIndex].astype(np.int32), circleRadius, destColour, circleThickness)
            cv2.putText(destImage, str(pointIndex + 1), (destPoints[pointIndex] + textOffset).astype(np.int32), cv2.FONT_HERSHEY_PLAIN, scale, fontColour, fontThickness)

        keyPressed = cv2.waitKey(1)
        if keyPressed in modes:
            mode = int(chr(keyPressed)) - 1
        elif keyPressed == ord('m'):
            print(mtx)
        elif keyPressed == ord('q'):
            break
        elif keyPressed == ord('p'):
            quitBool = False
            while True:
                pauseKey = cv2.waitKey(1)
                if pauseKey == ord('p'):
                    break
                elif pauseKey == ord('q'):
                    quitBool = True
                    break
                elif pauseKey in modes:
                    mode = int(chr(pauseKey)) - 1
            if quitBool:
                break

        cv2.imshow('source', srcImage)
        cv2.imshow('destination', destImage)

        onStart = False
    time.sleep(frameDelay)

cv2.destroyAllWindows()