import cv2
import time

cap = cv2.VideoCapture('.\data\\test_lane_video.mp4')
delay = 0.05

while True:
    ret, frame = cap.read()
    if ret:
        cv2.imshow('video', frame)
    if cv2.waitKey(1) == ord("q"):
        break
    time.sleep(delay)

cv2.destroyAllWindows()