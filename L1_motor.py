from L1_pwm import pwm_from_gpio_pin
import numpy as np
import time

p0 = pwm_from_gpio_pin(6)
p1 = pwm_from_gpio_pin(5)
p2 = pwm_from_gpio_pin(13)
p3 = pwm_from_gpio_pin(12)

# configure and enable
for p in (p0,p1,p2,p3):
    p.frequency = 150
    p.enable()

def computePWM(speed: float) -> tuple[float, float]:
    if speed == 0:
        return 0, 0
    else:
        # Shift range to [0,2]
        x = speed + 1.0
        
        # Channel A sweeps low to high
        chA = 0.5 * x
        chA = np.round(chA, 2)
        
        # Channel B sweeps high to low
        chB = 1 - (0.5 * x)
        chB = np.round(chB, 2)
        
        chA, chB = np.clip([chA, chB], 0, 1)

        return chA, chB

def driveLeft(speed: float):
    chA, chB = computePWM(speed)
    p0.duty_cycle, p1.duty_cycle = chA, chB

def driveRight(speed: float):
    chA, chB = computePWM(speed)
    p2.duty_cycle, p3.duty_cycle = chA, chB

def drive(speed):
    """speed ∈ [-1.0…+1.0]: + forward, - reverse, 0 stop"""
    driveLeft(speed)
    driveRight(speed)

if __name__ == "__main__":
    try:
        print("Forward")
        drive(0.8)
        time.sleep(4)

        print("Reverse")
        drive(-0.8)
        time.sleep(4)
        
        print("Left")
        driveLeft(0.8)
        driveRight(-0.8)
        time.sleep(4)

        print("Right")
        driveLeft(-0.8)
        driveRight(0.8)
        time.sleep(4)
        
        print("Stopping")
        drive(0)
    finally:
        p0.disable()
        p1.disable()
        p0.close()
        p1.close()

        p2.disable()
        p3.disable()
        p2.close()
        p3.close()