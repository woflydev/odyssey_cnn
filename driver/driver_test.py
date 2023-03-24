from board import SCL, SDA
import busio
from adafruit_pca9685 import PCA9685
from time import sleep

PWM_FREQ = 1000      # (Hz) max is 1.5 kHz
MAP_CONST = 655.35   # 65535 / 100

i2c_bus = busio.I2C(SCL, SDA)

# create PCA9685 class instance.
pca = PCA9685(i2c_bus)
pca.frequency = PWM_FREQ

# duty_cycle is 16 bits to match other PWM objects
# but the PCA9685 will only actually give 12 bits of resolution.
# 65535 is the maximum value.

pca.channels[0].duty_cycle = 0
pca.channels[1].duty_cycle = 0
pca.channels[2].duty_cycle = 0
pca.channels[3].duty_cycle = 0

motorLA = pca.channels[0]
motorLB = pca.channels[1]
motorRA = pca.channels[2]
motorRB = pca.channels[3]

# Path: driver\driver.py

# off/coast/stop are the same
def off():
    motorLA.duty_cycle = 0
    motorLB.duty_cycle = 0
    motorRA.duty_cycle = 0
    motorRB.duty_cycle = 0

def stop():
    off()
    
def coast():
    off()

# brakes after 1.5s of coasting
def ebrake():
    off()
    sleep(1.5)
    motorLA.duty_cycle = 65535
    motorLB.duty_cycle = 65535
    motorRA.duty_cycle = 65535
    motorRB.duty_cycle = 65535

# input -100 to 100 left and right sides
def move(LIN, RIN, timeout=0):
    L = int(LIN * MAP_CONST)  # map values to 0-65535
    R = int(RIN * MAP_CONST)
    off()
    if L > 0:
        motorLA.duty_cycle = L
        motorLB.duty_cycle = 0
    else:
        motorLA.duty_cycle = 0
        motorLB.duty_cycle = -L
    if R > 0:
        motorRA.duty_cycle = R
        motorRB.duty_cycle = 0
    else:
        motorRA.duty_cycle = 0
        motorRB.duty_cycle = -R
    sleep(timeout * 1000)

# testing functions
# Path: driver\driver_test.py
# testMove() a loop increasing the drive from (0,0) to (10,10) to (0,0) over 4 seconds
def testMove():
    print("Testing Move")
    for i in range(0, 10, 1):
        move(i, i)
        sleep(0.2)
    for i in range(10, 0, -1):
        move(i, i)
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