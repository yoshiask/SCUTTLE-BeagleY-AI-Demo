# L1_gamepad.py
import time
import threading
import numpy as np
import inputs
from inputs import devices, get_gamepad


class Gamepad:
    # raw axis min/max (your sticks) and trigger threshold
    DEADZONE = 125
    TRIGGER_THRESHOLD = 10   # >10 counts as “pressed”
    
    def __init__(self):
        gamepads = [d.name for d in devices if isinstance(d, inputs.GamePad)]
        if not gamepads:
            print("\nNo gamepad detected.\n")
            return
        print("Found gamepad(s):", gamepads)

        # map only the four main axes
        self.axesMap = {
            'ABS_X':  'LEFT_X',
            'ABS_Y':  'LEFT_Y',
            'ABS_RX': 'RIGHT_X',
            'ABS_RY': 'RIGHT_Y',
        }

        # digital buttons
        self.buttonMap = {
            'BTN_SOUTH':'Y',
            'BTN_EAST':  'B',
            'BTN_C':     'A',
            'BTN_NORTH': 'X',
            'BTN_WEST':  'LB',
            'BTN_Z':     'RB',
            'BTN_TL2':   'BACK',
            'BTN_TR2':   'START',
            'BTN_SELECT':'L_JOY',
            'BTN_START': 'R_JOY',
            'BTN_MODE':  'MODE',
            # note: BTN_TL and BTN_TR are the bumpers, not triggers
            'BTN_TL':    'LT',   # if your pad reports a digital LT/RT
            'BTN_TR':    'RT',
        }

        # initialize everything
        self.axes = {name: None for name in self.axesMap.values()}
        self.buttons = {name: 0 for name in self.buttonMap.values()}
        self.hat = [0, 0]
        self.states = {'axes': self.axes, 'buttons': self.buttons, 'hat': self.hat}

        self.stateUpdating = False
        self.thread = threading.Thread(target=self._updater, daemon=True)
        self.thread.start()

        self.calibrate(gamepads[0])

    def _poll(self):
        for event in get_gamepad():
            code, val = event.code, event.state

            if event.ev_type == "Absolute":
                # D-pad
                if code.startswith("ABS_HAT"):
                    if code.endswith("X"):
                        self.hat[0] = val
                    else:
                        self.hat[1] = val

                # main analog sticks
                elif code in self.axesMap:
                    self.axes[self.axesMap[code]] = val

                # treat analog triggers as digital buttons
                elif code == 'ABS_Z':    # left trigger
                    self.buttons['LT'] = 1 if val > self.TRIGGER_THRESHOLD else 0
                elif code == 'ABS_RZ':   # right trigger
                    self.buttons['RT'] = 1 if val > self.TRIGGER_THRESHOLD else 0

                # anything else: ignore
                else:
                    continue

            elif event.ev_type == "Key":
                if code in self.buttonMap:
                    self.buttons[self.buttonMap[code]] = val
                else:
                    # unknown key event
                    continue

        # update combined state
        self.states = {'axes': self.axes, 'buttons': self.buttons, 'hat': self.hat}

    def _updater(self):
        self.stateUpdating = True
        try:
            while True:
                self._poll()
        except Exception as e:
            print("Gamepad thread stopped:", e)
            self.stateUpdating = False

    def calibrate(self, controller_name: str):
        # Check for previous calibration data
        with open("joystick_calibration.tsv", "r") as f:
            while True:
                line = f.readline()
                if not line:
                    break
                data = line.strip().split('\t')
                name = data[0]
                if name == controller_name:
                    # Pull existing data
                    self.RAW_X_MIN = int(data[1])
                    self.RAW_X_MAX = int(data[2])
                    self.RAW_Y_MIN = int(data[3])
                    self.RAW_Y_MAX = int(data[4])
                    return

        print("Calibrating gamepad...")

        # Wait for updater to start
        while not self.stateUpdating:
            pass

        # Read extreme values for each axis
        self.RAW_X_MIN = self._readExtremeValue("left", ['LEFT_X', 'RIGHT_X'])
        self.RAW_X_MAX = self._readExtremeValue("right", ['LEFT_X', 'RIGHT_X'])
        self.RAW_Y_MIN = self._readExtremeValue("down", ['LEFT_Y', 'RIGHT_Y'])
        self.RAW_Y_MAX = self._readExtremeValue("up", ['LEFT_Y', 'RIGHT_Y'])

        # Update center value
        self.RAW_X_CEN = (self.RAW_X_MAX + self.RAW_X_MIN) / 2
        self.RAW_Y_CEN = (self.RAW_Y_MAX + self.RAW_Y_MIN) / 2

        # Save calibration data
        calibration_data = [controller_name,
                            str(self.RAW_X_MIN), str(self.RAW_X_MAX),
                            str(self.RAW_Y_MIN), str(self.RAW_Y_MAX)]
        line = "\t".join(calibration_data)
        with open("joystick_calibration.tsv", "a") as f:
            f.write(line)
            f.write("\n")
        print("Calibration complete:", line)
        
    def _readExtremeValue(self, direction_name: str, axis_codes: list[str], duration: float = 2.0):
        print(f"\n• Move stick *all the way* {direction_name} and press Enter →", end=' ', flush=True)
        input()
        print(f"  Recording for {duration:.1f}...")
 
        startTime = time.time()
        extremeVal = 0

        while (time.time() - startTime < duration):
            axes = self.getStates()["axes"]
            for code in axis_codes:
                if code not in axes:
                    continue
                val = axes[code]
                print(val)
                if abs(val) > abs(extremeVal):
                    extremeVal = val

        return extremeVal

    def getStates(self):
        return self.states

    def readValues(self):
        if not self.stateUpdating:
            return None

        # Unpack raw axis values
        raw_left_x = self.axes['LEFT_X']
        raw_left_y = self.axes['LEFT_Y']
        raw_right_x = self.axes['RIGHT_X']
        raw_right_y = self.axes['RIGHT_Y']
        
        # scale sticks ⇒ [-1, +1]
        left_x = self._scaleAxisValue(raw_left_x, self.RAW_X_MIN, self.RAW_X_MAX, self.DEADZONE)
        left_y = self._scaleAxisValue(raw_left_y, self.RAW_Y_MIN, self.RAW_Y_MAX, self.DEADZONE)
        right_x = self._scaleAxisValue(raw_right_x, self.RAW_X_MIN, self.RAW_X_MAX, self.DEADZONE)
        right_y = self._scaleAxisValue(raw_right_y, self.RAW_Y_MIN, self.RAW_Y_MAX, self.DEADZONE)

        axes = [left_x, left_y, right_x, right_y]

        # pack buttons (now including LT/RT from triggers)
        buttons = np.array([
            self.buttons['Y'],   self.buttons['B'],
            self.buttons['A'],   self.buttons['X'],
            self.buttons['LB'],  self.buttons['RB'],
            self.buttons['LT'],  self.buttons['RT'],
            self.buttons['BACK'],self.buttons['START'],
            self.buttons['L_JOY'],self.buttons['R_JOY'],
        ], dtype=int)

        return np.hstack((axes, buttons))
    
    def _scaleAxisValue(self, raw_value: int | None, raw_min: int, raw_max: int, deadzone: int) -> float:
        """Scale a raw axis value to a float in the range [-1.0, 1.0]."""
        if raw_value is None:
            return 0.0

        return raw_value / (raw_max - raw_min)

if __name__ == "__main__":
    gamepad = Gamepad()
    
    while True:
        data = gamepad.readValues()
        if data is None:
            break
        print(data)
        time.sleep(0.05)