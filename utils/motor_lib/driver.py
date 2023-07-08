# from board import SCL, SDA
# import busio
# from adafruit_pca9685 import PCA9685
import signal
from time import sleep
import math
from telemetrix import telemetrix
import sys 

PWM_FREQ = 3906  # (Hz) max is 1.5 kHz
MAP_CONST = 1 / 120 * 255  # 1 / 120 to limit speed below 100% duty cycle
HALF_WIDTH = 0.1          # Half of the width of droid, in metres
MAX_CENT_ACC = 30000   # Maximum "centripetal acceleration" the robot is allowed to undergo. UNITS ARE DODGY, MUST BE DETERMIEND BY EXPERIMENTATION
MAX_SPEED = MAP_CONST / 255 * 100  # (percent) max speed of motors
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

def exit_handler(signal, frame):
    print("\n...\nStopping motors...")
    off()
    print("Cleaning up...")  
    print("Done.")  
    board.shutdown()
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

board = telemetrix.Telemetrix()
print("Communication Successfully started")

motorLA = 13
motorLB = 12
motorRA = 8
motorRB = 9

motorPWMLA = 11
motorPWMLB = 6
motorPWMRA = 10
motorPWMRB = 5

Isense = 7

board.set_pin_mode_digital_output(motorLA)
board.set_pin_mode_digital_output(motorLB)
board.set_pin_mode_digital_output(motorRA)
board.set_pin_mode_digital_output(motorRB)

board.set_pin_mode_analog_output(motorPWMLA)
board.set_pin_mode_analog_output(motorPWMLB)
board.set_pin_mode_analog_output(motorPWMRA)
board.set_pin_mode_analog_output(motorPWMRB)

board.set_pin_mode_digital_input(Isense)

print("Motor driver initialized. \n path: utils\motor_lib\driver.py \n PWM frequency: " + str(PWM_FREQ) + "Hz \n Max speed: " + str(MAX_SPEED) + "%")

# Path: utils\motor_lib\driver.py
# off/coast/stop are the same
def off():
    # Enable pins are low during off() to coast
    board.analog_write(motorPWMLA,0)
    board.analog_write(motorPWMLB,0)
    board.analog_write(motorPWMRA,0)
    board.analog_write(motorPWMRB,0)

    board.digital_write(motorLA,0)
    board.digital_write(motorLB,0)
    board.digital_write(motorRA,0)
    board.digital_write(motorRB,0)

def stop():
    off()
    
def coast():
    off()

def brake():
    off()
    board.digital_write(motorLA,1)
    board.digital_write(motorLB,1)
    board.digital_write(motorRA,1)
    board.digital_write(motorRB,1)
    # Enable pins are high during brake() to brake
    board.analog_write(motorPWMLA,0)
    board.analog_write(motorPWMLB,0)
    board.analog_write(motorPWMRA,0)
    board.analog_write(motorPWMRB,0)

# brakes after 1.5s of coasting
def ebrake():
    off()
    sleep(1.5) # sleep(1.5)
    board.digital_write(motorLA,1)
    board.digital_write(motorLB,1)
    board.digital_write(motorRA,1)
    board.digital_write(motorRB,1)

# forward function
def fwd(speed, timeout=0):
    board.analog_write(motorPWMLA,int(speed * MAP_CONST))
    board.analog_write(motorPWMLB,0)
    board.analog_write(motorPWMRA,int(speed * MAP_CONST))
    board.analog_write(motorPWMRB,0)

    board.digital_write(motorLA,1)
    board.digital_write(motorLB,1)
    board.digital_write(motorRA,1)
    board.digital_write(motorRB,1)

    if timeout > 0:
        sleep(timeout / 1000)
        off()

# reverse function
def rev(speed, timeout=0):
    board.analog_write(motorPWMLA,0)
    board.analog_write(motorPWMLB,int(speed * MAP_CONST))
    board.analog_write(motorPWMRA,0)
    board.analog_write(motorPWMRB,int(speed * MAP_CONST))

    board.digital_write(motorLA,1)
    board.digital_write(motorLB,1)
    board.digital_write(motorRA,1)
    board.digital_write(motorRB,1)

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

# # input -100 to 100 left and right sides
def move(RIN, LIN, timeout=0):
    LIN = round(LIN / 5) * 5
    RIN = round(RIN / 5) * 5
    L = LIN * MAP_CONST  # map values to 0-255
    R = RIN * MAP_CONST
    #print(L, R)
    if L == 0 and R == 0:
        off()
        brake()
    else:
        #print(L, R)
        if L > 0:
            board.analog_write(motorPWMLA,int(abs(L)))
            board.analog_write(motorPWMLB,0)
        else:
            board.analog_write(motorPWMLA,0)
            board.analog_write(motorPWMLB,int(abs(L)))
        if R > 0:
            board.analog_write(motorPWMRA,int(abs(R)))
            board.analog_write(motorPWMRB,0)
        else:
            board.analog_write(motorPWMRA,0)
            board.analog_write(motorPWMRB,int(abs(R)))
            
        board.digital_write(motorLA,1)
        board.digital_write(motorLB,1)
        board.digital_write(motorRA,1)
        board.digital_write(motorRB,1)
        
    if timeout > 0:
        sleep(timeout / 1000)
        off()

def readCurrent():
    return board.digital_read(Isense)



