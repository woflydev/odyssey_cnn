import cv2
import numpy
import json

def chessboardCorners(img: numpy.array):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    retval, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, flags=cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)
    if retval:
        # Refines corner measurements
        corners = numpy.reshape(cv2.cornerSubPix(gray, corners, (11,11),(-1,-1), criteria), (49, 2))
        newCornerMatrix = rotateMatrix(average, corners)
        #img = cv2.drawChessboardCorners(frame, CHECKERBOARD, corners, retval)
        newImg = cv2.drawChessboardCorners(img, CHECKERBOARD, newCornerMatrix, retval)
        return newCornerMatrix, newImg
    else:
        return numpy.ndarray(img.shape), numpy.ndarray(img.shape)

def averageOfPoints(mask: numpy.array):
    x = numpy.arange(0, mask.shape[0], 1)
    y = numpy.arange(0, mask.shape[1], 1)
    xx, yy = numpy.meshgrid(x, y)
    xx, yy = numpy.transpose(xx), numpy.transpose(yy)
    maskedX = numpy.multiply(xx, mask / 255).flatten()
    maskedY = numpy.multiply(yy, mask / 255).flatten()
    averageX = numpy.median(maskedX[maskedX != 0])
    averageY = numpy.median(maskedY[maskedY != 0])
    try:
        # Sometimes NaN
        return round(averageY), round(averageX)
    except:
        return 0, 0

def rotateMatrix(averageCoordinates: tuple, newImg: numpy.array):
    distances = []
    cornerMatrix = []
    newMatrix = numpy.reshape(newImg, (7, 7, 2))
    corners = ((0, 0), (0, 6), (6, 6), (6, 0))
    for i in range(4):
        newDist = numpy.linalg.norm(newMatrix[corners[i][0]][corners[i][1]] - averageCoordinates)
        cornerMatrix.append(newMatrix[corners[i][0]][corners[i][1]])
        distances.append(newDist)
    minIndex = distances.index(min(distances))
    return numpy.reshape(numpy.rot90(numpy.reshape(newImg, (7, 7, 2)), minIndex - 3), (49, 2))


CHECKERBOARD = (7, 7)
frameSize = (480, 640)
identityMatrix = numpy.array([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
yBound = 100
xBound = 300
hsvRangeForSticker = numpy.array([[166, 11, 209], [202, 106, 229]])
# Criteria for iteration (to refine corner measurements)
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
chessboardSize = 50
xBuffer = 50
yBuffer = 500 # from bottom


xValues = numpy.arange(xBuffer, xBuffer + 7 * chessboardSize, chessboardSize)
yValues = numpy.arange(yBuffer - 7 * chessboardSize, yBuffer, chessboardSize)
coordinates = numpy.ndarray((7, 7, 2))
for y in range(7):
    for x in range(7):
        coordinates[y][x] = [xValues[x], yValues[y]]
cornerCoordinates = coordinates.reshape((49, 2))


"""cornerCoordinates = numpy.float32([(xBuffer, yBuffer - CHECKERBOARD[1] * chessboardSize), 
    (xBuffer + CHECKERBOARD[0] * chessboardSize, yBuffer - CHECKERBOARD[1] * chessboardSize),
    (xBuffer + CHECKERBOARD[0] * chessboardSize, yBuffer),
    (xBuffer, yBuffer)])"""

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
frameNum = 0
# How many frames until chessboard analysis will take place
period = 5
while cap.isOpened():
    ret, frame = cap.read()
    stickerMask = cv2.inRange(cv2.cvtColor(frame, cv2.COLOR_RGB2HSV_FULL), hsvRangeForSticker[0], hsvRangeForSticker[1])
    average = averageOfPoints(stickerMask)
    if frameNum == 0:
        mtx = numpy.array([])
        homMatrix = identityMatrix
    # To avoid using every frame for calculation
    if frameNum % period == 0:
        mtx, newImg = chessboardCorners(frame)
        cv2.imshow("adjusted", newImg)
        keyPressed = cv2.waitKey(1)
    # Shows position of sticker
    cv2.circle(frame, average, 25, (0, 0, 0), -1)
    cv2.imshow("feed", frame)
    cv2.imshow("mask", stickerMask)

    try:
        result = cv2.warpPerspective(frame, homMatrix, (800, 800))
        cv2.imshow("perspective", result)
    except:
        print("Error!")

    if keyPressed == ord("c"):
        #newCorners = numpy.float32([mtx[0], mtx[6], mtx[48], mtx[42]])
        newCorners = numpy.float32(mtx)
        homMatrix = cv2.findHomography(newCorners, cornerCoordinates)
        
        # Writes matrix to file
        outFile = open('matrix.json', 'w')
        json.dump(homMatrix, outFile, indent=6)

        outFile.close()
    elif keyPressed == ord("q"):
        break
    frameNum += 1

cv2.destroyAllWindows()