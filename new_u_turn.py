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

class OpenCVDriver(object):

    def __init__(self, car=None):
        logging.info('Creating a OpenCV_Driver...')
        self.car = car

        #current 90 degree steering angle to eliminate start lag
        self.curr_steering_angle = 90

    def perspective(self, frame, mtx, bounds):
        blankMask = np.zeros_like(frame)
        cv2.fillPoly(blankMask, bounds)

        newFrame = cv2.bitwise_and(frame, frame, mask=blankMask)

        frameSize = np.amax(bounds, 0) - np.amin(bounds, 0)

        return cv2.warpPerspective(newFrame, mtx, frameSize)

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
    
    srcPoints = np.array([[351, 297], [731, 287], [146, 439], [909, 424]]).astype(np.float32)
    destPoints = np.array([[118, 25], [938, 17], [105, 418], [900, 436]]).astype(np.float32)

    if USE_MATRIX:
        bounds = [1920, 1080]
        mtx = json.loads(open('matrix.json', 'r').read())
    else: 
        bounds = (np.amax(destPoints, 0) - np.amin(destPoints, 0)).astype(np.int32)
        mtx = cv2.getPerspectiveTransform(srcPoints, destPoints)

    while True:

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()
        if ret:
            cv2.imshow('original', frame)
            birdsEyeFrame = driver.perspective(frame, mtx, bounds)
            cv2.imshow('birds-eye', birdsEyeFrame)
            #result.write(newFrame)

if __name__ == "__main__":
    begin_analysis('.\data\self_car_data.mp4')