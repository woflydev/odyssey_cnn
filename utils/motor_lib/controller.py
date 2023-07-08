from pydualsense import *
from driver import *
import math
import cv2
# requires libhidapi-dev

LIMIT = 95

ds = pydualsense() 		# open controller
ds.init() 			# initialize controller

ds.light.setColorI(0,255,0) 	# set touchpad color to red
ds.triggerL.setMode(TriggerModes.Rigid)
ds.triggerR.setMode(TriggerModes.Pulse)
ds.conType.BT = False  		# set connection type to bluetooth

lightToggle = 0
# drivePin(15, 0)
video_type = cv2.VideoWriter_fourcc(*'MJPG')
video_overlay = cv2.VideoWriter("data/hi.avi", video_type, 10.0, (640, 480))
cap = cv2.VideoCapture(0)


while True:
    ret, frame = cap.read()
    video_overlay.write(frame)
    left = -ds.state.LY / 128 * LIMIT
    right = -ds.state.RY / 128 * LIMIT
    light = ds.state.L1 * 100 # ds.state.L2 ** 2 / (16384 / 25) # gradual control

    if ds.state.R1 == 1:              # brake with R1
        left = 0
        right = 0
        print(f'Brake: [{left}, {right}]')
        brake()

    if ds.state.R2 > 16:              # coast with R2
        left = 0
        right = 0
        print(f'Coast: [{left}, {right}]')
        off()

    if ds.state.cross == 1:            # exit with cross
        left = 0
        right = 0
        print(f'[{left}, {right}]')
        off()
        print("Stopped.")
        video_overlay.release()
        quit()

    print(f'Motor inputs [{left}, {right}]')
    move(left, right)
    # drivePin(15, light)
