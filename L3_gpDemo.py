# L3_telemetry.py
# A demonstration program: drive with gamepad and display telemetry.
# This program grabs data from the onboard sensors and log data in files
# for NodeRed access and integrate into a custom "flow".
# Access nodered at your.ip.address:1880

# v2020.11.29 DPM

# Import External programs
import numpy as np
import time

# Import Internal Programs
import L1_gamepad as gp
import L1_log as log
import L2_inverse_kinematics as inv
import L2_kinematics as kin
import L2_speed_control as sc

gamepad = gp.Gamepad()

# Run the main loop
while True:
    # # ACCELEROMETER SECTION
    # accel = mpu.getAccel()                          # call the function from within L1_mpu.py
    # (xAccel) = accel[0]                             # x axis is stored in the first element
    # (yAccel) = accel[1]                             # y axis is stored in the second element
    # #print("x axis:", xAccel, "\t y axis:", yAccel)     # print the two values
    # axes = np.array([xAccel, yAccel])               # store just 2 axes in an array
    # log.NodeRed2(axes)                              # send the data to txt files for NodeRed to access.
    
    # # DISPLAY BATTERY LEVEL
    # vb = adc.getDcJack()
    # log.tmpFile(vb,"vb.txt")
    
    # COLLECT GAMEPAD COMMANDS
    gp_data = gamepad.readValues()
    if gp_data is None:
        continue
    
    axis0 = gp_data[0] * -1
    axis1 = gp_data[1] * -1
    rthumb = gp_data[3] # up/down axis of right thumb
    horn = gp_data[4]   # "y" button
    
    
    # HORN FUNCTION
    # the horn is connected by relay to port 1 pin 0 (relay 1 of 2)
    # print("horn button:", horn)
    # if horn:
    #     gpio.write(1, 0, 1) # write HIGH
    #     time.sleep(0.30) # actuate for just 0.2 seconds
    #     gpio.write(1, 0, 0) # write LOW
    # #print("rthumb axis:", rthumb)
    
    phiDots = kin.getPdCurrent()
    myString = str(round(phiDots[0],1)) + "," + str(round(phiDots[1],1))
    log.stringTmpFile(myString,"phidots.txt")

    myString = str(round(axis0*100,1)) + "," + str(round(axis1*100,1))
    log.stringTmpFile(myString,"uFile.txt")
    print("Gamepad, xd: " ,axis1, " td: ", axis0) # print gamepad percents
    
    # DRIVE IN OPEN LOOP
    chassisTargets = inv.map_speeds(np.array([axis1, axis0])) # generate xd, td
    pdTargets = inv.convert(chassisTargets) # pd means phi dot (rad/s)
    # phiString = str(pdTargets[0]) + "," + str(pdTargets[1])
    # log.stringTmpFile(phiString,"pdTargets.txt")
    
    #DRIVING
    sc.driveOpenLoop(pdTargets) #call driving function 
    #servo.move1(rthumb) # control the servo for laser
    time.sleep(0.05)