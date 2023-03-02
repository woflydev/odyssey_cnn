import cv2
import numpy as np
import logging
import math
import sys
import time
import os
import json

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
        
        mergedMask = np.zeros(frame.shape)

        for maskedFrame in hsvArr:
            mergedMask = cv2.bitwise_or(mergedMask, maskedFrame)

        return mergedMask

    def findEdges(self, frame):
        pass

    def curveFits(self, lines, frame):
        pass
    
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

    masks = np.array([[[0, 0, 0], [0, 0, 0]]])
    USE_MATRIX = False

    frameDelay = 0.1
    frameScale = 0.5

    #result = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
    
    srcPoints = np.array([[254, 207], [439, 212], [576, 313], [61, 308]]).astype(np.float32)
    destPoints = np.array([[249, 11], [433, 12], [439, 344], [254, 342]]).astype(np.float32)

    corners = np.array([[246, 3], [437, 310]]).astype('uint32')

    createWindows(['original', 'birds-eye'])

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
            #result.write(newFrame)
        time.sleep(frameDelay)

if __name__ == "__main__":
    begin_analysis('.\data\\test_lane_video.mp4')