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

    """def findEdges(self, frame):
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
        return coords, grayFrame"""

    def distortFrame(self, frame, radius, isMask=True, log=False):
        if radius == np.inf or radius == -np.inf:
            return frame
        else:
            height = frame.shape[0]
            width = frame.shape[1]
            offset = self.offset(height, radius)

            newShape = list(frame.shape)
            newShape[1] += abs(offset)
            
            correctedFrame = np.zeros(newShape)

            for row in range(height):
                calcHeight = height - row - 1
                calcOffset = self.offset(calcHeight, radius)
                if log:
                    print(f"Height: {calcHeight}, Offset: {calcOffset}")

                correctedFrame[row][calcOffset - min(offset, 0):calcOffset - min(offset, 0) + width] = frame[row]
            return correctedFrame.astype('uint8') if isMask else correctedFrame.astype('bool')
    
    def curvature(self, maskedFrame, maxOffset, res):
        """for offset in range(-maxOffset, maxOffset, res):
            pass"""
        maxHeur = {"value": 0, "intensityArr": [], "frame": [], "radius": np.inf, "offset": 0}
        height, width = maskedFrame.shape
        for offset in range(-maxOffset, maxOffset, res):
            if offset != 0:
                radius = (offset ** 2 + height ** 2) /(2 * offset)
            else:
                radius = np.inf
            # Predicts one radius and then reverses the offset
            correctedFrame = self.distortFrame(maskedFrame, -radius)

            currentHeur = self.heuristic(correctedFrame)
            #print(f"Offset: {offset}, Heuristic: {currentHeur[0]}")
            if currentHeur[0] > maxHeur['value']:
                maxHeur['value'] = currentHeur[0]
                maxHeur['radius'] = radius
                maxHeur['intensityArr'] = currentHeur[1]
                maxHeur['offset'] = offset
                maxHeur['frame'] = correctedFrame

            #print(f"Radius: {radius}, Heuristic: {currentHeur[0]}")
            #print(f"Collapsed array: {currentHeur[1]}")
        return maxHeur
    
    # The amount that must be added from an x-value in an image to correct a curve with radius r.
    def offset(self, y, r):
        if r == np.inf:
            return 0
        else:
            return sign(r) * round(abs(r) - math.sqrt(r ** 2 - y ** 2))

    def heuristic(self, frame):
        collapsedArr = np.sum(frame / 255, 0)
        #print(collapsedArr)
        diffArr = np.abs(np.ediff1d(collapsedArr))
        #print(diffArr)
        diffArr = np.sort(diffArr)
        

        # Sums the greatest four differences (which assumes there are two lane lines for greater precision)
        # Divides by 100 (arbitrary) to make numbers more readable
        diffVal = np.sum(diffArr[-4:]) / 100
        return diffVal, collapsedArr
    
    def radiusToThrust(self, radius, speed, width=100, scale=1):
        if radius == np.inf:
            return [speed, speed]
        elif abs(radius) == width / 2:
            if radius < 0:
                return [0, speed]
            return [speed, 0]
        else:
            ratio = math.sqrt((radius/scale - width / 2) / (radius/scale + width / 2))
            return speed * np.array([ratio, 1/ratio])

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
    #np.set_printoptions(threshold=sys.maxsize)

    width = int(cap.get(3))
    height = int(cap.get(4))

    lineColour = (255, 0, 0)
    lineThickness = 5

    size = (width, height)

    # For blue and yellow
    #masks = np.array([[[0, 0, 248], [179, 24, 255]], [[94, 24, 218], [117, 255, 255]]])

    # For white
    masks = np.array([[[0, 0, 221], [179, 255, 255]]])
    USE_MATRIX = False

    frameDelay = 0
    frameScale = 0.5
    skipFrame = 1
    frameNum = 0
    
    # For testLaneVideo
    srcPoints = np.array([[254, 207], [439, 212], [576, 313], [61, 308]]).astype(np.float32)
    destPoints = np.array([[249, 11], [433, 12], [439, 344], [254, 342]]).astype(np.float32)
    corners = np.array([[255, 4], [449, 345]]).astype('uint32')
    
    # For testTrack
    '''srcPoints = np.array([[670, 181], [1106, 179], [1179, 534], [595, 522]]).astype(np.float32)
    destPoints = np.array([[477, 87], [842, 70], [871, 578], [462, 571]]).astype(np.float32)
    corners = np.array([[450, 100], [900, 600]]).astype('uint32')'''
    

    createWindows(['original', 'birds-eye', 'masked', 'corrected', 'birdsEyeLanes'])

    # Allows easier cropping
    #cv2.setMouseCallback('birds-eye', printCoordinates)


    if USE_MATRIX:
        bounds = np.array([1920, 1080])
        mtx = json.loads(open('matrix.json', 'r').read())[0]
        rvsMtx = json.loads(open('matrix.json', 'r').read())[1]
    else: 
        #bounds = (np.amax(destPoints, 0) - np.amin(destPoints, 0)).astype(np.int32)
        bounds = size
        #bounds = destPoints
        mtx = cv2.getPerspectiveTransform(srcPoints, destPoints)
        rvsMtx = cv2.getPerspectiveTransform(destPoints, srcPoints)

    while True:
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        ret, frame = cap.read()
        if ret and frameNum % skipFrame == 0:
            frame = cv2.resize(frame, (0, 0), fx=frameScale, fy=frameScale)
            cv2.imshow('original', frame)
            birdsEyeFrame = np.copy(frame)
            #birdsEyeFrame = driver.perspective(frame, mtx, bounds, corners, frameScale)
            #cv2.imshow('birds-eye', birdsEyeFrame)

            warpedBounds = birdsEyeFrame.shape

            #print(f"Birds-eye frame: {birdsEyeFrame}")
            #print(f"Warped frame: {warpedFrame}")
            #cv2.imshow('warp-test', warpedFrame)

            maskedFrame = driver.applyMasks(birdsEyeFrame, masks)
            #maskedFrame = driver.distortFrame(maskedFrame, 500)
            cv2.imshow('masked', maskedFrame)


            # Tries distortions from -100 pixels to 100 pixels with a resolution of 5 pixels.
            curveInfo = driver.curvature(maskedFrame, 100, 5)
            #print(curveInfo['radius'])
            if curveInfo['radius'] != np.inf:
                radius = int(curveInfo["radius"])
            else:
                radius = np.inf
            
            correctedFrame = driver.distortFrame(birdsEyeFrame, -radius)
            cv2.imshow('corrected', correctedFrame)

            birdsEyeLanes = np.copy(birdsEyeFrame)

            # Two brightest points (assumed that they are lanes)
            # Splits the intensity into two sides
            try:
                sides = np.split(curveInfo['intensityArr'], 2)
            except:
                sides = np.split(curveInfo['intensityArr'][:-1], 2)
            laneLocations = np.array([np.argsort(sides[0])[-1], np.argsort(sides[1])[-1] + sides[0].shape[0]]) - max(curveInfo['offset'], 0)

            if curveInfo["radius"] == np.inf:
                for lane in laneLocations:
                    cv2.line(birdsEyeLanes, (lane, 0), (lane, warpedBounds[0]), lineColour, lineThickness)
            else:
                for lane in laneLocations:
                    birdsEyeLanes = cv2.circle(birdsEyeLanes, (int(lane + radius), warpedBounds[0]), abs(radius), lineColour, lineThickness)    

            cv2.imshow('birdsEyeLanes', birdsEyeLanes)


            #print(f"Radius of curvature: {radius}")
            #print(f"Lane locations: {laneLocations}")
            print(f"Motor speeds: {driver.radiusToThrust(curveInfo['radius'], 50)}")
        time.sleep(frameDelay)
        frameNum += 1

if __name__ == "__main__":
    begin_analysis('.\data\\birds_eye_lane_data.mp4')