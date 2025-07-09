![Logo](image/jpg_1980px.jpg ':class=image-25')

# Welcome to the SCUTTLE Software Gude!

This guide explains how to setup and use all of the required software on SCUTTLE robot based on BeagleY-AI board.

## Environment Setup
Make sure all of the packages are up to date:
```bash
sudo apt update
```
Create a new virtual environment: \
To create: ```python3 -m venv ~/YOUR-ENV``` \
To activate: ```source ~/YOUR-ENV/bin/activate``` \
To deactivate: ```deactivate```

In the new environment install of the required libraries:
```bash
pip install numpy smbus2 python-periphery inputs
```

## How to install
### Clone the repo
```bash
git clone https://github.com/yoshiask/SCUTTLE-BeagleY-AI-Demo
```
### Navigate to the new directory
```bash
cd SCUTTLE-Beagle-AI-Demo
```

## Description
### L1_encoder.py
This file checks current positioning of both wheels. By running this file output should look like this:
```bash
$ python L1_encoder.py
Testing Encoders
Left:  9.3       Right:  120.1
Left:  9.3       Right:  120.2
```

### L1_motor.py

To check if the wheels are spinning. By running the file both wheels should spin 4 seconds forwards, 4 seconds backwards, and another 4 seconds not spinning to check the robot can stop. This is a great way to check if the wiring done correctly and if the mounted motors work at all. To run:
```bash
$ python L1_motor.py
```

### L1_gamepad.py
By running this file user can observe current states of each button on the gamepad:
```bash
$ python L1_gamepad.py
[-0.0210025  1.        -0.        -0.         0.         0.
  0.         0.         0.         0.         0.         0.
  0.         0.         0.         0.       ]
[-0.01880457  1.         -0.         -0.          0.          0.
  0.          0.          0.          0.          0.          0.
  0.          0.          0.          0.        ]
```

### L1_log.py
This program contains functions for logging robot parameters to local files.

### L1_pwm.py
This file is served to simplify pin PWM configuration. Instead of manually importing overlays and check which chip and channel pin operates, script does everything automatically.

### L2_kinematics.py
Computes the forward and turning velocities ($\dot{x}$, $\dot{\theta}$) from the left and right wheel velocities ($\dot{\varphi_L}$, $\dot{\varphi_R}$).

### L2_inverse_kinematics.py
Does the inverse: it computes the wheel velocities necessary to move forward and turn at a certain speed.

### L2_speed_control.py
This file contains all of the math calculations of SCUTTLE's speed.

### L3_gpDemo.py
Allows to control SCUTTLE using gamepad. In case of using a different controller recalibration is required which happens on first launch.
```bash
$ python gpDemo.py
```
<!--UNDER CONSTRUCTION-->