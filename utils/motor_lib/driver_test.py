from driver import *

# testing functions
# Path: driver\driver_test.py
# testMove() a loop increasing the drive from (0,0) to (10,10) to (0,0) over 4 seconds
def testMove():
    drivePin(15, 50)
    print("Testing Move")
    pm = 1
    for i in range(0, 100, 1):
        pm = -pm
        move(pm * i, pm * i)
        print(i)
        sleep(0.2)
    for i in range(100, 0, -1):
        pm = -pm
        move(pm * i, pm * i)
        print(i)
        sleep(0.2)
    off()
    print("Testing Move Complete")

# testBrake() a loop increasing the drive from (0,0) to (10,10) to (5,5) over 4 seconds and then ebrake
def testBrake():
    print("Testing Brake")
    for i in range(0, 10, 1):
        move(i, i)
        sleep(0.2)
    for i in range(10, 5, -1):
        move(i, i)
        sleep(0.4)
    ebrake()
    print("Testing Brake Complete")

# testShort() a drive forward for 0.5s at (10,10)
def testShort():
    print("Testing Short")
    move(10, 10)
    sleep(0.5)
    off()
    print("Testing Short Complete")

testMove()