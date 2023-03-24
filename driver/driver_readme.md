# Driver Library Usage

## Off/Coasting
`off()`\
`coast()`\
`stop()`

All three of the above functions pull the signals for the motor drivers low, causing them to coast.

## Moving
`move(L, R, `<em>`timeout`</em>`)`

L (int) – Left motor drive value (-100 to 100)

R (int) – Right motor drive value (-100 to 100)

timeout (int) (*optional*) – Time in milliseconds to run the motors for (default = 0)

## Emergency Brake
`ebrake()`

This function coasts the motors for 0.5 seconds, then pulls the signals high, causing them to active brake.
The function coasts the motors first to avoid damaging the motors or the drivers from back EMF.
Only use this function if need to stop the robot immediately, if not use `off()`, `coast()` or `stop()`.

## Testing Functions
`driver_test.py` also includes a few functions to help test the motors and drivers.


`testShort()`

This function will move the robot forward at a speed of (10,10) for 0.5s once.

`testMove()`

This function will move the robot forward at increasing and decreasing speeds for a total of 4 seconds, up to a speed of (10,10).

`testBrake()`

This function will move the robot forward at a speed increasing to (10,10) then decreasing to (5,5) and finally braking over a total of 4 seconds.

## Support and Resources
This library was designed for two BTS7960 motor driver modules, however it should work with any two generic H-bridge motor drivers. 
Below is the link to the datasheet for the BTS7960 high current half bridge.

[BTS7960 Datasheet](BTS7960.pdf)