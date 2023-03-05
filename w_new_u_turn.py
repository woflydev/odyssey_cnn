import cv2
import numpy as np
import logging
import math
import sys
import time
import os
import json

def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

class OpenCVDriver(object):

    def __init__(self, car=None):
        logging.info('Creating a OpenCV_Driver...')
        self.car = car

        #current 90 degree steering angle to eliminate start lag
        self.curr_steering_angle = 90


    # Bounds crop the destination image (a series of points defining a polygon)
    def perspective(self, frame, mtx, bounds, corners, scale, useCorners=True):
        warpedFrame = cv2.warpPerspective(frame, mtx, bounds)

        #blankMask = blankMask.astype('uint8')
        # Makes sure the corner coordinates are in ascending order
        newCorners = np.sort(corners, 0)

        # Slices the frame to fit a rectangular region
        if useCorners:
            return warpedFrame[newCorners[0][1]:newCorners[1][1], newCorners[0][0]:newCorners[1][0]]
        else:
            return warpedFrame
        #return warpedFrame

    def applyMasks(self, frame, masks):
        # Allows for multiple masks as an array to be applied then bitwise or.

        hsvArr = []
        for mask in masks:
            hsv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
            hsvArr.append(cv2.inRange(hsv, mask[0], mask[1]))
        
        mergedMask = np.zeros(frame.shape[:2]).astype('uint8')
        for maskedFrame in hsvArr:
            mergedMask = cv2.bitwise_or(mergedMask, maskedFrame)

        return mergedMask

    def findEdges(self, frame):
        # Parameters are tuned manually
        preprocessedFrame = cv2.Canny(frame, 100, 900)
        grayFrame = cv2.cvtColor(preprocessedFrame, cv2.COLOR_GRAY2BGR)
        lines = cv2.HoughLines(preprocessedFrame, 1, np.pi / 180, 100, None, 0, 0)

        coords = []
        if lines is not None:
            for i in range(0, len(lines)):
                # Polar parameters
                rho = lines[i][0][0]
                theta = lines[i][0][1]
                # Converts into rectilinear 
                a = math.cos(theta)
                b = math.sin(theta)
                x0 = a * rho
                y0 = b * rho

                pt1 = (int(x0 + 1000*(-b)), int(y0 + 1000*(a)))
                pt2 = (int(x0 - 1000*(-b)), int(y0 - 1000*(a)))

                coords.append([pt1, pt2])
                # Makes detected lines visible
                cv2.line(grayFrame, pt1, pt2, (0,0,255), 2, cv2.LINE_AA)
        return coords, grayFrame
    
    def curvature(self, maskedFrame, maxOffset, res):
        """for offset in range(-maxOffset, maxOffset, res):
            pass"""
        maxHeur = {"value": 0, "intensityArr": [], "frame": [], "radius": np.inf}
        height, width = maskedFrame.shape
        for offset in range(-maxOffset, maxOffset, res):
            if offset != 0:
                radius = (offset ** 2 + height ** 2) /(2 * offset)
            else:
                radius = np.inf

            correctedFrame = np.zeros((height, width + abs(offset)))

            for row in range(height):
                calcHeight = height - row - 1
                calcOffset = self.offset(calcHeight, radius)

                if calcOffset < 0:
                    correctedFrame[row][calcOffset - offset:calcOffset - offset + width] = maskedFrame[row]
                else:
                    correctedFrame[row][calcOffset:calcOffset + width] = maskedFrame[row]

            currentHeur = self.heuristic(correctedFrame)

            if currentHeur[0] > maxHeur['value']:
                maxHeur['value'] = currentHeur[0]
                maxHeur['radius'] = radius
                maxHeur['intensityArr'] = currentHeur[1]
                maxHeur['frame'] = correctedFrame

        return maxHeur
    
    # The amount that must be subtracted from an x-value in an image to correct a curve with radius r.
    def offset(self, y, r):
        if r == np.inf:
            return 0
        else:
            return round(r - sign(r) * math.sqrt(r ** 2 - y ** 2))

    def heuristic(self, frame):
        collapsedArr = np.sum(frame, 0)
        diffArr = np.sort(np.abs(np.ediff1d(collapsedArr)))

        # Sums the greatest four differences (which assumes there are two lane lines for greater precision)
        diffVal = np.sum(diffArr[-4:])
        return diffVal, collapsedArr
    
    def followLanes(self, curves, frame):
        pass

    def steer(self, params, frame):
        pass

def createWindows(nameArr):
    for name in nameArr:
        cv2.namedWindow(name)

def printCoordinates(event, x, y, flags, params):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(x, y)



def begin_analysis(path=0):
    cap = cv2.VideoCapture(path)
    driver = OpenCVDriver()

    width = int(cap.get(3))
    height = int(cap.get(4))

    size = (width, height)

    masks = np.array([[[0, 0, 197], [73, 38, 255]]])
    USE_MATRIX = False

    frameDelay = 0.1
    frameScale = 0.5

    #result = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
    
    srcPoints = np.array([[254, 207], [439, 212], [576, 313], [61, 308]]).astype(np.float32)
    destPoints = np.array([[249, 11], [433, 12], [439, 344], [254, 342]]).astype(np.float32)

    corners = np.array([[255, 4], [449, 345]]).astype('uint32')

    """srcPoints = np.array([[69, 138], [250, 146], [265, 181], [52, 178]]).astype(np.float32)
    destPoints = np.array([[96, 30], [238, 30], [230, 144], [98, 150]]).astype(np.float32)
    corners = np.array([])"""

    createWindows(['original', 'birds-eye', 'masked', 'edges', 'corrected'])

    # Allows easier cropping
    #cv2.setMouseCallback('birds-eye', printCoordinates)


    if USE_MATRIX:
        bounds = np.array([1920, 1080])
        mtx = json.loads(open('matrix.json', 'r').read())
    else: 
        #bounds = (np.amax(destPoints, 0) - np.amin(destPoints, 0)).astype(np.int32)
        bounds = (width, height)
        #bounds = destPoints
        mtx = cv2.getPerspectiveTransform(srcPoints, destPoints)

    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (0, 0), fx=frameScale, fy=frameScale)
            cv2.imshow('original', frame)
            birdsEyeFrame = driver.perspective(frame, mtx, bounds, corners, frameScale)
            cv2.imshow('birds-eye', birdsEyeFrame)

            maskedFrame = driver.applyMasks(birdsEyeFrame, masks)
            cv2.imshow('masked', maskedFrame)

            # Below lines of code to be replaced by RALPH code
            lines, edgedFrame = driver.findEdges(maskedFrame)
            cv2.imshow('edges', edgedFrame)


            # Below for testing, distorts the current image by a radius equivalent to if the top was shifted left by 100 pixels
            curveInfo = driver.curvature(maskedFrame, 100, 1)
            print(curveInfo['radius'])
            cv2.imshow('corrected', curveInfo['frame'])

            #result.write(newFrame)
        time.sleep(frameDelay)

if __name__ == "__main__":
    begin_analysis('.\data\\test_lane_video.mp4')