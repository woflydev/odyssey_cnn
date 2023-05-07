import cv2
import sys
import time
from os import getcwd
sys.path.insert(0, getcwd())
from utils.webpanel.telementry import show_image
from utils.camera_tools.preprocess import preprocess

cap = cv2.VideoCapture("data/TestTrack.mp4")
while True:
    ret, frame = cap.read()
    if(not ret):
        break
    p_start = time.process_time_ns()
    f = cv2.cvtColor(preprocess(frame)[0], cv2.COLOR_HSV2BGR)
    print(f"Preprocess image took {(time.process_time_ns() - p_start) / 1e6}ms")
    show_image("test_video_stream", f)
    #time.sleep(0.1)