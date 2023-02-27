import cv2
import numpy as np
import logging
import math
import sys
import time
import os
import json

masks = np.array([[[0, 0, 0], [0, 0, 0]], [[0, 0, 0], [0, 0, 0]]])
USE_MATRIX = False

frameDelay = 0.5

class OpenCVDriver(object):

    def __init__(self, car=None):
        logging.info('Creating a OpenCV_Driver...')
        self.car = car

        #current 90 degree steering angle to eliminate start lag
        self.curr_steering_angle = 90


    # Bounds crop the destination image (a series of points defining a polygon)
    def perspective(self, frame, mtx, bounds):
        warpedFrame = cv2.warpPerspective(frame, mtx, frame.shape[:2])

        blankMask = np.zeros(frame.shape[:2], dtype='uint8')
        cv2.fillPoly(blankMask, pts=[bounds], color=255)
        return cv2.bitwise_and(warpedFrame, warpedFrame, mask=blankMask)

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

    

def begin_analysis(path=0):
    cap = cv2.VideoCapture(path)
    driver = OpenCVDriver()

    width = int(cap.get(3))
    height = int(cap.get(4))

    size = (width, height)

    #result = cv2.VideoWriter(path, cv2.VideoWriter_fourcc(*'MJPG'), 10, size)
    
    srcPoints = np.array([[254, 207], [439, 212], [61, 308], [576, 313]]).astype(np.float32)
    destPoints = np.array([[249, 11], [433, 12], [254, 342], [439, 344]]).astype(np.float32)

    if USE_MATRIX:
        bounds = np.array([1920, 1080])
        mtx = json.loads(open('matrix.json', 'r').read())
    else: 
        #bounds = (np.amax(destPoints, 0) - np.amin(destPoints, 0)).astype(np.int32)
        bounds = np.array([[0, 0], [width, 0], [width, height], [0, height]])
        #bounds = destPoints
        mtx = cv2.getPerspectiveTransform(srcPoints, destPoints)

    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            cv2.imshow('original', frame)
            birdsEyeFrame = driver.perspective(frame, mtx, bounds)
            cv2.imshow('birds-eye', birdsEyeFrame)
            #result.write(newFrame)
        time.sleep(frameDelay)

if __name__ == "__main__":
    begin_analysis('.\data\\test_lane_video.mp4')