# import the opencv library
import cv2
import time
  
#zipline = "nvarguscamerasrc ! 'video/x-raw(memory:NVMM), width=(int)3264, height=(int)2464, framerate=(fraction)30/1, format=(string)NV12' ! nvvidconv ! video/x-raw, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink drop=1"
zipline = "v4l2src ! video/x-raw, format=(string)YUY2,width=640, height=480 ! videoconvert ! video/x-raw,format=BGR ! appsink"

# define a video capture object
#vid = cv2.VideoCapture("nvarguscamerasrc ! video/x-raw(memory:NVMM),format=NV12,width=640,height=480,framerate=30/1 ! nvvidconv ! video/x-raw,format=BGRx ! videoconvert ! video/x-raw,format=BGR ! appsink drop=1", cv2.CAP_GSTREAMER)
vid = cv2.VideoCapture(zipline)
if not vid.isOpened():
    print("l bozo")
    exit(-1)
while True:
# Capture the video frame
# by frame
    print(vid.isOpened())
    ret, frame = vid.read()
    if(ret == False):
        print("L bozo")
        print(frame)
    else:
        cv2.imwrite('img.test.png', frame)
        
    time.sleep(1)