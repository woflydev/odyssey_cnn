# from board import SCL, SDA
# import busio
# from adafruit_pca9685 import PCA9685
from time import sleep
import math
from pyfirmata import Arduino, util

PWM_FREQ = 1000      # (Hz) max is 1.5 kHz
MAP_CONST = 1 / 120   # 1 / 120 to limit speed below 100% duty cycle
HALF_WIDTH = 0.1          # Half of the width of droid, in metres
MAX_CENT_ACC = 30000   # Maximum "centripetal acceleration" the robot is allowed to undergo. UNITS ARE DODGY, MUST BE DETERMIEND BY EXPERIMENTATION
MAX_SPEED = MAP_CONST * 100  # (percent) max speed of motors
SERIAL_PORT = '/dev/ttyACM0' # Serial port for Arduino

# Left
#     A -> 13  
#     B -> 12
#   PWM -> 11

# Right
#     A -> 8
#     B -> 9
#   PWM -> 10

# I_Sense -> 7

board = Arduino(SERIAL_PORT)
print("Communication Successfully started")

motorLA = board.get_pin('d:13:o')
motorLB = board.get_pin('d:12:o')
motorRA = board.get_pin('d:8:o')
motorRB = board.get_pin('d:9:o')

motorPWML = board.get_pin('d:11:p')
motorPWMR = board.get_pin('d:10:p')

Isense = board.get_pin('d:7:i')

print("Motor driver initialized. \n path: utils\motor_lib\driver.py \n PWM frequency: " + str(PWM_FREQ) + "Hz \n Max speed: " + str(MAX_SPEED) + "%")

# Path: utils\motor_lib\driver.py
# off/coast/stop are the same
def off():
    # Enable pins are low during off() to coast
    motorPWML.write(0)
    motorPWMR.write(0)

    motorLA.write(0)
    motorLB.write(0)
    motorRA.write(0)
    motorRB.write(0)

def stop():
    off()
    
def coast():
    off()

def brake():
    off()
    motorLA.write(0)
    motorLB.write(0)
    motorRA.write(0)
    motorRB.write(0)
    # Enable pins are high during brake() to brake
    motorPWML.write(1)
    motorPWMR.write(1)

# brakes after 1.5s of coasting
def ebrake():
    off()
    sleep(1.5) # sleep(1.5)
    motorLA.write(1)
    motorLB.write(1)
    motorRA.write(1)
    motorRB.write(1)

# forward function
def fwd(speed, timeout=0):
    motorPWML.write(speed * MAP_CONST)
    motorPWMR.write(speed * MAP_CONST)

    motorLA.write(1)
    motorLB.write(0)
    motorRA.write(1)
    motorRB.write(0)

    if timeout > 0:
        sleep(timeout / 1000)
        off()

# reverse function
def rev(speed, timeout=0):
    motorPWML.write(speed * MAP_CONST)
    motorPWMR.write(speed * MAP_CONST)

    motorLA.write(0)
    motorLB.write(1)
    motorRA.write(0)
    motorRB.write(1)

    if timeout > 0:
        sleep(timeout / 1000)
        off()

# Write motor values for a turn, where a positive radius denotes a right turn (think +x), and negatvie radius defines left turn
def turn(speed: float, radius: float, timeout=0):
    r = abs(radius)
    if(speed < 0 or speed > 100):
        raise Exception(f"[MOTOR]: Invalid turn speed {speed}")
    if( r == 0 or speed * speed / r > MAX_CENT_ACC):
        print("[MOTOR]: Ignored attempt to turn at speed {speed} and radius {r} due to potential slipping.")
        return # Should I raise an exception instead?
    omega = speed / r
    if(radius > 0):
        move(omega * (r + HALF_WIDTH), omega * (r - HALF_WIDTH), timeout)
    elif(radius == 0):
        move(omega * (r - HALF_WIDTH), omega * (r + HALF_WIDTH), timeout)

# input -100 to 100 left and right sides
def move(LIN, RIN, timeout=0):
    LIN = round(LIN / 5) * 5
    RIN = round(RIN / 5) * 5
    L = LIN * MAP_CONST  # map values to 0-1
    R = RIN * MAP_CONST
    #print(L, R)
    if L == 0 and R == 0:
        off()
        brake()
    else:
        #print(L, R)
        if L > 0:
            motorLA.write(1)
            motorLB.write(0)
        else:
            motorLA.write(0)
            motorLB.write(1)
        if R > 0:
            motorRA.write(1)
            motorRB.write(0)
        else:
            motorRA.write(0)
            motorRB.write(1)
        
        motorPWML.write(abs(L))
        motorPWMR.write(abs(R))

    if timeout > 0:
        sleep(timeout / 1000)
        off()

# Drive pins other than motor pins
# def drivePin(pin, val):
#     if pin == 0 or pin == 1 or pin == 2 or pin == 3:
#         raise Exception(f"Pin {pin} is used for motors.")
#     else:
#         pca.channels[pin].duty_cycle = int(val / 100 * 65535)
#         print(f"Pin {pin} set to {val}%")
