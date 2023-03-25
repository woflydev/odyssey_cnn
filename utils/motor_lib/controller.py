from pydualsense import *
from driver import move, off, fwd
import math
# requires libhidapi-dev

ds = pydualsense() 		# open controller
ds.init() 			# initialize controller

ds.light.setColorI(0,255,0) 	# set touchpad color to red
ds.triggerL.setMode(TriggerModes.Rigid)
ds.triggerL.setForce(1, 255)
ds.triggerR.setMode(TriggerModes.Rigid)
ds.triggerR.setForce(1, 255)
ds.conType.BT = True 		# set connection type to bluetooth

constant = -0.2
left = 0
right = 0
L2 = 1

k = -35
l = 37
c = 2
d = 0.2

def doubleSigmoid(x):
    return (k * L2 / 2) * ((math.tanh(x / l + c)) - (math.tanh(c - x / l))) + d  # double sigmoid interpolation

while True:
    #left = (ds.state.LY * constant * L2 + 1)
    #right = (ds.state.RY * constant * L2 + 1)
    left = doubleSigmoid(ds.state.LY)
    right = doubleSigmoid(ds.state.RY)
    L2 = 1 + ds.state.L2 / 240            # L2 speed boost
    
    while ds.state.triangle == 1:
        #left = (ds.state.LY * constant * L2 * 1.8 + 1)
        #right = (ds.state.RY * constant * L2 * 1.8 + 1)
        left = doubleSigmoid(ds.state.LY)
        right = doubleSigmoid(ds.state.RY)
        L2 = 1 + ds.state.L2 / 240            # L2 speed boost
        print(f'ULTRABOOST: [{left}, {right}]')
        move(left, right)
        if ds.state.cross == 1:            # emergency stop with cross
            left = 0
            right = 0
            print(f'[{left}, {right}]')
            off()
            break

    if ds.state.R1 == 1:              # stop with R1
        left = 0
        right = 0
        print(f'OFF: [{left}, {right}]')
        off()

    while ds.state.R2 > 1:
        forward = ds.state.R2 * 0.2
        L2 = 1 + ds.state.L2 / 240            # Forward
        print(f'FWD: [{forward}]')
        fwd(forward)
        if ds.state.cross == 1:            # emergency stop with cross
            left = 0
            right = 0
            print(f'[{left}, {right}]')
            off()
            break

        while ds.state.triangle == 1:
            forward = ds.state.R2 * 0.2 * 1.8
            L2 = 1 + ds.state.L2 / 240            # L2 speed boost
            print(f'FWD ULTRABOOST: [{forward}]')
            fwd(forward)
            if ds.state.cross == 1:            # emergency stop with cross
                left = 0
                right = 0
                print(f'[{left}, {right}]')
                off()
                break
            

    if ds.state.cross == 1:            # emergency stop with cross
        left = 0
        right = 0
        print(f'[{left}, {right}]')
        off()
        break

    print(f'[{left}, {right}]')
    move(left, right)
    
print("Stopped.")
