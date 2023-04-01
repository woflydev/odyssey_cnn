from pydualsense import *
from driver import move, off, fwd
import math
# requires libhidapi-dev

LIMIT = 0.95

ds = pydualsense() 		# open controller
ds.init() 			# initialize controller

ds.light.setColorI(0,255,0) 	# set touchpad color to red
ds.triggerL.setMode(TriggerModes.Rigid)
ds.triggerL.setForce(1, 255)
ds.triggerR.setMode(TriggerModes.Rigid)
ds.triggerR.setForce(1, 255)
ds.conType.BT = True 		# set connection type to bluetooth

while True:
    left = (ds.state.LY / 128 * 100) * LIMIT
    right = (ds.state.RY / 128 * 100) * LIMIT

    if ds.state.R1 == 1:              # stop with R1
        left = 0
        right = 0
        print(f'OFF: [{left}, {right}]')
        off()

    if ds.state.cross == 1:            # exit with cross
        left = 0
        right = 0
        print(f'[{left}, {right}]')
        off()
        print("Stopped.")
        quit()

    print(f'[{left}, {right}]')
    move(left, right)
    